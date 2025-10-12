# Phase 2: Ready for Execution ✅

**Status**: 🟢 **ALL SYSTEMS GO**
**Date**: 2025-10-12
**Prerequisite**: PR 375 merged ✅

---

## Executive Summary

Phase 2 is **fully prepared** and **ready for Codex execution**. All tools validated, surgical fixes applied, safety measures in place.

---

## What's Complete ✅

### Phase 1 Results
- ✅ **PR #375 merged**: 351 files, 1,980+ fake TODOs removed, 1,977 orphaned noqa fixed
- ✅ **Real TODOs preserved**: 397 items with owner hints in `docs/audits/todos_final.csv`
- ✅ **Remediation infrastructure**: All scripts created and tested

### Phase 2 Preparation
- ✅ **Comprehensive brief**: [`PHASE_2_CODEX_BRIEF.md`](PHASE_2_CODEX_BRIEF.md) (707 lines)
- ✅ **Quick start guide**: [`CODEX_START_PHASE_2.md`](CODEX_START_PHASE_2.md)
- ✅ **JSON-safe manifest updater**: `scripts/update_manifest_paths.py`
- ✅ **Compat telemetry**: `scripts/check_alias_hits.py`
- ✅ **Makefile targets**: `update-manifest-paths`, `check-alias-hits`
- ✅ **All scripts tested**: Help, dry-run, and live execution validated

---

## Surgical Fixes Applied (Founder Review)

Your high-impact improvements are incorporated:

### 1. JSON-Safe Manifest Updates ✅
**Problem**: Original docs suggested `sed` on YAML, but manifests are JSON
**Fix**:
```bash
# Old (unsafe):
sed -i '' 's/"candidate\//"labs\//g' manifests/*.yaml

# New (JSON-safe):
python3 scripts/update_manifest_paths.py --root manifests --from candidate/ --to labs/
python3 scripts/gen_rules_coverage.py
python3 docs/check_links.py --root .
rg -n "candidate/" manifests || true
```

**Validation**: Dry-run tested - **640 of 929 manifests** will be updated

### 2. Compat Alias Telemetry ✅
**Addition**: Track compat layer usage during migration
```bash
# After each batch:
python3 scripts/check_alias_hits.py

# With threshold enforcement (future):
python3 scripts/check_alias_hits.py --max-hits 100
```

**Current status**: 0 alias hits (fresh start)

### 3. Explicit Success Gates ✅
**Added to both docs**:
- ✅ JSON manifests updated via script (no 'candidate/' under manifests)
- ✅ Compat alias hits reported and trending down
- ✅ `pytest --collect-only` passes (catch import errors early)
- ✅ Packaging sanity (pyproject.toml includes lukhas, labs, MATRIZ)

### 4. Enhanced Verification Steps ✅
**Batch 1 (Tests)**:
```bash
pytest tests/ -x --maxfail=5 -q
pytest --collect-only -q  # NEW: Catch import errors
```

**Batch 3 (candidate/ → labs/)**:
```bash
git mv candidate labs
python3 scripts/codemod_imports.py --apply --roots labs
python3 scripts/update_manifest_paths.py --root manifests --from candidate/ --to labs/  # NEW
python3 scripts/gen_rules_coverage.py  # NEW
python3 docs/check_links.py --root .  # NEW
rg -n "candidate/" manifests || true  # NEW: Verification
make lane-guard
make check-legacy-imports
pytest tests/smoke/ -q
python3 scripts/check_alias_hits.py  # NEW: Telemetry
```

---

## Tool Validation

### Manifest Updater
```bash
$ python3 scripts/update_manifest_paths.py --root manifests --from candidate/ --to labs/ --dry-run

DRY RUN SUMMARY:
  Root:         manifests
  Pattern:      candidate/ → labs/
  Files scanned: 929
  Files would be updated:  640
======================================================================
```

### Alias Hits Checker
```bash
$ python3 scripts/check_alias_hits.py

======================================================================
COMPAT LAYER ALIAS HITS REPORT
======================================================================
Total Hits: 0
======================================================================
```

### Import Codemod (Already Tested)
```bash
$ make codemod-dry
# Generates: docs/audits/codemod_preview.csv
```

---

## Execution Checklist for Codex

### Prerequisites ✅
- [x] PR 375 merged
- [x] Main branch up-to-date
- [x] All tools created and tested
- [x] Documentation complete
- [x] Safety measures in place

### Stage A: Preview (5-10 min)
- [ ] Create branch: `codex/phase-2-import-codemod`
- [ ] Run: `make codemod-dry`
- [ ] Review: `docs/audits/codemod_preview.csv`
- [ ] Report findings to user

### Stage B: Batch Execution (2-3 hours)
- [ ] **Batch 1**: Tests (~300 files, 15-20 min)
- [ ] **Batch 2**: lukhas/ (~250 files, 10-15 min)
- [ ] **Batch 3**: candidate/ → labs/ (~2,800 files, 45-60 min) ⚠️ **Largest**
- [ ] **Batch 4**: core/, packages/, tools/ (~280 files, 20-30 min)

### Stage C: Verification & PR (15-20 min)
- [ ] Full test suite: `pytest tests/ --maxfail=20`
- [ ] Lane boundaries: `make lane-guard`
- [ ] Legacy imports: `make check-legacy-imports` (exit 0)
- [ ] Manifest verification: `rg -n "candidate/" manifests` (empty)
- [ ] Alias hits: `python3 scripts/check_alias_hits.py`
- [ ] Create PR with detailed description

