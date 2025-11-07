# Ruff Violation Reduction Plan
**Created:** 2025-11-06
**Baseline:** 11,000 violations (2025-11-03)
**Current:** 5,327 violations (after auto-fixes)
**Progress:** -52% (-5,673 violations)

---

## 🎯 Current State

### Violations by Category (Top 10)
```
1,251  E402   module-import-not-at-top-of-file     [  ] Manual review required
1,215  UP035  deprecated-import                     [  ] Import + usage changes
  613  F821   undefined-name                        [  ] Requires investigation
  460  F401   unused-import                         [*] Some auto-fixable
  315  B904   raise-without-from-inside-except      [  ] Manual review
  225  SIM102 collapsible-if                        [  ] Manual simplification
  173  F403   undefined-local-with-import-star      [  ] Star import cleanup
  166  B008   function-call-in-default-argument     [  ] Design pattern review
  133  B018   useless-expression                    [  ] Dead code removal
  128  RUF012 mutable-class-default                 [  ] Dataclass review
```

**Total:** 5,327 violations across all rules

---

## ✅ Completed (Phase 1 - Auto-fixes)

**Completed:** 2025-11-06
**Commit:** 7afadcf63

### Auto-fix Wave 1: 437 violations eliminated
- **I001** (410): Unsorted imports → Alphabetized
- **F541** (32): F-string missing placeholders → Removed
- **UP015** (13): Redundant open modes → Simplified
- **F841** (9): Unused variables → Cleaned
- **C414** (4): Unnecessary casts → Removed

**Impact:** 5,679 → 5,327 (-8% immediate reduction)

---

## 🔄 In Progress (Active PRs)

### E402: Import Ordering (1,251 violations)
**Existing PRs:**
- **#942**: Fix E402 - Import ordering (189 violations)
- **#941**: Fix - Reorder module docstrings for E402

**Distribution:**
- `matriz/consciousness/`: 269 violations (21%)
- `core/governance/`: 153 violations (12%)
- `core/consciousness/`: 114 violations (9%)
- `lukhas_website/lukhas/`: 76 violations (6%)
- `tests/unit/`: 59 violations (5%)
- Other: 580 violations (46%)

**Strategy:** Continue PR-based manual review
- **Effort:** 4-8 hours per 100-200 violations
- **Risk:** Medium (can affect import-time side effects)
- **Expected reduction:** -600 to -800 violations (conservative)

### UP035: Deprecated Imports (1,215 violations)
**Existing PR:**
- **#868**: Refactor - Migrate 72 deprecated imports (UP035)

**Common patterns:**
```python
# OLD (deprecated in Python 3.9+)
from typing import List, Dict, Tuple, Optional

def foo(items: List[str]) -> Dict[str, int]:
    ...

# NEW (built-in generics)
def foo(items: list[str]) -> dict[str, int]:
    ...
```

**Strategy:** Batch migrations by module
- **Effort:** 2-4 hours per 100-150 violations
- **Risk:** Low (syntax-level change, well-defined)
- **Expected reduction:** -1,000 to -1,200 violations (aggressive)

---

## 📋 Next Steps (Priority Order)

### Priority 1: Complete Active PRs (2-3 days)
1. ✅ **Merge PR #942** - E402 fixes (189 violations)
2. ✅ **Merge PR #941** - E402 docstring reordering
3. ✅ **Merge PR #868** - UP035 migrations (72 violations)

**Expected impact:** 5,327 → ~5,066 (-261, -5%)

### Priority 2: UP035 Campaign (1 week)
**Target:** Migrate remaining 1,143 UP035 violations

**Approach:**
1. Create automated migration script using `libcst` or similar
2. Batch by directory (50-100 files at a time)
3. Create PRs for each batch:
   - Batch 1: `matriz/` (estimated 300 violations)
   - Batch 2: `core/` (estimated 250 violations)
   - Batch 3: `lukhas_website/` (estimated 150 violations)
   - Batch 4: `tests/` (estimated 150 violations)
   - Batch 5: Other modules (estimated 293 violations)

**Validation per batch:**
- Run `make smoke` to ensure no breakage
- Run affected module's unit tests
- Check type annotations with `mypy` (if applicable)

**Expected impact:** 5,066 → ~3,923 (-1,143, -22%)

### Priority 3: E402 Targeted Campaign (2-3 weeks)
**Target:** Reduce E402 from 1,251 to <500

**Strategy:**
1. **Phase 1:** Identify files with simple patterns (just comment blocks)
   - Estimated: 400-500 violations
   - Create automated PR with comment-aware import reorganization
2. **Phase 2:** Manual review for complex cases
   - sys.path manipulation: ~100-150 files
   - Conditional imports: ~200-300 files
   - Environment setup: ~150-200 files

