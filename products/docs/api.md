<!--
@generated LUKHAS scaffold v1.0
template_id: module.scaffold/v1
template_commit: f95979630
do_not_edit: false
human_editable: true
-->

# Products API Documentation

## Overview

Consolidated products organized by functional domain:

## Entrypoints

### Functions

#### `create_product_instance()`

**Import**: `from products import create_product_instance`

Function for create product instance operations.

#### `get_product_health()`

**Import**: `from products import get_product_health`

Function for get product health operations.

#### `get_products_catalog()`

**Import**: `from products import get_products_catalog`

Function for get products catalog operations.

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
import products

# Basic usage example
# Initialize module
# Perform operations
# Handle results
```
