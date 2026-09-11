#!/usr/bin/env bash
# このリポジトリの設定を ~/.claude と ~/.codex にシンボリックリンクで配置する。
# 実体をリポジトリ側に置くことで、設定を編集するとそのまま git 差分になる。
set -euo pipefail

repo="$(cd "$(dirname "$0")" && pwd)"
claude_home="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
codex_home="${CODEX_HOME:-$HOME/.codex}"
backup="$HOME/.agent-settings-backup/$(date +%Y%m%d%H%M%S)"

# link <リポジトリ相対パス> <リンクを張る絶対パス>
link() {
  local src="$repo/$1" dst="$2"
  mkdir -p "$(dirname "$dst")"
  # 既存の実体は退避してから張り替える(symlink なら上書きでよい)
  if [ -e "$dst" ] && [ ! -L "$dst" ]; then
    # ~/.claude/skills と ~/.codex/skills で名前が衝突するので親ディレクトリ名を付ける
    local saved="$backup/$(basename "$(dirname "$dst")")-$(basename "$dst")"
    mkdir -p "$backup"
    mv "$dst" "$saved"
    echo "backup: $dst -> $saved"
  fi
  ln -sfn "$src" "$dst"
  echo "link:   $dst"
}

link CLAUDE.md                     "$claude_home/CLAUDE.md"
link .claude/settings.json         "$claude_home/settings.json"
link .claude/statusline-command.sh "$claude_home/statusline-command.sh"
link .claude/statusline-parse.py   "$claude_home/statusline-parse.py"
link .claude/skills                "$claude_home/skills"

link AGENTS.md                     "$codex_home/AGENTS.md"
link .codex/skills                 "$codex_home/skills"
