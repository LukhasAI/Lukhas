# Phase 1 Task 3: Implement Per-User Data Isolation - T4 Security Prompt

**Context**: GPT-5 Pro audit identified CRITICAL data leakage - queries return ALL users' data without filtering

**Priority**: P0 - CRITICAL BLOCKER
**Effort**: 12 hours
**Depends On**: Task 1.2 (get_current_user must be deployed to provide validated user_id)
**Goal**: Ensure ALL database queries filter by user_id - prevent cross-user data access

---

## T4 Security Principles

1. **Database-Level Isolation** - ALL queries MUST filter by user_id
2. **No Global Data Access** - Remove queries that return all users' data
3. **Ownership Validation** - Verify user owns data before update/delete
4. **Index for Performance** - Add user_id indexes to prevent slow queries
5. **Test Multi-User Scenarios** - Verify User A cannot see User B's data

---

## Current Vulnerability

**OWASP A01: Broken Access Control + Privacy Violation (CRITICAL)**

```python
# memory/core.py (CURRENT - VULNERABLE)
class MemorySystem:
    async def get_memories(self):
        # ❌ RETURNS ALL MEMORIES FROM ALL USERS!
        return await self.db.query("SELECT * FROM memories")

    async def create_memory(self, content: dict):
        # ❌ NO USER_ID - CANNOT ISOLATE DATA!
        return await self.db.execute(
            "INSERT INTO memories (content) VALUES (?)",
            content
        )
```

```python
# consciousness/dream.py (CURRENT - VULNERABLE)
class DreamSystem:
    async def get_user_dreams(self, user_id: str):
        # ❌ HAS user_id PARAMETER BUT NO FILTERING!
        return await self.db.query("SELECT * FROM dreams")
        # Ignores user_id - returns ALL dreams!
```

```python
# serve/feedback_routes.py (CURRENT - VULNERABLE)
async def get_feedback():
    # ❌ RETURNS ALL FEEDBACK FROM ALL USERS!
    return await db.query("SELECT * FROM feedback")
```

**Impact**:
- User A can see User B's memories
- User A can see User B's dreams
- User A can see User B's feedback
- Privacy violation, data breach, GDPR violation
- 100% exploitable - trivial data leakage

**Risk**: CRITICAL - Complete privacy control bypass

---

## Task 3.1: Database Schema Updates

### Step 1: Create Database Migration

**Location**: `migrations/001_add_user_id_columns.sql`

**Implementation**:

```sql
-- Migration: Add user_id columns to all user data tables
-- Created: 2025-11-10
-- Purpose: Implement per-user data isolation for security

-- 1. Add user_id columns
ALTER TABLE memories ADD COLUMN user_id VARCHAR(255) NOT NULL DEFAULT 'system';
ALTER TABLE dreams ADD COLUMN user_id VARCHAR(255) NOT NULL DEFAULT 'system';
ALTER TABLE feedback ADD COLUMN user_id VARCHAR(255) NOT NULL DEFAULT 'system';
ALTER TABLE consciousness_states ADD COLUMN user_id VARCHAR(255) NOT NULL DEFAULT 'system';

-- 2. Create indexes for query performance
-- CRITICAL: Without indexes, filtering by user_id will be SLOW
CREATE INDEX idx_memories_user_id ON memories(user_id);
CREATE INDEX idx_dreams_user_id ON dreams(user_id);
CREATE INDEX idx_feedback_user_id ON feedback(user_id);
CREATE INDEX idx_consciousness_states_user_id ON consciousness_states(user_id);

-- 3. Add composite indexes for common queries
CREATE INDEX idx_memories_user_created ON memories(user_id, created_at DESC);
CREATE INDEX idx_dreams_user_status ON dreams(user_id, status);
CREATE INDEX idx_feedback_user_rating ON feedback(user_id, rating);

-- 4. Add unique constraints where needed
-- Ensure one consciousness state per user
ALTER TABLE consciousness_states ADD CONSTRAINT unique_user_state UNIQUE (user_id);

-- 5. Update existing data (if any)
-- IMPORTANT: Review existing data and assign to correct users
-- For now, assign orphaned data to 'system' user
UPDATE memories SET user_id = 'system' WHERE user_id IS NULL;
UPDATE dreams SET user_id = 'system' WHERE user_id IS NULL;
UPDATE feedback SET user_id = 'system' WHERE user_id IS NULL;
UPDATE consciousness_states SET user_id = 'system' WHERE user_id IS NULL;

-- 6. Remove DEFAULT after data migration
ALTER TABLE memories ALTER COLUMN user_id DROP DEFAULT;
ALTER TABLE dreams ALTER COLUMN user_id DROP DEFAULT;
ALTER TABLE feedback ALTER COLUMN user_id DROP DEFAULT;
ALTER TABLE consciousness_states ALTER COLUMN user_id DROP DEFAULT;

-- 7. Add NOT NULL constraints (already added above)
-- user_id is now required for all new records

COMMIT;
```

