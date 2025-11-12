# Phase 1 Task 2: Remove Optional user_id - T4 Security Prompt

**Context**: GPT-5 Pro audit identified CRITICAL identity spoofing vulnerability - clients can claim any user_id

**Priority**: P0 - CRITICAL BLOCKER
**Effort**: 12 hours
**Depends On**: Task 1.1 (StrictAuthMiddleware must be deployed first)
**Goal**: Derive ALL user_id values from JWT auth tokens, never from request bodies

---

## T4 Security Principles

1. **No Client-Provided Identity** - User identity ONLY from validated JWT tokens
2. **Preserve Existing Auth** - Use ΛiD JWT validation from lukhas/governance/auth
3. **Dependency Injection** - Use FastAPI `Depends(get_current_user)` pattern
4. **Remove All Optional user_id** - Eliminate ALL request body user_id fields
5. **Test Cross-User Access** - Verify User A cannot access User B's data

---

## Current Vulnerability

**OWASP A01: Broken Access Control + Identity Spoofing (CRITICAL)**

```python
# serve/feedback_routes.py (CURRENT - VULNERABLE)
class FeedbackRequest(BaseModel):
    user_id: Optional[str] = None  # ❌ CLIENT CAN CLAIM ANY USER_ID!
    rating: int
    comment: str

@router.post("/api/v1/feedback")
async def submit_feedback(request: FeedbackRequest):
    # Blindly trusts request.user_id from client!
    await feedback_service.store(user_id=request.user_id, ...)
    # Attacker can impersonate any user
```

```python
# serve/consciousness_api.py (CURRENT - VULNERABLE)
class QueryRequest(BaseModel):
    context: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None  # ❌ OPTIONAL USER_ID FROM CLIENT!

@router.post("/api/v1/consciousness/query")
async def query(
    request: QueryRequest = Body(...),
    engine: ConsciousnessEngine = Depends(get_consciousness_engine)
):
    # Uses unvalidated request.user_id
    return await engine.process_query(context=request.context)
```

**Impact**:
- Attacker can submit feedback as ANY user
- Attacker can query consciousness state for ANY user
- Attacker can manipulate memories/dreams for ANY user
- 100% exploitable - trivial identity spoofing attack

**Risk**: CRITICAL - Complete identity control bypass

---

## Task 2.1: Create get_current_user() Dependency

### Step 1: Create Authentication Dependency

**Location**: `lukhas/governance/auth/dependencies.py`

**Implementation**:

```python
"""Authentication dependencies for FastAPI endpoints."""

from fastapi import Depends, HTTPException, Request
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


async def get_current_user(request: Request) -> Dict[str, Any]:
    """
    Extract and validate current user from JWT token.

    This dependency MUST be used by all endpoints that need user identity.
    It extracts the validated user data that StrictAuthMiddleware stored
    in request.state.user.

    Returns:
        dict: User data with at minimum:
            - user_id: str (unique user identifier)
            - email: str (user email)
            - roles: List[str] (user roles/permissions)

    Raises:
        HTTPException 401: If no user found (auth middleware didn't run)

    Security:
        - User data comes from validated JWT token ONLY
        - Client cannot spoof user_id via request body
        - StrictAuthMiddleware must be installed for this to work
    """
    # Check if StrictAuthMiddleware populated request.state.user
    if not hasattr(request.state, "user"):
        logger.error(
            "get_current_user called but request.state.user not set. "
            "Is StrictAuthMiddleware installed?"
        )
        raise HTTPException(
            status_code=401,
            detail="Authentication required. User context not found."
        )

    user_data = request.state.user

    # Validate user data structure
    if not isinstance(user_data, dict):
        logger.error(f"Invalid user data type: {type(user_data)}")
        raise HTTPException(
            status_code=500,
            detail="Internal authentication error."
        )

    if "user_id" not in user_data:
        logger.error("User data missing user_id field")
        raise HTTPException(
            status_code=500,
            detail="Internal authentication error."
        )

    return user_data


async def get_current_user_id(request: Request) -> str:
    """
    Extract only the user_id from JWT token.

    Convenience dependency for endpoints that only need user_id.

    Returns:
        str: User ID from validated JWT token

    Raises:
        HTTPException 401: If no user found
    """
    user_data = await get_current_user(request)
    return user_data["user_id"]
```

