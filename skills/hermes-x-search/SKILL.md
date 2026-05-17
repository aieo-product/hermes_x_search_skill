---
name: hermes-x-search
description: Hermes Agent 経由で X (Twitter) リアルタイム検索を行う。ユーザーが「Xで調べて」「ツイート検索して」「@xxx のポストを取得」「X Search で」「X(旧Twitter)で〜」「Twitter検索」等と言ったとき、または X 上のリアルタイム情報（ニュース、トレンド、特定ユーザーの最新ポスト、キーワード検索）が必要になったときに発動する。
---

# hermes-x-search スキル

Hermes Agent（xAI Grok OAuth）経由で X (Twitter) のリアルタイム検索を行うスキル。

## 発動条件

以下のいずれかに該当する場合に自動的に発動する：

- ユーザーが以下のような表現でリクエストした場合：
  - 「Xで〜を調べて」「Twitterで〜を検索して」「X Search で〜」
  - 「@xxx のポストを取得して」「@xxx の最新ツイート」
  - 「ツイート検索」「X検索」「ポスト検索」
- `/x-search` スラッシュコマンドが入力された場合
- X 上のリアルタイム情報（ニュース、トレンド、ユーザー動向）の取得が必要な場合

## 前提条件

実行前に以下が満たされていることを確認する。未充足ならスキル本体に進む前にユーザーに案内する：

| 項目 | 確認コマンド | エラー時の案内 |
|---|---|---|
| `hermes` コマンドが PATH にある | `command -v hermes` | "Hermes Agent をインストールしてください: https://github.com/NousResearch/hermes-agent" |
| xAI Grok OAuth 認証済み | `hermes status \| grep "xAI"` | "`hermes model` を実行し xAI Grok OAuth を選択してログインしてください" |
| X (Twitter) Search ツールが有効 | （実行時に発火しなかったらエラー検出） | "`hermes tools` で X (Twitter) Search を有効化してください" |

## 引数仕様

`/x-search` の引数（自然言語呼び出し時はモデルが文脈から抽出する）：

| 引数 | 必須 | 既定値 | 説明 |
|------|:----:|:------:|------|
| `query` | ⭕ (※) | — | 検索キーワード。スペース区切りで複数。フレーズ検索は `"..."` で囲む |
| `user` | △ | — | 特定ユーザー指定。`@` 付き / 無しどちらも可。指定時 `query` は省略可 |
| `count` | — | 10 | 取得件数。1–50 |
| `since` | — | — | この日時以降（ISO 8601 / `YYYY-MM-DD`） |
| `until` | — | — | この日時以前（同上） |
| `output` | — | `md` | `md`（Markdown 表）/ `json`（構造化） |

※ `query` と `user` のいずれかは必須。両方指定で「指定ユーザーの投稿のうちキーワードを含むもの」を意味する。

## 実行内容

1. **前提条件チェック**: 上表のコマンドで `hermes` の利用可否を確認
2. **ラッパースクリプト呼び出し**:
   ```bash
   <skill-dir>/scripts/hermes_x_search.py \
     --query "<query>" \
     --user "<user>" \
     --count <count> \
     --since "<since>" --until "<until>" \
     --output <md|json>
   ```
3. **結果整形**: スクリプトの stdout をそのままユーザーに提示。`output=md` の場合は表形式、`json` の場合はコードフェンス内で JSON
4. **失敗時**: スクリプトの非 0 終了コードに応じてユーザーにわかりやすいエラーメッセージと対処法を返す

## 想定される失敗ケース

| ケース | 検出方法 | ユーザーへの案内 |
|--------|---------|----------------|
| `hermes` 未インストール | `command -v hermes` が空 | Hermes Agent インストール手順を案内 |
| OAuth 未認証 / 期限切れ | スクリプト終了コード `10` | `hermes login` の案内 |
| X Search ツール無効 | スクリプト終了コード `11` | `hermes tools` で有効化案内 |
| Grok レート制限 | スクリプト終了コード `12` | 時間を空けて再試行する旨を案内 |
| クエリ結果ゼロ件 | 終了コード `0`、出力が空配列 | 検索条件の見直しを提案 |
| Hermes が他ツールを呼んだ / 形式が壊れた | 終了コード `13` | raw 応答を表示しデバッグを促す |

## 既知の制約

- **キーワード検索（`--query`）の精度は Grok の判断に依存**：プロンプトで X Search ツール呼び出しを強制しているが、一般的な単語（例: "Claude Code"）の場合に Grok が tool を呼ばずに空配列を返すケースが観測されている。`--user` 指定との併用 / より具体的な単語 / 短期間指定で安定する傾向あり
- **`since` / `until` の解釈は Grok 任せ**：ISO 8601 を渡しても Grok 側で X Search のクエリ言語に変換される。期間が狭すぎる / 古すぎると 0 件になる
- **起動時間**: 1 リクエストあたり 30〜120 秒（Hermes 起動 + LLM 推論 + ツール実行）。常駐化は将来課題

## 設計メモ

- 本スキルは Claude Code 経由でも Codex 経由でも **同一の `scripts/hermes_x_search.py`** を呼ぶ。差分は呼び出し側のスキル/コマンド定義のみ
- Hermes oneshot (`hermes -z`) を内部で起動し、X Search ツールを発火させる。LLM 経由の発火のため起動オーバーヘッド（3〜8秒）あり
- セキュリティ: ラッパーは `subprocess` を `shell=False` + 引数配列で呼ぶ。ユーザー入力をシェルに直接渡さない

## 関連

- [README.md](../../README.md)
- 詳細セットアップ: [Issue #7](https://github.com/aieo-product/hermes_x_search_skill/issues/7)
- ラッパー実装: [Issue #4](https://github.com/aieo-product/hermes_x_search_skill/issues/4)
- Codex 連携: [Issue #5](https://github.com/aieo-product/hermes_x_search_skill/issues/5)
