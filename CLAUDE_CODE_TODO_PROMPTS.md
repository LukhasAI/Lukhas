# Claude Code Web TODO Prompts
*Complex TODO delegation with full repository context*

**Generated**: 2025-11-13
**Repository**: LUKHAS AI - Constellation Framework with Constitutional AI
**Total Files**: 7,000+ Python files across 133 root directories

---

## 🗺️ LUKHAS Repository Navigation

### **Core Architecture - 3-Lane System**

LUKHAS uses a lane-based development model to safely evolve AI systems:

```
CANDIDATE/ (2,877 files) → CORE/ (253 files) → LUKHAS/ (692 files) → PRODUCTS/ (4,093 files)
  Research &                Integration         Production          Enterprise
  Development               Testing             Deployment          Systems
```

**CRITICAL IMPORT RULES**:
- `lukhas/` can import from `core/`, `matriz/`, `universal_language/`
- `candidate/` can import from `core/`, `matriz/` ONLY (NO lukhas imports)
- `core/` is the integration lane - bridge between research and production
- Strict boundaries prevent cross-lane contamination

### **Constellation Framework (8-Star System)**

The system coordinates eight foundational capabilities:
- **⚛️ Identity**: Authentication, Lambda ID system, secure access
- **✦ Memory**: Persistent state, context preservation, recall systems
- **🔬 Vision**: Perception, pattern recognition, visual processing
- **🌱 Bio**: Bio-inspired adaptation, organic growth patterns
- **🌙 Dream**: Creative synthesis, unconscious processing, imagination
- **⚖️ Ethics**: Moral reasoning, value alignment, decision frameworks
- **🛡️ Guardian**: Constitutional AI, ethical enforcement, drift detection
- **⚛️ Quantum**: Quantum-inspired algorithms, superposition, entanglement

### **Key Directories**

```
LOCAL-REPOS/Lukhas/
├── lukhas/                  # Production lane (692 components)
│   ├── core/               # Core system coordination
│   ├── consciousness/      # Consciousness processing
│   ├── governance/         # Guardian system
│   ├── identity/          # Lambda ID authentication
│   └── api/               # Public API
├── candidate/              # Development lane (2,877 files)
│   ├── consciousness/     # Advanced consciousness research
│   ├── core/              # Core system prototypes
│   ├── bio/               # Bio-inspired patterns
│   ├── quantum/           # Quantum-inspired algorithms
│   └── memory/            # Memory systems
├── core/                   # Integration lane (253 files)
│   ├── consciousness/     # Consciousness integration
│   ├── colonies/          # Multi-agent swarm systems
│   ├── identity/          # Identity integration
│   ├── governance/        # Governance integration
│   └── bridge/            # External system bridges
├── matriz/                 # MATRIZ cognitive engine (20 files + 16K assets)
├── tests/                  # Comprehensive test suites (775+ tests)
│   ├── smoke/             # Basic health checks
│   ├── unit/              # Component tests
│   ├── integration/       # Cross-system tests
│   └── e2e/               # End-to-end workflows
└── docs/                   # Documentation
    ├── architecture/      # Architecture guides
    └── governance/        # Guardian & ethics docs
```

### **Development Commands**

```bash
# Navigate to LUKHAS directory
cd /Users/agi_dev/LOCAL-REPOS/Lukhas

# Development
make dev               # Start development environment
make test              # Run comprehensive test suite (775+ tests)
make smoke             # Quick smoke tests (15 tests)
make lint              # Run linting and type checking

# Lane validation
make lane-guard        # Validate import boundaries (CRITICAL!)
make imports-guard     # Check import compliance

# Testing specific components
pytest tests/unit/test_<component>.py -v
pytest tests/integration/ -v --cov=.
```

### **Code Quality Standards**

- **Python Version**: 3.9+ (active: 3.11)
- **Type Hints**: Use `Optional[T]`, `Dict[K,V]`, `List[T]` (NOT `|` syntax - Python 3.9 compatible)
- **Test Coverage**: 75%+ coverage required for production promotion
- **Import Rules**: ALWAYS respect lane boundaries (validate with `make lane-guard`)
- **Docstrings**: Required for all public functions/classes
- **Security**: No hardcoded secrets, use environment variables

### **T4 System (TODO Management)**

LUKHAS uses T4 (TODO, Tech Debt, Triage, Track) for quality management:

```python
# T4 annotation format (when creating new TODOs)
# TODO[T4-ISSUE]: {"code":"RULE","ticket":"GH-XXXX","owner":"team","status":"planned","reason":"explanation","estimate":"Xh","priority":"medium","dependencies":"none"}
```

For these tasks, you're IMPLEMENTING existing TODOs, so you'll be REMOVING the TODO comments once complete.

---

## 📋 Complex TODO Tasks for Delegation

---

## TODO #1: Quantum Decision Superposition (Advanced Consciousness Feature)

**File**: `core/consciousness/bridge.py`
**Line**: 44
**Complexity**: High
**Estimated Effort**: 3-5 hours
**Owner**: consciousness-team

### **Context**

The Decision Making Bridge (DMB) module provides strategic decision-making capabilities for LUKHAS consciousness systems. Currently implements:
- Utility Maximization (cost-benefit optimization)
- Risk-Aware decision making (conservative with safety margins)
- Ethical Priority (values-based decisions)
- Collaborative consensus building
- Emergency rapid response
- Adaptive context-dependent strategies

**Current TODO**:
```python
# Line 44 in core/consciousness/bridge.py
TODO: Implement quantum decision superposition for parallel evaluation
```

### **Technical Requirements**

**Goal**: Implement quantum-inspired superposition for evaluating multiple decision strategies simultaneously.

**Quantum-Inspired Design Principles**:
1. **Superposition State**: Represent decision states as probability distributions across multiple strategies
2. **Parallel Evaluation**: Evaluate all strategies in superposition (conceptually parallel)
3. **Interference Patterns**: Allow strategies to constructively/destructively interfere
4. **Measurement/Collapse**: Collapse superposition to single decision based on confidence weights
5. **Entanglement**: Related decisions should influence each other's probability amplitudes

**Implementation Approach**:

```python
# Add to bridge.py after line 44

from typing import List, Tuple
import numpy as np

@dataclass
class QuantumDecisionState:
    """Represents decision in superposition across multiple strategies."""
    strategies: List[DecisionStrategy]  # List of strategies in superposition
    amplitudes: np.ndarray  # Complex probability amplitudes for each strategy
    phase_factors: np.ndarray  # Phase information for interference
    entangled_decisions: List[str] = field(default_factory=list)  # IDs of entangled decisions

    def normalize_amplitudes(self) -> None:
        """Ensure amplitudes represent valid probability distribution."""
        prob_sum = np.sum(np.abs(self.amplitudes) ** 2)
        self.amplitudes = self.amplitudes / np.sqrt(prob_sum)

    def add_interference(self, phase_shift: float) -> None:
        """Add interference pattern by adjusting phase factors."""
        self.phase_factors = self.phase_factors + phase_shift

    def measure(self) -> Tuple[DecisionStrategy, float]:
        """Collapse superposition to single strategy with confidence."""
        probabilities = np.abs(self.amplitudes) ** 2
        chosen_idx = np.random.choice(len(self.strategies), p=probabilities)
        confidence = float(probabilities[chosen_idx])
        return self.strategies[chosen_idx], confidence

class QuantumDecisionEngine:
    """Evaluates decisions using quantum superposition principles."""

    def __init__(self):
        self._entanglement_graph = {}  # Track decision entanglements
        self._history = []  # Store collapsed decisions for learning

    def create_superposition(
        self,
        strategies: List[DecisionStrategy],
        initial_weights: Optional[List[float]] = None
    ) -> QuantumDecisionState:
        """
        Create quantum decision state with strategies in superposition.

        Args:
            strategies: List of decision strategies to evaluate
            initial_weights: Optional prior weights for each strategy

        Returns:
            QuantumDecisionState with normalized amplitudes
        """
        n = len(strategies)

        if initial_weights is None:
            # Equal superposition (Hadamard-like)
            amplitudes = np.ones(n, dtype=complex) / np.sqrt(n)
        else:
            # Weighted superposition
            amplitudes = np.array([np.sqrt(w) for w in initial_weights], dtype=complex)

        phase_factors = np.zeros(n)

        state = QuantumDecisionState(
            strategies=strategies,
            amplitudes=amplitudes,
            phase_factors=phase_factors
        )
        state.normalize_amplitudes()
        return state

    def apply_interference(
        self,
        state: QuantumDecisionState,
        context: Dict[str, Any]
    ) -> None:
        """
        Apply constructive/destructive interference based on context.

        Strategies aligned with ethical principles get constructive interference.
        Strategies conflicting with safety get destructive interference.
        """
        for idx, strategy in enumerate(state.strategies):
            # Ethical alignment -> constructive interference (positive phase)
            ethical_score = context.get("ethical_alignment", {}).get(strategy.name, 0.5)
            # Risk level -> destructive for high-risk strategies (negative phase)
            risk_penalty = context.get("risk_level", {}).get(strategy.name, 0.0)

            # Phase shift combines ethical boost and risk penalty
            phase_shift = (ethical_score - 0.5) * np.pi - risk_penalty * np.pi/2
            state.phase_factors[idx] += phase_shift

        # Apply phase to amplitudes
        state.amplitudes = state.amplitudes * np.exp(1j * state.phase_factors)
        state.normalize_amplitudes()

    def entangle_decisions(
        self,
        decision_id1: str,
        decision_id2: str,
        correlation: float = 0.7
    ) -> None:
        """
        Create entanglement between two decisions.

        Entangled decisions influence each other's probability distributions.
        Used for related decisions that should be consistent.
        """
        if decision_id1 not in self._entanglement_graph:
            self._entanglement_graph[decision_id1] = {}
        if decision_id2 not in self._entanglement_graph:
            self._entanglement_graph[decision_id2] = {}

        self._entanglement_graph[decision_id1][decision_id2] = correlation
        self._entanglement_graph[decision_id2][decision_id1] = correlation

    def parallel_evaluate(
        self,
        state: QuantumDecisionState,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate all strategies in superposition before measurement.

        Returns evaluation metrics for all strategies without collapsing.
        """
        evaluations = {}

        for idx, strategy in enumerate(state.strategies):
            amplitude = state.amplitudes[idx]
            probability = float(np.abs(amplitude) ** 2)
            phase = float(np.angle(amplitude))

            evaluations[strategy.name] = {
                "probability": probability,
                "phase": phase,
                "amplitude_real": float(amplitude.real),
                "amplitude_imag": float(amplitude.imag)
            }

        return {
            "strategy_evaluations": evaluations,
            "entropy": self._calculate_entropy(state),
            "coherence": self._calculate_coherence(state)
        }

    def _calculate_entropy(self, state: QuantumDecisionState) -> float:
        """Calculate von Neumann entropy of decision state."""
        probabilities = np.abs(state.amplitudes) ** 2
        # Remove zero probabilities to avoid log(0)
        probabilities = probabilities[probabilities > 1e-10]
        entropy = -np.sum(probabilities * np.log2(probabilities))
        return float(entropy)

    def _calculate_coherence(self, state: QuantumDecisionState) -> float:
        """Measure quantum coherence (off-diagonal terms of density matrix)."""
        # Simplified coherence measure
        density_matrix = np.outer(state.amplitudes, np.conj(state.amplitudes))
        off_diagonal = density_matrix - np.diag(np.diag(density_matrix))
        coherence = float(np.sum(np.abs(off_diagonal)))
        return coherence

    def collapse_and_decide(
        self,
        state: QuantumDecisionState,
        decision_id: str
    ) -> Tuple[DecisionStrategy, float, Dict[str, Any]]:
        """
        Collapse superposition to single decision.

        Returns:
            (chosen_strategy, confidence, metadata)
        """
        chosen_strategy, confidence = state.measure()

        metadata = {
            "decision_id": decision_id,
            "available_strategies": [s.name for s in state.strategies],
            "chosen_strategy": chosen_strategy.name,
            "confidence": confidence,
            "measurement_time": datetime.now(timezone.utc).isoformat(),
            "pre_measurement_entropy": self._calculate_entropy(state)
        }

        # Store in history for learning
        self._history.append({
            "decision_id": decision_id,
            "strategy": chosen_strategy.name,
            "confidence": confidence
        })

        return chosen_strategy, confidence, metadata


# Integration into existing DecisionMakingBridge class
# Add this method to the DecisionMakingBridge class:

def evaluate_with_quantum_superposition(
    self,
    decision_id: str,
    strategies: List[DecisionStrategy],
    context: Dict[str, Any],
    apply_interference: bool = True,
    entangled_with: Optional[List[str]] = None
) -> Tuple[DecisionStrategy, float, Dict[str, Any]]:
    """
    Evaluate decision using quantum superposition of multiple strategies.

    This method creates a superposition of all candidate strategies,
    applies interference patterns based on ethical/risk context,
    and collapses to the optimal strategy.

    Args:
        decision_id: Unique identifier for this decision
        strategies: List of strategies to evaluate in superposition
        context: Decision context with ethical_alignment, risk_level, etc.
        apply_interference: Whether to apply constructive/destructive interference
        entangled_with: List of related decision IDs for entanglement

    Returns:
        (chosen_strategy, confidence, evaluation_metadata)
    """
    if not hasattr(self, '_quantum_engine'):
        self._quantum_engine = QuantumDecisionEngine()

    # Create superposition state
    state = self._quantum_engine.create_superposition(strategies)

    # Apply interference if requested
    if apply_interference:
        self._quantum_engine.apply_interference(state, context)

    # Handle entanglement
    if entangled_with:
        for related_id in entangled_with:
            self._quantum_engine.entangle_decisions(decision_id, related_id)

    # Parallel evaluation (pre-measurement)
    evaluation = self._quantum_engine.parallel_evaluate(state, context)

    # Collapse and decide
    chosen_strategy, confidence, metadata = self._quantum_engine.collapse_and_decide(
        state, decision_id
    )

    # Merge evaluation data into metadata
    metadata["parallel_evaluation"] = evaluation

    logger.info(
        f"Quantum decision collapsed: {chosen_strategy.name} "
        f"(confidence={confidence:.3f}, entropy={evaluation['entropy']:.3f})"
    )

    return chosen_strategy, confidence, metadata
```

### **Testing Requirements**

Create comprehensive tests in `tests/unit/core/consciousness/test_quantum_decision.py`:

```python
import pytest
import numpy as np
from core.consciousness.bridge import (
    QuantumDecisionState,
    QuantumDecisionEngine,
    DecisionStrategy
)

class TestQuantumDecisionSuperposition:

    def test_equal_superposition_creation(self):
        """Test creating equal superposition of strategies."""
        strategies = [
            DecisionStrategy("utility"),
            DecisionStrategy("ethical"),
            DecisionStrategy("risk_aware")
        ]

        engine = QuantumDecisionEngine()
        state = engine.create_superposition(strategies)

        # Equal superposition should have equal probabilities
        probabilities = np.abs(state.amplitudes) ** 2
        assert np.allclose(probabilities, [1/3, 1/3, 1/3], atol=1e-6)

    def test_weighted_superposition(self):
        """Test creating weighted superposition with prior beliefs."""
        strategies = [DecisionStrategy(f"s{i}") for i in range(3)]
        weights = [0.5, 0.3, 0.2]

        engine = QuantumDecisionEngine()
        state = engine.create_superposition(strategies, initial_weights=weights)

        probabilities = np.abs(state.amplitudes) ** 2
        assert np.allclose(probabilities, weights, atol=1e-6)

    def test_interference_pattern(self):
        """Test constructive/destructive interference."""
        strategies = [DecisionStrategy("ethical"), DecisionStrategy("risky")]
        engine = QuantumDecisionEngine()
        state = engine.create_superposition(strategies)

        # Ethical strategy gets boost, risky gets penalty
        context = {
            "ethical_alignment": {"ethical": 1.0, "risky": 0.0},
            "risk_level": {"ethical": 0.0, "risky": 1.0}
        }

        initial_probs = np.abs(state.amplitudes) ** 2
        engine.apply_interference(state, context)
        final_probs = np.abs(state.amplitudes) ** 2

        # Ethical strategy probability should increase
        assert final_probs[0] > initial_probs[0]
        # Risky strategy probability should decrease
        assert final_probs[1] < initial_probs[1]

    def test_measurement_collapse(self):
        """Test that measurement collapses to valid strategy."""
        strategies = [DecisionStrategy(f"s{i}") for i in range(5)]
        engine = QuantumDecisionEngine()
        state = engine.create_superposition(strategies)

        chosen, confidence = state.measure()

        assert chosen in strategies
        assert 0.0 <= confidence <= 1.0

    def test_entropy_calculation(self):
        """Test von Neumann entropy calculation."""
        strategies = [DecisionStrategy(f"s{i}") for i in range(4)]
        engine = QuantumDecisionEngine()

        # Equal superposition has maximum entropy
        state_equal = engine.create_superposition(strategies)
        entropy_equal = engine._calculate_entropy(state_equal)

        # Biased state has lower entropy
        state_biased = engine.create_superposition(strategies, [0.7, 0.1, 0.1, 0.1])
        entropy_biased = engine._calculate_entropy(state_biased)

        assert entropy_equal > entropy_biased
        assert 0 <= entropy_biased <= 2.0  # Maximum entropy is log2(4) = 2

    def test_decision_entanglement(self):
        """Test entanglement between related decisions."""
        engine = QuantumDecisionEngine()

        engine.entangle_decisions("decision_1", "decision_2", correlation=0.8)

        assert "decision_2" in engine._entanglement_graph["decision_1"]
        assert "decision_1" in engine._entanglement_graph["decision_2"]
        assert engine._entanglement_graph["decision_1"]["decision_2"] == 0.8

    def test_parallel_evaluation(self):
        """Test parallel evaluation returns data for all strategies."""
        strategies = [DecisionStrategy(f"s{i}") for i in range(3)]
        engine = QuantumDecisionEngine()
        state = engine.create_superposition(strategies)

        evaluation = engine.parallel_evaluate(state, {})

        assert "strategy_evaluations" in evaluation
        assert len(evaluation["strategy_evaluations"]) == 3
        assert "entropy" in evaluation
        assert "coherence" in evaluation

        for strat_name, metrics in evaluation["strategy_evaluations"].items():
            assert "probability" in metrics
            assert "phase" in metrics
            assert 0 <= metrics["probability"] <= 1
```

### **Acceptance Criteria**

✅ **Functional Requirements**:
- [ ] `QuantumDecisionState` class with amplitude normalization
- [ ] `QuantumDecisionEngine` class with all methods implemented
- [ ] Superposition creation (equal and weighted)
- [ ] Interference patterns (constructive/destructive based on context)
- [ ] Measurement/collapse mechanism returning strategy + confidence
- [ ] Entanglement tracking between related decisions
- [ ] Entropy and coherence calculations
- [ ] Integration method in `DecisionMakingBridge` class

✅ **Testing Requirements**:
- [ ] 100% test coverage for quantum decision module
- [ ] Unit tests for all quantum operations (8+ tests)
- [ ] Integration test with DecisionMakingBridge
- [ ] Smoke test in `tests/smoke/test_quantum_decision_smoke.py`

