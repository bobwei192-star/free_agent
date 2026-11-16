#!/usr/bin/env bash
# Free_Agent 安装器：Linux / WSL / macOS
# 用法：./install.sh [--doctor]
set -euo pipefail

ROOT="$(cd -P -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="${FREE_AGENT_BIN_DIR:-$HOME/.local/bin}"
DOCTOR=0
for arg in "$@"; do
  case "$arg" in
    --doctor) DOCTOR=1 ;;
    -h|--help)
      echo "用法: ./install.sh [--doctor]"
      echo "  --doctor   安装后执行 fa doctor"
      echo "环境变量: FREE_AGENT_BIN_DIR（默认 ~/.local/bin）、PYTHON"
      exit 0
      ;;
  esac
done

bold() { printf '\033[1m%s\033[0m\n' "$*"; }
info() { printf '  %s\n' "$*"; }
ok()   { printf '  \033[32m✓\033[0m %s\n' "$*"; }
die()  { printf '  \033[31m✗\033[0m %s\n' "$*" >&2; exit 1; }

find_python() {
  local candidate
  for candidate in "${PYTHON:-}" python3 python; do
    [ -n "$candidate" ] || continue
    command -v "$candidate" >/dev/null 2>&1 || continue
    if "$candidate" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 9) else 1)' 2>/dev/null; then
      command -v "$candidate"
      return 0
    fi
  done
  return 1
}

bold "Free_Agent 安装器"
info "目录    $ROOT"
info "平台    $(uname -s) $(uname -m)"
if [[ -n "${WSL_DISTRO_NAME:-}" ]]; then
  info "WSL     $WSL_DISTRO_NAME（GUI 应用建议装在 Windows 原生侧）"
fi

PY="$(find_python || true)"
[[ -n "$PY" ]] || die "未找到 Python 3.9+。Debian/Ubuntu: sudo apt install python3；macOS: brew install python"
ok "Python  $("$PY" --version 2>&1)  ($PY)"

chmod +x "$ROOT/fa.sh" "$ROOT/install.sh"
mkdir -p "$BIN_DIR"
ln -sfn "$ROOT/fa.sh" "$BIN_DIR/fa"
ok "启动器  $BIN_DIR/fa → $ROOT/fa.sh"

PATH_NOTE=0
case ":${PATH}:" in
  *":$BIN_DIR:"*) ;;
  *)
    PATH_NOTE=1
    MARKER="# >>> Free_Agent >>>"
    for rc in "$HOME/.profile" "$HOME/.bashrc" "$HOME/.zshrc"; do
      [ -e "$rc" ] || continue
      if ! grep -qF "$MARKER" "$rc" 2>/dev/null; then
        {
          printf '\n%s\nexport PATH="%s:$PATH"\n# <<< Free_Agent <<<\n' "$MARKER" "$BIN_DIR"
        } >> "$rc"
        info "已写入 PATH 到 $rc"
      fi
    done
    ;;
esac

printf '\n'
"$BIN_DIR/fa" version

printf '\n'
bold "安装完成"
info "fa list                查看工具与安装状态"
info "fa install cli         安装全部终端 Agent"
info "fa doctor --net        体检环境与网络"
if [[ "$PATH_NOTE" == 1 ]]; then
  printf '\n'
  info "当前 shell 需要执行一次：export PATH=\"$BIN_DIR:\$PATH\""
  info "或重开终端让 PATH 生效"
fi

if [[ "$DOCTOR" == 1 ]]; then
  printf '\n'
  "$BIN_DIR/fa" doctor --net || true
fi
