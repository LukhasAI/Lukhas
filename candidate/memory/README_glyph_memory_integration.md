---
status: wip
type: documentation
---
# LUKHAS AI - Glyph-Memory Integration Module

## Overview

The Glyph-Memory Integration module (`glyph_memory_integration.py`) provides a comprehensive bridge between LUKHAS's symbolic glyph system and the memory fold architecture. This integration enables symbolic indexing, emotional coupling, and temporal compression of memories while preserving their glyph associations.

## Architecture

### Core Components

1. **GlyphMemoryIndex**
   - Maintains bidirectional mapping between glyphs and memory folds
   - Enables symbolic indexing and retrieval
   - Tracks binding strength and glyph affinity

2. **EmotionalFoldingEngine**
   - Implements temporal compression of memory folds
   - Preserves high-salience emotional states
   - Tracks emotional lineage through delta calculations
   - Supports multiple compression types (consolidation, abstraction, synthesis)

3. **GlyphAffectCoupler**
   - Manages coupling between glyphs and emotional states
   - Enables emotion-aware glyph retrieval
   - Provides affect propagation and modulation

4. **DreamMemoryBridge**
   - Connects dream states with memory glyphs
   - Enables dream-based memory consolidation
   - Tracks glyph activation patterns during dreams

5. **GlyphMemorySystem**
   - Main integration coordinator
   - Provides unified API for all subsystems
   - Manages configuration and statistics

## Key Features

### Symbolic Memory Indexing

Every memory fold can be associated with multiple glyphs, creating a rich symbolic network:

```python
memory = system.create_glyph_indexed_memory(
    emotion="joy",
    context="Successfully solved a complex problem",
    glyphs=["💡", "🌱", "✅"],
    user_id="user123"
)
```

### Glyph-Affect Coupling

Glyphs carry inherent emotional associations that can influence memory affect:

- 🌪️ (Chaos) → Fear/excitement affect
- 🛡️ (Protection) → Peaceful/secure affect
- 💡 (Insight) → Joy/excitement affect
- 🪞 (Reflection) → Contemplative/neutral affect

### Memory Folding with Temporal Compression

The system identifies and compresses related memories while preserving:
- Glyph associations
- Emotional trajectories
- High-salience states
- Causal relationships

### Emotional Lineage Tracking

Each folded memory maintains:
- Parent memory references
- Emotion vector deltas
- Compression ratios
- Temporal markers
- Preserved glyphs

## Usage Examples

### Basic Operations

```python
from lukhas.memory.glyph_memory_integration import get_glyph_memory_system

# Get global system instance
system = get_glyph_memory_system()

# Create memory with glyphs
memory = system.create_glyph_indexed_memory(
    emotion="curious",
    context="Discovered an interesting pattern",
    glyphs=["❓", "🔗", "👁️"]
)

# Recall by glyph pattern
insights = system.recall_by_glyph_pattern(
    glyphs=["💡", "🌱"],
    mode="any",  # or "all" for AND matching
    user_tier=3
)

# Perform temporal folding
results = system.perform_temporal_folding(
    time_window=timedelta(hours=24),
    min_salience=0.75
)
```

### Advanced Features

```python
# Process dream state
dream_results = system.dream_bridge.process_dream_state({
    'emotion': 'reflective',
    'content': 'Dream about past experiences',
    'glyphs': ['🪞', '🔁', '💡']
})

# Get glyph affinity
affinity = system.glyph_index.calculate_glyph_affinity("💡", "🌱")

# Retrieve by affect similarity
similar_memories = system.affect_coupler.retrieve_by_glyph_affect(
    target_glyph="🛡️",
    affect_threshold=0.3
)
```

## Configuration

The system uses the standard MemoryFoldConfig with additional glyph-specific settings:

```json
{
    "emotion_vectors": {
        "primary": {...},
        "secondary": {...}
    },
    "storage": {
        "type": "database",
        "db_path": "lukhas_memory_folds.db",
        "max_folds": 10000
    },
    "folding": {
        "temporal_window_hours": 24,
        "high_salience_threshold": 0.75,
        "emotional_drift_threshold": 0.3,
        "max_lineage_depth": 10
    }
}
```

## Testing and Visualization

The module includes comprehensive testing and visualization capabilities:

### Running Tests

```bash
python lukhas/tests/memory/test_glyph_memory_integration.py
```

### Generating Visualization

```bash
python lukhas/tests/memory/test_glyph_memory_integration.py demo
```

This generates an interactive HTML visualization showing:
- Memory fold timeline
- Glyph associations
- Emotional trajectories
- Lineage connections
- Compression statistics

## Integration Points

### Memory System
- Extends `MemoryFoldSystem` with glyph capabilities
- Compatible with existing memory fold operations
- Preserves database storage and tier-based access

### Glyph System
- Uses centralized `GLYPH_MAP` from `core.symbolic.glyphs`
- Supports dynamic glyph addition
- Maintains glyph semantic meanings

### Dream System
- Integrates with `dream_integration.py`
- Enables dream-triggered memory consolidation
- Tracks dream glyph activations

### Emotion System
- Uses emotion vectors for affect calculations
- Supports emotion distance metrics
- Enables emotional neighborhood discovery

## Performance Considerations

- **Indexing**: O(1) for glyph-to-memory lookups
- **Folding**: O(n log n) for memory group identification
- **Recall**: O(n) for pattern matching, optimized with indices
- **Storage**: Minimal overhead (~100 bytes per glyph binding)

## Future Enhancements

1. **Glyph Evolution**: Allow glyphs to evolve based on usage patterns
2. **Quantum Entanglement**: Support quantum-enhanced glyph relationships
3. **Predictive Folding**: Use AI to predict optimal folding times
4. **Multi-dimensional Glyphs**: Support compound glyph expressions
5. **Cross-module Integration**: Deeper integration with reasoning and consciousness modules

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all LUKHAS modules are in Python path
2. **Database Locks**: Check for concurrent access to memory database
3. **Memory Limits**: Monitor fold count and adjust max_folds setting
4. **Glyph Not Found**: Unknown glyphs are added dynamically with interpolated affects

### Debug Logging

Enable detailed logging:
```python
import logging
logging.getLogger("ΛTRACE.memory.glyph_integration").setLevel(logging.DEBUG)
```

## References

- [GLYPH_MAP Documentation](../core/symbolic/docs/GLYPH_GUIDANCE.md)
- [Memory Fold Architecture](./MEMORY_MODULE_ANALYSIS.md)
- [Dream Integration Guide](./core_memory/README.md)
- [Emotion Vector Specification](../emotion/README.md)

---

*Module created by Claude Code as part of Task 5: Memory-Glyph Linkage and Emotional Folding*
*Version 1.0.0 | Created: 2025-07-25*
