# Dream Consolidation - Simplified Plan

## Discovery
`labs/consciousness/dream/` already exists with 65 items and is the **canonical** dream location.
The root-level directories are redundant:
- `dream/` - 22 files (duplicates labs content)
- `dreamweaver_helpers_bundle/` - helper files (UI components, configs)

## Revised Strategy (MUCH SIMPLER)

### Phase 1: Archive Redundant Directories  
```bash
# Archive dream/
mkdir -p archive/dream_2025-10-26
git mv dream archive/dream_2025-10-26/

# Archive dreamweaver_helpers_bundle/ 
mkdir -p archive/dreamweaver_helpers_bundle_2025-10-26  
git mv dreamweaver_helpers_bundle archive/dreamweaver_helpers_bundle_2025-10-26/
```

### Phase 2: Create Compatibility Shim
Create `dream/__init__.py` that redirects to `labs.consciousness.dream`:

```python
"""Compatibility shim: dream → labs.consciousness.dream"""
import importlib, warnings
warnings.warn(
    "Top-level 'dream' module is deprecated. Import 'labs.consciousness.dream' instead.",
    DeprecationWarning,
    stacklevel=2
)
_mod = importlib.import_module("labs.consciousness.dream")
__all__ = getattr(_mod, '__all__', [])
```

### Phase 3: Test & Commit
```bash
make smoke
pytest tests/
git add -A
git commit -m "chore(dream): archive redundant root-level dream directories, add compatibility shim"
```

## Benefits
- ✅ No file moves needed - canonical location already correct
- ✅ Zero risk of import breakage
- ✅ Simple, fast (~10 min total)
- ✅ Easy rollback
- ✅ Preserves all history
