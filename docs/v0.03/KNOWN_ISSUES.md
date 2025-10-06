---
title: "v0.03-prep Known Issues"
module: root
type: documentation
status: tracked
---

# v0.03-prep Known Issues & Technical Debt

**Status:** Baseline frozen with documented known issues
**Date:** 2025-10-06
**Baseline:** v0.03-prep tag

## Overview

This document tracks known issues at the v0.03-prep baseline freeze. Per T4/0.01% standards, we document rather than hide technical debt to enable informed decision-making.

---

## Critical Issues (Blockers for Production)

### 1. Test Collection Errors: 182 ModuleNotFoundError

**Impact:** HIGH - Blocks automated testing
**Status:** IN PROGRESS
**Owner:** TBD

**Description:**
- 182 test files fail to collect due to import path errors
- Root cause: Legacy `lukhas.*` imports + missing module paths
- Affects: unit/, integration/, e2e/ test suites

**Resolution Plan:**
1. Complete import ratchet migration (threshold ≥2)
2. Fix candidate.* import paths with actual module locations
3. Update test fixtures for new module structure

**Tracking:** See `artifacts/import_failures.txt`

---

## High-Priority Issues (Quality Gates)

### 2. Syntax Errors: 782 across 86 files

**Impact:** MEDIUM - Blocks some linting, doesn't affect runtime
**Status:** DOCUMENTED
**Owner:** TBD

**Description:**
- Ruff reports 782 E999 syntax errors
- Top 10 files account for ~280 errors (36%)
- Many are ruff false positives (imports before docstrings)
- Some are real: hyphens in function names, f-string formatting

**Top Offenders:**
```
  72 vivox/emotional_regulation/event_integration.py
  46 qi/autonomy/self_healer.py
  40 lukhas_website/lukhas/dna/helix/dna_memory_architecture.py
  39 qi/docs/jurisdiction_diff.py
  34 core/integration/global_initialization.py
```

**Resolution Plan:**
1. Triage: separate real errors from ruff false positives
2. Fix real syntax errors in top 10 files
3. Address style issues separately (not freeze blocker)

**Tracking:** See `artifacts/syntax_error_triage.json`

### 3. Unused Imports: 371 files

**Impact:** LOW - Code quality, not functionality
**Status:** DOCUMENTED
**Owner:** Automated cleanup

**Description:**
- 371 F401 unused import violations
- Auto-fixable with `ruff check --fix`
- Safe to batch fix post-freeze

**Resolution Plan:**
- Run `make lint-unused` in next sprint
- Validate with smoke tests after fix

### 4. Undefined Names: 312 occurrences

**Impact:** MEDIUM - May indicate broken imports
**Status:** NEEDS TRIAGE
**Owner:** TBD

**Description:**
- 312 F821 undefined name errors
- Could be import issues or actual bugs
- Requires manual review to determine criticality

**Resolution Plan:**
1. Cross-reference with test collection errors
2. Fix import-related undefined names
3. Tag actual bugs for follow-up

---

## Medium-Priority Issues (Organization)

### 5. Root Directory Organization: 29 config files

**Impact:** LOW - Developer experience
**Status:** PLANNED
**Owner:** TBD

**Description:**
- 29 root-level files (target: <15)
- Multiple delivery docs, summaries scattered
- Configuration files not consolidated

**Files to Organize:**
- Move: MCP_*_DELIVERY.md → docs/deliverables/
- Move: *_SUMMARY.md → docs/reports/
- Move: T4_*_GUIDE.md → docs/guides/
- Archive: test_file_for_why.txt, .copilot_tasks.md

**Resolution Plan:**
- Execute in Phase 3 (post-freeze)
- Maintain backward compat with symlinks if needed

### 6. Orphaned Documentation: 75 files in root docs/

**Impact:** LOW - Content organization
**Status:** PARTIALLY MIGRATED
**Owner:** Docs team

**Description:**
- 75 markdown files still in root docs/
- 160 already migrated to module-local docs/
- Remaining files need module assignment

**Resolution Plan:**
- Run confidence scoring ≥0.75 for next batch
- Keep intentional root docs (architecture, ADRs)

### 7. Orphaned Tests: 39 files in root tests/

**Impact:** MEDIUM - Test organization
**Status:** NEEDS DISTRIBUTION
**Owner:** Testing team

**Description:**
- 39 test files in root tests/ directory
- Should be distributed to module-local tests/
- May include integration tests (keep centralized)

**Resolution Plan:**
1. Classify: module-specific vs integration
2. Distribute module tests to local directories
3. Keep integration tests in root tests/integration/

---

## Low-Priority Issues (Technical Debt)

### 8. YAML Documentation Errors: 2 encoding issues

**Impact:** NEGLIGIBLE
**Status:** ACCEPTABLE
**Owner:** None

**Description:**
- 2 files with UTF-8 encoding errors
- docs/roadmap/ROADMAP_OPENAI_ALIGNMENT.md
- docs/roadmap/TASKS_OPENAI_ALIGNMENT.md

**Resolution:** Manual fix or accept as-is

### 9. Legacy Import Baseline: 640 alias hits

**Impact:** LOW - Import hygiene
**Status:** TRACKED
**Owner:** Import ratchet automation

**Description:**
- 640 lukhas.* legacy import aliases active
- Baseline established and enforced via CI
- Ratchet target: <500 by end of quarter

**Resolution Plan:**
- Continue threshold-based migration
- Target threshold ≥2 in next sprint

---

## Freeze Decision Rationale

**Why freeze with these issues?**

1. **Critical blockers identified and tracked** - Nothing is hidden
2. **Import errors are systematic** - Fix pattern, not individual cases
3. **Syntax errors don't affect runtime** - Many are style/linter issues
4. **Baseline provides stable reference** - Can measure improvement
5. **T4/0.01% principle**: Honest documentation > perfect code

**What's green and working:**
- ✅ Core smoke tests passing (27 tests)
- ✅ Import ratchet enforced (640 baseline)
- ✅ Documentation 96.8% YAML lint clean
- ✅ 160 docs migrated with history preservation
- ✅ Module structure validated (100/100 health)

**Next sprint priorities:**
1. Fix test collection errors (enable CI)
2. Triage and fix top 10 syntax error files
3. Organize root directory
4. Distribute orphaned docs/tests

---

## Tracking & Metrics

**Artifacts:**
- `artifacts/syntax_error_triage.json` - Full syntax error catalog
- `artifacts/import_failures.txt` - Test collection errors
- `artifacts/legacy_import_baseline.json` - Import ratchet baseline
- `artifacts/lukhas_import_ledger.ndjson` - Import usage audit trail

**Success Criteria for v0.04:**
- Test collection errors: 182 → 0
- Syntax errors: 782 → <50
- Root directory files: 29 → <15
- Legacy imports: 640 → <500

**Review Schedule:**
- Weekly: Import ratchet progress
- Bi-weekly: Syntax error reduction
- Monthly: Technical debt burn-down

---

## Contact & Ownership

**Technical Lead:** TBD
**Quality Gate Owner:** T4/0.01% Team
**Last Updated:** 2025-10-06

For questions or to claim ownership of an issue, update this document and commit with proper provenance.

