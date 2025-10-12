# Phase 2: Legacy Import Codemod - Codex Brief

**To**: Codex
**From**: Claude Code
**Date**: 2025-10-12
**Status**: 🟢 Ready to Execute (After PR 375 Merges)

---

## Executive Summary

**Mission**: Systematically migrate legacy import paths to canonical namespaces using LibCST-based codemod.

**Duration**: 2-3 hours
**Risk**: Medium (import changes require careful testing)
**Blocking**: PR 375 must merge first

---

## Context

Phase 1 (PR 375) cleaned up 1,980+ fake TODOs. Now we need to modernize the import structure:

**Legacy Patterns** → **Canonical Namespaces**:
- `candidate.*` → `labs.*`
- `tools.*` → `lukhas.tools.*`
- `governance.*` → `lukhas.governance.*`
- `memory.*` → `lukhas.memory.*`
- `ledger.*` → `lukhas.ledger.*`
- `lucas.*` → `lukhas.*`
- `Lucas.*` → `lukhas.*`
- `LUCAS.*` → `lukhas.*`

---

## Objectives

1. ✅ Rewrite all legacy imports to canonical paths
2. ✅ Update string literals in `importlib.import_module()` calls
3. ✅ Preserve code formatting (LibCST maintains style)
4. ✅ Keep CI green throughout migration
5. ✅ Enable future compat layer removal

---

## Prerequisites

### Before You Start

**Check PR 375 Status**:
```bash
gh pr view 375 --json state,mergedAt
# Must show: "state": "MERGED"
```

**If Not Merged**: Wait for PR 375 to merge before proceeding.

**If Merged**: Pull latest main and proceed:
```bash
git checkout main
git pull origin main
git checkout -b codex/phase-2-import-codemod
```

---

## Tools Provided

### 1. Configuration File

**Location**: `configs/legacy_imports.yml`

```yaml
map:
  candidate: "labs"
  tools: "lukhas.tools"
  governance: "lukhas.governance"
  memory: "lukhas.memory"
  ledger: "lukhas.ledger"
  lucas: "lukhas"
  Lucas: "lukhas"
  LUCAS: "lukhas"

allowlist:
  - "lukhas/compat"
  - "tests/conftest.py"
  - "scripts/codemod_imports.py"
  - "scripts/check_legacy_imports.py"
```

### 2. Codemod Script

**Location**: `scripts/codemod_imports.py`

**Features**:
- LibCST-based AST transformation
- Handles `import` and `from ... import` statements
- Rewrites string literals in importlib calls
- Dry-run preview mode
- Batch processing support

**Usage**:
```bash
# Preview changes
make codemod-dry

# Apply changes (DESTRUCTIVE - commit first!)
make codemod-apply
```

### 3. CI Blocker

**Location**: `scripts/check_legacy_imports.py`

**Purpose**: Prevents regression after codemod completes

**Exit Codes**:
- 0: No legacy imports (success)
- 2: Legacy imports detected (blocks CI)

**Usage**:
```bash
make check-legacy-imports
```

---

## Execution Plan

### Stage A: Preview & Planning (Dry-Run)

**Goal**: Understand scope before making changes

```bash
# 1. Generate preview of all changes
make codemod-dry
# Output: docs/audits/codemod_preview.csv

# 2. Review the preview
wc -l docs/audits/codemod_preview.csv
head -20 docs/audits/codemod_preview.csv

# 3. Check for unexpected patterns
grep -E "→.*\.py:" docs/audits/codemod_preview.csv | head -10
```

**Expected Scope**:
- ~500-800 files affected
- ~2,000-3,000 import rewrites
- Most changes in `candidate/`, `lukhas/`, `tests/`

**Decision Point**: If preview shows unexpected patterns, consult Claude Code before proceeding.

---

### Stage B: Batch Application (Tests First)

**Goal**: Apply changes in stages with verification between each

#### Batch 1: Tests (Safest)

