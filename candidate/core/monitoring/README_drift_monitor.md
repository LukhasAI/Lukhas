# LUKHAS AI - Unified Drift Monitor

## Overview

The Unified Drift Monitor (`drift_monitor.py`) is the centralized drift detection, analysis, and intervention system for LUKHAS Cognitive AI. This module consolidates all drift-related functionality into a single, orchestrated engine that monitors symbolic, emotional, ethical, temporal, and entropy drift across the system.

## Architecture

### Core Components Integration

1. **Symbolic Drift Tracker** (`lukhas.core.symbolic.drift.symbolic_drift_tracker`)
   - Enterprise-grade drift algorithms
   - Multi-dimensional state comparison
   - Recursive loop detection
   - GLYPH divergence analysis

2. **Ethical Drift Sentinel** (`lukhas.ethics.sentinel.ethical_drift_sentinel`)
   - Real-time ethical monitoring
   - Violation detection and escalation
   - Intervention triggering

3. **Simple Drift Components** (`lukhas.trace`)
   - Basic drift metrics
   - Harmonization suggestions
   - Emotional alignment tracking

### Drift Dimensions

The unified monitor tracks drift across five primary dimensions:

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Symbolic | 30% | Changes in GLYPH/ΛTAG symbolic state |
| Emotional | 25% | Shifts in VAD emotional vectors |
| Ethical | 20% | Deviations in ethical alignment |
| Temporal | 15% | Time-based drift factors |
| Entropy | 10% | Changes in state entropy |

### Key Metrics

- **drift_score**: Overall drift magnitude (0.0-1.0)
- **theta_delta**: Change in theta parameter between states
- **intent_drift**: Frequency of intent/purpose changes

## Usage

### Basic Example

```python
from lukhas.core.monitoring.drift_monitor import create_drift_monitor

# Create and start monitor
monitor = await create_drift_monitor({
    'symbolic': {
        'cascade_threshold': 0.85
    },
    'ethical_interval': 0.5
})

# Register a session
await monitor.register_session("session_123", {
    'symbols': ['ΛSTART', 'hope'],
    'emotional_vector': [0.7, 0.2, 0.8],
    'ethical_alignment': 0.9,
    'theta': 0.3,
    'intent': 'exploration'
})

# Update state (drift will be computed)
await monitor.update_session_state("session_123", {
    'symbols': ['ΛDRIFT', 'uncertainty'],
    'emotional_vector': [-0.3, 0.8, 0.2],
    'ethical_alignment': 0.5,
    'theta': 0.7,
    'intent': 'recovery'
})

# Get drift summary
summary = monitor.get_drift_summary("session_123")
```

## Intervention System

### Intervention Types

The monitor can trigger six types of interventions based on drift severity:

1. **SOFT_REALIGNMENT** - Gentle corrective suggestions
2. **ETHICAL_CORRECTION** - Ethics module engagement
3. **EMOTIONAL_GROUNDING** - Emotional stabilization
4. **SYMBOLIC_QUARANTINE** - Isolate unstable symbols
5. **CASCADE_PREVENTION** - Prevent system-wide cascade
6. **EMERGENCY_FREEZE** - Immediate system halt

### Intervention Thresholds

Default thresholds (configurable):

```python
{
    'soft': 0.3,
    'ethical': 0.5,
    'emotional': 0.6,
    'quarantine': 0.75,
    'cascade': 0.85,
    'freeze': 0.95
}
```

## Drift Phases

The system classifies drift into four phases:

- **EARLY** (0.0-0.25): Minor deviations, monitoring only
- **MIDDLE** (0.25-0.5): Moderate drift, soft interventions
- **LATE** (0.5-0.75): Significant drift, active interventions
- **CASCADE** (0.75-1.0): Critical drift, emergency measures

## Alert System

### Alert Structure

```python
DriftAlert:
    - alert_id: Unique identifier
    - timestamp: When detected
    - drift_type: Primary drift dimension
    - severity: NOTICE/WARNING/CRITICAL/CASCADE_LOCK
    - drift_score: Complete drift analysis
    - interventions: Recommended actions
```

### Alert Escalation

1. **NOTICE**: Logged only
2. **WARNING**: Active monitoring increased
3. **CRITICAL**: Interventions triggered
4. **CASCADE_LOCK**: Emergency protocols engaged

