# Security Hardening Tasks - Missing Tests & Implementation

**Date**: 2025-11-10
**Context**: Based on PR Safety Review and User ID Integration Audit (55/100)
**Goal**: Achieve 90+/100 security score across all API endpoints

---

## Executive Summary

**Current State**:
- ✅ Security helpers created (`lukhas_website/lukhas/api/auth_helpers.py`)
- ✅ Security ADR created (`docs/adr/ADR-001-api-security-hardening-approach.md`)
- ✅ Test skeleton created (`tests/unit/api/test_dreams_api_security.py` - 24 tests, all skipped)
- ⏳ Authentication infrastructure exists (ΛiD, 6-tier system) but NOT ENFORCED
- ❌ 0/20 production endpoints have all 6 security test types
- ❌ serve/routes.py: 5 endpoints with NO authentication
- ❌ serve/openai_routes.py: 3 legacy endpoints with NO authentication

**Target State**:
- ✅ All endpoints require authentication (`Depends(get_current_user)`)
- ✅ All endpoints have authorization (`@lukhas_tier_required`)
- ✅ All endpoints have rate limiting (`@limiter.limit()`)
- ✅ All endpoints have user isolation (user-scoped queries)
- ✅ All endpoints have audit logging (with user_id)
- ✅ All endpoints have 6 security test types (success, 401, 403, cross-user, 429, 422)

---

## Task Categories

### Category 1: StrictAuthMiddleware (BLOCKING - 8 hours)

**Status**: ⏳ **NOT STARTED**
**Priority**: 🔴 **P0 - LAUNCH BLOCKER**
**Estimated Time**: 8 hours

**Description**: Create middleware that validates JWT tokens and attaches user context to all requests.

**Files to Create**:
- `lukhas_website/lukhas/api/middleware/strict_auth.py`

**Implementation**:
```python
class StrictAuthMiddleware:
    """
    Validate JWT tokens and attach user context to request.state.

    For all /v1/* and /api/* paths:
    - Verify Bearer token is present
    - Validate JWT signature
    - Extract user_id, tier, permissions
    - Attach to request.state (user_id, user_tier, user_permissions)
    - Reject with 401 if invalid/missing
    """
    async def __call__(self, request: Request, call_next):
        # Skip health endpoints
        if request.url.path in ["/healthz", "/health", "/readyz", "/metrics"]:
            return await call_next(request)

        # Protected paths
        if request.url.path.startswith(("/v1/", "/api/")):
            token = request.headers.get("Authorization")

            if not token or not token.startswith("Bearer "):
                raise HTTPException(status_code=401, detail="Missing or invalid Bearer token")

            # Validate JWT and extract claims
            claims = validate_jwt_token(token.replace("Bearer ", ""))

            # Attach to request state
            request.state.user_id = claims["sub"]
            request.state.user_tier = claims.get("tier", 0)
            request.state.user_permissions = claims.get("permissions", [])

        return await call_next(request)
```

**Tests Required**:
- `tests/unit/api/middleware/test_strict_auth.py` (12 tests)
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

**Acceptance Criteria**:
- [ ] Middleware created and tested
- [ ] Applied to FastAPI app (serve/main.py)
- [ ] All 12 tests passing
- [ ] JWT validation uses production-safe crypto
- [ ] No hardcoded secrets

**Related**:
- User ID Integration Audit: "Missing middleware that attaches user_id to request.state"
- ADR-001: Phase 1 requirement

---

### Category 2: Apply Security to serve/routes.py (BLOCKING - 12 hours)

**Status**: ⏳ **NOT STARTED**
**Priority**: 🔴 **P0 - LAUNCH BLOCKER**
**Estimated Time**: 12 hours (2-3 hours per endpoint)

**Description**: Add authentication, authorization, and user isolation to 5 unprotected endpoints.

**Endpoints to Secure** (5 total):