**For PostgreSQL**:
```sql
-- PostgreSQL-specific syntax
ALTER TABLE memories ADD COLUMN IF NOT EXISTS user_id VARCHAR(255) NOT NULL DEFAULT 'system';
-- ... (same pattern for other tables)

-- PostgreSQL index creation
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_memories_user_id ON memories(user_id);
-- ... (same pattern for other indexes)
```

**For SQLite** (development/testing):
```sql
-- SQLite doesn't support ALTER COLUMN, so recreate tables
-- Create new table with user_id
CREATE TABLE memories_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Copy data
INSERT INTO memories_new (id, user_id, content, created_at)
SELECT id, 'system', content, created_at FROM memories;

-- Replace old table
DROP TABLE memories;
ALTER TABLE memories_new RENAME TO memories;

-- Create indexes
CREATE INDEX idx_memories_user_id ON memories(user_id);
```

**TODO in Step 1**:
- [ ] Create migration file for your database (PostgreSQL/MySQL/SQLite)
- [ ] Add user_id columns to ALL user data tables
- [ ] Create indexes for performance (user_id, composite indexes)
- [ ] Update existing data (assign to 'system' or migrate properly)
- [ ] Test migration on development database
- [ ] Document rollback plan

---

## Task 3.2: Update Data Models

### Step 2: Update Pydantic Models

**Location**: `lukhas/memory/models.py`

**BEFORE (No user isolation)**:
```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Memory(BaseModel):
    id: int
    content: str
    created_at: datetime
    # ❌ NO user_id FIELD!
```

**AFTER (User-scoped)**:
```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Memory(BaseModel):
    id: int
    user_id: str  # ✅ REQUIRED FIELD
    content: str
    created_at: datetime

    class Config:
        # Ensure user_id cannot be None
        validate_assignment = True

class MemoryCreate(BaseModel):
    """Model for creating memories - user_id added by endpoint."""
    content: str
    # NO user_id field - added by endpoint from auth token

class MemoryFilter(BaseModel):
    """Model for filtering memories."""
    user_id: str  # Required for filtering
    limit: int = 50
    offset: int = 0
```

**Location**: `lukhas/consciousness/models.py`

```python
class Dream(BaseModel):
    id: int
    user_id: str  # ✅ REQUIRED
    dream_id: str
    status: str
    content: Optional[str] = None
    created_at: datetime

class DreamCreate(BaseModel):
    """Model for creating dreams."""
    context: Optional[Dict[str, Any]] = None
    # NO user_id - added by endpoint

class ConsciousnessState(BaseModel):
    user_id: str  # ✅ REQUIRED - one state per user
    awareness_level: float
    memory_folds: int
    last_updated: datetime
```

**TODO in Step 2**:
- [ ] Add `user_id: str` to ALL data models
- [ ] Create separate *Create models without user_id (added by endpoint)
- [ ] Update model validators to enforce user_id
- [ ] Document that user_id comes from auth, not client

---

## Task 3.3: Update Database Queries

### Step 3: Update Memory System

**Location**: `lukhas/memory/core.py` (or `memory/core.py`)

