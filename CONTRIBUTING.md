# Contributing to hermes_x_search_skill

歓迎します。本リポジトリは public OSS プロジェクトです。

## ガイドライン

### Issue
- 既存 issue を検索してから新規作成してください
- バグレポートには再現コマンドと期待 / 実際の出力を含めてください
- 機能要望は use case（誰がいつ何のために使うか）を書いてください

### Pull Request
- ブランチ命名: `feature/issue-N-slug` / `fix/issue-N-slug` / `docs/slug` / `chore/slug`
- PR 本文に `Closes #N` を含めて issue を自動 close
- セルフレビュー（テスト結果・機密スキャン結果）を PR コメントで投稿
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
