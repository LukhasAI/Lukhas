# MATRIZ Case Standardization - Migration Guide

**Date:** 2025-10-26
**Status:** ✅ Compatibility Layer Active
**Branch:** chore/standardize-MATRIZ-2025-10-26

## Summary

MATRIZ case standardization is complete with a compatibility layer that allows both import styles during migration.

## What Changed

### 1. Git Index Fixed ✅
- Removed duplicate lowercase `matriz/` entries (41 files)
- All files now tracked as `MATRIZ/` (uppercase) - 242 files
- Commit: `661d79a49`

### 2. Compatibility Layer Added ✅
- `MATRIZ/__init__.py` updated with sys.modules aliasing
- Both `import matriz` and `import matriz` work
- DeprecationWarning emitted for lowercase imports
- Commit: `aed134f9b`

## Current State

**Import Inventory:**
- **401 occurrences** of lowercase `matriz` imports found
- Breakdown:
  - artifacts/ (test logs): ~350 occurrences (safe to ignore)
  - Active code: ~51 occurrences (requires migration)

**Key Files with Legacy Imports:**
```
tests/performance/test_router_fast_path.py
tests/matriz/test_traces_tier1.py
tests/matriz/test_policy_engine.py
serve/main.py
core/symbolic/dast_engine.py
adapters/cloud_consolidation.py
```

Full list: `/tmp/matriz_imports.lst`

## Preferred Import Style

**✅ CORRECT (Use This):**
```python
from matriz.core import AsyncCognitiveOrchestrator
from matriz.adapters import EmotionAdapter
import matriz
```

**⚠️  DEPRECATED (Will Be Removed Q2 2026):**
```python
from matriz.core import AsyncCognitiveOrchestrator  # Emits DeprecationWarning
from matriz.adapters import EmotionAdapter          # Emits DeprecationWarning
import matriz                                        # Emits DeprecationWarning
```

## Migration Strategy

### Phase 1: Now - Q1 2026 (Soft Migration)
- ✅ Compatibility layer active
- ✅ Both import styles work
- ⚠️  Lowercase imports emit warnings
- **Action:** Update new code to use `MATRIZ` (uppercase)
- **Policy:** Allow existing lowercase imports, prevent new ones

### Phase 2: Q1 2026 (Active Migration)
- Run AST rewriter package-by-package
- ~50 imports per PR to minimize conflicts
- Target: Critical paths first (serve/, core/, tests/)

### Phase 3: Q2 2026 (Cleanup)
- Remove compatibility layer from `MATRIZ/__init__.py`
- Verify zero lowercase imports remain
- Update release notes

## How to Migrate (Manual)

**Before:**
```python
from matriz.core import AsyncCognitiveOrchestrator
```

**After:**
```python
from matriz.core import AsyncCognitiveOrchestrator
```

## How to Migrate (AST Rewriter - Recommended)

```bash
# Dry-run for specific package
python3 scripts/consolidation/rewrite_matriz_imports.py --dry-run --path tests/

# Apply if safe
python3 scripts/consolidation/rewrite_matriz_imports.py --path tests/
git add -A
git commit -m "chore(imports): migrate matriz -> MATRIZ in tests/ (AST)"
```

## CI & Pre-commit Integration (Preventing Future Regressions)

To lock in the MATRIZ consolidation and prevent accidental reintroduction of lowercase `matriz` imports, we add two guardrails:

### 1. GitHub Actions (PR Warning Job)
- **Path:** `.github/workflows/matriz-import-check.yml`
- **Behavior:** Scans the repository on PR open/sync and reports legacy `matriz` imports
- **Mode:** *Warning by default.* To enforce blocking, set `BLOCK_LEGACY=1` in the workflow or repo-level variables, which will make the job fail on any occurrences
- **Output:** Uploads `/tmp/matriz_imports_report.txt` as artifact for debugging

### 2. Pre-commit Hook (Local, Staged-File Checks)
- **Hook:** `scripts/consolidation/check_matriz_imports_precommit.sh`
- **Config:** `.pre-commit-config.yaml` adds a local hook that inspects staged Python files
- **Behavior:** Warns by default; to block local commits, developers can set `PRE_COMMIT_BLOCK_MATRIZ=1` in their shell environment (or CI can set this for gated branches)

### How to Flip to Blocking Enforcement

**For CI:**
- Open `.github/workflows/matriz-import-check.yml`
- Change `BLOCK_LEGACY: "0"` → `"1"` (or set repo variable `BLOCK_LEGACY=1`)
- PRs with legacy imports will fail

**For local commits:**
- Set `export PRE_COMMIT_BLOCK_MATRIZ=1` in developer shells or CI environment
- Pre-commit hook will block commits with lowercase imports

### Setup Instructions for Developers

```bash
# Install pre-commit (one-time)
pip install pre-commit

# Install the git hook
pre-commit install

# Optional: run against all files for initial check / to see warnings
pre-commit run --all-files
```

### Nightly Audit (Optional)

Run repo-wide grep nightly and create a ticket with the current inventory of `matriz` occurrences. This keeps migration progress visible.

### Rationale

- **Warning-mode** ensures no surprise CI failures at rollout; helps track remaining import sites
- After migration sweep of critical components, flip CI to blocking to prevent new regressions
- Non-destructive checks can be removed/modified if enforcement needs to be paused

### Recommended Timeline

1. **Keep warning-mode for 2-4 weeks**
2. **Run nightly audit** to track progress
3. **Migrate active imports** in critical paths (serve/, core/, tests/)
4. **Flip CI to blocking** to prevent new lowercase imports
5. **Tighten pre-commit enforcement** by encouraging `PRE_COMMIT_BLOCK_MATRIZ=1`

## Testing

Both import styles work:
```bash
python3 -c "import matriz; import matriz; print('Same?', matriz is MATRIZ)"
# Output: DeprecationWarning... Same? True
```

## Rollback

If needed, revert these commits:
```bash
git revert aed134f9b  # Compatibility layer
git revert 661d79a49  # Git index fix
```

## Timeline

- **Now:** Compatibility layer active, gradual migration encouraged
- **Q1 2026:** AST-based migration sprint (~51 imports)
- **Q2 2026:** Remove compatibility layer
- **Total Duration:** ~6 months migration window

## Impact

- ✅ Cross-platform compatibility (macOS + Linux)
- ✅ Zero immediate breakage
- ✅ Clear deprecation path
- ✅ Gradual, low-risk migration
- ✅ Professional T4-compliant approach

---

**Questions?** See [full consolidation session summary](CONSOLIDATION_SESSION_SUMMARY.md)