**BEFORE (Vulnerable)**:
```python
class MemorySystem:
    def __init__(self, db):
        self.db = db

    async def get_memories(self):
        """❌ RETURNS ALL MEMORIES FROM ALL USERS!"""
        return await self.db.query("SELECT * FROM memories")

    async def create_memory(self, content: str):
        """❌ NO USER_ID - CREATES ORPHANED DATA!"""
        return await self.db.execute(
            "INSERT INTO memories (content) VALUES (?)",
            content
        )

    async def get_memory_by_id(self, memory_id: int):
        """❌ NO OWNERSHIP CHECK!"""
        return await self.db.query_one(
            "SELECT * FROM memories WHERE id = ?",
            memory_id
        )
```

**AFTER (Secure)**:
```python
class MemorySystem:
    def __init__(self, db):
        self.db = db

    async def get_memories(self, user_id: str, limit: int = 50, offset: int = 0):
        """✅ RETURNS ONLY THIS USER'S MEMORIES"""
        return await self.db.query(
            "SELECT * FROM memories WHERE user_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
            user_id, limit, offset
        )

    async def create_memory(self, user_id: str, content: str):
        """✅ CREATES MEMORY WITH USER_ID"""
        return await self.db.execute(
            "INSERT INTO memories (user_id, content) VALUES (?, ?)",
            user_id, content
        )

    async def get_memory_by_id(self, user_id: str, memory_id: int):
        """✅ VALIDATES OWNERSHIP BEFORE RETURNING"""
        memory = await self.db.query_one(
            "SELECT * FROM memories WHERE id = ? AND user_id = ?",
            memory_id, user_id
        )
        if not memory:
            raise MemoryNotFoundError(f"Memory {memory_id} not found for user {user_id}")
        return memory

    async def update_memory(self, user_id: str, memory_id: int, content: str):
        """✅ VALIDATES OWNERSHIP BEFORE UPDATE"""
        result = await self.db.execute(
            "UPDATE memories SET content = ? WHERE id = ? AND user_id = ?",
            content, memory_id, user_id
        )
        if result.rowcount == 0:
            raise MemoryNotFoundError(f"Memory {memory_id} not found or not owned by user")
        return result

    async def delete_memory(self, user_id: str, memory_id: int):
        """✅ VALIDATES OWNERSHIP BEFORE DELETE"""
        result = await self.db.execute(
            "DELETE FROM memories WHERE id = ? AND user_id = ?",
            memory_id, user_id
        )
        if result.rowcount == 0:
            raise MemoryNotFoundError(f"Memory {memory_id} not found or not owned by user")
        return result
```

**TODO in Step 3**:
- [ ] Add `user_id` parameter to ALL memory methods
- [ ] Update ALL queries to filter by user_id
- [ ] Add ownership validation for update/delete operations
- [ ] Raise exceptions when user doesn't own data
- [ ] Add proper error messages

---

### Step 4: Update Dream System

**Location**: `lukhas/consciousness/dream.py` (or `consciousness/dream.py`)

**BEFORE (Vulnerable)**:
```python
class DreamSystem:
    async def get_user_dreams(self, user_id: str):
        """❌ HAS user_id PARAMETER BUT DOESN'T USE IT!"""
        return await self.db.query("SELECT * FROM dreams")

    async def create_dream(self, dream_data: dict):
        """❌ NO USER_ID IN CREATION!"""
        return await self.db.execute(
            "INSERT INTO dreams (dream_id, status, content) VALUES (?, ?, ?)",
            dream_data["dream_id"], dream_data["status"], dream_data["content"]
        )
```

