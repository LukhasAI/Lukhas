# Gemini AI Navigation Context
*This file is optimized for Gemini AI navigation and understanding*

---
title: gemini
slug: gemini.md
source: claude.me
optimized_for: gemini_ai
last_updated: 2025-10-26
---

# Dream Module - Claude AI Context

**Module**: dream
**Purpose**: Core dream processing components for consciousness integration
**Lane**: L2 (Integration)
**Language**: Python
**Last Updated**: 2025-10-18

---

## Module Overview

The dream module provides core dream processing capabilities for LUKHAS AI consciousness systems, implementing dream synthesis, creative processing, and dream state management. It enables the consciousness system to engage in creative exploration, problem-solving, and memory consolidation through dream-like processing.

### Key Components
- **Dream Engine**: Core dream processing and synthesis
- **Dream Bridge**: Integration bridge for consciousness systems
- **Dream Processor**: Dream sequence processing and analysis
- **Dream Context**: Contextual dream state management
- **Dream Types**: Multiple dream modalities (creative, problem-solving, exploratory)

### Constellation Framework Integration
- **🔮 Oracle Star (Prediction)**: Dream-based future state exploration
- **⚡ Spark Star (Creativity)**: Creative synthesis and ideation
- **🧠 Flow Star (Consciousness)**: Dream-consciousness coupling
- **✦ Trail Star (Memory)**: Dream memory consolidation

---

## Architecture

### Core Dream Components

#### Entrypoints (from manifest)
```python
from dream import (
    DreamBridge,
    DreamProcessor,
    create_dream_bridge,
)

from dream.engine import (
    DreamContext,
    DreamElement,
    DreamEngine,
    DreamSequence,
    DreamState,
    DreamType,
    get_dream_engine,
)
```

---

## Dream Processing Systems

### 1. Dream Engine

**Module**: `dream.engine`
**Purpose**: Core dream synthesis and processing engine

```python
from dream.engine import (
    DreamEngine,
    DreamType,
    DreamState,
    get_dream_engine,
)

# Get dream engine instance
engine: DreamEngine = get_dream_engine()

# Initiate dream session
dream_session = engine.start_dream(
    dream_type=DreamType.CREATIVE,
    duration=300,  # 5 minutes
    theme="explore consciousness patterns"
)

# Dream Types
DreamType.CREATIVE        # Creative exploration
DreamType.PROBLEM_SOLVING # Problem-solving dreams
DreamType.EXPLORATORY     # Open-ended exploration
DreamType.MEMORY_CONSOLIDATION  # Memory processing
```

**Key Features**:
- Multi-modal dream types
- State management
- Sequence generation
- Context tracking

---

### 2. Dream Sequence Processing

**Purpose**: Generate and process dream sequences

```python
from dream.engine import DreamSequence, DreamElement

# Create dream sequence
sequence = DreamSequence(
    elements=[
        DreamElement(type="concept", value="consciousness"),
        DreamElement(type="metaphor", value="flowing water"),
        DreamElement(type="connection", value="awareness streams"),
    ],
    coherence=0.8,
    creativity=0.9
)

# Process sequence
result = engine.process_sequence(sequence)
```

**Sequence Features**:
- Element composition
- Coherence tracking
- Creativity metrics
- Narrative generation

---

### 3. Dream Bridge

**Purpose**: Integration bridge for consciousness systems

```python
from dream import DreamBridge, create_dream_bridge

# Create dream bridge
bridge: DreamBridge = create_dream_bridge(
    consciousness_integration=True,
    memory_enabled=True
)

# Connect consciousness to dream processing
bridge.connect_consciousness(consciousness_instance)

# Process through bridge
dream_output = bridge.process(
    input_concept="emergence",
    context="consciousness_exploration"
)
```

---

### 4. Dream Processor

**Purpose**: Dream processing and analysis

```python
from dream import DreamProcessor

# Create processor
processor = DreamProcessor(
    creativity_level=0.8,
    constraint_level=0.3
)

# Process dream content
processed = processor.process(
    dream_content=raw_dream,
    extract_insights=True,
    generate_metaphors=True
)
```

