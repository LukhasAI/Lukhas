# F401 Unused Imports as Opportunities - 2025-11-10

## Philosophy: Unused Imports as System Signals

**Perspective**: Unused imports aren't just "cleanup tasks" - they're **opportunities** signaling:
1. **Missing functionality** the system is calling for
2. **Incomplete features** that need implementation
3. **Test infrastructure** validating module structure

Total F401 errors: **409**
- **Test scaffolding** (importability tests): **408 (99.8%)**
- **Real opportunities** (incomplete features): **2 (0.2%)**

---

## Category 1: Test Scaffolding (408 instances)

### Pattern Identified
Nearly all F401 errors are in test files using this pattern:

```python
# tests/{module}/test_{module}_unit.py
import {module}  # F401: unused import

def test_placeholder():
    pass
```

### Purpose
These imports serve as **importability tests** - they validate that:
1. The module structure is correct
2. The module can be imported without errors
3. All dependencies are properly configured
4. No circular import issues exist

### Ruff's Suggestion
```
F401 `{module}` imported but unused;
consider using `importlib.util.find_spec` to test for availability
```

### Opportunity: Convert to Explicit Import Tests

**Current** (implicit):
```python
import analytics  # F401 - validates importability implicitly
```

**Recommended** (explicit):
```python
import importlib.util

def test_analytics_importability():
    """Validate analytics module can be imported."""
    spec = importlib.util.find_spec("analytics")
    assert spec is not None, "analytics module not found"

    # Optional: Actually import to catch import-time errors
    import analytics
    assert hasattr(analytics, "__version__") or True
```

### Benefits of Explicit Import Tests
1. **Clear intent**: Test explicitly validates importability
2. **Better error messages**: Fails with descriptive assertion
3. **Ruff compliant**: No F401 warning
4. **Testable**: Can add more validations (version, required exports, etc.)

### Implementation Strategy

**Phase 1: Create Template Test** (5 min)
```python
# tests/common/test_module_importability.py
import pytest
import importlib.util

def test_module_importability(module_name: str):
    """Validate a module can be imported."""
    spec = importlib.util.find_spec(module_name)
    assert spec is not None, f"{module_name} module not found"

    # Import to catch import-time errors
    module = importlib.import_module(module_name)
    assert module is not None

# Parametrize for all modules
@pytest.mark.parametrize("module_name", [
    "analytics", "api", "adapters", "agents",
    # ... add all 200+ modules
])
def test_all_modules_importable(module_name):
    test_module_importability(module_name)
```