**AFTER (Secure)**:
```python
class DreamSystem:
    async def get_user_dreams(self, user_id: str, limit: int = 50):
        """✅ FILTERS BY USER_ID"""
        return await self.db.query(
            "SELECT * FROM dreams WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
            user_id, limit
        )

    async def create_dream(self, user_id: str, dream_data: dict):
        """✅ INCLUDES USER_ID IN CREATION"""
        return await self.db.execute(
            "INSERT INTO dreams (user_id, dream_id, status, content) VALUES (?, ?, ?, ?)",
            user_id, dream_data["dream_id"], dream_data["status"], dream_data.get("content")
        )

    async def get_dream_by_id(self, user_id: str, dream_id: str):
        """✅ VALIDATES OWNERSHIP"""
        dream = await self.db.query_one(
            "SELECT * FROM dreams WHERE dream_id = ? AND user_id = ?",
            dream_id, user_id
        )
        if not dream:
            raise DreamNotFoundError(f"Dream {dream_id} not found for user")
        return dream

    async def update_dream_status(self, user_id: str, dream_id: str, status: str):
        """✅ VALIDATES OWNERSHIP BEFORE UPDATE"""
        result = await self.db.execute(
            "UPDATE dreams SET status = ? WHERE dream_id = ? AND user_id = ?",
            status, dream_id, user_id
        )
        if result.rowcount == 0:
            raise DreamNotFoundError(f"Dream {dream_id} not found or not owned by user")
        return result
```

**TODO in Step 4**:
- [ ] Update get_user_dreams() to actually filter by user_id
- [ ] Add user_id to dream creation
- [ ] Add ownership validation for updates
- [ ] Test multi-user dream isolation

---

### Step 5: Update Feedback System

**Location**: `serve/feedback_routes.py` or `lukhas/feedback/core.py`

**BEFORE (Vulnerable)**:
```python
async def get_feedback():
    """❌ RETURNS ALL FEEDBACK FROM ALL USERS!"""
    return await db.query("SELECT * FROM feedback")

async def get_user_feedback(user_id: str):
    """❌ MIGHT HAVE user_id BUT NO FILTERING!"""
    return await db.query("SELECT * FROM feedback")
```

**AFTER (Secure)**:
```python
async def get_feedback(user_id: str, limit: int = 50):
    """✅ RETURNS ONLY THIS USER'S FEEDBACK"""
    return await db.query(
        "SELECT * FROM feedback WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
        user_id, limit
    )

async def create_feedback(user_id: str, rating: int, comment: str):
    """✅ INCLUDES USER_ID IN CREATION"""
    return await db.execute(
        "INSERT INTO feedback (user_id, rating, comment) VALUES (?, ?, ?)",
        user_id, rating, comment
    )

async def get_feedback_by_id(user_id: str, feedback_id: int):
    """✅ VALIDATES OWNERSHIP"""
    feedback = await db.query_one(
        "SELECT * FROM feedback WHERE id = ? AND user_id = ?",
        feedback_id, user_id
    )
    if not feedback:
        raise FeedbackNotFoundError(f"Feedback {feedback_id} not found for user")
    return feedback
```

**TODO in Step 5**:
- [ ] Update ALL feedback queries to filter by user_id
- [ ] Add user_id to feedback creation (from Task 1.2 dependency)
- [ ] Remove any global feedback queries
- [ ] Add ownership validation

---

### Step 6: Update Consciousness State

**Location**: `serve/consciousness_api.py` or `lukhas/consciousness/state.py`

**BEFORE (Vulnerable)**:
```python
class ConsciousnessEngine:
    async def get_user_state(self, user_id: str):
        """❌ PARAMETER EXISTS BUT NOT USED IN QUERY!"""
        # Might return wrong user's state or global state
        return await self.db.query_one("SELECT * FROM consciousness_states LIMIT 1")

    async def save_user_state(self, user_id: str, state: dict):
        """❌ NO VALIDATION THAT STATE BELONGS TO USER!"""
        return await self.db.execute(
            "UPDATE consciousness_states SET awareness_level = ?",
            state["awareness_level"]
        )
```

**AFTER (Secure)**:
```python
class ConsciousnessEngine:
    async def get_user_state(self, user_id: str):
        """✅ FILTERS BY USER_ID"""
        state = await self.db.query_one(
            "SELECT * FROM consciousness_states WHERE user_id = ?",
            user_id
        )
        if not state:
            # Create default state for new user
            return await self.create_default_state(user_id)
        return state

    async def save_user_state(self, user_id: str, state: dict):
        """✅ VALIDATES OWNERSHIP AND UPDATES ONLY THIS USER'S STATE"""
        result = await self.db.execute(
            """
            INSERT INTO consciousness_states (user_id, awareness_level, memory_folds)
            VALUES (?, ?, ?)
            ON CONFLICT (user_id) DO UPDATE SET
                awareness_level = excluded.awareness_level,
                memory_folds = excluded.memory_folds,
                last_updated = CURRENT_TIMESTAMP
            """,
            user_id, state["awareness_level"], state["memory_folds"]
        )
        return result

    async def create_default_state(self, user_id: str):
        """Create default consciousness state for new user."""
        return await self.db.execute(
            "INSERT INTO consciousness_states (user_id, awareness_level, memory_folds) VALUES (?, ?, ?)",
            user_id, 0.5, 0
        )
```

