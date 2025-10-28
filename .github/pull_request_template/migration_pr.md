---
name: Migration PR (imports/ AST rewriter)
about: PR template for migration work (e.g., MATRIZ migration)
---

## Migration PR Summary

**Migration target:** (e.g., `matriz` -> `MATRIZ`)  
**Files / directories changed:**  
**Dry-run artifact:** `dryrun_<group>.json` attached? [yes/no]  
**Migration summary file:** `migration-summary.md` present? [yes/no]

### Migration Summary (paste)
- Files changed:
- Imports updated:
- Tests run and outcome:
- Benchmark impact:
- Risk statement:

### CI/Validation Checklist
- [ ] Dry-run artifacts attached
- [ ] AST diffs reviewed
- [ ] `isort`/`black`/`ruff --fix` run post-rewrite
- [ ] Smoke tests: PASS
- [ ] Per-group tests: PASS
- [ ] Migration-summary.md included and complete
- [ ] Two reviewers (tech + infra) approved

### Notes
- Limit scope to <200 lines changed per PR where possible.
- Include `EXCEPTION` tags for justified `noqa` with TTL if applicable.