#### 2.1. POST /generate-dream/
**Current**: ❌ No authentication
**Required**:
```python
@router.post("/generate-dream/", response_model=DreamResponse)
@limiter.limit("50/minute")  # Rate limiting
@lukhas_tier_required(TierLevel.AUTHENTICATED, PermissionScope.RESOURCE_CREATE)
async def generate_dream(
    req: DreamRequest,
    current_user: dict = Depends(get_current_user)  # ✅ Authentication
) -> DreamResponse:
    user_id = current_user["user_id"]  # ✅ From auth, NOT request

    # User-scoped operation
    dream_result = await dream_service.generate(user_id=user_id, symbols=req.symbols)

    # Audit log
    audit_log_operation("dream_generate", user_id, {"dream_id": dream_result.id})

    return dream_result
```

**Tests Required** (6 tests):
- `test_generate_dream_success_authenticated` - Valid user can generate dream
- `test_generate_dream_401_no_auth` - Missing token returns 401
- `test_generate_dream_403_insufficient_tier` - PUBLIC tier rejected
- `test_generate_dream_403_cross_user` - Cannot access other user's dreams
- `test_generate_dream_429_rate_limited` - Exceeds 50/min limit
- `test_generate_dream_422_validation` - Invalid symbols format

#### 2.2. POST /glyph-feedback/
**Current**: ❌ No authentication
**Required**: Same security pattern as 2.1
**Tests Required**: 6 tests (same types)

#### 2.3. POST /tier-auth/
**Current**: ❌ No authentication (ironic - auth endpoint has no auth!)
**Required**: Same security pattern as 2.1
**Tests Required**: 6 tests (same types)

#### 2.4. POST /plugin-load/
**Current**: ❌ No authentication
**Required**: Higher tier required (PRIVILEGED or ADMIN)
```python
@router.post("/plugin-load/", response_model=PluginLoadResponse)
@limiter.limit("10/minute")  # Lower limit for admin operations
@lukhas_tier_required(TierLevel.PRIVILEGED, PermissionScope.SYSTEM_CONFIG)
async def plugin_load(
    req: PluginLoadRequest,
    current_user: dict = Depends(get_current_user)
) -> PluginLoadResponse:
    # Plugin loading is privileged operation
    user_id = current_user["user_id"]

    # Check tier is PRIVILEGED or ADMIN
    if current_user["tier"] < TierLevel.PRIVILEGED.value:
        raise HTTPException(status_code=403, detail="Privileged access required")

    # ... rest of implementation
```
**Tests Required**: 6 tests + 1 extra for tier validation

#### 2.5. GET /memory-dump/
**Current**: ❌ No authentication
**Required**: Same security pattern + user-scoped memory retrieval
**Tests Required**: 6 tests (same types)

**Total for Category 2**:
- Endpoints secured: 5
- Tests to write: 31 (6 × 5 + 1 extra for plugin-load)
- Estimated time: 12 hours

**Acceptance Criteria**:
- [ ] All 5 endpoints require authentication
- [ ] All 5 endpoints have tier requirements
- [ ] All 5 endpoints have rate limiting
- [ ] All 5 endpoints use user-scoped queries
- [ ] All 5 endpoints have audit logging
- [ ] All 31 security tests passing
- [ ] Test coverage ≥80% for serve/routes.py
- [ ] No user_id in request bodies (extracted from auth only)

**Related**:
- PR #1268: 39 functional tests exist, 0 security tests
- PR Safety Review: "Missing all 6 mandatory test types"

---

### Category 3: Apply Security to serve/openai_routes.py Legacy Endpoints (BLOCKING - 6 hours)

**Status**: ⏳ **NOT STARTED**
**Priority**: 🔴 **P0 - LAUNCH BLOCKER**
**Estimated Time**: 6 hours

**Description**: Add authentication to 3 legacy OpenAI endpoints that currently have NO security.

**Endpoints to Secure** (3 total):

#### 3.1. POST /openai/chat
**Current**: ❌ No authentication
**Required**: Add `Depends(require_api_key)` (already exists but NOT USED)
**Tests Required**: 6 tests

