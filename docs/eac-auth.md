# EAC 协付车道授权（dsh + dsh-our-free-model）

适用：在 DeepSeek Harness（dsh）里选了 EAC 分组模型（如 `EAC GLM 5.3 Flash`）后，
会话立刻以 `AUTHORIZATION_REQUIRED` 失败，而插件文档说的「设置 → Our Free Model → EAC 渠道授权」在界面上找不到。

## 一、症状

- 模型选择器里有 EAC 模型，一发就失败，报 `需要 GitHub 授权并 star 仓库后使用 / AUTHORIZATION_REQUIRED`。
- 按插件 README 找「设置 → Our Free Model」：设置对话框左侧只有 `通用设置 / 模型 / 内置插件 / Agent 预设` 四项，没有 `Our Free Model`。
- 「插件」页里能看到 `已安装插件 → Our Free Model`（带启用开关），但点进去只是 README，没有那十一页面板，也没有「EAC 渠道授权」区块。

## 二、根因

`dsh-our-free-model` 分两个半区：

| 半区 | 位置 | 本机实测 |
|---|---|---|
| 服务端（模型清单、`/api/our-free-model/*` 路由、GitHub 授权收发） | `~/.dsh/profiles/web/node_modules/dsh-our-free-model/index.js` | 正常，`/eac/status` 能返回 `available:true / required:true` |
| 客户端（`settings.section` 注入的十一页面板、EAC 授权区块） | 同目录 `client.js`，注入代码见 `client.js` 中 `ctx.slots.inject('settings.section', …)`（`id: 'our-free-model'`，`order: 35`） | **未加载** |

证据（dsh `0.2.2-rc.1`，Web UI `http://127.0.0.1:3080/`）：

1. 页面加载的插件客户端合并请求 `/plugins/??@deepseek-ai/...` 里全是官方 `@deepseek-ai/dsh-client-ui-*` 包，没有第三方 `dsh-our-free-model/client.js`；
2. 直接向页面要这个 bundle：`GET /plugins/dsh-our-free-model/client.js` → `404`；
3. 宿主设置面板的导航项由 `ctx.slots.entries('settings.section')` 按 `order` 排序生成，客户端半区没挂载，列表里自然没有第 35 位的那一项。

结论：不是插件没装好，也不是账号问题——这一版 Web 宿主没把第三方插件的客户端半区挂上来，
授权 UI 因此不可达，而授权动作本身（服务器侧 GitHub 校验 + 令牌落盘）完全可用。

## 三、解决：用命令行走同一条授权流程

```bash
fa eac                    # 看当前授权状态（车道 / 是否要求 / 已授权 / 已 star / 仓库）
fa eac --login            # 发起 GitHub 登录：打印授权链接并打开浏览器，然后自动确认
fa eac --login --no-open  # 同上，但只打印链接，由你自己复制去开
fa eac --collect <link>   # 上一轮没赶上（15 分钟领取窗口）时，凭 link 补领
fa eac --json             # 原始状态 JSON，脚本用
```

`fa eac` 做的事和插件面板逐字一致：借 dsh 首访问令牌换 30 天会话 Cookie，再调用插件自己的同源接口：

1. `POST /api/our-free-model/eac/login/start` → `{url, link, opened}`（插件在这一步会拉起系统浏览器）；
2. 在浏览器里用 GitHub 登录并 star `Ebony-Vinyl/dsh-our-free-model`；
3. `GET /api/our-free-model/eac/login/poll?link=<link>` → `{"status":"ok","login":"你的用户名"}`，
   令牌由插件服务端写入 `~/.dsh/our-free-model/eac-user.json`（0600）；
4. `GET /api/our-free-model/eac/status` 复核 `authorized: true`，重开会话即可使用 EAC 模型。

令牌不经过命令行，也不写进本仓库或任何日志；`fa eac` 只读状态和链接。

### 不装本仓库也能做：浏览器控制台

在已打开的 dsh Web UI 里按 F12，Console 执行：

```js
// 1) 发起登录，拿到 url 与 link（插件会自动打开浏览器）
await fetch('/api/our-free-model/eac/login/start', {method: 'POST'}).then(r => r.json())

// 2) 在 GitHub 页面登录 + Star 仓库后，用上一行的 link 领取
await fetch('/api/our-free-model/eac/login/poll?link=<link>').then(r => r.json())

// 3) 复核
await fetch('/api/our-free-model/eac/status').then(r => r.json())
```

## 四、几个必须知道的边界

- **star 是实时校验的**：取消 star 后 `authorized` 会变回 `false`，重新 star 即可恢复，无需重新登录。
- **link 有 15 分钟领取窗口**：窗口内随时能用 `fa eac --collect <link>` 补领；过期后 `status: expired`，重新 `fa eac --login`。
- **等待超时不等于授权失败**：`--login` 的等待窗口（默认 900 秒）到点只代表「本机没人去 poll」，
  GitHub 那侧的登录与 star 已经生效。此时别重开登录，直接用上一轮打印的 link 补领。
  判定只认两件事：`fa eac` 里 `本机凭据` 是否为 `已保存`，以及 `~/.dsh/our-free-model/eac-user.json` 是否存在。
- **免费车道不受影响**：`glm-5.3-flash-free`、`deepseek-v4.1-flash-free` 这类 `*-free` 模型无需任何授权，急着用可以直接选它们。
- **授权页打不开 GitHub**：是浏览器侧网络问题，不是插件网关问题。`fa proxy` 看写法，给浏览器配好代理再发起登录。
- **换端口 / 换 token**：`fa eac --port 3081 --token <journal 里最新那条>`。令牌默认从
  `journalctl --user -u dsh-web.service` 的启动行里取，取不到再扫 `~/.dsh/logs/startup-*.log`，也认环境变量 `DSH_WEB_TOKEN`。

## 五、状态码对照

| 现象 | 含义 | 处理 |
|---|---|---|
| `车道可用 否` | 当前运行环境没解锁 EAC 协付车道 | 换用 `*-free` 模型；或更新插件后重启 dsh |
| `接口未授权` + 找不到令牌 | dsh 首访问令牌已被新一次启动覆盖 | `journalctl --user -u dsh-web.service -o cat \| grep -o 'token=[^ ']*'` 取最新一条 |
| `status: unstarred` | GitHub 已登录，但还没 star | Star `Ebony-Vinyl/dsh-our-free-model` 后再 `fa eac --collect <link>` |
| `status: pending` 一直不变 | 浏览器里的登录没完成 | 确认该浏览器已登录 GitHub；必要时 `fa eac --login --no-open` 手动复制链接 |
| `策略确认：网关未确认` | 网关 `/auth/status` 没答上 | 状态是本机缓存的判定，稍后 `fa eac` 复查 |
| `no-lane` | 插件拿不到 EAC 凭据 | 重启 dsh（`systemctl --user restart dsh-web.service`）；仍不行就更新插件 |
