# Phase 1 Task 1: Implement StrictAuthMiddleware - T4 Security Prompt

**Context**: GPT-5 Pro audit identified LAUNCH BLOCKER - no authentication on API endpoints (55/100 security score)

**Priority**: P0 - CRITICAL BLOCKER
**Effort**: 16 hours
**Goal**: Enforce authentication on ALL API endpoints except explicit allowlist

---

## T4 Security Principles

1. **No New Features** - Only add authentication enforcement, no new functionality
2. **Preserve Existing Auth** - Leverage existing ΛiD JWT system (already implemented)
3. **Minimal Surface Area** - Small allowlist of public endpoints only
4. **Verify Existing Code** - Use `lukhas/governance/auth` components that exist
5. **Test Coverage** - Must test all endpoints return 401 without token

---

## Current Vulnerability

**OWASP A01: Broken Access Control (CRITICAL)**

```python
# serve/consciousness_api.py (CURRENT - VULNERABLE)
@router.post("/api/v1/consciousness/query")
async def query():  # ❌ NO AUTHENTICATION!
    return await engine.process_query()

# serve/feedback_routes.py (CURRENT - VULNERABLE)
@router.post("/api/v1/feedback")
async def submit_feedback(request: FeedbackRequest):  # ❌ NO AUTHENTICATION!
    return await feedback_service.store(request)
```

**Impact**: Anyone can access ANY endpoint without authentication
**Risk**: 100% exploitable - trivial attack

---

## Task 1.1: Create StrictAuthMiddleware

### Step 1: Create Middleware File

**Location**: `lukhas/governance/middleware/strict_auth.py`

**Implementation**:

```python
"""Strict authentication middleware enforcing auth on all routes except allowlist."""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Set
import logging

logger = logging.getLogger(__name__)


class StrictAuthMiddleware(BaseHTTPMiddleware):
    """
    Enforce authentication on all routes except explicit allowlist.

    Security Policy:
    - ALL routes require valid JWT token
    - ONLY allowlisted paths are public
    - Invalid/missing tokens return 401
    - Logs all auth failures for monitoring
    """

    # PUBLIC ENDPOINTS ONLY (minimal surface area)
    ALLOWED_PATHS: Set[str] = {
        "/health",              # Health check
        "/docs",                # API documentation
        "/openapi.json",        # OpenAPI schema
        "/redoc",               # Alternative API docs
        "/api/v1/auth/login",   # Login endpoint
        "/api/v1/auth/register" # Registration endpoint
    }

    async def dispatch(self, request: Request, call_next):
        """Check authentication for all non-allowlisted routes."""

        # Allow public endpoints
        if request.url.path in self.ALLOWED_PATHS:
            return await call_next(request)

        # Require authentication for everything else
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            logger.warning(
                f"Missing auth header: {request.method} {request.url.path} "
                f"from {request.client.host}"
            )
            raise HTTPException(
                status_code=401,
                detail="Authentication required. Include 'Authorization: Bearer <token>' header."
            )

        if not auth_header.startswith("Bearer "):
            logger.warning(
                f"Invalid auth format: {request.method} {request.url.path} "
                f"from {request.client.host}"
            )
            raise HTTPException(
                status_code=401,
                detail="Invalid authorization header format. Use 'Bearer <token>'."
            )

        # Extract token
        token = auth_header.split(" ")[1]

        # Validate token (integrate with existing ΛiD system)
        try:
            # TODO: Call existing token validation from lukhas.governance.auth
            # For now, basic validation (replace with actual ΛiD validation)
            if not token or len(token) < 20:
                raise ValueError("Invalid token format")

            # Store validated user in request state for downstream use
            # request.state.user = validated_user_data

        except Exception as e:
            logger.warning(
                f"Token validation failed: {request.method} {request.url.path} "
                f"from {request.client.host} - {str(e)}"
            )
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired authentication token."
            )

        # Authentication successful, proceed
        response = await call_next(request)
        return response
```

**TODO in Step 1**:
- [ ] Create `lukhas/governance/middleware/__init__.py` if not exists
- [ ] Create `lukhas/governance/middleware/strict_auth.py`
- [ ] Integrate with existing ΛiD token validation (replace TODO)

---

### Step 2: Integrate Middleware into FastAPI App

**Location**: `serve/main.py`

**Current Code** (find this):
```python
from fastapi import FastAPI

app = FastAPI(title="LUKHAS AI API")

# Routes registered here
app.include_router(consciousness_api.router)
app.include_router(feedback_routes.router)
# ... etc
```

