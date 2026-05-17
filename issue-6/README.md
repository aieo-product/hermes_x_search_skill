# Issue #6 — E2E 動作確認エビデンス

> このフォルダには [#6](https://github.com/aieo-product/hermes_x_search_skill/issues/6) の E2E 動作確認で取得した出力サンプルが格納されています。
> 個人特定可能な情報はサニタイズ済み（ユーザーハンドルは `@example_user`、ツイート ID は `0...0`、システムパスの username は `USER` に置換）。

## ファイル一覧

| ファイル | シナリオ | 内容 |
|---------|---------|------|
| `scenario1.md` | ユーザー指定検索（Markdown） | `--user example_user --count 5` の正常実行結果 |
| `scenario2-fixed.md` | キーワード検索（修正後） | `--query 'Claude Code' --count 5` — 0件（Grok 任せの既知制約） |
| `scenario3.md` | 期間指定 + キーワード | `--query 'Hermes Agent' --since 2026-05-15 --until 2026-05-18` |
| `scenario4.json` | JSON 出力 | `--user example_user --count 3 --output json` の構造化結果 |
| `scenario5.stderr` | 異常系：X Search OFF（モック） | exit 11 + ユーザー向けメッセージ |
| `scenario5.stdout` | 異常系：stdout（空であるべき）| — |
| `scenario-codex-v2.log` | Codex 経由実行 | `codex exec` でスキルが発見され、wrapper が呼ばれることを確認したログ |

## 取得日

2026-05-18