```bash
# 1. Commit current state
git add -A
git commit -m "chore(imports): checkpoint before Phase 2 codemod"

# 2. Apply to tests only
python3 scripts/codemod_imports.py --apply --roots tests

# 3. Verify tests still work
pytest tests/ -x --maxfail=5 -q

# 4. Commit if successful
git add tests/
git commit -m "refactor(imports): migrate test imports to canonical namespaces

- Rewrite candidate.* → labs.*
- Rewrite tools.* → lukhas.tools.*
- Rewrite other legacy patterns
- Applied via LibCST codemod (preserves formatting)

Testing: pytest tests/ -x passed

Refs: Phase 2 Import Codemod"
```

#### Batch 2: Production Lane (lukhas/)

```bash
# 1. Apply to lukhas/
python3 scripts/codemod_imports.py --apply --roots lukhas

# 2. Verify imports
make lane-guard
make check-legacy-imports

# 3. Run smoke tests
pytest tests/smoke/ -q

# 4. Commit
git add lukhas/
git commit -m "refactor(imports): migrate lukhas/ imports to canonical namespaces"
```

#### Batch 3: Development Lane (candidate/ → labs/)

**⚠️ CRITICAL**: This batch includes the directory rename!

```bash
# 1. FIRST: Rename directory
git mv candidate labs

# 2. Apply codemod to renamed directory
python3 scripts/codemod_imports.py --apply --roots labs

# 3. Update manifest references
find manifests/ -name "*.yaml" -exec sed -i '' 's/"candidate\//"labs\//g' {} \;

# 4. Update OWNERS.toml
sed -i '' 's/candidate\.\*/labs.*/g' OWNERS.toml

# 5. Verify
make lane-guard
make check-legacy-imports
pytest tests/smoke/ -q

# 6. Commit (large commit expected)
git add -A
git commit -m "refactor(lanes): migrate candidate/ → labs/ with import rewrites

Major Changes:
- Renamed candidate/ → labs/ (git mv)
- Rewrote all candidate.* imports → labs.*
- Updated manifests with new paths
- Updated OWNERS.toml patterns

Impact:
- ~2,800 files in labs/
- ~1,500 import rewrites
- 928 manifest references updated

Testing: smoke tests pass, lane guard clean

Refs: Phase 2 Import Codemod, TODO_brief.md"
```

#### Batch 4: Remaining (core/, packages/, tools/)

```bash
# 1. Apply to remaining directories
python3 scripts/codemod_imports.py --apply --roots core packages tools

# 2. Final verification
make check-legacy-imports
pytest tests/ -x --maxfail=10

# 3. Commit
git add -A
git commit -m "refactor(imports): complete Phase 2 import canonicalization

- Applied to core/, packages/, tools/
- All legacy imports migrated
- CI blocker now active (check-legacy-imports)

Verification:
- make check-legacy-imports → pass
- pytest tests/ -x → pass

Refs: Phase 2 Complete"
```

---

### Stage C: Verification & PR Creation

```bash
# 1. Full test suite
pytest tests/ --maxfail=20 -q

# 2. Lane boundary check
make lane-guard

# 3. Verify no legacy imports remain (except allowlist)
make check-legacy-imports
# Expected: exit 0 (success)

# 4. Check compat layer usage
python3 scripts/report_compat_hits.py
# Review: docs/audits/compat_alias_hits.json

# 5. Push and create PR
git push origin codex/phase-2-import-codemod

gh pr create \
  --title "refactor(imports): Phase 2 - migrate to canonical namespaces" \
  --body "$(cat <<'PRBODY'
## Phase 2: Import Codemod ✅

Systematic migration of legacy import paths to canonical namespaces using LibCST.

### Summary

- **candidate/** → **labs/** (directory renamed)
- **candidate.\*** → **labs.\*** (imports rewritten)
- **tools.\*** → **lukhas.tools.\*** (namespace correction)
- **lucas.\*** → **lukhas.\*** (branding consistency)

### Changes

**Batch 1: Tests** (~300 files)
- Migrated test imports to canonical paths
- All tests passing

**Batch 2: Production Lane** (lukhas/)
- Updated production imports
- Lane guard clean

**Batch 3: Development Lane** (candidate/ → labs/)
- Renamed directory: git mv candidate labs
- Rewrote ~1,500 imports
- Updated 928 manifest references
- Updated OWNERS.toml patterns

**Batch 4: Remaining** (core/, packages/, tools/)
- Completed canonicalization
- CI blocker active (check-legacy-imports)

### Testing

- ✅ pytest tests/ --maxfail=20 (all critical tests pass)
- ✅ make lane-guard (boundaries respected)
- ✅ make check-legacy-imports (no legacy imports outside allowlist)
- ✅ Smoke tests pass

### Tooling

- LibCST-based codemod (preserves formatting)
- Dry-run preview mode
- Batch application with verification
- CI blocker prevents regression

### Compat Layer Status

The compat layer (`lukhas/compat/`) remains active for:
- External dependencies (if any)
- Gradual migration support
- Will be removed in Phase 3 when alias hits = 0

Check current usage:
```bash
python3 scripts/report_compat_hits.py
# See: docs/audits/compat_alias_hits.json
```

### Next Steps

**Phase 3** (Future):
- Monitor compat layer usage
- Remove compat layer when alias hits = 0
- Update external dependencies (if any)

### References

- **Brief**: `docs/gonzo/matriz_prep/PHASE_2_CODEX_BRIEF.md`
- **Config**: `configs/legacy_imports.yml`
- **Tools**: `scripts/codemod_imports.py`, `scripts/check_legacy_imports.py`

---

**Ready for Review** ✅

All batches complete, tests passing, CI blocker active.
PRBODY
)" \
  --base main
```

