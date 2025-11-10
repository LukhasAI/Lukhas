#!/usr/bin/env python3
"""
Create Jules sessions for security hardening tasks (Categories 1-6 BLOCKING).

Based on: docs/tasks/SECURITY_HARDENING_TASKS_2025-11-10.md
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from bridge.llm_wrappers.jules_wrapper import JulesClient


SECURITY_TASKS = [
    {
        "title": "Category 1: StrictAuthMiddleware Implementation",
        "prompt": """
**BLOCKING TASK - P0 LAUNCH BLOCKER**

Create StrictAuthMiddleware that validates JWT tokens and attaches user context to all requests.

**Files to Create**:
- `lukhas_website/lukhas/api/middleware/strict_auth.py`
- `tests/unit/api/middleware/test_strict_auth.py`

**Implementation Requirements**:

1. Create middleware class that:
   - Validates Bearer tokens for all /v1/* and /api/* paths
   - Extracts user_id, tier, permissions from JWT claims
   - Attaches to request.state (user_id, user_tier, user_permissions)
   - Returns 401 for missing/invalid/expired tokens
   - Bypasses auth for health endpoints (/healthz, /health, /readyz, /metrics)

2. JWT Validation:
   - Use production-safe crypto (PyJWT with RS256 or HS256)
   - Validate signature
   - Check expiration
   - Extract claims: sub (user_id), tier, permissions

3. Request State Attachment:
   ```python
   request.state.user_id = claims["sub"]
   request.state.user_tier = claims.get("tier", 0)
   request.state.user_permissions = claims.get("permissions", [])
   ```

**Tests Required** (12 tests):
- Health endpoints bypass auth
- /v1/* paths require Bearer token
- Missing token returns 401
- Invalid token returns 401
- Expired token returns 401
- Valid token attaches user_id to request.state
- Valid token attaches user_tier to request.state
- Valid token attaches user_permissions to request.state
- Non-/v1/ paths bypass auth (for legacy routes)
- Bearer token with wrong signature returns 401
- Bearer token with tampered payload returns 401
- request.state.user_id matches JWT sub claim

**Success Criteria**:
- [ ] Middleware created and tested
- [ ] Applied to FastAPI app (serve/main.py)
- [ ] All 12 tests passing
- [ ] JWT validation uses production-safe crypto
- [ ] No hardcoded secrets

**Reference**: docs/tasks/SECURITY_HARDENING_TASKS_2025-11-10.md (Category 1)
**Time Estimate**: 8 hours
**Priority**: P0 BLOCKING
""",
        "priority": "P0",
        "time": "8h",
    },
    {
        "title": "Category 2: Apply Security to serve/routes.py (5 endpoints)",
        "prompt": """
**BLOCKING TASK - P0 LAUNCH BLOCKER**

Add authentication, authorization, rate limiting, and user isolation to 5 unprotected endpoints in serve/routes.py.

**Endpoints to Secure**:

1. POST /generate-dream/ (6 tests)
2. POST /glyph-feedback/ (6 tests)
3. POST /tier-auth/ (6 tests)
4. POST /plugin-load/ (7 tests - privileged operation)
5. GET /memory-dump/ (6 tests)

**Security Pattern for Each Endpoint**:

```python
@router.post("/endpoint/", response_model=ResponseModel)
@limiter.limit("50/minute")  # Rate limiting
@lukhas_tier_required(TierLevel.AUTHENTICATED, PermissionScope.RESOURCE_CREATE)
async def endpoint_handler(
    req: RequestModel,
    current_user: dict = Depends(get_current_user)  # ✅ Authentication
) -> ResponseModel:
    user_id = current_user["user_id"]  # ✅ From auth, NOT request

    # User-scoped operation
    result = await service.perform_operation(user_id=user_id, data=req.data)

    # Audit log
    audit_log_operation("operation_name", user_id, {"result_id": result.id})

    return result
```

**Special Case - plugin-load** (privileged operation):
- Requires TierLevel.PRIVILEGED or ADMIN
- Rate limit: 10/minute (lower for admin ops)
- Extra validation: Check tier >= PRIVILEGED.value

**Tests Required** (31 total):
Each endpoint needs 6 tests (plugin-load needs 7):
- test_success_authenticated (200)
- test_401_no_auth (401)
- test_403_insufficient_tier (403)
- test_403_cross_user (403)
- test_429_rate_limited (429)
- test_422_validation (422)
- (plugin-load only) test_403_requires_privileged_tier (403)

**Files to Modify**:
- `serve/routes.py`
- Create: `tests/unit/api/test_serve_routes_security.py`

**Success Criteria**:
- [ ] All 5 endpoints require authentication
- [ ] All 5 endpoints have tier requirements
- [ ] All 5 endpoints have rate limiting
- [ ] All 5 endpoints use user-scoped queries
- [ ] All 5 endpoints have audit logging
- [ ] All 31 security tests passing
- [ ] Test coverage ≥80% for serve/routes.py
- [ ] No user_id in request bodies (extracted from auth only)

**Reference**: docs/tasks/SECURITY_HARDENING_TASKS_2025-11-10.md (Category 2)
**Related**: PR #1268 has 39 functional tests but 0 security tests
**Time Estimate**: 12 hours
**Priority**: P0 BLOCKING
""",
        "priority": "P0",
        "time": "12h",
    },
    {
        "title": "Category 3: Apply Security to serve/openai_routes.py Legacy Endpoints",
        "prompt": """
**BLOCKING TASK - P0 LAUNCH BLOCKER**

Add authentication to 3 legacy OpenAI endpoints that currently have NO security.

**Endpoints to Secure**:

1. POST /openai/chat (6 tests)
2. POST /openai/chat/stream (6 tests)
3. GET /openai/metrics (4 tests - may keep public with rate limiting)

**Good News**:
- ✅ 3 v1 endpoints ALREADY have auth (/v1/models, /v1/embeddings, /v1/responses)
- ✅ `require_api_key()` helper already exists (serve/openai_routes.py:137)
- ✅ Just need to apply `Depends(require_api_key)` to legacy endpoints

**Implementation**:

```python
# Apply to POST /openai/chat and POST /openai/chat/stream
@router.post("/openai/chat")
@limiter.limit("50/minute")
async def chat_endpoint(
    request: ChatRequest,
    api_key: str = Depends(require_api_key)  # ✅ Add this
):
    # Existing implementation
    pass

# For GET /openai/metrics - decision needed
@router.get("/openai/metrics")
@limiter.limit("10/minute")  # May keep public but rate limited
async def metrics_endpoint():
    # Existing implementation - consider if auth needed
    pass
```

**Tests Required** (16 total):
- POST /openai/chat (6 tests): success, 401, 403, cross-user, 429, 422
- POST /openai/chat/stream (6 tests): success, 401, 403, cross-user, 429, 422
- GET /openai/metrics (4 tests): success, 429, validation (may skip 401/403/cross-user if public)

**Files to Modify**:
- `serve/openai_routes.py`
- Create: `tests/unit/api/test_openai_routes_security.py`

**Success Criteria**:
- [ ] All 3 legacy endpoints have authentication (or explicit public decision for metrics)
- [ ] All 16 security tests passing
- [ ] Rate limiting applied (50/min for chat, 10/min for metrics)
- [ ] Tests verify PolicyGuard integration
- [ ] No mocked authentication in tests (real auth flow)

**Reference**: docs/tasks/SECURITY_HARDENING_TASKS_2025-11-10.md (Category 3)
**Related**: PR #1267 has 46 functional tests but authentication completely mocked
**Time Estimate**: 6 hours
**Priority**: P0 BLOCKING
""",
        "priority": "P0",
        "time": "6h",
    },
    {
        "title": "Category 4: Implement Skipped Security Tests (24 tests)",
        "prompt": """
**BLOCKING TASK - P0 LAUNCH BLOCKER**

Implement 24 skipped tests in tests/unit/api/test_dreams_api_security.py.

**Current State**:
- ✅ Test skeleton exists (24 tests)
- ❌ All tests are `pytest.skip("Requires security controls implementation")`

**Endpoints Covered** (4 endpoints × 6 tests each):
1. POST /api/v1/dreams/simulate (6 tests)
2. POST /api/v1/dreams/mesh (6 tests)
3. GET /api/v1/dreams/{dream_id}/status (6 tests)
4. GET /api/v1/dreams/health (6 tests)

**Pattern for Converting Skipped Tests**:

BEFORE:
def test_simulate_success_with_auth(self, mock_authenticated_user):
    # 1. Success: Authenticated user can simulate dream
    pytest.skip("Requires security controls implementation")

AFTER:
def test_simulate_success_with_auth(self, mock_authenticated_user):
    # 1. Success: Authenticated user can simulate dream
    with patch("lukhas_website.lukhas.api.auth_helpers.get_current_user", return_value=mock_authenticated_user):
        response = client.post(
            "/api/v1/dreams/simulate",
            headers={"Authorization": "Bearer test_token"},
            json={"symbols": ["TRUST", "LEARN"], "depth": 2}
        )

    assert response.status_code == 200
    assert "dream_id" in response.json()
    assert response.json()["user_id"] == "user_test_123"

**Tests to Implement** (6 types per endpoint):
1. Success (200) - Authenticated user can access endpoint
2. Unauthorized (401) - Missing token returns 401
3. Forbidden (403) - Insufficient tier returns 403
4. Cross-user (403) - Cannot access other user's resources
5. Rate limited (429) - Exceeds rate limit returns 429
6. Validation (422) - Invalid payload returns 422

**Files to Modify**:
- `tests/unit/api/test_dreams_api_security.py`

**Implementation Notes**:
- Use auth_helpers (`get_current_user`, `lukhas_tier_required`)
- Verify JWT claims extraction
- Verify audit logging (check that user_id appears in logs)
- Use fixtures for mock users, tokens, auth headers

**Success Criteria**:
- [ ] All 24 tests implemented (no more pytest.skip)
- [ ] All tests passing
- [ ] Tests use auth_helpers
- [ ] Tests verify JWT claims extraction
- [ ] Tests verify audit logging

**Reference**: docs/tasks/SECURITY_HARDENING_TASKS_2025-11-10.md (Category 4)
**Time Estimate**: 4 hours
**Priority**: P0 BLOCKING
""",
        "priority": "P0",
        "time": "4h",
    },
    {
        "title": "Category 5: Memory Subsystem User Isolation (16h, 20 tests)",
        "prompt": """
**BLOCKING TASK - P0 LAUNCH BLOCKER**

Add user_id column to memory tables and update all memory operations for user isolation.

**Database Changes**:

1. Add user_id column to 3 memory tables:
   - `memory_folds`
   - `memory_events`
   - `memory_traces`

2. Create migration script:
```sql
ALTER TABLE memory_folds ADD COLUMN user_id VARCHAR(255) NOT NULL DEFAULT 'system';
CREATE INDEX idx_memory_folds_user_id ON memory_folds(user_id);

ALTER TABLE memory_events ADD COLUMN user_id VARCHAR(255) NOT NULL DEFAULT 'system';
CREATE INDEX idx_memory_events_user_id ON memory_events(user_id);

ALTER TABLE memory_traces ADD COLUMN user_id VARCHAR(255) NOT NULL DEFAULT 'system';
CREATE INDEX idx_memory_traces_user_id ON memory_traces(user_id);
```

**Code Changes**:

Update FoldManager and memory services to scope all queries by user_id:

```python
# BEFORE (INSECURE)
class FoldManager:
    async def get_fold(self, fold_id: str):
        return await db.query("SELECT * FROM memory_folds WHERE id = ?", fold_id)

# AFTER (SECURE)
class FoldManager:
    async def get_fold(self, fold_id: str, user_id: str):
        # ✅ User isolation
        return await db.query(
            "SELECT * FROM memory_folds WHERE id = ? AND user_id = ?",
            fold_id, user_id
        )
```

**Files to Modify/Create**:
- Create migration: `database/migrations/add_user_id_to_memory_tables.sql`
- Modify: `memory/fold_manager.py`
- Modify: `memory/event_store.py`
- Modify: `memory/trace_service.py`
- Create tests: `tests/unit/memory/test_user_isolation.py`

**Tests Required** (20 tests):
- User A can create fold
- User A can read own fold
- User A cannot read User B's fold
- User A can update own fold
- User A cannot update User B's fold
- User A can delete own fold
- User A cannot delete User B's fold
- Fold listing scoped to user
- Event logging includes user_id
- Trace retrieval scoped to user
- Cross-user access attempts logged
- Memory queries include user_id filter
- ... (8 more cross-user isolation tests)

**Success Criteria**:
- [ ] user_id column added to all memory tables
- [ ] Migration script created and tested
- [ ] All memory operations scoped by user_id
- [ ] All 20 user isolation tests passing
- [ ] No memory leaks between users
- [ ] Performance impact < 10ms (indexed queries)

**Reference**: docs/tasks/SECURITY_HARDENING_TASKS_2025-11-10.md (Category 5)
**Time Estimate**: 16 hours
**Priority**: P0 BLOCKING
""",
        "priority": "P0",
        "time": "16h",
    },
    {
        "title": "Category 6: Dream & Consciousness User Isolation (12h, 30 tests)",
        "prompt": """
**BLOCKING TASK - P0 LAUNCH BLOCKER**

Update dream generation and consciousness operations to use user-scoped memory.

**Changes Required**:

1. Update dream generation to accept user_id:
```python
# BEFORE
async def generate_dream(symbols: list[str], depth: int):
    memory = await memory_manager.get_active_memories()  # ❌ All users

# AFTER
async def generate_dream(user_id: str, symbols: list[str], depth: int):
    memory = await memory_manager.get_active_memories(user_id=user_id)  # ✅ User-scoped
```

2. Update consciousness engine to scope by user:
```python
# BEFORE
class ConsciousnessEngine:
    async def process(self, input_data):
        context = await self.memory.get_context()  # ❌ All users

# AFTER
class ConsciousnessEngine:
    async def process(self, user_id: str, input_data):
        context = await self.memory.get_context(user_id=user_id)  # ✅ User-scoped
```

**Files to Modify**:
- `lukhas_website/lukhas/dream/__init__.py`
- `consciousness/unified/auto_consciousness.py`
- All dream service modules
- All consciousness service modules

**Tests Required** (30 tests):
- `tests/unit/dream/test_user_isolation.py` (15 tests)
  - User A can generate dream
  - User A's dream uses only User A's memory
  - User A cannot access User B's dreams
  - Dream results scoped to user
  - Dream history scoped to user
  - Cross-user dream access blocked
  - Dream symbols from user-specific memory
  - ... (8 more tests)

- `tests/unit/consciousness/test_user_isolation.py` (15 tests)
  - User A's consciousness processing uses User A's memory
  - User A cannot access User B's consciousness state
  - Awareness snapshots scoped to user
  - Creativity operations scoped to user
  - Reflection reports scoped to user
  - Cross-user consciousness access blocked
  - ... (9 more tests)

**Success Criteria**:
- [ ] All dream operations require user_id
- [ ] All consciousness operations require user_id
- [ ] All 30 user isolation tests passing
- [ ] Cross-user memory access prevented
- [ ] Audit logs include user_id

**Reference**: docs/tasks/SECURITY_HARDENING_TASKS_2025-11-10.md (Category 6)
**Time Estimate**: 12 hours
**Priority**: P0 BLOCKING
""",
        "priority": "P0",
        "time": "12h",
    },
]


async def create_sessions():
    """Create Jules sessions for all security hardening tasks."""

    async with JulesClient() as jules:
        source_id = "sources/github/LukhasAI/Lukhas"

        print(f"Creating {len(SECURITY_TASKS)} Jules sessions for security hardening...\n")

        for idx, task in enumerate(SECURITY_TASKS, 1):
            print(f"[{idx}/{len(SECURITY_TASKS)}] Creating session: {task['title']}")
            print(f"  Priority: {task['priority']} | Time: {task['time']}")

            try:
                session = await jules.create_session(
                    prompt=task["prompt"],
                    source_id=source_id,
                    automation_mode="AUTO_CREATE_PR",  # Auto-create PRs
                )

                session_id = session.get("id", "unknown")
                session_url = f"https://jules.google.com/session/{session_id}"

                print(f"  ✅ Created: {session_url}\n")

            except Exception as e:
                print(f"  ❌ Failed: {e}\n")
                continue

        print("\n" + "="*70)
        print("✅ All security hardening sessions created!")
        print("="*70)
        print("\nNext steps:")
        print("1. Check session status: python3 scripts/list_all_jules_sessions.py")
        print("2. Approve plans when ready")
        print("3. Monitor PRs as they're created")


if __name__ == "__main__":
    asyncio.run(create_sessions())
