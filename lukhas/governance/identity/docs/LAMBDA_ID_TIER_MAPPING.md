<!--
════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - LAMBDA ID (ΛID) TO TIER MAPPING DOCUMENTATION
║ Comprehensive guide to user identity and tier-based access control
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠═══════════════════════════════════════════════════════════════════════════════
║ Document: LAMBDA_ID_TIER_MAPPING.md
║ Path: lukhas/identity/docs/LAMBDA_ID_TIER_MAPPING.md
║ Version: 1.0.0 | Created: 2025-07-26 | Modified: 2025-07-26
║ Authors: LUKHAS AI Identity Team
╚═══════════════════════════════════════════════════════════════════════════════
-->

# Lambda ID (ΛID) to Tier Mapping Documentation

## Overview

The LUKHAS identity system uses Lambda IDs (ΛID) as unique user identifiers that are directly linked to tier-based access control throughout the AGI system. This document explains how ΛIDs are mapped to tiers and how this affects module access.

## Table of Contents

1. [Lambda ID Structure](#lambda-id-structure)
2. [Tier Levels](#tier-levels)
3. [Mapping System](#mapping-system)
4. [Module Access Matrix](#module-access-matrix)
5. [Implementation Details](#implementation-details)
6. [API Usage](#api-usage)
7. [Best Practices](#best-practices)

## Lambda ID Structure

Lambda IDs (ΛID) are unique identifiers with the following characteristics:

- **Format**: Can be any string, but typically follow patterns like:
  - System users: `system_*` (e.g., `system_root`)
  - Admin users: `admin_*` (e.g., `admin_001`)
  - Regular users: Custom format based on identity service
  - Test users: `test_user_tier*` (e.g., `test_user_tier2`)

- **Persistence**: ΛIDs are permanent and tied to user profiles
- **Portability**: Can be used across different LUKHAS services

## Tier Levels

The system uses 6 tier levels, each granting progressively more access:

| Tier | Name | Level | Description | Default Permissions |
|------|------|-------|-------------|-------------------|
| LAMBDA_TIER_0 | PUBLIC | 0 | Basic public access | Read public data only |
| LAMBDA_TIER_1 | AUTHENTICATED | 1 | Standard authenticated user | Read/write personal data |
| LAMBDA_TIER_2 | ELEVATED | 2 | Elevated permissions | Memory operations, basic AI features |
| LAMBDA_TIER_3 | PRIVILEGED | 3 | Privileged access | Dream generation, consciousness access |
| LAMBDA_TIER_4 | ADMIN | 4 | Administrative access | User management, system configuration |
| LAMBDA_TIER_5 | SYSTEM | 5 | System-level access | Full control, internal operations |

## Mapping System

### Database-Backed Mapping

The new `UserTierMappingService` provides persistent tier assignments:

```python
from lukhas.identity.core.user_tier_mapping import get_tier_mapping_service

service = get_tier_mapping_service()

# Get user's current tier
tier = service.get_user_tier("user_lambda_id")

# Set user's tier
service.set_user_tier(
    lambda_id="user_lambda_id",
    tier=LambdaTier.LAMBDA_TIER_3,
    reason="Premium subscription activated"
)

# Temporary tier elevation
service.set_user_tier(
    lambda_id="user_lambda_id",
    tier=LambdaTier.LAMBDA_TIER_4,
    reason="Admin task delegation",
    duration_minutes=60  # Expires after 1 hour
)
```

### User Profile Structure

Each ΛID is associated with a complete profile:

```python
{
    "lambda_id": "user_123",
    "current_tier": "LAMBDA_TIER_2",
    "tier_level": 2,
    "tier_history": [
        {
            "from_tier": "LAMBDA_TIER_1",
            "to_tier": "LAMBDA_TIER_2",
            "timestamp": "2025-07-26T10:00:00Z",
            "reason": "Subscription upgrade",
            "temporary": false
        }
    ],
    "permissions": {
        "read_public": true,
        "read_personal": true,
        "write_personal": true,
        "memory_access": true,
        "memory_write": true,
        "dream_generation": false,
        "consciousness_access": false,
        "quantum_access": false,
        "admin_access": false,
        "system_access": false
    },
    "metadata": {
        "name": "John Doe",
        "subscription": "elevated",
        "created_date": "2025-01-15"
    },
    "created_at": "2025-01-15T09:00:00Z",
    "updated_at": "2025-07-26T10:00:00Z",
    "tier_expiry": null
}
```

## Module Access Matrix

### Memory Module
| Operation | Required Tier | Description |
|-----------|--------------|-------------|
| Read public memories | TIER_0 | Access shared knowledge base |
| Read personal memories | TIER_1 | Access own memory store |
| Write memories | TIER_2 | Create and modify memories |
| Memory fold operations | TIER_2 | Advanced memory compression |
| Cross-user memory access | TIER_4 | Admin memory management |

### Consciousness Module
| Operation | Required Tier | Description |
|-----------|--------------|-------------|
| View consciousness metrics | TIER_1 | Basic awareness data |
| Consciousness introspection | TIER_2 | Detailed state analysis |
| Modify consciousness parameters | TIER_3 | Adjust awareness settings |
| System consciousness access | TIER_5 | Core consciousness control |

### Dream Module
| Operation | Required Tier | Description |
|-----------|--------------|-------------|
| View dreams | TIER_1 | Access dream history |
| Create dreams | TIER_2 | Basic dream generation |
| Generate lucid dreams | TIER_3 | Advanced dream creation |
| Admin dream control | TIER_4 | Manage all user dreams |

### Quantum Module
| Operation | Required Tier | Description |
|-----------|--------------|-------------|
| Quantum state observation | TIER_3 | View quantum-like states |
| Quantum manipulation | TIER_4 | Modify quantum parameters |
| Quantum system reset | TIER_5 | System-level quantum control |

## Implementation Details

### Identity Interface Integration

The `IdentityClient` automatically checks tier levels:

```python
from lukhas.identity.interface import IdentityClient

client = IdentityClient()

# Check tier access
if client.verify_user_access(user_id="lambda_123", required_tier="LAMBDA_TIER_3"):
    # User has Tier 3 or higher
    perform_privileged_operation()
```

### Decorator-Based Access Control

Use decorators for automatic tier validation:

```python
from lukhas.core.identity_integration import require_identity

@require_identity(required_tier="LAMBDA_TIER_3", check_consent="dream_generation")
def generate_dream(user_id: str, dream_params: dict):
    # Function automatically validates tier and consent
    return create_dream(dream_params)
```

### Context-Based Access

For granular control within functions:

```python
from lukhas.core.identity_integration import IdentityContext

def adaptive_function(user_id: str, data: dict):
    result = {}
    
    # Basic features for all authenticated users
    with IdentityContext(user_id, "LAMBDA_TIER_1") as ctx:
        if ctx.has_access:
            result["basic"] = process_basic(data)
    
    # Advanced features for elevated users
    with IdentityContext(user_id, "LAMBDA_TIER_3") as ctx:
        if ctx.has_access:
            result["advanced"] = process_advanced(data)
        else:
            result["upgrade_prompt"] = "Upgrade to Tier 3 for advanced features"
    
    return result
```

## API Usage

### Check User Tier

```python
from lukhas.identity.core.user_tier_mapping import get_user_tier

# Get tier name
tier_name = get_user_tier("user_lambda_id")  # Returns "LAMBDA_TIER_2"
```

### Validate Tier Access

```python
from lukhas.identity.core.user_tier_mapping import check_tier_access

# Check if user meets required tier
has_access = check_tier_access("user_lambda_id", "LAMBDA_TIER_3")
```

### Elevate User Tier

```python
from lukhas.identity.core.user_tier_mapping import elevate_user_tier

# Temporarily elevate for admin task
success = elevate_user_tier(
    lambda_id="user_lambda_id",
    target_tier="LAMBDA_TIER_4",
    reason="Delegated admin task",
    duration_minutes=30
)
```

### Check Specific Permission

```python
from lukhas.identity.core.user_tier_mapping import get_tier_mapping_service

service = get_tier_mapping_service()
can_access_quantum = service.check_permission("user_lambda_id", "quantum_access")
```

## Best Practices

### 1. Always Validate Tiers

Never assume a user's tier based on their ΛID format:

```python
# Bad - assumes tier from ID
if user_id.startswith("admin_"):
    grant_admin_access()

# Good - checks actual tier
if check_tier_access(user_id, "LAMBDA_TIER_4"):
    grant_admin_access()
```

### 2. Use Appropriate Tier Requirements

Set tier requirements based on actual security needs:

- **TIER_1**: For any authenticated user operation
- **TIER_2**: For features that consume resources
- **TIER_3**: For premium features or sensitive operations
- **TIER_4**: For administrative functions
- **TIER_5**: Reserved for system internals only

### 3. Log Tier-Based Decisions

Always log when access is granted or denied:

```python
if not check_tier_access(user_id, required_tier):
    logger.warning(
        "Access denied",
        user_id=user_id,
        required_tier=required_tier,
        operation=operation_name
    )
    return {"error": "Insufficient tier level"}
```

### 4. Handle Tier Expiration

For temporary elevations, always check expiration:

```python
profile = service.get_user_profile(user_id)
if profile.get("tier_expiry"):
    expiry = datetime.fromisoformat(profile["tier_expiry"])
    if datetime.now(timezone.utc) > expiry:
        # Tier has expired, user reverted to base tier
        notify_user("Your temporary access has expired")
```

### 5. Provide Clear Error Messages

Help users understand tier requirements:

```python
TIER_ERROR_MESSAGES = {
    "LAMBDA_TIER_1": "This feature requires an authenticated account",
    "LAMBDA_TIER_2": "This feature requires an elevated account (Tier 2+)",
    "LAMBDA_TIER_3": "This feature is available for privileged users (Tier 3+)",
    "LAMBDA_TIER_4": "This operation requires administrative access",
    "LAMBDA_TIER_5": "This is a system-only operation"
}
```

## Migration from Prefix-Based System

If you have code using the old prefix-based system:

```python
# Old system
if user_id.startswith("admin_"):
    # Admin logic

# New system
from lukhas.identity.core.user_tier_mapping import check_tier_access

if check_tier_access(user_id, "LAMBDA_TIER_4"):
    # Admin logic
```

The new system maintains backward compatibility for special prefixes but should not be relied upon.

## Conclusion

The ΛID to tier mapping system provides a robust, scalable foundation for access control across all LUKHAS modules. By properly implementing tier checks and following best practices, you ensure secure, consistent access control throughout the AGI system.

For questions or additional support, contact the LUKHAS Identity Team.