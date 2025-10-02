# Core Module Context - Vendor-Neutral AI Guidance

**Module**: core
**Purpose**: Core system coordination and lane management
**Lane**: Production Integration
**Schema**: v2.0.0
**Last Updated**: 2025-10-02

---

## Context Sync Header

```
Lane: production_integration
Module: core
Canonical imports: lukhas.core.*
Components: Registry, Bootstrap, Lane Management
Integration: Constellation Framework foundation
```

---

## Module Purpose

The core module provides foundational system coordination, implementing the registry-based plugin architecture that enables LUKHAS's dynamic component loading, lane boundary enforcement, and Constellation Framework integration.

### Core Capabilities
- **Registry System**: Dynamic component registration and lifecycle management
- **Bootstrap**: System initialization and dependency resolution
- **Lane Management**: Boundary enforcement and promotion gates
- **Coordination**: Cross-module integration hub
- **Health Monitoring**: System status and vital signs

---

## Architecture Integration

### Constellation Framework Foundation
- **Central Hub**: Coordinates all constellation stars (⚛️✦🔬🛡️🌊⚡🎭🔮)
- **Registry Pattern**: Enables dynamic star registration and discovery
- **Lane Boundaries**: Enforces safe progression (candidate → integration → production)
- **Performance**: <100ms initialization target

### Lane Positioning
- **Current Lane**: Production Integration
- **Quality**: Battle-tested coordination layer
- **Stability**: Foundation for all LUKHAS systems
- **Role**: Bridge between development and production

---

## Key Components

### ComponentRegistry
Dynamic component registration system:
- Type-safe component retrieval
- Lazy loading for performance
- Lifecycle management (init/start/stop)
- Plugin discovery and loading

### Bootstrap System
System initialization framework:
- Dependency graph resolution
- Configuration loading and validation
- Health check coordination
- Graceful startup and shutdown

### LaneManager
Lane boundary enforcement:
- Import validation (prevent candidate → production)
- Feature flag coordination
- Promotion gate validation
- Cross-lane compatibility checks

---

## Usage Patterns

### Component Registration
```python
from lukhas.core.registry import ComponentRegistry

registry = ComponentRegistry.get_instance()
registry.register("consciousness", ConsciousnessEngine)
registry.register("memory", MemorySystem)

# Retrieve component
engine = registry.get("consciousness")
```

### System Bootstrap
```python
from lukhas.core import initialize_system, get_bootstrap

# Initialize LUKHAS
system = initialize_system()

# Access bootstrap
bootstrap = get_bootstrap()
bootstrap.start_component("identity")
```

### Lane Validation
```python
from lukhas.core.lanes import validate_import

# Validate import is allowed
validate_import(
    source_lane="production",
    target_module="candidate.experimental"
)  # Raises error if invalid
```

---

## Performance Targets

- **Initialization**: <100ms system startup
- **Registry Lookup**: <1ms component retrieval
- **Memory**: <50MB base system footprint
- **Availability**: 99.99% uptime (core infrastructure)

---

## Integration Points

### Constellation Framework
- Provides foundation for all constellation stars
- Coordinates Identity (⚛️), Memory (✦), Vision (🔬), Guardian (🛡️)
- Enables dynamic star registration and expansion

### MATRIZ Integration
- Registry pattern for MATRIZ nodes
- Pipeline coordination infrastructure
- Cognitive component lifecycle management

### All Modules
Core serves as the foundation:
- Bootstrap and initialization
- Component discovery
- Configuration management
- Health monitoring

---

## Development Guidelines

1. **Lane Boundaries**: Strictly enforce import rules
2. **Registry Pattern**: All components must use registry
3. **Performance**: <100ms initialization requirement
4. **Stability**: Core must never crash (99.99% uptime)
5. **Testing**: 80%+ coverage required (foundation code)
6. **Documentation**: Every public API must have comprehensive docs

---

## Documentation Structure

```
core/
├── README.md              # Module overview
├── CLAUDE.md             # AI development context
├── lukhas_context.md     # This file (vendor-neutral)
├── docs/
│   ├── REGISTRY.md       # Registry pattern documentation
│   ├── BOOTSTRAP.md      # Bootstrap system guide
│   ├── LANES.md          # Lane management documentation
│   └── ARCHITECTURE.md   # Core architecture
└── tests/
    ├── unit/             # Component tests
    ├── integration/      # Cross-system tests
    └── performance/      # Initialization benchmarks
```

---

## Lane System

### Lane Progression
```
candidate/ → lukhas/ → products/
(experimental) → (integration) → (production)
```

### Promotion Gates
1. **E2E Performance**: All SLOs met
2. **Schema Drift**: No breaking changes
3. **Chaos Testing**: Fail-closed validation
4. **Telemetry**: Complete observability
5. **Import Hygiene**: Lane boundaries respected

---

## Related Contexts

- **Main System**: [../lukhas_context.md](../lukhas_context.md)
- **Constellation Hub**: [../lukhas/lukhas_context.md](../lukhas/lukhas_context.md)
- **Identity**: [../identity/lukhas_context.md](../identity/lukhas_context.md)
- **Memory**: [../memory/lukhas_context.md](../memory/lukhas_context.md)
- **Module Index**: [../MODULE_INDEX.md](../MODULE_INDEX.md#core-integration)

---

**Status**: Production Integration
**Manifest**: ✓ module.manifest.json
**Team**: Core Infrastructure
**Architecture**: Constellation Framework v2.0.0
