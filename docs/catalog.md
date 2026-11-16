# 工具清单

> 由 `fa catalog --markdown` 从 `catalog/tools.json` 生成（2026-11-14）。
> 修改清单请编辑 JSON，再重新生成本文件。

## 终端 Agent

| ID | 工具 | 厂商 | 免费额度 | 登录方式 | 代理 | Linux / WSL | Windows |
|---|---|---|---|---|---|---|---|
| `gemini` | [Gemini CLI](https://github.com/google-gemini/gemini-cli) | Google | 个人 Google 账号免费档（约 60 次/分、1000 次/天） | gemini → 选 Google 登录 | 需要 | npm -g @google/gemini-cli | npm -g @google/gemini-cli |
| `qwen` | [Qwen Code](https://github.com/QwenLM/qwen-code) | 阿里 | Qwen OAuth 免费（约 1000–2000 次/天） | qwen → /auth 选 Qwen OAuth | - | npm -g @qwen-code/qwen-code | npm -g @qwen-code/qwen-code |
| `copilot` | [GitHub Copilot CLI](https://docs.github.com/copilot) | GitHub | Copilot Free：2000 补全 + 50 chat/月 | copilot login | 需要 | npm -g @github/copilot | npm -g @github/copilot |
| `codex` | [OpenAI Codex CLI](https://github.com/openai/codex) | OpenAI | ChatGPT 账号内置额度（免费档少量） | codex login | 需要 | npm -g @openai/codex | npm -g @openai/codex |
| `claude` | [Claude Code](https://docs.anthropic.com/en/docs/claude-code) | Anthropic | 无免费档：需 Pro/Max 订阅或 API Key | claude → /login | 需要 | npm -g @anthropic-ai/claude-code | npm -g @anthropic-ai/claude-code |
| `amp` | [Sourcegraph Amp](https://ampcode.com) | Sourcegraph | 免费档（有限流） | amp login | - | npm -g @sourcegraph/amp | npm -g @sourcegraph/amp |
| `cursor-agent` | [Cursor Agent CLI](https://cursor.com/cli) | Cursor | Cursor 免费档 + Agent CLI 额度，新用户有试用 | agent login | 需要 | curl https://cursor.com/install -fsS \| bash | 手动安装 |
| `kiro` | [Kiro CLI](https://kiro.dev/docs/cli/) | AWS | Builder ID 免费档（每月少量 credits） | kiro-cli login | 需要 | curl -fsSL https://cli.kiro.dev/install \| bash | 手动安装 |
| `droid` | [Factory Droid](https://app.factory.ai) | Factory | 注册送免费 token 额度 | droid → 按提示登录 | - | curl -fsSL https://app.factory.ai/cli \| sh | 手动安装 |
| `codebuddy` | [腾讯 CodeBuddy](https://copilot.tencent.com) | 腾讯 | 个人免费额度 | codebuddy → 按提示登录 | - | npm -g @tencent-ai/codebuddy-code | npm -g @tencent-ai/codebuddy-code |
| `qoder` | [Qoder CLI](https://qoder.com) | 阿里 | 注册送 credits | qodercli login | - | npm -g @qoder-ai/qodercli | npm -g @qoder-ai/qodercli |
| `iflow` | [心流 iFlow](https://iflow.cn) | iFlow | 免费（含国内模型） | iflow → 按提示登录 | - | npm -g @iflow-ai/iflow-cli | npm -g @iflow-ai/iflow-cli |
| `agy` | [Antigravity CLI](https://antigravity.google/docs) | Google | Google 账号免费档（Gemini 3 Pro 等） | agy → 按提示登录 | 需要 | 手动安装 | 手动安装 |
| `vibe` | [Mistral Vibe](https://docs.mistral.ai) | Mistral | Le Chat / Mistral API 免费额度 | 配置 MISTRAL_API_KEY | 需要 | uv tool mistral-vibe | uv tool mistral-vibe |
| `kimi` | [Kimi CLI](https://platform.moonshot.cn) | 月之暗面 | 需 Kimi API / 编程套餐 | kimi → 配置 API Key | - | uv tool kimi-cli | uv tool kimi-cli |
| `aider` | [Aider](https://aider.chat) | Aider | BYOK：可接各家免费/低价端点 | 设 ANTHROPIC_API_KEY / OPENAI_API_KEY 等 | - | uv tool aider-chat | uv tool aider-chat |
| `crush` | [Charm Crush](https://github.com/charmbracelet/crush) | Charm | 自带若干免费/试用 provider | crush → /models 选 provider | - | npm -g @charmland/crush | npm -g @charmland/crush |
| `cline` | [Cline CLI](https://cline.bot) | Cline | 可选免费 provider / BYOK | cline → 配置 provider | - | npm -g cline | npm -g cline |
| `continue` | [Continue CLI](https://continue.dev) | Continue | BYOK（可接免费端点） | cn → 配置 provider | - | npm -g @continuedev/cli | npm -g @continuedev/cli |
| `codebuff` | [CodeBuff](https://codebuff.com) | CodeBuff | 新用户试用额度 | codebuff → 首次运行自举后登录 | - | npm -g codebuff | npm -g codebuff |
| `opencode` | [OpenCode](https://opencode.ai/docs) | SST | BYOK / 各家免费 OAuth | opencode → /auth | - | curl -fsSL https://opencode.ai/install \| bash | npm -g opencode-ai |
| `doubao` | [豆包 Seed（火山方舟 + OpenCode）](https://www.volcengine.com/docs/ark) | 字节跳动 / 火山引擎 | 火山方舟新用户免费额度（按模型） | 在 ~/.config/free_agent/ark.env 填 ARK_API_KEY | - | 手动安装 | 手动安装 |
| `doubao-cli` | [豆包 CLI（官方）](https://www.doubao.com/work/docs/zh-cn/articles/218099810377-cli-quick-start) | 字节跳动 | 需豆包企业账号（个人账号扫码会报 login_required） | doubao-cli login（企业账号扫码） | - | npm -g @bytedance/doubao-cli | npm -g @bytedance/doubao-cli |

## 桌面 IDE / GUI

| ID | 工具 | 厂商 | 免费额度 | 登录方式 | 代理 | Linux / WSL | Windows |
|---|---|---|---|---|---|---|---|
| `cursor` | [Cursor IDE](https://www.cursor.com/downloads) | Cursor | 免费档 + 新用户试用 | 应用内登录 | 需要 | 手动安装 | winget Anysphere.Cursor |
| `trae` | [TRAE CN](https://www.trae.com.cn/download) | 字节跳动 | 注册送 credits | 手机号 / 微信扫码 | - | 手动安装 | 手动安装 |
| `qoder-ide` | [Qoder CN IDE](https://qoder.com/download) | 阿里 | 注册送 credits | 手机号 / 扫码 | - | 手动安装 | 手动安装 |
| `workbuddy` | [腾讯 WorkBuddy](https://www.workbuddy.cn) | 腾讯 | 个人免费额度 | 手机号 / 扫码 | - | 手动安装 | 手动安装 |
| `antigravity` | [Antigravity IDE](https://antigravity.google) | Google | Google 账号免费档 | Google 账号 | 需要 | 手动安装 | 手动安装 |
| `vscode` | [VS Code](https://code.visualstudio.com/download) | Microsoft | 免费 | 无需登录（扩展内登录） | - | 手动安装 | winget Microsoft.VisualStudioCode |

## 编辑器扩展

| ID | 工具 | 厂商 | 免费额度 | 登录方式 | 代理 | Linux / WSL | Windows |
|---|---|---|---|---|---|---|---|
| `ext-claude-code` | [Claude Code 扩展](https://marketplace.visualstudio.com/items?itemName=anthropic.claude-code) | Anthropic | 需订阅或 API Key | VS Code 内登录 | 需要 | code --install-extension anthropic.claude-code | code --install-extension anthropic.claude-code |
| `ext-cline` | [Cline 扩展](https://marketplace.visualstudio.com/items?itemName=saoudrizwan.claude-dev) | Cline | 可选免费 provider / BYOK | VS Code 内配置 provider | - | code --install-extension saoudrizwan.claude-dev | code --install-extension saoudrizwan.claude-dev |
| `ext-kilo-code` | [Kilo Code 扩展](https://marketplace.visualstudio.com/items?itemName=kilocode.kilo-code) | Kilo | 可选免费 provider / BYOK | VS Code 内配置 provider | - | code --install-extension kilocode.kilo-code | code --install-extension kilocode.kilo-code |
| `ext-continue` | [Continue 扩展](https://marketplace.visualstudio.com/items?itemName=continue.continue) | Continue | BYOK | VS Code 内配置 provider | - | code --install-extension continue.continue | code --install-extension continue.continue |
| `ext-codebuddy` | [CodeBuddy 扩展](https://marketplace.visualstudio.com/items?itemName=tencent-cloud.coding-copilot) | 腾讯 | 个人免费额度 | VS Code 内登录 | - | code --install-extension tencent-cloud.coding-copilot | code --install-extension tencent-cloud.coding-copilot |
| `ext-comate` | [Comate 文心快码](https://marketplace.visualstudio.com/items?itemName=baiducomate.comate) | 百度 | 个人免费额度 | VS Code 内登录 | - | code --install-extension baiducomate.comate | code --install-extension baiducomate.comate |
| `ext-marscode` | [MarsCode / TRAE 助手](https://marketplace.visualstudio.com/items?itemName=marscode.marscode-extension) | 字节跳动 | 个人免费额度 | VS Code 内登录 | - | code --install-extension marscode.marscode-extension | code --install-extension marscode.marscode-extension |
| `ext-lingma` | [通义灵码 / Qoder](https://marketplace.visualstudio.com/items?itemName=alibaba-cloud.tongyi-lingma) | 阿里 | 个人免费额度 | VS Code 内登录 | - | code --install-extension alibaba-cloud.tongyi-lingma | code --install-extension alibaba-cloud.tongyi-lingma |
| `ext-gemini` | [Gemini Code Assist](https://marketplace.visualstudio.com/items?itemName=google.geminicodeassist) | Google | Google 账号免费档 | VS Code 内登录 Google | 需要 | code --install-extension google.geminicodeassist | code --install-extension google.geminicodeassist |
| `ext-amazon-q` | [Amazon Q Developer](https://marketplace.visualstudio.com/items?itemName=amazonwebservices.amazon-q-vscode) | AWS | Builder ID 免费档 | VS Code 内登录 AWS | 需要 | code --install-extension amazonwebservices.amazon-q-vscode | code --install-extension amazonwebservices.amazon-q-vscode |
| `ext-cody` | [Sourcegraph Cody](https://marketplace.visualstudio.com/items?itemName=sourcegraph.cody-ai) | Sourcegraph | 免费档 | VS Code 内登录 | - | code --install-extension sourcegraph.cody-ai | code --install-extension sourcegraph.cody-ai |
| `ext-codegeex` | [CodeGeeX](https://marketplace.visualstudio.com/items?itemName=aminer.codegeex) | 智谱 | 免费 | VS Code 内登录 | - | code --install-extension aminer.codegeex | code --install-extension aminer.codegeex |
| `ext-tabnine` | [Tabnine](https://marketplace.visualstudio.com/items?itemName=tabnine.tabnine-vscode) | Tabnine | 免费档 | VS Code 内登录 | - | code --install-extension tabnine.tabnine-vscode | code --install-extension tabnine.tabnine-vscode |
| `ext-augment` | [Augment Code](https://marketplace.visualstudio.com/items?itemName=augment.vscode-augment) | Augment | 试用额度 | VS Code 内登录 | 需要 | code --install-extension augment.vscode-augment | code --install-extension augment.vscode-augment |
| `ext-iflow` | [iFlow 扩展](https://marketplace.visualstudio.com/items?itemName=iflow-cli.iflow-cli-vscode-ide-companion) | iFlow | 免费 | VS Code 内登录 | - | code --install-extension iflow-cli.iflow-cli-vscode-ide-companion | code --install-extension iflow-cli.iflow-cli-vscode-ide-companion |