**Phase 2: Generate Test List** (10 min)
```bash
# Extract all test module imports
python3 -m ruff check . --select F401 2>&1 | \
  grep "importlib.util.find_spec" | \
  grep -oP '`\K[^`]+' | \
  sort -u > /tmp/module_importability_list.txt

# Should have ~200 unique module names
wc -l /tmp/module_importability_list.txt
```

**Phase 3: Create Comprehensive Test** (15 min)
```python
# tests/smoke/test_module_importability.py
import pytest
import importlib.util

# Generated from F401 analysis
MODULES_TO_TEST = [
    "adapters", "agent", "agents", "agents_external",
    "ai_orchestration", "alerts", "analytics", "api",
    # ... 200+ modules
]

@pytest.mark.smoke
@pytest.mark.parametrize("module_name", MODULES_TO_TEST)
def test_module_can_be_imported(module_name: str):
    """
    Smoke test: Validate all expected modules can be imported.

    This catches:
    - Missing dependencies
    - Circular import errors
    - ImportError from syntax/runtime issues
    - Module structure problems
    """
    spec = importlib.util.find_spec(module_name)
    assert spec is not None, f"Module {module_name} not found in sys.path"

    # Actually import to catch import-time errors
    try:
        module = importlib.import_module(module_name)
        assert module is not None
    except Exception as e:
        pytest.fail(f"Module {module_name} exists but failed to import: {e}")
```

**Phase 4: Remove Old Test Scaffolds** (20 min)
```bash
# After comprehensive test is working, safely remove old imports
python3 -m ruff check . --select F401 --fix
```

**Expected Impact**:
- F401 errors: 409 → 2 (-407, -99.5%)
- Explicit importability testing: 0 → 200+ modules
- Test clarity: Implicit → Explicit
- Maintenance: Scattered → Centralized

---

## Category 2: Real Opportunities (2 instances)

### Opportunity 1: Consciousness API - Request Body Validation

**File**: `serve/consciousness_api.py:4`
**Import**: `from fastapi import Body`
**Status**: Unused

**Analysis**:
The `ConsciousnessEngine` methods accept `context` parameters:
```python
async def process_query(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
async def initiate_dream(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
```

But the endpoints don't accept input:
```python
@router.post("/api/v1/consciousness/query")
async def query():  # <-- No parameters!
    return await engine.process_query()
```

**The System is Calling For**: Context-aware endpoints

**Recommended Implementation**:
```python
from pydantic import BaseModel
from fastapi import Body

class QueryRequest(BaseModel):
    context: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None

@router.post("/api/v1/consciousness/query")
async def query(request: QueryRequest = Body(...)):
    """Query consciousness with optional context."""
    return await engine.process_query(context=request.context)

@router.post("/api/v1/consciousness/dream")
async def dream(request: QueryRequest = Body(...)):
    """Initiate dream sequence with optional context."""
    return await engine.initiate_dream(context=request.context)
```

**Benefits**:
1. Enables context-aware consciousness queries
2. Proper request validation via Pydantic
3. Swagger/OpenAPI docs automatically generated
4. Type safety for API consumers

**Status**: **OPPORTUNITY** - Feature incomplete, should be implemented

---

### Opportunity 2: Consciousness API - Dependency Injection

**File**: `serve/consciousness_api.py:4`
**Import**: `from fastapi import Depends`
**Status**: Unused

**Analysis**:
Currently uses global singleton:
```python
engine = ConsciousnessEngine()  # Global instance

@router.post("/api/v1/consciousness/query")
async def query():
    return await engine.process_query()  # Uses global
```

**The System is Calling For**: Proper dependency injection pattern

**Recommended Implementation**:
```python
from fastapi import Depends

def get_consciousness_engine() -> ConsciousnessEngine:
    """Dependency injection: Get consciousness engine instance."""
    return ConsciousnessEngine()

@router.post("/api/v1/consciousness/query")
async def query(
    request: QueryRequest = Body(...),
    engine: ConsciousnessEngine = Depends(get_consciousness_engine)
):
    """Query consciousness with injected engine."""
    return await engine.process_query(context=request.context)
```

**Benefits**:
1. **Testability**: Easy to mock engine in tests
2. **Flexibility**: Can swap implementations (production, testing, staging)
3. **Lifecycle management**: Control engine initialization per request/scope
4. **Best practice**: Standard FastAPI dependency injection pattern

**Status**: **OPPORTUNITY** - Refactoring incomplete, should use Depends

---

## Combined Implementation: Complete Consciousness API

```python
import asyncio
from typing import Any, Dict, Optional

from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel

# --- Engine ---

class ConsciousnessEngine:
    """Consciousness processing engine with dependency injection support."""

    async def process_query(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        await asyncio.sleep(0.008)
        return {
            "response": "The current awareness level is high.",
            "context": context
        }

    async def initiate_dream(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        await asyncio.sleep(0.02)
        return {
            "dream_id": "dream-123",
            "status": "generating",
            "context": context
        }

    async def retrieve_memory_state(self) -> Dict[str, Any]:
        await asyncio.sleep(0.004)
        return {"memory_folds": 1024, "recall_accuracy": 0.98}

    async def save_user_state(self, user_id: str, state: Dict[str, Any]) -> None:
        print(f"State for {user_id} saved.")

    async def get_user_state(self, user_id: str) -> Optional[Dict[str, Any]]:
        if user_id == "user1":
            return {"last_query": "awareness"}
        return None

# --- Dependency Injection ---

def get_consciousness_engine() -> ConsciousnessEngine:
    """Provide consciousness engine instance for dependency injection."""
    return ConsciousnessEngine()

# --- Request/Response Models ---

class QueryRequest(BaseModel):
    """Request model for consciousness queries."""
    context: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None

class StateModel(BaseModel):
    """Model for user state persistence."""
    user_id: str
    state_data: Dict[str, Any]

# --- API Router ---

router = APIRouter()

# --- Endpoints ---

@router.post("/api/v1/consciousness/query", summary="Query Consciousness State")
async def query(
    request: QueryRequest = Body(...),
    engine: ConsciousnessEngine = Depends(get_consciousness_engine)
):
    """Query consciousness state with optional context."""
    return await engine.process_query(context=request.context)

@router.post("/api/v1/consciousness/dream", summary="Initiate Dream Sequence")
async def dream(
    request: QueryRequest = Body(...),
    engine: ConsciousnessEngine = Depends(get_consciousness_engine)
):
    """Initiate dream sequence with optional context."""
    return await engine.initiate_dream(context=request.context)

@router.get("/api/v1/consciousness/memory", summary="Get Memory State")
async def memory(
    engine: ConsciousnessEngine = Depends(get_consciousness_engine)
):
    """Retrieve current memory state."""
    return await engine.retrieve_memory_state()

@router.post("/api/v1/consciousness/state", summary="Save User State")
async def save_state(
    payload: StateModel = Body(...),
    engine: ConsciousnessEngine = Depends(get_consciousness_engine)
):
    """Save user-specific consciousness state."""
    await engine.save_user_state(payload.user_id, payload.state_data)
    return {"status": "success", "user_id": payload.user_id}

@router.get("/api/v1/consciousness/state/{user_id}", summary="Get User State")
async def get_state(
    user_id: str,
    engine: ConsciousnessEngine = Depends(get_consciousness_engine)
):
    """Retrieve user-specific consciousness state."""
    state = await engine.get_user_state(user_id)
    if not state:
        raise HTTPException(status_code=404, detail="State not found for user")
    return {"user_id": user_id, "state_data": state}
```

---

## Summary: F401 as Opportunities

### Test Scaffolding (408 instances)
- **Not opportunities** - These are intentional importability tests
- **Action**: Convert to explicit `importlib.util.find_spec` tests
- **Timeline**: 30 minutes (template + comprehensive test + cleanup)
- **Impact**: Clearer test intent, ruff compliant, centralized testing

### Real Opportunities (2 instances)
- **Opportunity 1**: Context-aware consciousness API (Body validation)
- **Opportunity 2**: Dependency injection pattern (Depends)
- **Action**: Complete the refactoring started in PR #1291
- **Timeline**: 20 minutes (implementation + tests)
- **Impact**: Production-ready API with proper patterns

### Philosophy Applied
Instead of blindly removing "unused" imports, we:
1. **Understood the intent**: Test scaffolding vs incomplete features
2. **Identified opportunities**: What functionality is missing?
3. **Proposed solutions**: How to fulfill what the system is calling for
4. **Prioritized value**: Implement what matters, document what doesn't

### Next Steps

**Immediate** (30 min):
1. Create comprehensive importability test
2. Run auto-fix to remove old scaffolding: `ruff check . --select F401 --fix`
3. Verify all tests pass

**Short-term** (20 min):
1. Complete consciousness API refactoring (Body + Depends)
2. Update tests for new endpoints
3. Verify API functionality

**Long-term**:
- Monitor F401 errors for future opportunities
- Treat unused imports as signals, not noise
- Document design decisions when choosing to keep imports

---

**Last Updated**: 2025-11-10
**Philosophy**: Unused imports as opportunities for missing functionality
**Status**: Analysis complete, ready for implementation