---

## Safety Measures

### Automated
- ✅ LibCST preserves code formatting
- ✅ Dry-run preview before apply
- ✅ Batch processing with verification
- ✅ Git commits between batches (easy rollback)
- ✅ CI blocker prevents future regression
- ✅ JSON-safe manifest updates

### Manual
- ✅ Comprehensive execution guide (707 lines)
- ✅ Troubleshooting section with rollback plans
- ✅ Success criteria at each stage
- ✅ Communication protocol with founder
- ✅ Decision tree for error handling

---

## Expected Impact

### Files Affected
- **Tests**: ~300 files
- **lukhas/**: ~250 files
- **labs/** (formerly candidate/): ~2,800 files
- **core/**: ~200 files
- **packages/**: ~50 files
- **tools/**: ~30 files
- **manifests/**: 640 JSON files
- **Total**: ~4,230 files + manifests

### Import Rewrites
- **Estimated**: 3,000+ import statements
- **Patterns**:
  - `candidate.*` → `labs.*`
  - `tools.*` → `lukhas.tools.*`
  - `governance.*` → `lukhas.governance.*`
  - `memory.*` → `lukhas.memory.*`
  - `lucas.*` → `lukhas.*`

### Manifest Updates
- **640 JSON manifests** with path updates
- **928 total manifests** scanned
- **0 corruption risk** (JSON-safe script)

---

## Communication

### Codex Reports To
- **After Stage A**: Preview findings, any concerns
- **After Each Batch**: Success/failure, issues encountered
- **If Blocked**: Tag @claude-code with error details

### User Monitors
- **Real-time**: Git commits as batches complete
- **Alias hits**: Compat layer usage trending
- **PR creation**: Final review before merge

---

## Rollback Strategy

If any batch fails:

```bash
# Option 1: Revert specific batch
git log --oneline | head -5
git revert <commit-hash>

# Option 2: Full rollback
git reset --hard origin/main
git checkout -b codex/phase-2-import-codemod-retry

# Option 3: Cherry-pick successful batches
git checkout main
git checkout -b codex/phase-2-partial
git cherry-pick <batch-1-commit>
git cherry-pick <batch-2-commit>
# Document partial completion in PR
```

---

## Success Metrics

### Before PR Creation
- [ ] `pytest tests/ --maxfail=20` passes
- [ ] `make lane-guard` clean (exit 0)
- [ ] `make check-legacy-imports` clean (exit 0)
- [ ] `rg -n "candidate/" manifests` empty result
- [ ] Compat alias hits = 0 or documented
- [ ] No unexpected test failures

### After PR Merge (Phase 3 Prep)
- [ ] Monitor compat alias hits for 7 days
- [ ] When hits = 0: Remove compat layer
- [ ] Update CI to enforce import standards

---

## Documentation Tree

```
docs/gonzo/matriz_prep/
├── TODO_brief.md                    # Original plan
├── CODEX_HANDOFF.md                 # Phase 1 instructions (updated)
├── PR_375_REMEDIATION.md            # Phase 1 issue analysis
├── PR_375_SUMMARY.md                # Phase 1 executive summary
├── PHASE_2_CODEX_BRIEF.md          # Phase 2 comprehensive guide ⭐
├── CODEX_START_PHASE_2.md          # Phase 2 quick start ⭐
└── PHASE_2_READY.md                # This document ⭐

scripts/
├── harvest_todos.py                 # TODO scanner (Phase 1)
├── create_issues_from_csv.py       # GitHub issue generator
├── fix_orphaned_noqa.py            # Orphaned noqa cleanup
├── codemod_imports.py              # LibCST import rewriter ⭐
├── check_legacy_imports.py         # CI blocker ⭐
├── update_manifest_paths.py        # JSON-safe manifest updater ⭐
└── check_alias_hits.py             # Compat telemetry ⭐

configs/
└── legacy_imports.yml              # Import mapping config
```

---

## Quick Commands Reference

```bash
# Preview changes
make codemod-dry

# Apply imports
make codemod-apply

# Update manifests (Batch 3)
make update-manifest-paths

# Check legacy imports
make check-legacy-imports

# Check alias hits
make check-alias-hits

# Lane boundaries
make lane-guard

# Smoke tests
pytest tests/smoke/ -q

# Full tests
pytest tests/ --maxfail=20 -q
```

---

## Timeline Estimate

- **Stage A (Preview)**: 5-10 minutes
- **Stage B (Batch 1)**: 15-20 minutes
- **Stage B (Batch 2)**: 10-15 minutes
- **Stage B (Batch 3)**: 45-60 minutes ⚠️ **Largest batch**
- **Stage B (Batch 4)**: 20-30 minutes
- **Stage C (Verification & PR)**: 15-20 minutes

**Total**: ~2-3 hours

---

## Status: 🟢 **READY FOR EXECUTION**

All prerequisites met. All tools validated. Safety measures in place. Documentation complete.

**Codex**: Read [`PHASE_2_CODEX_BRIEF.md`](PHASE_2_CODEX_BRIEF.md) and begin when ready.

**Founder**: Monitor git commits and PR for review.

---

**Phase 2 is production-ready. Let's ship it! 🚀**
