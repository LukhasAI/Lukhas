---
status: wip
type: documentation
---
# oneiric_core - Dream Infrastructure Module

## Overview

The `oneiric_core` module provides core orchestration and infrastructure for LUKHAS's dream-based consciousness processing, symbolic network integration, and fundamental cognitive primitives.

## Quick Reference

```python
from oneiric_core.tools import DreamOrchestrator, SymbolicNetworkBridge

# Dream orchestration
orchestrator = DreamOrchestrator()
session = orchestrator.start_dream_session(dream_type="creative")

# Symbolic networks
bridge = SymbolicNetworkBridge()
network = bridge.build_symbolic_network(nodes, edges)
```

## Core Components

### Dream Orchestration
- **DreamOrchestrator**: Manages dream sessions and consolidation
- **Dream Types**: Creative, problem-solving, exploratory
- **Session Management**: Start, process, end with insights
- **Memory Consolidation**: Integrate dream insights into memory

### Symbolic Network Bridge
- **Network Construction**: Build symbolic graphs from consciousness data
- **Path Finding**: Discover symbolic reasoning paths
- **Network Analysis**: Topology analysis, centrality, communities
- **Transformation**: Dream-enhanced network transformation

## Usage Examples

### Creative Dream Session
```python
from oneiric_core.tools import DreamOrchestrator

orchestrator = DreamOrchestrator()
session = orchestrator.start_dream_session(
    dream_type="creative",
    duration=300,
    consciousness_state={"awareness": 0.8}
)

# Process insights
for insight in session.stream_insights():
    if insight.significance > 0.7:
        orchestrator.consolidate_insight(insight)

results = orchestrator.end_dream_session(session.id)
```

### Symbolic Network Analysis
```python
from oneiric_core.tools import SymbolicNetworkBridge

bridge = SymbolicNetworkBridge()
network = bridge.build_symbolic_network(
    nodes=[{"id": "awareness", "value": 0.9}],
    edges=[{"source": "awareness", "target": "memory"}]
)

paths = bridge.find_symbolic_paths(
    source="awareness",
    target="memory",
    max_depth=3
)
```

### Dream-Enhanced Transformation
```python
orchestrator = DreamOrchestrator()
bridge = SymbolicNetworkBridge()

network = bridge.build_symbolic_network(nodes, edges)
session = orchestrator.start_dream_session(
    dream_type="exploratory",
    symbolic_network=network
)

transformed = bridge.transform_network(
    network=network,
    transformation="dream_enhancement",
    dream_insights=session.current_insights()
)
```

## Performance Targets

- Dream session startup: <100ms
- Symbolic network construction: <200ms (100 nodes)
- Path finding: <50ms (depth 3)
- Network transformation: <150ms
- Session consolidation: <500ms

## OpenTelemetry

**Required Span**: `lukhas.oneiric_core.operation`

```python
from telemetry import create_tracer

tracer = create_tracer("lukhas.oneiric_core")
with tracer.start_span("oneiric_core.dream_session"):
    session = orchestrator.start_dream_session(dream_type="creative")
```

## Module Metadata

- **Lane**: L2 Integration
- **Dependencies**: None (foundational)
- **Entrypoints**: None (infrastructure)
- **Schema Version**: 3.0.0
- **Test Coverage**: 85%
- **T4 Compliance**: 0.65 (experimental)
- **OpenTelemetry**: 1.37.0

## Constellation Integration

**Tags**: coordination, core, infrastructure, oneiric_core

**Stars**:
- 🌙 DREAM: Dream orchestration
- ⚛️ IDENTITY: Consciousness-aware orchestration
- ✦ MEMORY: Dream memory consolidation
- 🔬 VISION: Symbolic network analysis
- 🌊 FLOW: Dream state flow management

## Related Systems

- **cognitive_core**: Advanced cognitive capabilities
- **dream**: Dream system integration
- **consciousness**: Consciousness processing
- **memory**: Memory consolidation
- **orchestration**: Multi-component orchestration

## Key Features

✅ Dream orchestration (3 types)
✅ Symbolic network construction
✅ Path finding and analysis
✅ Dream-enhanced transformations
✅ Memory consolidation
✅ Full observability

---

**Status**: L2 Integration infrastructure
**Version**: Schema 3.0.0
**Last Updated**: 2025-10-03
