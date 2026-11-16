# 平台部署说明

`fa` 启动时自动判定平台：

| 判定 | 依据 | 平台值 |
|---|---|---|
| Windows | `sys.platform == "win32"` | `windows` |
| WSL | `/proc/version` 含 `microsoft` 或存在 `WSL_DISTRO_NAME` | `wsl` |
| Linux | 其它 Linux | `linux` |
| macOS | `darwin` | `macos` |

安装方式按平台回退：`windows → default`；`wsl → linux → default`；`macos → linux → default`。

## Linux

```bash
./install.sh
```

安装器只做三件事：

1. 校验 Python 3.9+；
2. 在 `~/.local/bin/fa` 建立指向仓库 `fa.sh` 的符号链接；
3. 如果 `~/.local/bin` 不在 PATH 中，往 `~/.profile` / `~/.bashrc` / `~/.zshrc` 追加一段带标记的 PATH（已在 PATH 时不动）。

程序本体全部用户级，不需要 sudo：

| 内容 | 位置 |
|---|---|
| 启动器 | `~/.local/bin/fa` |
| npm 全局包 | `~/.local/lib/node_modules` 或 nvm prefix |
| uv 工具 | `~/.local/bin`（uv 默认） |
| GUI 应用（免 root 解包） | `~/.local/opt/<App>` |
| 菜单项 | `~/.local/share/applications/*.desktop` |
| GUI 日志 | `~/.cache/free_agent/<app>.log` |

Electron 应用（Cursor / TRAE / Qoder / WorkBuddy / Antigravity / VS Code）在没有 root 所有的 setuid
`chrome-sandbox` 时无法启用沙箱，包装脚本统一加 `--no-sandbox`。想正规化就系统级安装对应 deb：

```bash
sudo apt install ~/Downloads/cursor_*.deb ~/Downloads/Qoder-CN-linux-amd64.deb
```

## 开机自启动（systemd --user）

`fa autostart dsh` 只写用户级单元，不碰 `/etc/systemd/system`：

| 项目 | 值 |
|---|---|
| 单元文件 | `~/.config/systemd/user/dsh-web.service` |
| 启动命令 | `dsh web --no-open --port 3080` |
| 依赖 | `network-online.target` |
| 重启策略 | `Restart=always`（5 秒后重试） |
| linger | 自动 `loginctl enable-linger`（不登录也自启） |
| 代理 | 自动探测本地 HTTP 代理端口写进 `Environment=`；`--no-proxy` 可关闭 |

常用命令：

```bash
systemctl --user status dsh-web.service        # 看状态
systemctl --user restart dsh-web.service       # 重启
journalctl --user -u dsh-web.service -f        # 跟日志（里面有带 token 的访问链接）
systemctl --user disable --now dsh-web.service  # 停用
```

排查：

- 端口被占（`EADDRINUSE`）：先停掉手动跑的 `dsh web`，再 `systemctl --user restart dsh-web.service`；
- 代理没起（开机时 clash 还没运行）：模型请求会失败，等 clash 起来后无需重启服务；
- 浏览器提示未授权：用日志里的 `?token=` 链接打开一次，Cookie 有效期 30 天。

## WSL

- 终端 Agent 直接装在 WSL 里最省事，`fa install cli` 全流程可用。
- GUI 应用需要 WSLg（Windows 11 默认开启，`wsl --version` 可确认）；体验和性能仍不如 Windows 原生，**推荐在 Windows 侧装 IDE**，WSL 只装 CLI。
- WSL 会自动继承 Windows 的 PATH，`fa` 可能同时看到两侧的命令；以 `fa doctor` 打印的路径为准。
- 修改 PATH 后若没生效：`exec $SHELL -l` 或重开终端。

## Windows（PowerShell）

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

安装器行为：

1. 依次尝试 `py -3`、`python`、`python3`（排除 Microsoft Store 的占位别名），要求 3.9+；
2. 生成 `%USERPROFILE%\.local\bin\fa.cmd`，内容为设置 `PYTHONPATH` 后调用 `python -m fa`；
3. 把 `%USERPROFILE%\.local\bin` 追加到**用户级** PATH（不碰系统 PATH），当前会话立即生效。

依赖安装提示：

| 依赖 | 命令 |
|---|---|
| Python | `winget install Python.Python.3.12` |
| Node.js / npm | `winget install OpenJS.NodeJS.LTS` |
| winget 自身 | Microsoft Store 更新「应用安装程序」 |

代理（PowerShell）：

```powershell
$env:HTTP_PROXY  = "http://127.0.0.1:7890"
$env:HTTPS_PROXY = "http://127.0.0.1:7890"
$env:ALL_PROXY   = "http://127.0.0.1:7890"
```

`fa proxy` 会按当前平台打印对应写法。

## GUI 安装对照

| 工具 | Linux | Windows |
|---|---|---|
| Cursor | 官网下载 deb / AppImage，免 root 解包到 `~/.local/opt` | `winget install Anysphere.Cursor` |
| TRAE CN | 官网 x64 tar.gz（arm64 包不能装在 x64 机器） | 官网安装器 |
| Qoder CN | 解包 deb 到 `~/.local/opt/Qoder-CN` | 官网安装器 |
| WorkBuddy | 官方 update 接口返回 JSON，取 `url` 下载 deb；更新会重写安装目录 | 官网安装器 |
| Antigravity | 官网 tar.gz | 官网安装器 |
| VS Code | 官网 tar.gz | `winget install Microsoft.VisualStudioCode` |

CLI 侧对应的命令是 `fa install <id>`：自动可装的会直接执行；`manual` 类型会打印下载地址和注意事项。
