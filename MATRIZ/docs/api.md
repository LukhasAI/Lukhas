# Matriz API Documentation

## Overview

This module provides lowercase access to MATRIZ functionality for compatibility

## Entrypoints

### Functions

#### `create_shim()`

**Import**: `from matriz.legacy_shim import create_shim`

Function for create shim operations.

#### `get_shimmed_nodes()`

**Import**: `from matriz.legacy_shims import get_shimmed_nodes`

Function for get shimmed nodes operations.

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
import matriz

# Basic usage example
# Initialize module
# Perform operations
# Handle results
```
