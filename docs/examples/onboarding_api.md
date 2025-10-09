# Onboarding API Documentation

**Part of BATCH-COPILOT-2025-10-08-01**  
**TaskID**: ASSIST-LOW-README-ONBOARD-a3b4c5d6

## Overview

The LUKHAS Onboarding API provides a streamlined, GDPR-compliant user onboarding flow with integrated identity creation (ΛID), consent management, and tier assignment.

## Quick Start

### 1. Initiate Onboarding

```python
from candidate.bridge.api.onboarding import OnboardingAPI

onboarding = OnboardingAPI()

# Start onboarding flow
session = onboarding.start(
    jwt_token="eyJhbGciOiJIUz...",  # Valid JWT
    user_data={
        "email": "user@example.com",
        "name": "Test User",
        "tier": "free"
    },
    consent={
        "essential": True,  # Required
        "analytics": True,
        "marketing": False
    }
)

print(f"Onboarding Session: {session['session_id']}")
print(f"Lambda ID: {session['lambda_id']}")
```

### 2. Complete Required Steps

```python
# Step 1: Verify Email
verification_result = onboarding.verify_email(
    session_id=session["session_id"],
    verification_code="123456"
)

# Step 2: Set Up Profile
profile_result = onboarding.setup_profile(
    session_id=session["session_id"],
    profile_data={
        "bio": "AI researcher",
        "preferences": {
            "theme": "dark",
            "language": "en"
        }
    }
)

# Step 3: Review Terms & Finalize
finalize_result = onboarding.finalize(
    session_id=session["session_id"],
    terms_accepted=True
)

print(f"Onboarding Complete: {finalize_result['status']}")
```

## API Endpoints

### POST /onboarding/start

Initiate new onboarding session.

**Request**:
```json
{
  "user_data": {
    "email": "user@example.com",
    "name": "Test User",
    "tier": "free"
  },
  "consent": {
    "essential": true,
    "analytics": true,
    "marketing": false
  }
}
```

**Headers**:
```
Authorization: Bearer <JWT_TOKEN>
```

**Response** (201 Created):
```json
{
  "status": "success",
  "session_id": "onboard_abc123xyz",
  "lambda_id": "λ_user_789",
  "tier": "free",
  "steps": [
    {"id": "email_verify", "status": "pending"},
    {"id": "profile_setup", "status": "pending"},
    {"id": "terms_review", "status": "pending"}
  ],
  "expires_at": "2025-10-09T12:00:00Z"
}
```

### POST /onboarding/{session_id}/verify-email

Verify email address.

**Request**:
```json
{
  "verification_code": "123456"
}
```

**Response** (200 OK):
```json
{
  "status": "verified",
  "step_completed": "email_verify"
}
```

### POST /onboarding/{session_id}/profile

Set up user profile.

**Request**:
```json
{
  "profile_data": {
    "bio": "AI researcher",
    "avatar_url": "https://example.com/avatar.jpg",
    "preferences": {
      "theme": "dark",
      "language": "en",
      "notifications": true
    }
  }
}
```

**Response** (200 OK):
```json
{
  "status": "profile_updated",
  "step_completed": "profile_setup"
}
```

### POST /onboarding/{session_id}/finalize

Complete onboarding process.

**Request**:
```json
{
  "terms_accepted": true,
  "privacy_policy_accepted": true
}
```

**Response** (200 OK):
```json
{
  "status": "completed",
  "user_id": "user_123",
  "lambda_id": "λ_user_789",
  "tier": "free",
  "access_token": "eyJhbGciOiJIUz...",
  "refresh_token": "eyJhbGciOiJIUz...",
  "onboarded_at": "2025-10-09T10:30:00Z"
}
```

## Error Handling

### Common Errors

| Status Code | Error Code | Description |
|------------|------------|-------------|
| 400 | `INVALID_REQUEST` | Missing or invalid parameters |
| 401 | `UNAUTHORIZED` | Invalid or expired JWT token |
| 403 | `CONSENT_REQUIRED` | Essential consent not granted |
| 404 | `SESSION_NOT_FOUND` | Onboarding session expired or invalid |
| 409 | `EMAIL_EXISTS` | Email already registered |
| 429 | `RATE_LIMIT` | Too many onboarding attempts |

