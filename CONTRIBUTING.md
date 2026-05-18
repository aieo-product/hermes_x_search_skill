# Contributing to hermes_x_search_skill

歓迎します。本リポジトリは public OSS プロジェクトです。

## 基本ルール（必須）

### 1. Issue ファースト
作業は必ず issue を立ててから着手してください。リファクタ、bug fix、docs、chore も含めて例外なし。issue 番号は PR タイトル / 本文・コミットメッセージで参照します（`Refs #N` / `Closes #N`）。

### 2. PR にはテスト結果エビデンス必須
PR 本文または直後の PR コメントに、その変更に対応する試験結果を必ず添付してください。**エビデンス無しの PR はマージしません**。

| 変更種別 | 求めるエビデンス |
|---------|----------------|
| ロジック変更 | 単体テスト（pytest）の実行結果（pass/fail 件数 + 実行時間）|
| 振る舞い変更 | E2E 出力サンプル（再現コマンドと出力）、必要に応じ `evidence` ブランチへ push して URL を貼付 |
| ドキュメント変更 | レンダリング確認 or 主要リンクの疎通結果 |

### 3. セルフレビュー
人間レビューに回す前に、PR 作成者がセルフレビューコメントを投稿してください。観点：ロジック / エッジケース / セキュリティ / 機密情報スキャン結果。可能であれば別モデル（Codex 等）でのクロスレビューを併用してください。

## ガイドライン

### Issue
- 既存 issue を検索してから新規作成してください
- バグレポートには再現コマンドと期待 / 実際の出力を含めてください
- 機能要望は use case（誰がいつ何のために使うか）を書いてください

### Pull Request
- ブランチ命名: `feature/issue-N-slug` / `fix/issue-N-slug` / `docs/slug` / `chore/slug`
- PR 本文に `Closes #N` を含めて issue を自動 close
- レビューが付いたら squash merge

### コード規約
- Python: 標準ライブラリで完結を優先
- shell: `set -euo pipefail`、エラーは stderr へ
- コメント: 英語推奨（OSS 公開のため）

### テスト
- 単体テスト: `tests/` 配下、pytest 形式
- 実 Hermes を呼ぶテストは含めない（CI 不可、ローカルでのみ E2E 確認）
- 新規機能には必ず単体テストを追加

### 機密情報
**絶対にコミットしないでください：**
- `.env`、OAuth トークン、API キー
- ハンドル / メールアドレス / 個人を特定可能な情報
- セッションログ（`.hermes/`）

PR 作成前に以下を確認:
```bash
git diff --staged | grep -iE 'token|secret|api_?key|password|@[a-z0-9_]+'
```

### コミットメッセージ
- 1行目: `<type>: <summary>` 形式（`feat:` / `fix:` / `docs:` / `chore:` / `test:` / `refactor:`）80字以内
- 本文に背景・関連 issue を記載
- AI 生成時は `Co-Authored-By:` トレーラを付与

## 行動規範

[Contributor Covenant](https://www.contributor-covenant.org/) に準拠。

## 質問

[GitHub Discussions](https://github.com/aieo-product/hermes_x_search_skill/discussions) または issue でお願いします。
