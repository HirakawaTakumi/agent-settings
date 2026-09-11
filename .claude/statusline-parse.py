import json
import os
import subprocess
import sys
import time

# ステータスライン 1 行を組み立てて標準出力に出す。
# 入力は Claude Code が渡す JSON。欠けている項目は表示しない。

RESET = "\033[0m"
DIM = "\033[2m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
CYAN = "\033[36m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
BOLD = "\033[1m"


def colored_pct(pct: float) -> str:
    """使用率を閾値で色分けする(70% 未満 緑 / 90% 未満 黄 / 以上 赤)。"""
    color = GREEN if pct < 70 else YELLOW if pct < 90 else RED
    return f"{color}{round(pct)}%{RESET}"


def fmt_tokens(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:g}M"
    return f"{n / 1000:.1f}K" if n >= 1000 else str(n)


def shorten(text: str, max_len: int) -> str:
    return text if len(text) <= max_len else text[: max_len - 1] + "…"


def fmt_left(reset_at: float) -> str:
    sec = max(0, int(reset_at - time.time()))
    h, m = divmod(sec // 60, 60)
    d, h = divmod(h, 24)
    return f"{d}d{h}h" if d else f"{h}h{m:02d}m"


def git_branch() -> str:
    try:
        return subprocess.run(
            ["git", "--no-optional-locks", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, timeout=1,
        ).stdout.strip()
    except Exception:
        return ""


data = json.loads(sys.stdin.read())
# 行を分けて埋もれないようにする: 1 行目 場所 / 2 行目 セッション名 / 3 行目 使用量
parts: list[str] = []
usage: list[str] = []

model = (data.get("model") or {}).get("display_name", "unknown")
parts.append(f"{CYAN}{model}{RESET}")

cwd = data.get("cwd", "")
loc = f"{BLUE}{os.path.basename(cwd) or cwd}{RESET}"
branch = git_branch()
if branch:
    # 長いブランチ名は末尾を省略して他項目の表示領域を確保する
    loc += f" {DIM}on{RESET} {MAGENTA}{shorten(branch, 24)}{RESET}"
parts.append(loc)

cw = data.get("context_window") or {}
cu = cw.get("current_usage") or {}
total = sum(
    cu.get(k, 0) or 0
    for k in (
        "input_tokens",
        "output_tokens",
        "cache_creation_input_tokens",
        "cache_read_input_tokens",
    )
)
size = cw.get("context_window_size")
pct = cw.get("used_percentage")
# used_percentage が来ていない間は使用量と上限から自前で割合を出す
if pct is None and size and total:
    pct = total * 100 / size
if pct is not None or total:
    tok = f"{BOLD}{fmt_tokens(total) if total else '-'}{RESET}"
    if size:
        tok += f"{DIM}/{fmt_tokens(size).replace('.0K', 'K')}{RESET}"
    pct_s = colored_pct(pct) if pct is not None else "--%"
    usage.append(f"{tok} ({pct_s})")

rl = data.get("rate_limits") or {}
for key, label, color in (
    ("five_hour", "5h", CYAN),
    ("seven_day", "1w", MAGENTA),
):
    w = rl.get(key) or {}
    if w.get("used_percentage") is None:
        continue
    s = f"{color}{label}{RESET} {colored_pct(w['used_percentage'])}"
    if w.get("resets_at"):
        s += f" {DIM}↻{fmt_left(w['resets_at'])}{RESET}"
    usage.append(s)

# 3 行構成: 場所 / セッション名 / 使用量。セッション名は長くても省略しない
sep = f" {DIM}│{RESET} "
print(sep.join(parts))
if data.get("session_name"):
    print(f"{BOLD}{data['session_name']}{RESET}")
if usage:
    print(sep.join(usage))
