# Feature Flags Guide

**Privacy-First Feature Flags for LUKHAS AI**

This guide explains how to create, manage, and use feature flags in LUKHAS AI for controlled rollouts, A/B testing, and safe experimentation.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Flag Types](#flag-types)
- [Creating a New Flag](#creating-a-new-flag)
- [Using Flags in Code](#using-flags-in-code)
- [Rollout Strategy](#rollout-strategy)
- [Best Practices](#best-practices)
- [Privacy Considerations](#privacy-considerations)
- [Cleanup Process](#cleanup-process)
- [API Reference](#api-reference)
- [Testing](#testing)

## Overview

LUKHAS AI's feature flags system provides:

- **5 Flag Types**: Boolean, percentage, user targeting, time-based, environment-based
- **Privacy-First**: No user tracking without consent, local-first evaluation
- **Zero Dependencies**: No third-party services (LaunchDarkly, Split.io, etc.)
- **Safe Rollouts**: Gradual deployment from 0% → 1% → 10% → 50% → 100%
- **A/B Testing**: Built-in support for experimentation
- **Developer-Friendly**: Simple API, testing utilities, admin UI

## Quick Start

### 1. Create a Flag

Add to `branding/features/flags.yaml`:

```yaml
flags:
  my_new_feature:
    type: boolean
    enabled: false
    description: "My awesome new feature"
    owner: "team@lukhas.ai"
    created_at: "2025-11-08"
    jira_ticket: "GAPS-123"
    fallback: false
```

### 2. Validate Configuration

```bash
make flags-validate
# or
python tools/validate_flags.py
```

### 3. Use in Code

**Python:**

```python
from lukhas.features import is_enabled, FlagEvaluationContext

# Simple check
if is_enabled('my_new_feature'):
    # New feature code
    pass

# With context
context = FlagEvaluationContext(
    user_id="user-123",
    email="user@lukhas.ai",
    environment="prod"
)
if is_enabled('my_new_feature', context):
    # Feature enabled for this user
    pass
```

**Frontend (React/TypeScript):**

```typescript
import { useFeatureFlag } from '@/hooks/useFeatureFlag';

function MyComponent() {
  const { enabled, loading } = useFeatureFlag('my_new_feature');

  if (loading) return <Spinner />;
  if (!enabled) return null;

  return <NewFeature />;
}
```

## Flag Types

### 1. Boolean Flags

Simple on/off toggle for entire system.

```yaml
reasoning_lab_enabled:
  type: boolean
  enabled: false
  description: "Enable Reasoning Lab feature"
  owner: "platform-team@lukhas.ai"
  created_at: "2025-11-08"
  jira_ticket: "GAPS-B5"
```

**Use Case**: Feature toggles, kill switches, simple feature gates

### 2. Percentage Rollout

Gradual rollout to percentage of users (0-100%).

```yaml
matriz_v2_rollout:
  type: percentage
  enabled: true
  percentage: 10  # 10% of users
  description: "Gradual rollout of MATRIZ v2"
  owner: "consciousness-team@lukhas.ai"
  created_at: "2025-11-08"
  jira_ticket: "GAPS-B5"
```

**Use Case**: Gradual deployments, canary releases, A/B testing

**How It Works**: Uses consistent hashing on `user_id + flag_name` to ensure same user always gets same result.

### 3. User Targeting

Target specific users by email domain or privacy-preserving hash.

```yaml
enhanced_memory_beta:
  type: user_targeting
  enabled: true
  description: "Beta access for internal team"
  owner: "memory-team@lukhas.ai"
  created_at: "2025-11-08"
  allowed_domains:
    - "lukhas.ai"
    - "lukhas.com"
  # Optional: target specific users by SHA-256 hash
  # allowed_user_hashes:
  #   - "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"
```

**Use Case**: Internal testing, beta programs, VIP access

**Privacy Note**: User hashes are SHA-256 to prevent PII exposure in config.

### 4. Time-Based Flags

Enable/disable based on date/time.

```yaml
new_landing_page:
  type: time_based
  enabled: true
  description: "New landing page - go live Dec 1, 2025"
  owner: "marketing-team@lukhas.ai"
  created_at: "2025-11-08"
  enable_after: "2025-12-01T00:00:00Z"
  # Optional: disable_after: "2026-01-01T00:00:00Z"
```

**Use Case**: Scheduled launches, time-limited features, campaign launches

### 5. Environment-Based Flags

Enable only in specific environments (dev/staging/prod).

```yaml
debug_mode:
  type: environment
  enabled: true
  description: "Debug logging in non-prod environments"
  owner: "platform-team@lukhas.ai"
  created_at: "2025-11-08"
  allowed_environments:
    - "dev"
    - "staging"
```

**Use Case**: Debug features, testing tools, environment-specific behavior

## Creating a New Flag

### 1. Define the Flag

Add to `branding/features/flags.yaml`:

```yaml
my_new_feature:
  type: boolean  # or percentage, user_targeting, time_based, environment
  enabled: false  # Start disabled for safety
  description: "Clear description of what this flag does"
  owner: "your-team@lukhas.ai"
  created_at: "2025-11-08"
  jira_ticket: "GAPS-XXX"  # Link to ticket/issue
  fallback: false  # Safe default on errors
```

### 2. Validate Configuration

```bash
make flags-validate
```

### 3. Add to Version Control

```bash
git add branding/features/flags.yaml
git commit -m "feat(features): add my_new_feature flag"
```

### 4. Deploy Configuration

Flags are reloaded automatically with TTL (default: 60 seconds). For immediate reload:

```bash
curl -X POST http://api.lukhas.ai/api/features/my_new_feature/reload \
  -H "X-API-Key: admin_YOUR_KEY"
```

## Using Flags in Code

### Python Backend

```python
from lukhas.features import is_enabled, FlagEvaluationContext

# Simple boolean check
if is_enabled('reasoning_lab_enabled'):
    # Feature code
    pass

# With user context (for percentage/targeting)
context = FlagEvaluationContext(
    user_id="user-123",
    email="user@example.com",
    environment="prod"
)

if is_enabled('matriz_v2_rollout', context):
    # User is in the rollout percentage
    use_matriz_v2()
else:
    use_matriz_v1()
```

### React/TypeScript Frontend

```typescript
import { useFeatureFlag } from '@/hooks/useFeatureFlag';

function MyComponent() {
  const { enabled, loading, error } = useFeatureFlag('my_feature');

  if (loading) return <Spinner />;
  if (error) return <ErrorState />;
  if (!enabled) return <OldFeature />;

  return <NewFeature />;
}
```

### FastAPI Endpoints

```python
from lukhas.features import is_enabled
from fastapi import APIRouter

router = APIRouter()

@router.get("/my-endpoint")
async def my_endpoint():
    if is_enabled('new_api_format'):
        return {"version": "v2", "data": [...]}
    else:
        return {"data": [...]}  # Legacy format
```

## Rollout Strategy

### Recommended Rollout Schedule

For major features, use gradual percentage rollout:

| Phase | Percentage | Duration | Action |
|-------|-----------|----------|--------|
| 1. Internal | 0% | 1-2 days | Internal testing only |
| 2. Canary | 1% | 1-2 days | Monitor metrics closely |
| 3. Small | 10% | 2-3 days | Check error rates, performance |
| 4. Medium | 50% | 3-5 days | A/B test results, user feedback |
| 5. Full | 100% | - | Full rollout complete |

### Monitoring During Rollout

**Key Metrics to Monitor:**

- Error rate (should not increase)
- Performance metrics (latency, throughput)
- User feedback/complaints
- Resource usage (CPU, memory)

**Rollback Process:**

If issues detected, immediately reduce percentage or disable flag:

```yaml
# Rollback: reduce to 1%
my_feature:
  percentage: 1

# Emergency: disable completely
my_feature:
  enabled: false
```

### A/B Testing

For 50/50 A/B tests:

```yaml
onboarding_flow_v2:
  type: percentage
  enabled: true
  percentage: 50  # 50% get new flow, 50% get old
  description: "A/B test for new onboarding"
```

Track metrics for both groups and analyze results.

## Best Practices

### Naming Conventions

- Use `snake_case` for flag names
- Include feature name: `reasoning_lab_enabled`
- For rollouts: `feature_name_rollout`
- For experiments: `experiment_name_variant`

**Good Names:**
- `matriz_v2_rollout`
- `enhanced_memory_beta`
- `new_landing_page`

**Bad Names:**
- `flag1`, `test`, `temp` (not descriptive)
- `ReasoningLab` (use snake_case)

### Default Values

- **New flags**: Start with `enabled: false` for safety
- **Fallback**: Set `fallback: false` (fail safe)
- **Percentage**: Start at 0%, increase gradually

### Documentation

- **Description**: Clear, concise (1-2 sentences)
- **Owner**: Team email address
- **JIRA Ticket**: Always link to ticket/issue
- **Created Date**: ISO format (YYYY-MM-DD)

### Flag Lifecycle

1. **Create**: Add flag, start disabled
2. **Test**: Internal testing with targeting
3. **Rollout**: Gradual percentage increase
4. **Monitor**: Track metrics, collect feedback
5. **Complete**: Reach 100% or determine winner
6. **Cleanup**: Remove flag from code and config

## Privacy Considerations

### NO User Tracking Without Consent

- Flag evaluations logged only in aggregate
- No individual user data stored
- Privacy-preserving hashes (SHA-256) for targeting

### User Hash Generation

To target specific users without PII in config:

```python
import hashlib

def get_user_hash(user_id: str) -> str:
    return hashlib.sha256(user_id.encode()).hexdigest()

# Add to config
allowed_user_hashes:
  - "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"
```

### GDPR Compliance

- No personal data in flag configurations
- Email domains OK (not individual emails)
- User IDs hashed for targeting
- Audit logs anonymized

## Cleanup Process

### When to Remove a Flag

Remove flags when:

- ✅ Feature fully rolled out (100%)
- ✅ A/B test completed (winner chosen)
- ✅ Feature permanently disabled
- ❌ Flag not used for 90+ days

### How to Remove a Flag

1. **Remove from code:**

```bash
# Search for flag usage
grep -r "my_old_flag" lukhas/ products/

# Remove all references
# Update code to use only new behavior
```

2. **Remove from config:**

```yaml
# Delete flag from branding/features/flags.yaml
# DO NOT comment out - delete completely
```

3. **Validate:**

```bash
make flags-validate
make test
```

4. **Document in PR:**

```markdown
## Flag Cleanup

Removed flag `my_old_flag`:
- Feature fully rolled out to 100% on 2025-10-15
- No issues reported during rollout
- All code updated to use new behavior
```

### Automated Cleanup Detection

Run periodically:

```bash
# Find unused flags
python tools/find_unused_flags.py

# Suggests flags for cleanup based on:
# - Last modified date
# - Usage in code
# - Rollout status
```

## API Reference

### Python API

```python
from lukhas.features import (
    is_enabled,
    get_service,
    FlagEvaluationContext,
    FlagType
)

# Check if flag is enabled
is_enabled('flag_name', context=None) -> bool

# Get service instance
service = get_service()

# Service methods
service.is_enabled(flag_name, context) -> bool
service.get_flag(flag_name) -> Optional[FeatureFlag]
service.list_flags() -> List[str]
service.get_all_flags() -> Dict[str, FeatureFlag]
service.reload() -> None

# Evaluation context
context = FlagEvaluationContext(
    user_id="user-123",
    email="user@example.com",
    environment="prod",
    timestamp=datetime.now(timezone.utc)
)
```

### REST API

**Authentication**: All endpoints require `X-API-Key` header.

**Rate Limit**: 100 requests/minute per user.

#### List All Flags (Admin Only)

```http
GET /api/features
X-API-Key: admin_YOUR_KEY
```

Response:
```json
{
  "flags": [
    {
      "name": "reasoning_lab_enabled",
      "enabled": false,
      "flag_type": "boolean",
      "description": "Enable Reasoning Lab",
      "owner": "platform-team@lukhas.ai",
      "created_at": "2025-11-08",
      "jira_ticket": "GAPS-B5"
    }
  ],
  "total": 1
}
```

#### Get Flag

```http
GET /api/features/reasoning_lab_enabled
X-API-Key: YOUR_KEY
```

#### Evaluate Flag

```http
POST /api/features/reasoning_lab_enabled/evaluate
X-API-Key: YOUR_KEY
Content-Type: application/json

{
  "user_id": "user-123",
  "email": "user@example.com",
  "environment": "prod"
}
```

Response:
```json
{
  "flag_name": "reasoning_lab_enabled",
  "enabled": true,
  "flag_type": "boolean"
}
```

#### Update Flag (Admin Only)

```http
PATCH /api/features/reasoning_lab_enabled
X-API-Key: admin_YOUR_KEY
Content-Type: application/json

{
  "enabled": true,
  "percentage": 50
}
```

#### Reload Flag (Admin Only)

```http
POST /api/features/reasoning_lab_enabled/reload
X-API-Key: admin_YOUR_KEY
```

## Testing

### Unit Tests with Fixtures

```python
import pytest
from lukhas.features.testing import (
    override_flag,
    override_flags,
    temp_flags_config
)

def test_feature_with_flag():
    """Test feature when flag is enabled."""
    with override_flag('reasoning_lab_enabled', True):
        result = my_feature_function()
        assert result.uses_reasoning_lab

def test_feature_without_flag():
    """Test feature when flag is disabled."""
    with override_flag('reasoning_lab_enabled', False):
        result = my_feature_function()
        assert not result.uses_reasoning_lab

def test_multiple_flags():
    """Test with multiple flag overrides."""
    with override_flags({
        'reasoning_lab_enabled': True,
        'matriz_v2_rollout': False,
    }):
        result = my_complex_feature()
        assert result.expected_behavior
```

### Pytest Fixtures

```python
def test_with_fixture(feature_flags, flag_context):
    """Test using pytest fixtures."""
    assert feature_flags.is_enabled('test_boolean_flag')

    context = flag_context
    assert context.user_id == "test-user-123"
```

### Integration Tests

```python
from fastapi.testclient import TestClient
from lukhas.api.features import router

client = TestClient(router)

def test_evaluate_flag_api():
    """Test flag evaluation API."""
    response = client.post(
        "/api/features/test_flag/evaluate",
        headers={"X-API-Key": "test_key"},
        json={
            "user_id": "user-123",
            "environment": "test"
        }
    )
    assert response.status_code == 200
    assert response.json()["enabled"] in [True, False]
```

## Tools

### Validation

```bash
# Validate flags configuration
make flags-validate
python tools/validate_flags.py

# Validate specific file
python tools/validate_flags.py path/to/flags.yaml
```

### Migration

```bash
# Migrate from old format
python tools/migrate_flags.py old_flags.yaml new_flags.yaml

# Force overwrite
python tools/migrate_flags.py old_flags.yaml new_flags.yaml --force
```

## Troubleshooting

### Flag Not Loading

**Problem**: Flag changes not reflecting in application.

**Solutions**:
1. Check cache TTL (default: 60s)
2. Force reload: `service.reload()`
3. Verify config path: `branding/features/flags.yaml`
4. Check file permissions

### Percentage Rollout Not Working

**Problem**: All users getting same result.

**Solutions**:
1. Ensure `user_id` provided in context
2. Check percentage value (0-100)
3. Verify flag type is `percentage`
4. Check if flag is globally disabled

### Authentication Errors

**Problem**: 401/403 errors from API.

**Solutions**:
1. Provide `X-API-Key` header
2. Admin endpoints require `admin_` prefix
3. Check rate limits (100/min)

## Support

- **Documentation**: `branding/features/FEATURE_FLAGS_GUIDE.md`
- **Issues**: [GitHub Issues](https://github.com/LukhasAI/Lukhas/issues)
- **JIRA**: GAPS-B5
- **Owner**: platform-team@lukhas.ai

---

**Last Updated**: 2025-11-08
**Schema Version**: 1.0
**GAPS Item**: B5 (Safe Rollouts & Experimentation)
