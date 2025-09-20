<!--
════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - IDENTITY INTEGRATION GUIDE
║ Comprehensive guide for integrating identity system across modules
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠═══════════════════════════════════════════════════════════════════════════════
║ Document: IDENTITY_INTEGRATION_GUIDE.md
║ Path: lukhas/identity/IDENTITY_INTEGRATION_GUIDE.md
║ Version: 1.0.0 | Created: 2025-07-26 | Modified: 2025-07-26
║ Authors: LUKHAS AI Core Team
╠═══════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠═══════════════════════════════════════════════════════════════════════════════
║ This guide provides comprehensive instructions for integrating the LUKHAS
║ identity system with tier-based access control across all modules.
╚═══════════════════════════════════════════════════════════════════════════════
-->

# LUKHAS Identity Integration Guide

## Overview

The LUKHAS identity system provides unified identity management, tier-based access control, consent management, and audit logging across all Cognitive modules. This guide explains how to properly integrate identity validation into your modules.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Identity System Architecture](#identity-system-architecture)
3. [Tier Levels](#tier-levels)
4. [Integration Patterns](#integration-patterns)
5. [Best Practices](#best-practices)
6. [Common Issues and Solutions](#common-issues-and-solutions)

## Quick Start

### Basic Import and Setup

```python
# Import the identity client
from lukhas.identity.interface import IdentityClient

# Initialize the client
identity_client = IdentityClient()

# Basic usage
if identity_client.verify_user_access(user_id, "LAMBDA_TIER_2"):
    # User has required access
    identity_client.log_activity("operation_name", user_id, {"key": "value"})
```

### Using the Identity Integration Module

```python
from lukhas.core.identity_integration import require_identity, IdentityContext

# Decorator approach
@require_identity(required_tier="LAMBDA_TIER_3", check_consent="memory_access")
def protected_function(user_id: str, data: dict):
    # Function is automatically protected
    return process_data(data)

# Context manager approach
with IdentityContext(user_id, "LAMBDA_TIER_2") as ctx:
    if ctx.has_access:
        # Perform tier-gated operations
        result = perform_operation()
```

## Identity System Architecture

### Core Components

1. **IdentityClient** (`lukhas/identity/interface.py`)
   - Main interface for all identity operations
   - Handles tier validation, consent checking, and activity logging

2. **Identity Integration** (`lukhas/core/identity_integration.py`)
   - Provides decorators and utilities for easy integration
   - Includes `@require_identity` decorator and `IdentityContext` manager

3. **Tier System** (`lukhas/memory/systems/tier_system.py`)
   - Defines tier levels and permission scopes
   - Manages access control policies

## Tier Levels

### Standard Tiers

| Tier | Level | Name | Description | Typical Use Cases |
|------|-------|------|-------------|-------------------|
| LAMBDA_TIER_0 | 0 | PUBLIC | Public access | Read-only public data |
| LAMBDA_TIER_1 | 1 | AUTHENTICATED | Basic authenticated user | Personal data access |
| LAMBDA_TIER_2 | 2 | ELEVATED | Elevated permissions | Memory operations, basic AI features |
| LAMBDA_TIER_3 | 3 | PRIVILEGED | Privileged access | Dream generation, advanced features |
| LAMBDA_TIER_4 | 4 | ADMIN | Administrative access | System configuration, user management |
| LAMBDA_TIER_5 | 5 | SYSTEM | System-level access | Internal operations only |

### Consent Actions

Common consent actions that should be checked:

- `memory_access` - Reading/writing memory
- `memory_search` - Searching through memories
- `dream_generation` - Creating dreams
- `consciousness_introspection` - Accessing consciousness metrics
- `emotion_analysis` - Analyzing emotional states
- `creative_generation` - Generating creative content

## Integration Patterns

### Pattern 1: Simple Function Protection

```python
from lukhas.identity.interface import IdentityClient

class MyModule:
    def __init__(self):
        self.identity_client = IdentityClient()

    def protected_operation(self, user_id: str, data: dict):
        # Verify access
        if not self.identity_client.verify_user_access(user_id, "LAMBDA_TIER_2"):
            return {"error": "Insufficient access"}

        # Check consent
        if not self.identity_client.check_consent(user_id, "operation_name"):
            return {"error": "Consent required"}

        # Log activity
        self.identity_client.log_activity(
            "protected_operation",
            user_id,
            {"data_size": len(data)}
        )

        # Perform operation
        return {"result": process_data(data)}
```

### Pattern 2: Decorator-Based Protection

```python
from lukhas.core.identity_integration import require_identity

class AdvancedModule:
    @require_identity(required_tier="LAMBDA_TIER_3", check_consent="advanced_operation")
    def advanced_operation(self, user_id: str, params: dict):
        # Function automatically protected
        return {"status": "success", "data": process_advanced(params)}

    @require_identity(required_tier="LAMBDA_TIER_4")
    def admin_operation(self, user_id: str, config: dict):
        # Admin-only operation
        return update_system_config(config)
```

### Pattern 3: Granular Access Control

```python
from lukhas.core.identity_integration import IdentityContext, get_identity_client

def multi_tier_operation(user_id: str, request: dict):
    client = get_identity_client()
    results = {}

    # Basic tier operations
    with IdentityContext(user_id, "LAMBDA_TIER_1") as ctx:
        if ctx.has_access:
            results["basic"] = get_basic_info()

    # Advanced tier operations
    with IdentityContext(user_id, "LAMBDA_TIER_3") as ctx:
        if ctx.has_access:
            results["advanced"] = get_advanced_info()
        else:
            results["advanced"] = {"message": "Upgrade to tier 3 for advanced features"}

    # Log the access pattern
    if client:
        client.log_activity("multi_tier_access", user_id, {
            "tiers_accessed": list(results.keys())
        })

    return results
```

### Pattern 4: Service-Level Integration

```python
from lukhas.identity.interface import IdentityClient
import structlog

logger = structlog.get_logger(__name__)

class ProtectedService:
    def __init__(self):
        # Try to initialize identity client
        try:
            self.identity_client = IdentityClient()
            self.identity_available = True
        except ImportError:
            # Fallback for development
            self.identity_client = self._create_fallback_client()
            self.identity_available = False
            logger.warning("Running with fallback identity client")

    def _create_fallback_client(self):
        """Create a mock client for development."""
        class FallbackClient:
            def verify_user_access(self, user_id, tier):
                return True
            def check_consent(self, user_id, action):
                return True
            def log_activity(self, activity, user_id, metadata):
                logger.info(f"MOCK_LOG: {activity} by {user_id}")

        return FallbackClient()

    def process_request(self, user_id: str, request: dict):
        # Always use identity client (real or fallback)
        if not self.identity_client.verify_user_access(user_id, "LAMBDA_TIER_2"):
            return {"error": "Access denied"}

        # Process based on user tier
        result = self._process_with_tier_limits(user_id, request)

        # Log the activity
        self.identity_client.log_activity(
            "service_request",
            user_id,
            {"request_type": request.get("type")}
        )

        return result
```

## Best Practices

### 1. Always Check Both Tier and Consent

```python
# Good
if (self.identity_client.verify_user_access(user_id, "LAMBDA_TIER_2") and
    self.identity_client.check_consent(user_id, "data_processing")):
    process_user_data()

# Better - with proper error messages
if not self.identity_client.verify_user_access(user_id, "LAMBDA_TIER_2"):
    return {"error": "Requires tier 2 access"}
if not self.identity_client.check_consent(user_id, "data_processing"):
    return {"error": "User consent required for data processing"}
process_user_data()
```

### 2. Log All Significant Activities

```python
# Log both successes and failures
try:
    result = perform_operation(data)
    self.identity_client.log_activity("operation_success", user_id, {
        "operation": "data_processing",
        "records_processed": len(data)
    })
    return result
except Exception as e:
    self.identity_client.log_activity("operation_failure", user_id, {
        "operation": "data_processing",
        "error": str(e)
    })
    raise
```

### 3. Provide Graceful Degradation

```python
def adaptive_feature(user_id: str, params: dict):
    # Check what tier the user has
    client = get_identity_client()

    if client and client.verify_user_access(user_id, "LAMBDA_TIER_4"):
        return premium_algorithm(params)
    elif client and client.verify_user_access(user_id, "LAMBDA_TIER_2"):
        return standard_algorithm(params)
    else:
        return basic_algorithm(params)
```

### 4. Use Consistent Error Messages

```python
# Define standard error responses
TIER_ERRORS = {
    "LAMBDA_TIER_1": "This feature requires authenticated access",
    "LAMBDA_TIER_2": "This feature requires elevated permissions",
    "LAMBDA_TIER_3": "This feature requires privileged access",
    "LAMBDA_TIER_4": "This feature requires administrative access"
}

def get_tier_error(required_tier: str) -> dict:
    return {
        "error": "insufficient_tier",
        "message": TIER_ERRORS.get(required_tier, f"Requires {required_tier}"),
        "required_tier": required_tier
    }
```

## Common Issues and Solutions

### Issue 1: Import Errors

**Problem**: `ImportError: cannot import name 'IdentityClient'`

**Solution**: Ensure correct import path:
```python
# Correct
from lukhas.identity.interface import IdentityClient

# Incorrect (old path)
from lukhas.identity.identity_interface import IdentityClient
```

### Issue 2: Identity Client Not Available

**Problem**: Identity client is None in production

**Solution**: Always check if client is available:
```python
client = get_identity_client()
if client:
    # Use client
    client.verify_user_access(user_id, tier)
else:
    # Fallback behavior
    logger.warning("Identity client not available")
```

### Issue 3: User ID Not Available

**Problem**: Functions don't have access to user_id

**Solution**: Ensure user_id is passed through the call chain:
```python
# Add user_id to function signatures
def my_function(user_id: str, other_params: dict):
    # Now you can use user_id for identity checks
    pass

# Or extract from context/session
def get_current_user_id(request) -> str:
    return request.session.get("user_id") or "anonymous"
```

### Issue 4: Consent Confusion

**Problem**: Not sure what consent action to use

**Solution**: Use descriptive, consistent consent actions:
```python
# Good consent action names
"memory_read"
"memory_write"
"dream_generation"
"emotion_analysis"

# Poor consent action names
"access"
"use_feature"
"operation"
```

## Migration Guide

For modules not yet using identity:

1. **Add Import**
   ```python
   from lukhas.identity.interface import IdentityClient
   ```

2. **Initialize Client**
   ```python
   self.identity_client = IdentityClient()
   ```

3. **Add Tier Checks**
   ```python
   if not self.identity_client.verify_user_access(user_id, "LAMBDA_TIER_2"):
       return {"error": "Insufficient access"}
   ```

4. **Add Consent Checks**
   ```python
   if not self.identity_client.check_consent(user_id, "operation_name"):
       return {"error": "Consent required"}
   ```

5. **Add Activity Logging**
   ```python
   self.identity_client.log_activity("operation", user_id, metadata)
   ```

## Testing

When testing identity-integrated code:

```python
# Mock the identity client for tests
from unittest.mock import Mock

def test_my_function():
    # Create mock client
    mock_client = Mock()
    mock_client.verify_user_access.return_value = True
    mock_client.check_consent.return_value = True

    # Inject mock
    my_module.identity_client = mock_client

    # Test function
    result = my_module.protected_function("test_user", {})

    # Verify identity checks were made
    mock_client.verify_user_access.assert_called_with("test_user", "LAMBDA_TIER_2")
    mock_client.check_consent.assert_called_with("test_user", "operation_name")
```

## Conclusion

The LUKHAS identity system provides a robust foundation for secure, tier-based access control across all Cognitive modules. By following these integration patterns and best practices, you can ensure your module properly validates user access, respects consent preferences, and maintains comprehensive audit trails.

For questions or issues, consult the identity module documentation or contact the LUKHAS security team.
