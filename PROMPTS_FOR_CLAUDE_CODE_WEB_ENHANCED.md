# Enhanced Prompts for Claude Code Web - Future-Proofed API Creation

**Date**: 2025-11-10 (Enhanced)
**Based On**: User ID Integration, Endocrine, and Feedback System Audits
**Enhancement**: Added comprehensive security, authentication, and privacy requirements

---

## 🔒 CRITICAL: Universal Security Requirements for ALL APIs

**⚠️ THESE REQUIREMENTS ARE MANDATORY FOR EVERY API ENDPOINT**

Based on comprehensive security audits (scores: 55-70/100), the following patterns MUST be applied to all new API development to achieve production-ready status (>90/100).

### 1. Authentication & Authorization 🛡️

**ALWAYS REQUIRED**:
```python
from fastapi import Depends, HTTPException
from lukhas_website.lukhas.identity.tier_system import (
    lukhas_tier_required,
    TierLevel,
    PermissionScope
)

async def get_current_user(request: Request) -> dict:
    """Extract current user from request state (set by StrictAuthMiddleware)"""
    if not hasattr(request.state, "user_id"):
        raise HTTPException(status_code=401, detail="Not authenticated")

    return {
        "user_id": request.state.user_id,
        "tier": request.state.user_tier,
        "permissions": request.state.user_permissions,
    }

@router.post("/api/v1/resource")
@lukhas_tier_required(TierLevel.AUTHENTICATED, PermissionScope.RESOURCE_CREATE)
async def create_resource(
    request: CreateResourceRequest,
    current_user: dict = Depends(get_current_user)  # ✅ REQUIRED
):
    user_id = current_user["user_id"]  # ✅ Extract from auth, NOT request
    # ... implementation
```

**❌ NEVER DO THIS**:
```python
# BAD: user_id in request body (spoofable!)
class CreateResourceRequest(BaseModel):
    user_id: str  # ❌ SECURITY HOLE
    data: str

# BAD: Optional authentication
async def create_resource(request: CreateResourceRequest):
    user_id = request.user_id  # ❌ Anyone can claim any user_id!
```

### 2. User Isolation 🔐

**ALL data operations MUST be scoped to user_id**:

```python
# ✅ CORRECT: User-scoped operations
async def get_user_dreams(
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]
    dreams = await dream_engine.get_dreams(user_id=user_id)  # ✅ Scoped
    return dreams

# ✅ CORRECT: Validate cross-user access
async def get_dream_by_id(
    dream_id: str,
    current_user: dict = Depends(get_current_user)
):
    dream = await dream_engine.get_dream(dream_id)

    # ✅ CRITICAL: Validate ownership
    if dream.user_id != current_user["user_id"] and current_user["tier"] < TierLevel.ADMIN:
        raise HTTPException(403, "Cannot access other user's dreams")

    return dream

# ❌ BAD: Global queries (user A can see user B's data)
async def get_all_dreams():
    return await dream_engine.get_all_dreams()  # ❌ NO USER ISOLATION
```

### 3. Tier-Based Access Control 🎚️

**Apply appropriate tier requirements**:

| Tier | Access Level | Use Cases |
|------|-------------|-----------|
| **PUBLIC (0)** | Health checks, docs | GET /health, GET /docs |
| **AUTHENTICATED (2)** | Basic operations | Own data CRUD |
| **POWER_USER (3)** | Advanced features | Parallel dreams, advanced analytics |
| **PRO (4)** | Premium features | Custom analytics, exports |
| **ENTERPRISE (5)** | Enterprise features | Bulk operations, team management |
| **ADMIN/SYSTEM (6)** | Admin operations | Cross-user access, system config |

```python
# Examples:
@lukhas_tier_required(TierLevel.AUTHENTICATED, PermissionScope.DREAMS_CREATE)
async def create_dream(...):  # Tier 2+

@lukhas_tier_required(TierLevel.POWER_USER, PermissionScope.DREAMS_PARALLEL)
async def create_parallel_dream(...):  # Tier 3+

@lukhas_tier_required(TierLevel.PRO, PermissionScope.ANALYTICS_EXPORT)
async def export_analytics(...):  # Tier 4+

@lukhas_tier_required(TierLevel.ADMIN, PermissionScope.ADMIN_ACTIONS)
async def trigger_system_operation(...):  # Tier 6 only
```