**TODO in Step 6**:
- [ ] Update get_user_state() to filter by user_id
- [ ] Update save_user_state() with UPSERT pattern
- [ ] Create default states for new users
- [ ] Test one-state-per-user constraint

---

## Task 3.4: Update API Endpoints

### Step 7: Update Endpoint Calls

**Location**: `serve/consciousness_api.py`

**BEFORE (Vulnerable)**:
```python
@router.get("/api/v1/consciousness/memory")
async def memory(
    engine: ConsciousnessEngine = Depends(get_consciousness_engine)
):
    """❌ NO USER_ID - RETURNS ALL MEMORIES!"""
    return await engine.retrieve_memory_state()
```

**AFTER (Secure)**:
```python
from lukhas.governance.auth.dependencies import get_current_user_id

@router.get("/api/v1/consciousness/memory")
async def memory(
    engine: ConsciousnessEngine = Depends(get_consciousness_engine),
    user_id: str = Depends(get_current_user_id)  # ✅ FROM JWT!
):
    """✅ RETURNS ONLY THIS USER'S MEMORIES"""
    return await engine.retrieve_memory_state(user_id=user_id)
```

**Location**: `serve/feedback_routes.py`

**BEFORE (Vulnerable)**:
```python
@router.get("/api/v1/feedback")
async def get_all_feedback():
    """❌ RETURNS ALL FEEDBACK!"""
    return await feedback_service.get_feedback()
```

**AFTER (Secure)**:
```python
from lukhas.governance.auth.dependencies import get_current_user_id

@router.get("/api/v1/feedback")
async def get_my_feedback(
    user_id: str = Depends(get_current_user_id)
):
    """✅ RETURNS ONLY THIS USER'S FEEDBACK"""
    return await feedback_service.get_feedback(user_id=user_id)
```

**TODO in Step 7**:
- [ ] Update ALL endpoint calls to pass user_id
- [ ] Remove any "get all data" endpoints (security risk)
- [ ] Rename endpoints to reflect scoping (e.g., get_all → get_my)
- [ ] Test each endpoint returns only user's data

---

## Task 3.5: Create Tests

### Step 8: Test Multi-User Isolation

**Location**: `tests/integration/test_data_isolation.py`