#### 3.2. POST /openai/chat/stream
**Current**: ❌ No authentication
**Required**: Add `Depends(require_api_key)`
**Tests Required**: 6 tests

#### 3.3. GET /openai/metrics
**Current**: ❌ No authentication
**Required**: Add `Depends(require_api_key)` or keep public but add rate limiting
**Tests Required**: 4 tests (may keep public, so no 401/403/cross-user needed)

**Total for Category 3**:
- Endpoints secured: 3
- Tests to write: 16 tests
- Estimated time: 6 hours

**Good News**:
- ✅ 3 v1 endpoints ALREADY have authentication (`/v1/models`, `/v1/embeddings`, `/v1/responses`)
- ✅ `require_api_key()` helper already exists (serve/openai_routes.py:137)
- ✅ Just need to apply `Depends(require_api_key)` to legacy endpoints

**Acceptance Criteria**:
- [ ] All 3 legacy endpoints have authentication
- [ ] All 16 security tests passing
- [ ] Rate limiting applied (50/min for chat, 10/min for metrics)
- [ ] Tests verify PolicyGuard integration

**Related**:
- PR #1267: 46 functional tests exist, authentication completely mocked
- PR Safety Review: "Authentication is completely mocked (line 66)"

---

### Category 4: Implement Skipped Security Tests (BLOCKING - 4 hours)

**Status**: ⏳ **NOT STARTED**
**Priority**: 🔴 **P0 - LAUNCH BLOCKER**
**Estimated Time**: 4 hours

**Description**: Implement the 24 skipped tests in `tests/unit/api/test_dreams_api_security.py`.

**Files to Update**:
- `tests/unit/api/test_dreams_api_security.py`

**Current State**:
- ✅ Test skeleton exists (24 tests)
- ❌ All tests are `pytest.skip("Requires security controls implementation")`

**Implementation Required**:
```python
# Example: Convert skipped test to real test
def test_simulate_success_with_auth(self, mock_authenticated_user):
    """1. Success: Authenticated user can simulate dream"""
    # BEFORE: pytest.skip("Requires security controls implementation")

    # AFTER:
    with patch("lukhas_website.lukhas.api.auth_helpers.get_current_user", return_value=mock_authenticated_user):
        response = client.post(
            "/api/v1/dreams/simulate",
            headers={"Authorization": "Bearer test_token"},
            json={"symbols": ["TRUST", "LEARN"], "depth": 2}
        )

    assert response.status_code == 200
    assert "dream_id" in response.json()
    assert response.json()["user_id"] == "user_test_123"
```

**Tests to Implement** (24 total):
- POST /api/v1/dreams/simulate (6 tests)
- POST /api/v1/dreams/mesh (6 tests)
- GET /api/v1/dreams/{dream_id}/status (6 tests)
- GET /api/v1/dreams/health (6 tests)

**Acceptance Criteria**:
- [ ] All 24 tests implemented (no more skips)
- [ ] All tests passing
- [ ] Tests use auth_helpers (`get_current_user`, `lukhas_tier_required`)
- [ ] Tests verify JWT claims extraction
- [ ] Tests verify audit logging

**Related**:
- ADR-001: Phase 1 deliverable
- PR Safety Review: "Test skeleton created"

---

### Category 5: Memory Subsystem User Isolation (BLOCKING - 16 hours)

**Status**: ⏳ **NOT STARTED**
**Priority**: 🔴 **P0 - LAUNCH BLOCKER**
**Estimated Time**: 16 hours

**Description**: Add user_id column to memory tables and update all memory operations for user isolation.

**Database Changes**:
1. Add `user_id` column to memory tables:
   - `memory_folds` (user_id, indexed)
   - `memory_events` (user_id, indexed)
   - `memory_traces` (user_id, indexed)

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
- Update FoldManager to scope queries by user_id
- Update memory service to require user_id in all operations
- Update dream generation to use user-scoped memory
- Update consciousness operations to use user-scoped memory

