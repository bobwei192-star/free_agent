"""按平台解析安装方式、拼装命令并执行。"""

from __future__ import annotations

import shlex
import subprocess

from fa import platforms, ui
from fa.catalog import Catalog, Tool

TYPE_PREREQ = {
    "npm": "npm",
    "uv": "uv",
    "pipx": "pipx",
    "script": "bash",
    "vscode-ext": "vscode",
    "winget": "winget",
}


def command_for(tool: Tool, plat: str, upgrade: bool = False) -> list[str] | None:
    method = tool.method(plat)
    kind = method["type"]
    if kind == "manual":
        return None
    if kind == "npm":
        pkg = method["pkg"] + ("@latest" if upgrade else "")
        return ["npm", "install", "-g", "--no-audit", "--no-fund", pkg]
    if kind == "uv":
        return ["uv", "tool", "upgrade" if upgrade else "install", method["pkg"]]
    if kind == "pipx":
        return ["pipx", "upgrade" if upgrade else "install", method["pkg"]]
    if kind == "script":
        return ["bash", "-lc", method["cmd"]]
    if kind == "pwsh":
        return ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", method["cmd"]]
    if kind == "winget":
        action = "upgrade" if upgrade else "install"
        return ["winget", action, "--id", method["id"], "-e",
                "--accept-package-agreements", "--accept-source-agreements"]
    if kind == "vscode-ext":
        return ["code", "--install-extension", method["id"], "--force"]
    return None


def missing_prereqs(catalog: Catalog, tool: Tool, plat: str) -> list[str]:
    method = tool.method(plat)
    prereq = TYPE_PREREQ.get(method["type"])
    if not prereq:
        return []
    meta = catalog.prereqs.get(prereq, {})
    check = meta.get("check", prereq)
    if platforms.has(check):
        return []
    return [prereq]


def prereq_hint(catalog: Catalog, prereq: str, plat: str) -> str:
    meta = catalog.prereqs.get(prereq, {})
    hints = meta.get("hint", {})
    return hints.get(plat) or hints.get("default") or f"请先安装 {meta.get('label', prereq)}"


def describe(method: dict) -> str:
    kind = method["type"]
    if kind == "npm":
        return f"npm -g {method['pkg']}"
    if kind == "uv":
        return f"uv tool {method['pkg']}"
    if kind == "pipx":
        return f"pipx {method['pkg']}"
    if kind == "winget":
        return f"winget {method['id']}"
    if kind == "vscode-ext":
        return f"code --install-extension {method['id']}"
    if kind == "manual":
        return "手动安装"
    return method.get("cmd", kind)


def is_installed(tool: Tool, plat: str, extensions: set[str] | None = None) -> bool:
    if tool.kind == "ext":
        method = tool.method(plat)
        ext_id = str(method.get("id", "")).lower()
        if extensions is None:
            extensions = platforms.vscode_extensions()
        return ext_id in extensions
    return platforms.has(tool.bin(plat))


def install_tool(catalog: Catalog, tool: Tool, plat: str, *,
                 dry_run: bool = False, force: bool = False,
                 upgrade: bool = False) -> str:
    method = tool.method(plat)
    if method["type"] == "manual":
        url = method.get("url") or tool.docs()
        print(f"  {ui.bold(tool.id)}：手动安装 → {url}")
        if method.get("note"):
            print(f"    {ui.dim(method['note'])}")
        return "manual"

    command = command_for(tool, plat, upgrade=upgrade)
    if not command:
        return "manual"

    if dry_run:
        ui.say(f"  {ui.cyan('$')} {' '.join(command)}")
        return "dry"

    missing = missing_prereqs(catalog, tool, plat)
    if missing:
        for prereq in missing:
            ui.error(f"{tool.id} 需要 {prereq}：{prereq_hint(catalog, prereq, plat)}")
        return "blocked"

    if not upgrade and not force and is_installed(tool, plat):
        ui.say(f"  {ui.green('·')} {tool.id} 已安装，跳过（--force 可重装）")
        return "skip"

    ui.say(f"  {ui.cyan('$')} {' '.join(command)}")
    try:
        proc = platforms.run(command)
    except (OSError, subprocess.SubprocessError) as exc:
        ui.error(f"{tool.id} 安装失败：{exc}")
        return "failed"

    if proc.returncode != 0:
        ui.error(f"{tool.id} 安装失败（退出码 {proc.returncode}）")
        return "failed"

    if tool.kind == "ext" or platforms.has(tool.bin(plat)):
        ui.ok(f"{tool.id} 就绪")
        return "installed"

    ui.warn(f"{tool.id} 命令已执行，但 PATH 中还没有 {tool.bin(plat)}；请重开终端")
    return "installed"


def update_tool(tool: Tool, plat: str, *, dry_run: bool = False) -> str:
    if not is_installed(tool, plat):
        return "skip"

    if tool.update_cmd():
        command = shlex.split(tool.update_cmd())
        if dry_run:
            ui.say(f"  {ui.cyan('$')} {' '.join(command)}")
            return "dry"
        ui.say(f"  {ui.cyan('$')} {' '.join(command)}")
        try:
            return "updated" if platforms.run(command).returncode == 0 else "failed"
        except (OSError, subprocess.SubprocessError):
            return "failed"

    command = command_for(tool, plat, upgrade=True)
    if not command:
        ui.say(f"  {tool.id}：请手动升级（{tool.docs()}）")
        return "manual"

    if dry_run:
        ui.say(f"  {ui.cyan('$')} {' '.join(command)}")
        return "dry"
    ui.say(f"  {ui.cyan('$')} {' '.join(command)}")
    try:
        return "updated" if platforms.run(command).returncode == 0 else "failed"
    except (OSError, subprocess.SubprocessError):
        return "failed"
