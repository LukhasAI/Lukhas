# GPT-5 Pro Audit Action Plan - 2025-11-10

## Executive Summary

Based on the **GPT-5 Pro Review: LUKHAS Pre-Launch Audit**, LUKHAS AI has **LAUNCH BLOCKER** status due to critical security gaps. This document provides a prioritized, actionable plan to achieve **Conditional GO for Launch** within 4 weeks.

**Current Status**:
- **User ID Integration**: 55/100 (LAUNCH BLOCKER)
- **Feedback System**: 70/100 (LAUNCH BLOCKER)
- **Endocrine System**: 65/100 (Safe to launch with limitations)

**Goal**: Achieve 90/100+ scores across all systems by implementing critical P0 fixes

---

## Timeline & Resource Allocation

**Duration**: 4 weeks (120 hours with 2-person team)
**Budget**:
- **Phase 1** (P0 - Authentication): 40 hours (must complete Week 1-2)
- **Phase 2** (P0 - Feedback Security): 56 hours (must complete Week 2-3)
- **Phase 3** (P1 - Compliance): 15 hours (Week 3-4)
- **Phase 4** (P2 - Endocrine): 35 hours (optional, can defer post-launch)

**Parallelization Strategy**:
- Week 1-2: Engineer A (Auth), Engineer B (Feedback backend design)
- Week 2-3: Reconverge for integration, rate limiting
- Week 3-4: Compliance, testing, optional endocrine improvements

---

## Phase 1: Authentication & Authorization (P0 - BLOCKING)

**Priority**: CRITICAL - LAUNCH BLOCKER
**Duration**: 40 hours (Week 1-2)
**Owner**: Engineer A (primary) + Engineer B (support)

### Tasks

#### 1.1 Enforce Authentication on ALL Endpoints

**Status**: Pending
**Effort**: 16 hours
**Blocker**: YES

**Implementation**:

```python
# lukhas/governance/middleware/strict_auth.py
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

class StrictAuthMiddleware(BaseHTTPMiddleware):
    """Enforce authentication on all routes except explicit allowlist."""

    ALLOWED_PATHS = {
        "/health",
        "/docs",
        "/openapi.json",
        "/api/v1/auth/login",
        "/api/v1/auth/register"
    }

    async def dispatch(self, request: Request, call_next):
        if request.url.path not in self.ALLOWED_PATHS:
            # Verify JWT token exists and is valid
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                raise HTTPException(status_code=401, detail="Authentication required")

            # Validate token (integrate with existing ΛiD system)
            token = auth_header.split(" ")[1]
            # Call existing token validation logic
            # ...

        response = await call_next(request)
        return response
```

**Steps**:
1. Create `StrictAuthMiddleware` in lukhas/governance/middleware/
2. Add to FastAPI app.add_middleware() in serve/main.py
3. Update ALLOWED_PATHS to include only public endpoints
4. Test all protected endpoints return 401 without token
5. Test all endpoints work with valid token

**Success Criteria**:
- ✅ All API endpoints require authentication
- ✅ No endpoint accepts requests without valid JWT
- ✅ 401 returned for missing/invalid tokens
- ✅ Test coverage: 100% of endpoints tested for auth

**Risk**: OWASP A01: Broken Access Control (CRITICAL)

---

#### 1.2 Remove Optional user_id - Derive from Auth Token Only

**Status**: Pending
**Effort**: 12 hours
**Blocker**: YES

**Current Problem**:
```python
# serve/feedback_routes.py (VULNERABLE)
class FeedbackRequest(BaseModel):
    user_id: Optional[str] = None  # ❌ Client can claim ANY user_id!
    rating: int
    comment: str

@router.post("/api/v1/feedback")
async def submit_feedback(request: FeedbackRequest):
    # Uses request.user_id without validation!
    # Attacker can submit feedback as any user
```