## Configuration

### Full Configuration Example

```python
config = {
    # Symbolic tracker settings
    'symbolic': {
        'caution_threshold': 0.3,
        'warning_threshold': 0.5,
        'critical_threshold': 0.7,
        'cascade_threshold': 0.85,
        'entropy_decay_rate': 0.05
    },

    # Ethical monitoring
    'ethical_interval': 0.5,  # seconds
    'violation_retention': 1000,

    # Harmonizer settings
    'harmonizer_threshold': 0.2,

    # Monitoring settings
    'monitoring_interval': 1.0,  # seconds

    # Drift computation weights
    'drift_weights': {
        'symbolic': 0.30,
        'emotional': 0.25,
        'ethical': 0.20,
        'temporal': 0.15,
        'entropy': 0.10
    },

    # Intervention thresholds
    'intervention_thresholds': {
        'soft': 0.3,
        'ethical': 0.5,
        'emotional': 0.6,
        'quarantine': 0.75,
        'cascade': 0.85,
        'freeze': 0.95
    }
}
```

## Testing

Comprehensive test suite available at `tests/monitoring/test_drift_monitor.py`:

```bash
pytest tests/monitoring/test_drift_monitor.py -v
```

Test coverage includes:
- Drift spike detection
- Repair loop simulation
- Multi-dimensional drift computation
- Intervention triggering
- Cascade prevention
- Ethics integration
- Recursive pattern detection

## Integration Points

### Required Injections

For full functionality, inject these components:

```python
monitor.memory_manager = memory_manager_instance
monitor.orchestrator = orchestrator_instance
monitor.collapse_reasoner = collapse_reasoner_instance
```

### Event Flow

1. Session state updated →
2. Drift computed across all dimensions →
3. Alert created if threshold exceeded →
4. Intervention queued →
5. Intervention executed →
6. Results logged

## Performance Characteristics

- **Drift Computation**: <100ms per state update
- **Memory Usage**: O(n) with bounded history (1000 alerts max)
- **CPU Usage**: Minimal, async operation
- **Intervention Latency**: <500ms from detection to execution

## Safety Features

1. **Automatic Interventions**: Triggered at configurable thresholds
2. **Cascade Prevention**: Activates at 0.85 drift score
3. **Emergency Freeze**: Engages at 0.95 drift score
4. **Ethical Override**: Ethics module can force interventions
5. **Recursive Loop Detection**: Prevents drift-repair cycles

## Monitoring & Observability

### Logs

Structured logging with ΛTAGS:
- `ΛMONITOR` - General monitoring events
- `ΛDRIFT` - Drift detection events
- `ΛALERT` - Alert generation
- `ΛINTERVENE` - Intervention execution
- `ΛFREEZE` - Emergency actions

### Metrics

Key metrics exposed:
- `drift_score_current` - Current drift levels
- `alerts_total` - Total alerts generated
- `interventions_executed` - Intervention counts by type
- `phase_transitions` - Movement between drift phases

### Dashboards

Compatible with standard monitoring tools:
- Prometheus metrics export
- Grafana dashboard templates
- Real-time visualization support

## Future Enhancements

1. **ML-based Drift Prediction**: Predict drift before it occurs
2. **Advanced Intent Analysis**: NLP for semantic intent drift
3. **Recovery Strategies**: Automated recovery playbooks
4. **Distributed Monitoring**: Multi-node drift consensus
5. **Visualization Dashboard**: Real-time drift visualization UI

## Migration from Legacy Components

This unified monitor replaces:
- Multiple drift tracker implementations
- Separate ethical monitoring
- Simple drift metrics
- Individual harmonizers

To migrate:
1. Replace imports with `lukhas.core.monitoring.drift_monitor`
2. Use `UnifiedDriftMonitor` instead of individual trackers
3. Configure weights and thresholds as needed
4. Update intervention handling code

## Support

For issues or questions:
- Check test suite for usage examples
- Review docstrings in source code
- Consult LUKHAS architecture documentation
- Contact: lukhas-drift@lukhas.ai

---

**Version**: 1.0.0
**Last Updated**: 2025-07-25
**Module**: `lukhas.core.monitoring.drift_monitor`
**Status**: Production Ready
