# Test Blocking Issues - November 13, 2025

## Summary
Comprehensive audit of test failures blocking CI/CD pipeline and local development.

**Status**: 4 blocking issues identified, 2 fixed ✅

---

## ✅ FIXED: Issue #1 - aka_qualia MetricsConfig Missing

**File**: `aka_qualia/metrics.py`
**Test**: `tests/unit/aka_qualia/test_metrics.py`
**Error**: `ImportError: cannot import name 'MetricsConfig' from 'aka_qualia.metrics'`

**Root Cause**:
- Test imports `MetricsConfig` but class didn't exist
- Pytest collects modules before respecting `@pytest.mark.skip`
- Import failure prevents test collection

**Fix Applied** (Commit `660605191`):
```python
class MetricsConfig:
    """Placeholder configuration class for aka_qualia metrics."""
    pass

class AkaQualiaMetrics:
    """Placeholder metrics class for aka_qualia consciousness measurements."""
    def __init__(self, config=None):
        self.config = config or MetricsConfig()
```

**Result**: ✅ Test collection now succeeds, skips as intended

---

## ✅ FIXED: Issue #2 - aiohttp Virtual Environment Corruption

**File**: `.venv/lib/python3.9/site-packages/aiohttp/client_exceptions.py`
**Affected Tests**: All tests importing from `lukhas.api.*`, `lukhas.observability.*`
**Error**: `SyntaxError: from __future__ imports must occur at the beginning of the file`

**Root Cause**:
- `from __future__ import annotations` appears on line 63 (should be line 1-5)
- aiohttp package is corrupted in virtual environment
- Affects ~50+ test files via transitive imports

**Evidence**:
```python
# Line 55-63 in corrupted file:
class ClientError(Exception):
    """Base class for client connection errors."""
from __future__ import annotations  # ❌ Wrong location!
```

**Fix Applied**:
```bash
source .venv/bin/activate
pip uninstall aiohttp -y
pip install aiohttp==3.11.11
# Successfully downgraded from 3.13.2 (corrupted) to 3.11.11 (clean)
```

**Result**: ✅ aiohttp SyntaxError resolved, API tests can now import successfully

**Original Priority**: 🔴 CRITICAL - Was blocking 50+ API/observability tests

---

## ❌ BLOCKING: Issue #3 - Widespread Pydantic V1 Deprecation

**Scope**: 23 files across multiple modules
**Affected Modules**:
- `lukhas_website/lukhas/identity/validation_schemas.py` (10+ validators)
- `lukhas_website/lukhas/api/glyphs.py:50`
- `aka_qualia/models.py:64`
- And 20+ more files

**Error**: `PydanticDeprecatedSince20: Pydantic V1 style @validator validators are deprecated`

**Root Cause**:
- Codebase uses Pydantic V1 `@validator` decorator throughout
- Project has Pydantic V2 installed
- Deprecation warning treated as error in strict mode
- Affects production code (not just experimental)

**Fix Required**:
Migrate from Pydantic V1 to V2 syntax:

```python
# Before (V1):
from pydantic import BaseModel, validator

class ProtoQualia(BaseModel):
    @validator("colorfield")
    def validate_colorfield(cls, v):
        return v

# After (V2):
from pydantic import BaseModel, field_validator

class ProtoQualia(BaseModel):
    @field_validator("colorfield")
    @classmethod
    def validate_colorfield(cls, v):
        return v
```

**Affected Files** (23 total):
- Production: `lukhas_website/lukhas/identity/validation_schemas.py` (OAuth, WebAuthn)
- Production: `lukhas_website/lukhas/api/glyphs.py` (Glyph API)
- Experimental: `aka_qualia/models.py`
- And 20+ more across candidate/, lukhas_website/

**Recommended Fix Strategy**:
1. Create automated migration script using AST transformation
2. Batch convert all @validator to @field_validator
3. Test each module after conversion
4. OR: Use Jules AI to create 23 targeted PRs (one per file)

**Priority**: 🔴 CRITICAL - Blocks all tests that import Pydantic models (widespread)

