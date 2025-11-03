# Bridge Gap Follow-up & Metrics

**Goal:** Track progress and verify impact of bridge fixes.

**Metrics to Track:**
- `collection_errors` (baseline: 211 → target: <10)
- `tests_collecting` (current: 14/42 → target: 42/42)
- `pass_rate_percent` (target: >90%)
- Impact per bridge PR

**Tasks:**
- Create `release_artifacts/matriz_readiness_v1/metrics/bridge_progress.csv`
- Maintain `BRIDGE_PROGRESS.md` with weekly updates
- Post-mortem after Phase 2 automation

**CSV Format:**
```csv
bridge,pr_url,files,compile_ok,before,after,delta,date
lukhas.identity,https://github.com/.../123,2,Y,211,204,-7,2025-11-04
```

**Acceptance:**
- Metrics updated after each PR
- Dashboard shows progress to <50 target
- Final sign-off checklist completed
