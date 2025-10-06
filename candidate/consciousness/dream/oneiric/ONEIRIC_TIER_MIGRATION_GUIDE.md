---
status: wip
type: documentation
---
# Oneiric Dream Engine - Unified Tier Migration Guide

## Overview

This guide provides step-by-step instructions for migrating the Oneiric Dream Engine to use the unified LUKHAS tier system. The migration maintains backward compatibility while adding support for centralized identity and consent management.

## Migration Steps

### 1. Update Authentication Middleware

Replace the existing `auth_middleware.py` with `auth_middleware_unified.py` or update your imports:

```python
# Old import
from oneiric_core.identity.auth_middleware import get_current_user, lukhas_tier_required

# New import
from oneiric_core.identity.auth_middleware_unified import (
    get_current_user,
    oneiric_tier_required,
    require_lambda_tier,
    AuthUser,
    get_user_tier_features
)
```

### 2. Update Endpoint Decorators

Replace tier validation decorators in your endpoints:

#### Before:
```python
@lukhas_tier_required(3)
async def create_dream(request: Request):
    user = request.state.user
    # Process dream
```

#### After:
```python
@oneiric_tier_required(3, check_consent="dream_generation")
async def create_dream(user: AuthUser = Depends(get_current_user)):
    # User is automatically injected with tier validation
    # Process dream with user context
```

### 3. Add User Context to All Endpoints

Update endpoints to receive user context:

#### Before:
```python
@app.post("/dream/process")
async def process_dream(request: DreamRequest):
    # No user context
    result = dream_engine.process(request.dream_content)
    return result
```

#### After:
```python
@app.post("/dream/process")
@oneiric_tier_required(2, check_consent="dream_processing")
async def process_dream(
    request: DreamRequest,
    user: AuthUser = Depends(get_current_user)
):
    # User context available
    tier_features = await get_user_tier_features(user)

    # Apply tier-based processing
    if tier_features.get("quantum_enhancement"):
        result = dream_engine.process_quantum(request.dream_content, user.lukhas_id)
    else:
        result = dream_engine.process_basic(request.dream_content, user.lukhas_id)

    return result
```

### 4. Run Database Migration

Apply the database migration to add unified tier support:

```bash
# Navigate to Oneiric directory
cd lukhas/creativity/dream/oneiric_engine

# Run the migration
alembic upgrade head
```

This will:
- Add `lambda_tier` column to users table
- Add `consent_grants` for tracking permissions
- Create automatic sync between tier and lambda_tier
- Migrate existing users to the new format

### 5. Update User Model

The `AuthUser` model now includes both tier systems:

```python
class AuthUser(BaseModel):
    id: str
    email: Optional[str] = None
    tier: int = 1  # Oneiric tier (1-5)
    lambda_tier: str = "LAMBDA_TIER_1"  # Unified tier
    lukhas_id: Optional[str] = None
```

### 6. Implement Tier-Based Features

Use the tier features helper to implement tier-specific functionality:

```python
async def process_dream_with_features(user: AuthUser, dream_content: str):
    features = await get_user_tier_features(user)

    result = {
        "content": dream_content,
        "max_storage": features["dream_storage"],
        "quantum_enabled": features["quantum_enhancement"],
        "symbolic_access": features["symbolic_access"]
    }

    # Tier-specific processing
    if user.tier >= 4:  # Advanced features
        result["co_dreaming_available"] = True
        result["advanced_analysis"] = await perform_advanced_analysis(dream_content)

    return result
```

### 7. Add Consent Checking

Implement consent validation for sensitive operations:

```python
@app.post("/dream/share")
@oneiric_tier_required(4, check_consent="dream_sharing")
async def share_dream(
    dream_id: str,
    share_with: List[str],
    user: AuthUser = Depends(get_current_user)
):
    # Consent is automatically checked by decorator
    # If user hasn't granted "dream_sharing" consent, 403 is returned

    # Proceed with sharing logic
    await dream_sharing_service.share(dream_id, share_with, user.lukhas_id)
```