**Example**:
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

**Tests Required**:
- `tests/unit/memory/test_user_isolation.py` (20 tests)
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
  - ... (10 more cross-user tests)

**Acceptance Criteria**:
- [ ] user_id column added to all memory tables
- [ ] Migration script created and tested
- [ ] All memory operations scoped by user_id
- [ ] All 20 user isolation tests passing
- [ ] No memory leaks between users
- [ ] Performance impact < 10ms (indexed queries)

**Related**:
- User ID Integration Audit: "Memory operations lack user-level isolation"
- Phase 2 requirement (Week 2)

---

### Category 6: Dream & Consciousness User Isolation (BLOCKING - 12 hours)

**Status**: ⏳ **NOT STARTED**
**Priority**: 🔴 **P0 - LAUNCH BLOCKER**
**Estimated Time**: 12 hours

**Description**: Update dream generation and consciousness operations to use user-scoped memory.

**Files to Update**:
- `lukhas_website/lukhas/dream/__init__.py`
- `consciousness/unified/auto_consciousness.py`
- All dream-related service modules

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

**Tests Required**:
- `tests/unit/dream/test_user_isolation.py` (15 tests)
- `tests/unit/consciousness/test_user_isolation.py` (15 tests)

**Acceptance Criteria**:
- [ ] All dream operations require user_id
- [ ] All consciousness operations require user_id
- [ ] All 30 user isolation tests passing
- [ ] Cross-user memory access prevented
- [ ] Audit logs include user_id

**Related**:
- User ID Integration Audit: "Update dream/consciousness operations"
- Phase 2 requirement (Week 2)

---

### Category 7: Rate Limiting Infrastructure (Recommended - 8 hours)

**Status**: ⏳ **NOT STARTED**
**Priority**: 🟠 **P1 - RECOMMENDED**
**Estimated Time**: 8 hours

**Description**: Implement tier-based rate limiting using slowapi + Redis.

**Infrastructure Required**:
- Redis backend for distributed rate limiting
- slowapi integration with FastAPI

**Configuration**:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware

# Tier-based limits
TIER_LIMITS = {
    TierLevel.PUBLIC: "10/minute",
    TierLevel.AUTHENTICATED: "50/minute",
    TierLevel.ELEVATED: "200/minute",
    TierLevel.PRIVILEGED: "500/minute",
    TierLevel.ADMIN: "1000/minute",
    TierLevel.SYSTEM: "unlimited",
}

def get_user_limit(request: Request) -> str:
    """Get rate limit based on user tier"""
    if hasattr(request.state, "user_tier"):
        tier = TierLevel(request.state.user_tier)
        return TIER_LIMITS[tier]
    return TIER_LIMITS[TierLevel.PUBLIC]

limiter = Limiter(key_func=get_user_limit)
app.add_middleware(SlowAPIMiddleware)
```

**Tests Required**:
- `tests/unit/api/test_rate_limiting.py` (12 tests)
  - PUBLIC tier limited to 10/min
  - AUTHENTICATED tier limited to 50/min
  - Rate limit resets after 60 seconds
  - 429 response includes Retry-After header
  - Rate limit per-user (not per-IP)
  - Rate limit enforced across distributed instances (Redis)
  - ... (6 more tests)

**Acceptance Criteria**:
- [ ] Redis backend configured
- [ ] slowapi integrated
- [ ] Tier-based limits applied
- [ ] All 12 tests passing
- [ ] 429 responses include Retry-After header
- [ ] Rate limiting works in distributed environment

**Related**:
- User ID Integration Audit: "Rate limiting infrastructure exists but not enforced"
- Phase 3 requirement (Week 3)

---

### Category 8: Feature Flags for User Context (Recommended - 6 hours)

**Status**: ⏳ **NOT STARTED**
**Priority**: 🟠 **P1 - RECOMMENDED**
**Estimated Time**: 6 hours

**Description**: Implement user-context feature flag system for gradual rollout.

**Implementation**:
```python
class FeatureFlagManager:
    """User-context feature flag system"""

    async def is_enabled(self, feature: str, user_id: str, user_tier: int) -> bool:
        """
        Check if feature is enabled for user.

        Checks (in order):
        1. Global killswitch (feature disabled for all)
        2. Tier-based access (feature requires min tier)
        3. User allowlist (specific users enabled)
        4. Percentage rollout (gradual rollout)
        """
        # Global killswitch
        if await self.config.get(f"features.{feature}.disabled"):
            return False

        # Tier requirement
        min_tier = await self.config.get(f"features.{feature}.min_tier", 0)
        if user_tier < min_tier:
            return False

        # User allowlist
        allowlist = await self.config.get(f"features.{feature}.allowlist", [])
        if user_id in allowlist:
            return True

        # Percentage rollout
        percentage = await self.config.get(f"features.{feature}.percentage", 0)
        if percentage >= 100:
            return True

        # Hash user_id to deterministic bucket
        user_hash = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
        bucket = user_hash % 100
        return bucket < percentage
