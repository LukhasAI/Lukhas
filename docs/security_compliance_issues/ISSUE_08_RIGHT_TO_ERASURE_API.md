# GDPR Issue 8: Implement Right to Erasure API (GDPR Art. 17)

## Priority: P0 - GDPR Core Compliance
## Estimated Effort: 15 days
## Target: Complete Right to Erasure ("Forget Me") API

---

## 🎯 Objective

Implement the Right to Erasure API (GDPR Article 17) allowing users to permanently delete all their personal data from LUKHAS systems.

## 📊 Current State

- **GDPR Compliance**: 58%
- **Data Subject Rights APIs**: 0/4 implemented
- **Legal Requirement**: GDPR Article 17 mandates "Right to be Forgotten"
- **Target**: 75% GDPR compliance

## 🔍 Background

GDPR Article 17 grants data subjects the right to:
- Request deletion of personal data
- Have data erased without undue delay
- Exceptions: legal obligations require some audit logs

Non-compliance can result in fines up to 4% of annual revenue.

## 📋 Deliverables

### 1. API Endpoint Implementation

**File**: `lukhas/api/v1/data_rights.py`

```python
@router.delete("/users/{user_id}/data")
async def erase_user_data(
    user_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Right to Erasure ("Forget Me") - GDPR Article 17.
    
    Permanently deletes all user data unless legal retention required.
    
    Args:
        user_id: User identifier to erase
        current_user: Authenticated user making the request
        
    Returns:
        Erasure confirmation with timestamp
        
    Raises:
        HTTPException 403: If user requests erasure for another user
    """
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(403, "Can only erase own data")
    
    # Create audit log before deletion (required for compliance)
    await create_erasure_audit_log(user_id, current_user.id)
    
    # Delete from all systems
    results = {
        "identity": await erase_identity_data(user_id),
        "memory": await erase_memory_data(user_id),
        "consciousness": await erase_consciousness_data(user_id),
        "interactions": await erase_interaction_history(user_id),
        "audit_logs": await anonymize_audit_logs(user_id)  # Anonymize, don't delete
    }
    
    return {
        "status": "completed",
        "user_id": user_id,
        "erased_at": datetime.utcnow().isoformat(),
        "systems_processed": list(results.keys()),
        "audit_retention": "6 years (legal requirement)"
    }
```

### 2. Erasure Functions

**Identity Data Erasure**:
```python
async def erase_identity_data(user_id: str) -> Dict[str, Any]:
    """Delete all identity data."""
    # Delete from identity database
    deleted_count = await identity_db.delete({"user_id": user_id})
    
    # Delete authentication credentials
    await auth_db.delete({"user_id": user_id})
    
    return {
        "records_deleted": deleted_count,
        "timestamp": datetime.utcnow().isoformat()
    }

async def erase_memory_data(user_id: str) -> Dict[str, Any]:
    """Delete all memory folds and consciousness states."""
    memory_count = await memory_db.delete({"user_id": user_id})
    consciousness_count = await consciousness_db.delete({"user_id": user_id})
    
    return {
        "memory_folds_deleted": memory_count,
        "consciousness_states_deleted": consciousness_count
    }

async def anonymize_audit_logs(user_id: str) -> Dict[str, Any]:
    """Anonymize audit logs (don't delete - legal requirement)."""
    # Replace user_id with anonymized ID
    anonymized_id = f"ANON_{hash(user_id)}"
    updated_count = await audit_db.update(
        {"user_id": user_id},
        {"$set": {"user_id": anonymized_id}}
    )
    
    return {
        "logs_anonymized": updated_count,
        "anonymized_id": anonymized_id
    }
```

### 3. Confirmation Workflow

**Two-Step Confirmation**:
```python
@router.post("/users/{user_id}/erasure-request")
async def request_erasure(user_id: str, email: str):
    """Step 1: Request erasure, send confirmation email."""
    token = generate_erasure_token(user_id)
    await send_erasure_confirmation_email(email, token)
    return {"status": "confirmation_sent"}

@router.post("/users/{user_id}/confirm-erasure")
async def confirm_erasure(user_id: str, token: str):
    """Step 2: Confirm erasure with token."""
    if not verify_erasure_token(user_id, token):
        raise HTTPException(403, "Invalid erasure token")
    
    # Proceed with erasure
    return await erase_user_data(user_id, current_user)
```

### 4. Testing

```python
@pytest.mark.asyncio
async def test_erasure_deletes_all_data():
    """Verify all user data is deleted."""
    # Create test user with data
    user_id = "test_user_123"
    await create_test_user_data(user_id)
    
    # Request erasure
    response = await erase_user_data(user_id)
    
    # Verify all data deleted
    identity = await get_identity_data(user_id)
    memory = await get_memory_data(user_id)
    
    assert identity is None
    assert memory == []

@pytest.mark.asyncio
async def test_audit_logs_anonymized_not_deleted():
    """Audit logs should be anonymized, not deleted."""
    user_id = "test_user_123"
    await create_audit_log(user_id, "test_action")
    
    await erase_user_data(user_id)
    
    # Audit logs still exist but anonymized
    logs = await audit_db.find({"user_id": {"$regex": "ANON_"}})
    assert len(logs) > 0
```

### 5. Legal Compliance

**Audit Logging**:
```python
async def create_erasure_audit_log(
    user_id: str,
    requester_id: str
) -> None:
    """Create audit log for erasure request."""
    await audit_db.insert({
        "event": "data_erasure_request",
        "user_id": user_id,
        "requester_id": requester_id,
        "timestamp": datetime.utcnow(),
        "systems": ["identity", "memory", "consciousness", "interactions"],
        "retention_period": "6 years"
    })
```

### 6. Documentation

- [ ] Create `docs/gdpr/RIGHT_TO_ERASURE_API.md`
- [ ] Erasure workflow documentation
- [ ] Legal requirements and exceptions
- [ ] Audit log retention policy

## ✅ Acceptance Criteria

- [ ] API endpoint implemented and tested
- [ ] All data deleted from all systems
- [ ] Audit logs anonymized (not deleted)
- [ ] Two-step confirmation workflow
- [ ] Email confirmation sent
- [ ] Unit tests with >80% coverage
- [ ] Integration tests verify complete erasure
- [ ] Documentation complete
- [ ] Legal review completed

## 🏷️ Labels: `gdpr`, `compliance`, `p0`, `api`, `data-rights`, `right-to-be-forgotten`

---

**Estimated Days**: 15 days | **Phase**: GDPR Phase 2
