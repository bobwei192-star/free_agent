"""终端输出：颜色、对齐（含中日韩宽字符）、表格。"""

from __future__ import annotations

import os
import re
import sys
import unicodedata

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
_ENABLED = True


def _enable_windows_ansi() -> None:
    if os.name != "nt":
        return
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)
        mode = ctypes.c_uint32()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            kernel32.SetConsoleMode(handle, mode.value | 0x0004)
    except Exception:
        pass


def configure(color: bool | None = None) -> None:
    """color=None 时自动判断；True/False 强制开/关。"""
    global _ENABLED
    if color is None:
        _enable_windows_ansi()
        color = (
            sys.stdout.isatty()
            and not os.environ.get("NO_COLOR")
            and os.environ.get("TERM") != "dumb"
        )
    _ENABLED = bool(color)


def style(text: str, *codes: str) -> str:
    if not _ENABLED or not codes:
        return text
    return "".join(f"\x1b[{c}m" for c in codes) + text + "\x1b[0m"


def bold(text: str) -> str:
    return style(text, "1")


def dim(text: str) -> str:
    return style(text, "2")


def green(text: str) -> str:
    return style(text, "32")


def red(text: str) -> str:
    return style(text, "31")


def yellow(text: str) -> str:
    return style(text, "33")


def cyan(text: str) -> str:
    return style(text, "36")


def visible_width(text: str) -> int:
    text = _ANSI_RE.sub("", text)
    width = 0
    for ch in text:
        if unicodedata.combining(ch):
            continue
        width += 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
    return width


def pad(text: str, width: int, align: str = "left") -> str:
    gap = max(0, width - visible_width(text))
    if align == "right":
        return " " * gap + text
    if align == "center":
        left = gap // 2
        return " " * left + text + " " * (gap - left)
    return text + " " * gap


def truncate(text: str, width: int) -> str:
    if visible_width(text) <= width:
        return text
    out = ""
    used = 0
    for ch in text:
        w = 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
        if used + w > width - 1:
            break
        out += ch
        used += w
    return out + "…"


def table(headers: list[str], rows: list[list[str]], aligns: list[str] | None = None) -> str:
    aligns = aligns or ["left"] * len(headers)
    widths = [visible_width(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], visible_width(str(cell)))
    lines = [
        "  ".join(pad(style(h, "1"), widths[i]) for i, h in enumerate(headers)),
        "  ".join("─" * widths[i] for i in range(len(headers))),
    ]
    for row in rows:
        lines.append(
            "  ".join(
                pad(str(cell), widths[i], aligns[i] if i < len(aligns) else "left")
                for i, cell in enumerate(row)
            )
        )
    return "\n".join(line.rstrip() for line in lines)


def say(message: str = "") -> None:
    print(message)


def ok(message: str) -> None:
    print(f"{green('✓')} {message}")


def warn(message: str) -> None:
    print(f"{yellow('!')} {message}")


def error(message: str) -> None:
    print(f"{red('✗')} {message}", file=sys.stderr)


def confirm(question: str) -> bool:
    if not sys.stdin.isatty():
        return True
    answer = input(f"{question} [y/N] ").strip().lower()
    return answer in ("y", "yes")