```

**Features to Flag**:
- `PARALLEL_DREAMS_ENABLED` (already exists)
- `CONSCIOUSNESS_ADAPTIVE_ENABLED`
- `QRG_GENERATION_ENABLED`
- `MESH_CONSENSUS_ENABLED`

**Tests Required**:
- `tests/unit/features/test_feature_flags.py` (15 tests)

**Acceptance Criteria**:
- [ ] FeatureFlagManager implemented
- [ ] Config stored in Redis or database
- [ ] All 15 tests passing
- [ ] Feature flags used in routes
- [ ] Admin API for flag management

**Related**:
- User ID Integration Audit: "Feature flags with tier-based access"
- Phase 3 requirement (Week 3)

---

### Category 9: Monitoring & Audit Logging (Important - 12 hours)

**Status**: ⏳ **NOT STARTED**
**Priority**: 🟡 **P2 - IMPORTANT**
**Estimated Time**: 12 hours

**Description**: Implement comprehensive monitoring and audit logging for security events.

**Metrics to Track** (Prometheus):
```python
# Authentication metrics
auth_attempts_total = Counter("lukhas_auth_attempts_total", ["status", "tier"])
auth_failures_total = Counter("lukhas_auth_failures_total", ["reason"])
auth_latency_seconds = Histogram("lukhas_auth_latency_seconds")

# Authorization metrics
authz_checks_total = Counter("lukhas_authz_checks_total", ["endpoint", "tier", "result"])
authz_failures_total = Counter("lukhas_authz_failures_total", ["endpoint", "reason"])

# Rate limiting metrics
rate_limit_hits_total = Counter("lukhas_rate_limit_hits_total", ["endpoint", "tier"])
rate_limit_exceeded_total = Counter("lukhas_rate_limit_exceeded_total", ["endpoint", "tier"])

