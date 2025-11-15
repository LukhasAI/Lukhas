# Security Issue 5: Fix SQL Injection Vulnerabilities (HIGH)

## Priority: P1 - HIGH Security Pattern
## Estimated Effort: 10 days
## Target: Fix all 25 SQL concatenation patterns

---

## 🎯 Objective

Replace all 25 SQL query concatenations with parameterized queries to prevent SQL injection attacks.

## 📊 Current State

- **SQL concatenation occurrences**: 25
- **Risk Level**: HIGH
- **Security Impact**: Data breach, unauthorized access, data manipulation

## 🔍 Background

SQL injection allows attackers to:
- Read sensitive data
- Modify or delete data
- Execute administrative operations
- Access underlying operating system

## 📋 Deliverables

### 1. Standard Fix - Parameterized Queries

**For SQLite/PostgreSQL**:
```python
# ❌ BEFORE (HIGH RISK - SQL Injection)
user_id = request.get('user_id')
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# ✅ AFTER (SAFE - Parameterized)
from typing import Any, Dict, List

def safe_query_user(user_id: int) -> List[Dict[str, Any]]:
    """Safely query user with parameterized statement."""
    cursor.execute(
        "SELECT * FROM users WHERE id = ?",  # Placeholder
        (user_id,)  # Parameters tuple - prevents injection
    )
    return cursor.fetchall()
```

**For MySQL**:
```python
# ✅ Use %s placeholder for MySQL
cursor.execute(
    "SELECT * FROM users WHERE id = %s",
    (user_id,)
)
```

**For Complex Queries**:
```python
# ❌ BEFORE
query = f"SELECT * FROM users WHERE name = '{name}' AND age > {age}"

# ✅ AFTER
query = "SELECT * FROM users WHERE name = ? AND age > ?"
params = (name, age)
cursor.execute(query, params)
```

### 2. ORM Usage (Preferred)

**Use SQLAlchemy ORM**:
```python
# ✅ SQLAlchemy automatically parameterizes
from sqlalchemy.orm import Session

def safe_query_user_orm(session: Session, user_id: int):
    """Query using ORM - automatically safe."""
    return session.query(User).filter(User.id == user_id).first()
```

### 3. Input Validation

**Always validate inputs**:
```python
def validate_user_id(user_id: Any) -> int:
    """Validate user ID is a positive integer."""
    try:
        uid = int(user_id)
        if uid <= 0:
            raise ValueError("User ID must be positive")
        return uid
    except (ValueError, TypeError):
        raise ValueError(f"Invalid user ID: {user_id}")
```

### 4. Security Testing
```python
def test_sql_injection_prevented():
    """Ensure SQL injection attempts fail safely."""
    malicious_inputs = [
        "1 OR 1=1",
        "1; DROP TABLE users;",
        "1' UNION SELECT * FROM passwords--",
    ]
    
    for malicious in malicious_inputs:
        # Should either raise error or find no results
        result = safe_query_user(malicious)
        assert result is None or result == []
```

### 5. Documentation
- [ ] Create `docs/security/SQL_INJECTION_FIX_REPORT.md`
- [ ] Update database query guidelines
- [ ] Document ORM usage patterns

## ✅ Acceptance Criteria

- [ ] All 25 SQL concatenations replaced with parameterized queries
- [ ] No string formatting in SQL queries
- [ ] Input validation in place
- [ ] Prefer ORM where possible
- [ ] Security tests pass
- [ ] Complete documentation

## 🏷️ Labels: `security`, `high`, `p1`, `sql-injection`

---

**Estimated Days**: 10 days | **Phase**: Security Phase 1