**TODO in Step 1**:
- [ ] Create `lukhas/governance/auth/dependencies.py`
- [ ] Implement `get_current_user()` dependency
- [ ] Implement `get_current_user_id()` convenience dependency
- [ ] Add logging for security auditing
- [ ] Export from `lukhas/governance/auth/__init__.py`

---

### Step 2: Update StrictAuthMiddleware to Store User

**Location**: `lukhas/governance/middleware/strict_auth.py`

**Update the validation section** (from Task 1.1):

```python
# In StrictAuthMiddleware.dispatch() method
# Replace the TODO section with actual ΛiD validation:

# Validate token (integrate with existing ΛiD system)
try:
    from lukhas.governance.auth import validate_jwt_token

    # Validate token and get user data
    user_data = validate_jwt_token(token)

    # CRITICAL: Store validated user in request state
    request.state.user = user_data

    logger.info(
        f"Authenticated user {user_data.get('user_id')} "
        f"for {request.method} {request.url.path}"
    )

except Exception as e:
    logger.warning(
        f"Token validation failed: {request.method} {request.url.path} "
        f"from {request.client.host} - {str(e)}"
    )
    raise HTTPException(
        status_code=401,
        detail="Invalid or expired authentication token."
    )
```

**TODO in Step 2**:
- [ ] Update StrictAuthMiddleware to call `validate_jwt_token()`
- [ ] Store user data in `request.state.user`
- [ ] Ensure user_data includes at minimum: user_id, email, roles
- [ ] Add logging for authenticated user operations

---

## Task 2.2: Remove user_id from Request Models

### Step 3: Update Feedback Routes

**Location**: `serve/feedback_routes.py`

**BEFORE (Vulnerable)**:
```python
from fastapi import APIRouter, Body
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class FeedbackRequest(BaseModel):
    user_id: Optional[str] = None  # ❌ REMOVE THIS
    rating: int
    comment: str

@router.post("/api/v1/feedback")
async def submit_feedback(request: FeedbackRequest):
    await feedback_service.store(
        user_id=request.user_id,  # ❌ UNVALIDATED!
        rating=request.rating,
        comment=request.comment
    )
    return {"status": "success"}
```

**AFTER (Secure)**:
```python
from fastapi import APIRouter, Body, Depends
from pydantic import BaseModel
from lukhas.governance.auth.dependencies import get_current_user_id

router = APIRouter()

class FeedbackRequest(BaseModel):
    # NO user_id field - derived from auth token!
    rating: int
    comment: str

@router.post("/api/v1/feedback")
async def submit_feedback(
    request: FeedbackRequest,
    user_id: str = Depends(get_current_user_id)  # ✅ FROM JWT!
):
    """Submit feedback for authenticated user."""
    await feedback_service.store(
        user_id=user_id,  # ✅ VALIDATED FROM TOKEN!
        rating=request.rating,
        comment=request.comment
    )
    return {"status": "success", "user_id": user_id}
```

**TODO in Step 3**:
- [ ] Remove `user_id` field from `FeedbackRequest` model
- [ ] Add `user_id: str = Depends(get_current_user_id)` to endpoint
- [ ] Update all feedback operations to use validated user_id
- [ ] Test: Verify cannot submit feedback as another user

---

### Step 4: Update Consciousness API Routes

**Location**: `serve/consciousness_api.py`

**BEFORE (Vulnerable)**:
```python
class QueryRequest(BaseModel):
    context: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None  # ❌ REMOVE THIS

@router.post("/api/v1/consciousness/query")
async def query(
    request: QueryRequest = Body(...),
    engine: ConsciousnessEngine = Depends(get_consciousness_engine)
):
    return await engine.process_query(context=request.context)
```

**AFTER (Secure)**:
```python
from lukhas.governance.auth.dependencies import get_current_user_id

class QueryRequest(BaseModel):
    context: Optional[Dict[str, Any]] = None
    # NO user_id field - derived from auth token!

@router.post("/api/v1/consciousness/query")
async def query(
    request: QueryRequest = Body(...),
    engine: ConsciousnessEngine = Depends(get_consciousness_engine),
    user_id: str = Depends(get_current_user_id)  # ✅ FROM JWT!
):
    """Query consciousness state for authenticated user."""
    return await engine.process_query(
        context=request.context,
        user_id=user_id  # ✅ Pass validated user_id to engine
    )
```

