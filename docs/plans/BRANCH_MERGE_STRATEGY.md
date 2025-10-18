---
title: Branch Merge Strategy - Cleanup & Integration
updated: 2025-10-18
version: 1.0
owner: LUKHAS Core Team
status: active
tags: [git, branches, merge, cleanup]
---

# Branch Merge Strategy & Cleanup

## 📊 Branch Audit Results

**Total Branches**: 300+ (local + remote)
**Branches Ahead of Main**: 15
**Merge Candidates**: 12 high-value branches

## 🎯 High-Value Merge Candidates

### Category 1: Documentation Enhancements (Priority: HIGH)
These add valuable operational documentation without code changes.

| Branch | Commits | Content | Risk | Action |
|--------|---------|---------|------|--------|
| `docs/ga-deployment-runbook` | +1 | GA deployment procedures | LOW | ✅ MERGE |
| `docs/dependency-audit-trail` | +1 | Dependency audit documentation | LOW | ✅ MERGE |
| `docs/matriz-eval-harness` | +1 | MATRIZ evaluation harness + Makefile | LOW | ✅ MERGE |
| `docs/rc-soak-test-results` | +1 | RC soak test documentation | LOW | ✅ MERGE |

**Impact**: Improved operational documentation, better DevOps workflows

---

### Category 2: E402 Import Hygiene (Priority: MEDIUM)
Sequential batches fixing E402 import-before-statement violations.

| Branch | Commits | Files Fixed | Risk | Action |
|--------|---------|-------------|------|--------|
| `refactor/e402-simple-batch-2` | +1 | 5 test files | LOW | ✅ MERGE |
| `refactor/e402-simple-batch-3` | +1 | 5 files | LOW | ✅ MERGE |
| `refactor/e402-simple-batch-4` | +1 | 3 files | LOW | ✅ MERGE |
| `refactor/e402-simple-batch-5` | +1 | Unknown | LOW | ⚠️ CHECK |
| `refactor/e402-simple-batch-6` | +1 | Unknown | LOW | ⚠️ CHECK |
| `refactor/e402-simple-batch-7` | +1 | Unknown | LOW | ⚠️ CHECK |
| `refactor/e402-simple-batch-8` | +1 | Unknown | LOW | ⚠️ CHECK |

**Impact**: Reduced E402 linting errors, improved code hygiene

**Note**: Main already has comprehensive E402 fixes via PR #430, check for conflicts

---

### Category 3: Testing Infrastructure (Priority: HIGH)
| Branch | Commits | Content | Risk | Action |
|--------|---------|---------|------|--------|
| `feat/comprehensive-testing-task5-phase1` | +1 | Comprehensive testing strategy + deployment validation | LOW | ✅ MERGE |

**Impact**: Enhanced test coverage, deployment validation framework

---