### 4. Rate Limiting 🚦

**Prevent abuse with appropriate rate limits**:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# Standard operations: 100/minute
@router.get("/api/v1/resource")
@limiter.limit("100/minute")
async def get_resource(...):
    ...

# Write operations: 50/minute
@router.post("/api/v1/resource")
@limiter.limit("50/minute")
async def create_resource(...):
    ...

# Expensive operations: 10/minute
@router.post("/api/v1/analytics/export")
@limiter.limit("10/minute")
async def export_data(...):
    ...

# Admin operations: 5/minute
@router.post("/api/v1/admin/trigger")
@limiter.limit("5/minute")
async def trigger_operation(...):
    ...
```

### 5. Audit Logging 📝

**Log ALL operations with user_id**:

```python
import logging

logger = logging.getLogger(__name__)

async def create_resource(
    request: CreateResourceRequest,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]

    try:
        resource = await resource_manager.create(
            user_id=user_id,
            data=request.data
        )

        # ✅ Audit log with user_id
        logger.info(
            "Resource created",
            extra={
                "user_id": user_id,
                "resource_id": resource.id,
                "resource_type": "dream",
                "operation": "create",
                "tier": current_user["tier"]
            }
        )

        return resource

    except Exception as e:
        # ✅ Log failures too
        logger.error(
            f"Resource creation failed: {e}",
            extra={
                "user_id": user_id,
                "error": str(e),
                "operation": "create"
            }
        )
        raise
```

### 6. Input Validation & Injection Prevention 🛡️

**Validate ALL inputs with Pydantic**:

```python
from pydantic import BaseModel, Field, validator
from typing import Optional

class CreateDreamRequest(BaseModel):
    symbols: list[str] = Field(..., min_items=1, max_items=50)
    context: Optional[dict] = Field(None, max_items=20)
    priority: str = Field("NORMAL", regex="^(LOW|NORMAL|HIGH|URGENT)$")

    @validator("symbols")
    def validate_symbols(cls, v):
        """Prevent injection attacks"""
        for symbol in v:
            if len(symbol) > 100:
                raise ValueError("Symbol too long (max 100 chars)")
            if any(char in symbol for char in ["<", ">", "script", "eval"]):
                raise ValueError("Invalid characters in symbol")
        return v

    @validator("context")
    def validate_context(cls, v):
        """Limit context size"""
        if v and len(str(v)) > 10000:
            raise ValueError("Context too large (max 10KB)")
        return v
```

### 7. Error Handling Patterns ⚠️

**Consistent error responses**:

```python
from fastapi import HTTPException, status

# 401 Unauthorized - No valid authentication
if not current_user:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required"
    )

# 403 Forbidden - Authenticated but insufficient permissions
if current_user["tier"] < required_tier:
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"Requires tier {required_tier.name} or higher"
    )

# 403 Forbidden - Cross-user access attempt
if resource.user_id != current_user["user_id"] and not is_admin:
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Cannot access other user's resources"
    )

# 404 Not Found - Resource doesn't exist
if not resource:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Resource {resource_id} not found"
    )

# 429 Too Many Requests - Rate limit exceeded
# (Handled automatically by slowapi limiter)

# 500 Internal Server Error - Unexpected errors
try:
    result = await dangerous_operation()
except Exception as e:
    logger.error(f"Operation failed: {e}", extra={"user_id": user_id})
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Internal server error"
    )
```

### 8. Privacy & GDPR Compliance 🔒

**Privacy-preserving patterns**:

```python
import hashlib
from datetime import datetime, timedelta

def hash_user_id_for_analytics(user_id: str) -> str:
    """Hash user_id for privacy-preserving analytics"""
    return hashlib.sha256(user_id.encode()).hexdigest()[:16]

class DataRetentionPolicy:
    """Enforce data retention policies"""

    RETENTION_PERIODS = {
        "feedback": timedelta(days=90),
        "analytics": timedelta(days=365),
        "audit_logs": timedelta(days=730),
    }

    @staticmethod
    async def cleanup_expired_data(data_type: str):
        """Auto-delete data past retention period"""
        cutoff = datetime.utcnow() - DataRetentionPolicy.RETENTION_PERIODS[data_type]
        # Delete data older than cutoff