**Add After `app = FastAPI(...)`**:
```python
from fastapi import FastAPI
from lukhas.governance.middleware.strict_auth import StrictAuthMiddleware

app = FastAPI(title="LUKHAS AI API")

# SECURITY: Enforce authentication on all routes
app.add_middleware(StrictAuthMiddleware)

# Routes registered here
app.include_router(consciousness_api.router)
app.include_router(feedback_routes.router)
# ... etc
```

**TODO in Step 2**:
- [ ] Add import for StrictAuthMiddleware
- [ ] Add `app.add_middleware(StrictAuthMiddleware)` BEFORE route registrations
- [ ] Verify middleware applies to ALL routes

---

### Step 3: Verify Allowlist is Minimal

**Review**: Check if ANY other endpoints should be public

**Current Allowlist**:
```python
ALLOWED_PATHS: Set[str] = {
    "/health",              # Health check
    "/docs",                # API documentation
    "/openapi.json",        # OpenAPI schema
    "/redoc",               # Alternative API docs
    "/api/v1/auth/login",   # Login endpoint
    "/api/v1/auth/register" # Registration endpoint
}
```

**Action**: Search for endpoints that MUST be public:
```bash
# Find all route definitions
rg -t py "@router\.(get|post|put|delete|patch)" serve/

# Check if any endpoint has public=True or similar
rg -t py "public.*True" serve/
```

**TODO in Step 3**:
- [ ] Review all endpoints in `serve/`
- [ ] Confirm ONLY health, docs, auth should be public
- [ ] Add any legitimate public endpoints to ALLOWED_PATHS
- [ ] Document decision for each allowlisted path

---

### Step 4: Create Tests

**Location**: `tests/unit/lukhas/governance/middleware/test_strict_auth.py`

**Test Cases**:

```python
"""Tests for StrictAuthMiddleware."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from lukhas.governance.middleware.strict_auth import StrictAuthMiddleware


@pytest.fixture
def app():
    """Create test FastAPI app with auth middleware."""
    app = FastAPI()
    app.add_middleware(StrictAuthMiddleware)

    @app.get("/api/protected")
    async def protected_endpoint():
        return {"status": "success"}

    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


class TestStrictAuthMiddleware:
    """Test suite for authentication middleware."""

    def test_health_endpoint_public(self, client):
        """Health check should be accessible without auth."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    def test_protected_endpoint_requires_auth(self, client):
        """Protected endpoints should require authentication."""
        response = client.get("/api/protected")
        assert response.status_code == 401
        assert "Authentication required" in response.json()["detail"]

    def test_missing_bearer_prefix_rejected(self, client):
        """Tokens without Bearer prefix should be rejected."""
        response = client.get(
            "/api/protected",
            headers={"Authorization": "not-bearer-token"}
        )
        assert response.status_code == 401
        assert "Invalid authorization header format" in response.json()["detail"]

    def test_valid_token_grants_access(self, client):
        """Valid Bearer token should grant access."""
        # TODO: Replace with actual valid token from ΛiD system
        response = client.get(
            "/api/protected",
            headers={"Authorization": "Bearer valid-token-placeholder-min-20-chars"}
        )
        # Should succeed (will fail until ΛiD integration complete)
        assert response.status_code == 200

    def test_all_public_endpoints_accessible(self, client):
        """All allowlisted endpoints should be public."""
        public_paths = [
            "/health",
            "/docs",
            "/openapi.json",
            "/redoc"
        ]

        for path in public_paths:
            # Skip paths that don't exist in test app
            if path in ["/docs", "/openapi.json", "/redoc"]:
                continue

            response = client.get(path)
            assert response.status_code != 401, f"{path} should be public"

    def test_post_requests_require_auth(self, client):
        """POST requests should also require auth."""
        response = client.post("/api/protected")
        assert response.status_code == 401
```

**TODO in Step 4**:
- [ ] Create test file with all test cases
- [ ] Run tests: `pytest tests/unit/lukhas/governance/middleware/ -v`
- [ ] All tests should pass (except valid_token test until ΛiD integration)
- [ ] Add to CI pipeline

---

## Integration with Existing ΛiD System

**Current ΛiD Components** (verify these exist):

```bash
# Search for existing auth components
find lukhas/governance -name "*auth*" -type f
find lukhas/identity -name "*auth*" -type f

# Check for JWT validation functions
rg -t py "def.*validate.*token" lukhas/
rg -t py "class.*JWTValidator" lukhas/
```