## Consent Management

### Consent Types for Dream Engine

Define the following consent types:

- `dream_processing` - Basic dream processing
- `dream_storage` - Storing dreams long-term
- `dream_analysis` - Deep analysis of dream content
- `dream_sharing` - Sharing dreams with other users
- `memory_snapshot` - Creating memory snapshots
- `quantum_enhancement` - Using quantum-inspired processing
- `emotional_extraction` - Extracting emotional data

### Updating User Consent

```python
async def update_user_consent(user_id: str, consent_type: str, granted: bool):
    """Update user's consent in the database"""
    connection = await get_db_connection()

    await connection.execute("""
        UPDATE users
        SET consent_grants = consent_grants || %s
        WHERE id = %s
    """, (
        json.dumps({consent_type: {
            "granted": granted,
            "timestamp": datetime.now().isoformat()
        }}),
        user_id
    ))
```

## Testing the Migration

### 1. Test Tier Mapping

```python
def test_tier_mapping():
    """Verify tier mapping works correctly"""
    # Test user with Oneiric tier 3
    user = AuthUser(id="test", tier=3)
    assert user.lambda_tier == "LAMBDA_TIER_3"

    # Test tier validation
    adapter = OneiricTierAdapter()
    assert adapter.validate_access("test_user", 3) == True
    assert adapter.validate_access("test_user", 4) == False
```

### 2. Test Consent Validation

```python
async def test_consent_checking():
    """Test that consent is properly validated"""
    # Create test user without consent
    user = AuthUser(id="test", tier=3, lukhas_id="Λtest123")

    # This should fail without consent
    with pytest.raises(HTTPException) as exc:
        await dream_endpoint_requiring_consent(user)

    assert exc.value.status_code == 403
    assert "Consent required" in exc.value.detail
```

### 3. Test Feature Gating

```python
async def test_tier_features():
    """Test tier-based feature availability"""
    # Tier 2 user
    user_t2 = AuthUser(id="t2", tier=2)
    features_t2 = await get_user_tier_features(user_t2)
    assert features_t2["quantum_enhancement"] == False
    assert features_t2["dream_storage"] == 50

    # Tier 4 user
    user_t4 = AuthUser(id="t4", tier=4)
    features_t4 = await get_user_tier_features(user_t4)
    assert features_t4["quantum_enhancement"] == True
    assert features_t4["co_dreaming"] == True
```

## Rollback Procedure

If issues arise, you can rollback the migration:

```bash
# Rollback database migration
alembic downgrade -1

# Revert to original auth middleware
git checkout -- oneiric_core/identity/auth_middleware.py

# Remove unified imports from endpoints
# Revert endpoint changes to original format
```

## Benefits of Migration

1. **Unified Access Control**: Consistent tier validation across all LUKHAS modules
2. **Consent Management**: Fine-grained permission control
3. **Central Identity**: Integration with LUKHAS identity system
4. **Activity Logging**: Automatic logging of user activities
5. **Future-Proof**: Easy to add new tier levels or features

## Common Issues and Solutions

### Issue: "User not found in request"
**Solution**: Ensure you're using `Depends(get_current_user)` in endpoint parameters

### Issue: "Invalid tier format"
**Solution**: Use integer tiers (1-5) with `@oneiric_tier_required` or LAMBDA_TIER format with `@require_lambda_tier`

### Issue: "Consent check failing for all users"
**Solution**: Verify consent_grants column exists in database and run migration

## Next Steps

1. Update all existing endpoints to use the new decorators
2. Implement consent UI for users to manage permissions
3. Add tier upgrade/downgrade workflows
4. Monitor tier distribution using the statistics view
5. Implement tier-based pricing/limits in business logic

Remember: The goal is gradual migration. Both old and new decorators work during the transition period.
