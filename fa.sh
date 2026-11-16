#!/usr/bin/env bash
# Free_Agent 启动器（Linux / WSL / macOS）
# 安装方式：./install.sh，之后任意目录可用 fa
set -euo pipefail

src="${BASH_SOURCE[0]}"
while [ -L "$src" ]; do
  dir="$(cd -P -- "$(dirname -- "$src")" && pwd)"
  src="$(readlink -- "$src")"
  case "$src" in
    /*) ;;
    *) src="$dir/$src" ;;
  esac
done
here="$(cd -P -- "$(dirname -- "$src")" && pwd)"
export PYTHONPATH="$here${PYTHONPATH:+:$PYTHONPATH}"

if command -v python3 >/dev/null 2>&1; then
  py=python3
elif command -v python >/dev/null 2>&1; then
  py=python
else
  echo "Free_Agent 需要 Python 3.9+，请先安装 python3" >&2
  exit 127
fi

exec "$py" -m fa "$@"