**Update ALL consciousness endpoints**:
- `/api/v1/consciousness/query` - Add user_id dependency
- `/api/v1/consciousness/dream` - Add user_id dependency
- `/api/v1/consciousness/memory` - Add user_id dependency
- `/api/v1/consciousness/state` - Remove user_id from request body, use dependency
- `/api/v1/consciousness/state/{user_id}` - Validate path user_id matches auth user_id

**TODO in Step 4**:
- [ ] Remove `user_id` from `QueryRequest` model
- [ ] Add `user_id = Depends(get_current_user_id)` to all endpoints
- [ ] Update engine method calls to include validated user_id
- [ ] For GET `/state/{user_id}`: validate path param matches auth user_id

---

### Step 5: Update Other Routes with user_id

**Search for all routes with optional user_id**:
```bash
# Find all Pydantic models with user_id fields
rg -t py "user_id.*Optional" serve/

# Find all route parameters with user_id
rg -t py "user_id.*str.*None" serve/

# Find path parameters with user_id
rg -t py "@router\.(get|post|put|delete).*{user_id}" serve/
```

**For each endpoint found**:
1. Remove `user_id` from request Pydantic models
2. Add `user_id: str = Depends(get_current_user_id)` to endpoint signature
3. For path parameters like `/state/{user_id}`:
   ```python
   @router.get("/api/v1/consciousness/state/{path_user_id}")
   async def get_state(
       path_user_id: str,
       auth_user_id: str = Depends(get_current_user_id)
   ):
       # Validate ownership
       if path_user_id != auth_user_id:
           raise HTTPException(403, "Cannot access other user's data")

       # Now safe to use path_user_id
       state = await engine.get_user_state(path_user_id)
       return state
   ```

**TODO in Step 5**:
- [ ] Search for ALL routes with user_id parameters
- [ ] Remove user_id from request bodies
- [ ] Add dependency injection for user_id
- [ ] For path params: validate matches auth user_id
- [ ] Document any admin endpoints that need elevated privileges

---

## Task 2.3: Update Engine Methods

### Step 6: Update ConsciousnessEngine

**Location**: `serve/consciousness_api.py` (and eventually `lukhas/consciousness/`)

**Update engine methods to accept user_id**:

```python
class ConsciousnessEngine:
    """Consciousness engine with per-user state."""

    async def process_query(
        self,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None  # Accept user_id for isolation
    ) -> Dict[str, Any]:
        """Process consciousness query for specific user."""
        await asyncio.sleep(0.008)

        # In real implementation, filter by user_id
        # user_memories = await self.get_user_memories(user_id)

        return {
            "response": "The current awareness level is high.",
            "context": context,
            "user_id": user_id  # Include in response for verification
        }

    async def initiate_dream(
        self,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Initiate dream sequence for specific user."""
        await asyncio.sleep(0.02)

        return {
            "dream_id": f"dream-{user_id}-123",  # User-scoped dream ID
            "status": "generating",
            "context": context,
            "user_id": user_id
        }

    async def retrieve_memory_state(
        self,
        user_id: str  # Required for memory isolation
    ) -> Dict[str, Any]:
        """Retrieve memory state for specific user."""
        await asyncio.sleep(0.004)

        # In real implementation, query user-specific memories
        return {
            "memory_folds": 1024,
            "recall_accuracy": 0.98,
            "user_id": user_id
        }
```

**TODO in Step 6**:
- [ ] Add `user_id` parameter to all engine methods
- [ ] Update method implementations to use user_id for data filtering
- [ ] Include user_id in response for verification
- [ ] Update all engine method calls in routes

---

## Task 2.4: Create Tests

### Step 7: Test Cross-User Access Prevention

**Location**: `tests/unit/lukhas/governance/auth/test_dependencies.py`