**Reference**: https://docs.pydantic.dev/2.12/migration/

---

## ❌ BLOCKING: Issue #4 - lukhas.api.analytics Missing Exports

**File**: `lukhas/api/analytics.py`
**Test**: `tests/unit/lukhas/api/test_analytics.py`
**Error**: `ImportError: cannot import name 'AnalyticsAggregator' from 'lukhas.api.analytics'`

**Root Cause**:
- Test expects `AnalyticsAggregator` class
- Class doesn't exist in `lukhas/api/analytics.py`
- Similar pattern to aka_qualia metrics issue

**Investigation Needed**:
1. Check if `AnalyticsAggregator` should exist or test is outdated
2. If needed, implement placeholder or remove test
3. Verify all other expected exports from test file

**Fix Options**:
- **Option A**: Add placeholder class (if experimental)
- **Option B**: Implement full AnalyticsAggregator (if production-ready)
- **Option C**: Remove/skip test (if obsolete)

**Priority**: 🟡 MEDIUM - Affects analytics test suite only

---

## Quick Wins (Ordered by Impact)

### 1. Fix aiohttp Corruption (🔴 CRITICAL)
```bash
source .venv/bin/activate
pip uninstall aiohttp -y
pip install aiohttp==3.11.11
python -m pytest tests/unit/lukhas/api/ -x --tb=short
```
**Expected Impact**: Unblocks 50+ API tests

### 2. Fix analytics ImportError (🟡 MEDIUM)
```bash
# After investigating lukhas/api/analytics.py:
# Either add placeholder or remove test
python -m pytest tests/unit/lukhas/api/test_analytics.py -v
```
**Expected Impact**: Unblocks analytics test suite

### 3. Migrate aka_qualia to Pydantic V2 (🟡 MEDIUM)
```bash
# Update aka_qualia/models.py validators
python -m pytest tests/unit/aka_qualia/ -v
```
**Expected Impact**: Unblocks aka_qualia tests (low priority, experimental)

---

## Test Status Progress

**Initial State**:
```
collected 386 items / 1 error
ERROR - ImportError: MetricsConfig not found
```

**After Fix #1 (MetricsConfig)**:
```
collected 386 items / 2 errors
ERROR - aiohttp SyntaxError (blocking 50+ tests)
ERROR - Pydantic V1 deprecation (blocking 23+ files)
```

**After Fix #2 (aiohttp)**:
```
collected 386 items / 2 errors
ERROR - Pydantic V1 deprecation (widespread, 23 files)
ERROR - AnalyticsAggregator import error
```

**Progress**: 2/4 issues resolved ✅ (50% complete)

---

## Next Steps

1. **Immediate** (Today):
   - [x] Reinstall aiohttp to fix venv corruption ✅
   - [x] Verify API tests can import after aiohttp fix ✅
   - [x] Push fix #1 (MetricsConfig) to main ✅ (commit `660605191`)
   - [ ] Create Pydantic V2 migration strategy
   - [ ] Investigate AnalyticsAggregator import

2. **Short-term** (This week):
   - [ ] **CRITICAL**: Pydantic V1 → V2 migration (23 files)
     - Option A: Create automated AST migration script
     - Option B: Create 23 Jules sessions (one per file)
     - Estimated time: 4-6 hours for full migration
   - [ ] Fix AnalyticsAggregator import issue
   - [ ] Run full test suite to verify no new issues

3. **Long-term** (Next sprint):
   - [ ] Add pre-commit hook to prevent Pydantic V1 validators
   - [ ] Comprehensive venv health check and cleanup
   - [ ] Add CI check for import-time errors
   - [ ] Document test suite maintenance procedures

---

**Created**: 2025-11-13 at 14:20 GMT
**Updated**: 2025-11-13 at 14:21 GMT
**Fixed Issues**: 2/4 ✅ (50% complete)
**Remaining Blockers**: Pydantic V2 migration (23 files), AnalyticsAggregator
**Estimated Time to Clear**: 4-6 hours (Pydantic migration is the bottleneck)