**Expected impact:** 3,923 → ~3,172 to ~3,423 (-500 to -751, -13% to -19%)

### Priority 4: F821 Undefined Names (3-4 weeks)
**Target:** Investigate and fix 613 F821 violations

**Approach:**
1. Categorize by type:
   - Missing imports: ~200 (quick wins)
   - Typos: ~50 (immediate fixes)
   - False positives (TYPE_CHECKING blocks): ~100 (add # type: ignore)
   - Genuine bugs: ~263 (requires investigation)

2. Create issues for genuine bugs requiring design decisions

**Expected impact:** 3,172 → ~2,359 to ~2,672 (-500 to -813, -16% to -26%)

### Priority 5: Quick Wins (1-2 days)
**Target:** Auto-fixable and low-hanging fruit

Rules with potential auto-fixes or simple patterns:
- **F401** (460): Unused imports → Some auto-fixable with `--fix`
- **SIM102** (225): Collapsible if → Some safe to collapse
- **B018** (133): Useless expressions → Dead code removal
- **RUF012** (128): Mutable class defaults → Dataclass field(default_factory)

**Expected impact:** -200 to -400 violations

---

## 🎯 Milestone Targets

### 30-Day Target (2025-12-03)
**Goal:** <2,000 violations (from 11,000 baseline)
**Reduction:** -82%

**Path to goal:**
1. Complete auto-fixes: 11,000 → 5,327 ✅ (Done)
2. Merge active PRs: 5,327 → 5,066 ✅ (2-3 days)
3. UP035 campaign: 5,066 → 3,923 (1 week)
4. E402 phase 1: 3,923 → 3,423 (1 week)
5. F821 quick wins: 3,423 → 2,923 (3-4 days)
6. Quick wins (F401, SIM102, etc.): 2,923 → 2,523 (1-2 days)
7. Buffer for unexpected issues: 2,523 → ~2,200

**Feasibility:** **ACHIEVABLE** with dedicated focus

### 60-Day Target (2026-01-03)
**Goal:** <1,000 violations
**Reduction:** -91%

Requires completing:
- All UP035 migrations
- All E402 simple cases
- 50% of F821 investigations
- All quick wins

### 90-Day Target (2026-02-03)
**Goal:** <500 violations (A+ health score)
**Reduction:** -95%

---

## 🚧 Known Blockers

### Test Failures (Pre-existing)
**Issue:** `test_api_acl.py::test_valid_token_allows_access` failing
**Status:** Pre-existing from auth changes (commit 76cb00299 or later)
**Impact:** Blocks `make smoke` from passing
**Owner:** Auth/API team
**Priority:** P0 (blocks CI)

**Recommendation:** Fix auth issue before large-scale lint PRs

### Import-Time Side Effects
**Risk:** Moving imports (E402) can change initialization order
**Mitigation:**
- Manual review of all E402 fixes
- Test affected modules thoroughly
- Rollback plan for each PR

### Type Annotation Complexity
**Risk:** UP035 changes may expose mypy issues
**Mitigation:**
- Run mypy on affected files before/after
- Add `# type: ignore` where necessary
- Document mypy configuration changes

---

## 📊 Success Metrics

### Primary Metrics
1. **Total violations:** Track weekly (target: -10% per week)
2. **Smoke test pass rate:** Maintain 100%
3. **CI green rate:** Monitor for regressions

### Secondary Metrics
1. **E402 violations:** Track separately (target: <500 by Day 30)
2. **UP035 violations:** Track separately (target: <100 by Day 30)
3. **F821 violations:** Track separately (target: <300 by Day 30)

### Quality Gates
- No PR merged if smoke tests fail
- No PR merged if reduces test coverage
- No PR merged without manual review for E402 changes

---

## 🔧 Tooling Recommendations

### Automation Scripts Needed
1. **up035_migrator.py** - Automated typing → builtins migration
   - Use `libcst` for safe AST transformations
   - Generate per-directory PRs

2. **e402_analyzer.py** - Categorize E402 violations
   - Simple comment blocks (auto-fixable)
   - sys.path manipulation (manual)
   - Conditional imports (manual)

3. **f821_categorizer.py** - Triage undefined names
   - Missing imports (suggest fixes)
   - Typos (suggest corrections with fuzzy match)
   - False positives (auto-ignore)

### CI Integration
- Add ruff baseline check (fail if violations increase)
- Add smoke test requirement for all PRs
- Add violation count reporting in PR descriptions

---

**Plan Owner:** Claude (Audit Agent)
**Next Review:** 2025-11-13 (1 week)
**Full Re-audit:** 2025-12-03 (30 days)