**Expected Integration Points**:
1. `lukhas.governance.auth.validate_jwt_token(token: str) -> dict`
2. `lukhas.identity.ΛiD.verify_token(token: str) -> UserContext`

**Replace TODO in StrictAuthMiddleware**:

```python
# BEFORE (placeholder):
if not token or len(token) < 20:
    raise ValueError("Invalid token format")

# AFTER (actual ΛiD integration):
from lukhas.governance.auth import validate_jwt_token

try:
    user_data = validate_jwt_token(token)
    request.state.user = user_data  # Store for downstream use
except InvalidTokenError as e:
    raise HTTPException(401, detail=str(e))
```

**TODO in Integration**:
- [ ] Locate existing JWT validation function
- [ ] Replace placeholder validation with actual call
- [ ] Store validated user in `request.state.user`
- [ ] Test with real JWT tokens from ΛiD system

---

## Verification Checklist

Before marking task complete, verify:

### Security Verification
- [ ] **All endpoints return 401 without token** (except allowlist)
- [ ] **Health endpoint still works** without auth
- [ ] **Docs endpoints accessible** without auth
- [ ] **Invalid tokens rejected** with 401
- [ ] **Bearer format enforced** (tokens without "Bearer " rejected)

### Code Quality
- [ ] **No new features added** (only auth enforcement)
- [ ] **ΛiD integration complete** (not placeholder)
- [ ] **Logging enabled** for auth failures
- [ ] **Error messages informative** but not leaking implementation details

### Testing
- [ ] **Unit tests pass** (100% coverage of middleware)
- [ ] **Integration tests added** for protected endpoints
- [ ] **Manual test with curl** or Postman confirms 401s
- [ ] **CI pipeline includes** auth middleware tests

### Documentation
- [ ] **ALLOWED_PATHS documented** with justification for each
- [ ] **README updated** to mention auth requirement
- [ ] **API docs show** auth needed (OpenAPI spec)

---

## Success Criteria

**Functional**:
- ✅ StrictAuthMiddleware deployed to `serve/main.py`
- ✅ ALL endpoints require auth (except 6 allowlisted paths)
- ✅ Invalid/missing tokens return 401
- ✅ Valid ΛiD tokens grant access
- ✅ Logging captures auth failures

**Security**:
- ✅ OWASP A01 vulnerability eliminated
- ✅ No unauthenticated access possible
- ✅ Allowlist minimal (6 paths only)
- ✅ Audit logs show who accessed what

**Testing**:
- ✅ 100% test coverage for middleware
- ✅ All existing tests updated with auth headers
- ✅ CI pipeline enforces auth tests

**Impact**:
- Security Score: 55 → 80 (User ID Integration)
- LAUNCH BLOCKER: Partially lifted (needs Tasks 1.2 + 1.3)

---

## Estimated Timeline

- **Step 1** (Create middleware): 4 hours
- **Step 2** (Integrate into app): 2 hours
- **Step 3** (Verify allowlist): 2 hours
- **Step 4** (Create tests): 4 hours
- **Integration** (ΛiD system): 2 hours
- **Verification** (Manual testing): 2 hours

**Total**: 16 hours

---

## Related Tasks

**Dependencies**:
- Existing ΛiD JWT system (assumed present in `lukhas/governance/auth`)
- FastAPI application setup (assumed present in `serve/main.py`)

**Blocking**:
- Task 1.2 (Remove optional user_id) - Needs auth context from this task
- Task 1.3 (Per-user data isolation) - Needs request.state.user from this task
- Task 2.1 (Secure feedback) - Depends on auth middleware

**Next Steps After Completion**:
1. Move to Task 1.2 (Remove optional user_id)
2. Update all endpoints to use `request.state.user` instead of request body user_id
3. Test cross-user access prevention

---

## References

- **Action Plan**: docs/sessions/GPT5_AUDIT_ACTION_PLAN_2025-11-10.md
- **GPT-5 Audit**: docs/audits/GPT-5 Pro Review - LUKHAS Pre-Launch Au.md
- **OWASP A01**: https://owasp.org/Top10/A01_2021-Broken_Access_Control/
- **FastAPI Middleware**: https://fastapi.tiangolo.com/advanced/middleware/

---

**Created**: 2025-11-10
**Owner**: AI Agent (Claude Web / Jules / Copilot)
**Status**: Ready for execution
**Priority**: P0 - CRITICAL BLOCKER
