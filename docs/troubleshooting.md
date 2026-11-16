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

## 免费车道报 `Free usage limit reached`（HTTP 429）

`*-free` 不等于无限用量：车道按天配额，用满后上游直接 429，并给出
`providerRetryAfterMs`（实测 `deepseek-v4.1-flash-free` 为 38 334 000 ms，即次日 08:00 CST / 00:00 UTC 重置）。
特征：会话 `turn/end` 的 `reason.kind = error`，插件 `stats.json` 里对应样本
`ok:false / noUsage:true / input:0`，`failed` 计数增加，模型本身没跑。

换一条车道即可继续：`fa list` 里 `our-free-model` 的 Kilo 组（如
`nvidia/nemotron-3.5-lightning:free`）与 OpenCode 组配额独立；EAC 车道需先 `fa eac --login`。

## 想看 harness 一轮真实用了多少 token

`~/.dsh/our-free-model/stats.json` 是插件侧的逐次账本，`samples[]` 每条带
`origin`（`harness` / `title` 等）、`input` / `output` / `ttftMs` / `elapsedMs`；`models[<id>]`
是累计值，`logical.turns` 是总轮数。Web 端另有一份会话侧账本，在设置外的会话面板里读
`tokenUsage` 与 `contextBreakdown`（system / tools / message 三段），实测一轮空转：
输入 9 916 = system 1 402 + 工具 schema 7 395 + 消息 463，输出 119 —— 免费车道真正吃量的是
system + 工具清单，不是用户那句话，所以短问题也别频繁开新会话。

## EAC 模型报 `AUTHORIZATION_REQUIRED`，且找不到「EAC 渠道授权」入口

dsh 某些 Web 版本（实测 `0.2.2-rc.1`）只挂载 `dsh-our-free-model` 的服务端半区，插件十一页面板所在的
`settings.section` 客户端半区没被加载，所以设置里没有「Our Free Model」，README 指的授权区块无处可点。
授权流程本身可用，直接走插件自己的同源接口：

```bash
fa eac                 # 看状态：车道可用 / 需要授权 / 已授权 / 已 star
fa eac --login         # 发起 GitHub 登录并等待自动确认
fa eac --collect LINK  # 上一轮 15 分钟内没领到，凭 link 补领
```

浏览器里用 GitHub 登录并 star `Ebony-Vinyl/dsh-our-free-model` 即完成授权；`*-free` 免费模型不受此问题影响。
根因与手工兜底见 [EAC 授权](eac-auth.md)。

**`fa eac --login` 显示完成、状态却还是未授权**：登录+star 成功不等于授权落地。令牌是
`GET /eac/login/poll?link=…` 领回来后由插件服务端写 `~/.dsh/our-free-model/eac-user.json` 才算数；
等待窗口先到期、或页面没回到网关，都会留下「GitHub 已登录但本机没凭据」。
判据只看两条：`fa eac` 的 `本机凭据` 是否 `已保存`、`~/.dsh/our-free-model/eac-user.json` 是否存在。
补救用**同一轮**打印的 link：`fa eac --collect <link>`（link 15 分钟内有效，过期才需要重新 `--login`）。
`--timeout` 默认已提到 900 秒。

## EAC 车道已授权但请求超时

实测授权通过后 `z-ai/glm-5.3-flash` 能跑通，但首 token 延迟极高：成功的一次
`ttftMs 287 986`（4.8 分钟）、43 tok/s；后续几次在 300 秒整被切断
（`ok:false / noUsage:true / elapsedMs ≈ 300 005`），`deepseek-ai/deepseek-v4.1-flash` 三次尝试
（132 s / 30 s / 240 s）全部无响应。这是车道侧拥塞，不是授权问题。

单模型直测走 `/api/our-free-model/bench`（POST `{"model":"…","effort":"…"}`），它和别的
同源接口一样要先换 Cookie，最省事的是在浏览器 DevTools 控制台里发：

```js
await fetch('/api/our-free-model/bench', {method: 'POST',
  headers: {'content-type': 'application/json'},
  body: JSON.stringify({model: 'z-ai/glm-5.3-flash'})}).then(r => r.json())
```

拥堵时段优先退回 Kilo 组免费车道（`nvidia/nemotron-3.5-lightning:free` 实测一轮
9 916 输入 / 119 输出、TTFT 1.9 秒），EAC 留给确实需要的项目。

## 清单改坏了 / JSON 解析失败

```bash
python3 -m json.tool catalog/tools.json > /dev/null   # 先确认 JSON 合法
python3 -m unittest discover -s tests -v              # 再跑结构校验
```
