---
status: wip
type: documentation
---
# CREATIVITY Module

## Overview
Creative expression, dream systems, and personality engines

## Module Structure
- **Python Files**: 132
- **Submodules**: 6
- **Last Updated**: 2025-07-28

## Directory Structure
```
creativity/
├── dream/
├── dream_engine/
├── dream_systems/
├── emotion/
├── engines/
├── systems/
```

## Internal Dependencies
- `bio`
- `consciousness`
- `core`
- `creativity`
- `emotion`
- `ethics`
- `identity`
- `memory`
- `orchestration`
- `symbolic`

## Usage

```python
# Import example
from creativity import ...

# Module initialization
# Add specific examples based on module content
```

## Key Components

### `affect_stagnation_detector`
Module containing affect stagnation detector functionality.

### `creative_q_expression`
Module containing creative q expression functionality.

### `service`
Module containing service functionality.

### `creative_expression_core`
Module containing creative expression core functionality.

### `personality_engine`
Module containing personality engine functionality.

## Development

### Running Tests
```bash
pytest tests/test_{module_name}*.py
```

### Adding New Features
1. Create new module file in appropriate subdirectory
2. Update `__init__.py` exports
3. Add tests in `tests/` directory
4. Update this README

## Related Documentation
- [Main README](../README.md)
- [Architecture Overview](../docs/architecture.md)
- [API Reference](../docs/api_reference.md)
