"""平台探测与系统命令封装（Linux / WSL / Windows / macOS）。"""

from __future__ import annotations

import os
import platform
import re
import shutil
import socket
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

PLATFORMS = ("linux", "wsl", "windows", "macos")
_VSCODE_CACHE: set[str] | None = None


def detect() -> str:
    if sys.platform == "win32":
        return "windows"
    if sys.platform == "darwin":
        return "macos"
    try:
        version = Path("/proc/version").read_text(encoding="utf-8", errors="ignore").lower()
    except OSError:
        version = ""
    if "microsoft" in version or "wsl" in version or os.environ.get("WSL_DISTRO_NAME"):
        return "wsl"
    return "linux"


def label(plat: str) -> str:
    return {"linux": "Linux", "wsl": "WSL", "windows": "Windows", "macos": "macOS"}.get(plat, plat)


def distro() -> str:
    try:
        for line in Path("/etc/os-release").read_text(encoding="utf-8").splitlines():
            if line.startswith("PRETTY_NAME="):
                return line.split("=", 1)[1].strip().strip('"')
    except OSError:
        pass
    return platform.platform(terse=True)


def which(name: str | None) -> str | None:
    if not name:
        return None
    return shutil.which(name)


def has(name: str | None) -> bool:
    return which(name) is not None


def is_windows() -> bool:
    return os.name == "nt"


def _quote_windows(argv: list[str]) -> str:
    return subprocess.list2cmdline(argv)


def run(argv: list[str], *, check: bool = False, capture: bool = False,
        timeout: float | None = None) -> subprocess.CompletedProcess:
    """执行外部命令。Windows 下 .cmd/.bat（如 npm、winget）需要走 cmd。"""
    kwargs: dict = {"check": check, "timeout": timeout}
    if capture:
        kwargs.update(stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors="replace")
    if is_windows():
        exe = argv[0].lower()
        if exe.endswith((".cmd", ".bat")) or exe in ("npm", "npx", "winget", "code"):
            return subprocess.run(_quote_windows(argv), shell=True, **kwargs)
    return subprocess.run(argv, **kwargs)


def version_of(binary: str | None, timeout: float = 6.0) -> str:
    path = which(binary)
    if not path:
        return ""
    try:
        proc = run([path, "--version"], capture=True, timeout=timeout)
        text = proc.stdout or ""
    except (OSError, subprocess.SubprocessError):
        return ""
    match = re.search(r"\d+\.\d+(?:\.\d+)?[0-9A-Za-z.+-]*", text)
    if match:
        return match.group(0)
    for line in text.splitlines():
        line = line.strip()
        if line:
            return line[:32]
    return ""


def vscode_extensions(timeout: float = 10.0, refresh: bool = False) -> set[str]:
    global _VSCODE_CACHE
    if _VSCODE_CACHE is not None and not refresh:
        return _VSCODE_CACHE
    if not has("code"):
        _VSCODE_CACHE = set()
        return _VSCODE_CACHE
    try:
        proc = run(["code", "--list-extensions"], capture=True, timeout=timeout)
        _VSCODE_CACHE = {line.strip().lower() for line in (proc.stdout or "").splitlines() if line.strip()}
    except (OSError, subprocess.SubprocessError):
        _VSCODE_CACHE = set()
    return _VSCODE_CACHE


def port_open(host: str, port: int = 443, timeout: float = 3.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def check_hosts(hosts: list[tuple[str, int]], timeout: float = 3.0) -> dict[str, bool]:
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = pool.map(lambda hp: port_open(hp[0], hp[1], timeout), hosts)
        return {host: result for (host, _), result in zip(hosts, results)}


def exec_replace(argv: list[str]) -> int:
    """POSIX 下用 exec 替换当前进程，保证 TUI 的输入输出正常。"""
    if is_windows():
        return run(argv).returncode
    os.execvp(argv[0], argv)
    return 1
