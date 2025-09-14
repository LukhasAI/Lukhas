# LUKHAS Public API - Constellation Migration

**Version**: 1.0
**Date**: September 14, 2025
**Status**: Frozen during Trinity → Constellation migration

This document defines the stable public APIs that must remain compatible during the Trinity → Constellation framework migration.

## 🔒 Frozen Public APIs

### Branding Bridge (`lukhas/branding_bridge.py`)
```python
# STABLE - keep these function signatures
def get_trinity_description() -> str
def get_trinity_context(emphasis: Optional[str] = None) -> dict
```

### Core Wrapper (`lukhas/core/core_wrapper.py`)
```python
# STABLE - keep these function signatures
def create_trinity_glyph(component: str) -> dict
```

### Identity Lambda ID (`candidate/core/identity/lambda_id_core.py`)
```python
# STABLE - keep these function signatures
def validate_trinity_framework(context: dict) -> bool
def trinity_status() -> dict
```

### Colonies Base (`candidate/colonies/base.py`)
```python
# STABLE - keep this function signature
def trinity_sync() -> dict
```

## 🔄 Migration Strategy

### Phase 1: Compatibility Shims (✅ DONE)
- Created `lukhas/constellation/triad/__init__.py` (new namespace)
- Created `branding/trinity/__init__.py` (backwards compatibility shim)
- Added import test in `tests/test_constellation_shims.py`

### Phase 2: Internal Symbol Conversion (🚧 IN PROGRESS)
- Convert internal `trinity_` functions to `triad_` (safe)
- Convert internal `Trinity` classes to `Triad` (safe)
- Keep public API function names unchanged via shims

### Phase 3: Documentation Updates (⏳ PENDING)
- Update internal comments and docstrings
- Convert TODO tags to dual format: `[CONSTELLATION:MESH] ⚛️`

### Phase 4: Module Moves (⏳ PENDING)
- Move `branding/trinity/` → `branding/constellation/triad/`
- Keep shim at `branding/trinity/__init__.py`

### Phase 5: Deprecation Warnings (⏳ PENDING)
- Add CI warnings for legacy `branding.trinity` imports
- Monitor usage for 2 releases before removing shims

## 🚫 Breaking Changes Not Allowed

During migration, these imports MUST continue to work:
```python
# Legacy imports - KEEP WORKING
from branding.trinity import Identity, Consciousness, Guardian
from lukhas.branding_bridge import get_trinity_context
from candidate.colonies.base import trinity_sync

# New imports - ALSO WORK
from lukhas.constellation.triad import Identity, Consciousness, Guardian
from branding.constellation.triad import Identity
```

## 📋 Symbol Inventory

### Safe to Rename (Internal Only)
- `_calculate_trinity_*` → `_calculate_triad_*`
- `_validate_trinity_*` → `_validate_triad_*`
- `_get_trinity_*` → `_get_triad_*`
- `trinity_compliance` → `triad_compliance` (internal vars)

### Must Preserve (Public API)
- Function names in public modules
- CLI command names
- Configuration keys in external files
- API endpoint paths

## ⚠️ Special Cases

### Test Files
- Test function names can be converted: `test_trinity_*` → `test_triad_*`
- Test assertions should use new patterns where possible
- Keep some legacy tests for compatibility verification

### JSON/YAML Configuration
- External config files should keep current keys
- Add new keys alongside old ones during transition
- Phase out old keys in future major version

### Documentation
- Markdown files can reference new Constellation terminology
- Code examples should demonstrate both old and new patterns
- API docs must document both during transition

---

**Enforcement**: This document represents a contract during migration. Changes to frozen APIs require team approval and version bumps.

**Review Schedule**: Weekly during active migration, monthly afterward until shims are removed.

**Completion Criteria**: Migration complete when CI shows zero usage of deprecated patterns for 2 consecutive releases.
