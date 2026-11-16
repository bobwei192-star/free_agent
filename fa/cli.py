"""命令行入口：fa <命令>。"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import sys

from fa import __version__, autostart, doctor, eac_auth, installer, platforms, ui
from fa.catalog import Catalog, CatalogError, Tool, load

EPILOG = """示例：
  fa list                     查看全部工具与安装状态
  fa install cli              安装所有终端 Agent（npm / uv / 官方脚本）
  fa install gemini trae      安装指定工具
  fa run gemini               启动 Gemini CLI（参数原样透传）
  fa doctor --net             体检命令、依赖与网络
  fa login codex              执行某家的登录流程
  fa update                   升级已安装的终端 Agent
  fa autostart dsh            让 DeepSeek Harness 开机自启（systemd --user）
  fa eac --login              完成 EAC 协付车道的 GitHub 授权（登录 + star）
  fa catalog --markdown       生成工具清单文档
"""


# --------------------------------------------------------------------- 工具函数
def _status_color(status: str) -> str:
    if status == "OK":
        return ui.green(status)
    if status == "MANUAL":
        return ui.yellow(status)
    return ui.red(status)


def _method_label(tool: Tool, plat: str) -> str:
    method = tool.method(plat)
    if tool.kind == "ext":
        return str(method.get("id", ""))
    return tool.bin(plat) or "-"


def _print_banner(catalog: Catalog, plat: str) -> None:
    ui.say(ui.bold(f"Free_Agent {__version__}") + ui.dim(f"  ·  {platforms.label(plat)}  ·  清单 {catalog.updated}"))
    ui.say(ui.dim("白嫖 AI Agent 的跨平台部署器：Linux / WSL / Windows"))
    ui.say()
    ui.say(f"  {ui.cyan('fa list')}            查看工具与安装状态")
    ui.say(f"  {ui.cyan('fa install cli')}     一键安装终端 Agent")
    ui.say(f"  {ui.cyan('fa run gemini')}      启动某个 Agent")
    ui.say(f"  {ui.cyan('fa doctor --net')}    体检环境与网络")
    ui.say()
    ui.say(ui.dim("完整命令：fa --help"))


# --------------------------------------------------------------------- list
def cmd_list(args, catalog: Catalog, plat: str) -> int:
    target = args.group or args.target or "all"
    tools = catalog.select([target])
    extensions = platforms.vscode_extensions()

    records = []
    for tool in tools:
        status, version = doctor.tool_status(tool, plat, extensions, with_version=not args.fast)
        if args.installed and status != "OK":
            continue
        records.append({
            "id": tool.id,
            "name": tool.name,
            "vendor": tool.vendor,
            "kind": tool.kind,
            "installed": status == "OK",
            "status": status,
            "version": version,
            "bin": tool.bin(plat),
            "method": installer.describe(tool.method(plat)),
            "free": tool.free,
            "login": tool.login,
            "proxy": tool.proxy_required,
            "docs": tool.docs(),
        })

    if args.json:
        print(json.dumps(records, ensure_ascii=False, indent=2))
        return 0

    if not records:
        ui.warn("没有匹配的工具")
        return 0

    for kind, meta in catalog.groups.items():
        rows = []
        for record in records:
            if record["kind"] != kind:
                continue
            rows.append([
                record["id"],
                _status_color(record["status"]),
                record["version"] or "-",
                "需要" if record["proxy"] else "-",
                ui.truncate(record["free"], 38),
            ])
        if not rows:
            continue
        ui.say(ui.bold(meta.get("title", kind)))
        ui.say(ui.table(["ID", "状态", "版本", "代理", "免费额度"], rows,
                        aligns=["left", "left", "left", "center", "left"]))
        ui.say()

    installed = sum(1 for record in records if record["installed"])
    ui.say(ui.dim(f"共 {len(records)} 个，已安装 {installed} 个。详情：fa info <ID>；安装：fa install <ID>"))
    return 0


# --------------------------------------------------------------------- info
def cmd_info(args, catalog: Catalog, plat: str) -> int:
    tool = catalog.get(args.tool)
    status, version = doctor.tool_status(tool, plat)
    method = tool.method(plat)

    ui.say(ui.bold(f"{tool.id}  ·  {tool.name}"))
    rows = [
        ("厂商", tool.vendor),
        ("类型", catalog.group_title(tool.kind)),
        ("状态", f"{status}  {version}".strip()),
        ("命令", tool.bin(plat) or "-"),
        ("免费额度", tool.free),
        ("登录", tool.login),
        ("网络", "需要代理" if tool.proxy_required else "可直连"),
        ("安装方式", installer.describe(method)),
        ("安装命令", " ".join(installer.command_for(tool, plat) or []) or "-"),
        ("文档", tool.docs() or "-"),
    ]
    width = max(ui.visible_width(label) for label, _ in rows)
    for label, value in rows:
        ui.say(f"  {ui.dim(ui.pad(label, width))}  {value}")
    note = method.get("note")
    if note:
        ui.say(f"  {ui.dim(ui.pad('说明', width))}  {note}")
    if method.get("url") and method["type"] == "manual":
        ui.say(f"  {ui.dim(ui.pad('下载', width))}  {method['url']}")
    return 0


# --------------------------------------------------------------------- install
def cmd_install(args, catalog: Catalog, plat: str) -> int:
    targets = list(args.targets)
    if args.group:
        targets.append(args.group)
    if not targets:
        ui.error("请指定目标：fa install cli / fa install gemini / fa install all")
        return 2

    tools = catalog.select(targets)
    if not tools:
        ui.warn("没有匹配的工具")
        return 0

    if any(target in ("all", "gui") for target in targets) and not args.yes:
        if not ui.confirm(f"即将处理 {len(tools)} 个工具（含 GUI/手动项），继续？"):
            return 1

    ui.say(ui.bold(f"平台 {platforms.label(plat)}  ·  目标 {len(tools)} 个工具"))
    counts: dict[str, int] = {}
    for tool in tools:
        status = installer.install_tool(
            catalog, tool, plat,
            dry_run=args.dry_run, force=args.force,
        )
        counts[status] = counts.get(status, 0) + 1

    ui.say()
    labels = {
        "installed": "已安装", "skip": "已存在", "manual": "需手动",
        "dry": "预演", "blocked": "缺依赖", "failed": "失败",
    }
    summary = "，".join(f"{labels.get(key, key)} {value}" for key, value in sorted(counts.items()))
    ui.say(ui.bold("完成：") + summary)
    if counts.get("failed") or counts.get("blocked"):
        return 1
    return 0


# --------------------------------------------------------------------- run
def cmd_run(args, catalog: Catalog, plat: str) -> int:
    tool = catalog.get(args.tool)
    if tool.kind == "ext":
        ui.error(f"{tool.id} 是编辑器扩展，请在 VS Code 中使用")
        return 2

    binary = tool.bin(plat)
    if not binary:
        ui.error(f"{tool.id} 在 {platforms.label(plat)} 上需要手动启动；请查看 fa info {tool.id}")
        return 2
    if not platforms.has(binary):
        ui.error(f"未找到命令 {binary}；先执行 fa install {tool.id}")
        return 127

    extra = list(args.args)
    if extra and extra[0] == "--":
        extra = extra[1:]
    extra = tool.run_args(plat) + extra

    # 已经有开机自启服务在跑同一个命令时，别再起一份（端口会冲突）
    service = next((key for key, spec in autostart.SERVICES.items() if spec["binary"] == binary), None)
    if service:
        info = autostart.status(service)
        if info["active"]:
            ui.ok(f"{tool.name} 已在运行（开机自启服务 {info['unit']}）")
            ui.say(f"  地址  {info['url']}")
            ui.say(ui.dim(f"  日志  journalctl --user -u {info['unit']} -f"))
            return 0

    path = platforms.which(binary) or binary
    return platforms.exec_replace([path] + extra)


# --------------------------------------------------------------------- doctor
def cmd_doctor(args, catalog: Catalog, plat: str) -> int:
    return doctor.run(catalog, plat, net=args.net, strict=args.strict)


# --------------------------------------------------------------------- login
def cmd_login(args, catalog: Catalog, plat: str) -> int:
    if args.tool:
        tool = catalog.get(args.tool)
        command = tool.login_cmd()
        if command:
            return platforms.exec_replace(shlex.split(command))
        ui.say(f"{ui.bold(tool.id)}：{tool.login}")
        ui.say(ui.dim(f"文档：{tool.docs()}"))
        return 0

    ui.say(ui.bold("登录方式"))
    rows = [[tool.id, tool.login, "需要" if tool.proxy_required else "直连"] for tool in catalog.tools]
    ui.say(ui.table(["ID", "登录", "网络"], rows))
    ui.say()
    ui.say(ui.dim("带登录命令的工具可直接：fa login codex / fa login copilot / fa login qoder"))
    return 0


# --------------------------------------------------------------------- update
def cmd_update(args, catalog: Catalog, plat: str) -> int:
    if args.targets:
        tools = catalog.select(args.targets)
    else:
        tools = catalog.by_kind("cli")

    ui.say(ui.bold(f"升级（{platforms.label(plat)}）"))
    counts: dict[str, int] = {}
    for tool in tools:
        status = installer.update_tool(tool, plat, dry_run=args.dry_run)
        counts[status] = counts.get(status, 0) + 1

    labels = {"updated": "已升级", "skip": "未安装", "manual": "需手动", "dry": "预演", "failed": "失败"}
    ui.say()
    ui.say(ui.bold("完成：") + "，".join(f"{labels.get(k, k)} {v}" for k, v in sorted(counts.items())))
    return 1 if counts.get("failed") else 0


# --------------------------------------------------------------------- proxy
def cmd_proxy(args, catalog: Catalog, plat: str) -> int:
    url = f"http://{args.host}:{args.port}"
    ui.say(ui.bold("代理环境变量"))
    if plat == "windows":
        ui.say(f"  $env:HTTP_PROXY  = \"{url}\"")
        ui.say(f"  $env:HTTPS_PROXY = \"{url}\"")
        ui.say(f"  $env:ALL_PROXY   = \"{url}\"")
        ui.say()
        ui.say(ui.dim(f"  只在本次会话生效；单条命令：$env:HTTPS_PROXY=\"{url}\"; fa run gemini"))
    else:
        ui.say(f"  export http_proxy={url}")
        ui.say(f"  export https_proxy={url}")
        ui.say(f"  export all_proxy={url}")
        ui.say()
        ui.say(ui.dim(f"  单条命令：https_proxy={url} fa run gemini"))

    current = {key: value for key, value in {
        "HTTP_PROXY": os.environ.get("HTTP_PROXY"),
        "HTTPS_PROXY": os.environ.get("HTTPS_PROXY"),
        "ALL_PROXY": os.environ.get("ALL_PROXY"),
    }.items() if value}
    if current:
        ui.say()
        ui.say(ui.green("当前已设置：") + ", ".join(f"{k}={v}" for k, v in current.items()))
    return 0


# --------------------------------------------------------------------- autostart
def cmd_autostart(args, catalog: Catalog, plat: str) -> int:
    name = autostart.resolve(args.service)
    if not name:
        ui.error(f"未知服务 {args.service}；可用：{', '.join(sorted(autostart.SERVICES))}")
        return 2

    if plat not in ("linux", "wsl"):
        ui.error(f"开机自启动目前只支持 systemd --user（Linux / WSL），当前平台：{platforms.label(plat)}")
        return 2

    if args.disable:
        ok_flag, detail = autostart.disable(name)
        if ok_flag:
            ui.ok(f"已停用 {detail}")
            return 0
        ui.error(detail)
        return 1

    if args.status:
        info = autostart.status(name)
        rows = [
            ("服务", info["title"]),
            ("单元", info["unit"]),
            ("单元文件", info["unit_file"]),
            ("已安装", "是" if info["installed"] else "否"),
            ("已启用", "是" if info["enabled"] else "否"),
            ("运行中", "是" if info["active"] else "否"),
            ("端口监听", "是" if info["listening"] else "否"),
            ("linger（不登录也自启）", "是" if info["linger"] else "否"),
            ("地址", info["url"]),
        ]
        width = max(ui.visible_width(label) for label, _ in rows)
        for label, value in rows:
            ui.say(f"  {ui.dim(ui.pad(label, width))}  {value}")
        return 0

    proxy_port = None if args.no_proxy else (args.proxy_port or autostart.detect_proxy_port())
    ok_flag, detail = autostart.enable(name, port=args.port, proxy_port=proxy_port)
    if not ok_flag:
        ui.error(detail)
        return 1

    ui.ok(f"{autostart.SERVICES[name]['title']} 已设置开机自启动")
    ui.say(f"  单元文件  {detail}")
    ui.say(f"  代理环境  {'http://127.0.0.1:' + str(proxy_port) if proxy_port else '未设置（直连）'}")
    ui.say(f"  地址      http://127.0.0.1:{args.port or autostart.SERVICES[name]['port']}/")
    ui.say()
    ui.say(ui.dim("查看日志：journalctl --user -u %s -f" % autostart.SERVICES[name]["unit"]))
    ui.say(ui.dim("停用自启：fa autostart %s --disable" % name))
    return 0


# --------------------------------------------------------------------- eac 授权
def cmd_eac(args, catalog: Catalog, plat: str) -> int:
    try:
        client = eac_auth.connect(args.port, args.token)
        if args.collect:
            ui.say(ui.dim(f"领取授权（link={ui.truncate(args.collect, 20)}），最长等 {args.timeout:g} 秒……"))
            outcome = eac_auth.wait(client, args.collect, args.timeout)
        elif args.login:
            started = eac_auth.start_login(client)
            link = str(started.get("link") or "")
            url = str(started.get("url") or "")
            if not link:
                ui.error(f"插件没返回授权链接：{started}")
                return 1
            ui.say(ui.bold("授权链接：") + ui.cyan(url))
            ui.say(ui.dim(f"link={ui.truncate(link, 24)}  仓库={eac_auth.DEFAULT_REPO}"))
            if started.get("opened") is not True and not args.no_open:
                import webbrowser

                webbrowser.open(url)
            ui.say()
            ui.say(ui.dim(f"浏览器里登录 GitHub 并 star 仓库后自动确认，最长等 {args.timeout:g} 秒……"))
            ui.say(ui.dim("没赶上这一轮也别重开登录：稍后用 `fa eac --collect " + link + "` 领取。"))
            outcome = eac_auth.wait(client, link, args.timeout)
        else:
            outcome = eac_auth.status(client)
    except eac_auth.EacError as exc:
        ui.error(str(exc))
        return 1

    if args.json:
        print(json.dumps(outcome, ensure_ascii=False, indent=2))
        return 0

    state = str(outcome.get("status") or "")
    if state == "ok":
        ui.ok(f"授权成功：@{outcome.get('login', '')}")
        return 0
    if state == "unstarred":
        ui.warn(f"已登录 @{outcome.get('login', '')}，但还没 star 仓库；star 后重新执行 `fa eac --collect <link>`")
        return 1
    if state == "expired":
        ui.warn("这次登录已过期，重新执行 `fa eac --login`")
        return 1
    if "error" in outcome:
        ui.error(f"授权未完成：{outcome['error']}")
        return 1
    if state == "pending":
        ui.warn("仍在等待你在浏览器里完成 GitHub 登录 + star")
        return 1

    rows = eac_auth.describe(outcome)
    width = max(ui.visible_width(label) for label, _ in rows)
    for label, value in rows:
        ui.say(f"  {ui.dim(ui.pad(label, width))}  {value}")
    if outcome.get("authorized") is True:
        ui.say()
        ui.ok("EAC 车道已解锁，可以直接选 EAC 模型")
    elif outcome.get("required") is True:
        ui.say()
        ui.warn("EAC 模型需要 GitHub 登录 + star；执行 `fa eac --login` 完成授权（免费车道不受影响）")
    return 0 if outcome.get("authorized") is True else 1


# --------------------------------------------------------------------- catalog
def _escape_cell(text: str) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ")


def _markdown(catalog: Catalog) -> str:
    lines = [
        "# 工具清单",
        "",
        f"> 由 `fa catalog --markdown` 从 `catalog/tools.json` 生成（{catalog.updated}）。",
        "> 修改清单请编辑 JSON，再重新生成本文件。",
        "",
    ]
    for kind, meta in catalog.groups.items():
        tools = catalog.by_kind(kind)
        if not tools:
            continue
        lines += [
            f"## {meta.get('title', kind)}",
            "",
            "| ID | 工具 | 厂商 | 免费额度 | 登录方式 | 代理 | Linux / WSL | Windows |",
            "|---|---|---|---|---|---|---|---|",
        ]
        for tool in tools:
            name = f"[{tool.name}]({tool.docs()})" if tool.docs() else tool.name
            lines.append("| " + " | ".join(_escape_cell(cell) for cell in [
                f"`{tool.id}`",
                name,
                tool.vendor,
                tool.free,
                tool.login,
                "需要" if tool.proxy_required else "-",
                installer.describe(tool.method("linux")),
                installer.describe(tool.method("windows")),
            ]) + " |")
        lines.append("")
    return "\n".join(lines)


def cmd_catalog(args, catalog: Catalog, plat: str) -> int:
    if args.json:
        print(json.dumps(catalog.data, ensure_ascii=False, indent=2))
        return 0
    if args.markdown:
        print(_markdown(catalog))
        return 0
    ui.say(ui.bold(f"清单 {catalog.path}"))
    ui.say(f"  更新日期  {catalog.updated}")
    for kind, meta in catalog.groups.items():
        ui.say(f"  {meta.get('title', kind):<12} {len(catalog.by_kind(kind))} 个")
    ui.say()
    ui.say(ui.dim("fa catalog --markdown > docs/catalog.md    # 重新生成文档"))
    return 0


# --------------------------------------------------------------------- version / help
def cmd_version(args, catalog: Catalog | None, plat: str) -> int:
    ui.say(f"Free_Agent {__version__}")
    ui.say(f"平台      {platforms.label(plat)}")
    if catalog:
        ui.say(f"清单      {catalog.path}（{catalog.updated}）")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fa",
        description="Free_Agent —— 在 Linux / WSL / Windows 上快速部署白嫖 AI Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=EPILOG,
    )
    parser.add_argument("--no-color", action="store_true", help="关闭颜色输出")
    parser.add_argument("--catalog", help="指定 tools.json 路径")
    parser.add_argument("--version", action="store_true", help="显示版本")
    sub = parser.add_subparsers(dest="command", metavar="<命令>")

    p = sub.add_parser("list", aliases=["ls"], help="列出工具与安装状态")
    p.add_argument("target", nargs="?", default="all", help="组名（cli/gui/ext/all）或工具 ID")
    p.add_argument("--group", choices=("cli", "gui", "ext", "all"), help="按组过滤")
    p.add_argument("--installed", action="store_true", help="只看已安装")
    p.add_argument("--fast", action="store_true", help="不查询版本号")
    p.add_argument("--json", action="store_true", help="输出 JSON")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("info", help="查看单个工具的详细信息")
    p.add_argument("tool")
    p.set_defaults(func=cmd_info)

    p = sub.add_parser("install", aliases=["add"], help="安装工具")
    p.add_argument("targets", nargs="*", help="工具 ID / 组名（cli/gui/ext）/ all")
    p.add_argument("-y", "--yes", action="store_true", help="跳过确认")
    p.add_argument("--force", action="store_true", help="已安装也重新执行")
    p.add_argument("--dry-run", action="store_true", help="只打印命令，不执行")
    p.add_argument("--group", choices=("cli", "gui", "ext", "all"), help="按组安装")
    p.set_defaults(func=cmd_install)

    p = sub.add_parser("run", help="启动工具（参数原样透传）")
    p.add_argument("tool")
    p.add_argument("args", nargs=argparse.REMAINDER)
    p.set_defaults(func=cmd_run)

    p = sub.add_parser("doctor", help="体检命令、依赖与网络")
    p.add_argument("--net", action="store_true", help="检测关键域名可达性")
    p.add_argument("--strict", action="store_true", help="有缺失时返回非零退出码")
    p.set_defaults(func=cmd_doctor)

    p = sub.add_parser("login", help="查看或执行登录流程")
    p.add_argument("tool", nargs="?")
    p.set_defaults(func=cmd_login)

    p = sub.add_parser("update", help="升级已安装的工具")
    p.add_argument("targets", nargs="*", help="默认升级全部终端 Agent")
    p.add_argument("--dry-run", action="store_true", help="只打印命令")
    p.set_defaults(func=cmd_update)

    p = sub.add_parser("proxy", help="打印代理环境变量用法")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=7890)
    p.set_defaults(func=cmd_proxy)

    p = sub.add_parser("autostart", help="配置开机自启动（systemd --user）")
    p.add_argument("service", nargs="?", default="dsh", help="服务名（dsh）")
    p.add_argument("--port", type=int, help="监听端口（dsh 默认 3080）")
    p.add_argument("--proxy-port", type=int, help="本地 HTTP 代理端口（默认自动探测）")
    p.add_argument("--no-proxy", action="store_true", help="不注入代理环境变量")
    p.add_argument("--disable", action="store_true", help="停用开机自启")
    p.add_argument("--status", action="store_true", help="查看开机自启状态")
    p.set_defaults(func=cmd_autostart)

    p = sub.add_parser("eac", help="EAC 协付车道：查看/完成 GitHub 授权")
    p.add_argument("--login", action="store_true", help="发起 GitHub 登录并等待授权完成")
    p.add_argument("--collect", metavar="LINK", help="领取此前一次登录的授权（link）")
    p.add_argument("--timeout", type=float, default=240, help="等待秒数（默认 240）")
    p.add_argument("--no-open", action="store_true", help="不自动打开浏览器")
    p.add_argument("--port", type=int, help="dsh Web UI 端口（默认读单元文件，回落 3080）")
    p.add_argument("--token", help="访问令牌（默认从 journal / ~/.dsh/logs 里找）")
    p.add_argument("--json", action="store_true", help="输出原始 JSON 状态")
    p.set_defaults(func=cmd_eac)

    p = sub.add_parser("catalog", help="查看或导出工具清单")
    p.add_argument("--markdown", action="store_true", help="输出 Markdown 表格")
    p.add_argument("--json", action="store_true", help="输出原始 JSON")
    p.set_defaults(func=cmd_catalog)

    p = sub.add_parser("version", help="显示版本")
    p.set_defaults(func=cmd_version)

    p = sub.add_parser("help", help="显示帮助")
    p.set_defaults(func=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    ui.configure(False if args.no_color else None)
    plat = platforms.detect()

    if args.version:
        args.command = "version"
        args.func = cmd_version

    if not getattr(args, "command", None):
        try:
            catalog = load(args.catalog)
        except CatalogError as exc:
            ui.error(str(exc))
            return 2
        _print_banner(catalog, plat)
        return 0

    if args.command == "help":
        parser.print_help()
        return 0

    catalog = None
    try:
        catalog = load(args.catalog)
    except CatalogError as exc:
        if args.command != "version":
            ui.error(str(exc))
            return 2

    try:
        return args.func(args, catalog, plat)
    except CatalogError as exc:
        ui.error(str(exc))
        return 2
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