# GDPR Data Export
@router.get("/api/v1/users/{user_id}/export")
@lukhas_tier_required(TierLevel.AUTHENTICATED, PermissionScope.DATA_EXPORT)
async def export_user_data(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    # ✅ User can only export own data
    if user_id != current_user["user_id"] and current_user["tier"] < TierLevel.ADMIN:
        raise HTTPException(403, "Can only export own data")

    data = await collect_all_user_data(user_id)
    return {"data": data, "format": "json"}

# GDPR Data Deletion
@router.delete("/api/v1/users/{user_id}/data")
@lukhas_tier_required(TierLevel.ADMIN, PermissionScope.DATA_DELETE)
async def delete_user_data(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Admin-only: Complete user data deletion"""
    await delete_all_user_data(user_id)
    logger.info(f"Deleted all data for user {user_id}", extra={"admin_id": current_user["user_id"]})
    return {"message": "User data deleted successfully"}
```

### 9. Testing Requirements 🧪

**Every endpoint MUST have these tests**:

```python
# 1. Success case with valid auth
@pytest.mark.asyncio
async def test_create_resource_success():
    response = await client.post(
        "/api/v1/resource",
        headers={"Authorization": f"Bearer {valid_token}"},
        json={"data": "test"}
    )
    assert response.status_code == 201
    assert "user_id" not in response.json()  # Not exposed

# 2. 401 without authentication
@pytest.mark.asyncio
async def test_create_resource_unauthorized():
    response = await client.post("/api/v1/resource", json={"data": "test"})
    assert response.status_code == 401
    assert "Authentication required" in response.json()["detail"]

# 3. 403 with insufficient tier
@pytest.mark.asyncio
async def test_create_resource_forbidden():
    response = await client.post(
        "/api/v1/resource",
        headers={"Authorization": f"Bearer {tier1_token}"},  # Tier 1 too low
        json={"data": "test"}
    )
    assert response.status_code == 403
    assert "tier" in response.json()["detail"].lower()

# 4. Cross-user access blocked
@pytest.mark.asyncio
async def test_cannot_access_other_user_resource():
    # User A creates resource
    response_a = await client.post(
        "/api/v1/resource",
        headers={"Authorization": f"Bearer {user_a_token}"},
        json={"data": "test"}
    )
    resource_id = response_a.json()["id"]

    # User B tries to access
    response_b = await client.get(
        f"/api/v1/resource/{resource_id}",
        headers={"Authorization": f"Bearer {user_b_token}"}
    )
    assert response_b.status_code == 403
    assert "Cannot access other user" in response_b.json()["detail"]

# 5. Rate limiting
@pytest.mark.asyncio
async def test_rate_limiting():
    for i in range(51):  # Exceed 50/min limit
        response = await client.post(
            "/api/v1/resource",
            headers={"Authorization": f"Bearer {valid_token}"},
            json={"data": f"test{i}"}
        )

    assert response.status_code == 429  # Last request rate limited

# 6. Input validation
@pytest.mark.asyncio
async def test_input_validation():
    response = await client.post(
        "/api/v1/resource",
        headers={"Authorization": f"Bearer {valid_token}"},
        json={"data": "<script>alert('xss')</script>"}  # XSS attempt
    )
    assert response.status_code == 422  # Validation error
```

### 10. OpenAPI Documentation 📚

**Complete documentation for every endpoint**:

```python
@router.post(
    "/api/v1/dreams",
    response_model=DreamResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Dream",
    description="Create a new dream with the provided symbols and context.",
    responses={
        201: {
            "description": "Dream created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "dream_id": "drm_123",
                        "status": "processing",
                        "created_at": "2025-11-10T12:00:00Z"
                    }
                }
            }
        },
        401: {"description": "Authentication required"},
        403: {"description": "Insufficient tier or permissions"},
        422: {"description": "Validation error"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"}
    },
    tags=["dreams"]
)
@lukhas_tier_required(TierLevel.AUTHENTICATED, PermissionScope.DREAMS_CREATE)
@limiter.limit("50/minute")
async def create_dream(
    request: CreateDreamRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new dream.

    **Authentication**: Required (Tier 2+)
    **Rate Limit**: 50 requests/minute
    **User Isolation**: Can only create dreams for authenticated user

    **Permissions**:
    - Tier 2+: Standard dreams
    - Tier 3+: Parallel dreams (with PARALLEL_DREAMS_ENABLED)

    **Privacy**: User can only access own dreams unless Admin tier
    """
    user_id = current_user["user_id"]
    # ... implementation
```

---

## Task 3: Production API Routes (ENHANCED)

### Prompt for Claude Code Web

```
TASK: Create production-ready FastAPI routes with COMPREHENSIVE SECURITY

CONTEXT:
- Wrapper modules exist in lukhas/dream/, lukhas/glyphs/
- ⚠️  CRITICAL: Apply ALL security requirements from Universal Security Requirements section
- Feature flags: DREAMS_ENABLED, GLYPHS_ENABLED, PARALLEL_DREAMS_ENABLED
- This is Task 3 of the Core Wiring plan

SECURITY MANDATE:
🔴 EVERY endpoint MUST include:
1. `current_user: dict = Depends(get_current_user)` - NO EXCEPTIONS
2. `@lukhas_tier_required(...)` decorator with appropriate tier
3. `@limiter.limit(...)` for rate limiting
4. User isolation: All operations scoped to current_user["user_id"]
5. Cross-user access validation for GET by ID operations
6. Comprehensive audit logging with user_id
7. Input validation with Pydantic
8. All 6 test types (success, 401, 403, cross-user, rate-limit, validation)

OBJECTIVE:
Create three new FastAPI route modules with production-grade security.

FILES TO CREATE:
1. lukhas_website/lukhas/api/dreams.py (~200-250 lines with security)
2. lukhas_website/lukhas/api/drift.py (~150-200 lines with security)
3. lukhas_website/lukhas/api/glyphs.py (~200-250 lines with security)

REQUIREMENTS:

### 1. Dreams API (lukhas/api/dreams.py)

Endpoints:
- POST /api/v1/dreams/parallel - Create parallel dream [Tier 3+, 30/min]
- GET /api/v1/dreams/{dream_id} - Get dream by ID [Tier 2+, 100/min]
- GET /api/v1/dreams/list - List user's dreams [Tier 2+, 100/min]
- DELETE /api/v1/dreams/{dream_id} - Delete dream [Tier 2+, 50/min]

Example Implementation (SECURE):
```python
from fastapi import APIRouter, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from lukhas_website.lukhas.identity.tier_system import (
    lukhas_tier_required,
    TierLevel,
    PermissionScope
)
import logging

router = APIRouter(prefix="/api/v1/dreams", tags=["dreams"])
limiter = Limiter(key_func=get_remote_address)
logger = logging.getLogger(__name__)

async def get_current_user(request: Request) -> dict:
    """Extract current user from request state"""
    if not hasattr(request.state, "user_id"):
        raise HTTPException(401, "Authentication required")
    return {
        "user_id": request.state.user_id,
        "tier": request.state.user_tier,
        "permissions": request.state.user_permissions,
    }

class CreateDreamRequest(BaseModel):
    symbols: list[str] = Field(..., min_items=1, max_items=50)
    parallel: bool = Field(False)
    context: Optional[dict] = Field(None)

    @validator("symbols")
    def validate_symbols(cls, v):
        for symbol in v:
            if len(symbol) > 100:
                raise ValueError("Symbol too long")
        return v

@router.post(
    "/parallel",
    response_model=DreamResponse,
    status_code=201,
    summary="Create Parallel Dream",
    responses={
        201: {"description": "Dream created"},
        401: {"description": "Unauthorized"},
        403: {"description": "Insufficient tier or feature disabled"},
        429: {"description": "Rate limit exceeded"}
    }
)
@lukhas_tier_required(TierLevel.POWER_USER, PermissionScope.DREAMS_PARALLEL)
@limiter.limit("30/minute")
async def create_parallel_dream(
    request: CreateDreamRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Create parallel dream processing task.

    **Tier**: 3+ (Power User)
    **Rate**: 30/minute
    **Feature Flag**: Requires PARALLEL_DREAMS_ENABLED=true
    """
    user_id = current_user["user_id"]

    # Check feature flag
    if not os.getenv("PARALLEL_DREAMS_ENABLED", "false").lower() in ("true", "1"):
        raise HTTPException(403, "Parallel dreams feature not enabled")

    try:
        engine = get_dream_engine()
        dream = await engine.create_parallel_dream(
            user_id=user_id,
            symbols=request.symbols,
            context=request.context
        )

        logger.info(
            "Parallel dream created",
            extra={
                "user_id": user_id,
                "dream_id": dream.id,
                "symbols_count": len(request.symbols)
            }
        )

        return dream

    except Exception as e:
        logger.error(
            f"Parallel dream creation failed: {e}",
            extra={"user_id": user_id, "error": str(e)}
        )
        raise HTTPException(500, "Dream creation failed")

@router.get(
    "/{dream_id}",
    response_model=DreamResponse,
    summary="Get Dream by ID"
)
@lukhas_tier_required(TierLevel.AUTHENTICATED, PermissionScope.DREAMS_READ)
@limiter.limit("100/minute")
async def get_dream(
    dream_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get dream by ID. Users can only access own dreams unless Admin."""
    user_id = current_user["user_id"]

    engine = get_dream_engine()
    dream = await engine.get_dream(dream_id)

    if not dream:
        raise HTTPException(404, f"Dream {dream_id} not found")

    # ✅ CRITICAL: Validate ownership
    if dream.user_id != user_id and current_user["tier"] < TierLevel.ADMIN:
        logger.warning(
            "Cross-user dream access attempt",
            extra={
                "user_id": user_id,
                "dream_id": dream_id,
                "dream_owner": dream.user_id
            }
        )
        raise HTTPException(403, "Cannot access other user's dreams")

    return dream

@router.get(
    "/list",
    response_model=DreamListResponse,
    summary="List User's Dreams"
)
@lukhas_tier_required(TierLevel.AUTHENTICATED, PermissionScope.DREAMS_READ)
@limiter.limit("100/minute")
async def list_dreams(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """List dreams for current user (paginated)."""
    user_id = current_user["user_id"]  # ✅ Scoped to user

    engine = get_dream_engine()
    dreams = await engine.list_dreams(
        user_id=user_id,  # ✅ User-scoped query
        limit=limit,
        offset=offset
    )

    return {"dreams": dreams, "count": len(dreams)}

@router.delete(
    "/{dream_id}",
    status_code=204,
    summary="Delete Dream"
)
@lukhas_tier_required(TierLevel.AUTHENTICATED, PermissionScope.DREAMS_DELETE)
@limiter.limit("50/minute")
async def delete_dream(
    dream_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete dream by ID. Users can only delete own dreams."""
    user_id = current_user["user_id"]

    engine = get_dream_engine()
    dream = await engine.get_dream(dream_id)

    if not dream:
        raise HTTPException(404, f"Dream {dream_id} not found")

    # ✅ CRITICAL: Validate ownership
    if dream.user_id != user_id and current_user["tier"] < TierLevel.ADMIN:
        raise HTTPException(403, "Cannot delete other user's dreams")

    await engine.delete_dream(dream_id)

    logger.info(
        "Dream deleted",
        extra={"user_id": user_id, "dream_id": dream_id}
    )

    return None  # 204 No Content
```

### 2. Drift API (lukhas/api/drift.py)

Endpoints:
- GET /api/v1/drift/{user_id} - Get drift metrics [Tier 2+ for own, Tier 6 for others, 100/min]
- POST /api/v1/drift/update - Update metrics [Admin only, 10/min]
- GET /api/v1/drift/analysis - Drift analysis [Tier 4+, 50/min]

**Security Focus**:
- GET /{user_id}: Validate current_user can only access own drift unless Admin
- POST /update: Admin only (Tier 6)
- All operations audit logged

### 3. Glyphs API (lukhas/api/glyphs.py)

Endpoints:
- POST /api/v1/glyphs/bind - Bind GLYPH [Tier 2+, 50/min]
- GET /api/v1/glyphs/{glyph_id} - Get GLYPH [Tier 2+, 100/min]
- POST /api/v1/glyphs/validate - Validate GLYPH [Tier 2+, 100/min]
- DELETE /api/v1/glyphs/{glyph_id} - Unbind GLYPH [Tier 2+, 50/min]

**Security Focus**:
- All GLYPH operations audit logged (security-sensitive)
- Comprehensive input validation (prevent GLYPH injection)
- Cross-user access validation

TESTING:
Create tests/unit/api/test_dreams_routes_secure.py with ALL 6 test types:
1. ✅ Success with valid auth
2. ❌ 401 without auth
3. ❌ 403 with insufficient tier
4. ❌ 403 cross-user access
5. ❌ 429 rate limit exceeded
6. ❌ 422 validation error

SUCCESS CRITERIA:
- ✅ All routes require authentication (no unauthenticated access)
- ✅ All routes have tier requirements (no Tier 1/PUBLIC on write operations)
- ✅ All routes have rate limiting
- ✅ User isolation enforced (user A cannot access user B's data)
- ✅ Audit logging includes user_id for all operations
- ✅ All 6 test types pass for each endpoint
- ✅ OpenAPI docs complete with security requirements

COMMIT MESSAGE FORMAT:
feat(api): add production-ready secured routes for dreams, drift, glyphs

Implements Task 3 with comprehensive security requirements:
- Dreams API: parallel processing, lifecycle management (Tier 2-3)
- Drift API: Vivox metrics with user isolation (Tier 2-6)
- Glyphs API: token binding with audit logging (Tier 2+)

Security Features:
- ✅ Authentication required on ALL endpoints
- ✅ Tier-based access control (2-6)
- ✅ Rate limiting (30-100 req/min per endpoint)
- ✅ User isolation (user-scoped queries)
- ✅ Cross-user access validation
- ✅ Comprehensive audit logging with user_id
- ✅ Input validation (Pydantic + custom validators)

Tests: 80%+ coverage with all 6 security test types

Security Score: 90+/100 (vs 55/100 without these requirements)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## Task 4: Wire Parallel Dreams Feature Flag (ENHANCED - UNCHANGED)

[Keep original Task 4 as-is - it's not user-facing API so security requirements less critical]

---

## Task 5: Wire Vivox Drift into User Profiles (ENHANCED)

### Prompt for Claude Code Web

```
TASK: Integrate Vivox drift metrics with USER ISOLATION

CONTEXT:
- Previous audit found optional user_id in drift operations (security gap)
- Must enforce user-scoped drift data
- Cross-user drift access only for Admin tier
- This is Task 5 of the Core Wiring plan

SECURITY ENHANCEMENTS:
🔴 MANDATORY CHANGES:
1. user_id parameter REQUIRED (not optional) in all drift methods
2. User profiles endpoint validates cross-user access
3. Drift history scoped to user_id (no global queries)
4. Audit logging for all drift data access

[Include enhanced security version of original Task 5 with user_id enforcement]
```

---

## Task 6: Create GLYPH Bind Endpoints (ENHANCED)

[Enhanced version with security requirements already added above]

---

## Security Checklist for Each API ✅

Before marking any API task complete, verify:

- [ ] All endpoints have `Depends(get_current_user)`
- [ ] All endpoints have `@lukhas_tier_required` decorator
- [ ] All endpoints have `@limiter.limit()` decorator
- [ ] All data queries are user-scoped (includes user_id filter)
- [ ] GET-by-ID endpoints validate ownership (403 on cross-user access)
- [ ] All operations audit logged with user_id
- [ ] All Pydantic models have input validation
- [ ] All 6 test types implemented (success, 401, 403, cross-user, 429, 422)
- [ ] OpenAPI docs include authentication requirements
- [ ] No user_id in request body (only from auth token)
- [ ] Error responses use standard status codes (401/403/404/429/500)
- [ ] Privacy considerations (GDPR export/delete if applicable)

**Score Target**: 90+/100 (vs current 55-70/100)

---

*Enhanced by Claude Code on 2025-11-10 based on comprehensive security audits*
*Original prompts maintained compatibility while adding critical security layers*
