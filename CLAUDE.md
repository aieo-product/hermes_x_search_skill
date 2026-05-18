# CLAUDE.md — hermes_x_search_skill 開発ルール

このリポジトリでの Claude Code 作業ルール。

## プロジェクト概要

Claude Code / Codex CLI から Hermes Agent 経由で X (Twitter) 検索を行うスキル。
最終ゴールは **public OSS としての公開**。

## 重要なルール

### 機密情報の取り扱い（最優先）

- **絶対にコミットしない**: `.env` / OAuth トークン / API キー / セッション ID / 個人の handle 名を埋め込んだ実行例 / Hermes 認証ファイル
- ドキュメント・コード中のサンプルでは **架空のハンドル名 / トークン例（例: `@example_user`, `xxx_TOKEN_REDACTED_xxx`）** を使うこと
- 動作確認のエビデンスをコミットする場合は、画像・ログ内に表示される個人情報がないか目視確認すること
- PR 作成前に `git diff --staged` で機密混入チェック
- `.gitignore` の対象を独断で外さない（追加は OK、緩めるのは要相談）

### 開発フロー

**1. Issue ファースト（必須）**

作業は必ず issue を立ててから着手する。リファクタ、bug fix、docs、chore も含めて例外なし。issue 番号は PR タイトル / 本文・コミットメッセージで参照する（`Refs #N` / `Closes #N`）。

**2. PR にはテスト結果エビデンス必須（必須）**

PR 本文または直後の PR コメントに、その変更に対応する試験結果を必ず添付する：
- ロジック変更：単体テスト（pytest）の実行結果（pass/fail 件数 + 実行時間）
- 振る舞い変更：E2E 出力サンプル（実コマンドと出力）、必要に応じて `evidence` ブランチへ push して URL を貼る
- ドキュメント変更：レンダリング確認 or 主要リンクの疎通結果

**エビデンス無しの PR はマージしない**。再現コマンドは PR レビュー時に追試できる形で記載する。

**3. セルフレビュー**

人間レビューに回す前に、PR 作成者がセルフレビューコメントを投稿する。可能であれば Codex などの別モデルでクロスレビューを併用する。

### コメント / PR の言語

- issue / PR / コメントは **日本語**
- コードコメントは **英語**（OSS 公開を想定）
- README は **日本語 + 必要に応じて英語見出し**

### ブランチ命名

- `feature/issue-<N>-<slug>` — 機能追加
- `fix/issue-<N>-<slug>` — バグ修正
- `chore/<slug>` — 雑務
- `docs/<slug>` — ドキュメント
- `evidence` — テストエビデンス専用（自動 push、レビュー不要）

### コミットメッセージ

- 1行目: 80 字以内、`<type>: <summary>` 形式（`feat:`, `fix:`, `docs:`, `chore:`, `test:`, `refactor:`）
- 必要に応じて本文で背景 / 関連 issue を記載
- 末尾に `Co-Authored-By: ...` トレーラ（AI 生成時）

### PR

- `Closes #N` を本文に含めて自動 close
- セルフレビュー（Codex + Claude）コメントを必ず投稿してから人間レビューに回す
- マージ前に CI green（CI 未整備の段階ではローカルチェック結果を PR コメントに添付）

### テスト

- 単体テストは `tests/` 配下に配置（pytest 想定）
- E2E は `tests/e2e/` 配下、実 Hermes 起動を伴うため CI からは除外可
- 大規模リファクタ時は Feature Flag を用いた Red/Green テスト（FF off で旧動作を再現 → FF on で新動作を確認）を推奨

### 依存追加

- Python: 標準ライブラリで完結を優先。外部依存を増やす場合は PR で正当化
- Node: 不要な依存追加禁止

## OSS 公開チェックリスト（public 化前に必ず確認）

- [ ] LICENSE が存在し、年と組織名が正しい
- [ ] README に前提条件・インストール・使い方・トラブルシュートが揃っている
- [ ] CONTRIBUTING.md がある（コントリビュータ向けガイド、後続で追加検討）
- [ ] CODE_OF_CONDUCT.md の検討
- [ ] `.gitignore` で機密情報を完全ブロック
- [ ] `git log -p` 全体に対し `grep -iE 'token|secret|api_?key|password|sk-[a-z0-9]{20,}|<maintainer-handle>'` で漏洩チェック（実際の検査時は `<maintainer-handle>` をメンテナのハンドル名で置き換える）
- [ ] サンプル / テストデータに個人情報が含まれない
- [ ] 依存ライブラリのライセンスが MIT と互換

## 参照

- [Hermes Agent README](https://github.com/NousResearch/hermes-agent)
- [Claude Code Docs](https://docs.claude.com/claude-code)
