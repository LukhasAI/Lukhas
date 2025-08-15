# Quantum-Inspired (QI) Components

This module contains quantum-inspired safety and calibration systems for LUKHAS AI.

## Components

### 1. Uncertainty & Calibration Engine (`qi/metrics/calibration.py`)

Tracks model confidence vs actual correctness to improve prediction reliability.

**Features:**
- Confidence calibration tracking (ECE - Expected Calibration Error)
- Per-module trust scores and adjustments
- Epistemic and aleatoric uncertainty estimation
- Historical event tracking with sliding window
- Automatic confidence adjustment suggestions

**Usage:**
```python
from qi.metrics.calibration import UncertaintyCalibrationEngine

engine = UncertaintyCalibrationEngine()

# Record a prediction
engine.record_prediction("consciousness", confidence=0.8, prediction="action_1")

# Record the outcome
engine.record_outcome("consciousness", "action_1", actual="result", correct=True)

# Get calibration score
score = engine.get_calibration_score()  # 0.0-1.0, higher is better

# Get confidence adjustment suggestion
adjustment = engine.suggest_confidence_adjustment("consciousness")  # -0.3 to +0.3
```

### 2. TEQ Coupler (`qi/safety/teq_gate.py`)

Transient Equilibrium Quantum-inspired gate that allows controlled exploration while maintaining safety.

**Features:**
- Dynamic state management (stable, exploring, transient, recovering, locked)
- Energy budget system for action intensity control
- Risk accumulation with safety thresholds
- Module-specific trust profiles
- Emergency lockdown and recovery mechanisms

**States:**
- **STABLE**: Normal operation, low-risk actions allowed
- **EXPLORING**: Controlled exploration with moderate limits
- **TRANSIENT**: Temporary instability for high-value exploration
- **RECOVERING**: Returning to stability, only safe actions
- **LOCKED**: Emergency safety mode, minimal actions

**Usage:**
```python
from qi.safety.teq_gate import TEQCoupler

teq = TEQCoupler(energy_budget=100.0)

# Evaluate an action
allowed, reason, suggestions = teq.evaluate_action(
    module="creativity",
    action="dream",
    risk_level=0.7,  # 0.0-1.0
    energy=5.0       # Energy cost
)

if allowed:
    # Proceed with action
    pass
else:
    # Action blocked, check suggestions
    print(f"Blocked: {reason}")
```

### 3. Integration Module (`qi/integration.py`)

Unified interface for using both QI components together.

**Usage:**
```python
from qi.integration import get_qi_integration

qi = get_qi_integration()

# Evaluate action through both systems
allowed, context = qi.evaluate_action(
    module="reasoning",
    action="hypothesize",
    confidence=0.75,
    risk_estimate=0.4,
    energy=3.0
)

# Record outcome for learning
qi.record_outcome("reasoning", "hypothesize", success=True)

# Get system status
status = qi.get_system_status()
```

## Running Demos

Test each component individually:

```bash
# Test Calibration Engine
python3 -m qi.metrics.calibration

# Test TEQ Coupler
python3 -m qi.safety.teq_gate

# Test Integration
python3 -m qi.integration
```

## Integration with LUKHAS

The QI components are designed to work seamlessly with LUKHAS modules:

1. **Before Action**: Call `qi.evaluate_action()` to check if action is safe
2. **After Action**: Call `qi.record_outcome()` to improve calibration
3. **Monitor**: Check `qi.get_system_status()` for health metrics

## State Persistence

Both components save state to `~/.lukhas/state/qi/`:
- Calibration data: `~/.lukhas/state/qi/calibration/`
- TEQ state: `~/.lukhas/state/qi/teq/`

## Safety Features

- **Automatic Lockdown**: TEQ enters lockdown if risk exceeds thresholds
- **Energy Budget**: Prevents runaway high-energy actions
- **Trust Scoring**: Modules build trust through good behavior
- **Calibration Learning**: System learns from outcomes to improve predictions
- **Emergency Reset**: `qi.emergency_reset()` for immediate safety recovery

## Configuration

Key parameters can be adjusted:

```python
# Calibration
engine = UncertaintyCalibrationEngine(
    window_size=1000  # Events to track
)

# TEQ Coupler
teq = TEQCoupler(
    stability_threshold=0.7,  # Risk threshold for stable state
    transient_duration=5.0,   # Seconds in transient state
    energy_budget=100.0       # Total energy budget
)
```

## License
Part of LUKHAS AI
