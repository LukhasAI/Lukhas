<!--
@generated LUKHAS scaffold v1.0
template_id: module.scaffold/v1
template_commit: f95979630
do_not_edit: false
human_editable: true
-->

# Governance API Documentation

## Overview

This module provides governance capabilities for the LUKHAS AI system.

## Entrypoints

### Functions

#### `get_audit_stats()`

**Import**: `from governance.audit_trail import get_audit_stats`

Function for get audit stats operations.

#### `get_colony_stats()`

**Import**: `from governance.colony_memory_validator import get_colony_stats`

Function for get colony stats operations.

#### `get_metrics()`

**Import**: `from governance.colony_memory_validator import get_metrics`

Function for get metrics operations.

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
import governance

# Basic usage example
# Initialize module
# Perform operations
# Handle results
```
