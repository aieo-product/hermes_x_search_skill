# Issue #16 — Codex サンドボックス権限検証エビデンス

実行: 2026-05-18 morning, codex-cli 0.128.0
個人情報サニタイズ済（ハンドル → `@example_user`、tweet ID → ゼロ埋め、ローカル username → `USER`）

## 比較表

| サンドボックス設定 | 書き込み結果 | ネットワーク結果 | hermes 動作 |
|------------------|------------|----------------|-----------|
| `--sandbox read-only` | ✗ `~/.hermes/logs/agent.log` 書き込み拒否 | ✗ Connection error | ❌ 失敗 |
| `--sandbox workspace-write`（既定設定）| ✗ cwd 外不可 | ✗ Connection error | ❌ 失敗 |
| `--sandbox workspace-write` + `writable_roots=["~/.hermes"]` | ✓ 書き込み OK | ✗ Connection error | ❌ 失敗（ネット不足）|
| `--sandbox workspace-write` + `writable_roots=["~/.hermes"]` + `network_access=true` | ✓ | ✓ | ✅ **成功（47秒で実データ取得）** |
| `--sandbox danger-full-access` | ✓ | ✓ | ✅（過剰権限）|

## 結論

最小権限の組み合わせ：

```bash
codex exec --sandbox workspace-write \
  -c 'sandbox_workspace_write.writable_roots=["~/.hermes"]' \
  -c 'sandbox_workspace_write.network_access=true' \
  "<prompt>"
```

`danger-full-access` は不要、`writable_roots` は `~/.hermes` のみで十分（home 全体を開ける必要なし）。