### Category 4: Already Reviewed (Priority: N/A)
| Branch | Commits | Content | Status | Action |
|--------|---------|---------|--------|--------|
| `codex/exec-plan-ph1-3` (PR #431) | +2 | Phase 1-4 automated execution | REVIEWED | ❌ SKIP (conflicts with our work) |
| `pr-431-review` | +2 | Local copy of PR #431 | DUPLICATE | ❌ DELETE |

---

## 🔄 Merge Execution Plan

### Phase 1: Documentation Merges (Safe, No Conflicts)
```bash
git checkout main
git merge --no-ff docs/ga-deployment-runbook -m "docs(ops): merge GA deployment runbook"
git merge --no-ff docs/dependency-audit-trail -m "docs: merge dependency audit trail"
git merge --no-ff docs/matriz-eval-harness -m "docs(matriz): merge evaluation harness"
git merge --no-ff docs/rc-soak-test-results -m "docs: merge RC soak test results"
```

**Expected Result**: 4 documentation files added, 0 conflicts

---

### Phase 2: Testing Infrastructure Merge
```bash
git merge --no-ff feat/comprehensive-testing-task5-phase1 -m "feat(test): merge comprehensive testing strategy"
```

**Expected Result**: Test infrastructure added, possible minor conflicts in Makefile

---

### Phase 3: E402 Refactor Merges (Check for Conflicts)
```bash
# Check each batch for conflicts with PR #430
git merge --no-ff refactor/e402-simple-batch-2 -m "refactor: merge E402 batch 2 (5 test files)"
git merge --no-ff refactor/e402-simple-batch-3 -m "refactor: merge E402 batch 3 (5 files)"
git merge --no-ff refactor/e402-simple-batch-4 -m "refactor: merge E402 batch 4 (3 files)"

# Check batches 5-8 individually (verify no overlap with existing fixes)
for batch in 5 6 7 8; do
  echo "Checking refactor/e402-simple-batch-$batch..."
  git diff main..refactor/e402-simple-batch-$batch --name-only
done
```

**Expected Result**: ~20 files fixed, possible overlaps to resolve

---

## 🗑️ Branch Cleanup Strategy

### Branches to Delete After Merge
- `docs/ga-deployment-runbook` → Delete after merge
- `docs/dependency-audit-trail` → Delete after merge
- `docs/matriz-eval-harness` → Delete after merge
- `docs/rc-soak-test-results` → Delete after merge
- `feat/comprehensive-testing-task5-phase1` → Delete after merge
- `refactor/e402-simple-batch-*` → Delete after merge (if merged)
- `pr-431-review` → Delete (local duplicate)

### Stale Branches to Archive (Not Ahead of Main)
Review branches from >30 days ago with no commits ahead:
```bash
git for-each-ref --sort=committerdate --format='%(committerdate:short) %(refname:short)' refs/heads/ | \
  awk '$1 < "2025-09-18" {print $2}'
```

Action: Archive to `archived-branches.txt` and delete locally

---

## ⚠️ Conflict Resolution Strategy

### Expected Conflicts

#### 1. Makefile (docs/matriz-eval-harness)
- **Cause**: Multiple branches adding targets
- **Resolution**: Merge both sets of targets, alphabetize

#### 2. E402 Files (refactor/e402-simple-batch-*)
- **Cause**: PR #430 already fixed E402 in production files
- **Resolution**: Check for overlap, skip if already fixed

#### 3. Test Files (feat/comprehensive-testing-task5-phase1)
- **Cause**: May add tests in directories with recent changes
- **Resolution**: Keep both, ensure no duplicate test names

---

## 📊 Expected Outcomes

### Files Added
- **Documentation**: ~4-6 new .md files in docs/
- **Tests**: ~3-5 new test files
- **Makefile Targets**: ~5-10 new targets

### Code Quality Improvements
- **E402 Errors**: Reduced by ~15-20 files
- **Test Coverage**: Improved by deployment validation tests
- **Documentation Coverage**: Improved operational docs

### Branch Count Reduction
- **Before**: 300+ branches
- **After Merge**: 290+ branches (merge 12)
- **After Cleanup**: ~250 branches (delete 40+ stale)

---

## 🚀 Execution Steps

### Step 1: Backup Current State
```bash
git branch backup-before-branch-merge-$(date +%Y%m%d)
git tag pre-branch-merge-$(date +%Y%m%d)
```

### Step 2: Execute Phase 1 (Docs)
```bash
git checkout main
git merge --no-ff docs/ga-deployment-runbook
git merge --no-ff docs/dependency-audit-trail
git merge --no-ff docs/matriz-eval-harness
git merge --no-ff docs/rc-soak-test-results
```

### Step 3: Execute Phase 2 (Testing)
```bash
git merge --no-ff feat/comprehensive-testing-task5-phase1
```

### Step 4: Execute Phase 3 (E402 - Conditional)
Check for overlaps first, then merge if clean

### Step 5: Push to Remote
```bash
git push origin main
```

### Step 6: Delete Merged Branches
```bash
git branch -d docs/ga-deployment-runbook
git branch -d docs/dependency-audit-trail
git branch -d docs/matriz-eval-harness
git branch -d docs/rc-soak-test-results
git branch -d feat/comprehensive-testing-task5-phase1
git branch -d pr-431-review
```

---

## 📋 Success Criteria

- ✅ All documentation branches merged without conflicts
- ✅ Testing infrastructure merged successfully
- ✅ E402 fixes merged (or skipped if redundant)
- ✅ No broken tests after merge
- ✅ Main pushed to remote successfully
- ✅ Merged branches deleted
- ✅ Git history remains clean

---

## 🔍 Post-Merge Validation

```bash
# Run tests
make smoke
make test

# Check for syntax errors
ruff check .

# Validate manifests
python scripts/validate_contract_refs.py

# Check git status
git status
git log --oneline -10
```

---

**Status**: Ready for Execution
**Risk Level**: LOW (mostly documentation)
**Estimated Time**: 30-45 minutes
**Recommended**: Execute Phase 1 & 2 immediately

---

**Last Updated**: 2025-10-18
**Author**: Claude Code