```python
"""Integration tests for per-user data isolation."""

import pytest
from fastapi.testclient import TestClient


class TestDataIsolation:
    """Verify data isolation between users."""

    @pytest.fixture
    def user_a_token(self, client):
        """Get auth token for User A."""
        response = client.post("/api/v1/auth/login", json={
            "email": "userA@example.com",
            "password": "passwordA"
        })
        return response.json()["access_token"]

    @pytest.fixture
    def user_b_token(self, client):
        """Get auth token for User B."""
        response = client.post("/api/v1/auth/login", json={
            "email": "userB@example.com",
            "password": "passwordB"
        })
        return response.json()["access_token"]

    def test_memories_isolated_between_users(self, client, user_a_token, user_b_token):
        """User A cannot see User B's memories."""
        # User A creates a memory
        response = client.post(
            "/api/v1/consciousness/memory",
            headers={"Authorization": f"Bearer {user_a_token}"},
            json={"content": "User A's secret memory"}
        )
        assert response.status_code == 200
        memory_a_id = response.json()["id"]

        # User A can retrieve their memory
        response = client.get(
            f"/api/v1/consciousness/memory/{memory_a_id}",
            headers={"Authorization": f"Bearer {user_a_token}"}
        )
        assert response.status_code == 200
        assert "User A's secret" in response.json()["content"]

        # User B CANNOT retrieve User A's memory
        response = client.get(
            f"/api/v1/consciousness/memory/{memory_a_id}",
            headers={"Authorization": f"Bearer {user_b_token}"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

        # User B gets their own memories (should not include User A's)
        response = client.get(
            "/api/v1/consciousness/memory",
            headers={"Authorization": f"Bearer {user_b_token}"}
        )
        assert response.status_code == 200
        memories = response.json()
        assert memory_a_id not in [m["id"] for m in memories]

    def test_dreams_isolated_between_users(self, client, user_a_token, user_b_token):
        """User A cannot see User B's dreams."""
        # User A creates a dream
        response = client.post(
            "/api/v1/consciousness/dream",
            headers={"Authorization": f"Bearer {user_a_token}"},
            json={"context": {"theme": "flying"}}
        )
        assert response.status_code == 200
        dream_a_id = response.json()["dream_id"]

        # User B CANNOT access User A's dream
        response = client.get(
            f"/api/v1/consciousness/dream/{dream_a_id}",
            headers={"Authorization": f"Bearer {user_b_token}"}
        )
        assert response.status_code == 404

        # User B's dream list should not include User A's dreams
        response = client.get(
            "/api/v1/consciousness/dream",
            headers={"Authorization": f"Bearer {user_b_token}"}
        )
        assert response.status_code == 200
        dreams = response.json()
        assert dream_a_id not in [d["dream_id"] for d in dreams]

    def test_feedback_isolated_between_users(self, client, user_a_token, user_b_token):
        """User A cannot see User B's feedback."""
        # User A submits feedback
        response = client.post(
            "/api/v1/feedback",
            headers={"Authorization": f"Bearer {user_a_token}"},
            json={"rating": 5, "comment": "User A's feedback"}
        )
        assert response.status_code == 200
        feedback_a_id = response.json()["id"]

        # User B CANNOT see User A's feedback
        response = client.get(
            "/api/v1/feedback",
            headers={"Authorization": f"Bearer {user_b_token}"}
        )
        assert response.status_code == 200
        feedback_list = response.json()
        assert feedback_a_id not in [f["id"] for f in feedback_list]
        assert all("User A's feedback" not in f["comment"] for f in feedback_list)

    def test_consciousness_state_isolated_between_users(self, client, user_a_token, user_b_token):
        """Each user has their own consciousness state."""
        # User A saves their state
        response = client.post(
            "/api/v1/consciousness/state",
            headers={"Authorization": f"Bearer {user_a_token}"},
            json={"awareness_level": 0.9, "memory_folds": 100}
        )
        assert response.status_code == 200

        # User B saves their state
        response = client.post(
            "/api/v1/consciousness/state",
            headers={"Authorization": f"Bearer {user_b_token}"},
            json={"awareness_level": 0.3, "memory_folds": 10}
        )
        assert response.status_code == 200

        # User A retrieves THEIR state (not User B's)
        response = client.get(
            "/api/v1/consciousness/state",
            headers={"Authorization": f"Bearer {user_a_token}"}
        )
        assert response.status_code == 200
        state = response.json()
        assert state["awareness_level"] == 0.9
        assert state["memory_folds"] == 100

        # User B retrieves THEIR state (not User A's)
        response = client.get(
            "/api/v1/consciousness/state",
            headers={"Authorization": f"Bearer {user_b_token}"}
        )
        assert response.status_code == 200
        state = response.json()
        assert state["awareness_level"] == 0.3
        assert state["memory_folds"] == 10
```

**TODO in Step 8**:
- [ ] Create integration tests for all data types
- [ ] Test memories, dreams, feedback, consciousness state
- [ ] Verify User A cannot access User B's data
- [ ] Verify queries return only user's own data
- [ ] Test ownership validation on updates/deletes
- [ ] All tests must pass

---

## Verification Checklist

Before marking task complete, verify:

### Database Schema
- [ ] **All user data tables have user_id column**
- [ ] **Indexes created** (user_id, composite indexes for common queries)
- [ ] **Unique constraints** where appropriate (e.g., one state per user)
- [ ] **Migration tested** on development database
- [ ] **Rollback plan documented**

