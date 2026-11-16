# Free_Agent 进度记录

最后更新：2026-11-14
状态：可用（23 个终端 Agent + 6 个 GUI 全部 OK）

## 一、本轮完成（2026-11-14）

| 事项 | 结果 | 说明 |
|---|---|---|
| 新增 WorkBuddy（腾讯）GUI | ✅ | Linux deb 5.6.2.40046327，sha256 `12149ad8…97523` 校验通过 |
| WorkBuddy 安装方式 | ✅ | 免 root 解包到 `~/.local/opt/WorkBuddy`（1.7G），包装脚本 `~/.local/bin/workbuddy` 带 `--no-sandbox` |
| WorkBuddy 菜单项 | ✅ | `~/.local/share/applications/workbuddy.desktop` + hicolor 全尺寸图标，GNOME 搜索 "WorkBuddy" 可开 |
| WorkBuddy 启动验证 | ✅ | `make workbuddy` 拉起主进程 + zygote，日志 `~/.cache/free_agent/workbuddy.log`，workbuddy.cn 直连 200 |
| 阿里 Qoder CN | ✅ 已有 | 之前已装在 `~/.local/opt/Qoder-CN`，本轮复验 `make qoder-ide` 正常（Linux Wayland 会话自动回退 x11 ozone） |
| Makefile 同步 | ✅ | `GUI_TARGETS` / help / list / doctor / login 都加入 workbuddy |
| 全局入口 `free` | ✅ | `free workbuddy` 已可用 |
| README 同步 | ✅ | GUI 表格、Downloads 清单、快速验证、网络说明均已更新 |
| 豆包官方 CLI（`doubao-cli`） | ✅ 已装 | npm 包 `@bytedance/doubao-cli` 2.36.2，`~/.local/bin/doubao-cli`；仅支持企业账号，个人扫码会报 `login_required` |
| 豆包 Seed（`doubao`） | ✅ 可用（待填 Key） | 包装脚本 `~/.local/bin/doubao` = OpenCode + 火山方舟 Ark，配置 `~/.config/free_agent/ark.env` 与 `opencode-doubao.json` |
| 豆包接入清单 | ✅ | `catalog/tools.json` 新增 `doubao` / `doubao-cli`，网络端点加入 `ark.cn-beijing.volces.com` |

### 本轮改动的文件

- `~/Free_Agent/catalog/tools.json`：新增 `doubao`（Ark + OpenCode）与 `doubao-cli`（官方），网络端点加入火山方舟
- `~/Free_Agent/Makefile` / `README.md` / `docs/catalog.md`：同步豆包两条路线
- `~/.local/bin/doubao`：包装脚本（读 `ark.env`，`OPENCODE_CONFIG` 指向 Ark 配置，`opencode --standalone`）
- `~/.config/free_agent/ark.env`、`~/.config/free_agent/opencode-doubao.json`：Ark Key 与模型配置
- `~/Free_Agent/README.md`：GUI 表格新增 WorkBuddy 行、终端表格新增豆包行
- `~/.local/bin/free`：TARGETS 加入 `workbuddy`、`doubao`

### 关键命令

```bash
make workbuddy        # 启动腾讯 WorkBuddy
make qoder-ide        # 启动阿里 Qoder CN
free workbuddy        # 全局入口，等价写法
make list             # 看全部版本 / 是否已装
```

## 二、当前安装清单

### 终端 Agent（22 个，全部 OK）

```
gemini 0.68.0        qwen 0.27.3          copilot 1.0.111.
codex 0.169.0        claude 2.1.323       amp 0.0.1794571247-g07b20f
cursor-agent 2026.11.11-b912975         kiro 3.3.0
droid 1.10.0         codebuddy 2.184.0    qoder 1.1.89
iflow 0.5.19         agy 1.5.8            vibe 3.1.2
kimi 1.52.0          aider 0.86.2         crush 0.101.0
cline 3.0.74         continue 1.5.47      codebuff 1.0.688
opencode 2.3.0       doubao（Ark）       doubao-cli 2.36.2
```

### 桌面 / GUI（6 个，全部 OK）

| 目标 | 命令 | 状态 |
|---|---|---|
| `make cursor` | `cursor` | OK |
| `make trae` | `trae-cn` | OK |
| `make qoder-ide` | `qoder-cn` | OK |
| `make workbuddy` | `workbuddy` | OK（本轮新增） |
| `make antigravity` | `antigravity-ide` | OK |
| `make vscode` | `code` | OK |

