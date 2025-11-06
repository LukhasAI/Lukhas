# T4 Lint Platform - Baseline Metrics Report
**Date**: 2025-11-06
**Branch**: replace/t4-lint-platform
**Phase**: 1 - Dry-run & Baseline Collection

## Summary Statistics

### Total Violations by Category
- **Total**: 647 violations detected across production lanes
- **Annotated**: 0 (baseline - no structured annotations yet)
- **Missing Annotations**: 647 (100%)
- **Quality Issues**: 0

### Top Violation Categories (from dry-run)
1. **F821** (undefined-name): ~150+ occurrences
2. **F401** (unused-import): ~100+ occurrences  
3. **RUF006** (asyncio.create_task): ~80+ occurrences
4. **B904** (raise-without-from): ~50+ occurrences
5. **F403** (import-star): ~40+ occurrences
6. **SIM102** (collapsible-if): ~30+ occurrences
7. **B018** (useless-expression): ~20+ occurrences
8. **B008** (function-call-default): ~10+ occurrences
9. **F811** (redefinition): ~10+ occurrences
10. **RUF012** (mutable-class-default): ~8+ occurrences
11. **E701/E702** (multiple-statements): ~5+ occurrences
12. **SIM105/SIM115/SIM117** (simplify): ~10+ occurrences

### Distribution by Production Lane
- **MATRIZ/consciousness**: ~350 violations (largest)
- **core/orchestration**: ~150 violations
- **memory**: ~80 violations
- **core** (other): ~40 violations
- **identity**: ~10 violations
- **lukhas**: ~10 violations
- **api**: ~7 violations

## Autofix Potential

### High Autofix Candidates (safe with ruff --fix)
- **I001** (import-sorting): Not counted but detected by linter
- **SIM102** (collapsible-if): ~30 violations
- **RUF001** (ambiguous-unicode): Minimal
- **F401** (unused-import): ~100 violations (overlap with T4 Unused Imports)

### Codemod Candidates (B008 pilot ready)
- **B008** (function-call-default): ~10 violations
  - Pilot target: lukhas/core (small scope first)
  - Transformer: fix_b008.py (LibCST)
  - Status: Ready for dry-run

### Manual Review Required
- **F821** (undefined-name): ~150 violations
  - Many are missing imports (np, pd, torch, etc.)
  - Heuristic suggestions available for common aliases
  - High-impact but requires case-by-case review

- **RUF006** (asyncio.create_task): ~80 violations
  - Need to assess if tasks should be stored/tracked
  - Pattern: fire-and-forget vs. managed tasks

- **B904** (raise-without-from): ~50 violations
  - Requires semantic review of exception handling
  - Suggestion: `raise ... from err` or `raise ... from None`

- **F403** (import-star): ~40 violations
  - Codemod opportunity: analyze used names and make explicit
  - Requires AST analysis per file

## T4 Platform Deployment Status

### Phase 0: ✅ Complete
- Policy document: `T4_LINT_PLATFORM.md`
- Opportunities document: `T4_LINT_OPPORTUNITIES.md`
- Annotator: `lint_annotator.py`
- Validator: `check_lint_issues_todo.py`
- Autofix script: `lint_autofix.sh`
- B008 codemod: `fix_b008.py` + `run_fix_b008.py`
- GitHub workflow: `t4-lint-platform.yml`
- Branch pushed: `replace/t4-lint-platform`

### Phase 1: ✅ Complete
- Dry-run annotator: 647 violations detected
- Validator baseline: 0/647 annotated (100% gap)
- JSON reports generated
- Baseline metrics documented

## Next Steps (Phase 2-5)

### Phase 2: Autofix Safe Issues
1. Run `lint_autofix.sh` on small package (e.g., `core/orchestration`)
2. Review diffs carefully
3. Create PR grouped by package
4. Human review required before merge
5. Track PR acceptance rate

### Phase 3: B008 Codemod Pilot
1. Dry-run on `lukhas/core` (~2-3 files expected)
2. Review transformations
3. Apply if safe
4. Run full test suite
5. Create pilot PR
6. If successful, expand to other lanes

### Phase 4: Triage & Intent Registry
1. Annotate high-impact F821 violations with heuristics
2. Create GH issues for top 20 reserved items
3. Assign owners + tickets for planned state
4. Ingest logs to Intent Registry
5. Query stale items (>30 days)

### Phase 5: Enable Strict CI (After 2-4 weeks)
1. Monitor autofix PR acceptance (target: >60%)
2. Ensure annotation quality (target: >70% with owner+ticket)
3. Flip validator to strict mode in CI
4. Require passing validation before merge

## Risk Mitigation

### Conservative Defaults
- All changes start in dry-run mode
- Human review required for all autofix PRs
- No automatic merging
- Small package-scoped batches
- Full test suite runs on all changes

### Rollback Plan
- Backup files created (.b008bak suffix)
- Git revert available for all PRs
- Policy docs backed up in docs/backup_t4/
- Intent Registry provides audit trail

## Acceptance Criteria

Before enabling strict CI:
- Autofix PR acceptance rate ≥ 60%
- Annotation Quality Score ≥ 70% (owner+ticket for planned/committed)
- Top-10 lint codes show ≤ 50% of baseline violations
- No critical test regressions

## Metrics Tracking

Intent Registry will track:
- Per-code violation counts over time
- Annotation lifecycle states
- Staleness (age of reserved items)
- Owner/ticket coverage
- Time-to-implement
- Autofix PR acceptance rate

---

**Report Generated**: 2025-11-06 by T4 Lint Platform
**Next Review**: After Phase 2 autofix PR creation
