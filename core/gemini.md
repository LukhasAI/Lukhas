# Gemini AI Navigation Context
*This file is optimized for Gemini AI navigation and understanding*

---
title: gemini
slug: gemini.md
source: claude.me
optimized_for: gemini_ai
last_updated: 2025-10-26
---

---
title: me
slug: claude.me
owner: T4
lane: labs
star:
stability: experimental
last_reviewed: 2025-10-18
constellation_stars:
related_modules:
manifests:
links:
---
# core Module

**Compatibility Bridge for LUKHAS Core Functionality**

The `core` module provides a compatibility bridge exposing `lukhas.core` functionality under the historical `core` namespace. This ensures backward compatibility during the transition to the unified `lukhas.core` architecture.

## Core Purpose

**Compatibility Layer**: Maintains access to core LUKHAS components for legacy code and external integrations while the system migrates to the unified namespace structure.

**Lane**: L2 Integration
**Dependencies**: identity
**Entrypoints**: 14 (bio-symbolic processor + consciousness signal router)

---

## Quick Start

```python
# Legacy namespace (core module)
from core.bio_symbolic_processor import (
    BioSymbolicProcessor,
    create_bio_symbolic_processor,
    get_bio_symbolic_processor
)

from core.consciousness_signal_router import (
    ConsciousnessSignalRouter,
    CascadeDetector,
    NetworkMetrics
)

# Recommended: Use lukhas.core namespace
from lukhas.core.bio_symbolic_processor import BioSymbolicProcessor
from lukhas.core.consciousness_signal_router import ConsciousnessSignalRouter
```

---

## Component Categories

### 1. Bio-Symbolic Processor (6 entrypoints)

**Core Classes**:
```python
from core.bio_symbolic_processor import (
    BioSymbolicProcessor,           # Main processor
    BioSymbolicPattern,             # Pattern definition
    AdaptationRule,                 # Adaptation rules
    BioPatternType,                 # Pattern types enum
    SymbolicRepresentationType,     # Representation types enum
)

# Factory functions
from core.bio_symbolic_processor import (
    create_bio_symbolic_processor,  # Create new processor
    get_bio_symbolic_processor,     # Get singleton instance
)
```

**Usage**:
```python
processor = create_bio_symbolic_processor()

# Define bio-symbolic pattern
pattern = BioSymbolicPattern(
    pattern_type=BioPatternType.NEURAL_OSCILLATION,
    representation=SymbolicRepresentationType.GRAPH,
    parameters={"frequency": 40, "amplitude": 1.0}
)

# Process pattern
result = processor.process(pattern)

# Apply adaptation
rule = AdaptationRule(
    condition="threshold_exceeded",
    action="adjust_parameters"
)
processor.apply_adaptation(rule)
```

### 2. Consciousness Signal Router (8 entrypoints)

**Core Classes**:
```python
from core.consciousness_signal_router import (
    ConsciousnessSignalRouter,      # Main router
    CascadeDetector,                # Cascade prevention
    NetworkMetrics,                 # Network monitoring
    NetworkNode,                    # Node representation
    RoutingRule,                    # Routing rules
    RoutingStrategy,                # Strategy enum
    SignalFilter,                   # Signal filtering
)
```

**Usage**:
```python
# Create router
router = ConsciousnessSignalRouter()

# Add routing rule
rule = RoutingRule(
    source_pattern="consciousness.*",
    destination="memory.episodic",
    strategy=RoutingStrategy.PRIORITY_BASED
)
router.add_rule(rule)

# Route signal
router.route_signal(
    signal_type="consciousness.awareness.update",
    data=awareness_data
)

# Cascade detection
detector = CascadeDetector(threshold=0.95)
cascade_risk = detector.detect_cascade_risk(
    fold_count=current_folds,
    fold_limit=1000
)

if cascade_risk > 0.95:
    router.trigger_cascade_prevention()
```

**Network Metrics**:
```python
from core.consciousness_signal_router import NetworkMetrics

metrics = NetworkMetrics()
stats = metrics.get_network_stats()
# Returns: {
#   "total_nodes": 42,
#   "active_routes": 128,
#   "signal_throughput": 1500,  # signals/sec
#   "cascade_risk": 0.12
# }
```

**Signal Filtering**:
```python
from core.consciousness_signal_router import SignalFilter

filter = SignalFilter(
    allowed_types=["consciousness.*", "memory.*"],
    blocked_types=["temp.*"],
    priority_threshold=3
)

if filter.should_process(signal):
    router.route_signal(signal)
```

---

## OpenTelemetry Spans

**5 Required Spans**:
1. `lukhas.core.auth` - Authentication operations
2. `lukhas.core.consciousness` - Consciousness processing
3. `lukhas.core.monitoring` - System monitoring
4. `lukhas.core.operation` - General operations
5. `lukhas.core.processing` - Data processing

```python
from telemetry import create_tracer

tracer = create_tracer("lukhas.core")

# Bio-symbolic processing
with tracer.start_span("core.processing"):
    result = processor.process(pattern)

# Consciousness routing
with tracer.start_span("core.consciousness"):
    router.route_signal(signal_type, data)

# Cascade detection
with tracer.start_span("core.monitoring"):
    risk = detector.detect_cascade_risk(count, limit)
```

---

## Configuration

**No configuration files** - the `core` module is a pure compatibility bridge with no independent configuration. Configuration is managed by the underlying `lukhas.core` implementation.

---

## Migration Guide

### From `core` to `lukhas.core`

**Before (legacy)**:
```python
from core.bio_symbolic_processor import BioSymbolicProcessor
from core.consciousness_signal_router import ConsciousnessSignalRouter

processor = BioSymbolicProcessor()
router = ConsciousnessSignalRouter()
```