# Security incidents
security_incidents_total = Counter("lukhas_security_incidents_total", ["type", "severity"])
```

**Audit Log Events**:
- Authentication success/failure
- Authorization grant/denial
- Tier elevation attempts
- Cross-user access attempts
- Rate limit exceedances
- Feature flag checks
- Sensitive operation logs

**Audit Log Format**:
```json
{
  "timestamp": "2025-11-10T15:50:00Z",
  "event_type": "authorization_denied",
  "user_id": "user_test_123",
  "user_tier": 1,
  "endpoint": "/api/v1/dreams/simulate",
  "required_tier": 2,
  "reason": "insufficient_tier",
  "request_id": "req_abc123",
  "ip_address": "192.168.1.1"
}
```

**Dashboards to Create** (Grafana):
1. Authentication Overview
   - Successful/failed auth attempts
   - Auth latency (p50, p95, p99)
   - Failed auth by reason
2. Authorization Overview
   - Authz checks by endpoint
   - Authz denials by reason
   - Cross-user access attempts
3. Rate Limiting Overview
   - Rate limit hits by tier
   - Rate limit exceedances by endpoint
   - Top rate-limited users
4. Security Incidents
   - Incidents by type (auth failure, authz denial, rate limit)
   - Incidents by severity (low, medium, high, critical)
   - Top 10 suspicious users

**Alerts to Configure** (AlertManager):
```yaml
groups:
  - name: lukhas_security
    rules:
      - alert: HighAuthFailureRate
        expr: rate(lukhas_auth_failures_total[5m]) > 10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High authentication failure rate"

      - alert: CrossUserAccessAttempt
        expr: lukhas_security_incidents_total{type="cross_user_access"} > 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Cross-user access attempt detected"

      - alert: RateLimitExceededPersistent
        expr: rate(lukhas_rate_limit_exceeded_total[10m]) > 5
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Persistent rate limit exceedances"
```

**Tests Required**:
- `tests/unit/monitoring/test_security_metrics.py` (15 tests)
- `tests/unit/monitoring/test_audit_logs.py` (10 tests)

**Acceptance Criteria**:
- [ ] All Prometheus metrics implemented
- [ ] Audit logging for all security events
- [ ] Grafana dashboards created
- [ ] AlertManager rules configured
- [ ] All 25 tests passing
- [ ] Audit logs sent to centralized logging (ELK/Loki)

**Related**:
- User ID Integration Audit: "Monitoring + audit logging"
- Phase 4 requirement (Week 4)

---

### Category 10: Compliance Reporting (Important - 6 hours)

**Status**: ⏳ **NOT STARTED**
**Priority**: 🟡 **P2 - IMPORTANT**
**Estimated Time**: 6 hours

**Description**: Generate GDPR/CCPA/SOC2 compliance reports from audit logs.

**Reports to Generate**:

1. **GDPR Data Access Report**:
   - All data stored for user
   - All operations performed by user
   - All third-party data shares (if any)

2. **GDPR Right to Erasure Report**:
   - Data deletion workflow
   - Confirmation of deletion
   - Residual data audit

3. **CCPA Data Collection Report**:
   - Categories of data collected
   - Purposes of data collection
   - Third parties with access

4. **SOC 2 Access Control Report**:
   - User access logs (who accessed what)
   - Authorization decisions
   - Failed access attempts
   - Tier elevations

**Implementation**:
```python
class ComplianceReporter:
    """Generate compliance reports from audit logs"""

    async def gdpr_data_access_report(self, user_id: str) -> dict:
        """GDPR Article 15: Right of access"""
        return {
            "user_id": user_id,
            "data_stored": await self.get_user_data(user_id),
            "operations": await self.get_user_operations(user_id),
            "third_parties": [],  # LUKHAS doesn't share data
            "generated_at": datetime.utcnow(),
        }

    async def gdpr_erasure_report(self, user_id: str) -> dict:
        """GDPR Article 17: Right to erasure"""
        deleted_data = await self.delete_user_data(user_id)
        residual_data = await self.audit_residual_data(user_id)

        return {
            "user_id": user_id,
            "deleted": deleted_data,
            "residual": residual_data,
            "deletion_confirmed": len(residual_data) == 0,
            "deleted_at": datetime.utcnow(),
        }
