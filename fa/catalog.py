"""工具清单（catalog/tools.json）的加载、校验与平台解析。"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

VALID_KINDS = ("cli", "gui", "ext")
VALID_TYPES = ("npm", "uv", "pipx", "script", "pwsh", "winget", "vscode-ext", "manual")
REQUIRED_FIELDS = ("id", "name", "vendor", "kind", "bins", "free", "login", "install")

_FALLBACKS = {
    "wsl": ("wsl", "linux", "default"),
    "macos": ("macos", "linux", "default"),
    "linux": ("linux", "default"),
    "windows": ("windows", "default"),
}


class CatalogError(Exception):
    pass


def default_path() -> Path:
    env = os.environ.get("FREE_AGENT_CATALOG")
    if env:
        return Path(env).expanduser()
    here = Path(__file__).resolve()
    candidates = [
        here.parent.parent / "catalog" / "tools.json",
        Path(sys.prefix) / "share" / "free-agent" / "tools.json",
        here.parent / "data" / "tools.json",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise CatalogError(
        "找不到 catalog/tools.json；请设置 FREE_AGENT_CATALOG 指向清单文件"
    )


def _pick(mapping, plat: str, sentinel=None):
    """按平台优先级取值；显式 null 视为“该平台无此项”，不再回退。"""
    if not isinstance(mapping, dict):
        return mapping
    for key in _FALLBACKS.get(plat, (plat, "default")):
        if key in mapping:
            return mapping[key]
    return sentinel


class Tool:
    def __init__(self, raw: dict):
        self.raw = raw

    def __getattr__(self, item):
        try:
            return self.raw[item]
        except KeyError as exc:
            raise AttributeError(item) from exc

    @property
    def proxy_required(self) -> bool:
        return bool(self.raw.get("proxy", False))

    def bin(self, plat: str) -> str | None:
        value = _pick(self.raw.get("bins"), plat)
        return value if isinstance(value, str) and value else None

    def method(self, plat: str) -> dict:
        value = _pick(self.raw.get("install", {}), plat)
        if not isinstance(value, dict):
            return {"type": "manual", "url": self.raw.get("docs", ""),
                    "note": "该平台暂无自动安装方式"}
        return value

    def login_cmd(self) -> str | None:
        return self.raw.get("login_cmd")

    def update_cmd(self) -> str | None:
        return self.raw.get("update_cmd")

    def docs(self) -> str:
        return self.raw.get("docs", "")


class Catalog:
    def __init__(self, data: dict, path: Path):
        self.data = data
        self.path = path
        self.tools = [Tool(raw) for raw in data["tools"]]
        self._by_id = {tool.id: tool for tool in self.tools}

    @property
    def updated(self) -> str:
        return str(self.data.get("updated", ""))

    @property
    def groups(self) -> dict:
        return self.data.get("groups", {})

    @property
    def prereqs(self) -> dict:
        return self.data.get("prereqs", {})

    @property
    def network(self) -> list[dict]:
        return self.data.get("network", [])

    def get(self, tool_id: str) -> Tool:
        try:
            return self._by_id[tool_id]
        except KeyError as exc:
            raise CatalogError(f"未知工具：{tool_id}") from exc

    def by_kind(self, kind: str) -> list[Tool]:
        return [tool for tool in self.tools if tool.kind == kind]

    def group_title(self, kind: str) -> str:
        return self.groups.get(kind, {}).get("title", kind)

    def select(self, targets: list[str]) -> list[Tool]:
        """targets 可以是工具 id、组名（cli/gui/ext）或 all。"""
        if not targets:
            return []
        selected: list[Tool] = []
        seen: set[str] = set()
        for target in targets:
            if target == "all":
                found = list(self.tools)
            elif target in self.groups:
                found = self.by_kind(target)
            elif target in self._by_id:
                found = [self._by_id[target]]
            else:
                raise CatalogError(f"未知目标：{target}（可用：all / {' / '.join(self.groups)} / 工具 id）")
            for tool in found:
                if tool.id not in seen:
                    seen.add(tool.id)
                    selected.append(tool)
        return selected


def validate(data: dict) -> None:
    if not isinstance(data, dict) or data.get("schema") != 1:
        raise CatalogError("清单格式错误：缺少 schema=1")
    groups = data.get("groups")
    if not isinstance(groups, dict) or not groups:
        raise CatalogError("清单格式错误：缺少 groups")
    tools = data.get("tools")
    if not isinstance(tools, list) or not tools:
        raise CatalogError("清单格式错误：缺少 tools")
    seen: set[str] = set()
    for index, raw in enumerate(tools):
        where = f"tools[{index}]"
        if not isinstance(raw, dict):
            raise CatalogError(f"{where} 不是对象")
        for field in REQUIRED_FIELDS:
            if field not in raw:
                raise CatalogError(f"{where} 缺少字段 {field}")
        tool_id = raw["id"]
        if not isinstance(tool_id, str) or not tool_id:
            raise CatalogError(f"{where}.id 非法")
        if tool_id in seen:
            raise CatalogError(f"工具 id 重复：{tool_id}")
        seen.add(tool_id)
        if raw["kind"] not in groups:
            raise CatalogError(f"{where}.kind 未在 groups 中定义：{raw['kind']}")
        install = raw["install"]
        if not isinstance(install, dict) or not install:
            raise CatalogError(f"{where}.install 必须是非空对象")
        for platform_key, method in install.items():
            if platform_key not in ("default", "linux", "wsl", "windows", "macos"):
                raise CatalogError(f"{where}.install 平台键非法：{platform_key}")
            _validate_method(where, platform_key, method)
    for name, meta in (data.get("prereqs") or {}).items():
        if not isinstance(meta, dict) or "check" not in meta:
            raise CatalogError(f"prereqs.{name} 缺少 check 字段")


def _validate_method(where: str, platform_key: str, method) -> None:
    if not isinstance(method, dict):
        raise CatalogError(f"{where}.install.{platform_key} 不是对象")
    method_type = method.get("type")
    if method_type not in VALID_TYPES:
        raise CatalogError(f"{where}.install.{platform_key}.type 非法：{method_type}")
    if method_type in ("npm", "uv", "pipx") and not method.get("pkg"):
        raise CatalogError(f"{where}.install.{platform_key} 缺少 pkg")
    if method_type in ("script", "pwsh") and not method.get("cmd"):
        raise CatalogError(f"{where}.install.{platform_key} 缺少 cmd")
    if method_type in ("winget", "vscode-ext") and not method.get("id"):
        raise CatalogError(f"{where}.install.{platform_key} 缺少 id")


def load(path: str | Path | None = None) -> Catalog:
    target = Path(path).expanduser() if path else default_path()
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CatalogError(f"清单不存在：{target}") from exc
    except json.JSONDecodeError as exc:
        raise CatalogError(f"清单 JSON 解析失败：{target}: {exc}") from exc
    validate(data)
    return Catalog(data, target)