### 安装位置约定（全部 rootless，不需要 sudo）

- 程序本体：`~/.local/opt/`（WorkBuddy / Qoder-CN / trae-cn / antigravity / vscode）、`~/.local/share/cursor`
- 命令行包装：`~/.local/bin/`
- 菜单项：`~/.local/share/applications/*.desktop`
- GUI 运行日志：`~/.cache/free_agent/<app>.log`

## 三、已知问题 / 注意事项

1. **Electron 一律 `--no-sandbox`**：本机没有 root 拥有的 setuid `chrome-sandbox`，所有 GUI 都靠包装脚本加 `--no-sandbox`。想正规化需 `sudo apt install` 对应 deb。
2. **WorkBuddy 官方站点只给 UOS / 麒麟商店入口**，没有公开 Linux 下载按钮；包地址从 `https://www.workbuddy.cn/v2/update?platform=workbuddy-linux-x64-deb` 的 JSON 里取 `url`。升级同理，换 `platform=workbuddy-linux-arm64-deb` 等。
3. **WorkBuddy 更新会清空安装目录重新写入**（官方 FAQ），本地文件别放 `~/.local/opt/WorkBuddy` 下。
4. **opencode 两个版本别混用**：现用 `~/.opencode/bin/opencode` v2.3.0，旧 v1.19.5 已改名 `opencode-v1.19.5`，升级用 `opencode upgrade`。
5. **TRAE CN**：`~/Downloads` 里的 `TRAE_CN-linux-arm64.deb` 架构不对（本机 x86_64），实际用的是官方 x64 tar.gz。
6. **代理**：gemini / agy / copilot / codex / claude / kiro / cursor / vibe 需代理；qwen / iflow / kimi / codebuddy / qoder / droid / amp / TRAE CN / Qoder CN / WorkBuddy 可直连。
7. **豆包官方 CLI 只认企业账号**：个人豆包 App 扫码会返回 `login_required`；个人可用 `doubao`（火山方舟 Ark，需在 `~/.config/free_agent/ark.env` 填 `ARK_API_KEY`，模型默认 `doubao-seed-2-1-pro-260915`）。

## 四、待办 / 可选

- [ ] 按需清理 `~/Downloads` 里的大包：`WorkBuddy-linux-x64-deb.deb`（410M）、`cursor_3.30.8_amd64.deb`、`TRAE_CN-linux-x64.tar.gz`
- [ ] 如想系统级安装（沙箱正常、`/usr/bin` 有命令），执行一次 `sudo apt install` 对应 deb
- [ ] `make update` 里可考虑加 WorkBuddy / Qoder CN 的升级检查（两者自带 updater，暂未纳入批量升级）
- [ ] 豆包：在 `~/.config/free_agent/ark.env` 填入 `ARK_API_KEY` 后，`fa run doubao` 即可使用；如走自定义推理接入点，把 `opencode-doubao.json` 里的模型 ID 换成 `ep-xxxxxxxx`

## 五、工程化改造（2026-11-14）

| 事项 | 结果 |
|---|---|
| 目录重构 | 根目录只留 README / Makefile / LICENSE / 安装器；CLI 进 `fa/`，清单进 `catalog/`，文档进 `docs/`，测试进 `tests/` |
| 统一清单 | 44 个工具（23 CLI + 6 GUI + 15 扩展）收进 `catalog/tools.json`，含免费额度、登录、代理、各平台安装方式 |
| 跨平台 CLI | 纯标准库 `fa`：list / info / install / run / login / update / doctor / proxy / catalog |
| 安装器 | `install.sh`（Linux/WSL/macOS，免 root）+ `install.ps1`（Windows，生成 `fa.cmd` 并写用户 PATH） |
| 体检 | `fa doctor --net` 检查命令、按平台裁剪前置依赖、并发探测 18 个关键域名 |
| 文档 | README + 平台说明、网络账号、排错手册、自动生成的工具清单 |
| 质量 | 19 个单元测试、GitHub Actions（Ubuntu + Windows × Python 3.9/3.12）、pyproject 支持 pipx/uv 安装 |
| 兼容 | 保留旧 `free` 入口与 `make <agent>` 目标；`fa` 通过软链安装到 `~/.local/bin` |

