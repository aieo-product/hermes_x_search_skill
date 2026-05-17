# hermes_x_search_skill

> Claude Code / Codex CLI から **Hermes Agent** 経由で **X (Twitter) リアルタイム検索** を行うためのスキル。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## これは何？

[Hermes Agent](https://github.com/NousResearch/hermes-agent) には、xAI Grok の OAuth ログイン（X Premium / SuperGrok 加入者向け）でアクセス可能な **X Search ツール** が組み込まれています。本リポジトリは、その X Search を **Claude Code** や **Codex CLI** の中から自然言語 / スラッシュコマンドで呼び出せるようにする薄いブリッジを提供します。

```
Claude/Codex の会話
   │
   │ 「@example_user の最新ポスト10件を取得して」
   ▼
hermes_x_search.py (本リポジトリ)
   │
   ▼
hermes -z "..."   (oneshot)
   │
   ▼
Grok (xAI OAuth) → X Search ツール → 結果
```

## 前提条件

- **X Premium** または **SuperGrok** サブスクリプション
- Python 3.9+
- [Hermes Agent](https://github.com/NousResearch/hermes-agent) インストール済み + `hermes model` で xAI Grok OAuth 認証済み + `hermes tools` で X Search 有効化
- Claude Code または Codex CLI

## クイックスタート

> 詳細なセットアップ手順・トラブルシュートは [Issue #7](https://github.com/aieo-product/hermes_x_search_skill/issues/7) 完了後に本セクションへ追記予定。

```bash
# 1. clone
git clone https://github.com/aieo-product/hermes_x_search_skill.git
cd hermes_x_search_skill

# 2. Claude Code skill としてインストール（手順は後続 issue で確定）

# 3. 試す
echo '@example_user の最新ポストを取得して' | claude
```

## ドキュメント

- [SKILL.md](./SKILL.md) — Claude Code スキル定義（Issue #3 で作成）
- [CLAUDE.md](./CLAUDE.md) — 本リポジトリでの Claude Code 作業ルール

## ライセンス

[MIT License](./LICENSE)

## 関連プロジェクト

- [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)
- [Anthropic Claude Code](https://docs.claude.com/claude-code)
- [OpenAI Codex CLI](https://github.com/openai/codex)