```python
"""Tests for authentication dependencies."""

import pytest
from fastapi import FastAPI, Depends, HTTPException
from fastapi.testclient import TestClient
from lukhas.governance.auth.dependencies import get_current_user, get_current_user_id


@pytest.fixture
def app():
    """Create test FastAPI app."""
    app = FastAPI()

    @app.get("/api/protected")
    async def protected_endpoint(user_id: str = Depends(get_current_user_id)):
        return {"message": "success", "user_id": user_id}

    @app.get("/api/profile")
    async def profile_endpoint(user_data = Depends(get_current_user)):
        return user_data

    return app


@pytest.fixture
def client(app):
    return TestClient(app)


class TestGetCurrentUser:
    """Test suite for get_current_user dependency."""

    def test_requires_request_state_user(self, client):
        """Should fail if request.state.user not set."""
        # StrictAuthMiddleware not installed - no request.state.user
        response = client.get("/api/protected")
        assert response.status_code == 401
        assert "User context not found" in response.json()["detail"]

    def test_extracts_user_id_from_state(self, app, client):
        """Should extract user_id from request.state.user."""
        # Mock middleware that sets request.state.user
        from starlette.middleware.base import BaseHTTPMiddleware

        class MockAuthMiddleware(BaseHTTPMiddleware):
            async def dispatch(self, request, call_next):
                request.state.user = {
                    "user_id": "user123",
                    "email": "test@example.com",
                    "roles": ["user"]
                }
                return await call_next(request)

        app.add_middleware(MockAuthMiddleware)
        client = TestClient(app)

        response = client.get("/api/protected")
        assert response.status_code == 200
        assert response.json()["user_id"] == "user123"

    def test_fails_if_user_id_missing(self, app, client):
        """Should fail if user data missing user_id."""
        from starlette.middleware.base import BaseHTTPMiddleware

        class MockAuthMiddleware(BaseHTTPMiddleware):
            async def dispatch(self, request, call_next):
                request.state.user = {"email": "test@example.com"}  # No user_id!
                return await call_next(request)

        app.add_middleware(MockAuthMiddleware)
        client = TestClient(app)

        response = client.get("/api/protected")
        assert response.status_code == 500
        assert "authentication error" in response.json()["detail"].lower()
```

**Location**: `tests/integration/test_cross_user_access.py`

```python
"""Integration tests for cross-user access prevention."""

import pytest
from fastapi.testclient import TestClient


class TestCrossUserAccessPrevention:
    """Verify users cannot access each other's data."""

    def test_cannot_submit_feedback_as_another_user(self, client):
        """User A cannot submit feedback claiming to be User B."""
        # Login as User A
        login_resp = client.post("/api/v1/auth/login", json={
            "email": "userA@example.com",
            "password": "passwordA"
        })
        token_a = login_resp.json()["access_token"]

        # Try to submit feedback (will use User A's ID from token)
        response = client.post(
            "/api/v1/feedback",
            headers={"Authorization": f"Bearer {token_a}"},
            json={
                # NO user_id field - cannot spoof!
                "rating": 5,
                "comment": "Great app!"
            }
        )

        assert response.status_code == 200
        # Verify feedback attributed to User A (from token)
        assert response.json()["user_id"] == "userA_id"

        # Verify cannot inject user_id in request body
        response = client.post(
            "/api/v1/feedback",
            headers={"Authorization": f"Bearer {token_a}"},
            json={
                "user_id": "userB_id",  # Try to spoof User B
                "rating": 1,
                "comment": "Hacking attempt"
            }
        )

        # Should either ignore user_id or reject request
        # But MUST NOT attribute feedback to User B
        if response.status_code == 200:
            assert response.json()["user_id"] == "userA_id"  # Still User A!

    def test_cannot_query_another_users_consciousness(self, client):
        """User A cannot query User B's consciousness state."""
        # Login as User A
        login_resp = client.post("/api/v1/auth/login", json={
            "email": "userA@example.com",
            "password": "passwordA"
        })
        token_a = login_resp.json()["access_token"]

        # Query consciousness (will use User A's context from token)
        response = client.post(
            "/api/v1/consciousness/query",
            headers={"Authorization": f"Bearer {token_a}"},
            json={"context": {"query": "awareness"}}
        )

        assert response.status_code == 200
        # Verify response scoped to User A
        assert response.json()["user_id"] == "userA_id"

        # Try to access User B's state via path parameter
        response = client.get(
            "/api/v1/consciousness/state/userB_id",  # User B's ID
            headers={"Authorization": f"Bearer {token_a}"}  # User A's token
        )

        # Should return 403 Forbidden
        assert response.status_code == 403
        assert "Cannot access other user" in response.json()["detail"]
```