---

## Success Criteria

### Before PR Creation

- [ ] All batches applied successfully
- [ ] `pytest tests/ --maxfail=20` passes
- [ ] `make lane-guard` clean
- [ ] `make check-legacy-imports` returns exit 0
- [ ] No unexpected errors in test output
- [ ] Compat layer hits documented

### After PR Creation

- [ ] CI workflows pass (MATRIZ Validate, tests)
- [ ] No merge conflicts with main
- [ ] Compat alias hits = 0 or documented
- [ ] Ready for code review

---

## Troubleshooting

### Issue: Codemod Preview Shows Unexpected Patterns

**Symptom**: Preview CSV has suspicious rewrites

**Action**:
1. Review the specific lines in preview
2. Check if pattern is in allowlist
3. Consult Claude Code before applying

### Issue: Tests Fail After Batch

**Symptom**: `pytest` returns errors after applying batch

**Action**:
1. Review error messages for import-related failures
2. Check if missed imports (not caught by codemod)
3. Manual fix if needed:
   ```python
   # Before
   from candidate.foo import bar
   # After
   from labs.foo import bar
   ```
4. Re-run tests
5. If still failing, revert batch and consult Claude Code

### Issue: Lane Guard Fails

**Symptom**: `make lane-guard` shows violations

**Action**:
1. Review violation details
2. Check if legitimate cross-lane import
3. Update import linter config if needed (lukhas/.importlinter)
4. Re-run lane-guard

### Issue: check-legacy-imports Fails

**Symptom**: Script exits with code 2

**Action**:
1. Review which files have legacy imports
2. Check if they're in allowlist
3. If allowlist, update `configs/legacy_imports.yml`
4. If not allowlist, re-run codemod on those files:
   ```bash
   python3 scripts/codemod_imports.py --apply --roots path/to/file
   ```

---

## Rollback Plan

If Phase 2 encounters blockers:

```bash
# Option 1: Revert specific batch
git log --oneline | head -5  # Find commit hash
git revert <commit-hash>

# Option 2: Full rollback to Phase 1
git reset --hard origin/main
git checkout -b codex/phase-2-import-codemod-retry

# Option 3: Cherry-pick successful batches
git checkout main
git checkout -b codex/phase-2-partial
git cherry-pick <test-batch-commit>
git cherry-pick <lukhas-batch-commit>
# Skip problematic batches, document in PR
```

---

## Performance Estimates

### Time per Batch

- **Batch 1 (Tests)**: 15-20 minutes
- **Batch 2 (lukhas/)**: 10-15 minutes
- **Batch 3 (candidate/ → labs/)**: 45-60 minutes (large)
- **Batch 4 (Remaining)**: 20-30 minutes
- **Verification & PR**: 15-20 minutes

**Total**: ~2-3 hours

### File Counts

