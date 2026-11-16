"""环境体检：命令、前置依赖、网络可达性。"""

from __future__ import annotations

import shutil
import sys

from fa import __version__, autostart, installer, platforms, ui
from fa.catalog import Catalog, Tool


def tool_status(tool: Tool, plat: str, extensions: set[str] | None = None,
                with_version: bool = True) -> tuple[str, str]:
    if tool.kind == "ext":
        if extensions is None:
            extensions = platforms.vscode_extensions()
        method = tool.method(plat)
        installed = str(method.get("id", "")).lower() in extensions
        return ("OK" if installed else "MISSING", "-")
    binary = tool.bin(plat)
    if not binary:
        return ("MANUAL", "-")
    if platforms.has(binary):
        return ("OK", platforms.version_of(binary) if with_version else "-")
    return ("MISSING", "-")


def run(catalog: Catalog, plat: str, *, net: bool = False, strict: bool = False) -> int:
    extensions = platforms.vscode_extensions()

    ui.say(ui.bold(f"Free_Agent {__version__}") + ui.dim(f"  ·  清单 {catalog.path.name}（{catalog.updated}）"))
    ui.say(f"  平台      {platforms.label(plat)}  {ui.dim(platforms.distro())}")
    ui.say(f"  Python    {sys.version.split()[0]}  {ui.dim(sys.executable)}")
    ui.say(f"  启动器    {ui.dim(shutil.which('fa') or '未在 PATH 中（可直接用 python -m fa）')}")
    ui.say()

    ui.say(ui.bold("前置依赖"))
    needed = {
        installer.TYPE_PREREQ[tool.method(plat)["type"]]
        for tool in catalog.tools
        if tool.method(plat)["type"] in installer.TYPE_PREREQ
    }
    missing_prereqs: list[str] = []
    for name, meta in catalog.prereqs.items():
        if name not in needed:
            continue
        check = meta.get("check", name)
        if platforms.has(check):
            ui.say(f"  {ui.green('✓')} {name:<8} {ui.dim(platforms.which(check) or '')}")
        else:
            missing_prereqs.append(name)
            ui.say(f"  {ui.red('✗')} {name:<8} {installer.prereq_hint(catalog, name, plat)}")
    ui.say()

    if plat in ("linux", "wsl") and autostart.systemd_ok():
        ui.say(ui.bold("开机自启（systemd --user）"))
        for name in autostart.SERVICES:
            info = autostart.status(name)
            if not info["installed"]:
                ui.say(f"  {ui.yellow('○')} {name:<8} {ui.dim('未配置：fa autostart ' + name)}")
                continue
            state = "运行中" if info["active"] else ("已启用" if info["enabled"] else "已停用")
            color = ui.green if info["active"] else (ui.yellow if info["enabled"] else ui.red)
            extra = ""
            if not info["listening"]:
                extra = ui.dim("  端口未监听")
            ui.say(f"  {color('✓')} {name:<8} {ui.pad(state, 8)} {ui.dim(info['url'])}{extra}")
        ui.say(ui.dim(f"  linger：{'已开启' if autostart.linger_enabled() else '未开启（登录后才会自启）'}"))
        ui.say()

    missing_tools: list[str] = []
    manual_tools: list[str] = []
    for kind, meta in catalog.groups.items():
        tools = catalog.by_kind(kind)
        if not tools:
            continue
        ui.say(ui.bold(meta.get("title", kind)))
        rows = []
        for tool in tools:
            status, version = tool_status(tool, plat, extensions)
            if status == "MISSING":
                missing_tools.append(tool.id)
            elif status == "MANUAL":
                manual_tools.append(tool.id)
            color = ui.green if status == "OK" else (ui.yellow if status == "MANUAL" else ui.red)
            label = tool.method(plat).get("id") if tool.kind == "ext" else tool.bin(plat)
            rows.append([tool.id, color(status), version or "-", label or "-",
                         platforms.which(tool.bin(plat)) or ""])
        ui.say(ui.table(["ID", "状态", "版本", "命令 / 扩展", "路径"], rows))
        ui.say()

    if net:
        ui.say(ui.bold("网络可达性") + ui.dim("（3 秒超时；000 表示需要代理）"))
        hosts = [(entry["host"], 443) for entry in catalog.network]
        results = platforms.check_hosts(hosts)
        for entry in catalog.network:
            reachable = results.get(entry["host"], False)
            marker = ui.green("OK ") if reachable else ui.red("-- ")
            tag = "需代理" if entry.get("proxy") else "直连"
            ui.say(f"  {marker} {entry['host']:<40} {ui.dim(tag)}  {entry.get('label', '')}")
        ui.say()

    if missing_tools:
        ui.say(ui.dim(f"缺少 {len(missing_tools)} 个：fa install <ID>（或 fa install cli）"))
    if manual_tools:
        ui.say(ui.dim(f"需手动确认 {len(manual_tools)} 个：{', '.join(manual_tools)}"))

    if strict and (missing_prereqs or missing_tools):
        return 1
    return 0