**TODO in Step 7**:
- [ ] Create unit tests for `get_current_user()` dependency
- [ ] Create integration tests for cross-user access prevention
- [ ] Test feedback submission cannot be spoofed
- [ ] Test consciousness queries scoped to auth user
- [ ] Test path parameters validated against auth user
- [ ] All tests must pass

---

## Verification Checklist

Before marking task complete, verify:

### Security Verification
- [ ] **No endpoint accepts user_id from request body** (all models updated)
- [ ] **All endpoints use Depends(get_current_user_id)** for user identity
- [ ] **StrictAuthMiddleware stores user in request.state.user**
- [ ] **get_current_user() validates user data structure**
- [ ] **Cross-user access tests FAIL** (User A cannot access User B's data)
- [ ] **Path parameter validation** (e.g., `/state/{user_id}` checks ownership)

### Code Quality
- [ ] **All request models cleaned** (no user_id fields)
- [ ] **All engine methods updated** (accept user_id parameter)
- [ ] **Logging enabled** for user operations
- [ ] **Error messages informative** but not leaking user IDs
- [ ] **Consistent pattern** across all endpoints

### Testing
- [ ] **Unit tests pass** (get_current_user dependency)
- [ ] **Integration tests pass** (cross-user access prevention)
- [ ] **Manual test with curl** confirms cannot spoof user_id
- [ ] **CI pipeline includes** identity tests

### Documentation
- [ ] **Dependencies documented** in lukhas/governance/auth/README.md
- [ ] **Endpoint changes documented** in API docs
- [ ] **Security model explained** (JWT → user_id flow)

---

## Success Criteria

**Functional**:
- ✅ `get_current_user()` dependency deployed
- ✅ ALL endpoints derive user_id from JWT token
- ✅ NO endpoint accepts user_id from client
- ✅ Path parameters validated against auth user
- ✅ Engine methods updated for per-user operations

**Security**:
- ✅ Identity spoofing vulnerability eliminated
- ✅ OWASP A01 partially mitigated (identity layer secure)
- ✅ Cross-user access prevented
- ✅ Audit logs show actual user, not spoofed user

**Testing**:
- ✅ 100% test coverage for auth dependencies
- ✅ Cross-user access tests demonstrate protection
- ✅ CI pipeline enforces identity security tests

**Impact**:
- Security Score: 55 → 75 (Identity Spoofing eliminated)
- LAUNCH BLOCKER: 50% lifted (still need Task 1.3 for full mitigation)

---

## Estimated Timeline

- **Step 1** (get_current_user dependency): 2 hours
- **Step 2** (Update middleware): 1 hour
- **Step 3** (Update feedback routes): 2 hours
- **Step 4** (Update consciousness routes): 2 hours
- **Step 5** (Search and update other routes): 2 hours
- **Step 6** (Update engine methods): 1 hour
- **Step 7** (Create tests): 2 hours

**Total**: 12 hours

---

## Related Tasks

**Dependencies**:
- Task 1.1 (StrictAuthMiddleware) - MUST be deployed first to populate request.state.user

**Blocking**:
- Task 1.3 (Per-user data isolation) - Needs validated user_id from this task
- Task 2.1 (Secure feedback) - Depends on get_current_user() dependency
- All future endpoint development - Must use this pattern

**Next Steps After Completion**:
1. Move to Task 1.3 (Implement per-user data isolation at database level)
2. Update all data queries to filter by user_id
3. Test multi-user scenarios with real database

---

## References

- **Action Plan**: docs/sessions/GPT5_AUDIT_ACTION_PLAN_2025-11-10.md
- **GPT-5 Audit**: docs/audits/GPT-5 Pro Review - LUKHAS Pre-Launch Au.md
- **OWASP A01**: https://owasp.org/Top10/A01_2021-Broken_Access_Control/
- **FastAPI Dependencies**: https://fastapi.tiangolo.com/tutorial/dependencies/

---

**Created**: 2025-11-10
**Owner**: AI Agent (Claude Web / Jules / Copilot)
**Status**: Ready for execution
**Priority**: P0 - CRITICAL BLOCKER
**Depends On**: Task 1.1 (StrictAuthMiddleware)
