---
title: lukhas_context
slug: lukhas_context
owner: T4
lane: labs
star:
stability: experimental
last_reviewed: 2025-10-18
constellation_stars:
related_modules:
manifests:
links:
status: wip
type: documentation
---
# core - Compatibility Bridge Module

## Overview

The `core` module provides backward compatibility by exposing `lukhas.core` functionality under the historical `core` namespace. This enables smooth migration for legacy code while the system transitions to the unified namespace structure.

**Module**: core
**Purpose**: Compatibility bridge for lukhas.core namespace
**Lane**: L2 Integration
**Schema**: v3.0.0
**Last Updated**: 2025-10-18

## Quick Reference

```python
# Legacy namespace (compatibility)
from core.bio_symbolic_processor import BioSymbolicProcessor, create_bio_symbolic_processor
from core.consciousness_signal_router import ConsciousnessSignalRouter, CascadeDetector

# Recommended namespace (migrate to this)
from lukhas.core.bio_symbolic_processor import BioSymbolicProcessor
from lukhas.core.consciousness_signal_router import ConsciousnessSignalRouter
```

## Core Components

### Bio-Symbolic Processor (6 entrypoints)
- **BioSymbolicProcessor**: Main processor for bio-symbolic patterns
- **BioSymbolicPattern**: Pattern definition with type and representation
- **AdaptationRule**: Rules for bio-symbolic adaptation
- **BioPatternType**: Enum for pattern types (neural oscillation, etc.)
- **SymbolicRepresentationType**: Enum for representation types (graph, etc.)
- **Factory functions**: `create_bio_symbolic_processor`, `get_bio_symbolic_processor`

### Consciousness Signal Router (8 entrypoints)
- **ConsciousnessSignalRouter**: Routes consciousness signals across system
- **CascadeDetector**: Detects and prevents memory cascade risk
- **NetworkMetrics**: Network monitoring and statistics
- **NetworkNode**: Node representation in consciousness network
- **RoutingRule**: Routing rule definition
- **RoutingStrategy**: Strategy enum (priority-based, round-robin, etc.)
- **SignalFilter**: Filters signals based on type and priority

## Usage Examples

### Bio-Symbolic Processing
```python
from core.bio_symbolic_processor import (
    create_bio_symbolic_processor,
    BioSymbolicPattern,
    BioPatternType
)

processor = create_bio_symbolic_processor()
pattern = BioSymbolicPattern(
    pattern_type=BioPatternType.NEURAL_OSCILLATION,
    parameters={"frequency": 40}
)
result = processor.process(pattern)
```

### Consciousness Signal Routing
```python
from core.consciousness_signal_router import (
    ConsciousnessSignalRouter,
    RoutingRule,
    RoutingStrategy
)

router = ConsciousnessSignalRouter()
rule = RoutingRule(
    source_pattern="consciousness.*",
    destination="memory.episodic",
    strategy=RoutingStrategy.PRIORITY_BASED
)
router.add_rule(rule)
router.route_signal("consciousness.awareness.update", data)
```

### Cascade Prevention
```python
from core.consciousness_signal_router import CascadeDetector

detector = CascadeDetector(threshold=0.95)
risk = detector.detect_cascade_risk(
    fold_count=950,
    fold_limit=1000
)
if risk > 0.95:
    # Trigger prevention
    router.trigger_cascade_prevention()
```

## Performance Targets

- Bio-symbolic processing: <100ms
- Signal routing: <10ms
- Cascade detection: <5ms
- Network metrics: <20ms
- Signal filtering: <1ms

## OpenTelemetry

**5 Required Spans**:
- `lukhas.core.auth`: Authentication operations
- `lukhas.core.consciousness`: Consciousness processing
- `lukhas.core.monitoring`: System monitoring
- `lukhas.core.operation`: General operations
- `lukhas.core.processing`: Data processing

```python
from telemetry import create_tracer

tracer = create_tracer("lukhas.core")
with tracer.start_span("core.processing"):
    result = processor.process(pattern)
```

## Migration Path

**Legacy Code**:
```python
from core.bio_symbolic_processor import BioSymbolicProcessor
```

**Migrated Code** (recommended):
```python
from lukhas.core.bio_symbolic_processor import BioSymbolicProcessor
```

Both work during transition period. New code should use `lukhas.core`.

## Module Metadata

- **Lane**: L2 Integration
- **Dependencies**: identity
- **Entrypoints**: 14 (6 bio-symbolic + 8 routing)
- **Schema Version**: 3.0.0
- **Test Coverage**: 85%
- **T4 Compliance**: 0.65 (experimental)
- **OpenTelemetry**: 1.37.0

## Constellation Integration

**Tags**: authentication, consciousness, coordination, core, infrastructure, monitoring, orchestration

**Stars**:
- ⚛️ IDENTITY: Authentication integration
- 🔬 VISION: Monitoring and metrics
- 🛡️ GUARDIAN: Cascade prevention
- ✦ MEMORY: Signal routing
- 🌊 FLOW: Consciousness flow management

## Related Systems

- **lukhas.core**: Target namespace (migrate here)
- **identity**: Authentication
- **consciousness**: Consciousness processing
- **memory**: Memory integration
- **monitoring**: System monitoring

## Key Features

✅ Backward compatibility bridge
✅ 14 entrypoints (bio-symbolic + routing)
✅ Cascade detection (0.95 threshold)
✅ Network metrics and monitoring
✅ 5 OpenTelemetry spans
✅ Sub-100ms processing targets

## Important Notes

⚠️ **Compatibility Layer**: Use `lukhas.core` for new code
⚠️ **No Direct Implementation**: Delegates to `lukhas.core`
⚠️ **Transition Period**: Plan migration timeline

---

**Status**: Compatibility bridge (transitional)
**Version**: Schema 3.0.0
**Last Updated**: 2025-10-18
