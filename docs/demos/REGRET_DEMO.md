# Regret Demo Runbook

**Target Audience**: Developers
**Duration**: ~2 minutes
**Purpose**: Demonstrate regret signature generation and continuity analysis

## Overview

The regret demo showcases the Oneiric dream system's ability to:
- Generate dreams with emotional signatures
- Track valence and arousal across dream sequences
- Emit regret signatures for post-hoc analysis
- Enable reproducible runs with seed locking

## Prerequisites

```bash
# Ensure you're in the Lukhas directory
cd /path/to/Lukhas

# Python 3.10+ required
python --version
```

## Running the Demo

### Method 1: CLI Command

```bash
python cli/lukhas.py demo-regret
```

### Method 2: Direct Python

```python
from oneiric.core.generator import DreamGenerator, SimpleEventBus

# Create event bus and generator
bus = SimpleEventBus()
generator = DreamGenerator(event_bus=bus)

# Generate dream with context
dream = generator.synthesize_dream({
    "seed_content": "Walking through a misty forest",
    "themes": ["mystery", "exploration"],
    "intensity": 0.7
})

# Get regret signature
signature = generator.get_last_signature()
print(f"Valence: {signature['valence']}")
print(f"Arousal: {signature['arousal']}")
print(f"Cause: {signature['cause_tag']}")
```

## Seed Lock for Reproducibility

Enable reproducible dream generation for testing:

```python
from oneiric.core.config import OneiricConfig

# Set seed lock
config = OneiricConfig(seed_lock=42)

# Now dream generation will be deterministic
# Same seed + same context = same dream
```

## Expected Outputs

### Dream Structure
```json
{
  "id": "dream_1234567890.123",
  "content": "A dream unfolds...",
  "themes": ["mystery", "exploration"],
  "intensity": 0.7,
  "timestamp": "2025-11-12T18:00:00.000Z"
}
```

### Regret Signature
```json
{
  "valence": 0.4,
  "arousal": 0.84,
  "cause_tag": "mystery",
  "timestamp": "2025-11-12T18:00:00.000Z"
}
```

## Rollback Notes

### Memory Fold Linkage

Dreams are automatically linked to memory folds and WaveC snapshots:

```python
from oneiric.core.persistence import DreamPersistence

persistence = DreamPersistence()

# Save with fold linkage
record = persistence.save_dream(
    dream,
    fold_id="fold_abc123",
    auto_link_wavec=True
)

# Retrieve dreams by fold
fold_dreams = persistence.get_dreams_by_fold("fold_abc123")
```

### WaveC Drift Detection

Dreams can trigger rollbacks if drift exceeds threshold:

```python
from core.wavec.checkpoint import WaveCCheckpoint

wavec = WaveCCheckpoint(drift_threshold=0.4)

# Create snapshot before dream
snapshot = wavec.create_snapshot(current_state)

# After dream generation
rollback = wavec.check_and_rollback(new_state)

if rollback:
    # Rollback occurred - check metadata
    print(rollback.metadata['drift_value'])
    print(rollback.metadata['branch_from'])
```

## Interpreting Results

### Valence
- **-1.0 to -0.5**: Strong negative (regret, sadness, loss)
- **-0.5 to 0.0**: Mild negative (unease, concern)
- **0.0 to 0.5**: Mild positive (contentment, hope)
- **0.5 to 1.0**: Strong positive (joy, achievement)

### Arousal
- **0.0 to 0.3**: Calm, low energy
- **0.3 to 0.7**: Moderate activation
- **0.7 to 1.0**: High intensity, strong activation

### Cause Tags
Common tags: `mystery`, `fear`, `joy`, `loss`, `achievement`, `exploration`

## Troubleshooting

### Issue: No regret signatures emitted

**Solution**: Ensure event bus is configured
```python
generator = DreamGenerator(event_bus=SimpleEventBus())
```

### Issue: Dreams not reproducible

**Solution**: Set seed lock in config
```python
config = OneiricConfig(seed_lock=42)
```

### Issue: WaveC rollbacks not triggering

**Solution**: Check drift threshold
```python
wavec = WaveCCheckpoint(drift_threshold=0.3)  # Lower = more sensitive
```

## Next Steps

1. Integrate with Guardian for emotional safety checks
2. Link to Memory system for long-term tracking
3. Add Endocrine system for hormone-emotion coupling
4. Enable MATRIZ analysis for emotional continuity

## References

- Oneiric Core: `oneiric/core/generator.py`
- Persistence: `oneiric/core/persistence.py`
- WaveC: `core/wavec/checkpoint.py`
- CLI: `cli/lukhas.py`