### Error Response Format

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Email address is required",
    "details": {
      "field": "user_data.email",
      "requirement": "valid email format"
    }
  }
}
```

### Example Error Handling

```python
try:
    session = onboarding.start(jwt_token=token, user_data=data)
except OnboardingError as e:
    if e.code == "EMAIL_EXISTS":
        print("Email already registered. Try logging in instead.")
    elif e.code == "CONSENT_REQUIRED":
        print("Essential consent is required to proceed.")
    else:
        print(f"Onboarding failed: {e.message}")
```

## Tier-Based Features

### Free Tier
- Basic consciousness features
- Limited API calls (1000/month)
- Community support

### Pro Tier
- Advanced consciousness features
- Higher API limits (50,000/month)
- Priority support
- MEG integration

### Enterprise Tier
- Full consciousness suite
- Unlimited API calls
- Dedicated support
- Custom integrations
- SLA guarantees

## GDPR Compliance

### Consent Management

All consent is recorded with:
- Timestamp
- IP address
- User agent
- Consent version
- Audit trail (ΛTRACE)

### Right to Access

```python
# User can request their data
data_export = onboarding.request_data_export(user_id="user_123")
```

### Right to Deletion

```python
# User can request account deletion
deletion_request = onboarding.request_deletion(
    user_id="user_123",
    reason="gdpr_right_to_erasure"
)
```

## Trinity Framework Integration

### Identity (⚛️)

Every onboarded user receives a Lambda ID (ΛID):

```python
lambda_id = session["lambda_id"]  # e.g., "λ_user_789"
```

### Consciousness (🧠)

Onboarding activates consciousness features:

```python
consciousness_status = onboarding.get_consciousness_status(lambda_id)
# Returns: {"state": "active", "awareness_level": 0.75}
```

### Guardian (🛡️)

Guardian system monitors onboarding:

```python
guardian_check = onboarding.guardian_review(session_id)
# Returns: {"status": "approved", "flags": []}
```

## Testing

### Unit Test Example

```python
import pytest

def test_onboarding_start_success():
    """Test successful onboarding initiation."""
    onboarding = OnboardingAPI()
    
    session = onboarding.start(
        jwt_token="valid_token",
        user_data={"email": "test@example.com"},
        consent={"essential": True}
    )
    
    assert session["status"] == "success"
    assert "session_id" in session
    assert "lambda_id" in session
```

### Integration Test Example

```python
@pytest.mark.integration
def test_complete_onboarding_flow():
    """Test complete onboarding from start to finish."""
    onboarding = OnboardingAPI()
    
    # Start
    session = onboarding.start(...)
    
    # Verify email
    onboarding.verify_email(session["session_id"], "123456")
    
    # Setup profile
    onboarding.setup_profile(session["session_id"], {...})
    
    # Finalize
    result = onboarding.finalize(session["session_id"], terms_accepted=True)
    
    assert result["status"] == "completed"
```

## Best Practices

1. **Always validate JWT tokens** before starting onboarding
2. **Require essential consent** for GDPR compliance
3. **Set session expiration** (default: 30 minutes)
4. **Log all steps** to ΛTRACE audit system
5. **Handle errors gracefully** with user-friendly messages
6. **Support session resumption** for interrupted flows

## Rate Limiting

- **Start onboarding**: 5 requests per IP per hour
- **Email verification**: 3 attempts per session
- **Profile updates**: 10 requests per session

## Webhooks

Subscribe to onboarding events:

```python
webhook_config = {
    "url": "https://your-app.com/webhooks/onboarding",
    "events": ["onboarding.completed", "onboarding.failed"],
    "secret": "your_webhook_secret"
}

onboarding.configure_webhook(webhook_config)
```

## Support

- Documentation: https://docs.lukhas.ai/onboarding
- API Reference: https://api.lukhas.ai/docs
- Support: support@lukhas.ai

---

**⚛️🧠🛡️ LUKHAS AI Platform - Seamless Onboarding**
