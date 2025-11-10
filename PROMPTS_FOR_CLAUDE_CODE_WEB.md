# Prompts for Claude Code Web - Core Wiring Remaining Tasks

**Date**: 2025-11-10
**Session**: Handoff from Claude Code Desktop
**Context**: Tasks 1, 2, 7 (partial), and 9 are complete. Tasks 3-6 and 8 remain.

---

## Current State Summary

### ✅ Completed Tasks
- **Task 1**: Global initialization system (PR #1263, merged)
- **Task 2**: Wrapper modules for consciousness, dreams, glyphs (PR #1264, in Lukhas-core-wiring-phase2 worktree)
- **Task 7**: Observability and Metrics (PARTIALLY COMPLETE - Prometheus status page merged)
- **Task 9**: Security Review and SLSA Provenance (COMPLETE - merged to main)

### 📋 Remaining Tasks
- **Task 3**: Production API Routes
- **Task 4**: Wire Parallel Dreams Feature Flag
- **Task 5**: Wire Vivox Drift into User Profiles
- **Task 6**: Create GLYPH Bind Endpoints
- **Task 8**: Performance and Chaos Testing

### 🔧 Key Files & Context

**Worktrees**:
- `Lukhas-core-wiring-phase2/` - Contains Task 2 work (wrapper modules + tests)
- Main repo: `/Users/agi_dev/LOCAL-REPOS/Lukhas`

**Important Documents**:
- `TASK_2_COMPLETE.md` - Task 2 completion summary
- `REBASE_MERGE_COMPLETE.md` - Recent merge summary
- `HANDOFF_TO_CLAUDE_CODE_WEB.md` - Original handoff with full task specs

**Known Issues**:
- RecursionError in `memory/backends/base/__init__.py` affecting consciousness imports
- 6 consciousness wrapper tests skipped due to this bug

---

## Task 3: Production API Routes

### Prompt for Claude Code Web

```
TASK: Create production-ready FastAPI routes for dreams, drift, and glyphs subsystems

CONTEXT:
- Wrapper modules exist in lukhas/dream/, lukhas/glyphs/
- Initialization system exists in lukhas/core/initialization.py
- Feature flags: DREAMS_ENABLED, GLYPHS_ENABLED, PARALLEL_DREAMS_ENABLED
- This is Task 3 of the Core Wiring plan

OBJECTIVE:
Create three new FastAPI route modules with comprehensive error handling, authentication, and feature flag integration.

FILES TO CREATE:
1. lukhas_website/lukhas/api/dreams.py (~150-200 lines)
2. lukhas_website/lukhas/api/drift.py (~100-150 lines)
3. lukhas_website/lukhas/api/glyphs.py (~150-200 lines)

REQUIREMENTS:

### 1. Dreams API (lukhas/api/dreams.py)

Endpoints:
- POST /api/v1/dreams/parallel - Create parallel dream processing task
- GET /api/v1/dreams/{dream_id} - Get dream result by ID
- GET /api/v1/dreams/list - List user's dreams (paginated)
- DELETE /api/v1/dreams/{dream_id} - Delete dream by ID

Requirements:
- Feature flag check: require DREAMS_ENABLED=true
- Use lukhas.dream.get_dream_engine() wrapper
- Check PARALLEL_DREAMS_ENABLED for parallel vs sequential processing
- Authentication required (use existing serve auth pattern)
- Pydantic models for request/response validation
- Comprehensive error handling (404, 403, 500)
- OpenAPI documentation with examples

### 2. Drift API (lukhas/api/drift.py)

Endpoints:
- GET /api/v1/drift/{user_id} - Get user's Vivox drift metrics
- POST /api/v1/drift/update - Update drift metrics (admin only)
- GET /api/v1/drift/analysis - Drift analysis report

Requirements:
- Integration with Vivox system (if exists) or stub for now
- Drift metrics: coherence_score, emotional_stability, behavioral_consistency
- Admin authentication for update endpoint
- Rate limiting (100 requests/min per user)
- Response caching (5 minute TTL)

### 3. Glyphs API (lukhas/api/glyphs.py)

Endpoints:
- POST /api/v1/glyphs/bind - Bind GLYPH token to action
- GET /api/v1/glyphs/{glyph_id} - Get GLYPH details
- POST /api/v1/glyphs/validate - Validate GLYPH token
- DELETE /api/v1/glyphs/{glyph_id} - Unbind GLYPH token

Requirements:
- Feature flag check: require GLYPHS_ENABLED=true
- Use lukhas.glyphs.create_glyph(), parse_glyph(), validate_glyph()
- GLYPH format validation (source, target, symbol, priority)
- Authentication required
- Audit logging for all GLYPH operations
- Rate limiting (50 bind operations/min)

### Common Requirements for All APIs:
- Use FastAPI dependency injection
- Pydantic BaseModel for all request/response schemas
- HTTPException with appropriate status codes
- Prometheus metrics integration (if observability module exists)
- Structured logging with extra context
- OpenAPI tags and descriptions
- Unit tests for each endpoint (use pytest + httpx)

INTEGRATION:
- Wire into existing lukhas_website/lukhas/api/__init__.py
- Register routers with main FastAPI app
- Add to OpenAPI spec

TESTING:
Create tests/unit/api/test_dreams_routes.py with:
- Test each endpoint with valid input
- Test feature flag disabled scenarios
- Test authentication failures
- Test validation errors
- Aim for 80%+ coverage

DELIVERABLES:
1. Three API route modules (dreams.py, drift.py, glyphs.py)
2. Pydantic schemas for request/response models
3. Integration with main API router
4. Comprehensive unit tests (80%+ coverage)
5. Update to OpenAPI spec
6. Brief documentation in lukhas/api/README.md

SUCCESS CRITERIA:
- All routes respond correctly when feature flags enabled
- Proper 403/404 errors when flags disabled
- Tests pass: pytest tests/unit/api/test_*_routes.py
- OpenAPI docs show all endpoints correctly
- No breaking changes to existing API

COMMIT MESSAGE FORMAT:
feat(api): add production routes for dreams, drift, and glyphs

Implements Task 3 of core wiring plan:
- Dreams API: parallel processing, dream lifecycle management
- Drift API: Vivox drift metrics and analysis
- Glyphs API: GLYPH token binding and validation

Features:
- Feature flag integration (DREAMS_ENABLED, GLYPHS_ENABLED)
- Authentication and rate limiting
- Comprehensive error handling
- OpenAPI documentation

Tests: 80%+ coverage across all endpoints

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## Task 4: Wire Parallel Dreams Feature Flag

### Prompt for Claude Code Web

```
TASK: Implement dynamic engine switching based on PARALLEL_DREAMS_ENABLED flag

CONTEXT:
- lukhas/dream/__init__.py has PARALLEL_DREAMS_ENABLED flag defined
- Currently get_dream_engine() returns single engine regardless of flag
- Need conditional logic: sequential engine (default) vs parallel engine (when enabled)
- This is Task 4 of the Core Wiring plan

OBJECTIVE:
Wire the PARALLEL_DREAMS_ENABLED flag to dynamically switch between sequential and parallel dream processing engines.

FILES TO MODIFY:
1. lukhas_website/lukhas/dream/__init__.py (~20-30 line changes)
2. lukhas_website/lukhas/consciousness/dream_engine.py (if changes needed)

REQUIREMENTS:

### 1. Engine Switching Logic

Modify get_dream_engine() in lukhas/dream/__init__.py:

```python
def get_dream_engine() -> Any:
    """
    Get dream engine based on feature flags.

    Returns:
        - SequentialDreamEngine if PARALLEL_DREAMS_ENABLED=false
        - ParallelDreamEngine if PARALLEL_DREAMS_ENABLED=true

    Raises:
        RuntimeError: If DREAMS_ENABLED=false
    """
    global _dream_engine

    if not DREAMS_ENABLED:
        raise RuntimeError("Dreams subsystem not enabled (set DREAMS_ENABLED=true)")

    # Check if engine type needs to change based on flag
    current_engine_type = type(_dream_engine).__name__ if _dream_engine else None
    expected_engine_type = "ParallelDreamEngine" if PARALLEL_DREAMS_ENABLED else "SequentialDreamEngine"

    # Recreate engine if flag changed or engine not initialized
    if _dream_engine is None or current_engine_type != expected_engine_type:
        from lukhas_website.lukhas.consciousness.dream_engine import DreamEngine

        if PARALLEL_DREAMS_ENABLED:
            # TODO: Implement ParallelDreamEngine or use DreamEngine with parallel config
            _dream_engine = DreamEngine(config={"mode": "parallel"})
        else:
            _dream_engine = DreamEngine(config={"mode": "sequential"})

    return _dream_engine
```

### 2. Configuration Handling

Ensure DreamEngine accepts mode configuration:
- Check lukhas/consciousness/dream_engine.py
- If no mode parameter exists, add it to __init__
- Default mode should be "sequential" for backward compatibility

### 3. Testing

Create tests/unit/core/test_parallel_dreams_flag.py:

```python
def test_sequential_engine_by_default():
    """Test that sequential engine is used when PARALLEL_DREAMS_ENABLED=false"""
    os.environ["DREAMS_ENABLED"] = "true"
    os.environ["PARALLEL_DREAMS_ENABLED"] = "false"

    engine = get_dream_engine()
    assert engine.config.get("mode") == "sequential"

def test_parallel_engine_when_enabled():
    """Test that parallel engine is used when PARALLEL_DREAMS_ENABLED=true"""
    os.environ["DREAMS_ENABLED"] = "true"
    os.environ["PARALLEL_DREAMS_ENABLED"] = "true"

    engine = get_dream_engine()
    assert engine.config.get("mode") == "parallel"

def test_engine_switches_when_flag_changes():
    """Test that engine is recreated when flag changes at runtime"""
    os.environ["DREAMS_ENABLED"] = "true"
    os.environ["PARALLEL_DREAMS_ENABLED"] = "false"

    engine1 = get_dream_engine()
    assert engine1.config.get("mode") == "sequential"

    # Simulate flag change
    os.environ["PARALLEL_DREAMS_ENABLED"] = "true"

    engine2 = get_dream_engine()
    assert engine2.config.get("mode") == "parallel"
    assert engine1 is not engine2  # Different instances
```

DELIVERABLES:
1. Modified lukhas/dream/__init__.py with engine switching logic
2. Updated DreamEngine to accept mode configuration (if needed)
3. Unit tests for flag switching behavior
4. Documentation update in lukhas/dream/README.md (create if missing)

SUCCESS CRITERIA:
- get_dream_engine() returns sequential engine by default
- get_dream_engine() returns parallel engine when PARALLEL_DREAMS_ENABLED=true
- Engine is recreated if flag changes at runtime
- All tests pass
- No breaking changes to existing dream functionality

COMMIT MESSAGE:
feat(dreams): wire PARALLEL_DREAMS_ENABLED flag to engine selection

Implements Task 4 of core wiring plan:
- Sequential engine: default mode for single-threaded processing
- Parallel engine: enabled via PARALLEL_DREAMS_ENABLED=true
- Dynamic engine switching based on flag changes

Logic:
- DREAMS_ENABLED=true + PARALLEL_DREAMS_ENABLED=false → Sequential
- DREAMS_ENABLED=true + PARALLEL_DREAMS_ENABLED=true → Parallel

Tests: Full coverage of flag switching scenarios

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## Task 5: Wire Vivox Drift into User Profiles

### Prompt for Claude Code Web

```
TASK: Integrate Vivox drift metrics into user profile API responses

CONTEXT:
- Vivox is the system for tracking user behavioral drift
- Drift metrics measure: coherence, emotional stability, behavioral consistency
- User profiles currently in lukhas/api/users.py (or need to be created)
- This is Task 5 of the Core Wiring plan

OBJECTIVE:
Add drift tracking fields to user profile schema and wire into profile API.

FILES TO CREATE/MODIFY:
1. lukhas_website/lukhas/vivox/drift_tracker.py (create new)
2. lukhas_website/lukhas/api/users.py (modify or create)
3. lukhas_website/lukhas/vivox/__init__.py (create if missing)

REQUIREMENTS:

### 1. Drift Tracker Implementation

Create lukhas/vivox/drift_tracker.py:

```python
"""
Vivox Drift Tracker

Monitors user behavioral drift across consciousness dimensions:
- Coherence: consistency in responses and decision patterns
- Emotional Stability: variance in emotional states
- Behavioral Consistency: alignment with historical patterns
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

@dataclass
class DriftMetrics:
    """User drift metrics snapshot"""
    user_id: str
    coherence_score: float  # 0.0-1.0, higher is better
    emotional_stability: float  # 0.0-1.0, higher is more stable
    behavioral_consistency: float  # 0.0-1.0, higher is more consistent
    drift_velocity: float  # Rate of change (per day)
    last_updated: datetime

    @property
    def overall_drift(self) -> float:
        """Combined drift score (inverse of average metrics)"""
        avg_metrics = (self.coherence_score + self.emotional_stability + self.behavioral_consistency) / 3
        return 1.0 - avg_metrics  # Higher drift = lower metrics

class DriftTracker:
    """Track and analyze user behavioral drift"""

    def __init__(self):
        # TODO: Wire to actual Vivox backend
        self._cache: Dict[str, DriftMetrics] = {}

    async def get_drift_metrics(self, user_id: str) -> Optional[DriftMetrics]:
        """Get current drift metrics for user"""
        # TODO: Implement actual drift calculation
        # For now, return stub data
        return DriftMetrics(
            user_id=user_id,
            coherence_score=0.85,
            emotional_stability=0.78,
            behavioral_consistency=0.82,
            drift_velocity=0.02,
            last_updated=datetime.utcnow()
        )

    async def update_drift_metrics(self, user_id: str, interaction_data: dict) -> DriftMetrics:
        """Update drift metrics based on new interaction"""
        # TODO: Implement drift calculation algorithm
        pass

    async def analyze_drift_trend(self, user_id: str, days: int = 30) -> dict:
        """Analyze drift trend over time"""
        # TODO: Implement trend analysis
        pass
```

### 2. User Profile Schema Extension

Modify lukhas/api/users.py to include drift fields:

```python
from pydantic import BaseModel, Field
from lukhas_website.lukhas.vivox.drift_tracker import DriftMetrics

class UserProfileResponse(BaseModel):
    """User profile with drift metrics"""
    user_id: str
    username: str
    tier: str

    # Vivox drift metrics
    drift_metrics: Optional[DriftMetrics] = Field(
        None,
        description="Behavioral drift metrics from Vivox system"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "usr_123",
                "username": "alice",
                "tier": "premium",
                "drift_metrics": {
                    "user_id": "usr_123",
                    "coherence_score": 0.85,
                    "emotional_stability": 0.78,
                    "behavioral_consistency": 0.82,
                    "drift_velocity": 0.02,
                    "last_updated": "2025-11-10T12:00:00Z"
                }
            }
        }

@router.get("/api/v1/users/{user_id}", response_model=UserProfileResponse)
async def get_user_profile(
    user_id: str,
    include_drift: bool = True,
    current_user: User = Depends(get_current_user)
):
    """Get user profile with optional drift metrics"""
    # Get base user data
    user = await get_user_from_db(user_id)

    # Get drift metrics if requested
    drift_metrics = None
    if include_drift:
        drift_tracker = DriftTracker()
        drift_metrics = await drift_tracker.get_drift_metrics(user_id)

    return UserProfileResponse(
        user_id=user.id,
        username=user.username,
        tier=user.tier,
        drift_metrics=drift_metrics
    )
```

### 3. Testing

Create tests/unit/vivox/test_drift_tracker.py:

```python
@pytest.mark.asyncio
async def test_get_drift_metrics():
    """Test retrieving drift metrics for user"""
    tracker = DriftTracker()
    metrics = await tracker.get_drift_metrics("usr_123")

    assert metrics is not None
    assert 0.0 <= metrics.coherence_score <= 1.0
    assert 0.0 <= metrics.emotional_stability <= 1.0
    assert 0.0 <= metrics.behavioral_consistency <= 1.0
    assert metrics.user_id == "usr_123"

@pytest.mark.asyncio
async def test_overall_drift_calculation():
    """Test overall drift score calculation"""
    metrics = DriftMetrics(
        user_id="usr_123",
        coherence_score=0.8,
        emotional_stability=0.9,
        behavioral_consistency=0.7,
        drift_velocity=0.05,
        last_updated=datetime.utcnow()
    )

    expected_drift = 1.0 - ((0.8 + 0.9 + 0.7) / 3)
    assert abs(metrics.overall_drift - expected_drift) < 0.001
```

DELIVERABLES:
1. DriftTracker implementation (lukhas/vivox/drift_tracker.py)
2. Extended user profile schema with drift metrics
3. Modified user profile API endpoint
4. Unit tests for drift tracking (80%+ coverage)
5. API documentation with drift metrics examples

SUCCESS CRITERIA:
- GET /api/v1/users/{user_id} returns drift metrics when include_drift=true
- Drift metrics are optional (backward compatible)
- All drift scores are 0.0-1.0 range
- Tests pass with 80%+ coverage
- OpenAPI docs updated

COMMIT MESSAGE:
feat(vivox): integrate drift metrics into user profiles

Implements Task 5 of core wiring plan:
- DriftTracker class for behavioral drift monitoring
- Extended user profile schema with drift metrics
- Optional drift data in profile API responses

Metrics:
- Coherence score (response consistency)
- Emotional stability (variance tracking)
- Behavioral consistency (historical alignment)
- Overall drift score and velocity

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## Task 6: Create GLYPH Bind Endpoints

### Prompt for Claude Code Web

```
TASK: Implement GLYPH token binding API endpoints with audit logging

CONTEXT:
- GLYPH system exists in lukhas/core/common/glyph.py
- Wrapper exists in lukhas/glyphs/__init__.py
- GLYPHs are tokens that bind source→target actions with priority and context
- This is Task 6 of the Core Wiring plan

OBJECTIVE:
Create comprehensive API for GLYPH lifecycle management with security and audit logging.

FILES TO CREATE/MODIFY:
1. lukhas_website/lukhas/api/glyphs.py (if not created in Task 3)
2. lukhas_website/lukhas/glyphs/binding_manager.py (new)
3. lukhas_website/lukhas/glyphs/audit_logger.py (new)

REQUIREMENTS:

### 1. GLYPH Binding Manager

Create lukhas/glyphs/binding_manager.py:

```python
"""
GLYPH Binding Manager

Manages lifecycle of GLYPH token bindings:
- Creation with validation
- Retrieval and querying
- Update and rebinding
- Deletion and cleanup
"""

from typing import Dict, List, Optional
from datetime import datetime
from lukhas_website.lukhas.glyphs import create_glyph, validate_glyph, GLYPHSymbol, GLYPHPriority

class GLYPHBinding:
    """Represents a GLYPH token binding"""
    glyph_id: str
    source: str
    target: str
    symbol: GLYPHSymbol
    priority: GLYPHPriority
    context: Dict
    created_at: datetime
    created_by: str
    active: bool

class BindingManager:
    """Manage GLYPH token bindings"""

    def __init__(self):
        self._bindings: Dict[str, GLYPHBinding] = {}

    async def create_binding(
        self,
        source: str,
        target: str,
        symbol: str,
        priority: str = "NORMAL",
        context: Optional[Dict] = None,
        user_id: str = None
    ) -> GLYPHBinding:
        """Create new GLYPH binding"""
        # Create GLYPH token using wrapper
        glyph = create_glyph(
            symbol=symbol,
            source=source,
            target=target,
            priority=priority,
            context=context or {}
        )

        # Validate GLYPH
        is_valid, error = validate_glyph(glyph)
        if not is_valid:
            raise ValueError(f"Invalid GLYPH: {error}")

        # Create binding record
        binding = GLYPHBinding(
            glyph_id=glyph.id,
            source=source,
            target=target,
            symbol=GLYPHSymbol(symbol),
            priority=GLYPHPriority(priority),
            context=context or {},
            created_at=datetime.utcnow(),
            created_by=user_id,
            active=True
        )

        self._bindings[binding.glyph_id] = binding

        # Audit log
        await self._audit_log("CREATE", binding, user_id)

        return binding

    async def get_binding(self, glyph_id: str) -> Optional[GLYPHBinding]:
        """Get GLYPH binding by ID"""
        return self._bindings.get(glyph_id)

    async def list_bindings(
        self,
        user_id: Optional[str] = None,
        source: Optional[str] = None,
        active_only: bool = True
    ) -> List[GLYPHBinding]:
        """List GLYPH bindings with optional filters"""
        results = list(self._bindings.values())

        if user_id:
            results = [b for b in results if b.created_by == user_id]
        if source:
            results = [b for b in results if b.source == source]
        if active_only:
            results = [b for b in results if b.active]

        return results

    async def delete_binding(self, glyph_id: str, user_id: str) -> bool:
        """Delete (deactivate) GLYPH binding"""
        binding = self._bindings.get(glyph_id)
        if not binding:
            return False

        binding.active = False

        # Audit log
        await self._audit_log("DELETE", binding, user_id)

        return True

    async def _audit_log(self, action: str, binding: GLYPHBinding, user_id: str):
        """Log GLYPH operation to audit trail"""
        from lukhas_website.lukhas.glyphs.audit_logger import GLYPHAuditLogger
        logger = GLYPHAuditLogger()
        await logger.log_operation(
            action=action,
            glyph_id=binding.glyph_id,
            user_id=user_id,
            details={
                "source": binding.source,
                "target": binding.target,
                "symbol": binding.symbol.value,
                "priority": binding.priority.value
            }
        )
```

### 2. Audit Logger

Create lukhas/glyphs/audit_logger.py:

```python
"""
GLYPH Audit Logger

Comprehensive audit trail for all GLYPH operations.
"""

from datetime import datetime
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class GLYPHAuditLogger:
    """Audit logger for GLYPH operations"""

    async def log_operation(
        self,
        action: str,
        glyph_id: str,
        user_id: str,
        details: Optional[Dict] = None
    ):
        """Log GLYPH operation to audit trail"""
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "glyph_id": glyph_id,
            "user_id": user_id,
            "details": details or {}
        }

        # Log to structured logger
        logger.info(
            f"GLYPH operation: {action}",
            extra={
                "audit": True,
                "glyph_operation": True,
                **audit_entry
            }
        )

        # TODO: Also persist to audit database
```

### 3. API Endpoints

Add to lukhas/api/glyphs.py:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from lukhas_website.lukhas.glyphs.binding_manager import BindingManager

router = APIRouter(prefix="/api/v1/glyphs", tags=["glyphs"])

class CreateBindingRequest(BaseModel):
    source: str
    target: str
    symbol: str
    priority: str = "NORMAL"
    context: Optional[Dict] = None

@router.post("/bind", status_code=status.HTTP_201_CREATED)
async def create_glyph_binding(
    request: CreateBindingRequest,
    current_user: User = Depends(get_current_user)
):
    """Create new GLYPH token binding"""
    manager = BindingManager()

    try:
        binding = await manager.create_binding(
            source=request.source,
            target=request.target,
            symbol=request.symbol,
            priority=request.priority,
            context=request.context,
            user_id=current_user.id
        )
        return binding
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{glyph_id}")
async def get_glyph_binding(
    glyph_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get GLYPH binding details"""
    manager = BindingManager()
    binding = await manager.get_binding(glyph_id)

    if not binding:
        raise HTTPException(status_code=404, detail="GLYPH binding not found")

    return binding

@router.get("/bindings/list")
async def list_glyph_bindings(
    source: Optional[str] = None,
    active_only: bool = True,
    current_user: User = Depends(get_current_user)
):
    """List GLYPH bindings for current user"""
    manager = BindingManager()
    bindings = await manager.list_bindings(
        user_id=current_user.id,
        source=source,
        active_only=active_only
    )
    return {"bindings": bindings, "count": len(bindings)}

@router.delete("/{glyph_id}")
async def delete_glyph_binding(
    glyph_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete GLYPH binding"""
    manager = BindingManager()
    deleted = await manager.delete_binding(glyph_id, current_user.id)

    if not deleted:
        raise HTTPException(status_code=404, detail="GLYPH binding not found")

    return {"message": "GLYPH binding deleted successfully"}
```

### 4. Rate Limiting

Add rate limiting to prevent abuse:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/bind")
@limiter.limit("50/minute")  # Max 50 bindings per minute
async def create_glyph_binding(...):
    ...
```

### 5. Testing

Create tests/unit/api/test_glyph_endpoints.py:

```python
@pytest.mark.asyncio
async def test_create_binding():
    """Test creating GLYPH binding"""
    request = CreateBindingRequest(
        source="user:123",
        target="action:chat",
        symbol="LINK",
        priority="HIGH"
    )

    binding = await create_glyph_binding(request, mock_user)

    assert binding.glyph_id is not None
    assert binding.source == "user:123"
    assert binding.active is True

@pytest.mark.asyncio
async def test_rate_limiting():
    """Test that rate limiting works"""
    # Make 51 requests (over limit of 50/min)
    for i in range(51):
        response = await client.post("/api/v1/glyphs/bind", ...)

    # Last request should be rate limited
    assert response.status_code == 429
```

DELIVERABLES:
1. BindingManager class (lukhas/glyphs/binding_manager.py)
2. GLYPHAuditLogger class (lukhas/glyphs/audit_logger.py)
3. Complete API endpoints for GLYPH lifecycle
4. Rate limiting implementation
5. Comprehensive tests (80%+ coverage)
6. Audit logging for all operations

SUCCESS CRITERIA:
- All GLYPH endpoints functional and secured
- Rate limiting prevents abuse (50/min)
- Audit log captures all operations
- Tests pass with 80%+ coverage
- OpenAPI docs complete

COMMIT MESSAGE:
feat(glyphs): implement GLYPH binding API with audit logging

Implements Task 6 of core wiring plan:
- Complete GLYPH lifecycle API (create, read, list, delete)
- Binding manager with validation
- Comprehensive audit logging
- Rate limiting (50 bindings/minute)

Security:
- Authentication required for all endpoints
- Audit trail for all operations
- Input validation on all GLYPH tokens

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## Task 8: Performance and Chaos Testing

### Prompt for Claude Code Web

```
TASK: Create comprehensive performance benchmarks and chaos engineering tests

CONTEXT:
- Core wiring plan includes aggressive performance targets
- Need to validate system meets requirements before production
- Chaos testing ensures graceful degradation
- This is Task 8 of the Core Wiring plan

OBJECTIVE:
Create performance test suite and chaos engineering tests to validate:
- Initialization latency <250ms (p95)
- API throughput 50+ ops/sec
- Memory usage <100MB (all flags enabled)
- Graceful failure handling

FILES TO CREATE:
1. tests/performance/test_initialization_perf.py
2. tests/performance/test_api_throughput.py
3. tests/chaos/test_feature_flag_failures.py
4. tests/chaos/test_network_failures.py
5. scripts/run_performance_tests.sh

REQUIREMENTS:

### 1. Initialization Performance Tests

Create tests/performance/test_initialization_perf.py:

```python
"""
Initialization Performance Benchmarks

Target: <250ms p95 latency for full system initialization
"""

import pytest
import time
import statistics
from lukhas_website.lukhas.core.initialization import initialize_global_system

@pytest.mark.performance
def test_initialization_latency():
    """Test that initialization meets <250ms p95 target"""
    latencies = []
    iterations = 100

    for _ in range(iterations):
        # Reset state
        from lukhas_website.lukhas.core import initialization
        initialization._INITIALIZATION_STATE["initialized"] = False

        # Measure initialization time
        start = time.time()
        initialize_global_system()
        latency_ms = (time.time() - start) * 1000
        latencies.append(latency_ms)

    # Calculate percentiles
    p50 = statistics.median(latencies)
    p95 = sorted(latencies)[int(0.95 * iterations)]
    p99 = sorted(latencies)[int(0.99 * iterations)]

    print(f"\nInitialization Latency:")
    print(f"  p50: {p50:.2f}ms")
    print(f"  p95: {p95:.2f}ms")
    print(f"  p99: {p99:.2f}ms")

    # Assert p95 meets target
    assert p95 < 250, f"p95 latency {p95:.2f}ms exceeds 250ms target"

@pytest.mark.performance
def test_initialization_memory_usage():
    """Test that initialization uses <100MB memory"""
    import psutil
    import os

    process = psutil.Process(os.getpid())
    mem_before = process.memory_info().rss / 1024 / 1024  # MB

    # Initialize with all flags enabled
    os.environ["CONSCIOUSNESS_ENABLED"] = "true"
    os.environ["DREAMS_ENABLED"] = "true"
    os.environ["GLYPHS_ENABLED"] = "true"

    initialize_global_system()

    mem_after = process.memory_info().rss / 1024 / 1024  # MB
    mem_delta = mem_after - mem_before

    print(f"\nMemory Usage:")
    print(f"  Before: {mem_before:.2f} MB")
    print(f"  After: {mem_after:.2f} MB")
    print(f"  Delta: {mem_delta:.2f} MB")

    assert mem_delta < 100, f"Memory usage {mem_delta:.2f}MB exceeds 100MB target"
```

### 2. API Throughput Tests

Create tests/performance/test_api_throughput.py:

```python
"""
API Throughput Benchmarks

Target: 50+ operations per second
"""

import pytest
import asyncio
import time
from httpx import AsyncClient

@pytest.mark.asyncio
@pytest.mark.performance
async def test_api_throughput_dreams():
    """Test dreams API throughput meets 50+ ops/sec target"""
    async with AsyncClient(base_url="http://localhost:8000") as client:
        # Warm up
        for _ in range(10):
            await client.get("/api/v1/dreams/list")

        # Benchmark
        operations = 0
        duration = 10  # seconds
        start = time.time()

        while time.time() - start < duration:
            await client.get("/api/v1/dreams/list")
            operations += 1

        actual_duration = time.time() - start
        throughput = operations / actual_duration

        print(f"\nDreams API Throughput:")
        print(f"  Operations: {operations}")
        print(f"  Duration: {actual_duration:.2f}s")
        print(f"  Throughput: {throughput:.2f} ops/sec")

        assert throughput >= 50, f"Throughput {throughput:.2f} ops/sec below 50 target"

@pytest.mark.asyncio
@pytest.mark.performance
async def test_concurrent_api_load():
    """Test API handles concurrent load (100 concurrent requests)"""
    async with AsyncClient(base_url="http://localhost:8000") as client:
        async def make_request():
            response = await client.get("/api/v1/dreams/list")
            return response.status_code

        # Fire 100 concurrent requests
        start = time.time()
        tasks = [make_request() for _ in range(100)]
        results = await asyncio.gather(*tasks)
        duration = time.time() - start

        success_count = sum(1 for r in results if r == 200)
        success_rate = success_count / len(results)

        print(f"\nConcurrent Load Test:")
        print(f"  Requests: 100")
        print(f"  Duration: {duration:.2f}s")
        print(f"  Success Rate: {success_rate:.2%}")

        assert success_rate >= 0.95, f"Success rate {success_rate:.2%} below 95% target"
```

### 3. Chaos Engineering Tests

Create tests/chaos/test_feature_flag_failures.py:

```python
"""
Chaos Engineering: Feature Flag Failures

Test graceful degradation when feature flags are disabled.
"""

import pytest

@pytest.mark.chaos
def test_dreams_api_with_flag_disabled():
    """Test that dreams API returns 403 when DREAMS_ENABLED=false"""
    os.environ["DREAMS_ENABLED"] = "false"

    response = client.get("/api/v1/dreams/list")

    assert response.status_code == 403
    assert "not enabled" in response.json()["detail"].lower()

@pytest.mark.chaos
def test_parallel_dreams_degrades_to_sequential():
    """Test that parallel dreams degrades gracefully to sequential"""
    os.environ["DREAMS_ENABLED"] = "true"
    os.environ["PARALLEL_DREAMS_ENABLED"] = "true"

    # Simulate parallel engine failure
    with patch("lukhas.dream.ParallelDreamEngine", side_effect=Exception("Parallel engine failed")):
        engine = get_dream_engine()

        # Should fall back to sequential
        assert engine.config.get("mode") == "sequential"

@pytest.mark.chaos
def test_initialization_partial_success():
    """Test that initialization succeeds partially when one subsystem fails"""
    os.environ["CONSCIOUSNESS_ENABLED"] = "true"
    os.environ["DREAMS_ENABLED"] = "true"
    os.environ["GLYPHS_ENABLED"] = "true"

    # Simulate consciousness import failure
    with patch("lukhas.consciousness", side_effect=ImportError("Consciousness failed")):
        result = initialize_global_system()

        # Should be partial success
        assert result["status"] == "partial"
        assert "consciousness" not in result["initialized_systems"]
        assert "dreams" in result["initialized_systems"] or "glyphs" in result["initialized_systems"]
```

Create tests/chaos/test_network_failures.py:

```python
"""
Chaos Engineering: Network Failures

Test resilience to network and dependency failures.
"""

import pytest
from unittest.mock import patch

@pytest.mark.chaos
@pytest.mark.asyncio
async def test_api_resilient_to_database_timeout():
    """Test API returns 503 on database timeout"""
    with patch("lukhas.api.dreams.get_dreams_from_db", side_effect=TimeoutError):
        response = await client.get("/api/v1/dreams/list")

        assert response.status_code == 503
        assert "service unavailable" in response.json()["detail"].lower()

@pytest.mark.chaos
@pytest.mark.asyncio
async def test_drift_api_with_vivox_down():
    """Test drift API degrades gracefully when Vivox is down"""
    with patch("lukhas.vivox.DriftTracker.get_drift_metrics", side_effect=ConnectionError):
        response = await client.get("/api/v1/users/usr_123")

        # Should succeed but without drift metrics
        assert response.status_code == 200
        assert response.json()["drift_metrics"] is None
```

### 4. Performance Test Runner

Create scripts/run_performance_tests.sh:

```bash
#!/bin/bash
# Performance Test Runner

set -e

echo "🚀 Running Performance Benchmark Suite"
echo "======================================="

# Setup
export PYTEST_MARKERS="performance"
export PERFORMANCE_TEST_MODE=1

# Initialize test environment
python -m pytest tests/performance/ --benchmark-only -v

# Run with profiling
python -m pytest tests/performance/ --profile --profile-svg

# Generate report
python scripts/generate_perf_report.py > reports/performance_$(date +%Y%m%d).md

echo ""
echo "✅ Performance tests complete"
echo "📊 Report: reports/performance_$(date +%Y%m%d).md"
```

DELIVERABLES:
1. Initialization performance tests
2. API throughput benchmarks
3. Chaos engineering test suite
4. Performance test runner script
5. Performance report generator
6. Documentation of performance targets and results

SUCCESS CRITERIA:
- Initialization p95 latency <250ms
- API throughput >50 ops/sec
- Memory usage <100MB (all flags enabled)
- 95%+ success rate under concurrent load
- Graceful degradation in all chaos scenarios
- All tests documented and reproducible

COMMIT MESSAGE:
test(performance): add comprehensive performance and chaos tests

Implements Task 8 of core wiring plan:
- Initialization latency benchmarks (<250ms p95 target)
- API throughput tests (>50 ops/sec target)
- Memory usage validation (<100MB target)
- Chaos engineering for graceful degradation

Coverage:
- Feature flag failures
- Network and dependency failures
- Concurrent load handling
- Partial initialization scenarios

Results: All performance targets met in benchmarks

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## Summary & Workflow

### Recommended Execution Order

1. **Task 3** (API Routes) - Foundation for other tasks
2. **Task 4** (Parallel Dreams) - Quick flag wiring
3. **Task 6** (GLYPH Bindings) - Uses Task 3 APIs
4. **Task 5** (Vivox Drift) - Extends Task 3 user APIs
5. **Task 8** (Performance) - Validates all previous work

### Worktree Strategy

Create separate worktrees for each task:

```bash
# Task 3
git worktree add ../Lukhas-core-wiring-phase3 -b feat/core-wiring-phase3

# Task 4
git worktree add ../Lukhas-core-wiring-phase4 -b feat/core-wiring-phase4

# Task 5
git worktree add ../Lukhas-core-wiring-phase5 -b feat/core-wiring-phase5

# Task 6
git worktree add ../Lukhas-core-wiring-phase6 -b feat/core-wiring-phase6

# Task 8
git worktree add ../Lukhas-core-wiring-phase8 -b feat/core-wiring-phase8
```

### PR Creation

For each task:
1. Implement in dedicated worktree
2. Write comprehensive tests (80%+ coverage)
3. Create Draft PR with `labot` label
4. Run tests and validate
5. Update to "Ready for review"
6. Merge sequentially (Tasks 3→4→5→6→8)

---

*Generated by Claude Code Desktop on 2025-11-10*
