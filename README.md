# Free_Agent

在 **Linux / WSL / Windows PowerShell** 上快速部署「白嫖」AI Agent 工具的跨平台部署器。

一套工具清单（catalog）+ 一个命令行（`fa`）+ 两个安装器（`install.sh` / `install.ps1`），
把各家终端 Agent、桌面 IDE、VS Code 扩展的**安装、启动、登录、体检、升级**收敛到同一套命令里。

```
23 个终端 Agent   ·   6 个桌面 IDE   ·   15 个 VS Code 扩展   ·   3 个平台
```

## 特性

- **一份清单，三个平台**：`catalog/tools.json` 声明每个工具的 Linux / WSL / Windows 安装方式，CLI 自动选路。
- **不改系统**：Linux / WSL 默认免 root（`~/.local/bin` + `npm -g` / `uv tool`），Windows 只写用户级 PATH。
- **幂等**：已安装自动跳过，`--force` 重装，`--dry-run` 先看命令再执行。
- **可体检**：`fa doctor --net` 一次看清命令、前置依赖、关键域名是否可达（是否需要代理）。
- **白嫖信息内置**：每个工具的免费额度、登录方式、是否需要代理都写在清单里，`fa info` 直接查。
- **纯标准库**：CLI 只依赖 Python 3.9+，没有第三方包。

## 平台支持

| 能力 | Linux | WSL | Windows |
|---|---|---|---|
| 终端 Agent（npm / uv / 官方脚本） | ✅ | ✅ | ✅（npm / winget） |
| 桌面 IDE | ✅ 免 root 解包或系统包 | ⚠️ 依赖 WSLg，建议装 Windows 原生 | ✅ winget / 官方安装器 |
| VS Code 扩展 | ✅ | ✅ | ✅ |
| 代理环境变量 | ✅ bash | ✅ bash | ✅ PowerShell |

> 免费额度、登录方式以各家官网当日政策为准；本项目只做部署编排，不绕过任何限制。

## 快速开始

### Linux / WSL / macOS

```bash
cd ~/Free_Agent
./install.sh            # 安装 fa 到 ~/.local/bin（已在 PATH 时不会改 rc 文件）
fa doctor --net         # 检查 Python / Node / uv 与网络
fa install cli          # 安装全部终端 Agent（缺依赖的会提示）
fa run gemini           # 启动；首次运行按提示登录
```

### 开机自启动（Linux / WSL）

把 DeepSeek Harness 的 Web UI（`http://127.0.0.1:3080/`）注册成 systemd 用户服务，开机自动拉起：

```bash
fa autostart dsh                # 写入 ~/.config/systemd/user/dsh-web.service 并 enable --now
fa autostart dsh --status       # 看是否启用 / 运行中 / 端口监听
fa autostart dsh --disable      # 停用并停止
journalctl --user -u dsh-web.service -f   # 看日志
```

要点：

- 单元写在**用户级** `~/.config/systemd/user/`，不需要 sudo，不污染系统目录；
- 自动 `loginctl enable-linger`，**不登录桌面也会开机自启**；
- 自动探测本机 HTTP 代理端口（环境变量 → clash 常见端口），写进单元的 `Environment=`；需要直连时加 `--no-proxy`；
- 端口由 `--port` 指定（默认 3080），只监听回环地址；
- 浏览器首访问用 dsh 打印的 `?token=` 链接换 30 天 Cookie，之后直接开 `http://127.0.0.1:3080/` 即可。
- `fa doctor` 里有一栏「开机自启」，随时能看到自启服务是否启用 / 运行中 / 端口是否监听。

### Windows PowerShell

```powershell
cd $HOME\Free_Agent
powershell -ExecutionPolicy Bypass -File .\install.ps1
fa doctor --net
fa install cli
fa run qwen
```

前置条件：Python 3.9+（`winget install Python.Python.3.12`）、Node.js 18+（`winget install OpenJS.NodeJS.LTS`）。
`fa doctor` 会逐项告诉你缺什么、怎么装。

### 可选：作为 Python 包安装

```bash
pipx install .
# 或
uv tool install .
```

安装后 `fa` 直接来自 console script，不依赖仓库路径。

## 命令速查

| 命令 | 说明 |
|---|---|
| `fa` / `fa help` | 概览与完整帮助 |
| `fa list [cli\|gui\|ext\|all]` | 工具列表：状态、版本、是否需代理、免费额度 |
| `fa list --json` | 机器可读输出（便于脚本 / CI） |
| `fa info <id>` | 单个工具详情：安装命令、登录方式、文档 |
| `fa install <id\|组\|all>` | 安装；`--dry-run` 预演、`--force` 重装、`-y` 免确认 |
| `fa run <id> [参数...]` | 启动工具，参数原样透传（POSIX 下 `exec`，TUI 正常） |
| `fa login [id]` | 查看登录方式；有登录命令的直接执行 |
| `fa doctor [--net] [--strict]` | 体检命令、依赖、网络；`--strict` 有缺失时非零退出 |
| `fa update [id...]` | 升级已安装工具（npm / uv / 自带 updater） |
| `fa autostart dsh [--port 3080] [--disable] [--status]` | DeepSeek Harness 开机自启（systemd --user） |
| `fa proxy [--port 7890]` | 打印 bash / PowerShell 代理写法 |
| `fa catalog --markdown` | 由 JSON 重新生成 `docs/catalog.md` |

