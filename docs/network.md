# 网络与账号

## 直连可用（国内网络）

| 工具 | 关键域名 |
|---|---|
| Qwen Code / Qoder | `qwen.ai`、`qoder.com` |
| 心流 iFlow | `iflow.cn` |
| Kimi | `api.moonshot.cn` |
| CodeBuddy | 腾讯 |
| Droid | `app.factory.ai` |
| Amp | `ampcode.com` |
| 豆包 | `www.doubao.com` |
| 豆包 Seed（火山方舟 Ark） | `ark.cn-beijing.volces.com` |
| TRAE CN | `www.trae.com.cn` |
| WorkBuddy | `www.workbuddy.cn` |
| VS Code 扩展市场 | `marketplace.visualstudio.com` |
| 智谱 GLM（可作 OpenAI 兼容 provider） | `open.bigmodel.cn` |

## 需要代理

| 工具 | 关键域名 |
|---|---|
| Gemini CLI / Antigravity | `accounts.google.com`、`generativelanguage.googleapis.com` |
| GitHub Copilot | `github.com/login/device`（`api.github.com` 本身可通） |
| Codex | `api.openai.com`、`chatgpt.com` |
| Claude Code | `api.anthropic.com`（部分地区 403） |
| Kiro | `console.kiro.dev` |
| Cursor / Cursor Agent | `auth.cursor.com` |
| Mistral Vibe | `api.mistral.ai` |

`fa doctor --net` 会并发探测上表域名（3 秒超时），`--` 表示需要代理。

## 代理用法

```bash
fa proxy                          # 打印当前平台的写法
https_proxy=http://127.0.0.1:7890 fa run gemini
```

只给单条命令加代理，不影响其它进程。GUI 应用一般读取系统代理设置，或者在应用内单独配置。

## 建议注册顺序（按白嫖性价比）

1. Google 账号 —— Gemini CLI + Antigravity，免费档最厚
2. 阿里 Qwen —— Qwen Code OAuth 免费额度，国内直连
3. 心流 iFlow —— 国内直连，免费
4. Cursor —— Agent CLI + IDE 试用额度
5. AWS Builder ID —— Kiro CLI 每月免费 credits
6. GitHub —— Copilot Free（2000 补全 + 50 chat/月）
7. 字节 TRAE CN / 阿里 Qoder —— 注册送 credits
8. 腾讯 CodeBuddy / 百度 Comate —— 国内免费档
9. Factory（Droid）/ Sourcegraph（Amp）—— 注册送试用额度
10. 月之暗面 Kimi、智谱 GLM、MiniMax —— 国内 API 便宜/有免费额度，可接 BYOK 类工具

## 说明

- 额度和模型可用性随时调整，以官网为准；`fa info <id>` 里的文案是维护时的快照，欢迎更新 `catalog/tools.json`。
- BYOK 类工具（Aider、Continue、Cline、Crush、OpenCode）不绑定厂商，接任意 OpenAI 兼容端点即可。
- 不要把账号凭据写进仓库；各家 CLI 默认把凭据存在自己的配置目录（如 `~/.codex`、`~/.claude`）。
