# hermes_x_search_skill

> Claude Code / Codex CLI から **Hermes Agent** 経由で **X (Twitter) リアルタイム検索** を行うためのスキル。
>
> X Premium / SuperGrok 加入者であれば追加の API キーなしで、Claude / Codex の会話の中から X のリアルタイム情報にアクセスできます。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![tests](https://img.shields.io/badge/tests-27%20passing-brightgreen)](./tests/)

## 目次

- [これは何？](#これは何)
- [前提条件](#前提条件)
- [セットアップ](#セットアップ)
- [使い方](#使い方)
- [既知の制約](#既知の制約)
- [トラブルシュート](#トラブルシュート)
- [貢献](#貢献)
- [ライセンス](#ライセンス)

## これは何？

[Hermes Agent](https://github.com/NousResearch/hermes-agent) は xAI Grok の OAuth ログインで X Search ツールが使えるエージェントです。本リポジトリは、その X Search を **Claude Code** や **Codex CLI** の中から自然言語 / スラッシュコマンドで呼び出せる薄いブリッジを提供します。

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
   │
   ▼
Markdown / JSON に整形して返却
```

### できること

- 特定ユーザーの最新ポスト取得（`@xxx の最新N件`）
- キーワード検索（`"foo" を含むポスト`）
- 期間指定検索（`since: / until:`）
- Markdown 表 / JSON 構造化出力の切り替え
- Claude Code / Codex 両対応（同一ラッパー共有）

### できないこと

- X の API キー（v2 API）は使わない → ポストの likes / reposts / views は取得できない場合あり
- 投稿・DM 送信などの書き込み系操作（read-only）

## 前提条件

| 項目 | 要件 |
|------|------|
| サブスクリプション | **X Premium** または **SuperGrok**（Grok OAuth ログインで X Search が有効化される） |
| Python | 3.9+ |
| OS | macOS / Linux / Termux（Hermes Agent の対応範囲に準拠） |
| クライアント | [Claude Code](https://docs.claude.com/claude-code) または [Codex CLI](https://github.com/openai/codex)（両方でも可） |

## セットアップ

### Step 1: Hermes Agent をインストール

```bash
# 公式 install.sh をダウンロードして中身を確認してから実行することを推奨
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh -o /tmp/hermes-install.sh
less /tmp/hermes-install.sh      # 中身を確認
bash /tmp/hermes-install.sh --skip-browser
```

### Step 2: PATH を通す

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc   # bash の場合は ~/.bashrc
source ~/.zshrc
hermes --version
```

### Step 3: xAI Grok OAuth で認証

```bash
hermes model
```

→ 「**xAI Grok OAuth (SuperGrok Subscription)**」を選択 → ブラウザが開く → X アカウント（Premium / SuperGrok 加入済み）でログイン → Allow → ターミナルに戻る。

確認:
```bash
hermes status | grep -i xai
# → "xAI / Grok" 行が認証済みになっていること
```

### Step 4: X (Twitter) Search ツールを有効化

```bash
hermes tools
```

対話 TUI で「**X (Twitter) Search**」をスペースキーで ON にして Enter。

> ⚠️ `hermes tools` はインタラクティブターミナルでのみ動作します（パイプ・サブシェル不可）。

### Step 5: 本スキルをインストール

```bash
git clone https://github.com/aieo-product/hermes_x_search_skill.git
cd hermes_x_search_skill
./scripts/install.sh
```

`install.sh` は `~/.claude/` / `~/.codex/` のどちらか／両方に **symlink** でスキルを設置します（idempotent、`--uninstall` で完全戻り道）。

| オプション | 動作 |
|-----------|------|
| `./scripts/install.sh` | Claude Code / Codex の存在を auto-detect して両方に設置 |
| `./scripts/install.sh --claude` | Claude Code のみ |
| `./scripts/install.sh --codex` | Codex のみ |
| `./scripts/install.sh --uninstall` | symlink を削除 |

### Step 6: 動作確認

**Claude Code:**
```
@example_user の最新ポスト 3件を取得して
```
→ Claude が `hermes-x-search` スキルを発動し、結果を表示します。

**Codex:**

Codex のデフォルトサンドボックスは Hermes が `~/.hermes/logs/` 等へ書き込むのを拒否します（`workspace-write` は cwd 配下しか書けないため不十分）。`~/.hermes` をホームに持つ Hermes を呼ぶには **`--sandbox danger-full-access`** を指定するか、Codex の writable_roots 設定に `~/.hermes` を追加してください。

```bash
# 最も手早い方法（フルアクセス、サンドボックス無効）
codex exec --sandbox danger-full-access \
  "@example_user の最新ポスト 3件を取得して"

# よりきめ細かい権限制御：~/.hermes を writable_roots に追加
codex exec --sandbox workspace-write \
  -c 'sandbox_workspace_write.writable_roots=["~/.hermes"]' \
  "@example_user の最新ポスト 3件を取得して"
```

**直接コマンド（ラッパー単体）:**
```bash
./skills/hermes-x-search/scripts/hermes_x_search.py --user example_user --count 3
```

## 使い方

### スキル発動トリガー（Claude / Codex 共通）

自然言語の以下のような表現で自動発動：
- 「Xで〜を調べて」「Twitterで〜を検索して」
- 「@xxx のポストを取得して」「@xxx の最新ツイート」
- 「ツイート検索」「X検索」「ポスト検索」
- 「X Search で〜」「X(旧Twitter)で〜」

### CLI 引数

```bash
hermes_x_search.py [OPTIONS]
```

| 引数 | 必須 | 既定値 | 説明 |
|------|:----:|:------:|------|
| `--query`, `-q` | ⭕(※) | — | 検索キーワード。フレーズは `"..."` |
| `--user`, `-u` | △ | — | ユーザー指定（`@` 付き / 無し可）|
| `--count`, `-n` | — | `10` | 取得件数（1–50）|
| `--since` | — | — | この日時以降（YYYY-MM-DD）|
| `--until` | — | — | この日時以前（YYYY-MM-DD）|
| `--output`, `-o` | — | `md` | `md` または `json` |
| `--hermes-bin` | — | `hermes` | hermes バイナリのパス（`$HERMES_BIN` でも可）|
| `--debug` | — | — | プロンプト + 生応答を stderr へ |

※ `--query` と `--user` の少なくとも一方が必要。

### 出力例（Markdown）

```markdown
> Recent posts from user @example_user limited to 3 results

| # | 日時 | 投稿者 | 本文 | リンク |
|---|------|--------|------|--------|
| 1 | Just now | @example_user | ついに導入する理由が出来ました | [link](https://x.com/.../status/...) |
| 2 | 13:38 | @example_user | Xポスト検索が無料なのはデカすぎる | [link](https://x.com/.../status/...) |
```

### 出力例（JSON）

```json
{
  "results": [
    {
      "url": "https://x.com/example_user/status/0000000000000000000",
      "author": "@example_user",
      "posted_at": "2026-05-18T01:00:00Z",
      "text": "...",
      "likes": null,
      "reposts": null,
      "views": null
    }
  ],
  "query_summary": "Recent posts by @example_user"
}
```

## 既知の制約

- **キーワード検索の精度は Grok 任せ**: 一般的な単語（例: "Claude Code"）の場合、Grok が X Search ツールを呼ばずに空配列を返すことがあります。`--user` 指定との併用、より具体的なフレーズ、短期間指定で安定する傾向。
- **`since` / `until` は Grok が X 検索クエリ言語に翻訳**: 期間が狭すぎる・古すぎると 0 件になります。
- **起動時間**: 1 リクエストあたり 30〜120 秒（Hermes 起動 + LLM 推論 + ツール実行）。将来的な常駐デーモン化は ToDo。
- **Codex のサンドボックス**: デフォルトの `read-only` サンドボックスでは Hermes が `~/.hermes/logs/agent.log` への書き込みを拒否されます。`workspace-write` も cwd 外を書けないため、`--sandbox danger-full-access` を指定するか、`-c 'sandbox_workspace_write.writable_roots=["~/.hermes"]'` で `~/.hermes` を明示許可してください。
- **likes / reposts / views**: X Search ツールが返さない場合があり、その時は `null` になります。

## トラブルシュート

| 症状 | 対処 |
|------|------|
| `error: hermes binary not found` | Step 1 / Step 2 を再確認。`hermes` が PATH に無い場合は `--hermes-bin /full/path/to/hermes` で明示 |
| `exit 10` / `OAuth login required` | `hermes model` で xAI Grok OAuth を再ログイン |
| `exit 11` / `x_search_unavailable` | `hermes tools` で「X (Twitter) Search」を ON |
| `exit 12` / `rate limit` | しばらく待って再試行 |
| `exit 13` / `could not parse JSON` | `--debug` で生応答を確認。Grok の出力が壊れている可能性 |
| Claude Code が skill を発動しない | `~/.claude/skills/hermes-x-search/` が存在するか確認。無ければ `./scripts/install.sh` を再実行 |
| Codex が hermes を呼べない | サンドボックス問題: `--sandbox danger-full-access` か `-c 'sandbox_workspace_write.writable_roots=["~/.hermes"]'`。PATH 問題: `HERMES_BIN=/path/to/hermes` を設定 |
| 「No matching posts found.」が返るが結果があるはず | 既知制約セクション参照。`--user` 併用や具体的キーワードを試す |

### 詳細デバッグ

```bash
./skills/hermes-x-search/scripts/hermes_x_search.py \
  --user example_user --count 3 --debug 2>&1 | tee /tmp/hxs.log
```

stderr に「=== PROMPT TO HERMES ===」「=== HERMES STDOUT ===」が出力されます。

## 貢献

Issue / PR 歓迎。本リポジトリは [](https://github.com/) 準拠の開発フローを採用しています：

1. issue を立てる
2. `/issue-investigate <URL>` で調査・対応方針コメント
3. `/issue-implement <URL>` で実装 + PR
4. `/pr-review <URL>` で Codex + Claude セルフレビュー
5. 人間レビュー → マージ

開発時のルールは [CLAUDE.md](./CLAUDE.md) を参照。詳細は [CONTRIBUTING.md](./CONTRIBUTING.md)。

### テスト

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install pytest
pytest tests/
```

## ライセンス

[MIT License](./LICENSE)

## 関連プロジェクト

- [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) — 本スキルが内部で利用する基盤エージェント
- [Anthropic Claude Code](https://docs.claude.com/claude-code)
- [OpenAI Codex CLI](https://github.com/openai/codex)
