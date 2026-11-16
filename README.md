# Free_Agent

[![CI](https://github.com/bobwei192-star/free_agent/actions/workflows/ci.yml/badge.svg)](https://github.com/bobwei192-star/free_agent/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org)

在 **Linux / WSL / Windows（PowerShell）/ macOS** 上快速部署「白嫖」AI Agent 工具的跨平台部署器。

一套工具清单（catalog）+ 一个命令行（`fa`）+ 两个安装器（`install.sh` / `install.ps1`），
把各家终端 Agent、桌面 IDE、VS Code 扩展的**安装、启动、登录、体检、升级、开机自启**收敛到同一套命令里。

```
24 个终端 Agent   ·   6 个桌面 IDE   ·   15 个 VS Code 扩展   ·   共 45 个工具
```

> 30 秒上手：`./install.sh` → `fa doctor --net` → `fa install cli` → `fa run qwen`

## 目录

- [特性](#特性)
- [平台支持](#平台支持)
- [快速开始](#快速开始)
- [命令详解](#命令详解)
- [工具清单](#工具清单)
- [OpenCode 使用指南](#opencode-使用指南)
- [典型工作流](#典型工作流)
- [登录指南](#登录指南)
- [网络与代理](#网络与代理)
- [开机自启（DeepSeek Harness Web UI）](#开机自启deepseek-harness-web-ui)
- [自定义工具](#自定义工具)
- [项目结构](#项目结构)
- [开发指南](#开发指南)
- [常见问题 FAQ](#常见问题-faq)
- [文档](#文档)
- [说明与免责](#说明与免责)
- [License](#license)

## 特性

- **一份清单，多个平台**：`catalog/tools.json` 是唯一事实来源，声明每个工具的 Linux / WSL / Windows / macOS 安装方式，CLI 自动选路。
- **不改系统**：Linux / WSL / macOS 默认免 root（`~/.local/bin` + `npm -g` / `uv tool`），Windows 只写用户级 PATH。
- **幂等**：已安装自动跳过，`--force` 重装，`--dry-run` 先看命令再执行。
- **可体检**：`fa doctor --net` 一次看清命令、前置依赖、关键域名是否可达（是否需要代理）、开机自启状态。
- **白嫖信息内置**：每个工具的免费额度、登录方式、是否需要代理都写在清单里，`fa info` 直接查。
- **开机自启**：`fa autostart dsh` 把 DeepSeek Harness Web UI 注册成 systemd 用户服务，不登录桌面也能开机自启。
- **纯标准库**：CLI 只依赖 Python 3.9+，没有第三方包；`pipx` / `uv tool` 也能装。
- **有测试有 CI**：30 个离线单元测试，GitHub Actions 在 Ubuntu + Windows × Python 3.9/3.12 上跑，并校验清单文档同步。

## 平台支持

| 能力 | Linux | WSL | Windows | macOS |
|---|---|---|---|---|
| 终端 Agent（npm / uv / 官方脚本） | ✅ | ✅ | ✅（npm / winget / pwsh） | ✅（回退 linux 方式） |
| 桌面 IDE | ✅ 免 root 解包或系统包 | ⚠️ 依赖 WSLg，建议装 Windows 原生 | ✅ winget / 官方安装器 | ⚠️ 官网安装器 |
| VS Code 扩展 | ✅ | ✅ | ✅ | ✅ |
| 代理环境变量 | ✅ bash | ✅ bash | ✅ PowerShell | ✅ bash |
| 开机自启（systemd --user） | ✅ | ✅ | ✗ | ✗ |

平台自动判定：`win32 → windows`；`/proc/version` 含 microsoft 或有 `WSL_DISTRO_NAME → wsl`；`darwin → macos`；其余 `linux`。
安装方式回退顺序：`windows → default`；`wsl → linux → default`；`macos → linux → default`。

> 免费额度、登录方式以各家官网当日政策为准；本项目只做部署编排，不绕过任何限制。

## 快速开始

### Linux / WSL / macOS

```bash
git clone https://github.com/bobwei192-star/free_agent.git ~/Free_Agent
cd ~/Free_Agent
./install.sh            # 安装 fa 到 ~/.local/bin（已在 PATH 时不会改 rc 文件）
fa doctor --net         # 检查 Python / Node / uv 与网络
fa install cli          # 安装全部终端 Agent（缺依赖的会提示）
fa run gemini           # 启动；首次运行按提示登录
```

安装器行为（详见 [docs/platforms.md](docs/platforms.md)）：

1. 校验 Python 3.9+（可用 `PYTHON` 环境变量指定解释器）；
2. 建立符号链接 `~/.local/bin/fa → 仓库/fa.sh`（目录可用 `FREE_AGENT_BIN_DIR` 改）；
3. 仅当 `~/.local/bin` 不在 PATH 时，往已存在的 `~/.profile` / `~/.bashrc` / `~/.zshrc` 追加带标记的 PATH 段。

可选：`./install.sh --doctor` 安装后直接体检。

### Windows PowerShell

```powershell
git clone https://github.com/bobwei192-star/free_agent.git $HOME\Free_Agent
cd $HOME\Free_Agent
powershell -ExecutionPolicy Bypass -File .\install.ps1
fa doctor --net
fa install cli
fa run qwen
```

前置条件：Python 3.9+（`winget install Python.Python.3.12`）、Node.js 18+（`winget install OpenJS.NodeJS.LTS`）。
安装器生成 `%USERPROFILE%\.local\bin\fa.cmd` 并把该目录写入**用户级** PATH；`fa doctor` 会逐项告诉你缺什么、怎么装。
可选参数：`-BinDir <目录>`、`-Doctor`。

### 作为 Python 包安装（可选）

```bash
pipx install .
# 或
uv tool install .
```

安装后 `fa` 直接来自 console script，不依赖仓库路径；清单随包安装到 `share/free-agent/tools.json`。

### 验证安装

```bash
fa version              # 版本 + 平台 + 清单路径
fa list --fast          # 45 个工具的状态总览（不查版本号，快）
fa doctor --net         # 依赖 + 网络 + 自启服务体检
```

不装启动器也能用：仓库根目录 `./fa.sh <命令>`（POSIX）或 `python -m fa <命令>`（任意平台）。

## 命令详解

```
fa [--no-color] [--catalog 路径] <命令> [参数...]
```

全局选项：

| 选项 | 说明 |
|---|---|
| `--no-color` | 关闭彩色输出（也认 `NO_COLOR` 环境变量；非 TTY 自动关闭） |
| `--catalog <路径>` | 指定另一份 `tools.json`（也认 `FREE_AGENT_CATALOG` 环境变量） |
| `--version` | 显示版本 |

### fa list —— 工具列表

```bash
fa list                 # 全部工具：状态 / 版本 / 是否需代理 / 免费额度
fa list cli             # 只看终端 Agent（gui / ext / all 同理）
fa list gemini          # 只看某个工具
fa list --installed     # 只看已安装
fa list --fast          # 不执行 --version 查询，秒出
fa list --json          # 机器可读 JSON（脚本 / CI 用）
```

别名 `fa ls`。状态含义：`OK` 已安装、`MISSING` 未安装、`MANUAL` 该平台需手动安装。

### fa info —— 单个工具详情

```bash
fa info qwen            # 厂商 / 免费额度 / 登录方式 / 是否需代理 / 安装命令 / 文档
fa info trae            # manual 类型会给出下载地址和注意事项
```

### fa install —— 安装

```bash
fa install cli                  # 按组安装：cli / gui / ext
fa install gemini qwen aider    # 按 ID 安装，可多个
fa install all                  # 全部（含 GUI / 手动项，会先确认）
fa install cli --dry-run        # 只打印将执行的命令，不执行
fa install gemini --force       # 已安装也重新执行
fa install cli -y               # 跳过确认（脚本 / CI）
```

别名 `fa add`。行为细节：

- **幂等**：已安装的跳过并提示 `--force`；
- **缺前置依赖**（npm / uv / pipx / code / winget / bash）时不执行，打印对应平台的安装提示，计为 `blocked`；
- `manual` 类型打印官网地址与说明，计为 `manual`，不算失败；
- 目标含 `all` / `gui` 且未加 `-y` 时交互确认（非 TTY 自动继续）；
- 结束打印汇总：`已安装 / 已存在 / 需手动 / 预演 / 缺依赖 / 失败`。

### fa run —— 启动

```bash
fa run gemini                   # 启动 Gemini CLI
fa run qwen --help              # 参数原样透传
fa run codex -- --model o3      # 用 -- 分隔 fa 与工具参数（可选）
fa run dsh-free-model           # 自动带上清单里的 run_args（dsh web）
```

- POSIX 下用 `exec` 替换当前进程，TUI / 交互完全正常；Windows 下子进程运行并透传退出码；
- 未安装提示 `fa install <id>`（退出码 127）；扩展类（ext）提示去 VS Code 里用；
- 若该工具已有开机自启服务在运行（如 dsh），**不会重复起一份**，直接打印服务地址和日志命令。

`make <工具ID>` 是等价便捷写法：`make gemini ARGS="--help"`。

### fa login —— 登录

```bash
fa login                # 一览表：每家的登录方式 + 是否需代理
fa login codex          # 有登录命令的直接执行（codex login）
fa login qwen           # 无登录命令的打印指引（qwen → /auth 选 Qwen OAuth）
```

内置登录命令的工具：`copilot`、`codex`、`amp`、`cursor-agent`、`kiro`、`qoder`、`doubao-cli`。
其余工具在首次运行时按提示登录，详见 [登录指南](#登录指南)。

### fa doctor —— 体检

```bash
fa doctor               # 平台 / Python / 启动器 / 前置依赖 / 每个工具的状态与路径
fa doctor --net         # 追加并发探测 19 个关键域名（3 秒超时）
fa doctor --strict      # 有缺失（依赖或工具）时退出码 1，可用于 CI 门禁
```

输出分节：前置依赖（按平台裁剪，只检查清单实际用到的）、开机自启（Linux / WSL 且 systemd 可用时）、
三组工具状态表、网络可达性（`OK` 可直连 / `--` 需要代理）。

### fa update —— 升级

```bash
fa update               # 升级全部已安装的终端 Agent
fa update gemini qwen   # 只升级指定工具
fa update --dry-run     # 只看命令
```

升级策略：清单有 `update_cmd` 的优先用自带 updater（`agent update` / `droid update` / `opencode upgrade` / `agy update` / `doubao-cli update`）；
否则 npm 包 `@latest` 重装、uv / pipx `upgrade`、winget `upgrade`。未安装的跳过；script / manual 且无 updater 的提示手动升级。

### fa proxy —— 代理写法

```bash
fa proxy                        # 按当前平台打印 bash / PowerShell 代理环境变量写法
fa proxy --port 7897            # 自定义端口（默认 127.0.0.1:7890）
fa proxy --host 192.168.1.5     # 自定义主机
```

同时回显当前会话已设置的 `HTTP_PROXY` / `HTTPS_PROXY` / `ALL_PROXY`。详见 [网络与代理](#网络与代理)。

### fa autostart —— 开机自启

```bash
fa autostart dsh                # 写入用户级 systemd 单元并 enable --now
fa autostart dsh --status       # 已安装 / 已启用 / 运行中 / 端口监听 / linger / 地址
fa autostart dsh --disable      # 停用并停止
fa autostart dsh --port 4000    # 自定义监听端口（默认 3080）
fa autostart dsh --proxy-port 7897   # 显式指定本地 HTTP 代理端口
fa autostart dsh --no-proxy     # 不注入代理环境变量（直连）
```

服务名可用别名 `dsh-web` / `harness`。仅支持 Linux / WSL（systemd --user）。完整说明见 [开机自启](#开机自启deepseek-harness-web-ui)。

### fa catalog —— 清单查看 / 导出

```bash
fa catalog                      # 清单路径 / 更新日期 / 各组数量
fa catalog --json               # 原始 JSON
fa catalog --markdown           # 生成 Markdown 表格
make docs                       # 等价于 fa catalog --markdown > docs/catalog.md
```

### fa version / fa help

```bash
fa version              # 版本 / 平台 / 清单路径与更新日期
fa help                 # 完整帮助（fa --help 等价）
fa                      # 概览横幅 + 常用命令提示
```

### 退出码约定

| 码 | 含义 |
|---|---|
| 0 | 成功 |
| 1 | 有失败 / 缺依赖（install、update）；`doctor --strict` 有缺失；确认被拒绝 |
| 2 | 用法错误：未知工具 / 目标、缺少参数、平台不支持 |
| 127 | `fa run` 找不到命令（未安装） |
| 130 | Ctrl-C 中断 |

## 工具清单

完整表格（免费额度 / 登录 / 各平台安装方式）见 **[docs/catalog.md](docs/catalog.md)**（由清单自动生成）。
随时用 `fa info <id>` 查单个工具，`fa list --json` 拿结构化数据。

### 终端 Agent（24 个）

| 分类 | ID |
|---|---|
| 国内直连，注册即用 | `qwen`（Qwen Code）、`iflow`（心流）、`codebuddy`（腾讯）、`qoder`（Qoder CLI）、`doubao`（豆包 Seed / 火山方舟）、`doubao-cli`（豆包官方，需企业账号） |
| 海外免费档，需代理 | `gemini`（Google）、`copilot`（GitHub）、`codex`（OpenAI）、`claude`（Anthropic，无免费档）、`cursor-agent`、`kiro`（AWS）、`agy`（Antigravity CLI）、`vibe`（Mistral） |
| 直连 / 部分需代理 | `amp`（Sourcegraph）、`droid`（Factory）、`kimi`（月之暗面）、`crush`（Charm）、`codebuff` |
| BYOK（自带 Key / 任意端点） | `aider`、`cline`、`continue`、`opencode` |
| 本地免费推理 | `dsh-free-model`（DeepSeek Harness，免费 token 按出口 IP 计，Web UI 可开机自启） |

### 桌面 IDE（6 个）

`cursor`、`trae`（TRAE CN）、`qoder-ide`（Qoder CN）、`workbuddy`（腾讯）、`antigravity`（Google）、`vscode`。
Linux 免 root 解包到 `~/.local/opt/`，包装脚本在 `~/.local/bin/`；Windows 走 winget 或官网安装器。

### VS Code 扩展（15 个）

`ext-claude-code`、`ext-cline`、`ext-kilo-code`、`ext-continue`、`ext-codebuddy`、`ext-comate`（百度文心快码）、
`ext-marscode`（字节）、`ext-lingma`（通义灵码）、`ext-gemini`、`ext-amazon-q`、`ext-cody`、`ext-codegeex`（智谱）、
`ext-tabnine`、`ext-augment`、`ext-iflow`。

```bash
fa install ext          # 一键装全部扩展（需要 code 命令在 PATH）
fa list ext             # 查看已装状态
```

### 两条特殊路线

- **`dsh-free-model`（DeepSeek Harness）**：无需登录，免费额度按出口 IP 计算（约 4k–5.6k token/次，含 harness 注入），
  触及 429 会锁定约 6 小时。`fa run dsh-free-model` 起 Web UI；`fa autostart dsh` 开机自启，见 [专节](#开机自启deepseek-harness-web-ui)。
- **豆包两条路线**：`doubao` 走火山方舟 API（OpenCode + Ark 包装脚本，在 `~/.config/free_agent/ark.env` 填 `ARK_API_KEY`，
  模型默认 `doubao-seed-2-1-pro-260915`）；`doubao-cli` 是官方 CLI，**需要豆包企业账号**，个人账号扫码会报 `login_required`。

## OpenCode 使用指南

[OpenCode](https://opencode.ai/docs) 是开源终端 AI 编码 Agent，支持 BYOK（自带 Key / 任意 OpenAI 兼容端点）与多家 OAuth 登录，
也是 `doubao`（火山方舟）路线的底层引擎。

### 安装

官方安装脚本（Linux / WSL / macOS，推荐）：

```bash
curl -fsSL https://opencode.ai/install | bash
```

或交给 `fa` 按平台自动选路（执行的就是上面这条命令）：

```bash
fa install opencode
fa install opencode --dry-run    # 先预演，只看命令不执行
```

Windows 走 npm 包（版本可能落后于官方脚本，遇旧版请改用官网安装方式）：

```powershell
npm install -g opencode-ai
```

二进制落在 `~/.opencode/bin/opencode`，装完重开终端验证：

```bash
opencode --version
fa list opencode
```

### 启动与基本用法

```bash
cd 你的项目
fa run opencode                  # 等价于 opencode，参数原样透传
opencode                         # 启动 TUI
opencode run "解释这个仓库的结构"  # 非交互模式，跑完即退出
```

TUI 常用命令：

| 命令 | 作用 |
|---|---|
| `/auth` | 添加 / 登录 provider（OAuth 或 API Key） |
| `/models` | 切换模型 |
| `/init` | 生成项目 `AGENTS.md`（给 agent 的项目说明） |
| `/undo` / `/redo` | 撤销 / 重做上一次改动 |
| `/compact` | 压缩上下文 |
| `/help` | 全部命令 |

### 接入模型

两条路线：

1. **OAuth / 免费档**：`/auth` 里选 provider，按提示登录；
2. **BYOK**：设环境变量（如 `OPENAI_API_KEY`、`ANTHROPIC_API_KEY`），或写配置文件接任意 OpenAI 兼容端点
   （智谱 GLM、月之暗面 Kimi、火山方舟 Ark、本地 llama-server 等）。

配置文件：项目级 `opencode.json`，全局 `~/.config/opencode/opencode.json`，也可用 `OPENCODE_CONFIG` 环境变量指定。
自定义端点示例（Key 走环境变量，**不要硬编码进仓库**）：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "myprovider": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "My Provider",
      "options": {
        "baseURL": "https://api.example.com/v1",
        "apiKey": "{env:MY_API_KEY}"
      },
      "models": {
        "some-model": { "name": "Some Model" }
      }
    }
  }
}
```

`doubao` 路线就是这个模式：OpenCode + 火山方舟 Ark 端点，见 [两条特殊路线](#两条特殊路线)。

### 升级

```bash
opencode upgrade                 # 自带 updater
fa update opencode               # 等价写法（清单 update_cmd）
```

### 注意事项

- **两个版本别混用**：npm 的 `opencode-ai` 与官方脚本版同时存在时，会报
  `Database is not empty and has no session table`。用 `which -a opencode` 检查，
  只保留官方脚本那份（`~/.opencode/bin/opencode`），删掉旧 npm 包，升级统一走 `opencode upgrade`。
- 凭据存在 opencode 自己的配置目录，不要写进本仓库。

## 典型工作流

### 新机器全流程

```bash
./install.sh --doctor           # 装 fa 并体检
fa install cli -y               # 全部终端 Agent
fa install ext -y               # 全部 VS Code 扩展（可选）
fa login                        # 看各家登录方式，逐个登录
fa list --installed             # 确认战果
```

### 只用国内直连（无代理环境）

```bash
fa install qwen iflow codebuddy qoder kimi crush
fa run qwen                     # /auth 选 Qwen OAuth，免费额度国内直连
fa run iflow
```

### 海外工具（有本地代理，如 clash）

```bash
fa proxy --port 7890            # 看写法
export https_proxy=http://127.0.0.1:7890 http_proxy=http://127.0.0.1:7890
fa install gemini copilot codex
fa run gemini                   # 首次选 Google 登录
```

或只给单条命令加代理，不污染整个会话：

```bash
https_proxy=http://127.0.0.1:7890 fa run gemini
```

### BYOK：一个 Key 接多家

Aider / Continue / Cline / Crush / OpenCode 不绑定厂商，任意 OpenAI 兼容端点即可
（智谱 GLM、月之暗面 Kimi、火山方舟 Ark、本地 llama-server 等）：

```bash
fa install aider opencode
export OPENAI_API_KEY=sk-...    # 或 ANTHROPIC_API_KEY 等，按工具文档
fa run aider
```

### DeepSeek Harness 常驻 Web UI

```bash
fa install dsh-free-model
fa autostart dsh                # 开机自启 http://127.0.0.1:3080/
fa autostart dsh --status
journalctl --user -u dsh-web.service -f   # 日志里有带 ?token= 的首访问链接
```

### GUI 免 root 安装（Linux）

`fa install gui` 中 manual 项会打印官网地址；下载后解包到 `~/.local/opt/<App>`，
包装脚本放 `~/.local/bin/`（Electron 应用加 `--no-sandbox`），菜单项放 `~/.local/share/applications/`。
细节与各家注意事项见 [docs/platforms.md](docs/platforms.md)。

## 登录指南

| 方式 | 工具 | 操作 |
|---|---|---|
| 一条命令 | copilot / codex / amp / cursor-agent / kiro / qoder / doubao-cli | `fa login <id>` 直接执行 |
| 首次运行内 OAuth | gemini（Google）、qwen（`/auth`）、claude（`/login`）、opencode（`/auth`） | `fa run <id>` 后按提示 |
| 手机号 / 扫码 | trae、qoder-ide、workbuddy、codebuddy、iflow、doubao-cli（企业） | 应用内操作，CLI 无法代劳 |
| API Key | vibe（`MISTRAL_API_KEY`）、kimi、aider、doubao（`ARK_API_KEY`） | 写环境变量或配置文件 |
| 无需登录 | dsh-free-model、vscode（扩展内各自登录） | 直接用 |

凭据都由各家 CLI 存在自己的配置目录（`~/.codex`、`~/.claude` 等），**不要写进本仓库**。

## 网络与代理

- `fa doctor --net` 并发探测 19 个关键域名：`OK` 可直连，`--` 需要代理；
- 直连阵营：qwen / iflow / kimi / codebuddy / qoder / droid / amp / TRAE CN / Qoder CN / WorkBuddy / 豆包 / 火山方舟；
- 需代理阵营：gemini / agy / copilot（登录页）/ codex / claude / kiro / cursor / vibe / dsh；
- 完整域名表、注册优先级建议见 [docs/network.md](docs/network.md)。

```bash
# bash（Linux / WSL / macOS）
export http_proxy=http://127.0.0.1:7890
export https_proxy=http://127.0.0.1:7890

# PowerShell（Windows）
$env:HTTP_PROXY  = "http://127.0.0.1:7890"
$env:HTTPS_PROXY = "http://127.0.0.1:7890"
```

注意：

- 优先用 **http://** 形式的代理变量；部分工具不认 `ALL_PROXY=socks5://`，会导致请求库报错，必要时 `unset ALL_PROXY`；
- 本地回环地址应绕过代理：`export no_proxy=localhost,127.0.0.1,::1`（自启单元已自动设置）；
- GUI 应用一般读系统代理或应用内配置，环境变量不一定生效。

## 开机自启（DeepSeek Harness Web UI）

把 dsh 的 Web UI（默认 `http://127.0.0.1:3080/`）注册成 **systemd 用户服务**，开机自动拉起（仅 Linux / WSL）：

```bash
fa autostart dsh                # 写入 ~/.config/systemd/user/dsh-web.service 并 enable --now
fa autostart dsh --status       # 已启用 / 运行中 / 端口监听 / linger 一目了然
fa autostart dsh --disable      # 停用并停止
journalctl --user -u dsh-web.service -f   # 跟日志
```

设计要点：

- 单元写在**用户级** `~/.config/systemd/user/`，不需要 sudo，不污染系统目录；
- 自动 `loginctl enable-linger`，**不登录桌面也会开机自启**；
- 自动探测本机 HTTP 代理端口（环境变量 → clash 常见端口 7897/7890/7891/10809/1080），写进单元 `Environment=`；
  需要直连时加 `--no-proxy`，显式指定用 `--proxy-port`；
- 端口由 `--port` 指定（默认 3080），只监听回环地址；`--status` / `fa doctor` / `fa run` 会读取单元里的实际端口；
- `Restart=always`（5 秒重试），依赖 `network-online.target`，日志进 journal；
- 浏览器首访问用日志里打印的 `?token=` 链接换 30 天 Cookie，之后直接开 `http://127.0.0.1:3080/`；
- 服务在跑时 `fa run dsh-free-model` 不会重复起进程，直接告诉你地址；
- `fa doctor` 有「开机自启」一栏，随时看服务是否启用 / 运行 / 端口监听。

排查：

| 症状 | 处理 |
|---|---|
| 端口被占（EADDRINUSE） | 停掉手动跑的 `dsh web`，再 `systemctl --user restart dsh-web.service` |
| 开机时代理还没起 | 模型请求会失败，等 clash 起来即可，无需重启服务 |
| 浏览器提示未授权 | 用 journal 里的 `?token=` 链接打开一次（Cookie 30 天） |
| 改了端口想换回 | `fa autostart dsh --port 3080` 重新写入单元 |

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

字段说明：

| 字段 | 必填 | 说明 |
|---|---|---|
| `id` / `name` / `vendor` / `kind` | ✅ | kind ∈ `cli` / `gui` / `ext`；id 全局唯一 |
| `bins` | ✅ | 可执行文件名；可按平台写对象，显式 `null` 表示该平台无命令（状态 MANUAL） |
| `free` / `login` | ✅ | 免费额度与登录方式文案（维护时快照） |
| `install` | ✅ | 各平台安装方式，见下 |
| `proxy` | ✗ | 是否需要代理（默认 false） |
| `login_cmd` | ✗ | `fa login <id>` 直接执行的命令 |
| `run_args` | ✗ | `fa run` 自动附加的默认参数（字符串或数组，可按平台） |
| `update_cmd` | ✗ | 自带升级命令，`fa update` 优先使用 |
| `docs` | ✗ | 文档 / 官网链接 |

支持的安装类型：

| type | 必填键 | 执行命令 |
|---|---|---|
| `npm` | `pkg` | `npm install -g --no-audit --no-fund <pkg>` |
| `uv` | `pkg` | `uv tool install <pkg>` |
| `pipx` | `pkg` | `pipx install <pkg>` |
| `script` | `cmd` | `bash -lc "<cmd>"`（官方安装脚本） |
| `pwsh` | `cmd` | `powershell -NoProfile -ExecutionPolicy Bypass -Command "<cmd>"` |
| `winget` | `id` | `winget install --id <id> -e --accept-…` |
| `vscode-ext` | `id` | `code --install-extension <id> --force` |
| `manual` | `url` / `note` 可选 | 打印下载地址与说明 |

平台键：`default` / `linux` / `wsl` / `windows` / `macos`；回退顺序见 [平台支持](#平台支持)。

改完跑一遍校验与文档同步：

```bash
make test               # 清单结构校验 + 全部单元测试
make docs               # 重新生成 docs/catalog.md（CI 会检查两者同步）
```

## 项目结构

```
Free_Agent/
├── catalog/tools.json     # 唯一事实来源：工具、免费额度、各平台安装方式、网络端点
├── fa/                    # 跨平台 CLI（纯标准库）
│   ├── cli.py             #   命令解析与各子命令
│   ├── catalog.py         #   清单加载 / 校验 / 平台回退
│   ├── installer.py       #   命令拼装与执行、升级
│   ├── doctor.py          #   体检
│   ├── autostart.py       #   systemd --user 开机自启（dsh web）
│   ├── platforms.py       #   平台探测、命令执行、网络探测
│   └── ui.py              #   颜色与中日韩宽字符对齐表格
├── fa.sh                  # POSIX 启动器（被 install.sh 链接为 fa）
├── install.sh             # Linux / WSL / macOS 安装器
├── install.ps1            # Windows PowerShell 安装器
├── tests/                 # 30 个单元测试（不联网、不写系统目录）
├── docs/                  # 平台说明、网络、排错、清单（自动生成）、进度日志
├── .github/workflows/     # CI：Ubuntu + Windows × Python 3.9/3.12
├── Makefile               # make 便捷入口（fa 的封装）
└── pyproject.toml         # 可 pipx / uv 安装
```

## 开发指南

```bash
python3 -m unittest discover -s tests -v   # 全部测试（离线）
./fa.sh list --fast                        # 冒烟
./fa.sh install cli --dry-run              # 预演安装
make help                                  # 全部 make 目标
```

- **代码约定**：纯标准库、Python 3.9+ 兼容（`from __future__ import annotations`）；
  测试不联网、不写系统目录；清单改动必须过 `validate()` 并同步 `docs/catalog.md`。
- **加一个工具**：编辑 `catalog/tools.json` → `make test` → `make docs` → 提交。
- **CI**（`.github/workflows/ci.yml`）：Ubuntu + Windows × Python 3.9/3.12 跑同一套测试与冒烟，
  Ubuntu 上额外 diff `fa catalog --markdown` 与 `docs/catalog.md`，防止文档漂移。
- **make 目标**：`install` / `install-cli` / `install-ext` / `list` / `doctor` / `login` / `proxy` / `update` /
  `test` / `docs` / `clean` / `dsh-autostart[-status|-off]`，以及每个工具同名目标（`ARGS=` 透传参数）。

## 常见问题 FAQ

**`fa: command not found`** —— `~/.local/bin` 不在 PATH：`export PATH="$HOME/.local/bin:$PATH"` 或重开终端；
Windows 新开一个 PowerShell。临时绕过：`./fa.sh list` / `python -m fa list`。

**Windows 上 python 打开 Microsoft Store** —— 装官方 Python（`winget install Python.Python.3.12`），
关闭「应用执行别名」里的 python.exe，或直接用 `py -3`。

**npm 全局安装报 EACCES** —— 不要 `sudo npm -g`；用 nvm，或 `npm config set prefix ~/.local`。

**`uv: command not found`** —— `curl -LsSf https://astral.sh/uv/install.sh | sh`，装完重开终端。

**Electron 应用启动即退出 / sandbox 报错** —— 无 root 环境统一 `--no-sandbox` 启动；
看日志 `~/.cache/free_agent/<app>.log`；彻底解决需系统级安装 deb。

**登录 / OAuth 卡住超时** —— 先 `fa doctor --net` 确认域名可达性，再按 `fa proxy` 设代理重试。

**`fa install all` 有「需手动」条目** —— GUI 与部分国内 CLI 只提供官网安装包，属预期；`fa info <id>` 看地址。

**opencode 报 `Database is not empty…`** —— 新旧版本混用；`which -a opencode` 只保留官方脚本那份，升级用 `opencode upgrade`。

更多见 [排错手册](docs/troubleshooting.md)。

## 文档

- [平台部署说明](docs/platforms.md) —— 各平台差异、安装器行为、GUI 免 root 安装、Electron 沙箱、自启细节
- [工具清单](docs/catalog.md) —— 全部 45 个工具的免费额度 / 登录 / 安装方式（自动生成）
- [网络与账号](docs/network.md) —— 直连 / 代理域名表、代理用法、注册优先级
- [排错手册](docs/troubleshooting.md) —— 常见报错与处理
- [进度日志](docs/journal.md) —— 每轮改动记录与本机安装快照

## 说明与免责

- 本项目只负责安装与启动编排；账号、订阅、额度以各家官方为准，请遵守各自服务条款。
- 免费额度文案是维护时的快照，随时可能调整，欢迎更新 `catalog/tools.json`。
- 部分国内工具需要手机号 / 扫码登录，CLI 无法代劳，`fa login` 会提示。
- 无 root 环境下的 Electron 应用统一以 `--no-sandbox` 启动，详见 [平台说明](docs/platforms.md)。
- 不要把账号凭据、API Key 写进仓库。

## License

[MIT](LICENSE)