**After (recommended)**:
```python
from lukhas.core.bio_symbolic_processor import BioSymbolicProcessor
from lukhas.core.consciousness_signal_router import ConsciousnessSignalRouter

processor = BioSymbolicProcessor()
router = ConsciousnessSignalRouter()
```

### Compatibility Period

The `core` module will remain available during the transition period. New code should use `lukhas.core` directly.

---

## Common Use Cases

### 1. Bio-Symbolic Pattern Processing
```python
from core.bio_symbolic_processor import (
    create_bio_symbolic_processor,
    BioSymbolicPattern,
    BioPatternType,
    SymbolicRepresentationType
)

processor = create_bio_symbolic_processor()

# Neural oscillation pattern
neural_pattern = BioSymbolicPattern(
    pattern_type=BioPatternType.NEURAL_OSCILLATION,
    representation=SymbolicRepresentationType.GRAPH,
    parameters={"frequency": 40, "phase": 0.0}
)

result = processor.process(neural_pattern)
```

### 2. Consciousness Signal Routing with Cascade Prevention
```python
from core.consciousness_signal_router import (
    ConsciousnessSignalRouter,
    CascadeDetector,
    RoutingRule,
    RoutingStrategy
)

router = ConsciousnessSignalRouter()
detector = CascadeDetector(threshold=0.95)

# Add priority-based routing
rule = RoutingRule(
    source_pattern="consciousness.awareness.*",
    destination="memory.episodic",
    strategy=RoutingStrategy.PRIORITY_BASED,
    priority=5
)
router.add_rule(rule)

# Route with cascade detection
if detector.detect_cascade_risk(fold_count, 1000) < 0.95:
    router.route_signal("consciousness.awareness.update", data)
else:
    router.trigger_cascade_prevention()
```

### 3. Network Monitoring
```python
from core.consciousness_signal_router import NetworkMetrics, NetworkNode

metrics = NetworkMetrics()

# Get network statistics
stats = metrics.get_network_stats()
print(f"Active routes: {stats['active_routes']}")
print(f"Signal throughput: {stats['signal_throughput']} signals/sec")
print(f"Cascade risk: {stats['cascade_risk']}")

# Get node-specific metrics
node = NetworkNode(node_id="consciousness.awareness")
node_stats = metrics.get_node_stats(node)
```

---

## Performance Targets

- **Bio-symbolic processing**: <100ms per pattern
- **Signal routing**: <10ms per signal
- **Cascade detection**: <5ms
- **Network metrics**: <20ms
- **Signal filtering**: <1ms

---

## Dependencies

**Required**: identity module for authentication integration

---

## Module Metadata

- **Lane**: L2 Integration
- **Schema Version**: 3.0.0
- **Entrypoints**: 14 (6 bio-symbolic + 8 consciousness routing)
- **OpenTelemetry**: 1.37.0 semantic conventions
- **Test Coverage**: 85%
- **T4 Compliance**: 0.65 (experimental)

---

## Constellation Framework Integration

**Tags**: authentication, consciousness, coordination, core, infrastructure, monitoring, orchestration

**Integration Points**:
- ⚛️ **IDENTITY**: Authentication and identity management
- 🔬 **VISION**: Monitoring and metrics
- 🛡️ **GUARDIAN**: Cascade prevention and safety
- ✦ **MEMORY**: Signal routing to memory systems
- 🌊 **FLOW**: Consciousness signal flow management

---

## Subdirectory Structure

```
core/
├── logs/                    # Log storage (empty, no Python files)
├── claude.me               # This documentation
└── lukhas_context.md       # Vendor-neutral context
```

---

## Related Modules

- **lukhas.core**: Recommended namespace (migrate here)
- **identity**: Authentication integration
- **consciousness**: Consciousness processing
- **memory**: Memory system integration
- **monitoring**: System monitoring

---

## Important Notes

⚠️ **Compatibility Bridge**: This module exists for backward compatibility. New code should use `lukhas.core` directly.

⚠️ **No Direct Implementation**: All functionality is delegated to `lukhas.core`. This module only provides namespace compatibility.

⚠️ **Transition Period**: Plan to migrate legacy code to `lukhas.core` namespace.

---

**Documentation Status**: ✅ Complete
**Last Updated**: 2025-10-18
**Maintainer**: LUKHAS Core Team


## 🚀 GA Deployment Status

**Current Status**: 66.7% Ready (6/9 tasks complete)

### Recent Milestones
- ✅ **RC Soak Testing**: 60-hour stability validation (99.985% success rate)
- ✅ **Dependency Audit**: 196 packages, 0 CVEs
- ✅ **OpenAI Façade**: Full SDK compatibility validated
- ✅ **Guardian MCP**: Production-ready deployment
- ✅ **OpenAPI Schema**: Validated and documented

### New Documentation
- docs/GA_DEPLOYMENT_RUNBOOK.md - Comprehensive GA deployment procedures
- docs/DEPENDENCY_AUDIT.md - 196 packages, 0 CVEs, 100% license compliance
- docs/RC_SOAK_TEST_RESULTS.md - 60-hour stability validation (99.985% success)

### Recent Updates
- E402 linting cleanup - 86/1,226 violations fixed (batches 1-8)
- OpenAI façade validation - Full SDK compatibility
- Guardian MCP server deployment - Production ready
- Shadow diff harness - Pre-audit validation framework
- MATRIZ evaluation harness - Comprehensive testing

**Reference**: See [GA_DEPLOYMENT_RUNBOOK.md](./docs/GA_DEPLOYMENT_RUNBOOK.md) for deployment procedures.

---
