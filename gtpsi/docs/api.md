<!--
@generated LUKHAS scaffold v1.0
template_id: module.scaffold/v1
template_commit: f95979630
do_not_edit: false
human_editable: true
-->

# Gtpsi API Documentation

## Overview

Optional MFA/consent factor using gesture recognition for high-risk actions.

## Entrypoints

### Functions

#### `get_action_risk_level()`

**Import**: `from gtpsi import get_action_risk_level`

Function for get action risk level operations.

#### `get_max_approval_time()`

**Import**: `from gtpsi import get_max_approval_time`

Function for get max approval time operations.

#### `process_gesture()`

**Import**: `from gtpsi import process_gesture`

Function for process gesture operations.

## Error Handling

All API functions follow LUKHAS error handling patterns:

```python
try:
    result = module_function()
except LUKHASException as e:
    # Handle LUKHAS-specific errors
    logger.error(f"Module error: {e}")
except Exception as e:
    # Handle general errors
    logger.error(f"Unexpected error: {e}")
```

## Examples

```python
import gtpsi

# Basic usage example
# Initialize module
# Perform operations
# Handle results
```
