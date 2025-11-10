# LUKHAS Wrapper Modules Documentation

## Overview

Wrapper modules provide production-safe access to core consciousness, dream, and glyph functionality. All features are **OFF by default** and must be explicitly enabled via environment variables.

## Architecture

```
lukhas/
├── consciousness/   # Consciousness state & orchestration wrapper
├── dream/          # Dream simulation & parallel processing wrapper
└── glyphs/         # GLYPH symbolic communication wrapper
```

Each wrapper:
- ✅ Feature flag gated (default OFF)
- ✅ Safe imports (won't crash on missing deps)
- ✅ Graceful degradation
- ✅ Consistent API patterns
- ✅ Comprehensive logging

## Feature Flags

| Flag | Module | Default | Description |
|------|--------|---------|-------------|
| `LUKHAS_CONSCIOUSNESS_ENABLED` | consciousness | `0` | Enable consciousness subsystem |
| `LUKHAS_DREAMS_ENABLED` | dream | `0` | Enable dream simulation |
| `LUKHAS_PARALLEL_DREAMS` | dream | `0` | Enable parallel dream mesh |
| `LUKHAS_GLYPHS_ENABLED` | glyphs | `0` | Enable GLYPH encoding/binding |

### Enabling Features

```bash
# Enable dreams only
export LUKHAS_DREAMS_ENABLED=1

# Enable dreams with parallel processing
export LUKHAS_DREAMS_ENABLED=1
export LUKHAS_PARALLEL_DREAMS=1

# Enable all subsystems
export LUKHAS_CONSCIOUSNESS_ENABLED=1
export LUKHAS_DREAMS_ENABLED=1
export LUKHAS_GLYPHS_ENABLED=1
```

## Usage Examples

### Consciousness Wrapper

```python
from lukhas.consciousness import (
    is_enabled,
    get_consciousness_state,
    create_state,
    get_orchestrator
)

if is_enabled():
    # Get state for an agent
    state = get_consciousness_state("agent_id")

    # Create new state
    new_state = create_state(
        agent_id="new_agent",
        consciousness_type="agent",
        metadata={"role": "assistant"}
    )

    # Get network metrics
    from lukhas.consciousness import get_network_metrics
    metrics = get_network_metrics()
```

### Dream Wrapper

```python
from lukhas.dream import (
    is_enabled,
    simulate_dream,
    parallel_dream_mesh
)

if is_enabled():
    # Simulate a single dream
    result = simulate_dream(
        seed="morning_reflection",
        context={"mood": "calm", "time": "06:00"}
    )

    if result["success"]:
        dream_id = result["dream_id"]
        print(f"Dream created: {dream_id}")

    # Parallel dream mesh (if enabled)
    if is_parallel_enabled():
        mesh_result = parallel_dream_mesh(
            seeds=["seed1", "seed2", "seed3"],
            consensus_threshold=0.7
        )
```

### Glyphs Wrapper

```python
from lukhas.glyphs import (
    is_enabled,
    encode_concept,
    bind_glyph,
    validate_glyph
)

if is_enabled():
    # Encode a concept
    symbol = encode_concept(
        concept="morning_gratitude",
        emotion={"joy": 0.8, "calm": 0.6},
        source_module="daily_reflection"
    )

    # Validate GLYPH data
    glyph_data = {"concept": "test", "emotion": {"joy": 0.5}}
    is_valid, error = validate_glyph(glyph_data)

    if is_valid:
        # Bind to memory
        result = bind_glyph(
            glyph_data=glyph_data,
            memory_id="mem_123",
            user_id="user_1"
        )
```

## Safety Guarantees

### 1. Feature Flags Default OFF
```python
# Without env vars set, all functions return safely
from lukhas.dream import simulate_dream

result = simulate_dream("test")
# Returns: {"success": False, "error": "Dream subsystem not enabled"}
```

### 2. Import Safety
```python
# If core modules missing, wrappers still import
import lukhas.consciousness  # ✓ Always succeeds
lukhas.consciousness.is_enabled()  # ✓ Returns False if unavailable
```

### 3. Graceful Degradation
```python
# Functions return None or error dicts, never crash
from lukhas.consciousness import get_consciousness_state

state = get_consciousness_state("agent")
if state is None:
    # Handle unavailable state
    pass
```

## Testing

Run wrapper tests:
```bash
python -m pytest tests/unit/lukhas/test_wrappers.py -v
```

Test individual subsystems:
```bash
# Test all disabled (default)
python -c "import lukhas.consciousness, lukhas.dream, lukhas.glyphs; \
    print('All disabled:', \
    not lukhas.consciousness.is_enabled() and \
    not lukhas.dream.is_enabled() and \
    not lukhas.glyphs.is_enabled())"

# Test dreams enabled
LUKHAS_DREAMS_ENABLED=1 python -c "import lukhas.dream; \
    result = lukhas.dream.simulate_dream('test'); \
    print('Success:', result['success'])"
```

## API Reference

### Consciousness API

- `is_enabled() -> bool` - Check if subsystem available
- `get_consciousness_state(agent_id: str) -> Optional[ConsciousnessState]`
- `create_state(agent_id, consciousness_type, metadata) -> Optional[ConsciousnessState]`
- `get_orchestrator() -> Optional[MatrizConsciousnessOrchestrator]`
- `get_network_metrics() -> dict`

### Dream API

- `is_enabled() -> bool` - Check if subsystem available
- `is_parallel_enabled() -> bool` - Check if parallel processing enabled
- `simulate_dream(seed, context, parallel) -> dict`
- `get_dream_by_id(dream_id) -> Optional[dict]`
- `parallel_dream_mesh(seeds, consensus_threshold) -> dict`

### Glyphs API

- `is_enabled() -> bool` - Check if subsystem available
- `encode_concept(concept, emotion, modalities, domains) -> Optional[dict]`
- `decode_symbol(symbol_data) -> Optional[str]`
- `bind_glyph(glyph_data, memory_id, user_id, token) -> dict`
- `get_binding(binding_id) -> Optional[dict]`
- `validate_glyph(glyph_data) -> tuple[bool, Optional[str]]`
- `get_glyph_stats() -> dict`

## Deployment Checklist

Before enabling in production:

- [ ] Feature flag tested in staging
- [ ] Monitoring/observability configured
- [ ] Error handling validated
- [ ] Performance benchmarks met
- [ ] Security review completed
- [ ] Rollback plan documented
- [ ] Two-key approval obtained (for consciousness features)

## Troubleshooting

### "Subsystem not enabled" errors

Check environment variables:
```bash
env | grep LUKHAS_
```

### Import errors from core modules

Verify core modules exist:
```bash
ls -la labs/core/consciousness/
ls -la labs/core/glyph/
```

### Feature enabled but functions return None

Check logs for import errors:
```python
import logging
logging.basicConfig(level=logging.INFO)
import lukhas.consciousness  # Check log output
```

## Related Documentation

- [API Routes Documentation](../api/README.md)
- [Feature Flags Guide](../operations/FEATURE_FLAGS.md)
- [Core Integration Architecture](../../labs/core/README.md)

## Contributing

When modifying wrappers:

1. Maintain feature flag safety
2. Add tests for new functions
3. Update this documentation
4. Ensure backward compatibility
5. Keep error messages clear