### Data Models
- [ ] **All Pydantic models include user_id**
- [ ] **Create models exclude user_id** (added by endpoint)
- [ ] **Model validation enforces user_id**

### Database Queries
- [ ] **ALL queries filter by user_id** (memories, dreams, feedback, state)
- [ ] **No global data queries** (removed or admin-only)
- [ ] **Ownership validation** before update/delete
- [ ] **Proper error messages** when user doesn't own data

### API Endpoints
- [ ] **All endpoints pass user_id** from Depends(get_current_user_id)
- [ ] **Engine methods updated** to accept user_id
- [ ] **No "get all data" endpoints** exposed to users

### Testing
- [ ] **Multi-user isolation tests pass**
- [ ] **Cross-user access tests FAIL** (User A cannot access User B)
- [ ] **Performance tests** (queries with indexes <100ms)
- [ ] **CI pipeline includes** data isolation tests

### Performance
- [ ] **Query performance** <100ms for user_id filtered queries
- [ ] **Indexes used** (verify with EXPLAIN QUERY PLAN)
- [ ] **No N+1 queries** introduced

---

## Success Criteria

**Functional**:
- ✅ Database schema updated with user_id columns
- ✅ ALL queries filter by user_id
- ✅ No global data access (all scoped to user)
- ✅ Ownership validation before update/delete
- ✅ Each user has isolated data (memories, dreams, feedback, state)

**Security**:
- ✅ OWASP A01 fully mitigated (access control at database level)
- ✅ Privacy violations eliminated
- ✅ GDPR compliance improved (user data isolated)
- ✅ Cross-user access prevented and tested

**Performance**:
- ✅ Indexes created for all user_id queries
- ✅ Query performance <100ms
- ✅ No slow queries introduced

**Testing**:
- ✅ 100% test coverage for data isolation
- ✅ Multi-user scenario tests demonstrate isolation
- ✅ CI pipeline enforces data isolation tests

**Impact**:
- Security Score: 75 → 90 (Data Isolation complete)
- LAUNCH BLOCKER: LIFTED for Phase 1 (all P0 tasks complete)
- Ready for Phase 2 (feedback system security)

---

## Estimated Timeline

- **Step 1** (Database migration): 2 hours
- **Step 2** (Update data models): 1 hour
- **Step 3** (Update memory system): 2 hours
- **Step 4** (Update dream system): 1 hour
- **Step 5** (Update feedback system): 1 hour
- **Step 6** (Update consciousness state): 1 hour
- **Step 7** (Update endpoints): 2 hours
- **Step 8** (Create tests): 2 hours

**Total**: 12 hours

---

## Related Tasks

**Dependencies**:
- Task 1.1 (StrictAuthMiddleware) - Provides authentication
- Task 1.2 (Remove optional user_id) - Provides validated user_id via get_current_user_id()

**Blocking**:
- Phase 2 Tasks (Feedback security, rate limiting) - Need data isolation in place
- Production Launch - This is the final P0 blocker for Phase 1

**Next Steps After Completion**:
1. **Phase 1 Complete** - All P0 tasks done, security score improved significantly
2. Move to Phase 2 Task 2.1 (Secure feedback endpoints with auth + rate limiting)
3. Implement rate limiting for DoS prevention
4. Create feedback backend storage for persistence

---

## References

- **Action Plan**: docs/sessions/GPT5_AUDIT_ACTION_PLAN_2025-11-10.md
- **GPT-5 Audit**: docs/audits/GPT-5 Pro Review - LUKHAS Pre-Launch Au.md
- **OWASP A01**: https://owasp.org/Top10/A01_2021-Broken_Access_Control/
- **GDPR**: https://gdpr.eu/ (Articles 17, 20)
- **Database Indexing**: https://use-the-index-luke.com/

---

**Created**: 2025-11-10
**Owner**: AI Agent (Claude Web / Jules / Copilot)
**Status**: Ready for execution
**Priority**: P0 - CRITICAL BLOCKER
**Depends On**: Tasks 1.1 + 1.2