**Correct Implementation**:
```python
# serve/feedback_routes.py (SECURE)
from lukhas.governance.auth import get_current_user

class FeedbackRequest(BaseModel):
    # NO user_id field - derived from auth!
    rating: int
    comment: str

@router.post("/api/v1/feedback")
async def submit_feedback(
    request: FeedbackRequest,
    current_user: dict = Depends(get_current_user)  # Extract from JWT
):
    user_id = current_user["user_id"]  # From auth token, not request!
    # Now use this verified user_id for all operations
```

**Files to Update**:
1. `serve/feedback_routes.py` - Remove user_id from request models
2. `serve/consciousness_api.py` - Already done! ✅ (QueryRequest.user_id should be removed in future)
3. `serve/openai_routes.py` - Ensure chat completions use auth user_id
4. Any route with `user_id: Optional[str]` parameters

**Steps**:
1. Create `get_current_user()` dependency in lukhas/governance/auth.py
2. Remove all `user_id` fields from request Pydantic models
3. Add `current_user = Depends(get_current_user)` to all endpoints
4. Update all data operations to use `current_user["user_id"]`
5. Test: Verify cannot spoof user_id via request body

**Success Criteria**:
- ✅ No endpoint accepts user_id from client
- ✅ All user_id values derived from JWT token
- ✅ Cross-user access prevented (Test: User A cannot access User B's data)
- ✅ Admin routes have separate tier check

**Risk**: OWASP A01: Broken Access Control + Identity Spoofing (CRITICAL)

---

#### 1.3 Implement Per-User Data Isolation

**Status**: Pending
**Effort**: 12 hours
**Blocker**: YES

**Current Problem**:
```python
# memory/core.py (VULNERABLE)
async def get_memories():
    # Returns ALL memories from ALL users! ❌
    return await db.query("SELECT * FROM memories")
```

**Correct Implementation**:
```python
# memory/core.py (SECURE)
async def get_memories(user_id: str):
    # Returns ONLY this user's memories ✅
    return await db.query(
        "SELECT * FROM memories WHERE user_id = ?",
        user_id
    )

# Add user_id validation
async def create_memory(user_id: str, content: dict):
    # Verify user owns this data before creating
    return await db.execute(
        "INSERT INTO memories (user_id, content) VALUES (?, ?)",
        user_id, content
    )
```

**Database Schema Updates**:
```sql
-- Add user_id to all user data tables
ALTER TABLE memories ADD COLUMN user_id VARCHAR(255) NOT NULL;
ALTER TABLE dreams ADD COLUMN user_id VARCHAR(255) NOT NULL;
ALTER TABLE feedback ADD COLUMN user_id VARCHAR(255) NOT NULL;

-- Add indexes for performance
CREATE INDEX idx_memories_user_id ON memories(user_id);
CREATE INDEX idx_dreams_user_id ON dreams(user_id);
CREATE INDEX idx_feedback_user_id ON feedback(user_id);

-- Add unique constraints where needed
ALTER TABLE user_states ADD UNIQUE (user_id, state_key);
```

**Files to Update**:
1. `memory/core.py` - Add user_id filtering to all queries
2. `consciousness/dream.py` - Add user_id to dream operations
3. `serve/feedback_routes.py` - Ensure feedback tied to user_id
4. Database migration scripts

**Steps**:
1. Create database migration to add user_id columns
2. Update all data models to include user_id field
3. Update all queries to filter by user_id
4. Add ownership validation before updates/deletes
5. Test multi-user scenario: User A cannot see User B's data

**Success Criteria**:
- ✅ All user data tables have user_id column
- ✅ All queries filter by user_id
- ✅ Cross-user access tests fail (security validation)
- ✅ Performance: Indexed queries <100ms

**Risk**: OWASP A01: Broken Access Control + Privacy Violation (CRITICAL)

---

## Phase 2: Feedback System Security (P0 - BLOCKING)

**Priority**: CRITICAL - LAUNCH BLOCKER
**Duration**: 56 hours (Week 2-3)
**Owner**: Engineer B (primary) + Engineer A (auth integration)

### Tasks

#### 2.1 Secure Feedback Endpoints with Authentication

**Status**: Pending
**Effort**: 16 hours
**Blocker**: YES

**Current Problem**:
```python
# serve/feedback_routes.py (VULNERABLE)
@router.post("/api/v1/feedback")
async def submit_feedback(request: FeedbackRequest):
    # NO AUTHENTICATION! ❌
    # Anyone can submit feedback
    # Attacker can spam or poison data
```

**Correct Implementation**:
```python
# serve/feedback_routes.py (SECURE)
@router.post("/api/v1/feedback")
@rate_limit(max_calls=10, window_seconds=60)  # Add rate limiting
async def submit_feedback(
    request: FeedbackRequest,
    current_user: dict = Depends(get_current_user)  # Require auth ✅
):
    user_id = current_user["user_id"]
    # Store feedback with verified user_id
    return await feedback_service.store(user_id, request)
```

**Steps**:
1. Add `Depends(get_current_user)` to all feedback endpoints
2. Implement rate limiting decorator (see task 2.2)
3. Remove any public/unauthenticated feedback routes
4. Test: Verify 401 without auth, 429 when rate limited
5. Integration test: Authenticated user can submit feedback

**Success Criteria**:
- ✅ All feedback endpoints require authentication
- ✅ Rate limiting active (max 10 requests/minute per user)
- ✅ No unauthenticated feedback submission possible
- ✅ Spam attack test: Cannot flood system with requests

**Risk**: Data Poisoning + DoS Attack (CRITICAL)

---

#### 2.2 Implement Rate Limiting

**Status**: Pending
**Effort**: 20 hours
**Blocker**: YES

**Implementation**:
```python
# lukhas/governance/ratelimit.py
from fastapi import HTTPException, Request
from functools import wraps
import time
from collections import defaultdict

class RateLimiter:
    """
    Rate limiter using sliding window algorithm.
    Tracks requests per user_id (authenticated) or IP (fallback).
    """
    def __init__(self):
        self.requests = defaultdict(list)  # {user_id: [timestamp1, timestamp2, ...]}

    def is_allowed(self, key: str, max_calls: int, window_seconds: int) -> bool:
        now = time.time()
        window_start = now - window_seconds

        # Remove old requests outside window
        self.requests[key] = [
            ts for ts in self.requests[key]
            if ts > window_start
        ]

        # Check if under limit
        if len(self.requests[key]) >= max_calls:
            return False

        # Record this request
        self.requests[key].append(now)
        return True

rate_limiter = RateLimiter()

def rate_limit(max_calls: int = 60, window_seconds: int = 60):
    """
    Rate limit decorator for FastAPI routes.
    Usage: @rate_limit(max_calls=10, window_seconds=60)
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(
            *args,
            request: Request,
            current_user: dict = None,
            **kwargs
        ):
            # Use user_id if authenticated, otherwise IP
            key = current_user.get("user_id") if current_user else request.client.host

            if not rate_limiter.is_allowed(key, max_calls, window_seconds):
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded: {max_calls} requests per {window_seconds}s"
                )

            return await func(*args, request=request, current_user=current_user, **kwargs)
        return wrapper
    return decorator
```

**Endpoints to Rate Limit**:
1. `/api/v1/auth/login` - 5 attempts/minute (prevent brute force)
2. `/api/v1/feedback` - 10 requests/minute (prevent spam)
3. `/api/v1/consciousness/query` - 60 requests/minute (prevent abuse)
4. `/api/v1/consciousness/dream` - 20 requests/minute (expensive operation)
5. `/api/v1/memory/*` - 100 requests/minute (moderate usage)

**Steps**:
1. Create RateLimiter class with sliding window algorithm
2. Implement @rate_limit decorator
3. Apply to critical endpoints (start with feedback and login)
4. Add global fallback rate limit (1000 req/min per IP)
5. Load test: Verify 429 returned when limits exceeded
6. Monitor: Add metrics for rate limit hits

**Success Criteria**:
- ✅ Rate limiting active on all critical endpoints
- ✅ 429 responses returned when exceeded
- ✅ DoS attack test: System remains stable under 10k requests/sec
- ✅ Legitimate users not impacted (limits generous enough)

**Risk**: DoS Attack + System Overload (HIGH)

---

#### 2.3 Implement Feedback Backend Storage

**Status**: Pending
**Effort**: 20 hours
**Blocker**: YES (at least basic storage)

**Database Schema**:
```sql
CREATE TABLE feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    metadata JSONB,  -- For additional context
    created_at TIMESTAMP DEFAULT NOW(),
    processed BOOLEAN DEFAULT FALSE,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_feedback_user_id ON feedback(user_id);
CREATE INDEX idx_feedback_created_at ON feedback(created_at DESC);
CREATE INDEX idx_feedback_processed ON feedback(processed);
```

**Feedback Service**:
```python
# lukhas/feedback/service.py
from typing import Dict, List, Optional
from datetime import datetime

class FeedbackService:
    """Service for storing and processing user feedback."""

    async def store(
        self,
        user_id: str,
        rating: int,
        comment: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """Store user feedback in database."""
        feedback_id = await db.execute(
            """
            INSERT INTO feedback (user_id, rating, comment, metadata)
            VALUES (?, ?, ?, ?)
            RETURNING id
            """,
            user_id, rating, comment, metadata
        )
        return {"id": feedback_id, "status": "stored"}

    async def get_user_feedback(
        self,
        user_id: str,
        limit: int = 50
    ) -> List[Dict]:
        """Retrieve feedback submitted by a user."""
        return await db.query(
            """
            SELECT id, rating, comment, created_at
            FROM feedback
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            user_id, limit
        )

    async def get_unprocessed_feedback(self, limit: int = 100) -> List[Dict]:
        """Get feedback that hasn't been processed for learning."""
        return await db.query(
            """
            SELECT id, user_id, rating, comment, metadata
            FROM feedback
            WHERE processed = FALSE
            ORDER BY created_at ASC
            LIMIT ?
            """,
            limit
        )

    async def mark_processed(self, feedback_ids: List[str]):
        """Mark feedback as processed."""
        await db.execute(
            "UPDATE feedback SET processed = TRUE WHERE id = ANY(?)",
            feedback_ids
        )
```

**Steps**:
1. Create feedback database schema
2. Implement FeedbackService class
3. Update feedback_routes.py to use service
4. Add GET endpoint for users to view their feedback
5. Test: Create, retrieve, and process feedback

**Success Criteria**:
- ✅ Feedback stored in database with user_id
- ✅ Users can retrieve their own feedback
- ✅ Unprocessed feedback can be queried for ML pipeline
- ✅ No data loss (transactions, error handling)

**Risk**: Data Loss + Incomplete Feature (MEDIUM)

---

## Phase 3: Compliance & Logging (P1 - IMPORTANT)

**Priority**: HIGH (not launch blocking, but needed soon)
**Duration**: 15 hours (Week 3)
**Owner**: Either engineer (can parallelize with other tasks)

### Tasks

#### 3.1 Enable Audit Logging

**Status**: Pending
**Effort**: 10 hours

**Implementation**:
```python
# lukhas/observability/audit_logger.py
import logging
from typing import Optional, Dict
from datetime import datetime

class AuditLogger:
    """Centralized audit logging for security-sensitive operations."""

    def __init__(self):
        self.logger = logging.getLogger("lukhas.audit")
        # Configure to write to separate audit.log file
        handler = logging.FileHandler("/var/log/lukhas/audit.log")
        handler.setFormatter(logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s'
        ))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def log_auth_attempt(
        self,
        user_id: Optional[str],
        success: bool,
        ip: str,
        details: Optional[Dict] = None
    ):
        """Log authentication attempts."""
        self.logger.info(
            f"AUTH | user_id={user_id} | success={success} | ip={ip} | {details}"
        )

    def log_data_access(
        self,
        user_id: str,
        resource: str,
        action: str,
        success: bool
    ):
        """Log data access events (read, write, delete)."""
        self.logger.info(
            f"DATA_ACCESS | user_id={user_id} | resource={resource} | "
            f"action={action} | success={success}"
        )

    def log_permission_denied(
        self,
        user_id: str,
        resource: str,
        required_tier: str,
        user_tier: str
    ):
        """Log authorization failures."""
        self.logger.warning(
            f"PERMISSION_DENIED | user_id={user_id} | resource={resource} | "
            f"required={required_tier} | user={user_tier}"
        )

    def log_feedback_submission(
        self,
        user_id: str,
        feedback_id: str,
        rating: int
    ):
        """Log feedback submissions."""
        self.logger.info(
            f"FEEDBACK | user_id={user_id} | id={feedback_id} | rating={rating}"
        )

audit_logger = AuditLogger()
```

**Events to Log**:
1. Authentication attempts (success/failure)
2. Permission denied events
3. Data access (memories, dreams, user states)
4. Feedback submissions
5. Administrative actions
6. Rate limit violations

**Steps**:
1. Create AuditLogger class
2. Integrate into auth middleware
3. Add log calls to critical endpoints
4. Configure log rotation (daily, keep 90 days)
5. Test: Verify logs captured for all sensitive operations

**Success Criteria**:
- ✅ All sensitive operations logged
- ✅ Logs include user_id, timestamp, action, success
- ✅ Log retention policy configured (90 days)
- ✅ SOC 2 CC6.2 compliance (access logging)

---

#### 3.2 GDPR Basics - Privacy Policy & Data Deletion

**Status**: Pending
**Effort**: 5 hours

**Implementation**:

**1. Privacy Policy** (Legal document - template needed):
- Data collection practices
- How data is used
- User rights (access, deletion, portability)
- Data retention periods
- Contact for privacy requests

**2. Data Deletion Endpoint**:
```python
# serve/privacy_routes.py
@router.delete("/api/v1/users/me/data")
async def delete_user_data(
    current_user: dict = Depends(get_current_user),
    confirm: bool = Query(..., description="Must be true to confirm deletion")
):
    """
    Delete all user data (GDPR Article 17 - Right to Erasure).
    WARNING: This is irreversible!
    """
    if not confirm:
        raise HTTPException(400, "Must confirm deletion")

    user_id = current_user["user_id"]

    # Delete from all tables
    await db.execute("DELETE FROM memories WHERE user_id = ?", user_id)
    await db.execute("DELETE FROM dreams WHERE user_id = ?", user_id)
    await db.execute("DELETE FROM feedback WHERE user_id = ?", user_id)
    await db.execute("DELETE FROM user_states WHERE user_id = ?", user_id)
    # Soft delete user account (keep for audit trail)
    await db.execute(
        "UPDATE users SET deleted_at = NOW(), email = NULL WHERE id = ?",
        user_id
    )

    audit_logger.log_data_deletion(user_id, success=True)

    return {"status": "deleted", "user_id": user_id}
```

**3. Data Export Endpoint**:
```python
@router.get("/api/v1/users/me/export")
async def export_user_data(
    current_user: dict = Depends(get_current_user)
):
    """Export all user data (GDPR Article 20 - Right to Data Portability)."""
    user_id = current_user["user_id"]

    data = {
        "user_id": user_id,
        "exported_at": datetime.utcnow().isoformat(),
        "memories": await get_user_memories(user_id),
        "dreams": await get_user_dreams(user_id),
        "feedback": await get_user_feedback(user_id),
        "state": await get_user_state(user_id)
    }

    return JSONResponse(content=data)
```

**Steps**:
1. Draft Privacy Policy (or use template)
2. Implement data deletion endpoint
3. Implement data export endpoint
4. Add privacy routes to serve/main.py
5. Test: Verify deletion removes all user data
6. Document: Add privacy endpoints to API docs

**Success Criteria**:
- ✅ Privacy Policy published
- ✅ Users can delete their data
- ✅ Users can export their data (JSON format)
- ✅ GDPR Article 17 & 20 compliance (basic)

---

## Phase 4: Endocrine System Refactor (P2 - OPTIONAL)

**Priority**: MEDIUM (can launch without this if documented)
**Duration**: 35 hours (Week 3-4, if time permits)
**Owner**: Either engineer (stretch goal)

### Tasks

#### 4.1 Refactor to Per-User Endocrine State

**Status**: Deferred (can launch with limitation documented)
**Effort**: 35 hours

**Current Problem**:
```python
# core/endocrine/hormone_system.py (GLOBAL STATE)
class EndocrineSystem:
    _instance = None  # Singleton - shared by ALL users! ❌

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.hormones = {}  # Global state
        return cls._instance
```

**Correct Implementation**:
```python
# core/endocrine/hormone_system.py (PER-USER STATE)
from typing import Dict

class UserEndocrineManager:
    """Manages per-user endocrine system instances."""

    def __init__(self):
        self.user_systems: Dict[str, EndocrineSystem] = {}

    def get_or_create(self, user_id: str) -> EndocrineSystem:
        """Get endocrine system for a user, creating if needed."""
        if user_id not in self.user_systems:
            self.user_systems[user_id] = EndocrineSystem(user_id)
        return self.user_systems[user_id]

    def cleanup_inactive(self, inactive_threshold_hours: int = 24):
        """Remove endocrine systems for inactive users."""
        # Implement LRU cache or time-based cleanup
        pass

# Dependency injection
def get_user_endocrine(
    current_user: dict = Depends(get_current_user)
) -> EndocrineSystem:
    """Get endocrine system for current user."""
    manager = UserEndocrineManager()  # Or singleton manager
    return manager.get_or_create(current_user["user_id"])
```

**If Deferred**: Document as **Known Limitation**:
- "Emotional modulation is in beta and uses a shared model"
- "Personalized emotional states coming in future update"
- Disable any user-facing hormone APIs that could leak cross-user effects

**Steps** (if implemented):
1. Create UserEndocrineManager class
2. Refactor EndocrineSystem to accept user_id
3. Update all endocrine usage to be user-specific
4. Implement cleanup for inactive users (memory management)
5. Test: Multiple users have separate hormone states

**Success Criteria**:
- ✅ Each user has isolated hormone state
- ✅ No cross-user hormone effects
- ✅ Memory efficient (cleanup inactive users)
- ✅ Privacy compliant (user data separation)

---

## Minimum Viable Secure Launch Checklist

Before announcing public launch, **all** items below must be ✅:

### Critical Security (P0)
- [ ] **All API endpoints require authentication** (StrictAuthMiddleware deployed)
- [ ] **user_id derived from auth token only** (no optional user_id in requests)
- [ ] **Per-user data isolation implemented** (memories, dreams, feedback scoped)
- [ ] **Feedback endpoints secured** (auth required, rate limited)
- [ ] **Rate limiting active** (critical endpoints protected from spam/DoS)
- [ ] **JWT auth fully integrated** (ΛiD system with tier checks)

### Compliance & Operations (P1)
- [ ] **Audit logging enabled** (sensitive actions logged with user_id, timestamp)
- [ ] **GDPR basics addressed** (Privacy Policy, data deletion endpoint)
- [ ] **Security testing complete** (pentest or thorough manual review)
- [ ] **Load testing passed** (system stable under expected traffic + margin)

### Documentation & Readiness
- [ ] **Known limitations documented** (e.g., global endocrine state if not fixed)
- [ ] **Rollback plan ready** (feature flags, database backup, quick disable)
- [ ] **API documentation updated** (Swagger shows auth requirements)
- [ ] **Internal runbook created** (incident response procedures)

### Optional (P2)
- [ ] **Endocrine system per-user** (or limitation clearly disclosed)
- [ ] **Advanced feedback analytics** (pattern detection, can defer)
- [ ] **Feature flag system** (canary rollouts, can add post-launch)

**Launch Decision**:
- **GO** if all P0 and P1 items are ✅
- **NO-GO** if any P0 item is incomplete (security risk too high)
- **CONDITIONAL GO** if P0 complete but P1 has minor gaps (fix rapidly post-launch)

---

## Post-Launch Priorities

After securing conditional GO for launch:

1. **Complete Endocrine Refactor** (if deferred)
2. **Enhance Feedback Learning Loop** (pattern extraction, policy updates)
3. **Full GDPR Compliance** (automated data export, retention policies)
4. **Monitoring & Automation** (anomaly detection, auto-blocking malicious IPs)
5. **Performance Optimization** (caching, reduce auth overhead if needed)
6. **External Security Audit** (professional pentest)
7. **SOC 2 Certification Prep** (if targeting enterprise customers)

---

## Risk Register

| Risk | Severity | Likelihood | Mitigation |
|------|----------|------------|------------|
| **Broken Access Control** | CRITICAL | 100% | P0 Tasks 1.1-1.3 (auth, user_id, isolation) |
| **Identity Spoofing** | CRITICAL | 100% | P0 Task 1.2 (remove optional user_id) |
| **Feedback Spam/Poisoning** | HIGH | 90% | P0 Tasks 2.1-2.2 (auth + rate limit) |
| **DoS Attack** | HIGH | 80% | P0 Task 2.2 (rate limiting) |
| **Global Endocrine Leak** | MEDIUM | 60% | P2 Task 4.1 (or document limitation) |
| **GDPR Non-Compliance** | HIGH | 50% | P1 Task 3.2 (Privacy Policy, deletion) |
| **Audit Trail Gaps** | MEDIUM | 40% | P1 Task 3.1 (audit logging) |

**Risk Acceptance**:
- Global endocrine state (P2) can be accepted for MVP if properly documented
- Manual GDPR processes (P1) acceptable for beta, must automate for scale

---

## Success Metrics

**Week 1 Checkpoint**:
- ✅ StrictAuthMiddleware deployed
- ✅ user_id removed from all request models
- ✅ get_current_user() dependency created
- ✅ 50% of endpoints updated with auth

**Week 2 Checkpoint**:
- ✅ 100% of endpoints require auth
- ✅ Per-user data isolation complete
- ✅ Rate limiting implemented
- ✅ Feedback backend storing data

**Week 3 Checkpoint**:
- ✅ Audit logging active
- ✅ GDPR endpoints implemented
- ✅ Security testing in progress
- ✅ Load testing passing

**Week 4 (Launch Ready)**:
- ✅ All P0 tasks complete
- ✅ All P1 tasks complete
- ✅ Known limitations documented
- ✅ Security score: 90/100+

**Go/No-Go Decision**: End of Week 4
- **Metrics Required**:
  - User ID Integration: 55 → 90+ (target: 95)
  - Feedback System: 70 → 90+ (target: 95)
  - Endocrine System: 65 → 75+ (or limitation documented)

---

## Resources & Tools

**Implementation**:
- FastAPI dependency injection (Depends)
- Pydantic for request validation
- Existing ΛiD JWT system (leverage what's built)
- PostgreSQL for user data (with proper indexing)

**Testing**:
- pytest for unit/integration tests
- Locust for load testing (already have: tests/performance/test_load_benchmarks.py)
- Manual pentest or automated tools (OWASP ZAP)

**Monitoring**:
- Prometheus metrics (already configured)
- Audit logs (/var/log/lukhas/audit.log)
- Rate limit hit counters

**Documentation**:
- Swagger/OpenAPI (auto-generated by FastAPI)
- Privacy Policy template (legal review recommended)
- Internal runbook (Google Docs or similar)

---

## Conclusion

This action plan provides a **clear, prioritized roadmap** to transform LUKHAS from **LAUNCH BLOCKER** status to **Conditional GO for Launch** within 4 weeks.

**Critical Path**:
1. Week 1-2: Authentication & Authorization (P0)
2. Week 2-3: Feedback Security & Rate Limiting (P0)
3. Week 3-4: Compliance & Testing (P1)
4. Optional: Endocrine Improvements (P2, or defer)

**Expected Outcome**:
- **Security Score**: 55 → 95 (User ID Integration)
- **Feedback Security**: 70 → 95 (Feedback System)
- **Launch Ready**: 4 weeks if all P0/P1 tasks complete

**Risk Mitigation**: Clear go/no-go criteria, documented limitations for any deferred features, rollback plan in place.

---

**Document Version**: 1.0
**Date**: 2025-11-10
**Next Review**: Weekly checkpoints
**Owner**: Development Team
**Approver**: [To be assigned]
