## Promotion Batch #<N>

### Summary
- Files moved: <count>
- candidate/ remaining: <count>
- Coverage delta: <+/- X%>
- Quarantined tests changed: <+/- N>

### Gates
- [ ] MATRIZ validation ✅
- [ ] Coverage ≥ baseline (or `allow:coverage-drop` present)
- [ ] `artifacts/import_failures.json` empty
- [ ] Artifacts updated: promotion_log.md, batch_promotion_summary.md, where_is_which.*

### Artifacts
- artifacts/promotion_batch.plan.jsonl
- artifacts/batch_promotion_summary.md
- tests/matrix_coverage_report.md
- artifacts/import_failures.json
- artifacts/where_is_which.md / .csv

---

<!-- Dashboard bot will auto-comment with real-time metrics -->