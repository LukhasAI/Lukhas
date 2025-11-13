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
**Contact**: @consciousness-team, @ethics-team, @governance-team

*Use these prompts to delegate complex TODOs while maintaining LUKHAS architecture patterns and quality standards.*
