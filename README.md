# agent-settings

Claude Code と Codex の個人設定。実体をこのリポジトリに置き、`~/.claude` と `~/.codex` からシンボリックリンクで参照。

## 想定環境

- macOS
- Windows は WSL2 上（リポジトリは `/mnt/c` ではなく WSL 側のファイルシステムに clone）

## 構成

```
.
├── AGENTS.md                  # エージェント共通のルール(実体)
├── CLAUDE.md -> AGENTS.md     # 中身が分岐したら実ファイル化
├── .agents/
│   └── skills/                # エージェント共通のスキル(実体)
│       └── pr-review/SKILL.md
├── .claude/
│   ├── settings.json          # モデル / effortLevel / テーマ・TUI / ステータスライン / プラグイン
│   ├── statusline-command.sh  # ステータスラインのエントリポイント
│   ├── statusline-parse.py    # 画面下部の表示を組み立てる本体
│   └── skills -> ../.agents/skills
└── .codex/
    └── skills -> ../.agents/skills
```

スキルは `.agents/skills/` にだけ配置。`.claude/` と `.codex/` にはそのエージェント固有の設定のみ。

## セットアップ

設定を持ち込みたい別の PC で実行。設定の出どころの PC では実行不要（既存の `~/.claude` をそのまま使用）。

```sh
./install.sh
```

- 何度実行しても安全。すでにリンクなら張り直しのみ
- リンクでない実ファイルは `~/.agent-settings-backup/<日時>/` に退避してから張り替え
- 置き場所は `CLAUDE_CONFIG_DIR` / `CODEX_HOME` で変更可（既定 `~/.claude`、`~/.codex`）

## 更新

- ルールは `AGENTS.md`、スキルは `.agents/skills/<名前>/SKILL.md` を編集・追加して commit
- `install.sh` 済みの PC は保存時点で反映。他の PC は `git pull` のみ
- リンクしていない PC（設定の出どころ）は `~/.claude` 側の変更を手でコピー

## ref
1. [Claude Code と Codex でスキルと設定を共有する](https://zenn.dev/optimisuke/articles/7c68a24a032b4d#%E3%81%AF%E3%81%98%E3%82%81%E3%81%AB)