```

**Tests Required**:
- `tests/unit/compliance/test_gdpr_reports.py` (10 tests)
- `tests/unit/compliance/test_ccpa_reports.py` (5 tests)
- `tests/unit/compliance/test_soc2_reports.py` (5 tests)

**Acceptance Criteria**:
- [ ] ComplianceReporter implemented
- [ ] All 4 report types generated
- [ ] All 20 tests passing
- [ ] Reports exportable as PDF/JSON
- [ ] Automated generation on request

**Related**:
- User ID Integration Audit: "GDPR/CCPA compliance gaps"
- Phase 4 requirement (Week 4)

---

## Task Summary

| Category | Priority | Time | Tests | Status |
|----------|----------|------|-------|--------|
| 1. StrictAuthMiddleware | 🔴 P0 BLOCKING | 8h | 12 | ⏳ Not Started |
| 2. serve/routes.py Security | 🔴 P0 BLOCKING | 12h | 31 | ⏳ Not Started |
| 3. serve/openai_routes.py Security | 🔴 P0 BLOCKING | 6h | 16 | ⏳ Not Started |
| 4. Implement Skipped Tests | 🔴 P0 BLOCKING | 4h | 24 | ⏳ Not Started |
| 5. Memory User Isolation | 🔴 P0 BLOCKING | 16h | 20 | ⏳ Not Started |
| 6. Dream/Consciousness Isolation | 🔴 P0 BLOCKING | 12h | 30 | ⏳ Not Started |
| 7. Rate Limiting | 🟠 P1 RECOMMENDED | 8h | 12 | ⏳ Not Started |
| 8. Feature Flags | 🟠 P1 RECOMMENDED | 6h | 15 | ⏳ Not Started |
| 9. Monitoring & Audit Logging | 🟡 P2 IMPORTANT | 12h | 25 | ⏳ Not Started |
| 10. Compliance Reporting | 🟡 P2 IMPORTANT | 6h | 20 | ⏳ Not Started |
| **TOTAL** | - | **90 hours** | **205 tests** | - |

**Blocking Work** (Categories 1-6): **58 hours** (133 tests)
**Recommended Work** (Categories 7-8): **14 hours** (27 tests)
**Important Work** (Categories 9-10): **18 hours** (45 tests)

---

## Execution Plan

### Phase 1: BLOCKING (Week 1-2, 58 hours)

**Week 1 Focus** (28 hours):
1. Create StrictAuthMiddleware (8h) → 12 tests
2. Apply security to serve/routes.py (12h) → 31 tests
3. Apply security to serve/openai_routes.py (6h) → 16 tests
4. Implement skipped dreams security tests (2h) → 24 tests

**Milestone**: All API endpoints have authentication ✅

**Week 2 Focus** (30 hours):
5. Memory subsystem user isolation (16h) → 20 tests
6. Dream/consciousness user isolation (12h) → 30 tests
7. Integration testing (2h) → 10 tests

**Milestone**: User data isolation complete ✅

**Success Criteria**:
- ✅ Security score: 90+/100 (from 55/100)
- ✅ All 133 blocking tests passing
- ✅ Zero cross-user data access possible
- ✅ Production launch unblocked

### Phase 2: RECOMMENDED (Week 3, 14 hours)

7. Rate limiting infrastructure (8h) → 12 tests
8. Feature flags for user context (6h) → 15 tests

**Milestone**: Advanced security controls ✅

**Success Criteria**:
- ✅ Tier-based rate limiting enforced
- ✅ Gradual feature rollout possible
- ✅ All 27 recommended tests passing

### Phase 3: IMPORTANT (Week 4, 18 hours)

9. Monitoring & audit logging (12h) → 25 tests
10. Compliance reporting (6h) → 20 tests

**Milestone**: Production-ready observability ✅

**Success Criteria**:
- ✅ Grafana dashboards live
- ✅ AlertManager configured
- ✅ GDPR/CCPA reports generated
- ✅ All 45 important tests passing

---

## Testing Standards

**All new security tests MUST include**:

### 1. Success Test (200 OK)
```python
def test_endpoint_success_authenticated(client, auth_headers):
    response = client.post("/endpoint", headers=auth_headers, json=valid_payload)
    assert response.status_code == 200
    assert "expected_field" in response.json()
```

### 2. Unauthorized Test (401)
```python
def test_endpoint_401_no_auth(client):
    response = client.post("/endpoint", json=valid_payload)  # No auth header
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
```

### 3. Forbidden Test (403)
```python
def test_endpoint_403_insufficient_tier(client, low_tier_auth_headers):
    response = client.post("/endpoint", headers=low_tier_auth_headers, json=valid_payload)
    assert response.status_code == 403
    assert "Insufficient tier" in response.json()["detail"]
