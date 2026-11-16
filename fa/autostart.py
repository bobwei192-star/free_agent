"""开机自启动：systemd --user 单元（Linux / WSL）。

只做用户级注册，不碰系统级目录、不需要 root：
单元写入 `~/.config/systemd/user/`，用 `systemctl --user enable --now` 启用。
配合 `loginctl enable-linger`（用户不登录也能开机自启）。
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from fa import platforms, ui

SERVICES: dict[str, dict] = {
    "dsh": {
        "title": "DeepSeek Harness Web UI",
        "unit": "dsh-web.service",
        "binary": "dsh",
        "args": ["web", "--no-open"],
        "port": 3080,
        "docs": "https://github.com/deepseek-ai/dsh",
    },
}

ALIASES = {"dsh-web": "dsh", "harness": "dsh"}


def resolve(name: str) -> str | None:
    key = (name or "").strip().lower()
    return ALIASES.get(key, key) if key in ALIASES or key in SERVICES else None


def user_unit_dir() -> Path:
    return Path.home() / ".config" / "systemd" / "user"


def unit_file(name: str) -> Path:
    spec = SERVICES[name]
    return user_unit_dir() / spec["unit"]


def systemd_ok() -> bool:
    return shutil.which("systemctl") is not None and Path("/run/systemd/system").exists()


def linger_enabled() -> bool:
    if not shutil.which("loginctl"):
        return False
    proc = platforms.run(["loginctl", "show-user", os.environ.get("USER", ""), "-p", "Linger"],
                         capture=True, timeout=8)
    return "Linger=yes" in (proc.stdout or "")


def enable_linger() -> bool:
    """让用户不登录时也能开机自启（对自己的账号操作，通常不需要 sudo）。"""
    if not shutil.which("loginctl"):
        return False
    if linger_enabled():
        return True
    proc = platforms.run(["loginctl", "enable-linger"], capture=True, timeout=15)
    return proc.returncode == 0 and linger_enabled()


def detect_proxy_port() -> int | None:
    """猜测本机本地 HTTP 代理端口：先看环境变量，再看常见 clash 端口。"""
    for key in ("HTTPS_PROXY", "https_proxy", "HTTP_PROXY", "http_proxy"):
        value = os.environ.get(key, "")
        if "://127.0.0.1:" in value:
            try:
                return int(value.rsplit(":", 1)[1].split("/")[0])
            except ValueError:
                continue
    for port in (7897, 7890, 7891, 10809, 1080):
        if platforms.port_open("127.0.0.1", port, timeout=0.4):
            return port
    return None


def render_unit(name: str, *, port: int | None = None, proxy_port: int | None = None) -> str:
    spec = SERVICES[name]
    home = str(Path.home())
    binary = platforms.which(spec["binary"]) or f"{home}/.local/bin/{spec['binary']}"
    listen = port or spec["port"]
    args = " ".join(spec["args"])
    if listen:
        args = f"{args} --port {listen}"

    path_entries = [
        f"{home}/.local/bin",
        f"{home}/.local/node24/bin",
        f"{home}/.local/node/bin",
        f"{home}/.npm-global/bin",
        "/usr/local/bin",
        "/usr/bin",
        "/bin",
    ]

    lines = [
        "[Unit]",
        f"Description={spec['title']} (http://127.0.0.1:{listen})",
        f"Documentation={spec['docs']}",
        "After=network-online.target",
        "Wants=network-online.target",
        "",
        "[Service]",
        "Type=simple",
        f"ExecStart={binary} {args}",
        "Restart=always",
        "RestartSec=5",
        f"Environment=HOME={home}",
        "Environment=PATH=" + ":".join(path_entries),
        "Environment=NODE_ENV=production",
    ]

    if proxy_port:
        proxy = f"http://127.0.0.1:{proxy_port}"
        bypass = "localhost,127.0.0.1,::1"
        lines += [
            f"Environment=HTTP_PROXY={proxy}",
            f"Environment=HTTPS_PROXY={proxy}",
            f"Environment=http_proxy={proxy}",
            f"Environment=https_proxy={proxy}",
            f"Environment=NO_PROXY={bypass}",
            f"Environment=no_proxy={bypass}",
            "UnsetEnvironment=ALL_PROXY all_proxy",
        ]

    lines += [
        "StandardOutput=journal",
        "StandardError=journal",
        "",
        "[Install]",
        "WantedBy=default.target",
        "",
    ]
    return "\n".join(lines)


def install(name: str, *, port: int | None = None, proxy_port: int | None = None) -> Path:
    path = unit_file(name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_unit(name, port=port, proxy_port=proxy_port), encoding="utf-8")
    return path


def systemctl(*args: str, timeout: float = 30.0) -> subprocess.CompletedProcess:
    return platforms.run(["systemctl", "--user", *args], capture=True, timeout=timeout)


def enable(name: str, *, port: int | None = None, proxy_port: int | None = None) -> tuple[bool, str]:
    if not systemd_ok():
        return False, "systemd --user 不可用（当前系统不支持？）"
    path = install(name, port=port, proxy_port=proxy_port)
    systemctl("daemon-reload")
    proc = systemctl("enable", "--now", SERVICES[name]["unit"])
    if proc.returncode != 0:
        return False, (proc.stdout or "").strip() or "systemctl enable 失败"
    enable_linger()
    return True, str(path)


def disable(name: str) -> tuple[bool, str]:
    if not systemd_ok():
        return False, "systemd --user 不可用"
    proc = systemctl("disable", "--now", SERVICES[name]["unit"])
    if proc.returncode != 0:
        return False, (proc.stdout or "").strip() or "systemctl disable 失败"
    return True, SERVICES[name]["unit"]


def status(name: str) -> dict:
    spec = SERVICES[name]
    info: dict = {
        "name": name,
        "title": spec["title"],
        "unit": spec["unit"],
        "port": spec["port"],
        "url": f"http://127.0.0.1:{spec['port']}/",
        "unit_file": str(unit_file(name)),
        "installed": unit_file(name).exists(),
        "enabled": False,
        "active": False,
        "listening": False,
        "linger": linger_enabled(),
    }
    if not systemd_ok():
        return info
    info["enabled"] = "enabled" in (systemctl("is-enabled", spec["unit"]).stdout or "")
    info["active"] = (systemctl("is-active", spec["unit"]).stdout or "").strip() == "active"
    info["listening"] = platforms.port_open("127.0.0.1", spec["port"], timeout=1.5)
    return info
