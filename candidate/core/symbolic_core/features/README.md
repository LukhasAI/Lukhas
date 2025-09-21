# LUKHAS Symbolic System

## Overview

The LUKHAS symbolic system provides the core symbolic reasoning, GLYPH processing, and drift/collapse detection capabilities for the AI architecture. This module handles symbolic representation, drift detection, and the complex symbolic collapse mechanisms that ensure system stability.

## Quick Start

### Basic GLYPH Usage

```python
from lukhas.core.symbolic import GLYPH_MAP, get_glyph_meaning

# Access available glyphs
print(f"Available glyphs: {len(GLYPH_MAP)}")

# Get meaning of a specific glyph
if GLYPH_MAP:
    glyph = list(GLYPH_MAP.keys())[0]
    meaning = get_glyph_meaning(glyph)
    print(f"Glyph '{glyph}' means: {meaning}")
```

### Drift Detection

```python
from lukhas.core.symbolic.drift import get_drift_status, calculate_drift_score

# Check drift status
status = get_drift_status(0.3)  # Low drift
high_status = get_drift_status(0.8)  # High drift

# Calculate drift between states
score = calculate_drift_score("state1", "state2")
print(f"Drift score: {score}")
```

### Collapse Mechanisms

```python
from lukhas.core.symbolic.collapse import trigger_collapse

# Check if collapse should be triggered
should_collapse = trigger_collapse(0.8)  # High threshold
forced_collapse = trigger_collapse(0.1, force=True)  # Force collapse
```

## Core Components

### GLYPH System
- **GLYPH_MAP**: Dictionary of available symbolic glyphs
- **get_glyph_meaning()**: Retrieves meaning for specific glyphs
- **GlyphRedactorEngine**: Advanced glyph processing

### Drift Detection
- **SymbolicDriftTracker**: Monitors symbolic drift patterns
- **get_drift_status()**: Categorizes drift levels
- **calculate_drift_score()**: Quantifies drift between states
- **DRIFT_CONFIG**: Configuration for drift detection

### Collapse System
- **CollapseEngine**: Core collapse processing
- **trigger_collapse()**: Determines if collapse should occur
- **COLLAPSE_CONFIG**: Configuration for collapse mechanisms

## Configuration

### Drift Configuration
```python
from lukhas.core.symbolic.drift import DRIFT_CONFIG

print(f"Drift configuration: {DRIFT_CONFIG}")
```

### Collapse Configuration
```python
from lukhas.core.symbolic.collapse import COLLAPSE_CONFIG

print(f"Collapse configuration: {COLLAPSE_CONFIG}")
```

## Integration

### Memory System Integration

The symbolic system integrates with the memory system through:

```python
from lukhas.core.memory import SYMBOLIC_INTEGRATION_ENABLED

if SYMBOLIC_INTEGRATION_ENABLED:
    # Symbolic context is included in memory operations
    pass
```

### Cross-Module Access

Access symbolic functions from other modules:

```python
# Import commonly used functions
from lukhas.core.symbolic import (
    GLYPH_MAP,
    get_glyph_meaning,
    get_drift_status,
    trigger_collapse
)
```

## Testing

Run symbolic system tests:

```bash
# All symbolic tests
pytest tests/ -m symbolic

# Specific subsystems
pytest tests/ -m "symbolic and drift"
pytest tests/ -m "symbolic and collapse"
pytest tests/symbolic/ -v
```

## Migration Notes

This module includes migrated functionality from:
- Original GLYPH system
- Drift detection mechanisms
- Collapse trigger systems
- Symbolic integration components

For migration details, see: `lukhas/docs/TEST_COVERAGE.md`

---

**Status**: Active
**Last Updated**: 2025-07-25 (TASK 18)
**Documentation**: Module-specific README for symbolic system