✅ **Documentation Requirements**:
- [ ] Docstrings for all classes and methods
- [ ] Inline comments explaining quantum-inspired concepts
- [ ] Example usage in module docstring
- [ ] Update `core/consciousness/bridge.py` module docstring to mention quantum superposition

✅ **Quality Standards**:
- [ ] Python 3.9+ compatible type hints (use `Optional[T]`, `Dict[K,V]`)
- [ ] Lane-guard validation passes (`make lane-guard`)
- [ ] Linting passes (`make lint`)
- [ ] No hardcoded values (use constants/config)
- [ ] TODO comment removed after implementation

### **LUKHAS-Specific Patterns**

1. **Logging**: Use structured logging with context
```python
logger.info(
    "Quantum decision event",
    extra={"decision_id": decision_id, "confidence": confidence}
)
```

2. **Error Handling**: Use LUKHAS exception patterns
```python
from lukhas.exceptions import LukhasError

if not strategies:
    raise LukhasError("Cannot create superposition with empty strategy list")
```

3. **Configuration**: Check environment variables for feature flags
```python
import os
ENABLE_QUANTUM_DECISIONS = os.getenv("ENABLE_QUANTUM_DECISIONS", "1") == "1"
```

4. **Performance**: Use numpy for vector operations (already imported)

5. **Constitutional AI**: Ensure ethical alignment is respected in interference patterns

### **References**

- **Module**: `core/consciousness/bridge.py` (Decision Making Bridge)
- **Related Systems**:
  - Ethics framework: `ethics/guardian/` (for ethical alignment scores)
  - Guardian system: `lukhas/governance/` (for constitutional validation)
- **Documentation**:
  - Architecture: `docs/architecture/consciousness.md`
  - Guardian system: `docs/governance/GUARDIAN_EXAMPLE.md`

---

## TODO #2: Guardian Feedback Integration for Adaptive Drift Thresholds

**File**: `core/colonies/ethics_swarm_colony.py`
**Line**: 92
**Complexity**: Medium-High
**Estimated Effort**: 2-4 hours
**Owner**: ethics-team / guardian-team

### **Context**

The `EthicsSwarmColony` manages ethical drift detection using a swarm of ethical signal watchers. Currently uses a fixed `drift_threshold` parameter (default 0.62). The Guardian system provides real-time feedback scores from constitutional AI evaluations that could be used to adaptively adjust drift detection sensitivity.

**Current TODO**:
```python
# Line 92 in core/colonies/ethics_swarm_colony.py
# ✅ TODO: integrate Guardian feedback scores for adaptive drift thresholds.
```

**Current Implementation**:
```python
def __init__(
    self,
    *,
    max_history: int = 64,
    drift_threshold: float = 0.62,  # Fixed threshold
    escalation_penalty: float = 0.12,
) -> None:
    self._signals: deque[EthicalSignal] = deque(maxlen=max_history)
    self.drift_threshold = max(0.0, min(drift_threshold, 1.0))
    self.escalation_penalty = escalation_penalty
```

### **Technical Requirements**

**Goal**: Integrate Guardian system feedback scores to dynamically adjust drift detection thresholds based on constitutional AI evaluations.

**Guardian Feedback System**:
- Guardian provides ethical compliance scores (0.0 to 1.0)
- Scores reflect alignment with constitutional principles
- Lower scores indicate ethical drift → should lower threshold (more sensitive)
- Higher scores indicate stability → can raise threshold (less sensitive)

**Implementation Approach**:

```python
# Add to core/colonies/ethics_swarm_colony.py

from typing import Optional, Deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

@dataclass
class GuardianFeedback:
    """Guardian system feedback for drift threshold adaptation."""
    score: float  # 0.0 to 1.0 (constitutional alignment)
    timestamp: datetime
    source: str  # Guardian component that provided feedback
    context: dict = field(default_factory=dict)


class AdaptiveDriftThresholdManager:
    """
    Manages dynamic drift threshold adjustment based on Guardian feedback.

    Uses exponential moving average of Guardian scores to adapt sensitivity.
    Lower Guardian scores → lower threshold (more sensitive to drift)
    Higher Guardian scores → higher threshold (less sensitive, system stable)
    """

    def __init__(
        self,
        base_threshold: float = 0.62,
        min_threshold: float = 0.3,
        max_threshold: float = 0.85,
        feedback_window: int = 20,
        adaptation_rate: float = 0.15
    ):
        """
        Initialize adaptive threshold manager.

        Args:
            base_threshold: Starting threshold value
            min_threshold: Minimum allowed threshold (max sensitivity)
            max_threshold: Maximum allowed threshold (min sensitivity)
            feedback_window: Number of feedback scores to track
            adaptation_rate: Rate of threshold adjustment (0.0 to 1.0)
        """
        self.base_threshold = base_threshold
        self.min_threshold = min_threshold
        self.max_threshold = max_threshold
        self.adaptation_rate = adaptation_rate

        self._feedback_history: Deque[GuardianFeedback] = deque(maxlen=feedback_window)
        self._current_threshold = base_threshold
        self._last_update = datetime.now(timezone.utc)

    def add_guardian_feedback(self, feedback: GuardianFeedback) -> None:
        """
        Add Guardian feedback and recalculate threshold.

        Args:
            feedback: Guardian feedback with score and metadata
        """
        self._feedback_history.append(feedback)
        self._recalculate_threshold()

        logger.info(
            "Guardian feedback received",
            extra={
                "score": feedback.score,
                "source": feedback.source,
                "new_threshold": self._current_threshold
            }
        )

    def _recalculate_threshold(self) -> None:
        """
        Recalculate drift threshold based on Guardian feedback history.

        Formula:
        - avg_score = exponential moving average of Guardian scores
        - If avg_score LOW (ethical issues) → threshold LOW (more sensitive)
        - If avg_score HIGH (ethical stability) → threshold HIGH (less sensitive)

        threshold = base_threshold + adaptation_rate * (avg_score - 0.5) * 2
        This maps avg_score [0,1] to threshold adjustment [-adaptation_rate, +adaptation_rate]
        """
        if not self._feedback_history:
            self._current_threshold = self.base_threshold
            return

        # Calculate exponential moving average
        weights = [0.8 ** i for i in range(len(self._feedback_history))]
        weights.reverse()  # Recent feedback gets higher weight
        total_weight = sum(weights)

        weighted_score = sum(
            fb.score * w for fb, w in zip(self._feedback_history, weights)
        ) / total_weight

        # Adapt threshold based on weighted score
        # Score 0.5 → no change
        # Score < 0.5 → decrease threshold (more sensitive)
        # Score > 0.5 → increase threshold (less sensitive)
        score_deviation = (weighted_score - 0.5) * 2  # Maps [0,1] to [-1,1]
        threshold_adjustment = self.adaptation_rate * score_deviation

        new_threshold = self.base_threshold + threshold_adjustment

        # Clamp to min/max bounds
        self._current_threshold = max(
            self.min_threshold,
            min(self.max_threshold, new_threshold)
        )

        self._last_update = datetime.now(timezone.utc)

    def get_current_threshold(self) -> float:
        """Get the currently adapted threshold value."""
        return self._current_threshold

    def get_feedback_summary(self) -> dict:
        """Get summary of Guardian feedback and threshold state."""
        if not self._feedback_history:
            return {
                "current_threshold": self._current_threshold,
                "feedback_count": 0,
                "avg_guardian_score": None
            }

        avg_score = sum(fb.score for fb in self._feedback_history) / len(self._feedback_history)

        return {
            "current_threshold": self._current_threshold,
            "base_threshold": self.base_threshold,
            "feedback_count": len(self._feedback_history),
            "avg_guardian_score": avg_score,
            "recent_scores": [fb.score for fb in list(self._feedback_history)[-5:]],
            "last_update": self._last_update.isoformat(),
            "threshold_bounds": {
                "min": self.min_threshold,
                "max": self.max_threshold
            }
        }

    def reset_to_baseline(self) -> None:
        """Reset threshold to baseline and clear history."""
        self._feedback_history.clear()
        self._current_threshold = self.base_threshold
        self._last_update = datetime.now(timezone.utc)

        logger.info("Drift threshold reset to baseline", extra={"threshold": self.base_threshold})


# Integration into EthicsSwarmColony
# Modify the __init__ method:

def __init__(
    self,
    *,
    max_history: int = 64,
    drift_threshold: float = 0.62,
    escalation_penalty: float = 0.12,
    enable_adaptive_threshold: bool = True,
    guardian_feedback_window: int = 20
) -> None:
    """
    Initialize Ethics Swarm Colony with optional adaptive drift threshold.

    Args:
        max_history: Maximum ethical signal history
        drift_threshold: Base drift threshold (used as baseline for adaptation)
        escalation_penalty: Penalty for ethical escalations
        enable_adaptive_threshold: Enable Guardian feedback-based adaptation
        guardian_feedback_window: Number of Guardian feedback scores to track
    """
    self._signals: deque[EthicalSignal] = deque(maxlen=max_history)
    self.escalation_penalty = escalation_penalty

    # Initialize adaptive threshold manager
    self._enable_adaptive = enable_adaptive_threshold
    if enable_adaptive_threshold:
        self._threshold_manager = AdaptiveDriftThresholdManager(
            base_threshold=drift_threshold,
            feedback_window=guardian_feedback_window
        )
        self.drift_threshold = self._threshold_manager.get_current_threshold()
    else:
        self.drift_threshold = max(0.0, min(drift_threshold, 1.0))
        self._threshold_manager = None


# Add new method to EthicsSwarmColony:

def update_guardian_feedback(
    self,
    score: float,
    source: str = "guardian",
    context: Optional[dict] = None
) -> None:
    """
    Update drift threshold based on Guardian system feedback.

    Args:
        score: Guardian ethical compliance score (0.0 to 1.0)
        source: Guardian component providing feedback
        context: Additional context about the feedback
    """
    if not self._enable_adaptive:
        logger.debug("Adaptive threshold disabled, ignoring Guardian feedback")
        return

    feedback = GuardianFeedback(
        score=max(0.0, min(1.0, score)),  # Clamp to valid range
        timestamp=datetime.now(timezone.utc),
        source=source,
        context=context or {}
    )

    self._threshold_manager.add_guardian_feedback(feedback)
    self.drift_threshold = self._threshold_manager.get_current_threshold()

    logger.info(
        "Drift threshold updated from Guardian feedback",
        extra={
            "guardian_score": score,
            "new_threshold": self.drift_threshold,
            "source": source
        }
    )


# Add method to get threshold state:

def get_threshold_state(self) -> dict:
    """
    Get current drift threshold state and adaptation metrics.

    Returns:
        Dict with threshold value, adaptation status, and Guardian feedback summary
    """
    base_state = {
        "current_threshold": self.drift_threshold,
        "adaptive_enabled": self._enable_adaptive
    }

    if self._enable_adaptive and self._threshold_manager:
        base_state.update(self._threshold_manager.get_feedback_summary())

    return base_state
```

### **Testing Requirements**

Create tests in `tests/unit/core/colonies/test_guardian_feedback_integration.py`:

```python
import pytest
from datetime import datetime, timezone
from core.colonies.ethics_swarm_colony import (
    EthicsSwarmColony,
    GuardianFeedback,
    AdaptiveDriftThresholdManager
)

class TestAdaptiveDriftThreshold:

    def test_threshold_increases_with_high_guardian_scores(self):
        """High Guardian scores should increase threshold (less sensitive)."""
        manager = AdaptiveDriftThresholdManager(base_threshold=0.62)

        # Add high Guardian scores (ethical stability)
        for _ in range(10):
            manager.add_guardian_feedback(
                GuardianFeedback(score=0.9, timestamp=datetime.now(timezone.utc), source="test")
            )

        # Threshold should increase (less sensitive since system is stable)
        assert manager.get_current_threshold() > 0.62

    def test_threshold_decreases_with_low_guardian_scores(self):
        """Low Guardian scores should decrease threshold (more sensitive)."""
        manager = AdaptiveDriftThresholdManager(base_threshold=0.62)

        # Add low Guardian scores (ethical drift detected)
        for _ in range(10):
            manager.add_guardian_feedback(
                GuardianFeedback(score=0.2, timestamp=datetime.now(timezone.utc), source="test")
            )

        # Threshold should decrease (more sensitive to detect drift)
        assert manager.get_current_threshold() < 0.62

    def test_threshold_respects_bounds(self):
        """Threshold should stay within min/max bounds."""
        manager = AdaptiveDriftThresholdManager(
            base_threshold=0.62,
            min_threshold=0.3,
            max_threshold=0.85
        )

        # Try to push threshold below minimum
        for _ in range(50):
            manager.add_guardian_feedback(
                GuardianFeedback(score=0.0, timestamp=datetime.now(timezone.utc), source="test")
            )
        assert manager.get_current_threshold() >= 0.3

        # Try to push threshold above maximum
        manager.reset_to_baseline()
        for _ in range(50):
            manager.add_guardian_feedback(
                GuardianFeedback(score=1.0, timestamp=datetime.now(timezone.utc), source="test")
            )
        assert manager.get_current_threshold() <= 0.85

    def test_exponential_moving_average_weights_recent_feedback(self):
        """Recent Guardian feedback should have more weight."""
        manager = AdaptiveDriftThresholdManager(base_threshold=0.62)

        # Add old low scores
        for _ in range(10):
            manager.add_guardian_feedback(
                GuardianFeedback(score=0.2, timestamp=datetime.now(timezone.utc), source="test")
            )

        threshold_after_low = manager.get_current_threshold()

        # Add recent high scores (should pull threshold back up)
        for _ in range(5):
            manager.add_guardian_feedback(
                GuardianFeedback(score=0.9, timestamp=datetime.now(timezone.utc), source="test")
            )

        threshold_after_high = manager.get_current_threshold()

        # Recent high scores should increase threshold
        assert threshold_after_high > threshold_after_low

    def test_ethics_swarm_colony_integration(self):
        """Test EthicsSwarmColony integration with adaptive threshold."""
        colony = EthicsSwarmColony(
            drift_threshold=0.62,
            enable_adaptive_threshold=True
        )

        initial_threshold = colony.drift_threshold

        # Update with Guardian feedback
        colony.update_guardian_feedback(score=0.9, source="guardian_test")

        # Threshold should have changed
        assert colony.drift_threshold != initial_threshold

        # Get state
        state = colony.get_threshold_state()
        assert state["adaptive_enabled"] is True
        assert "avg_guardian_score" in state

    def test_adaptive_threshold_can_be_disabled(self):
        """Test that adaptive threshold can be disabled."""
        colony = EthicsSwarmColony(
            drift_threshold=0.62,
            enable_adaptive_threshold=False
        )

        initial_threshold = colony.drift_threshold

        # Try to update with Guardian feedback (should be ignored)
        colony.update_guardian_feedback(score=0.2, source="guardian_test")

        # Threshold should not change
        assert colony.drift_threshold == initial_threshold

    def test_feedback_summary(self):
        """Test Guardian feedback summary."""
        manager = AdaptiveDriftThresholdManager(base_threshold=0.62)

        # Add some feedback
        for score in [0.8, 0.7, 0.9, 0.6, 0.85]:
            manager.add_guardian_feedback(
                GuardianFeedback(score=score, timestamp=datetime.now(timezone.utc), source="test")
            )

        summary = manager.get_feedback_summary()

        assert summary["feedback_count"] == 5
        assert 0 <= summary["avg_guardian_score"] <= 1
        assert len(summary["recent_scores"]) == 5
        assert "threshold_bounds" in summary
```

### **Acceptance Criteria**

✅ **Functional Requirements**:
- [ ] `GuardianFeedback` dataclass created
- [ ] `AdaptiveDriftThresholdManager` class implemented
- [ ] Exponential moving average calculation for Guardian scores
- [ ] Threshold adaptation formula (maps score [0,1] to threshold adjustment)
- [ ] Min/max bounds enforcement
- [ ] Integration into `EthicsSwarmColony.__init__`
- [ ] `update_guardian_feedback()` method
- [ ] `get_threshold_state()` method
- [ ] Optional enable/disable flag (`enable_adaptive_threshold`)

✅ **Testing Requirements**:
- [ ] Unit tests for `AdaptiveDriftThresholdManager` (6+ tests)
- [ ] Integration tests with `EthicsSwarmColony`
- [ ] Test threshold increases with high Guardian scores
- [ ] Test threshold decreases with low Guardian scores
- [ ] Test bounds enforcement
- [ ] Test exponential moving average weighting
- [ ] Test disabled mode

✅ **Documentation**:
- [ ] Docstrings for all new classes and methods
- [ ] Inline comments explaining adaptation formula
- [ ] Example usage in module docstring
- [ ] TODO comment removed

✅ **Integration with Guardian**:
- [ ] Design supports Guardian system callback pattern
- [ ] Compatible with existing Guardian feedback API
- [ ] Handles missing/invalid feedback gracefully

### **Guardian System Integration Notes**

The Guardian system (in `lukhas/governance/`) provides constitutional AI oversight. To integrate:

1. **Guardian Feedback Format**:
```python
# Guardian systems should call:
ethics_swarm.update_guardian_feedback(
    score=guardian_compliance_score,  # 0.0 to 1.0
    source="guardian_constitutional_ai",
    context={
        "principle_violated": "autonomy",
        "severity": "low",
        "recommendation": "adjust_threshold"
    }
)
```

2. **Callback Pattern**:
```python
# Guardian can register callback
def on_guardian_evaluation(result):
    ethics_swarm.update_guardian_feedback(
        score=result.compliance_score,
        source=result.guardian_component,
        context=result.metadata
    )
```

3. **Environment Configuration**:
```python
# config/settings.py
ADAPTIVE_DRIFT_ENABLED = os.getenv("ADAPTIVE_DRIFT_ENABLED", "1") == "1"
DRIFT_ADAPTATION_RATE = float(os.getenv("DRIFT_ADAPTATION_RATE", "0.15"))
```

### **References**

- **Module**: `core/colonies/ethics_swarm_colony.py`
- **Guardian System**: `lukhas/governance/` and `ethics/guardian/`
- **Constitutional AI**: `ethics/guardian/claude.me`
- **Documentation**: `docs/governance/GUARDIAN_EXAMPLE.md`

---

## TODO #3: Drift Detector Archival Persistence

**File**: `core/consciousness/drift_detector.py`
**Line**: 103
**Complexity**: Medium
**Estimated Effort**: 2-3 hours
**Owner**: consciousness-team / governance-team

### **Context**

The `DriftDetector` monitors ethical drift across consciousness layers. Currently has a `reset()` method that clears all history but doesn't persist it. For audit and compliance purposes, cleared drift history should be archived to persistent storage for reconciliation.

**Current TODO**:
```python
# Line 103 in core/consciousness/drift_detector.py
# TODO: persist cleared state to archival store for audit reconciliation.
```

**Current Implementation**:
```python
def reset(self) -> None:
    """Clear all recorded history."""
    self._history.clear()
    self._logger.info("# ΛTAG: drift_reset -- cleared drift detector history")
    # TODO: persist cleared state to archival store for audit reconciliation.
```

### **Technical Requirements**

**Goal**: Persist drift history to archival storage before clearing, enabling audit trails and compliance reporting.

**Archival Requirements**:
1. **Immutable Archive**: Once written, drift snapshots cannot be modified
2. **Timestamped**: Each archive entry has clear timestamp
3. **Queryable**: Support queries by time range, layer, drift severity
4. **Compliance Ready**: Support GDPR/audit trail requirements
5. **Storage Backend**: Support file-based and database backends