`make` 仍然可用，只是 `fa` 的便捷封装：`make install-cli`、`make list`、`make doctor`、`make gemini`。

## 工具清单

完整表格（免费额度 / 登录 / 各平台安装方式）见 [docs/catalog.md](docs/catalog.md)。

- **终端 Agent**：Gemini CLI、Qwen Code、Copilot CLI、Codex、Claude Code、Amp、Cursor Agent、Kiro、Droid、CodeBuddy、Qoder、iFlow、Antigravity CLI、Vibe、Kimi、Aider、Crush、Cline、Continue、CodeBuff、OpenCode、豆包 Seed（Ark）、豆包 CLI（官方）
- **桌面 IDE**：Cursor、TRAE CN、Qoder CN、WorkBuddy、Antigravity、VS Code
- **VS Code 扩展**：Claude Code、Cline、Kilo Code、Continue、CodeBuddy、Comate、MarsCode、通义灵码、Gemini Code Assist、Amazon Q、Cody、CodeGeeX、Tabnine、Augment、iFlow

> 豆包两条路线：`doubao` 走火山方舟 API（本机包装脚本 `~/.local/bin/doubao`，在 `~/.config/free_agent/ark.env` 填 `ARK_API_KEY` 即可，模型默认 `doubao-seed-2-1-pro-260915`）；`doubao-cli` 是官方 CLI，需要豆包企业账号，个人账号扫码会报 `login_required`。

```bash
fa info qwen         # 看某家的免费额度和登录方式
fa list --installed  # 只看已装
```

## 项目结构

```
Free_Agent/
├── catalog/tools.json     # 唯一事实来源：工具、免费额度、各平台安装方式、网络端点
├── fa/                    # 跨平台 CLI（纯标准库）
│   ├── cli.py             #   命令解析
│   ├── catalog.py         #   清单加载 / 校验 / 平台回退
│   ├── installer.py       #   命令拼装与执行
│   ├── doctor.py          #   体检
│   ├── autostart.py       #   systemd --user 开机自启（dsh web）
│   ├── platforms.py       #   平台探测、命令执行、网络探测
│   └── ui.py              #   颜色与中英混排表格
├── fa.sh                  # POSIX 启动器（被 install.sh 链接为 fa）
├── install.sh             # Linux / WSL / macOS 安装器
├── install.ps1            # Windows PowerShell 安装器
├── tests/                 # 单元测试（不联网）
├── docs/                  # 平台说明、网络、排错、清单、变更日志
├── Makefile               # make 便捷入口
└── pyproject.toml         # 可 pipx / uv 安装
```

## 自定义工具

编辑 `catalog/tools.json`，加一条即可，CLI 会自动出现在 `list` / `install` 里：

```json
{
  "id": "mytool",
  "name": "My Agent",
  "vendor": "Acme",
  "kind": "cli",
  "bins": "mytool",
  "free": "注册送额度",
  "login": "mytool login",
  "login_cmd": "mytool login",
  "proxy": false,
  "docs": "https://example.com",
  "install": {
    "default": { "type": "npm", "pkg": "@acme/mytool" },
    "windows": { "type": "winget", "id": "Acme.MyTool" }
  }
}
```

支持的安装类型：`npm`、`uv`、`pipx`、`script`（bash 官方脚本）、`pwsh`、`winget`、`vscode-ext`、`manual`。
平台回退顺序：`windows` → `default`；`wsl` → `linux` → `default`；`macos` → `linux` → `default`。
改完运行 `make docs` 同步文档、`make test` 校验清单。

## 开发

```bash
python3 -m unittest discover -s tests -v
./fa.sh list --fast
./fa.sh install cli --dry-run
```

CI 在 Ubuntu 与 Windows 上跑同一套测试（见 `.github/workflows/ci.yml`）。

## 文档

- [平台部署说明](docs/platforms.md) —— 三个平台的差异、GUI 安装、Electron 沙箱
- [工具清单](docs/catalog.md) —— 全部工具的免费额度 / 登录 / 安装方式
- [网络与账号](docs/network.md) —— 直连 / 代理清单、注册优先级
- [排错手册](docs/troubleshooting.md) —— 常见报错与处理
- [变更日志](docs/journal.md)

## 说明

- 本项目只负责安装与启动编排；账号、订阅、额度以各家官方为准，请遵守各自服务条款。
- 部分国内工具需要手机号 / 扫码登录，CLI 无法代劳，`fa login` 会提示。
- 无 root 环境下的 Electron 应用统一以 `--no-sandbox` 启动，详见 [平台说明](docs/platforms.md)。

## License

[MIT](LICENSE)
