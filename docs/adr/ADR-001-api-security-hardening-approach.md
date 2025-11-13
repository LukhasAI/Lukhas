# ADR-001: API Security Hardening Approach

**Status**: Proposed
**Date**: 2025-11-10
**Context**: Task 3 (Production API Routes) Security Hardening

## Context

Current state analysis:
- ✅ 3 API modules exist (dreams.py, drift.py, glyphs.py) - ~700 LOC
- ❌ Security score: 55-70/100 (per audit findings)
- ❌ Target: 90+/100
- ❌ Missing: Authentication, authorization, rate limiting, user isolation, comprehensive tests

## Problem

Task 3 was scoped as "Create production API routes" but routes already exist. Real need is **security hardening** which is substantially larger:

**Scope Analysis:**
- Files affected: 3 (dreams.py, drift.py, glyphs.py)
- Endpoints affected: 15 total
- Required tests: 90 (6 types × 15 endpoints)
- Estimated LOC: 1000-1500 total
- Exceeds: LUKHAS Test Surgeon ≤120 LOC guideline (Rule #7)

**Missing Security Controls (per Master Prompt):**
1. Authentication (`Depends(get_current_user)`) - 0/15 endpoints
2. Authorization (`@lukhas_tier_required`) - 0/15 endpoints
3. Rate limiting (`@limiter.limit()`) - 0/15 endpoints
4. User isolation (user-scoped queries) - 0/15 endpoints
5. Audit logging (with user_id) - partial
6. Comprehensive tests (6 types each) - 0/90 tests

## Decision

**Adopt Phased Approach (Option A):**

### Phase 1: Reference Implementation (Current)
- ✅ Create security helper module (`auth_helpers.py`)
- ✅ Create test skeleton (24 tests for dreams.py)
- ⏳ Update dreams.py health endpoint as reference
- ⏳ Document pattern in this ADR

### Phase 2: Dreams API Complete (Next PR)
- Apply security to all 4 dreams.py endpoints
- Implement all 24 tests
- Add rate limiting
- Achieve 90+/100 score for dreams.py

### Phase 3: Drift API (Separate PR)
- Apply pattern to drift.py (4 endpoints)
- Implement 24 tests
- Security hardening

### Phase 4: Glyphs API (Separate PR)
- Apply pattern to glyphs.py (7 endpoints)
- Implement 42 tests
- Security hardening

## Security Pattern (Reference)

### Authentication
```python
from lukhas_website.lukhas.api.auth_helpers import get_current_user, lukhas_tier_required
from identity.tier_system import TierLevel, PermissionScope

@router.post("/api/v1/dreams/simulate")
@lukhas_tier_required(TierLevel.AUTHENTICATED, PermissionScope.RESOURCE_CREATE)
async def create_dream(
    request: DreamRequest,
    current_user: dict = Depends(get_current_user)  # ✅ REQUIRED
):
    user_id = current_user["user_id"]  # ✅ From auth, NOT request body

    # User-scoped operation
    result = await dream_service.create(user_id=user_id, data=request)

    # Audit log
    audit_log_operation("dream_create", user_id, {"dream_id": result.id})

    return result
```

### Rate Limiting
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/api/v1/dreams/simulate")
@limiter.limit("50/minute")  # ✅ Per-endpoint limits
@lukhas_tier_required(TierLevel.AUTHENTICATED, PermissionScope.RESOURCE_CREATE)
async def create_dream(...):
    pass
```

### User Isolation
```python
# ✅ CORRECT: User-scoped retrieval
async def get_dream(dream_id: str, current_user: dict = Depends(get_current_user)):
    dream = await dream_service.get(dream_id)

    # ✅ CRITICAL: Validate ownership
    if dream.user_id != current_user["user_id"] and current_user["tier"] < TierLevel.ADMIN.value:
        raise HTTPException(403, "Cannot access other user's dreams")

    return dream
```

### Test Requirements (6 types per endpoint)
1. Success case (with valid auth)
2. Unauthorized (401) - no auth token
3. Forbidden (403) - insufficient tier
4. Cross-user (403) - cannot access other user's data
5. Rate limiting (429) - exceeds limit
6. Validation (422) - invalid request data

## Consequences

**Positive:**
- ✅ Manageable PR sizes (~300-400 LOC each)
- ✅ Clear pattern demonstration
- ✅ Incremental security improvement
- ✅ Easier review and testing
- ✅ Can measure progress (33% → 66% → 100%)

**Negative:**
- ⚠️ 4 PRs instead of 1 (more overhead)
- ⚠️ Partial security until all phases complete
- ⚠️ Need to maintain consistency across phases

**Risk Mitigation:**
- Phase 1 (reference) establishes patterns
- Each phase is independently testable
- Security gaps documented until completion
- Can prioritize by risk (dreams → drift → glyphs)

## Implementation Status

### Completed
- ✅ Security helper module (`auth_helpers.py`) - 120 LOC
- ✅ Test skeleton (`test_dreams_api_security.py`) - 160 LOC
- ✅ ADR documenting approach

### Next Steps
1. Complete Phase 1: Update dreams.py health endpoint as reference
2. Commit Phase 1 as "feat(api): add security pattern for dreams API (reference)"
3. Create Phase 2 PR: Full dreams.py security hardening
4. Repeat for drift.py and glyphs.py

### Success Metrics (Per Phase)
- All endpoints have `Depends(get_current_user)` ✅
- All endpoints have `@lukhas_tier_required` ✅
- All endpoints have `@limiter.limit()` ✅
- All queries user-scoped ✅
- GET-by-ID validates ownership ✅
- All operations audit logged ✅
- All 6 test types implemented ✅
- Target: 90+/100 security score

## References
- LUKHAS Test Surgeon security requirements (MASTER_PROMPT)
- Security audit findings (55-70/100 → 90+/100 target)
- T4 guidelines (Sam/Dario/Steve/Demis alignment)
- OWASP API Security Top 10

---

**Author**: Claude Code Web
**Reviewed**: Pending steward review
**Approved**: Pending