**Implementation Approach**:

```python
# Add to core/consciousness/drift_detector.py

import json
import sqlite3
from pathlib import Path
from typing import Protocol, Optional, List
from datetime import datetime, timezone
from dataclasses import asdict

class DriftArchiveBackend(Protocol):
    """Protocol for drift history archival backends."""

    def archive_snapshot(self, snapshot: dict) -> str:
        """
        Archive a drift detection snapshot.

        Args:
            snapshot: Drift snapshot with layers, timestamps, metrics

        Returns:
            Archive ID for the stored snapshot
        """
        ...

    def query_archives(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        layer: Optional[str] = None,
        min_drift: Optional[float] = None
    ) -> List[dict]:
        """Query archived drift snapshots."""
        ...


class FileDriftArchive:
    """File-based drift archive using JSON lines."""

    def __init__(self, archive_dir: Path):
        """
        Initialize file-based archive.

        Args:
            archive_dir: Directory to store archive files
        """
        self.archive_dir = Path(archive_dir)
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        self._current_file = self._get_current_archive_file()

    def _get_current_archive_file(self) -> Path:
        """Get current archive file (one per day)."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return self.archive_dir / f"drift_archive_{today}.jsonl"

    def archive_snapshot(self, snapshot: dict) -> str:
        """Archive snapshot to JSON lines file."""
        archive_id = f"drift_{datetime.now(timezone.utc).isoformat()}"

        archive_entry = {
            "archive_id": archive_id,
            "archived_at": datetime.now(timezone.utc).isoformat(),
            "snapshot": snapshot
        }

        # Append to daily archive file
        with open(self._current_file, 'a') as f:
            f.write(json.dumps(archive_entry) + '\n')

        return archive_id

    def query_archives(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        layer: Optional[str] = None,
        min_drift: Optional[float] = None
    ) -> List[dict]:
        """Query archived snapshots from JSON lines files."""
        results = []

        # Scan all archive files
        for archive_file in sorted(self.archive_dir.glob("drift_archive_*.jsonl")):
            with open(archive_file, 'r') as f:
                for line in f:
                    entry = json.loads(line)

                    # Apply filters
                    archived_at = datetime.fromisoformat(entry["archived_at"])
                    if start_time and archived_at < start_time:
                        continue
                    if end_time and archived_at > end_time:
                        continue

                    # Layer and drift filters require parsing snapshot
                    if layer or min_drift:
                        snapshot = entry["snapshot"]
                        if layer:
                            # Filter by layer presence
                            if layer not in snapshot.get("layers", {}):
                                continue
                        if min_drift:
                            # Filter by drift score
                            layers = snapshot.get("layers", {})
                            max_drift = max(
                                (l.get("drift_score", 0) for l in layers.values()),
                                default=0
                            )
                            if max_drift < min_drift:
                                continue

                    results.append(entry)

        return results


class SQLiteDriftArchive:
    """SQLite-based drift archive with indexed queries."""

    def __init__(self, db_path: Path):
        """
        Initialize SQLite archive.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    def _init_database(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS drift_archives (
                    archive_id TEXT PRIMARY KEY,
                    archived_at TIMESTAMP NOT NULL,
                    snapshot_json TEXT NOT NULL,
                    max_drift_score REAL,
                    layer_count INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create indexes for common queries
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_archived_at
                ON drift_archives(archived_at)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_max_drift
                ON drift_archives(max_drift_score)
            """)

            conn.commit()

    def archive_snapshot(self, snapshot: dict) -> str:
        """Archive snapshot to SQLite database."""
        archive_id = f"drift_{datetime.now(timezone.utc).isoformat()}"
        archived_at = datetime.now(timezone.utc).isoformat()

        # Extract metadata for indexing
        layers = snapshot.get("layers", {})
        max_drift_score = max(
            (l.get("drift_score", 0) for l in layers.values()),
            default=0
        )
        layer_count = len(layers)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO drift_archives
                (archive_id, archived_at, snapshot_json, max_drift_score, layer_count)
                VALUES (?, ?, ?, ?, ?)
            """, (
                archive_id,
                archived_at,
                json.dumps(snapshot),
                max_drift_score,
                layer_count
            ))
            conn.commit()

        return archive_id

    def query_archives(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        layer: Optional[str] = None,
        min_drift: Optional[float] = None
    ) -> List[dict]:
        """Query archived snapshots with indexed filtering."""
        query = "SELECT archive_id, archived_at, snapshot_json FROM drift_archives WHERE 1=1"
        params = []

        if start_time:
            query += " AND archived_at >= ?"
            params.append(start_time.isoformat())
        if end_time:
            query += " AND archived_at <= ?"
            params.append(end_time.isoformat())
        if min_drift:
            query += " AND max_drift_score >= ?"
            params.append(min_drift)

        query += " ORDER BY archived_at DESC"

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, params)
            results = []

            for row in cursor:
                archive_id, archived_at, snapshot_json = row
                snapshot = json.loads(snapshot_json)

                # Additional layer filter (not indexed)
                if layer:
                    if layer not in snapshot.get("layers", {}):
                        continue

                results.append({
                    "archive_id": archive_id,
                    "archived_at": archived_at,
                    "snapshot": snapshot
                })

        return results


# Modify DriftDetector class
class DriftDetector:
    """Drift detection with archival support."""

    def __init__(
        self,
        *,
        archive_backend: Optional[DriftArchiveBackend] = None,
        archive_on_reset: bool = True
    ):
        """
        Initialize drift detector with optional archival.

        Args:
            archive_backend: Backend for archiving drift snapshots
            archive_on_reset: Whether to archive history on reset
        """
        self._history: dict = {}
        self._logger = logging.getLogger(__name__)
        self._archive_backend = archive_backend
        self._archive_on_reset = archive_on_reset

        # Initialize default archive if none provided
        if archive_backend is None and archive_on_reset:
            # Use file-based archive by default
            archive_dir = Path("data/drift_archives")
            self._archive_backend = FileDriftArchive(archive_dir)

    def reset(self) -> Optional[str]:
        """
        Clear all recorded history with optional archival.

        Returns:
            Archive ID if snapshot was archived, None otherwise
        """
        archive_id = None

        # Archive before clearing if enabled
        if self._archive_on_reset and self._archive_backend:
            try:
                snapshot = self.summarize()
                archive_id = self._archive_backend.archive_snapshot(snapshot)

                self._logger.info(
                    "# ΛTAG: drift_reset -- archived drift history",
                    extra={
                        "archive_id": archive_id,
                        "layer_count": len(snapshot.get("layers", {}))
                    }
                )
            except Exception as e:
                self._logger.error(
                    f"# ΛTAG: drift_reset -- failed to archive: {e}",
                    exc_info=True
                )

        # Clear history
        self._history.clear()
        self._logger.info("# ΛTAG: drift_reset -- cleared drift detector history")

        return archive_id

    def query_archived_snapshots(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        layer: Optional[str] = None,
        min_drift: Optional[float] = None
    ) -> List[dict]:
        """
        Query archived drift snapshots.

        Args:
            start_time: Filter by minimum archive time
            end_time: Filter by maximum archive time
            layer: Filter by layer name
            min_drift: Filter by minimum drift score

        Returns:
            List of archived snapshots matching filters
        """
        if not self._archive_backend:
            self._logger.warning("No archive backend configured")
            return []

        return self._archive_backend.query_archives(
            start_time=start_time,
            end_time=end_time,
            layer=layer,
            min_drift=min_drift
        )


# Factory function for archive backends
def get_drift_archive_backend(
    backend_type: str = "file",
    **kwargs
) -> DriftArchiveBackend:
    """
    Factory for creating drift archive backends.

    Args:
        backend_type: Type of backend ("file" or "sqlite")
        **kwargs: Backend-specific configuration

    Returns:
        Configured archive backend
    """
    if backend_type == "file":
        archive_dir = kwargs.get("archive_dir", Path("data/drift_archives"))
        return FileDriftArchive(archive_dir)
    elif backend_type == "sqlite":
        db_path = kwargs.get("db_path", Path("data/drift_archives.db"))
        return SQLiteDriftArchive(db_path)
    else:
        raise ValueError(f"Unknown backend type: {backend_type}")
```

### **Testing Requirements**

Create tests in `tests/unit/core/consciousness/test_drift_archival.py`:

```python
import pytest
from pathlib import Path
from datetime import datetime, timezone, timedelta
from core.consciousness.drift_detector import (
    DriftDetector,
    FileDriftArchive,
    SQLiteDriftArchive,
    get_drift_archive_backend
)

class TestFileDriftArchive:

    @pytest.fixture
    def archive_dir(self, tmp_path):
        """Temporary archive directory."""
        return tmp_path / "drift_archives"

    @pytest.fixture
    def file_archive(self, archive_dir):
        """File-based archive."""
        return FileDriftArchive(archive_dir)

    def test_archive_creates_directory(self, archive_dir):
        """Archive should create directory if it doesn't exist."""
        archive = FileDriftArchive(archive_dir)
        assert archive_dir.exists()

    def test_archive_snapshot(self, file_archive):
        """Test archiving a drift snapshot."""
        snapshot = {
            "layers": {
                "layer1": {"drift_score": 0.75, "affect_delta": 0.2}
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        archive_id = file_archive.archive_snapshot(snapshot)

        assert archive_id.startswith("drift_")
        # Verify file was created
        archive_files = list(file_archive.archive_dir.glob("drift_archive_*.jsonl"))
        assert len(archive_files) > 0

    def test_query_archives(self, file_archive):
        """Test querying archived snapshots."""
        # Archive multiple snapshots
        now = datetime.now(timezone.utc)

        for i in range(3):
            snapshot = {
                "layers": {
                    "layer1": {"drift_score": 0.5 + i * 0.1}
                },
                "timestamp": (now - timedelta(hours=i)).isoformat()
            }
            file_archive.archive_snapshot(snapshot)

        # Query all
        results = file_archive.query_archives()
        assert len(results) == 3

        # Query with min_drift filter
        results = file_archive.query_archives(min_drift=0.6)
        assert len(results) == 2  # Only snapshots with drift >= 0.6


class TestSQLiteDriftArchive:

    @pytest.fixture
    def db_path(self, tmp_path):
        """Temporary database path."""
        return tmp_path / "drift_archives.db"

    @pytest.fixture
    def sqlite_archive(self, db_path):
        """SQLite archive."""
        return SQLiteDriftArchive(db_path)

    def test_database_initialization(self, sqlite_archive, db_path):
        """Test database schema creation."""
        assert db_path.exists()

        import sqlite3
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='drift_archives'"
            )
            tables = cursor.fetchall()
            assert len(tables) == 1

    def test_archive_snapshot_with_indexing(self, sqlite_archive):
        """Test archiving with metadata indexing."""
        snapshot = {
            "layers": {
                "layer1": {"drift_score": 0.75},
                "layer2": {"drift_score": 0.60}
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        archive_id = sqlite_archive.archive_snapshot(snapshot)

        assert archive_id.startswith("drift_")

        # Verify indexed metadata
        import sqlite3
        with sqlite3.connect(sqlite_archive.db_path) as conn:
            cursor = conn.execute(
                "SELECT max_drift_score, layer_count FROM drift_archives WHERE archive_id = ?",
                (archive_id,)
            )
            row = cursor.fetchone()
            assert row[0] == 0.75  # max drift score
            assert row[1] == 2     # layer count

    def test_indexed_query_performance(self, sqlite_archive):
        """Test that queries use indexes."""
        # Archive many snapshots
        for i in range(100):
            snapshot = {
                "layers": {"layer1": {"drift_score": i / 100}},
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            sqlite_archive.archive_snapshot(snapshot)

        # Query with indexed filter (should be fast)
        start_time = datetime.now(timezone.utc) - timedelta(minutes=5)
        results = sqlite_archive.query_archives(
            start_time=start_time,
            min_drift=0.5
        )

        # Should find ~50 results with drift >= 0.5
        assert len(results) >= 45


class TestDriftDetectorWithArchival:

    @pytest.fixture
    def archive_backend(self, tmp_path):
        """File-based archive backend."""
        return FileDriftArchive(tmp_path / "archives")

    def test_reset_archives_history(self, archive_backend):
        """Test that reset() archives history before clearing."""
        detector = DriftDetector(
            archive_backend=archive_backend,
            archive_on_reset=True
        )

        # Simulate some drift history
        # (Assuming detector has methods to record drift - adjust as needed)
        # detector.record_drift("layer1", 0.75, 0.2)

        # Reset should return archive ID
        archive_id = detector.reset()

        assert archive_id is not None
        assert archive_id.startswith("drift_")

    def test_archival_can_be_disabled(self, archive_backend):
        """Test that archival can be disabled."""
        detector = DriftDetector(
            archive_backend=archive_backend,
            archive_on_reset=False
        )

        archive_id = detector.reset()

        # Should not archive
        assert archive_id is None

    def test_query_archived_snapshots(self, archive_backend):
        """Test querying archived snapshots from detector."""
        detector = DriftDetector(
            archive_backend=archive_backend,
            archive_on_reset=True
        )

        # Archive some snapshots
        for _ in range(3):
            detector.reset()

        # Query archives
        results = detector.query_archived_snapshots()

        assert len(results) >= 3

    def test_archive_failure_does_not_prevent_reset(self, tmp_path):
        """Test that archive failure doesn't block reset."""
        # Create archive with invalid path (will fail)
        bad_archive = FileDriftArchive(Path("/invalid/path/archives"))

        detector = DriftDetector(
            archive_backend=bad_archive,
            archive_on_reset=True
        )

        # Reset should complete even if archive fails
        archive_id = detector.reset()

        # Archive should fail, but reset should succeed
        assert archive_id is None  # Archive failed


class TestArchiveBackendFactory:

    def test_create_file_backend(self):
        """Test creating file archive backend."""
        backend = get_drift_archive_backend(
            backend_type="file",
            archive_dir=Path("/tmp/test_archives")
        )

        assert isinstance(backend, FileDriftArchive)

    def test_create_sqlite_backend(self):
        """Test creating SQLite archive backend."""
        backend = get_drift_archive_backend(
            backend_type="sqlite",
            db_path=Path("/tmp/test.db")
        )

        assert isinstance(backend, SQLiteDriftArchive)

    def test_invalid_backend_type_raises_error(self):
        """Test that invalid backend type raises error."""
        with pytest.raises(ValueError):
            get_drift_archive_backend(backend_type="invalid")
```

### **Acceptance Criteria**

✅ **Functional Requirements**:
- [ ] `DriftArchiveBackend` protocol defined
- [ ] `FileDriftArchive` class (JSON lines storage)
- [ ] `SQLiteDriftArchive` class (indexed database storage)
- [ ] `DriftDetector` modified to support archival
- [ ] `reset()` method archives before clearing
- [ ] `query_archived_snapshots()` method
- [ ] Factory function `get_drift_archive_backend()`
- [ ] Configurable archive enablement (`archive_on_reset` flag)

