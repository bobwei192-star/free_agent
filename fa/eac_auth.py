"""EAC 协付车道授权：走插件自带的同源 API 完成 GitHub 登录 + star。

dsh 的某些 Web 版本只加载 `dsh-our-free-model` 的**服务端**半区（模型清单、
`/api/our-free-model/*` 路由都在），插件面板所在的 `settings.section` 客户端半区没有挂载，
于是「设置」里看不到「Our Free Model」，「EAC 渠道授权」区块无处可点，
会话直接以 `AUTHORIZATION_REQUIRED` 失败。

这里复刻面板实际调用的几个请求，用命令行把同一条流程走完：

1. 用 journal 里打印的 `?token=` 链接换 30 天 Cookie（与浏览器首访问等价）；
2. `POST /eac/login/start` 取回授权链接（插件在这一步会自己拉起系统浏览器）；
3. 在浏览器里登录 GitHub 并 star 仓库；
4. `GET /eac/login/poll?link=...` 领取网关签发的用户令牌，由插件服务端落盘
   `~/.dsh/our-free-model/eac-user.json`（0600）。

令牌只在插件服务端与本机文件之间流转，本模块只读状态与链接，不写任何凭据。
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from http.cookiejar import CookieJar

API = "/api/our-free-model"
TOKEN_RE = re.compile(r"[?&]token=([A-Za-z0-9_.\-]{16,})")
DEFAULT_PORT = 3080
DEFAULT_UNIT = "dsh-web.service"
DEFAULT_REPO = "Ebony-Vinyl/dsh-our-free-model"


class EacError(RuntimeError):
    """授权流程中可呈现给用户的失败。"""


def web_port() -> int:
    """dsh Web UI 端口：单元文件里的 --port，回落到默认 3080。"""
    try:
        from fa import autostart

        info = autostart.status("dsh")
        port = int(info.get("port") or DEFAULT_PORT)
        if port > 0:
            return port
    except Exception:
        pass
    return DEFAULT_PORT


def find_token(unit: str = DEFAULT_UNIT, port: int = DEFAULT_PORT) -> str:
    """取最近一次启动打印的访问令牌：环境变量优先，其次 journal，最后本机日志文件。"""
    env = os.environ.get("DSH_WEB_TOKEN", "").strip()
    if env:
        return env
    text = ""
    if shutil_which("journalctl"):
        proc = subprocess.run(
            ["journalctl", "--user", "-u", unit, "--no-pager", "-o", "cat"],
            capture_output=True, text=True, errors="replace", timeout=20, check=False,
        )
        text = proc.stdout or ""
    if not TOKEN_RE.search(text):
        text += read_recent_logs(port)
    hits = TOKEN_RE.findall(text)
    return hits[-1] if hits else ""


def shutil_which(binary: str) -> str:
    import shutil

    return shutil.which(binary) or ""


def read_recent_logs(port: int) -> str:
    """非 systemd 平台的兜底：扫 ~/.dsh/logs/ 里最近几个启动日志。"""
    from pathlib import Path

    root = Path(os.environ.get("DSH_HOME") or Path.home() / ".dsh") / "logs"
    try:
        files = sorted((p for p in root.glob("startup-*.log")), key=lambda p: p.stat().st_mtime)[-3:]
    except OSError:
        return ""
    out = []
    for path in files:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if f"127.0.0.1:{port}" in text or port == DEFAULT_PORT:
            out.append(text)
    return "\n".join(out)


class Session:
    """带 Cookie 的同源 HTTP 客户端：只连本机，刻意绕开环境里的代理设置。"""

    def __init__(self, port: int, token: str = "") -> None:
        self.base = f"http://127.0.0.1:{port}"
        self.token = token
        self._opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(CookieJar()), urllib.request.ProxyHandler({})
        )

    def _send(self, method: str, path: str, body: bytes | None = None) -> tuple[int, dict]:
        request = urllib.request.Request(
            f"{self.base}{path}", data=body, method=method, headers={"accept": "application/json"}
        )
        try:
            with self._opener.open(request, timeout=30) as response:
                status, payload = response.status, response.read()
        except urllib.error.HTTPError as exc:
            status, payload = exc.code, exc.read()
        except OSError as exc:
            raise EacError(f"连不上 dsh Web UI（{self.base}）：{exc}。先 `fa autostart dsh` 或手动 `dsh web`。") from exc
        try:
            data = json.loads(payload.decode("utf-8", "replace")) if payload else {}
        except json.JSONDecodeError:
            data = {"error": payload.decode("utf-8", "replace")[:200]}
        return status, data if isinstance(data, dict) else {"value": data}

    def connect(self) -> "Session":
        """确认会话可用：必要时用 ?token= 首访问换 30 天 Cookie。"""
        status, _ = self._send("GET", f"{API}/meta")
        if status == 401:
            if not self.token:
                raise EacError(
                    "接口未授权，且本机没找到访问令牌。\n"
                    f"  · Linux/WSL：journalctl --user -u {DEFAULT_UNIT} -o cat | grep -o 'token=[^ ]*'\n"
                    f"  · 其它平台：dsh 启动时打印的 {self.base}/?token=... 里复制\n"
                    "拿到后加 `--token`，或导出环境变量 DSH_WEB_TOKEN 再试。"
                )
            self._send("GET", f"/?token={self.token}")
            status, _ = self._send("GET", f"{API}/meta")
            if status == 401:
                raise EacError("令牌没能换成会话 Cookie：多半是旧一次启动的令牌，请用最新日志里的那条。")
        return self

    def api(self, method: str, path: str, body: dict | None = None) -> dict:
        raw = json.dumps(body).encode() if body is not None else None
        status, data = self._send(method, f"{API}{path}", raw)
        if status >= 400:
            raise EacError(f"{method} {path} 失败（HTTP {status}）：{data.get('error', data)}")
        return data


def connect(port: int | None = None, token: str | None = None) -> Session:
    listen = port or web_port()
    return Session(listen, token if token is not None else find_token(port=listen)).connect()


def status(client: Session) -> dict:
    return client.api("GET", "/eac/status")


def start_login(client: Session) -> dict:
    """发起 GitHub 登录，返回 {url, link, opened}。"""
    return client.api("POST", "/eac/login/start", {})


def poll(client: Session, link: str) -> dict:
    return client.api("GET", f"/eac/login/poll?link={urllib.parse.quote(link, safe='')}")


def wait(client: Session, link: str, timeout: int = 900, interval: float = 2.5) -> dict:
    """轮询到授权完成 / 过期 / 出错，最多等 timeout 秒。"""
    deadline = time.time() + timeout
    last: dict = {}
    while True:
        try:
            last = poll(client, link)
        except EacError as exc:
            last = {"error": str(exc)}
        if last.get("status") in ("ok", "expired") or "error" in last:
            return last
        if time.time() >= deadline:
            return last
        time.sleep(interval)


def describe(data: dict) -> list[tuple[str, str]]:
    """把状态文档摊平成可打印的键值行。"""
    def mark(value) -> str:
        return "是" if value is True else "否" if value is False else "未知"

    rows = [
        ("车道可用", mark(data.get("available"))),
        ("需要授权", mark(data.get("required"))),
        ("已授权", mark(data.get("authorized"))),
        ("已 star", mark(data.get("starred"))),
        ("GitHub 账号", data.get("login") or "—"),
        ("本机凭据", "已保存" if data.get("local") else "无"),
        ("策略确认", "网关未确认" if data.get("unverified") else "已确认"),
        ("目标仓库", data.get("repo") or DEFAULT_REPO),
    ]
    if data.get("reason"):
        rows.append(("原因", str(data["reason"])))
    return rows
