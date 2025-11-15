# GDPR Issue 10: Implement Right to Rectification API (GDPR Art. 16)

## Priority: P0 - GDPR Core Compliance
## Estimated Effort: 10 days
## Target: Complete Right to Rectification API

---

## 🎯 Objective

Implement the Right to Rectification API (GDPR Article 16) allowing users to correct inaccurate personal data.

## 📊 Current State

- **GDPR Compliance**: 58%
- **Data Subject Rights APIs**: 0/4 implemented
- **Legal Requirement**: GDPR Article 16
- **Target**: 75% GDPR compliance

## 🔍 Background

GDPR Article 16 grants the right to:
- Correct inaccurate personal data
- Complete incomplete data
- Have corrections applied promptly

## 📋 Deliverables

### 1. API Endpoint

```python
@router.patch("/users/{user_id}/data")
async def rectify_user_data(
    user_id: str,
    corrections: Dict[str, Any],
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Right to Rectification - GDPR Article 16.
    
    Allow users to correct inaccurate personal data.
    """
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(403, "Can only rectify own data")
    
    # Validate corrections
    validated = validate_corrections(corrections)
    
    # Apply corrections with audit trail
    results = await apply_data_corrections(user_id, validated)
    
    return {
        "status": "completed",
        "corrected_fields": list(validated.keys()),
        "corrected_at": datetime.utcnow().isoformat()
    }
```

### 2. Validation

```python
def validate_corrections(corrections: Dict[str, Any]) -> Dict[str, Any]:
    """Validate correction data."""
    validated = {}
    
    allowed_fields = [
        "email", "name", "preferences", "profile"
    ]
    
    for field, value in corrections.items():
        if field not in allowed_fields:
            raise ValueError(f"Cannot modify field: {field}")
        
        # Field-specific validation
        if field == "email":
            if not is_valid_email(value):
                raise ValueError(f"Invalid email: {value}")
        
        validated[field] = value
    
    return validated
```

### 3. Testing

```python
@pytest.mark.asyncio
async def test_rectify_email():
    """Test email correction."""
    response = await client.patch(
        "/v1/data-rights/users/user123/data",
        json={"email": "newemail@example.com"}
    )
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_prevent_unauthorized_fields():
    """Test that unauthorized fields cannot be modified."""
    response = await client.patch(
        "/v1/data-rights/users/user123/data",
        json={"is_admin": True}  # Should be rejected
    )
    assert response.status_code == 400
```

### 4. Documentation

- [ ] Create `docs/gdpr/RIGHT_TO_RECTIFICATION_API.md`
- [ ] Field modification permissions
- [ ] Validation rules

## ✅ Acceptance Criteria

- [ ] API endpoint implemented
- [ ] Field validation in place
- [ ] Audit trail for corrections
- [ ] Unit tests with >80% coverage
- [ ] Documentation complete

## 🏷️ Labels: `gdpr`, `compliance`, `p0`, `api`, `data-correction`

---

**Estimated Days**: 10 days | **Phase**: GDPR Phase 2
