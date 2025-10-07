---
status: draft
type: sprint-plan
owner: unknown
module: v0.04
redirect: false
moved_to: null
---

![Status: Draft](https://img.shields.io/badge/status-draft-orange)

# v0.04 Sprint Plan: Test Infrastructure & Code Quality

**Sprint Goal:** Enable full CI/CD pipeline with green test suite

**Duration:** 2 weeks (2025-10-06 to 2025-10-20)
**Team:** TBD
**Success Metric:** 182 test errors → 0, CI pipeline green

---

## Objectives (from v0.03-prep Health Report)

### Critical Path (Must Complete)

**1. Fix Test Collection Errors: 182 → 0**
- **Owner:** Testing Lead
- **Effort:** 3-5 days
- **Impact:** Unblocks CI/CD pipeline

Tasks:
- [ ] Analyze 182 ModuleNotFoundError patterns
- [ ] Fix missing `__init__.py` in candidate/* packages
- [ ] Update test imports to actual module locations
- [ ] Validate: `python3 -m pytest --collect-only` → 0 errors

**2. Fix Top 10 Syntax Error Files (~280 errors)**
- **Owner:** Code Quality Lead
- **Effort:** 2-3 days
- **Impact:** Reduces ruff errors by 36%

Files to fix:
```
  72 errors: vivox/emotional_regulation/event_integration.py
  46 errors: qi/autonomy/self_healer.py
  40 errors: lukhas_website/lukhas/dna/helix/dna_memory_architecture.py
  39 errors: qi/docs/jurisdiction_diff.py
  34 errors: core/integration/global_initialization.py
  26 errors: qi/safety/ci_report.py
  26 errors: qi/ui/cockpit_api.py
  21 errors: qi/ops/auto_safety_report.py
  21 errors: qi/safety/teq_replay.py
  19 errors: core/notion_sync.py
```

Tasks:
- [ ] Run `scripts/ci/triage_syntax_errors.py`
- [ ] Fix real syntax errors (f-strings, parens, indentation)
- [ ] Ignore style-only issues (imports before docstrings)
- [ ] Validate: ruff errors < 500

**3. Import Ratchet to Threshold ≥2**
- **Owner:** Import System Lead
- **Effort:** 1 day
- **Impact:** Reduces legacy imports 640 → ~400

Tasks:
- [ ] Run: `python3 tools/codemod_lukhas_from_ledger.py --threshold 2 --apply`
- [ ] Test: `make smoke`
- [ ] Update baseline: `UPDATE_BASELINE=1 make gate-legacy`
- [ ] Commit with provenance

---

### High Priority (Should Complete)

**4. Auto-Fix Unused Imports: 371 → 0**
- **Owner:** Automated (CI)
- **Effort:** 1 hour
- **Impact:** Clean code quality metrics

Tasks:
- [ ] Run: `python3 -m ruff check . --select=F401 --fix`
- [ ] Validate: `make smoke`
- [ ] Commit: "refactor: remove 371 unused imports"

**5. Organize Root Directory: 29 → <15 files**
- **Owner:** Documentation Lead
- **Effort:** 2-3 hours
- **Impact:** Professional repository appearance

Tasks:
- [ ] Move: MCP_*_DELIVERY.md → docs/deliverables/
- [ ] Move: *_SUMMARY.md → docs/reports/
- [ ] Move: T4_*_GUIDE.md → docs/guides/
- [ ] Archive: .copilot_tasks.md, test_file_for_why.txt
- [ ] Validate: `ls -1 | wc -l` < 15

**6. Distribute Orphaned Tests: 39 → module-local**
- **Owner:** Testing Lead
- **Effort:** 1-2 days
- **Impact:** Module self-containment

Tasks:
- [ ] Classify tests: module-specific vs integration
- [ ] Move module tests to respective module/tests/
- [ ] Keep integration tests in root tests/integration/
- [ ] Update CI test discovery

---

### Medium Priority (Nice to Have)

**7. Complete Docs Migration: 75 remaining**
- **Owner:** Documentation Lead
- **Effort:** 1 day
- **Impact:** Full module doc colocalization

Tasks:
- [ ] Run: confidence ≥0.75 batch migration
- [ ] Review ambiguous docs manually
- [ ] Create redirect stubs
- [ ] Update docs index

**8. Enable Full CI Pipeline**
- **Owner:** DevOps Lead
- **Effort:** 2-3 days
- **Impact:** Automated quality gates

Tasks:
- [ ] Configure tier-1 test suite in CI
- [ ] Add syntax error budget gate
- [ ] Enable import ratchet enforcement
- [ ] Set up test coverage reporting

**9. Performance Baseline Metrics**
- **Owner:** Performance Team
- **Effort:** 3 days
- **Impact:** Measurable performance targets

Tasks:
- [ ] Run benchmark suite
- [ ] Document p95 latencies
- [ ] Establish regression thresholds
- [ ] Generate baseline report

---

## Sprint Timeline

### Week 1 (Oct 6-12)
- **Days 1-2:** Fix test collection errors (Critical #1)
- **Days 3-4:** Fix top 10 syntax files (Critical #2)
- **Day 5:** Import ratchet + unused imports (Critical #3, High #4)

### Week 2 (Oct 13-20)
- **Days 6-7:** Root directory organization + test distribution (High #5-6)
- **Days 8-9:** Docs migration + CI pipeline (Medium #7-8)
- **Day 10:** Sprint review + v0.04 release

---

## Success Criteria (Exit Gates)

### Must Pass (Required for v0.04 Release)
- [ ] Test collection: 0 errors
- [ ] Smoke tests: 27/27 passing
- [ ] Import baseline: <500 legacy imports
- [ ] Syntax errors: <500 (from 782)

### Should Pass (Strongly Recommended)
- [ ] Root files: <15
- [ ] Unused imports: 0
- [ ] Tier-1 tests: >90% passing
- [ ] CI pipeline: Green

### Nice to Have (Bonus)
- [ ] Full docs migrated
- [ ] Performance baseline established
- [ ] Coverage report >75%

---

## Risk & Mitigation

**Risk 1:** Test fixes expose deeper import issues
- **Mitigation:** Fix systematically, one module at a time
- **Fallback:** Mark problematic tests as xfail with tracking

**Risk 2:** Syntax fixes break working code
- **Mitigation:** Fix + smoke test after each file
- **Fallback:** Revert individual file, mark as known issue

**Risk 3:** Import ratchet breaks compatibility
- **Mitigation:** Test thoroughly before baseline update
- **Fallback:** Revert codemod, keep threshold at 3

---

## Tracking & Reporting

**Daily Standup Questions:**
1. Test collection errors reduced?
2. Syntax errors reduced?
3. Any new blockers discovered?

**Weekly Review:**
- **Monday:** Sprint kickoff, assign ownership
- **Friday:** Progress review, adjust priorities

**Metrics Dashboard:**
```bash
# Generate daily metrics
python3 scripts/sprint/v04_metrics.py
```

**Artifacts:**
- `artifacts/v04_daily_progress.json` - Daily metrics
- `docs/v0.04/SPRINT_RETROSPECTIVE.md` - End of sprint
- `docs/v0.04/v0.04-HEALTH_REPORT.md` - Release health

---

## Definition of Done

A task is "done" when:
1. Code committed with T4/0.01% message format
2. Smoke tests pass (`make smoke`)
3. No regressions in baseline metrics
4. Documentation updated if needed
5. Provenance tracked in commit message

---

## Resources & References

**Key Documents:**
- `docs/v0.03/KNOWN_ISSUES.md` - Issues to fix
- `docs/v0.03/v0.03-prep-HEALTH_REPORT.md` - Baseline state
- `scripts/ci/triage_syntax_errors.py` - Syntax analysis tool
- `tools/codemod_lukhas_from_ledger.py` - Import migration tool

**Commands:**
```bash
# Check progress
make smoke                    # Smoke tests
make gate-legacy             # Import baseline
python3 scripts/ci/triage_syntax_errors.py  # Syntax status

# Apply fixes
python3 -m ruff check . --fix  # Auto-fix imports
python3 tools/codemod_lukhas_from_ledger.py --apply --threshold 2

# Update baselines
UPDATE_BASELINE=1 make gate-legacy
```

---

**Created:** 2025-10-06
**Sprint Lead:** TBD
**Review Date:** 2025-10-13 (mid-sprint), 2025-10-20 (end)

