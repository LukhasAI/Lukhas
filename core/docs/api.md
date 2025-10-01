<!--
@generated LUKHAS scaffold v1.0
template_id: module.scaffold/v1
template_commit: f95979630
do_not_edit: false
human_editable: true
-->

# Core API Documentation

## Overview

Compatibility bridge exposing :mod:`lukhas.core` under the historical ``core`` namespace.

## Entrypoints

### Functions

#### `create_bio_symbolic_processor()`

**Import**: `from core.bio_symbolic_processor import create_bio_symbolic_processor`

Function for create bio symbolic processor operations.

#### `get_bio_symbolic_processor()`

**Import**: `from core.bio_symbolic_processor import get_bio_symbolic_processor`

Function for get bio symbolic processor operations.

#### `get_processing_statistics()`

**Import**: `from core.bio_symbolic_processor import get_processing_statistics`

Function for get processing statistics operations.

#### `process_consciousness_signal()`

**Import**: `from core.bio_symbolic_processor import process_consciousness_signal`

Function for process consciousness signal operations.

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
import core

# Basic usage example
# Initialize module
# Perform operations
# Handle results
```
