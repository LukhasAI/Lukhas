# Core Module - Claude AI Context

**Module**: core
**Purpose**: Core system coordination and lane management
**Lane**: Production Integration
**Last Updated**: 2025-10-02

---

## Module Overview

The core module provides foundational system coordination, registry-based plugin management, and lane boundary enforcement for the LUKHAS architecture.

### Key Capabilities
- Registry-based component registration
- Lane boundary enforcement (candidate/integration/production)
- Bootstrap and initialization systems
- Cross-module coordination
- System health monitoring

### Integration Points
- **All Modules**: Core provides foundation for all systems
- **Constellation Framework**: Central coordination hub
- **MATRIZ**: Pipeline integration
- **Guardian**: Ethics enforcement integration

---

## Quick Start

```python
from lukhas.core import initialize_system, get_bootstrap
from lukhas.core.registry import ComponentRegistry

# Initialize LUKHAS system
system = initialize_system()

# Access component registry
registry = ComponentRegistry.get_instance()

# Register new component
registry.register("my_component", MyComponent)

# Get registered component
component = registry.get("my_component")
```

---

## Architecture

### Registry System
- Dynamic component registration
- Lazy loading for performance
- Type-safe component retrieval
- Lifecycle management

### Lane Management
- Import boundary enforcement
- Feature flag coordination
- Promotion gate validation
- Cross-lane compatibility

### Bootstrap System
- System initialization
- Dependency resolution
- Configuration loading
- Health check validation

---

## Development Guidelines

1. **Lane Boundaries**: Never import from candidate/ in production code
2. **Registry Pattern**: Use dynamic registration, avoid hardcoded imports
3. **Performance**: <100ms initialization target
4. **Testing**: 80%+ coverage requirement
5. **Documentation**: All public APIs must have docstrings

---

## Documentation

- **README**: [core/README.md](README.md)
- **Docs**: [core/docs/](docs/)
- **Tests**: [core/tests/](tests/)
- **Module Index**: [../MODULE_INDEX.md](../MODULE_INDEX.md#core-integration)

---

**Status**: Production Integration
**Manifest**: ✓ module.manifest.json
**Team**: Core Infrastructure