```

### 4. Cross-User Isolation Test (403)
```python
def test_endpoint_403_cross_user(client, user_a_auth, user_b_auth):
    # User A creates resource
    response_a = client.post("/endpoint", headers=user_a_auth, json={"data": "A"})
    resource_id = response_a.json()["id"]

    # User B cannot access User A's resource
    response_b = client.get(f"/endpoint/{resource_id}", headers=user_b_auth)
    assert response_b.status_code == 403
    assert "Cannot access other user's resources" in response_b.json()["detail"]
```

### 5. Rate Limiting Test (429)
```python
def test_endpoint_429_rate_limited(client, auth_headers):
    # Exceed rate limit
    for _ in range(51):  # Limit is 50/min
        client.post("/endpoint", headers=auth_headers, json=valid_payload)

    # Next request should be rate limited
    response = client.post("/endpoint", headers=auth_headers, json=valid_payload)
    assert response.status_code == 429
    assert "Retry-After" in response.headers
```

### 6. Validation Test (422)
```python
def test_endpoint_422_validation(client, auth_headers):
    response = client.post("/endpoint", headers=auth_headers, json=invalid_payload)
    assert response.status_code == 422
    assert "validation" in response.json()["detail"].lower()
```

---

## Code Review Checklist

**Before merging ANY security-related PR**:

- [ ] All endpoints have `Depends(get_current_user)`
- [ ] All endpoints have `@lukhas_tier_required` decorator
- [ ] All endpoints have `@limiter.limit()` decorator
- [ ] All data queries are user-scoped
- [ ] GET-by-ID endpoints validate ownership
- [ ] All operations have audit logging with user_id
- [ ] All 6 test types implemented for each endpoint
- [ ] OpenAPI docs include auth requirements
- [ ] No user_id in request bodies (from auth only)
- [ ] Python 3.9 compatibility (no 3.10+ syntax)
- [ ] No hardcoded secrets
- [ ] guard_patch passing
- [ ] All tests passing
- [ ] Coverage ≥80%

---

## Progress Tracking

**To mark a category complete**:
1. Create PR for the category
2. Run all tests: `pytest tests/unit/ -v`
3. Run guard_patch: `python3 tools/guard_patch.py`
4. Generate artifacts: junit.xml, coverage.xml, events.ndjson
5. Create Draft PR with `labot` label
6. Get human review
7. Merge when approved

**To track progress**:
```bash
# Run security test suite
pytest tests/unit/api/test_*_security.py -v

# Check coverage
pytest --cov=lukhas_website/lukhas/api --cov-report=term-missing

# Count implemented vs skipped tests
grep -r "pytest.skip" tests/unit/api/ | wc -l  # Should be 0 when done
```

---

## Related Documents

- [PR Safety Review](../audits/PR_SAFETY_REVIEW_2025-11-10.md) - Identified missing security tests
- [User ID Integration Audit](../audits/identity/USER_ID_INTEGRATION_AUDIT_2025-11-10.md) - 55/100 score, remediation plan
- [ΛiD Authentication Audit](../LAMBDA_ID_AUTHENTICATION_AUDIT.md) - 90/100 infrastructure score
- [ADR-001: API Security Hardening](../adr/ADR-001-api-security-hardening-approach.md) - Phased approach
- [CLAUDE_CODE_WEB_MASTER_PROMPT.md](../../CLAUDE_CODE_WEB_MASTER_PROMPT.md) - LUKHAS Test Surgeon rules
- [GPT5_PRO_REVIEW_PROMPT.md](../audits/GPT5_PRO_REVIEW_PROMPT.md) - Code review template

---

**Prepared by**: Claude Code (Sonnet 4.5)
**Date**: 2025-11-10
**Purpose**: Comprehensive task list for security hardening to achieve 90+/100 score
**Next Step**: Begin Phase 1, Category 1 (StrictAuthMiddleware)
