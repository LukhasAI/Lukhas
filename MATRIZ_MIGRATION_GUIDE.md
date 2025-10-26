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
- Both `import matriz` and `import MATRIZ` work
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
from MATRIZ.core import AsyncCognitiveOrchestrator
from MATRIZ.adapters import EmotionAdapter
import MATRIZ
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
from MATRIZ.core import AsyncCognitiveOrchestrator
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

## CI Policy

**Recommended Rule:** Warn on legacy imports, block new additions

```yaml
# .github/workflows/check-matriz.yml
name: Check MATRIZ imports
on: [pull_request]
jobs:
  matriz-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Detect legacy matriz imports
        run: |
          git diff origin/main... | grep -E "^\+.*from\s+matriz\.|^\+.*import\s+matriz\b" && \
          echo "❌ New lowercase 'matriz' imports detected. Use 'MATRIZ' (uppercase)." && \
          exit 1 || echo "✅ No new lowercase imports"
```

## Testing

Both import styles work:
```bash
python3 -c "import matriz; import MATRIZ; print('Same?', matriz is MATRIZ)"
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