✅ **Testing Requirements**:
- [ ] File archive tests (4+ tests)
- [ ] SQLite archive tests (3+ tests)
- [ ] DriftDetector integration tests (4+ tests)
- [ ] Factory function tests (3 tests)
- [ ] Test archive failure handling (doesn't block reset)
- [ ] Test query filters (time range, layer, drift score)

✅ **Documentation**:
- [ ] Docstrings for all classes and methods
- [ ] Example usage in module docstring
- [ ] Configuration guide (file vs SQLite backends)
- [ ] Compliance/audit trail notes
- [ ] TODO comment removed

✅ **Compliance Requirements**:
- [ ] Immutable archives (no modification after write)
- [ ] Timestamped entries
- [ ] Queryable for audit trails
- [ ] GDPR-compatible (can export/delete archived data)

### **Configuration**

```python
# config/drift_archival.py

import os
from pathlib import Path
from core.consciousness.drift_detector import get_drift_archive_backend

# Archive backend configuration
DRIFT_ARCHIVE_ENABLED = os.getenv("DRIFT_ARCHIVE_ENABLED", "1") == "1"
DRIFT_ARCHIVE_BACKEND = os.getenv("DRIFT_ARCHIVE_BACKEND", "file")  # "file" or "sqlite"

# File-based archive settings
DRIFT_ARCHIVE_DIR = Path(os.getenv("DRIFT_ARCHIVE_DIR", "data/drift_archives"))

# SQLite archive settings
DRIFT_ARCHIVE_DB = Path(os.getenv("DRIFT_ARCHIVE_DB", "data/drift_archives.db"))

# Factory function for production use
def create_drift_detector():
    """Create DriftDetector with configured archival backend."""
    from core.consciousness.drift_detector import DriftDetector

    if not DRIFT_ARCHIVE_ENABLED:
        return DriftDetector(archive_on_reset=False)

    backend = get_drift_archive_backend(
        backend_type=DRIFT_ARCHIVE_BACKEND,
        archive_dir=DRIFT_ARCHIVE_DIR,
        db_path=DRIFT_ARCHIVE_DB
    )

    return DriftDetector(
        archive_backend=backend,
        archive_on_reset=True
    )
```

### **References**

- **Module**: `core/consciousness/drift_detector.py`
- **Guardian System**: `lukhas/governance/` (uses drift detection)
- **Audit Requirements**: `docs/governance/GUARDIAN_EXAMPLE.md`
- **Compliance**: Multi-jurisdiction requirements (GDPR, CCPA)

---

## 🎯 Prioritization & Selection Guide

**Recommended Order**:

1. **START HERE: Guardian Feedback Integration** (TODO #2)
   - Medium complexity, clear requirements
   - High business value (adaptive ethics)
   - Good for learning LUKHAS patterns
   - Estimated: 2-4 hours

2. **Drift Detector Archival** (TODO #3)
   - Medium complexity, well-scoped
   - Compliance/audit value
   - Standalone feature
   - Estimated: 2-3 hours

3. **Quantum Decision Superposition** (TODO #1)
   - High complexity, advanced feature
   - Requires understanding of decision systems
   - Large implementation
   - Estimated: 3-5 hours

**Selection Criteria**:
- Choose based on your interest in:
  - **Ethics/Governance**: TODO #2 (Guardian feedback)
  - **Data/Compliance**: TODO #3 (Archival persistence)
  - **Algorithms/AI**: TODO #1 (Quantum superposition)

---

## 📚 Additional Resources

### **LUKHAS Documentation**
- **Main Context**: `/Users/agi_dev/LOCAL-REPOS/Lukhas/lukhas_context.md`
- **Architecture Docs**: `/Users/agi_dev/LOCAL-REPOS/Lukhas/docs/architecture/`
- **Guardian Guide**: `/Users/agi_dev/LOCAL-REPOS/Lukhas/docs/governance/GUARDIAN_EXAMPLE.md`
- **Consciousness Docs**: `/Users/agi_dev/LOCAL-REPOS/Lukhas/docs/architecture/consciousness.md`

### **Testing Patterns**
```python
# Typical LUKHAS test structure
import pytest
from unittest.mock import MagicMock, patch

class TestMyFeature:

    @pytest.fixture
    def my_component(self):
        """Fixture for component under test."""
        return MyComponent(config={})

    def test_basic_functionality(self, my_component):
        """Test description."""
        result = my_component.do_something()
        assert result is not None

    def test_edge_case(self, my_component):
        """Test edge case handling."""
        with pytest.raises(ValueError):
            my_component.do_invalid_thing()

    @pytest.mark.integration
    def test_integration_with_guardian(self, my_component):
        """Integration test with Guardian system."""
        # Integration test code
        pass
```

### **Logging Patterns**
```python
import logging

logger = logging.getLogger(__name__)

# Structured logging with extra context
logger.info(
    "Event description",
    extra={
        "component": "quantum_decision",
        "decision_id": decision_id,
        "confidence": confidence
    }
)

# Use ΛTAG for Lambda markers
logger.debug("# ΛTAG: quantum_collapse -- decision collapsed to strategy")
```

### **Import Patterns**
```python
# Good (respects lane boundaries)
from core.consciousness.bridge import DecisionMakingBridge  # core/ → core/
from matriz.core.nodes import Node  # core/ → matriz/

# Bad (violates lane boundaries)
from lukhas.api.features import FeatureFlagsService  # core/ cannot import lukhas/
from candidate.quantum.superposition import QuantumState  # lukhas/ cannot import candidate/
```

---

## TODO #4: ML-Based Pattern Prediction for Symbolic Anomaly Detection

**File**: `core/symbolic/symbolic_anomaly_explorer.py`
**Line**: 55
**Complexity**: High
**Estimated Effort**: 4-6 hours
**Owner**: consciousness-team / dream-team

### **Context**

The Symbolic Anomaly Explorer is a Jules-13 analysis engine that detects irregularities in dream sessions. It currently performs reactive analysis - detecting anomalies after they occur. The TODO requests adding **ML-based pattern prediction** for proactive anomaly detection.

**Current System Capabilities**:
- Multi-session symbolic pattern detection with temporal correlation
- Emotional volatility tracking across dream sequences
- Recursive loop identification with pattern classification
- Symbolic conflict analysis between competing narratives
- Drift score integration for stability assessment

**Anomaly Types Detected**:
- Symbolic Conflict: Competing motifs creating narrative tension
- Recursive Loops: Patterns that trap consciousness in cycles
- Emotional Dissonance: Affect misalignment with symbolic content
- Motif Mutation: Unexpected transformation of stable symbols
- Drift Acceleration: Rapid symbolic instability patterns

**Current TODO**:
```python
# Line 55 in core/symbolic/symbolic_anomaly_explorer.py
TODO: Add ML-based pattern prediction for proactive anomaly detection
```

### **Technical Requirements**

**Goal**: Implement ML-based time series forecasting to predict future anomalies before they manifest, enabling proactive intervention.

**Machine Learning Approach**:
1. **Feature Engineering**: Extract temporal features from dream session history
2. **Time Series Forecasting**: Use LSTM/GRU or Prophet for sequence prediction
3. **Anomaly Probability**: Predict likelihood of each anomaly type in next N sessions
4. **Confidence Scoring**: Provide uncertainty estimates for predictions
5. **Incremental Learning**: Update model as new dream sessions occur

**Implementation Approach**:

```python
# Add to core/symbolic/symbolic_anomaly_explorer.py

from typing import List, Tuple, Dict, Optional
import numpy as np
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from collections import deque

# Optional ML dependencies (graceful degradation if not available)
try:
    from sklearn.ensemble import RandomForestClassifier, IsolationForest
    from sklearn.preprocessing import StandardScaler
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

try:
    # Prophet for time series forecasting
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False


@dataclass
class AnomalyPrediction:
    """Prediction of future anomaly occurrence."""
    anomaly_type: AnomalyType
    probability: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0 (uncertainty measure)
    time_horizon: int  # Sessions ahead (1-10)
    contributing_features: Dict[str, float]
    predicted_severity: AnomalySeverity
    recommended_action: Optional[str] = None


@dataclass
class PredictionFeatures:
    """Features extracted from dream session history for ML prediction."""

    # Temporal features
    session_count: int
    time_span_hours: float
    avg_session_duration: float

    # Symbolic features
    unique_symbols_count: int
    symbol_repetition_rate: float
    motif_stability_score: float

    # Emotional features
    avg_valence: float
    avg_arousal: float
    emotional_volatility: float

    # Drift features
    avg_drift_score: float
    drift_acceleration: float
    max_drift_spike: float

    # Anomaly history features
    recent_conflict_count: int
    recent_loop_count: int
    recent_dissonance_count: int
    recent_mutation_count: int

    # Temporal patterns
    session_interval_variance: float
    time_of_day_pattern: float  # 0-23 hour average


class MLAnomalyPredictor:
    """
    Machine Learning-based predictor for symbolic anomalies.

    Uses ensemble of classifiers to predict anomaly occurrence:
    - Random Forest for anomaly type classification
    - Isolation Forest for general anomaly detection
    - Prophet (optional) for time series forecasting
    """

    def __init__(
        self,
        *,
        history_window: int = 50,
        prediction_horizon: int = 5,
        confidence_threshold: float = 0.6
    ):
        """
        Initialize ML predictor.

        Args:
            history_window: Number of sessions to use for training
            prediction_horizon: How many sessions ahead to predict
            confidence_threshold: Minimum confidence for predictions
        """
        if not ML_AVAILABLE:
            raise ImportError(
                "ML dependencies not available. Install: pip install scikit-learn"
            )

        self.history_window = history_window
        self.prediction_horizon = prediction_horizon
        self.confidence_threshold = confidence_threshold

        # Models
        self._anomaly_classifier = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self._isolation_forest = IsolationForest(
            contamination=0.1,
            random_state=42
        )
        self._scaler = StandardScaler()

        # Training data
        self._feature_history: deque = deque(maxlen=history_window)
        self._anomaly_history: deque = deque(maxlen=history_window)

        self._is_trained = False
        self._logger = logger

    def extract_features(
        self,
        session_history: List[Dict[str, Any]],
        anomaly_history: List[Dict[str, Any]]
    ) -> PredictionFeatures:
        """
        Extract ML features from session and anomaly history.

        Args:
            session_history: List of dream session summaries
            anomaly_history: List of detected anomalies

        Returns:
            PredictionFeatures for ML model
        """
        if not session_history:
            raise ValueError("Cannot extract features from empty history")

        # Temporal features
        session_count = len(session_history)

        timestamps = [
            datetime.fromisoformat(s["timestamp"])
            for s in session_history if "timestamp" in s
        ]
        time_span_hours = (
            (max(timestamps) - min(timestamps)).total_seconds() / 3600
            if len(timestamps) > 1 else 0
        )

        avg_session_duration = np.mean([
            s.get("duration_seconds", 0) for s in session_history
        ])

        # Symbolic features
        all_symbols = []
        for session in session_history:
            all_symbols.extend(session.get("symbols", []))

        unique_symbols_count = len(set(all_symbols))
        symbol_repetition_rate = (
            1 - (unique_symbols_count / len(all_symbols))
            if all_symbols else 0
        )

        # Motif stability (how consistent are symbols across sessions)
        from collections import Counter
        symbol_counts = Counter(all_symbols)
        motif_stability_score = (
            max(symbol_counts.values()) / len(all_symbols)
            if all_symbols else 0
        )

        # Emotional features
        valences = [s.get("valence", 0) for s in session_history]
        arousals = [s.get("arousal", 0) for s in session_history]

        avg_valence = np.mean(valences) if valences else 0
        avg_arousal = np.mean(arousals) if arousals else 0
        emotional_volatility = np.std(valences) if valences else 0

        # Drift features
        drift_scores = [s.get("drift_score", 0) for s in session_history]
        avg_drift_score = np.mean(drift_scores) if drift_scores else 0
        max_drift_spike = max(drift_scores) if drift_scores else 0

        # Drift acceleration (derivative)
        drift_acceleration = 0
        if len(drift_scores) > 1:
            drift_deltas = np.diff(drift_scores)
            drift_acceleration = float(np.mean(drift_deltas))

        # Anomaly history features
        recent_anomalies = anomaly_history[-10:] if anomaly_history else []
        anomaly_types = [a.get("type") for a in recent_anomalies]

        recent_conflict_count = anomaly_types.count("symbolic_conflict")
        recent_loop_count = anomaly_types.count("recursive_loop")
        recent_dissonance_count = anomaly_types.count("emotional_dissonance")
        recent_mutation_count = anomaly_types.count("motif_mutation")

        # Temporal patterns
        if len(timestamps) > 1:
            intervals = [
                (timestamps[i+1] - timestamps[i]).total_seconds()
                for i in range(len(timestamps) - 1)
            ]
            session_interval_variance = float(np.std(intervals))
        else:
            session_interval_variance = 0

        time_of_day_pattern = (
            np.mean([t.hour for t in timestamps])
            if timestamps else 12
        )

        return PredictionFeatures(
            session_count=session_count,
            time_span_hours=time_span_hours,
            avg_session_duration=avg_session_duration,
            unique_symbols_count=unique_symbols_count,
            symbol_repetition_rate=symbol_repetition_rate,
            motif_stability_score=motif_stability_score,
            avg_valence=avg_valence,
            avg_arousal=avg_arousal,
            emotional_volatility=emotional_volatility,
            avg_drift_score=avg_drift_score,
            drift_acceleration=drift_acceleration,
            max_drift_spike=max_drift_spike,
            recent_conflict_count=recent_conflict_count,
            recent_loop_count=recent_loop_count,
            recent_dissonance_count=recent_dissonance_count,
            recent_mutation_count=recent_mutation_count,
            session_interval_variance=session_interval_variance,
            time_of_day_pattern=time_of_day_pattern
        )

    def _features_to_array(self, features: PredictionFeatures) -> np.ndarray:
        """Convert PredictionFeatures to numpy array for ML model."""
        return np.array([
            features.session_count,
            features.time_span_hours,
            features.avg_session_duration,
            features.unique_symbols_count,
            features.symbol_repetition_rate,
            features.motif_stability_score,
            features.avg_valence,
            features.avg_arousal,
            features.emotional_volatility,
            features.avg_drift_score,
            features.drift_acceleration,
            features.max_drift_spike,
            features.recent_conflict_count,
            features.recent_loop_count,
            features.recent_dissonance_count,
            features.recent_mutation_count,
            features.session_interval_variance,
            features.time_of_day_pattern
        ])

    def update_history(
        self,
        features: PredictionFeatures,
        anomalies: List[AnomalyType]
    ) -> None:
        """
        Update prediction history with new session data.

        Args:
            features: Extracted features from latest sessions
            anomalies: Anomalies detected in latest session
        """
        self._feature_history.append(features)
        self._anomaly_history.append(anomalies)

        # Retrain if we have enough data
        if len(self._feature_history) >= 20:
            self._train_models()

    def _train_models(self) -> None:
        """Train ML models on accumulated history."""
        if len(self._feature_history) < 20:
            self._logger.warning("Insufficient data for training (need 20+ samples)")
            return

        # Prepare training data
        X = np.array([
            self._features_to_array(f) for f in self._feature_history
        ])

        # Binary labels: 1 if any anomaly occurred, 0 otherwise
        y_binary = np.array([
            1 if anomalies else 0
            for anomalies in self._anomaly_history
        ])

        # Scale features
        X_scaled = self._scaler.fit_transform(X)

        # Train Isolation Forest (unsupervised anomaly detection)
        self._isolation_forest.fit(X_scaled)

        # Train Random Forest Classifier (if we have positive examples)
        if y_binary.sum() > 0:
            self._anomaly_classifier.fit(X_scaled, y_binary)
            self._is_trained = True

        self._logger.info(
            "ML models trained",
            extra={
                "samples": len(X),
                "anomaly_rate": float(y_binary.mean())
            }
        )

    def predict_anomalies(
        self,
        current_features: PredictionFeatures,
        time_horizon: int = 5
    ) -> List[AnomalyPrediction]:
        """
        Predict anomalies for upcoming sessions.

        Args:
            current_features: Current feature state
            time_horizon: Number of sessions to predict ahead

        Returns:
            List of anomaly predictions with probabilities
        """
        if not self._is_trained:
            self._logger.warning("Predictor not trained yet, returning empty predictions")
            return []

        predictions = []

        # Convert features to array
        X = self._features_to_array(current_features).reshape(1, -1)
        X_scaled = self._scaler.transform(X)

        # Get probability from classifier
        if hasattr(self._anomaly_classifier, "predict_proba"):
            proba = self._anomaly_classifier.predict_proba(X_scaled)[0]
            anomaly_prob = proba[1] if len(proba) > 1 else 0
        else:
            anomaly_prob = 0.5

        # Get anomaly score from Isolation Forest
        iso_score = self._isolation_forest.score_samples(X_scaled)[0]
        # Convert to probability (lower score = more anomalous)
        iso_prob = 1 / (1 + np.exp(iso_score))  # Sigmoid transformation

        # Combine probabilities
        combined_prob = (anomaly_prob + iso_prob) / 2

        # Feature importance (which features contribute most)
        feature_importance = {}
        if hasattr(self._anomaly_classifier, "feature_importances_"):
            feature_names = [
                "session_count", "time_span_hours", "avg_session_duration",
                "unique_symbols_count", "symbol_repetition_rate", "motif_stability_score",
                "avg_valence", "avg_arousal", "emotional_volatility",
                "avg_drift_score", "drift_acceleration", "max_drift_spike",
                "recent_conflict_count", "recent_loop_count", "recent_dissonance_count",
                "recent_mutation_count", "session_interval_variance", "time_of_day_pattern"
            ]
            for name, importance in zip(feature_names, self._anomaly_classifier.feature_importances_):
                if importance > 0.05:  # Only include significant features
                    feature_importance[name] = float(importance)

        # Predict specific anomaly types based on feature patterns
        anomaly_type_predictions = self._predict_anomaly_types(current_features, combined_prob)

        for anomaly_type, type_prob in anomaly_type_predictions:
            if type_prob >= self.confidence_threshold:
                # Determine severity based on probability
                if type_prob >= 0.8:
                    severity = AnomalySeverity.CRITICAL
                elif type_prob >= 0.6:
                    severity = AnomalySeverity.HIGH
                elif type_prob >= 0.4:
                    severity = AnomalySeverity.MEDIUM
                else:
                    severity = AnomalySeverity.LOW

                # Generate recommendation
                recommendation = self._generate_recommendation(anomaly_type, type_prob)

                predictions.append(AnomalyPrediction(
                    anomaly_type=anomaly_type,
                    probability=type_prob,
                    confidence=combined_prob,
                    time_horizon=time_horizon,
                    contributing_features=feature_importance,
                    predicted_severity=severity,
                    recommended_action=recommendation
                ))

        return sorted(predictions, key=lambda p: p.probability, reverse=True)

    def _predict_anomaly_types(
        self,
        features: PredictionFeatures,
        base_prob: float
    ) -> List[Tuple[AnomalyType, float]]:
        """
        Predict specific anomaly types based on feature patterns.

        Uses heuristics to map features to anomaly types.
        """
        type_probs = []

        # Symbolic Conflict: High symbol repetition + high volatility
        conflict_score = (
            features.symbol_repetition_rate * 0.4 +
            features.emotional_volatility * 0.3 +
            (features.recent_conflict_count / 10) * 0.3
        )
        type_probs.append((AnomalyType.SYMBOLIC_CONFLICT, conflict_score * base_prob))

        # Recursive Loop: Low motif stability + high recent loops
        loop_score = (
            (1 - features.motif_stability_score) * 0.5 +
            (features.recent_loop_count / 10) * 0.5
        )
        type_probs.append((AnomalyType.RECURSIVE_LOOP, loop_score * base_prob))

        # Emotional Dissonance: High emotional volatility
        dissonance_score = (
            features.emotional_volatility * 0.6 +
            (features.recent_dissonance_count / 10) * 0.4
        )
        type_probs.append((AnomalyType.EMOTIONAL_DISSONANCE, dissonance_score * base_prob))

        # Motif Mutation: High recent mutations + low stability
        mutation_score = (
            (features.recent_mutation_count / 10) * 0.5 +
            (1 - features.motif_stability_score) * 0.5
        )
        type_probs.append((AnomalyType.MOTIF_MUTATION, mutation_score * base_prob))

        # Drift Acceleration: High drift acceleration
        drift_score = min(abs(features.drift_acceleration) / 0.5, 1.0)
        type_probs.append((AnomalyType.DRIFT_ACCELERATION, drift_score * base_prob))

        return type_probs

    def _generate_recommendation(
        self,
        anomaly_type: AnomalyType,
        probability: float
    ) -> str:
        """Generate actionable recommendation for predicted anomaly."""
        recommendations = {
            AnomalyType.SYMBOLIC_CONFLICT: "Consider symbolic integration exercises or motif reconciliation",
            AnomalyType.RECURSIVE_LOOP: "Implement loop-breaking interventions or pattern interrupts",
            AnomalyType.EMOTIONAL_DISSONANCE: "Schedule emotional processing or affect regulation session",
            AnomalyType.MOTIF_MUTATION: "Monitor symbol stability and consider symbolic anchoring",
            AnomalyType.DRIFT_ACCELERATION: "Increase drift monitoring frequency and consider stabilization"
        }

        base_rec = recommendations.get(
            anomaly_type,
            "Monitor closely and prepare intervention protocols"
        )

        if probability >= 0.8:
            return f"URGENT: {base_rec}"
        elif probability >= 0.6:
            return f"RECOMMENDED: {base_rec}"
        else:
            return f"SUGGESTED: {base_rec}"

    def get_model_stats(self) -> Dict[str, Any]:
        """Get statistics about predictor state and performance."""
        return {
            "is_trained": self._is_trained,
            "training_samples": len(self._feature_history),
            "history_window": self.history_window,
            "prediction_horizon": self.prediction_horizon,
            "confidence_threshold": self.confidence_threshold,
            "ml_available": ML_AVAILABLE,
            "prophet_available": PROPHET_AVAILABLE
        }


# Integration into SymbolicAnomalyExplorer class
# Add this method to the existing class:

def __init__(
    self,
    *,
    enable_ml_prediction: bool = True,
    prediction_horizon: int = 5
):
    """
    Initialize Symbolic Anomaly Explorer with optional ML prediction.

    Args:
        enable_ml_prediction: Enable ML-based anomaly prediction
        prediction_horizon: Sessions ahead to predict
    """
    # ... existing initialization ...

    # ML Predictor
    self._enable_ml_prediction = enable_ml_prediction and ML_AVAILABLE
    if self._enable_ml_prediction:
        try:
            self._ml_predictor = MLAnomalyPredictor(
                prediction_horizon=prediction_horizon
            )
        except ImportError:
            logger.warning("ML prediction requested but dependencies not available")
            self._enable_ml_prediction = False
            self._ml_predictor = None
    else:
        self._ml_predictor = None


def predict_future_anomalies(
    self,
    session_history: List[Dict[str, Any]],
    anomaly_history: List[Dict[str, Any]],
    time_horizon: int = 5
) -> List[AnomalyPrediction]:
    """
    Predict future anomalies using ML models.

    Args:
        session_history: Historical dream session data
        anomaly_history: Historical anomaly detections
        time_horizon: How many sessions ahead to predict

    Returns:
        List of predicted anomalies with probabilities
    """
    if not self._enable_ml_prediction or not self._ml_predictor:
        logger.warning("ML prediction not enabled or available")
        return []

    # Extract features from current state
    features = self._ml_predictor.extract_features(
        session_history,
        anomaly_history
    )

    # Update predictor with latest data
    recent_anomalies = [
        a.get("type") for a in anomaly_history[-1:]
    ] if anomaly_history else []

    self._ml_predictor.update_history(features, recent_anomalies)

    # Get predictions
    predictions = self._ml_predictor.predict_anomalies(
        features,
        time_horizon=time_horizon
    )

    logger.info(
        "ML anomaly predictions generated",
        extra={
            "prediction_count": len(predictions),
            "time_horizon": time_horizon,
            "max_probability": max([p.probability for p in predictions]) if predictions else 0
        }
    )

    return predictions
```

### **Testing Requirements**

Create tests in `tests/unit/core/symbolic/test_ml_anomaly_prediction.py`:

```python
import pytest
import numpy as np
from datetime import datetime, timezone, timedelta
from core.symbolic.symbolic_anomaly_explorer import (
    MLAnomalyPredictor,
    PredictionFeatures,
    AnomalyType,
    AnomalySeverity,
    ML_AVAILABLE
)

pytestmark = pytest.mark.skipif(
    not ML_AVAILABLE,
    reason="ML dependencies not available"
)


class TestFeatureExtraction:

    def test_extract_basic_features(self):
        """Test feature extraction from session history."""
        predictor = MLAnomalyPredictor()

        session_history = [
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "duration_seconds": 300,
                "symbols": ["tree", "water", "mountain"],
                "valence": 0.5,
                "arousal": 0.6,
                "drift_score": 0.3
            }
        ]

        features = predictor.extract_features(session_history, [])

        assert features.session_count == 1
        assert features.unique_symbols_count == 3
        assert features.avg_valence == 0.5
        assert features.avg_arousal == 0.6

    def test_symbol_repetition_calculation(self):
        """Test symbol repetition rate calculation."""
        predictor = MLAnomalyPredictor()

        session_history = [
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "symbols": ["tree", "tree", "water", "tree"],  # 3 tree, 1 water
                "valence": 0,
                "arousal": 0,
                "drift_score": 0
            }
        ]

        features = predictor.extract_features(session_history, [])

        # 4 symbols, 2 unique -> repetition = 1 - (2/4) = 0.5
        assert features.symbol_repetition_rate == 0.5

    def test_drift_acceleration_calculation(self):
        """Test drift acceleration from multiple sessions."""
        predictor = MLAnomalyPredictor()

        session_history = [
            {
                "timestamp": (datetime.now(timezone.utc) - timedelta(hours=i)).isoformat(),
                "drift_score": 0.1 + i * 0.1,  # Increasing drift
                "symbols": ["test"],
                "valence": 0,
                "arousal": 0
            }
            for i in range(5)
        ]

        features = predictor.extract_features(session_history, [])

        # Drift acceleration should be positive (increasing)
        assert features.drift_acceleration > 0


class TestMLPredictor:

    @pytest.fixture
    def trained_predictor(self):
        """Create a predictor trained on synthetic data."""
        predictor = MLAnomalyPredictor(history_window=30)

        # Generate synthetic training data
        for i in range(25):
            features = PredictionFeatures(
                session_count=i,
                time_span_hours=i * 2.0,
                avg_session_duration=300,
                unique_symbols_count=5 + i % 3,
                symbol_repetition_rate=0.3 + (i % 10) * 0.05,
                motif_stability_score=0.7 - (i % 5) * 0.1,
                avg_valence=0.5,
                avg_arousal=0.5,
                emotional_volatility=0.1 + (i % 8) * 0.05,
                avg_drift_score=0.3 + (i % 7) * 0.05,
                drift_acceleration=0.02,
                max_drift_spike=0.5,
                recent_conflict_count=i % 3,
                recent_loop_count=i % 2,
                recent_dissonance_count=i % 4,
                recent_mutation_count=i % 2,
                session_interval_variance=100.0,
                time_of_day_pattern=12.0
            )

            # Anomalies occur when certain conditions met
            anomalies = []
            if i % 5 == 0:
                anomalies.append(AnomalyType.SYMBOLIC_CONFLICT)

            predictor.update_history(features, anomalies)

        return predictor

    def test_predictor_trains_with_sufficient_data(self, trained_predictor):
        """Test that predictor trains when it has enough data."""
        assert trained_predictor._is_trained

    def test_prediction_returns_probabilities(self, trained_predictor):
        """Test that predictions return valid probabilities."""
        features = PredictionFeatures(
            session_count=30,
            time_span_hours=60.0,
            avg_session_duration=300,
            unique_symbols_count=8,
            symbol_repetition_rate=0.4,
            motif_stability_score=0.6,
            avg_valence=0.5,
            avg_arousal=0.5,
            emotional_volatility=0.2,
            avg_drift_score=0.4,
            drift_acceleration=0.03,
            max_drift_spike=0.6,
            recent_conflict_count=2,
            recent_loop_count=1,
            recent_dissonance_count=0,
            recent_mutation_count=1,
            session_interval_variance=150.0,
            time_of_day_pattern=14.0
        )

        predictions = trained_predictor.predict_anomalies(features, time_horizon=5)

        # Should return at least one prediction
        assert len(predictions) > 0

        # All probabilities should be in [0, 1]
        for pred in predictions:
            assert 0 <= pred.probability <= 1
            assert 0 <= pred.confidence <= 1

    def test_high_conflict_features_predict_conflict(self, trained_predictor):
        """Test that high conflict features predict conflict anomaly."""
        features = PredictionFeatures(
            session_count=30,
            time_span_hours=60.0,
            avg_session_duration=300,
            unique_symbols_count=8,
            symbol_repetition_rate=0.9,  # Very high repetition
            motif_stability_score=0.3,
            avg_valence=0.5,
            avg_arousal=0.5,
            emotional_volatility=0.8,  # Very high volatility
            avg_drift_score=0.4,
            drift_acceleration=0.03,
            max_drift_spike=0.6,
            recent_conflict_count=5,  # Many recent conflicts
            recent_loop_count=0,
            recent_dissonance_count=0,
            recent_mutation_count=0,
            session_interval_variance=150.0,
            time_of_day_pattern=14.0
        )

        predictions = trained_predictor.predict_anomalies(features)

        # Should predict symbolic conflict
        conflict_preds = [
            p for p in predictions
            if p.anomaly_type == AnomalyType.SYMBOLIC_CONFLICT
        ]
        assert len(conflict_preds) > 0

    def test_recommendations_generated(self, trained_predictor):
        """Test that predictions include actionable recommendations."""
        features = PredictionFeatures(
            session_count=30, time_span_hours=60.0, avg_session_duration=300,
            unique_symbols_count=8, symbol_repetition_rate=0.4,
            motif_stability_score=0.6, avg_valence=0.5, avg_arousal=0.5,
            emotional_volatility=0.2, avg_drift_score=0.4,
            drift_acceleration=0.03, max_drift_spike=0.6,
            recent_conflict_count=2, recent_loop_count=1,
            recent_dissonance_count=0, recent_mutation_count=1,
            session_interval_variance=150.0, time_of_day_pattern=14.0
        )

        predictions = trained_predictor.predict_anomalies(features)

        for pred in predictions:
            assert pred.recommended_action is not None
            assert len(pred.recommended_action) > 0

    def test_severity_scales_with_probability(self, trained_predictor):
        """Test that predicted severity scales with probability."""
        # High probability should have higher severity
        # This is tested implicitly through the severity assignment logic
        pass

    def test_model_stats(self, trained_predictor):
        """Test that model statistics are accessible."""
        stats = trained_predictor.get_model_stats()

        assert stats["is_trained"] is True
        assert stats["training_samples"] >= 20
        assert "ml_available" in stats


class TestIntegrationWithSymbolicAnomalyExplorer:

    def test_prediction_integration(self):
        """Test integration with SymbolicAnomalyExplorer."""
        from core.symbolic.symbolic_anomaly_explorer import SymbolicAnomalyExplorer

        explorer = SymbolicAnomalyExplorer(
            enable_ml_prediction=True,
            prediction_horizon=5
        )

        # Generate synthetic session history
        session_history = [
            {
                "timestamp": (datetime.now(timezone.utc) - timedelta(hours=i)).isoformat(),
                "duration_seconds": 300,
                "symbols": ["symbol" + str(j) for j in range(5)],
                "valence": 0.5,
                "arousal": 0.5,
                "drift_score": 0.3 + i * 0.01
            }
            for i in range(30)
        ]

        anomaly_history = []

        predictions = explorer.predict_future_anomalies(
            session_history,
            anomaly_history,
            time_horizon=5
        )

        # Should return predictions (may be empty if not enough training data)
        assert isinstance(predictions, list)
```

### **Acceptance Criteria**

✅ **Functional Requirements**:
- [ ] `PredictionFeatures` dataclass with 18+ features
- [ ] `AnomalyPrediction` dataclass with probability, confidence, recommendations
- [ ] `MLAnomalyPredictor` class with all methods
- [ ] Feature extraction from session history
- [ ] Random Forest classifier for anomaly detection
- [ ] Isolation Forest for unsupervised anomaly detection
- [ ] Feature scaling with StandardScaler
- [ ] Anomaly type prediction based on feature patterns
- [ ] Severity prediction (CRITICAL/HIGH/MEDIUM/LOW)
- [ ] Actionable recommendation generation
- [ ] Incremental learning (update as new data arrives)
- [ ] Integration method in `SymbolicAnomalyExplorer`

✅ **Testing Requirements**:
- [ ] Feature extraction tests (3+ tests)
- [ ] ML predictor tests (6+ tests)
- [ ] Integration tests with SymbolicAnomalyExplorer
- [ ] Test prediction probabilities in valid range
- [ ] Test recommendations generation
- [ ] Test graceful degradation if ML not available

✅ **Documentation**:
- [ ] Docstrings for all classes and methods
- [ ] Feature descriptions
- [ ] ML approach explanation
- [ ] Example usage
- [ ] TODO comment removed

✅ **Dependencies**:
- [ ] Optional dependency handling (graceful degradation)
- [ ] Requirements: `scikit-learn>=1.0.0`
- [ ] Optional: `prophet>=1.0` for time series forecasting

### **Configuration**

```python
# config/ml_prediction.py

import os

# ML Prediction Configuration
ML_PREDICTION_ENABLED = os.getenv("ML_PREDICTION_ENABLED", "1") == "1"
PREDICTION_HORIZON = int(os.getenv("PREDICTION_HORIZON", "5"))
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.6"))
TRAINING_WINDOW = int(os.getenv("TRAINING_WINDOW", "50"))

# Feature to install ML dependencies
# pip install scikit-learn>=1.0.0
# pip install prophet>=1.0  # optional for time series
```

### **References**

- **Module**: `core/symbolic/symbolic_anomaly_explorer.py`
- **Dream System**: `candidate/consciousness/dream/`
- **Drift Detection**: `core/consciousness/drift_detector.py`
- **Documentation**: `docs/architecture/consciousness.md`

---

## TODO #5: Quantum Entanglement Modeling for Superpositions

**File**: `candidate/quantum/superposition_engine.py`
**Line**: 176
**Complexity**: High
**Estimated Effort**: 4-6 hours
**Owner**: quantum-team / consciousness-team

### **Context**

The `QuantumSuperpositionEngine` creates and manages quantum-inspired superposition states for the QI-AGI (Quantum-Inspired AGI) system. Currently supports single superposition states with interference patterns. The TODO requests extending with **entanglement modeling across multiple superpositions**.

**Current System**:
- Creates normalized superposition states with complex amplitudes
- Applies interference patterns based on context
- Supports measurement/collapse to single option
- Computes amplitudes with phase information

**Current TODO**:
```python
# Line 176 in candidate/quantum/superposition_engine.py
# TODO: Extend with entanglement modelling across multiple superpositions.
```

### **Technical Requirements**

**Goal**: Implement quantum-inspired entanglement between multiple superposition states, where measurement of one state affects probabilities in entangled states.

**Quantum Entanglement Concepts**:
1. **Entangled States**: Multiple superpositions linked by correlation
2. **Non-local Correlation**: Measuring one affects the other
3. **Bell States**: Maximally entangled states
4. **Partial Entanglement**: Correlation strength parameter (0 to 1)
5. **Entanglement Preservation**: Maintain correlations through operations

**Implementation Approach**:

```python
# Add to candidate/quantum/superposition_engine.py

from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import cmath

@dataclass
class EntanglementLink:
    """Represents entanglement between two superposition states."""
    state_id_1: str
    state_id_2: str
    correlation: float  # -1.0 to 1.0 (strength and type of correlation)
    entanglement_type: str  # "bell", "partial", "custom"
    created_at: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class EntanglementType(Enum):
    """Types of quantum entanglement patterns."""
    BELL_PHI_PLUS = "bell_phi_plus"  # Maximally entangled, positive correlation
    BELL_PHI_MINUS = "bell_phi_minus"  # Maximally entangled, negative correlation
    BELL_PSI_PLUS = "bell_psi_plus"
    BELL_PSI_MINUS = "bell_psi_minus"
    PARTIAL = "partial"  # Partial entanglement with custom correlation
    GHZ = "ghz"  # Greenberger-Horne-Zeilinger (3+ states)


@dataclass
class EntangledSuperpositionState:
    """Superposition state with entanglement tracking."""
    state_id: str
    options: list[dict[str, Any]]
    amplitudes: list[complex]
    metadata: dict[str, Any]
    entangled_with: Set[str] = field(default_factory=set)
    is_measured: bool = False
    measured_outcome: Optional[int] = None


class QuantumEntanglementManager:
    """
    Manages entanglement relationships between multiple superposition states.

    Implements quantum-inspired entanglement where measuring one superposition
    affects the probability distributions of entangled superpositions.
    """

    def __init__(self):
        """Initialize entanglement manager."""
        self._states: Dict[str, EntangledSuperpositionState] = {}
        self._entanglements: List[EntanglementLink] = []
        self._entanglement_graph: Dict[str, Set[str]] = {}
        self._logger = logging.getLogger(__name__)

    def register_state(
        self,
        state_id: str,
        state: SuperpositionState
    ) -> EntangledSuperpositionState:
        """
        Register a superposition state for entanglement tracking.

        Args:
            state_id: Unique identifier for this state
            state: SuperpositionState to register

        Returns:
            EntangledSuperpositionState with tracking
        """
        entangled_state = EntangledSuperpositionState(
            state_id=state_id,
            options=state.options,
            amplitudes=state.amplitudes,
            metadata=state.metadata
        )

        self._states[state_id] = entangled_state
        self._entanglement_graph[state_id] = set()

        self._logger.debug(f"Registered state {state_id} with {len(state.options)} options")

        return entangled_state

    def create_entanglement(
        self,
        state_id_1: str,
        state_id_2: str,
        entanglement_type: EntanglementType = EntanglementType.PARTIAL,
        correlation: float = 0.8
    ) -> EntanglementLink:
        """
        Create entanglement between two superposition states.

        Args:
            state_id_1: First state ID
            state_id_2: Second state ID
            entanglement_type: Type of entanglement pattern
            correlation: Correlation strength (-1.0 to 1.0)

        Returns:
            EntanglementLink describing the entanglement
        """
        if state_id_1 not in self._states or state_id_2 not in self._states:
            raise ValueError(f"Both states must be registered before entanglement")

        # Validate correlation
        correlation = max(-1.0, min(1.0, correlation))

        # Create entanglement link
        link = EntanglementLink(
            state_id_1=state_id_1,
            state_id_2=state_id_2,
            correlation=correlation,
            entanglement_type=entanglement_type.value,
            created_at=time.time()
        )

        self._entanglements.append(link)

        # Update entanglement graph
        self._entanglement_graph[state_id_1].add(state_id_2)
        self._entanglement_graph[state_id_2].add(state_id_1)

        # Update states
        self._states[state_id_1].entangled_with.add(state_id_2)
        self._states[state_id_2].entangled_with.add(state_id_1)

        # Apply entanglement to amplitudes
        self._apply_entanglement_pattern(state_id_1, state_id_2, entanglement_type, correlation)

        self._logger.info(
            f"Created {entanglement_type.value} entanglement between {state_id_1} and {state_id_2} "
            f"(correlation={correlation:.2f})"
        )

        return link

    def _apply_entanglement_pattern(
        self,
        state_id_1: str,
        state_id_2: str,
        entanglement_type: EntanglementType,
        correlation: float
    ) -> None:
        """
        Apply entanglement pattern to modify state amplitudes.

        Entanglement creates correlations in the probability distributions.
        """
        state1 = self._states[state_id_1]
        state2 = self._states[state_id_2]

        if entanglement_type in [EntanglementType.BELL_PHI_PLUS, EntanglementType.BELL_PHI_MINUS]:
            # Bell states: Maximally entangled states
            # Adjust amplitudes to create correlation
            n1 = len(state1.amplitudes)
            n2 = len(state2.amplitudes)

            # For Bell Phi+: Same outcomes have high correlation
            # For Bell Phi-: Opposite outcomes have high correlation
            sign = 1.0 if entanglement_type == EntanglementType.BELL_PHI_PLUS else -1.0

            # Modify phase relationships
            for i in range(min(n1, n2)):
                phase_shift = sign * np.pi / 4 * correlation
                state1.amplitudes[i] *= cmath.exp(1j * phase_shift)
                state2.amplitudes[i] *= cmath.exp(1j * phase_shift)

            # Renormalize
            self._normalize_state(state_id_1)
            self._normalize_state(state_id_2)

        elif entanglement_type == EntanglementType.PARTIAL:
            # Partial entanglement: Adjust phases based on correlation strength
            n = min(len(state1.amplitudes), len(state2.amplitudes))

            for i in range(n):
                # Create phase correlation
                phase_correlation = correlation * np.pi / 2
                state1.amplitudes[i] *= cmath.exp(1j * phase_correlation * i / n)
                state2.amplitudes[i] *= cmath.exp(1j * phase_correlation * i / n)

            self._normalize_state(state_id_1)
            self._normalize_state(state_id_2)

    def _normalize_state(self, state_id: str) -> None:
        """Normalize amplitudes of a state to ensure valid probability distribution."""
        state = self._states[state_id]
        amplitudes = np.array(state.amplitudes)
        norm = np.sqrt(np.sum(np.abs(amplitudes) ** 2))
        if norm > 0:
            state.amplitudes = list(amplitudes / norm)

    def measure_state(
        self,
        state_id: str
    ) -> Tuple[int, Any]:
        """
        Measure a superposition state, collapsing it to single outcome.

        If state is entangled, this affects probability distributions of
        entangled states.

        Args:
            state_id: ID of state to measure

        Returns:
            (outcome_index, outcome_value)
        """
        if state_id not in self._states:
            raise ValueError(f"State {state_id} not registered")

        state = self._states[state_id]

        if state.is_measured:
            self._logger.warning(f"State {state_id} already measured")
            return state.measured_outcome, state.options[state.measured_outcome]

        # Compute probabilities
        probabilities = np.abs(np.array(state.amplitudes)) ** 2
        probabilities /= probabilities.sum()  # Normalize

        # Measure (collapse)
        outcome_index = np.random.choice(len(state.options), p=probabilities)
        outcome_value = state.options[outcome_index]

        # Mark as measured
        state.is_measured = True
        state.measured_outcome = outcome_index

        self._logger.info(
            f"Measured state {state_id}: outcome {outcome_index} "
            f"(probability={probabilities[outcome_index]:.3f})"
        )

        # Propagate measurement to entangled states
        self._propagate_measurement(state_id, outcome_index)

        return outcome_index, outcome_value

    def _propagate_measurement(
        self,
        measured_state_id: str,
        measured_outcome: int
    ) -> None:
        """
        Propagate measurement to entangled states.

        When one state is measured, entangled states' probability
        distributions are updated based on correlation.
        """
        measured_state = self._states[measured_state_id]

        # Find entanglement links involving this state
        for link in self._entanglements:
            if link.state_id_1 == measured_state_id:
                partner_id = link.state_id_2
            elif link.state_id_2 == measured_state_id:
                partner_id = link.state_id_1
            else:
                continue  # Link doesn't involve measured state

            if partner_id not in self._states:
                continue

            partner_state = self._states[partner_id]

            if partner_state.is_measured:
                continue  # Already measured

            # Update partner state amplitudes based on correlation
            self._apply_measurement_correlation(
                partner_state,
                measured_outcome,
                link.correlation
            )

            self._logger.debug(
                f"Propagated measurement from {measured_state_id} to {partner_id} "
                f"(correlation={link.correlation:.2f})"
            )

    def _apply_measurement_correlation(
        self,
        partner_state: EntangledSuperpositionState,
        measured_outcome: int,
        correlation: float
    ) -> None:
        """
        Apply measurement correlation to update partner state amplitudes.

        Positive correlation: Increase probability of same outcome
        Negative correlation: Decrease probability of same outcome
        """
        n = len(partner_state.amplitudes)

        # Map measured outcome to partner state (may have different size)
        partner_outcome = min(measured_outcome, n - 1)

        # Modify amplitudes based on correlation
        for i in range(n):
            if correlation > 0:
                # Positive correlation: boost matching outcome
                if i == partner_outcome:
                    partner_state.amplitudes[i] *= (1 + abs(correlation))
                else:
                    partner_state.amplitudes[i] *= (1 - abs(correlation) * 0.5)
            else:
                # Negative correlation: suppress matching outcome
                if i == partner_outcome:
                    partner_state.amplitudes[i] *= (1 - abs(correlation) * 0.5)
                else:
                    partner_state.amplitudes[i] *= (1 + abs(correlation) * 0.3)

        # Renormalize
        amplitudes = np.array(partner_state.amplitudes)
        norm = np.sqrt(np.sum(np.abs(amplitudes) ** 2))
        if norm > 0:
            partner_state.amplitudes = list(amplitudes / norm)

    def get_entanglement_network(self) -> Dict[str, List[str]]:
        """
        Get the full entanglement network structure.

        Returns:
            Dict mapping state IDs to lists of entangled partner IDs
        """
        return {
            state_id: list(partners)
            for state_id, partners in self._entanglement_graph.items()
        }

    def compute_entanglement_entropy(self, state_id: str) -> float:
        """
        Compute von Neumann entropy of a state (measure of entanglement).

        Higher entropy indicates more entanglement/uncertainty.
        """
        if state_id not in self._states:
            raise ValueError(f"State {state_id} not registered")

        state = self._states[state_id]
        probabilities = np.abs(np.array(state.amplitudes)) ** 2

        # Remove zero probabilities
        probabilities = probabilities[probabilities > 1e-10]

        # Von Neumann entropy
        entropy = -np.sum(probabilities * np.log2(probabilities))

        return float(entropy)

    def get_correlation_matrix(self) -> np.ndarray:
        """
        Compute correlation matrix for all states.

        Returns:
            NxN matrix where [i,j] is correlation between states i and j
        """
        state_ids = list(self._states.keys())
        n = len(state_ids)

        matrix = np.zeros((n, n))

        for link in self._entanglements:
            try:
                i = state_ids.index(link.state_id_1)
                j = state_ids.index(link.state_id_2)
                matrix[i, j] = link.correlation
                matrix[j, i] = link.correlation  # Symmetric
            except ValueError:
                continue  # State not in current list

        # Diagonal is 1.0 (state perfectly correlated with itself)
        np.fill_diagonal(matrix, 1.0)

        return matrix

    def reset_all_measurements(self) -> None:
        """Reset all states to unmeasured (for re-measurement)."""
        for state in self._states.values():
            state.is_measured = False
            state.measured_outcome = None

        self._logger.info("Reset all state measurements")


# Integration into QuantumSuperpositionEngine
class QuantumSuperpositionEngine:
    """Create and manage quantum-inspired superposition states with entanglement."""

    def __init__(self, *, rng: Any | None = None, enable_entanglement: bool = True) -> None:
        self._rng = rng or random.Random()
        self._enable_entanglement = enable_entanglement

        if enable_entanglement:
            self._entanglement_manager = QuantumEntanglementManager()
        else:
            self._entanglement_manager = None

    def create_entangled_pair(
        self,
        options_1: Sequence[Mapping[str, Any]],
        options_2: Sequence[Mapping[str, Any]],
        context: Mapping[str, Any] | None = None,
        correlation: float = 0.8
    ) -> Tuple[EntangledSuperpositionState, EntangledSuperpositionState]:
        """
        Create a pair of entangled superposition states.

        Args:
            options_1: Options for first state
            options_2: Options for second state
            context: Optional context for interference
            correlation: Correlation strength (0 to 1)

        Returns:
            Tuple of two entangled superposition states
        """
        if not self._enable_entanglement:
            raise RuntimeError("Entanglement not enabled")

        # Create both states
        state1 = self.create_state(options_1, context)
        state2 = self.create_state(options_2, context)

        # Register with entanglement manager
        state_id_1 = f"state_{id(state1)}"
        state_id_2 = f"state_{id(state2)}"

        entangled_1 = self._entanglement_manager.register_state(state_id_1, state1)
        entangled_2 = self._entanglement_manager.register_state(state_id_2, state2)

        # Create entanglement
        self._entanglement_manager.create_entanglement(
            state_id_1,
            state_id_2,
            entanglement_type=EntanglementType.BELL_PHI_PLUS,
            correlation=correlation
        )

        return entangled_1, entangled_2

    def measure_entangled_state(
        self,
        state: EntangledSuperpositionState
    ) -> Tuple[int, Any]:
        """
        Measure an entangled state.

        This will affect all states entangled with this one.
        """
        if not self._enable_entanglement:
            raise RuntimeError("Entanglement not enabled")

        return self._entanglement_manager.measure_state(state.state_id)
```

### **Testing Requirements**

Create tests in `tests/unit/candidate/quantum/test_entanglement.py`:

```python
import pytest
import numpy as np
from candidate.quantum.superposition_engine import (
    QuantumSuperpositionEngine,
    QuantumEntanglementManager,
    EntanglementType,
    SuperpositionState
)


class TestQuantumEntanglement:

    @pytest.fixture
    def entanglement_manager(self):
        """Create entanglement manager."""
        return QuantumEntanglementManager()

    @pytest.fixture
    def sample_states(self, entanglement_manager):
        """Create sample states for testing."""
        state1 = SuperpositionState(
            options=[{"id": "A"}, {"id": "B"}],
            amplitudes=[1/np.sqrt(2), 1/np.sqrt(2)],
            metadata={}
        )
        state2 = SuperpositionState(
            options=[{"id": "X"}, {"id": "Y"}],
            amplitudes=[1/np.sqrt(2), 1/np.sqrt(2)],
            metadata={}
        )

        es1 = entanglement_manager.register_state("state1", state1)
        es2 = entanglement_manager.register_state("state2", state2)

        return es1, es2

    def test_register_state(self, entanglement_manager):
        """Test registering a state."""
        state = SuperpositionState(
            options=[{"id": "A"}],
            amplitudes=[1.0+0j],
            metadata={}
        )

        es = entanglement_manager.register_state("test_state", state)

        assert es.state_id == "test_state"
        assert len(es.options) == 1
        assert len(es.entangled_with) == 0

    def test_create_entanglement(self, entanglement_manager, sample_states):
        """Test creating entanglement between two states."""
        es1, es2 = sample_states

        link = entanglement_manager.create_entanglement(
            "state1",
            "state2",
            entanglement_type=EntanglementType.PARTIAL,
            correlation=0.8
        )

        assert link.correlation == 0.8
        assert "state2" in es1.entangled_with
        assert "state1" in es2.entangled_with

    def test_measurement_propagation(self, entanglement_manager, sample_states):
        """Test that measuring one state affects entangled states."""
        es1, es2 = sample_states

        # Create entanglement
        entanglement_manager.create_entanglement(
            "state1",
            "state2",
            entanglement_type=EntanglementType.BELL_PHI_PLUS,
            correlation=0.9
        )

        # Get initial probabilities of state2
        initial_probs_2 = np.abs(np.array(es2.amplitudes)) ** 2

        # Measure state1
        outcome1, _ = entanglement_manager.measure_state("state1")

        # State2 probabilities should have changed
        final_probs_2 = np.abs(np.array(es2.amplitudes)) ** 2

        # Due to positive correlation, same outcome should be more likely
        assert final_probs_2[outcome1] > initial_probs_2[outcome1]

    def test_positive_correlation(self, entanglement_manager, sample_states):
        """Test positive correlation favors same outcomes."""
        es1, es2 = sample_states

        entanglement_manager.create_entanglement(
            "state1",
            "state2",
            correlation=1.0  # Perfect positive correlation
        )

        # Measure state1 multiple times (reset between measurements)
        matches = 0
        trials = 100

        for _ in range(trials):
            entanglement_manager.reset_all_measurements()

            outcome1, _ = entanglement_manager.measure_state("state1")
            outcome2, _ = entanglement_manager.measure_state("state2")

            if outcome1 == outcome2:
                matches += 1

        # With positive correlation, should have more matches than random (50%)
        assert matches > trials * 0.6

    def test_negative_correlation(self, entanglement_manager, sample_states):
        """Test negative correlation favors opposite outcomes."""
        es1, es2 = sample_states

        entanglement_manager.create_entanglement(
            "state1",
            "state2",
            correlation=-1.0  # Perfect negative correlation
        )

        matches = 0
        trials = 100

        for _ in range(trials):
            entanglement_manager.reset_all_measurements()

            outcome1, _ = entanglement_manager.measure_state("state1")
            outcome2, _ = entanglement_manager.measure_state("state2")

            if outcome1 == outcome2:
                matches += 1

        # With negative correlation, should have fewer matches than random (50%)
        assert matches < trials * 0.4

    def test_entanglement_entropy(self, entanglement_manager, sample_states):
        """Test entropy calculation."""
        es1, _ = sample_states

        entropy = entanglement_manager.compute_entanglement_entropy("state1")

        # Equal superposition should have maximum entropy
        # For 2 options: max entropy = log2(2) = 1.0
        assert entropy == pytest.approx(1.0, abs=0.01)

    def test_correlation_matrix(self, entanglement_manager, sample_states):
        """Test correlation matrix generation."""
        es1, es2 = sample_states

        entanglement_manager.create_entanglement(
            "state1",
            "state2",
            correlation=0.7
        )

        matrix = entanglement_manager.get_correlation_matrix()

        assert matrix.shape == (2, 2)
        assert matrix[0, 0] == 1.0  # Self-correlation
        assert matrix[1, 1] == 1.0
        assert matrix[0, 1] == 0.7
        assert matrix[1, 0] == 0.7

    def test_entanglement_network(self, entanglement_manager):
        """Test entanglement network structure."""
        # Create 3 states
        for i in range(3):
            state = SuperpositionState(
                options=[{"id": str(i)}],
                amplitudes=[1.0+0j],
                metadata={}
            )
            entanglement_manager.register_state(f"state{i}", state)

        # Create entanglements: 0-1, 1-2 (chain)
        entanglement_manager.create_entanglement("state0", "state1")
        entanglement_manager.create_entanglement("state1", "state2")

        network = entanglement_manager.get_entanglement_network()

        assert "state1" in network["state0"]
        assert "state0" in network["state1"]
        assert "state2" in network["state1"]
        assert "state1" in network["state2"]


class TestSuperpositionEngineWithEntanglement:

    def test_create_entangled_pair(self):
        """Test creating entangled pair of states."""
        engine = QuantumSuperpositionEngine(enable_entanglement=True)

        options1 = [{"action": "left"}, {"action": "right"}]
        options2 = [{"choice": "A"}, {"choice": "B"}]

        state1, state2 = engine.create_entangled_pair(
            options1,
            options2,
            correlation=0.8
        )

        assert state1.state_id != state2.state_id
        assert state2.state_id in state1.entangled_with
        assert state1.state_id in state2.entangled_with

    def test_measure_entangled_state(self):
        """Test measuring entangled states."""
        engine = QuantumSuperpositionEngine(enable_entanglement=True)

        options = [{"id": str(i)} for i in range(3)]
        state1, state2 = engine.create_entangled_pair(options, options, correlation=0.9)

        outcome1, value1 = engine.measure_entangled_state(state1)

        assert 0 <= outcome1 < 3
        assert value1 in options
        assert state1.is_measured
```

### **Acceptance Criteria**

✅ **Functional Requirements**:
- [ ] `EntanglementLink` dataclass
- [ ] `EntanglementType` enum with Bell states
- [ ] `EntangledSuperpositionState` class
- [ ] `QuantumEntanglementManager` class with all methods
- [ ] State registration and tracking
- [ ] Entanglement creation (partial, Bell states)
- [ ] Measurement propagation to entangled states
- [ ] Correlation-based amplitude updates
- [ ] Entanglement entropy calculation
- [ ] Correlation matrix generation
- [ ] Network structure retrieval
- [ ] Integration into `QuantumSuperpositionEngine`

✅ **Testing Requirements**:
- [ ] Entanglement manager tests (8+ tests)
- [ ] Integration tests with engine (2+ tests)
- [ ] Test positive correlation favors same outcomes
- [ ] Test negative correlation favors opposite outcomes
- [ ] Test measurement propagation
- [ ] Test entropy calculation
- [ ] Test correlation matrix

✅ **Documentation**:
- [ ] Docstrings with quantum concepts explained
- [ ] Example usage for entangled pairs
- [ ] Correlation parameter guide
- [ ] TODO comment removed

### **References**

- **Module**: `candidate/quantum/superposition_engine.py`
- **Quantum Systems**: `candidate/quantum/`
- **Decision Systems**: `core/consciousness/bridge.py` (uses superpositions)
- **Documentation**: Quantum-inspired algorithms guide

---

## TODO #6: Distributed GLYPH Registry Synchronization

**File**: `core/symbolic/glyph_specialist.py`
**Line**: 97
**Complexity**: Medium-High
**Estimated Effort**: 3-5 hours
**Owner**: symbolic-team / distributed-systems-team

### **Context**

The `GlyphSpecialist` manages symbolic glyphs with drift thresholds for consensus. Currently uses local drift threshold storage. The TODO requests synchronizing thresholds to a **distributed GLYPH registry** for multi-instance coordination.

**Current Implementation**:
```python
def update_threshold(self, new_threshold: float) -> None:
    """Update drift threshold used for consensus."""
    if new_threshold <= 0:
        raise ValueError("new_threshold must be positive")
    self.drift_threshold = new_threshold
    self._logger.info(
        "# ΛTAG: glyph_threshold_update -- updated drift threshold",
        extra={"drift_threshold": new_threshold},
    )
    # TODO: sync threshold to distributed GLYPH registry once service hook lands.
```

**Current TODO**:
```python
# Line 97 in core/symbolic/glyph_specialist.py
# TODO: sync threshold to distributed GLYPH registry once service hook lands.
```

### **Technical Requirements**

**Goal**: Implement distributed registry synchronization for GLYPH thresholds, enabling multi-instance consensus and coordination.

**Distributed Registry Design**:
1. **Registry Backend**: Support Redis, etcd, or in-memory backends
2. **Threshold Publishing**: Publish threshold updates to registry
3. **Threshold Subscription**: Subscribe to updates from other instances
4. **Conflict Resolution**: Handle concurrent updates with timestamps
5. **Eventual Consistency**: Guarantee convergence across instances
6. **Health Monitoring**: Detect and handle registry failures

**Implementation Approach**:

```python
# Add to core/symbolic/glyph_specialist.py

from typing import Protocol, Optional, Dict, Callable
from abc import ABC, abstractmethod
from datetime import datetime, timezone
import json
import threading
import time

class GlyphRegistryBackend(Protocol):
    """Protocol for distributed GLYPH registry backends."""

    def publish_threshold(self, glyph_id: str, threshold: float, metadata: Dict[str, Any]) -> None:
        """Publish threshold update to registry."""
        ...

    def get_threshold(self, glyph_id: str) -> Optional[Dict[str, Any]]:
        """Get current threshold from registry."""
        ...

    def subscribe_to_updates(
        self,
        glyph_id: str,
        callback: Callable[[float, Dict[str, Any]], None]
    ) -> None:
        """Subscribe to threshold updates."""
        ...

    def list_all_glyphs(self) -> Dict[str, Dict[str, Any]]:
        """List all glyphs in registry."""
        ...


class RedisGlyphRegistry:
    """Redis-based distributed GLYPH registry."""

    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        """
        Initialize Redis registry.

        Args:
            redis_url: Redis connection URL
        """
        try:
            import redis
        except ImportError:
            raise ImportError("Redis backend requires redis package: pip install redis")

        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self._subscribers: Dict[str, Callable] = {}
        self._pubsub_thread = None
        self._logger = logging.getLogger(__name__)

    def publish_threshold(
        self,
        glyph_id: str,
        threshold: float,
        metadata: Dict[str, Any]
    ) -> None:
        """Publish threshold to Redis."""
        key = f"glyph:threshold:{glyph_id}"

        data = {
            "threshold": threshold,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "instance_id": metadata.get("instance_id", "unknown"),
            **metadata
        }

        # Store in hash
        self.redis_client.hset(key, mapping={
            k: json.dumps(v) if not isinstance(v, str) else v
            for k, v in data.items()
        })

        # Publish update notification
        channel = f"glyph:updates:{glyph_id}"
        self.redis_client.publish(channel, json.dumps(data))

        self._logger.info(
            f"Published threshold update for {glyph_id}",
            extra={"threshold": threshold, "instance": data["instance_id"]}
        )

    def get_threshold(self, glyph_id: str) -> Optional[Dict[str, Any]]:
        """Get threshold from Redis."""
        key = f"glyph:threshold:{glyph_id}"

        data = self.redis_client.hgetall(key)

        if not data:
            return None

        # Parse JSON values
        result = {}
        for k, v in data.items():
            try:
                result[k] = json.loads(v)
            except (json.JSONDecodeError, TypeError):
                result[k] = v

        return result

    def subscribe_to_updates(
        self,
        glyph_id: str,
        callback: Callable[[float, Dict[str, Any]], None]
    ) -> None:
        """Subscribe to threshold updates via Redis pub/sub."""
        self._subscribers[glyph_id] = callback

        # Start pub/sub thread if not already running
        if self._pubsub_thread is None:
            self._start_pubsub_listener()

    def _start_pubsub_listener(self) -> None:
        """Start Redis pub/sub listener thread."""
        pubsub = self.redis_client.pubsub()

        # Subscribe to all glyph update channels
        for glyph_id in self._subscribers.keys():
            channel = f"glyph:updates:{glyph_id}"
            pubsub.subscribe(channel)

        def listen():
            for message in pubsub.listen():
                if message["type"] == "message":
                    try:
                        data = json.loads(message["data"])

                        # Extract glyph_id from channel name
                        channel = message["channel"]
                        glyph_id = channel.split(":")[-1]

                        if glyph_id in self._subscribers:
                            threshold = data["threshold"]
                            metadata = {k: v for k, v in data.items() if k != "threshold"}
                            self._subscribers[glyph_id](threshold, metadata)

                    except Exception as e:
                        self._logger.error(f"Error processing pub/sub message: {e}")

        self._pubsub_thread = threading.Thread(target=listen, daemon=True)
        self._pubsub_thread.start()

    def list_all_glyphs(self) -> Dict[str, Dict[str, Any]]:
        """List all glyphs in registry."""
        pattern = "glyph:threshold:*"
        glyphs = {}

        for key in self.redis_client.scan_iter(match=pattern):
            glyph_id = key.split(":")[-1]
            data = self.get_threshold(glyph_id)
            if data:
                glyphs[glyph_id] = data

        return glyphs


class InMemoryGlyphRegistry:
    """In-memory GLYPH registry for testing/development."""

    def __init__(self):
        """Initialize in-memory registry."""
        self._storage: Dict[str, Dict[str, Any]] = {}
        self._subscribers: Dict[str, list] = {}
        self._logger = logging.getLogger(__name__)

    def publish_threshold(
        self,
        glyph_id: str,
        threshold: float,
        metadata: Dict[str, Any]
    ) -> None:
        """Publish threshold to in-memory storage."""
        data = {
            "threshold": threshold,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            **metadata
        }

        self._storage[glyph_id] = data

        # Notify subscribers
        if glyph_id in self._subscribers:
            for callback in self._subscribers[glyph_id]:
                try:
                    callback(threshold, metadata)
                except Exception as e:
                    self._logger.error(f"Error in subscriber callback: {e}")

    def get_threshold(self, glyph_id: str) -> Optional[Dict[str, Any]]:
        """Get threshold from in-memory storage."""
        return self._storage.get(glyph_id)

    def subscribe_to_updates(
        self,
        glyph_id: str,
        callback: Callable[[float, Dict[str, Any]], None]
    ) -> None:
        """Subscribe to threshold updates."""
        if glyph_id not in self._subscribers:
            self._subscribers[glyph_id] = []
        self._subscribers[glyph_id].append(callback)

    def list_all_glyphs(self) -> Dict[str, Dict[str, Any]]:
        """List all glyphs."""
        return dict(self._storage)


class DistributedGlyphSynchronizer:
    """
    Manages synchronization of GLYPH thresholds across multiple instances.

    Handles publishing local updates and subscribing to remote updates.
    """

    def __init__(
        self,
        registry: GlyphRegistryBackend,
        instance_id: Optional[str] = None,
        sync_interval: float = 5.0
    ):
        """
        Initialize synchronizer.

        Args:
            registry: Registry backend (Redis, in-memory, etc.)
            instance_id: Unique identifier for this instance
            sync_interval: Seconds between sync checks
        """
        self.registry = registry
        self.instance_id = instance_id or f"instance_{int(time.time())}"
        self.sync_interval = sync_interval

        self._local_thresholds: Dict[str, float] = {}
        self._sync_thread = None
        self._running = False
        self._logger = logging.getLogger(__name__)

    def publish_threshold_update(
        self,
        glyph_id: str,
        threshold: float
    ) -> None:
        """
        Publish threshold update to distributed registry.

        Args:
            glyph_id: GLYPH identifier
            threshold: New threshold value
        """
        self._local_thresholds[glyph_id] = threshold

        metadata = {
            "instance_id": self.instance_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        self.registry.publish_threshold(glyph_id, threshold, metadata)

        self._logger.info(
            f"Published threshold for {glyph_id}",
            extra={"threshold": threshold, "instance": self.instance_id}
        )

    def subscribe_to_glyph(
        self,
        glyph_id: str,
        callback: Callable[[float, Dict[str, Any]], None]
    ) -> None:
        """
        Subscribe to updates for a specific GLYPH.

        Args:
            glyph_id: GLYPH to subscribe to
            callback: Function to call when threshold updates
        """
        def wrapped_callback(threshold: float, metadata: Dict[str, Any]):
            # Don't process our own updates
            if metadata.get("instance_id") == self.instance_id:
                return

            self._logger.info(
                f"Received threshold update for {glyph_id}",
                extra={
                    "threshold": threshold,
                    "from_instance": metadata.get("instance_id")
                }
            )

            callback(threshold, metadata)

        self.registry.subscribe_to_updates(glyph_id, wrapped_callback)

    def get_consensus_threshold(
        self,
        glyph_id: str,
        strategy: str = "latest"
    ) -> Optional[float]:
        """
        Get consensus threshold from registry.

        Args:
            glyph_id: GLYPH identifier
            strategy: Consensus strategy ("latest", "average", "max", "min")

        Returns:
            Consensus threshold value or None
        """
        data = self.registry.get_threshold(glyph_id)

        if not data:
            return None

        if strategy == "latest":
            return data.get("threshold")

        # For other strategies, would need to query multiple instances
        # This is simplified for now
        return data.get("threshold")

    def start_background_sync(self) -> None:
        """Start background synchronization thread."""
        if self._running:
            self._logger.warning("Background sync already running")
            return

        self._running = True

        def sync_loop():
            while self._running:
                try:
                    self._perform_sync()
                except Exception as e:
                    self._logger.error(f"Error in sync loop: {e}")

                time.sleep(self.sync_interval)

        self._sync_thread = threading.Thread(target=sync_loop, daemon=True)
        self._sync_thread.start()

        self._logger.info("Started background synchronization")

    def _perform_sync(self) -> None:
        """Perform periodic synchronization check."""
        # Re-publish local thresholds to ensure freshness
        for glyph_id, threshold in self._local_thresholds.items():
            self.publish_threshold_update(glyph_id, threshold)

    def stop_background_sync(self) -> None:
        """Stop background synchronization."""
        self._running = False
        if self._sync_thread:
            self._sync_thread.join(timeout=2.0)

        self._logger.info("Stopped background synchronization")


# Integration into GlyphSpecialist
class GlyphSpecialist:
    """Symbolic GLYPH specialist with distributed synchronization."""

    def __init__(
        self,
        *,
        drift_threshold: float = 0.85,
        enable_distributed_sync: bool = False,
        registry_backend: str = "memory",
        redis_url: Optional[str] = None
    ):
        """
        Initialize GLYPH specialist.

        Args:
            drift_threshold: Local drift threshold
            enable_distributed_sync: Enable distributed registry sync
            registry_backend: "redis" or "memory"
            redis_url: Redis connection URL (if using Redis)
        """
        self.drift_threshold = drift_threshold
        self._logger = logging.getLogger(__name__)

        # Distributed synchronization
        self._enable_distributed_sync = enable_distributed_sync
        if enable_distributed_sync:
            registry = self._create_registry(registry_backend, redis_url)
            self._synchronizer = DistributedGlyphSynchronizer(registry)

            # Subscribe to threshold updates
            glyph_id = "default"  # Could be made configurable
            self._synchronizer.subscribe_to_glyph(
                glyph_id,
                self._on_remote_threshold_update
            )

            self._synchronizer.start_background_sync()
        else:
            self._synchronizer = None

    def _create_registry(
        self,
        backend_type: str,
        redis_url: Optional[str]
    ) -> GlyphRegistryBackend:
        """Create registry backend."""
        if backend_type == "redis":
            return RedisGlyphRegistry(redis_url or "redis://localhost:6379/0")
        elif backend_type == "memory":
            return InMemoryGlyphRegistry()
        else:
            raise ValueError(f"Unknown registry backend: {backend_type}")

    def update_threshold(self, new_threshold: float) -> None:
        """
        Update drift threshold used for consensus.

        Syncs to distributed registry if enabled.
        """
        if new_threshold <= 0:
            raise ValueError("new_threshold must be positive")

        self.drift_threshold = new_threshold
        self._logger.info(
            "# ΛTAG: glyph_threshold_update -- updated drift threshold",
            extra={"drift_threshold": new_threshold},
        )

        # Sync to distributed registry
        if self._enable_distributed_sync and self._synchronizer:
            self._synchronizer.publish_threshold_update("default", new_threshold)

    def _on_remote_threshold_update(
        self,
        threshold: float,
        metadata: Dict[str, Any]
    ) -> None:
        """
        Handle threshold update from remote instance.

        Args:
            threshold: Updated threshold value
            metadata: Update metadata (instance_id, timestamp, etc.)
        """
        self._logger.info(
            "Received remote threshold update",
            extra={
                "new_threshold": threshold,
                "from_instance": metadata.get("instance_id"),
                "timestamp": metadata.get("timestamp")
            }
        )

        # Apply update (could add conflict resolution logic here)
        self.drift_threshold = threshold
```

### **Testing Requirements**

Create tests in `tests/unit/core/symbolic/test_glyph_registry.py`:

```python
import pytest
import time
from unittest.mock import Mock
from core.symbolic.glyph_specialist import (
    InMemoryGlyphRegistry,
    DistributedGlyphSynchronizer,
    GlyphSpecialist
)

class TestInMemoryRegistry:

    def test_publish_and_get_threshold(self):
        """Test publishing and retrieving thresholds."""
        registry = InMemoryGlyphRegistry()

        registry.publish_threshold(
            "glyph1",
            0.85,
            {"instance": "test"}
        )

        data = registry.get_threshold("glyph1")

        assert data["threshold"] == 0.85
        assert data["instance"] == "test"

    def test_subscribe_to_updates(self):
        """Test subscription to threshold updates."""
        registry = InMemoryGlyphRegistry()

        updates = []

        def callback(threshold, metadata):
            updates.append((threshold, metadata))

        registry.subscribe_to_updates("glyph1", callback)

        registry.publish_threshold("glyph1", 0.9, {"test": "data"})

        assert len(updates) == 1
        assert updates[0][0] == 0.9

    def test_list_all_glyphs(self):
        """Test listing all glyphs."""
        registry = InMemoryGlyphRegistry()

        registry.publish_threshold("glyph1", 0.85, {})
        registry.publish_threshold("glyph2", 0.75, {})

        glyphs = registry.list_all_glyphs()

        assert len(glyphs) == 2
        assert "glyph1" in glyphs
        assert "glyph2" in glyphs


class TestDistributedSynchronizer:

    @pytest.fixture
    def registry(self):
        """Create in-memory registry."""
        return InMemoryGlyphRegistry()

    @pytest.fixture
    def synchronizer(self, registry):
        """Create synchronizer."""
        return DistributedGlyphSynchronizer(
            registry,
            instance_id="test_instance",
            sync_interval=1.0
        )

    def test_publish_threshold_update(self, synchronizer):
        """Test publishing threshold update."""
        synchronizer.publish_threshold_update("glyph1", 0.85)

        data = synchronizer.registry.get_threshold("glyph1")

        assert data["threshold"] == 0.85
        assert data["instance_id"] == "test_instance"

    def test_subscribe_to_glyph(self, synchronizer):
        """Test subscribing to GLYPH updates."""
        updates = []

        def callback(threshold, metadata):
            updates.append(threshold)

        synchronizer.subscribe_to_glyph("glyph1", callback)

        # Publish from different instance
        synchronizer.registry.publish_threshold(
            "glyph1",
            0.9,
            {"instance_id": "other_instance"}
        )

        # Should receive update
        assert len(updates) == 1
        assert updates[0] == 0.9

    def test_ignores_own_updates(self, synchronizer):
        """Test that own updates are ignored in subscription."""
        updates = []

        def callback(threshold, metadata):
            updates.append(threshold)

        synchronizer.subscribe_to_glyph("glyph1", callback)

        # Publish from same instance
        synchronizer.publish_threshold_update("glyph1", 0.85)

        # Should NOT receive update (own instance)
        assert len(updates) == 0

    def test_get_consensus_threshold(self, synchronizer):
        """Test getting consensus threshold."""
        synchronizer.publish_threshold_update("glyph1", 0.85)

        consensus = synchronizer.get_consensus_threshold("glyph1", strategy="latest")

        assert consensus == 0.85

    def test_background_sync(self, synchronizer):
        """Test background synchronization."""
        synchronizer.start_background_sync()

        assert synchronizer._running is True

        # Publish threshold
        synchronizer.publish_threshold_update("glyph1", 0.85)

        # Wait for sync
        time.sleep(2.0)

        # Verify threshold still present
        data = synchronizer.registry.get_threshold("glyph1")
        assert data["threshold"] == 0.85

        synchronizer.stop_background_sync()
        assert synchronizer._running is False


class TestGlyphSpecialistIntegration:

    def test_glyph_specialist_with_distributed_sync(self):
        """Test GlyphSpecialist with distributed sync enabled."""
        specialist = GlyphSpecialist(
            drift_threshold=0.85,
            enable_distributed_sync=True,
            registry_backend="memory"
        )

        # Update threshold
        specialist.update_threshold(0.9)

        # Verify it was synced to registry
        assert specialist.drift_threshold == 0.9

    def test_glyph_specialist_without_sync(self):
        """Test GlyphSpecialist without distributed sync."""
        specialist = GlyphSpecialist(
            drift_threshold=0.85,
            enable_distributed_sync=False
        )

        # Update threshold
        specialist.update_threshold(0.9)

        # Should work without registry
        assert specialist.drift_threshold == 0.9

    def test_remote_threshold_propagation(self):
        """Test that remote updates propagate to local instance."""
        # Create two instances sharing same registry
        registry = InMemoryGlyphRegistry()

        sync1 = DistributedGlyphSynchronizer(registry, instance_id="instance1")
        sync2 = DistributedGlyphSynchronizer(registry, instance_id="instance2")

        # Track updates on instance2
        updates = []

        def callback(threshold, metadata):
            updates.append(threshold)

        sync2.subscribe_to_glyph("default", callback)

        # Publish from instance1
        sync1.publish_threshold_update("default", 0.95)

        # Instance2 should receive update
        assert len(updates) == 1
        assert updates[0] == 0.95
```

### **Acceptance Criteria**

✅ **Functional Requirements**:
- [ ] `GlyphRegistryBackend` protocol
- [ ] `RedisGlyphRegistry` implementation
- [ ] `InMemoryGlyphRegistry` implementation
- [ ] `DistributedGlyphSynchronizer` class
- [ ] Publish threshold to registry
- [ ] Subscribe to threshold updates
- [ ] Background synchronization thread
- [ ] Consensus threshold retrieval
- [ ] Integration into `GlyphSpecialist`
- [ ] Optional enable/disable flag

✅ **Testing Requirements**:
- [ ] In-memory registry tests (3+ tests)
- [ ] Synchronizer tests (6+ tests)
- [ ] GlyphSpecialist integration tests (3+ tests)
- [ ] Test multi-instance synchronization
- [ ] Test update propagation
- [ ] Test own-update filtering

✅ **Documentation**:
- [ ] Docstrings for all classes
- [ ] Registry backend selection guide
- [ ] Configuration examples
- [ ] TODO comment removed

✅ **Configuration**:
- [ ] Environment variables for registry backend
- [ ] Redis URL configuration
- [ ] Sync interval configuration

### **Configuration**

```python
# config/glyph_registry.py

import os

DISTRIBUTED_SYNC_ENABLED = os.getenv("GLYPH_DISTRIBUTED_SYNC", "0") == "1"
REGISTRY_BACKEND = os.getenv("GLYPH_REGISTRY_BACKEND", "memory")  # "redis" or "memory"
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
SYNC_INTERVAL = float(os.getenv("GLYPH_SYNC_INTERVAL", "5.0"))
```

### **References**

- **Module**: `core/symbolic/glyph_specialist.py`
- **Symbolic Systems**: `core/symbolic/`
- **Distributed Systems**: Redis pub/sub, etcd
- **Documentation**: LUKHAS distributed architecture

---

## TODO #7: Blockchain Integration for Decentralized Dream Commerce

**File**: `core/bridge/dream_commerce.py`
**Line**: 46
**Complexity**: Very High
**Estimated Effort**: 6-10 hours
**Owner**: blockchain-team / dream-commerce-team

### **Context**

The Dream Commerce system (SEEDRA Protocol) provides consent-driven dream experience generation with commercial integration. Currently lacks blockchain backend for decentralized commerce. The TODO requests adding **blockchain integration** for transparent, trustless dream content transactions.

**Current System (SEEDRA Protocol)**:
- Creative, Brand, Educational, Therapeutic dream content
- Consent-driven marketing with privacy preservation
- Revenue sharing and creator compensation
- Ethical advertising boundary enforcement
- Dream experience marketplace

**Current TODO**:
```python
# Line 46 in core/bridge/dream_commerce.py
ΛTODO: Add blockchain integration for decentralized dream commerce
```

### **Technical Requirements**

**Goal**: Implement blockchain-based smart contracts for:
1. **Dream Content NFTs**: Tokenize dream experiences as NFTs
2. **Royalty Distribution**: Automated creator compensation
3. **Consent Ledger**: Immutable consent tracking
4. **Escrow Payments**: Trustless payment handling
5. **Reputation System**: On-chain creator/consumer reputation

**Blockchain Architecture**:
- **Smart Contracts**: Solidity contracts for Ethereum/Polygon
- **Web3 Integration**: Python web3.py for blockchain interaction
- **IPFS Storage**: Decentralized dream content storage
- **Oracle Integration**: Off-chain data verification
- **Gas Optimization**: Minimize transaction costs

**Implementation Approach**:

```python
# Add to core/bridge/dream_commerce.py

from typing import Optional, Dict, List, Any
from decimal import Decimal
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import hashlib

# Blockchain dependencies (optional)
try:
    from web3 import Web3, HTTPProvider
    from web3.contract import Contract
    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False

try:
    import ipfshttpclient
    IPFS_AVAILABLE = True
except ImportError:
    IPFS_AVAILABLE = False


@dataclass
class DreamContentNFT:
    """Represents a dream content NFT."""
    token_id: int
    dream_seed_id: str
    creator_address: str
    content_hash: str  # IPFS hash
    metadata_uri: str  # IPFS metadata URI
    mint_timestamp: datetime
    royalty_percentage: Decimal  # 0-100
    license_terms: Dict[str, Any]


@dataclass
class ConsentRecord:
    """Blockchain-backed consent record."""
    user_address: str
    dream_seed_id: str
    consent_given: bool
    timestamp: datetime
    transaction_hash: str
    ipfs_proof_hash: Optional[str] = None


class DreamCommerceBlockchain:
    """
    Blockchain integration for decentralized dream commerce.

    Manages NFT minting, royalty distribution, and consent ledger
    on Ethereum-compatible blockchains.
    """

    # Smart contract ABIs (simplified for example)
    DREAM_NFT_ABI = json.loads('''[
        {
            "inputs": [{"type": "string", "name": "contentHash"}, {"type": "uint256", "name": "royalty"}],
            "name": "mintDreamNFT",
            "outputs": [{"type": "uint256"}],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [{"type": "uint256", "name": "tokenId"}],
            "name": "tokenURI",
            "outputs": [{"type": "string"}],
            "stateMutability": "view",
            "type": "function"
        }
    ]''')

    CONSENT_LEDGER_ABI = json.loads('''[
        {
            "inputs": [{"type": "string", "name": "dreamSeedId"}, {"type": "bool", "name": "consent"}],
            "name": "recordConsent",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [{"type": "address", "name": "user"}, {"type": "string", "name": "dreamSeedId"}],
            "name": "getConsent",
            "outputs": [{"type": "bool"}],
            "stateMutability": "view",
            "type": "function"
        }
    ]''')

    def __init__(
        self,
        *,
        blockchain_rpc_url: str = "http://localhost:8545",
        dream_nft_contract_address: Optional[str] = None,
        consent_ledger_address: Optional[str] = None,
        ipfs_api: str = "/ip4/127.0.0.1/tcp/5001",
        private_key: Optional[str] = None
    ):
        """
        Initialize blockchain integration.

        Args:
            blockchain_rpc_url: Ethereum RPC endpoint
            dream_nft_contract_address: Deployed NFT contract address
            consent_ledger_address: Deployed consent ledger address
            ipfs_api: IPFS API endpoint
            private_key: Private key for signing transactions
        """
        if not WEB3_AVAILABLE:
            raise ImportError("Blockchain features require web3: pip install web3")

        self.w3 = Web3(HTTPProvider(blockchain_rpc_url))

        if not self.w3.is_connected():
            raise ConnectionError(f"Cannot connect to blockchain at {blockchain_rpc_url}")

        self.dream_nft_address = dream_nft_contract_address
        self.consent_ledger_address = consent_ledger_address
        self._private_key = private_key

        # Initialize contracts
        self.dream_nft_contract: Optional[Contract] = None
        self.consent_ledger_contract: Optional[Contract] = None

        if dream_nft_contract_address:
            self.dream_nft_contract = self.w3.eth.contract(
                address=dream_nft_contract_address,
                abi=self.DREAM_NFT_ABI
            )

        if consent_ledger_address:
            self.consent_ledger_contract = self.w3.eth.contract(
                address=consent_ledger_address,
                abi=self.CONSENT_LEDGER_ABI
            )

        # IPFS client
        self._ipfs_client = None
        if IPFS_AVAILABLE:
            try:
                self._ipfs_client = ipfshttpclient.connect(ipfs_api)
            except Exception as e:
                logging.warning(f"Could not connect to IPFS: {e}")

        self._logger = logging.getLogger(__name__)

    def upload_to_ipfs(self, content: bytes) -> str:
        """
        Upload content to IPFS.

        Args:
            content: Raw content bytes

        Returns:
            IPFS hash (CID)
        """
        if not self._ipfs_client:
            raise RuntimeError("IPFS client not available")

        result = self._ipfs_client.add_bytes(content)
        ipfs_hash = result

        self._logger.info(f"Uploaded to IPFS: {ipfs_hash}")

        return ipfs_hash

    def mint_dream_nft(
        self,
        dream_seed_id: str,
        content: bytes,
        creator_address: str,
        royalty_percentage: Decimal,
        metadata: Dict[str, Any]
    ) -> DreamContentNFT:
        """
        Mint a dream content NFT on blockchain.

        Args:
            dream_seed_id: Dream seed identifier
            content: Dream content (imagery, audio, etc.)
            creator_address: Creator's blockchain address
            royalty_percentage: Royalty for secondary sales (0-100)
            metadata: NFT metadata

        Returns:
            DreamContentNFT with token ID and IPFS hashes
        """
        if not self.dream_nft_contract:
            raise RuntimeError("Dream NFT contract not initialized")

        # Upload content to IPFS
        content_hash = self.upload_to_ipfs(content)

        # Create metadata
        nft_metadata = {
            "name": metadata.get("name", f"Dream {dream_seed_id}"),
            "description": metadata.get("description", ""),
            "image": f"ipfs://{content_hash}",
            "dream_seed_id": dream_seed_id,
            "creator": creator_address,
            "royalty": float(royalty_percentage),
            **metadata
        }

        # Upload metadata to IPFS
        metadata_bytes = json.dumps(nft_metadata).encode()
        metadata_hash = self.upload_to_ipfs(metadata_bytes)
        metadata_uri = f"ipfs://{metadata_hash}"

        # Mint NFT on blockchain
        account = self.w3.eth.account.from_key(self._private_key)

        tx = self.dream_nft_contract.functions.mintDreamNFT(
            content_hash,
            int(royalty_percentage)
        ).build_transaction({
            'from': account.address,
            'nonce': self.w3.eth.get_transaction_count(account.address),
            'gas': 200000,
            'gasPrice': self.w3.eth.gas_price
        })

        # Sign and send transaction
        signed_tx = account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

        # Wait for confirmation
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        # Extract token ID from logs (simplified)
        token_id = int.from_bytes(receipt['logs'][0]['topics'][1], 'big')

        nft = DreamContentNFT(
            token_id=token_id,
            dream_seed_id=dream_seed_id,
            creator_address=creator_address,
            content_hash=content_hash,
            metadata_uri=metadata_uri,
            mint_timestamp=datetime.now(timezone.utc),
            royalty_percentage=royalty_percentage,
            license_terms=metadata.get("license", {})
        )

        self._logger.info(
            f"Minted Dream NFT #{token_id}",
            extra={
                "dream_seed_id": dream_seed_id,
                "creator": creator_address,
                "tx_hash": tx_hash.hex()
            }
        )

        return nft

    def record_consent_on_chain(
        self,
        user_address: str,
        dream_seed_id: str,
        consent_given: bool
    ) -> ConsentRecord:
        """
        Record user consent on blockchain for immutable audit trail.

        Args:
            user_address: User's blockchain address
            dream_seed_id: Dream seed identifier
            consent_given: Whether consent was given

        Returns:
            ConsentRecord with transaction hash
        """
        if not self.consent_ledger_contract:
            raise RuntimeError("Consent ledger contract not initialized")

        account = self.w3.eth.account.from_key(self._private_key)

        # Build transaction
        tx = self.consent_ledger_contract.functions.recordConsent(
            dream_seed_id,
            consent_given
        ).build_transaction({
            'from': account.address,
            'nonce': self.w3.eth.get_transaction_count(account.address),
            'gas': 100000,
            'gasPrice': self.w3.eth.gas_price
        })

        # Sign and send
        signed_tx = account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

        # Wait for confirmation
        self.w3.eth.wait_for_transaction_receipt(tx_hash)

        record = ConsentRecord(
            user_address=user_address,
            dream_seed_id=dream_seed_id,
            consent_given=consent_given,
            timestamp=datetime.now(timezone.utc),
            transaction_hash=tx_hash.hex()
        )

        self._logger.info(
            f"Recorded consent on-chain",
            extra={
                "user": user_address,
                "dream_seed": dream_seed_id,
                "consent": consent_given,
                "tx_hash": tx_hash.hex()
            }
        )

        return record

    def verify_consent_on_chain(
        self,
        user_address: str,
        dream_seed_id: str
    ) -> bool:
        """
        Verify consent from blockchain ledger.

        Args:
            user_address: User's blockchain address
            dream_seed_id: Dream seed identifier

        Returns:
            True if consent was given, False otherwise
        """
        if not self.consent_ledger_contract:
            raise RuntimeError("Consent ledger contract not initialized")

        consent = self.consent_ledger_contract.functions.getConsent(
            user_address,
            dream_seed_id
        ).call()

        return bool(consent)

    def distribute_royalties(
        self,
        token_id: int,
        sale_amount: Decimal,
        buyer_address: str
    ) -> Dict[str, Decimal]:
        """
        Distribute royalties from secondary sale.

        Args:
            token_id: NFT token ID
            sale_amount: Sale price in wei
            buyer_address: Buyer's address

        Returns:
            Dict mapping addresses to amounts
        """
        # This would interact with a marketplace contract
        # Simplified implementation

        # Get royalty percentage from NFT metadata
        metadata_uri = self.dream_nft_contract.functions.tokenURI(token_id).call()
        # Fetch and parse metadata...

        # Calculate distributions
        royalty_percentage = Decimal("10")  # From metadata
        creator_amount = sale_amount * royalty_percentage / 100
        seller_amount = sale_amount - creator_amount

        return {
            "creator": creator_amount,
            "seller": seller_amount
        }


# Integration into DreamCommerceService
class DreamCommerceService:
    """Dream commerce service with blockchain integration."""

    def __init__(
        self,
        *,
        enable_blockchain: bool = False,
        blockchain_config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize dream commerce service.

        Args:
            enable_blockchain: Enable blockchain features
            blockchain_config: Blockchain configuration dict
        """
        self._enable_blockchain = enable_blockchain and WEB3_AVAILABLE

        if self._enable_blockchain:
            self._blockchain = DreamCommerceBlockchain(**(blockchain_config or {}))
        else:
            self._blockchain = None

    def publish_dream_content(
        self,
        dream_seed: Dict[str, Any],
        content: bytes,
        creator_address: str,
        royalty_percentage: Decimal = Decimal("10")
    ) -> Dict[str, Any]:
        """
        Publish dream content as NFT (if blockchain enabled).

        Args:
            dream_seed: Dream seed data
            content: Dream content bytes
            creator_address: Creator's blockchain address
            royalty_percentage: Royalty for secondary sales

        Returns:
            Publication result with NFT details
        """
        if not self._enable_blockchain or not self._blockchain:
            # Fallback to traditional publishing
            return {
                "published": True,
                "blockchain": False,
                "dream_seed_id": dream_seed["id"]
            }

        # Mint as NFT
        nft = self._blockchain.mint_dream_nft(
            dream_seed_id=dream_seed["id"],
            content=content,
            creator_address=creator_address,
            royalty_percentage=royalty_percentage,
            metadata={
                "name": dream_seed.get("title"),
                "description": dream_seed.get("description"),
                "category": dream_seed.get("type")
            }
        )

        return {
            "published": True,
            "blockchain": True,
            "dream_seed_id": dream_seed["id"],
            "nft": {
                "token_id": nft.token_id,
                "content_hash": nft.content_hash,
                "metadata_uri": nft.metadata_uri
            }
        }
```

### **Smart Contract Example (Solidity)**

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract DreamContentNFT is ERC721, Ownable {
    uint256 private _tokenIdCounter;

    struct DreamNFT {
        string contentHash;  // IPFS hash
        uint256 royaltyPercentage;  // 0-100
        address creator;
    }

    mapping(uint256 => DreamNFT) public dreamNFTs;

    event DreamMinted(uint256 indexed tokenId, string contentHash, address creator);

    constructor() ERC721("DreamContent", "DREAM") {}

    function mintDreamNFT(string memory contentHash, uint256 royaltyPercentage)
        public
        returns (uint256)
    {
        require(royaltyPercentage <= 100, "Royalty cannot exceed 100%");

        uint256 tokenId = _tokenIdCounter;
        _tokenIdCounter++;

        _safeMint(msg.sender, tokenId);

        dreamNFTs[tokenId] = DreamNFT({
            contentHash: contentHash,
            royaltyPercentage: royaltyPercentage,
            creator: msg.sender
        });

        emit DreamMinted(tokenId, contentHash, msg.sender);

        return tokenId;
    }

    function tokenURI(uint256 tokenId)
        public
        view
        override
        returns (string memory)
    {
        require(_exists(tokenId), "Token does not exist");
        return string(abi.encodePacked("ipfs://", dreamNFTs[tokenId].contentHash));
    }
}

contract ConsentLedger is Ownable {
    mapping(address => mapping(string => bool)) private consents;

    event ConsentRecorded(address indexed user, string dreamSeedId, bool consent);

    function recordConsent(string memory dreamSeedId, bool consent) public {
        consents[msg.sender][dreamSeedId] = consent;
        emit ConsentRecorded(msg.sender, dreamSeedId, consent);
    }

    function getConsent(address user, string memory dreamSeedId)
        public
        view
        returns (bool)
    {
        return consents[user][dreamSeedId];
    }
}
```

### **Testing Requirements**

Create tests in `tests/unit/core/bridge/test_dream_blockchain.py`:

```python
import pytest
from decimal import Decimal
from unittest.mock import Mock, MagicMock, patch
from core.bridge.dream_commerce import (
    DreamCommerceBlockchain,
    DreamContentNFT,
    ConsentRecord,
    WEB3_AVAILABLE
)

pytestmark = pytest.mark.skipif(
    not WEB3_AVAILABLE,
    reason="Web3 dependencies not available"
)


class TestDreamCommerceBlockchain:

    @pytest.fixture
    def mock_web3(self):
        """Mock Web3 instance."""
        with patch('core.bridge.dream_commerce.Web3') as mock_w3_class:
            mock_w3 = MagicMock()
            mock_w3.is_connected.return_value = True
            mock_w3.eth.gas_price = 1000000000
            mock_w3_class.return_value = mock_w3
            yield mock_w3

    @pytest.fixture
    def blockchain(self, mock_web3):
        """Create blockchain instance with mocks."""
        with patch('core.bridge.dream_commerce.ipfshttpclient'):
            bc = DreamCommerceBlockchain(
                blockchain_rpc_url="http://localhost:8545",
                dream_nft_contract_address="0x" + "1" * 40,
                consent_ledger_address="0x" + "2" * 40,
                private_key="0x" + "a" * 64
            )
            yield bc

    def test_initialization(self, blockchain):
        """Test blockchain initialization."""
        assert blockchain.w3 is not None
        assert blockchain.dream_nft_address == "0x" + "1" * 40

    def test_upload_to_ipfs(self, blockchain):
        """Test IPFS upload."""
        with patch.object(blockchain, '_ipfs_client') as mock_ipfs:
            mock_ipfs.add_bytes.return_value = "Qm123abc"

            content = b"test dream content"
            ipfs_hash = blockchain.upload_to_ipfs(content)

            assert ipfs_hash == "Qm123abc"
            mock_ipfs.add_bytes.assert_called_once_with(content)

    def test_mint_dream_nft(self, blockchain):
        """Test NFT minting."""
        # Mock IPFS uploads
        with patch.object(blockchain, 'upload_to_ipfs', side_effect=["Qm123content", "Qm456metadata"]):
            # Mock contract transaction
            with patch.object(blockchain.dream_nft_contract.functions, 'mintDreamNFT') as mock_mint:
                mock_build = MagicMock()
                mock_build.build_transaction.return_value = {"gas": 200000}
                mock_mint.return_value = mock_build

                # Mock transaction sending
                with patch.object(blockchain.w3.eth, 'send_raw_transaction', return_value=b'\x12\x34'):
                    with patch.object(blockchain.w3.eth, 'wait_for_transaction_receipt') as mock_receipt:
                        mock_receipt.return_value = {
                            'logs': [{'topics': [b'', b'\x00' * 31 + b'\x01']}]
                        }

                        nft = blockchain.mint_dream_nft(
                            dream_seed_id="dream_001",
                            content=b"dream content",
                            creator_address="0x" + "3" * 40,
                            royalty_percentage=Decimal("10"),
                            metadata={"name": "Test Dream"}
                        )

                        assert isinstance(nft, DreamContentNFT)
                        assert nft.token_id == 1
                        assert nft.content_hash == "Qm123content"

    def test_record_consent_on_chain(self, blockchain):
        """Test consent recording."""
        with patch.object(blockchain.consent_ledger_contract.functions, 'recordConsent') as mock_record:
            mock_build = MagicMock()
            mock_build.build_transaction.return_value = {"gas": 100000}
            mock_record.return_value = mock_build

            with patch.object(blockchain.w3.eth, 'send_raw_transaction', return_value=b'\xab\xcd'):
                with patch.object(blockchain.w3.eth, 'wait_for_transaction_receipt'):
                    record = blockchain.record_consent_on_chain(
                        user_address="0x" + "4" * 40,
                        dream_seed_id="dream_001",
                        consent_given=True
                    )

                    assert isinstance(record, ConsentRecord)
                    assert record.consent_given is True
                    assert record.transaction_hash is not None

    def test_verify_consent_on_chain(self, blockchain):
        """Test consent verification."""
        with patch.object(blockchain.consent_ledger_contract.functions, 'getConsent') as mock_get:
            mock_call = MagicMock()
            mock_call.call.return_value = True
            mock_get.return_value = mock_call

            consent = blockchain.verify_consent_on_chain(
                user_address="0x" + "4" * 40,
                dream_seed_id="dream_001"
            )

            assert consent is True
```

### **Acceptance Criteria**

✅ **Functional Requirements**:
- [ ] `DreamContentNFT` and `ConsentRecord` dataclasses
- [ ] `DreamCommerceBlockchain` class
- [ ] IPFS content upload
- [ ] NFT minting with royalties
- [ ] Consent recording on-chain
- [ ] Consent verification from chain
- [ ] Royalty distribution calculation
- [ ] Integration into `DreamCommerceService`
- [ ] Smart contract examples (Solidity)

✅ **Testing Requirements**:
- [ ] Blockchain integration tests (5+ tests)
- [ ] Mock Web3 interactions
- [ ] IPFS upload tests
- [ ] NFT minting tests
- [ ] Consent ledger tests
- [ ] Graceful degradation if blockchain unavailable

✅ **Documentation**:
- [ ] Comprehensive docstrings
- [ ] Smart contract documentation
- [ ] Deployment guide
- [ ] TODO comment removed

✅ **Dependencies**:
- [ ] `web3>=6.0.0`
- [ ] `ipfshttpclient>=0.8.0`
- [ ] OpenZeppelin contracts for Solidity

### **Configuration**

```python
# config/blockchain.py

import os

BLOCKCHAIN_ENABLED = os.getenv("BLOCKCHAIN_ENABLED", "0") == "1"
BLOCKCHAIN_RPC_URL = os.getenv("BLOCKCHAIN_RPC_URL", "http://localhost:8545")
DREAM_NFT_CONTRACT = os.getenv("DREAM_NFT_CONTRACT_ADDRESS")
CONSENT_LEDGER_CONTRACT = os.getenv("CONSENT_LEDGER_CONTRACT_ADDRESS")
IPFS_API = os.getenv("IPFS_API", "/ip4/127.0.0.1/tcp/5001")
BLOCKCHAIN_PRIVATE_KEY = os.getenv("BLOCKCHAIN_PRIVATE_KEY")  # Keep secure!
```

### **References**

- **Module**: `core/bridge/dream_commerce.py`
- **Dream Systems**: `candidate/consciousness/dream/`
- **SEEDRA Protocol**: Dream content consent and commerce
- **Documentation**: Blockchain integration architecture

---

## ✅ Submission Checklist

Before considering a TODO complete:

- [ ] Implementation matches technical requirements
- [ ] All acceptance criteria met
- [ ] Tests written and passing (pytest)
- [ ] Lane-guard validation passes (`make lane-guard`)
- [ ] Linting passes (`make lint`)
- [ ] Docstrings added for all public APIs
- [ ] TODO comment removed from original file
- [ ] Example usage documented
- [ ] Smoke test added (if applicable)
- [ ] Integration test with related systems (if applicable)

---

**Generated for**: Claude Code Web
**Repository**: /Users/agi_dev/LOCAL-REPOS/Lukhas
**Contact**: @consciousness-team, @ethics-team, @governance-team, @quantum-team, @blockchain-team

*Use these prompts to delegate complex TODOs while maintaining LUKHAS architecture patterns and quality standards.*
