# Issue #19 — media_urls フィールド対応 エビデンス

実装後に複数パターンで E2E 検証した結果。個人特定可能な情報はサニタイズ済み。

## ファイル
- `md-no-media.md` — 通常検索の Markdown 出力（新しい「メディア」列が追加されたことを確認）
- `e2e-media-test1.json` — `--user NousResearch` の JSON 出力（媒体: `media: []`）
- `e2e-media-test2.json` — `filter:images cats` クエリの JSON 出力（媒体: `media: []`）
- `e2e-media-debug.stdout` — `filter:images sunset` の debug 実行

## 結論

- ラッパーの schema・パーサ・renderer はメディア対応完了（単体テスト 33 件 pass、うち 5 件が media 関連）
- ただし Hermes Agent の X Search ツール（`tools/x_search_tool.py`）が現状メディア URL 専用フィールドを持たないため、Grok の応答に URL が含まれない限り `media: []` となる
- 画像付きと明示できるポストでも `media: []` を返すケース多数（実機確認）
- 「捏造禁止」プロンプトを明示しているため、嘘の URL は混入しない（最悪でも空）