- **Tests**: ~300 files
- **lukhas/**: ~250 files
- **labs/** (formerly candidate/): ~2,800 files
- **core/**: ~200 files
- **packages/**: ~50 files
- **tools/**: ~30 files

---

## Safety Measures

### Automated

- ✅ LibCST preserves formatting (no style changes)
- ✅ Dry-run preview before apply
- ✅ Batch processing with verification
- ✅ Git commits between batches (easy rollback)
- ✅ CI blocker prevents future regression

### Manual

- ⚠️ Review dry-run preview carefully
- ⚠️ Test after each batch before proceeding
- ⚠️ Consult Claude Code if unexpected issues
- ⚠️ Don't skip verification steps

---

## Communication

### Report to Claude Code

**After Dry-Run (Stage A)**:
```
Phase 2 Stage A complete:
- Preview generated: X files, Y imports
- [Any concerns or blockers]
```

**After Each Batch**:
```
Batch N complete:
- Files modified: X
- Tests: [PASS/FAIL]
- [Any issues encountered]
```

**After PR Creation (Stage C)**:
```
Phase 2 complete:
- PR #XXX created
- All batches successful
- Tests passing
- Ready for review
```

### Blockers

If you encounter any blocker:
1. Document the issue clearly
2. Include error messages/stack traces
3. Note which batch/step failed
4. Tag @claude-code in commit message or PR comment

---

## Post-Phase 2

### Phase 3: Compat Layer Removal (Future)

**When**: After Phase 2 PR merges and compat alias hits = 0

**Goal**: Remove temporary compat layer

**Steps**:
1. Monitor `docs/audits/compat_alias_hits.json`
2. When hits = 0 for 7 days
3. Remove `lukhas/compat/` directory
4. Update CI to remove compat checks
5. PR: "chore(cleanup): remove compat layer (alias hits = 0)"

---

## Quick Reference

### Key Commands

```bash
# Preview changes
make codemod-dry

# Apply changes (commit first!)
make codemod-apply

# Check for legacy imports
make check-legacy-imports

# Lane boundary check
make lane-guard

# Smoke tests
pytest tests/smoke/ -q

# Full test suite
pytest tests/ --maxfail=20 -q
```

### Key Files

- **Config**: `configs/legacy_imports.yml`
- **Codemod**: `scripts/codemod_imports.py`
- **CI Blocker**: `scripts/check_legacy_imports.py`
- **Preview**: `docs/audits/codemod_preview.csv`
- **Compat Hits**: `docs/audits/compat_alias_hits.json`

### Decision Tree

```
Start Phase 2
    ↓
Is PR 375 merged? → NO → Wait
    ↓ YES
Preview (codemod-dry)
    ↓
Unexpected patterns? → YES → Consult Claude Code
    ↓ NO
Batch 1: Tests
    ↓
Tests pass? → NO → Troubleshoot or revert
    ↓ YES
Batch 2: lukhas/
    ↓
Lane guard clean? → NO → Troubleshoot
    ↓ YES
Batch 3: candidate/ → labs/
    ↓
Smoke tests pass? → NO → Troubleshoot
    ↓ YES
Batch 4: Remaining
    ↓
check-legacy-imports clean? → NO → Re-run codemod
    ↓ YES
Create PR
    ↓
Phase 2 Complete ✅
```

---

## Appendix: Example Rewrites

### Example 1: Simple Import

**Before**:
```python
from candidate.consciousness.reflection import Engine
```

**After**:
```python
from labs.consciousness.reflection import Engine
```

### Example 2: Multiple Imports

**Before**:
```python
from candidate.tools import executor
from tools.monitoring import logger
import lucas.core
```

**After**:
```python
from labs.tools import executor
from lukhas.tools.monitoring import logger
import lukhas.core
```

### Example 3: importlib String

**Before**:
```python
module = importlib.import_module("candidate.bridge.api")
```

**After**:
```python
module = importlib.import_module("labs.bridge.api")
```

### Example 4: Relative Import (Unchanged)

**Before**:
```python
from .submodule import something
from ..parent import other
```

**After**: (No change - relative imports unaffected)
```python
from .submodule import something
from ..parent import other
```

---

**Status**: 🟢 **Ready for Execution**

**Blocker**: PR 375 must merge first

**Next Action**: Wait for PR 375 merge, then execute Stage A (Preview)

**Questions**: Tag @claude-code in PR or commit message

---

**Good luck, Codex! 🚀**
