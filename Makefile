# Free_Agent —— make 只是 fa CLI 的便捷封装
# 用法：make help
SHELL := /bin/bash
.DEFAULT_GOAL := help

FA := ./fa.sh
ARGS ?=

CLI_TARGETS := gemini qwen copilot codex claude amp cursor-agent kiro droid \
               codebuddy qoder iflow agy vibe kimi aider crush cline \
               continue codebuff opencode doubao doubao-cli dsh-free-model
GUI_TARGETS := cursor trae qoder-ide workbuddy antigravity vscode

.PHONY: help install install-cli install-ext list status doctor login proxy update test docs clean \
        $(CLI_TARGETS) $(GUI_TARGETS)

help:
	@printf '\033[1mFree_Agent\033[0m — 跨平台 AI Agent 部署器（Linux / WSL / Windows）\n\n'
	@printf '\033[36m安装与体检\033[0m\n'
	@printf '  \033[32mmake %-14s\033[0m%s\n' \
		install '安装 fa 启动器（Linux/WSL/macOS）' \
		install-cli '安装全部终端 Agent' \
		install-ext '安装全部 VS Code 扩展' \
		list '列出工具与安装状态' \
		doctor '体检命令、依赖与网络' \
		login '查看各家的登录方式' \
		proxy '代理环境变量用法' \
		update '升级已安装的终端 Agent'
	@printf '\n\033[36m终端 Agent\033[0m\n'
	@printf '  \033[32mmake %-14s\033[0m%s\n' \
		gemini 'Google Gemini CLI' \
		qwen '阿里 Qwen Code' \
		copilot 'GitHub Copilot CLI' \
		codex 'OpenAI Codex CLI' \
		claude 'Anthropic Claude Code' \
		amp 'Sourcegraph Amp' \
		cursor-agent 'Cursor Agent CLI' \
		kiro 'AWS Kiro CLI' \
		droid 'Factory Droid' \
		codebuddy '腾讯 CodeBuddy' \
		qoder '阿里 Qoder CLI' \
		iflow '心流 iFlow' \
		agy 'Google Antigravity CLI' \
		vibe 'Mistral Vibe' \
		kimi '月之暗面 Kimi' \
		aider 'Aider' \
		crush 'Charm Crush' \
		cline 'Cline CLI' \
		continue 'Continue CLI' \
		codebuff 'CodeBuff' \
		opencode 'OpenCode' \
		doubao '豆包 Seed（火山方舟 + OpenCode）' \
		doubao-cli '豆包 CLI（官方，需企业账号）' \
		dsh-free-model 'dsh Free Model（DeepSeek Harness 免费 token）'
	@printf '\n\033[36m桌面 / GUI\033[0m\n'
	@printf '  \033[32mmake %-14s\033[0m%s\n' \
		cursor 'Cursor IDE' \
		trae 'TRAE CN' \
		qoder-ide 'Qoder CN IDE' \
		workbuddy '腾讯 WorkBuddy' \
		antigravity 'Google Antigravity IDE' \
		vscode 'VS Code'
	@printf '\n\033[36m开发\033[0m\n'
	@printf '  \033[32mmake %-14s\033[0m%s\n' \
		test '运行单元测试' \
		docs '重新生成 docs/catalog.md'
	@printf '\n\033[2m提示：make gemini ARGS="--help" 透传参数；跨平台请直接用 fa <命令>\033[0m\n'

install:
	@./install.sh

install-cli:
	@$(FA) install cli -y

install-ext:
	@$(FA) install ext -y

list status:
	@$(FA) list

doctor:
	@$(FA) doctor --net

login:
	@$(FA) login

proxy:
	@$(FA) proxy

update:
	@$(FA) update

test:
	@python3 -m unittest discover -s tests -v

docs:
	@$(FA) catalog --markdown > docs/catalog.md
	@echo "已生成 docs/catalog.md"

clean:
	@find . -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true
	@rm -rf build dist *.egg-info

$(CLI_TARGETS) $(GUI_TARGETS):
	@exec $(FA) run $@ $(ARGS)
