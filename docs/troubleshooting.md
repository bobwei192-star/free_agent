# 排错手册

## `fa: command not found`

- Linux / WSL：确认 `~/.local/bin` 在 PATH 中，或执行 `export PATH="$HOME/.local/bin:$PATH"`，再重开终端。
- Windows：`%USERPROFILE%\.local\bin` 已写入用户 PATH，但**已打开的终端不会自动刷新**，需要新开一个 PowerShell。
- 临时绕过启动器：仓库根目录执行 `./fa.sh list`（Windows：`py -3 -m fa list`）。

## 提示找不到 Python / Python 版本过低

需要 3.9+。Windows 上如果 `python` 打开的是 Microsoft Store，请安装官方 Python 并关闭「应用执行别名」里的
`python.exe` / `python3.exe`，或者直接使用 `py -3`。

```powershell
winget install Python.Python.3.12
```

## npm 全局安装报 EACCES / 权限错误

不要用 `sudo npm -g`。改用 nvm 管理 Node，或把 npm 前缀指到用户目录：

```bash
npm config set prefix ~/.local
```

## `uv: command not found`

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

装完在 `~/.local/bin`，需要重开终端。Windows 使用：

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## `winget` 不存在

Microsoft Store 更新「应用安装程序（App Installer）」，或改用官网安装器（`fa info <id>` 里有地址）。

## Electron 应用启动即退出 / 报 sandbox 错误

无 root 环境下没有 setuid 的 `chrome-sandbox`，启动脚本已加 `--no-sandbox`。如果仍然失败：

```bash
tail -n 50 ~/.cache/free_agent/<app>.log
```

彻底解决需要系统级安装对应 deb（`sudo apt install ...`），让沙箱恢复。

## opencode 版本混乱（`Database is not empty and has no session table`）

同时存在 npm 旧版和官方安装脚本的新版时会出现。检查：

```bash
which -a opencode
opencode --version
```

只保留 `~/.opencode/bin/opencode`（或官方脚本安装的那份），删掉旧的 npm 包：

```bash
rm -rf ~/.local/lib/node_modules/opencode-ai
```

升级统一用 `opencode upgrade`，不要再用 npm 装 `opencode-ai`。

## TRAE CN 的 deb 装不上

`TRAE_CN-linux-arm64.deb` 是 arm64 包，x86_64 机器要用官方 x64 tar.gz。`uname -m` 确认架构后再下载。

## WorkBuddy 更新后本地文件消失

官方更新会清空并重写安装目录，不要把个人文件放在 `~/.local/opt/WorkBuddy` 下。

## Qoder CN 在 Wayland 下白屏

启动脚本会自动回退 Ozone/X11 平台；如果仍异常，手动指定：

```bash
qoder-cn --ozone-platform=x11
```

## 登录 / OAuth 卡住或超时

先跑 `fa doctor --net`，确认对应域名是否需要代理；再按 `fa proxy` 设置环境变量后重试：

```bash
https_proxy=http://127.0.0.1:7890 fa run gemini
```

## `fa install all` 有些条目显示「需手动」

GUI 应用和部分国内 CLI 只提供官网安装包，清单里标记为 `manual`，会打印下载地址。这是预期行为：

```bash
fa info trae
fa info workbuddy
```

## `fa list` 的版本列不是数字

个别工具 `--version` 输出的是横幅而不是版本号，`fa` 会退化为显示第一行文本，不影响使用。

## 清单改坏了 / JSON 解析失败

```bash
python3 -m json.tool catalog/tools.json > /dev/null   # 先确认 JSON 合法
python3 -m unittest discover -s tests -v              # 再跑结构校验
```