---

### 5. Dream Context Management

**Purpose**: Manage dream state and context

```python
from dream.engine import DreamContext, DreamState

# Create dream context
context = DreamContext(
    state=DreamState.ACTIVE,
    theme="creative synthesis",
    constraints={"coherence_min": 0.6},
    memory_access=True
)

# Dream States
DreamState.INITIATING   # Dream starting
DreamState.ACTIVE       # Dream in progress
DreamState.CONCLUDING   # Dream wrapping up
DreamState.COMPLETE     # Dream finished
```

---

## Observability

### Required Spans

```python
# Required spans from module.manifest.json
REQUIRED_SPANS = [
    "lukhas.dream.operation",      # Dream operations
    "lukhas.dream.processing",     # Dream processing
]
```

---

## Module Structure

```
dream/
├── module.manifest.json         # Dream manifest (schema v3.0.0)
├── module.manifest.lock.json    # Locked manifest
├── README.md                    # Dream overview
├── __init__.py                  # Module exports
├── engine.py                    # Dream engine (MATRIZ_PROCESSOR)
├── config/                      # Dream configuration
├── docs/                        # Dream documentation
└── tests/                       # Dream test suites
```

---

## Development Guidelines

### 1. Starting Dream Sessions

```python
from dream.engine import get_dream_engine, DreamType

# Get engine and start dream
engine = get_dream_engine()
dream = engine.start_dream(
    dream_type=DreamType.CREATIVE,
    duration=600,
    initial_concepts=["emergence", "patterns"]
)
```

### 2. Processing Dream Sequences

```python
from dream.engine import DreamSequence

# Create and process sequence
sequence = DreamSequence(elements=dream_elements)
result = engine.process_sequence(sequence)

# Extract insights
insights = result.extract_insights()
```

### 3. Integrating with Consciousness

```python
from dream import create_dream_bridge

# Create bridge to consciousness
bridge = create_dream_bridge(consciousness_integration=True)
bridge.connect_consciousness(consciousness_system)

# Process through integrated system
output = bridge.process(input_data)
```

---

## MATRIZ Pipeline Integration

This module operates within the MATRIZ cognitive framework:

- **M (Memory)**: Dream-based memory consolidation
- **A (Attention)**: Focus on creative elements
- **T (Thought)**: Creative synthesis and ideation
- **R (Risk)**: Creative risk exploration
- **I (Intent)**: Dream theme and direction
- **A (Action)**: Dream-inspired action generation

---

## Cognitive Domains

From manifest:
- **dream_synthesis**: Creative dream generation
- **creative_processing**: Open-ended creative exploration

---

## Performance Targets

- **Dream Initiation**: <100ms to start dream session
- **Sequence Processing**: <500ms per dream sequence
- **Bridge Processing**: <250ms for consciousness integration
- **Dream Completion**: Efficient session wrap-up
- **Insight Extraction**: <200ms to extract key insights

---

## Dependencies

**Required Modules**: None (standalone module)

**Integration Points**:
- `consciousness` - For consciousness-dream coupling
- `memory` - For dream memory consolidation
- `emotion` - For emotional dream content

---

## Related Modules

- **Consciousness** ([../consciousness/](../consciousness/)) - Consciousness integration
- **Memory** ([../memory/](../memory/)) - Memory consolidation
- **Emotion** ([../emotion/](../emotion/)) - Emotional processing

---

## Documentation

- **README**: [dream/README.md](README.md) - Dream overview
- **Docs**: [dream/docs/](docs/) - Dream processing guides
- **Tests**: [dream/tests/](tests/) - Dream test suites
- **Module Index**: [../MODULE_INDEX.md](../MODULE_INDEX.md#dream)

---

**Status**: Integration Lane (L2)
**Manifest**: ✓ module.manifest.json (schema v3.0.0)
**Team**: Core
**Code Owners**: @lukhas-core
**Entrypoints**: 9 dream processing functions
**Test Coverage**: 85.0%
**Last Updated**: 2025-10-18


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
