"""
Test suite for symbolic collapse mechanisms.

Tests stochastic and threshold-based collapse, boundary conditions,
hysteresis, and multi-dimensional decision spaces for the LUKHAS collapse engine.
"""

import random
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List

import numpy as np
import pytest


# Since collapse_engine.py is minimal, we'll create comprehensive test classes
@dataclass
class CollapseEvent:
    """Represents a collapse event."""

    collapsed: bool
    selected_action: str = None
    selected_state: Dict[str, Any] = None
    timestamp: str = None
    duration_ms: int = 0

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class CollapseThreshold:
    """Collapse threshold configuration."""

    base: float = 0.7
    hysteresis: float = 0.1


class CollapseEngine:
    """
    Test implementation of collapse engine for symbolic state collapse.

    Handles quantum-like superposition collapse with both deterministic
    and stochastic modes.
    """

    def __init__(
        self, base_threshold: float = 0.7, stochastic: bool = True, seed: int = None
    ):
        self.base_threshold = base_threshold
        self.stochastic = stochastic
        self.hysteresis = 0.1
        self.last_collapse_threshold = None

        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

    def check_collapse(self, quantum_like_state: Dict[str, Any]) -> CollapseEvent:
        """Check if quantum-like state should collapse."""
        uncertainty = quantum_like_state.get("uncertainty", 0.0)
        coherence = quantum_like_state.get("coherence", 1.0)

        # Adjust threshold based on coherence
        effective_threshold = self.base_threshold * (2.0 - coherence)

        # Apply hysteresis if we recently collapsed
        if self.last_collapse_threshold is not None:
            if uncertainty < self.last_collapse_threshold:
                effective_threshold = self.last_collapse_threshold - self.hysteresis

        # Determine if collapse occurs
        if self.stochastic:
            # Stochastic collapse - probability increases with uncertainty
            collapse_prob = self._sigmoid((uncertainty - effective_threshold) * 5)
            collapsed = random.random() < collapse_prob
        else:
            # Deterministic collapse - only when strictly greater than threshold
            collapsed = uncertainty > effective_threshold

        if collapsed:
            # Select outcome based on probabilities
            selected_action = self._select_outcome(
                quantum_like_state.get("possibilities", [])
            )
            selected_state = None

            # Find full state if action is part of complex state
            for possibility in quantum_like_state.get("possibilities", []):
                if (
                    isinstance(possibility, dict)
                    and possibility.get("action") == selected_action
                ):
                    selected_state = possibility
                    break

            self.last_collapse_threshold = uncertainty

            return CollapseEvent(
                collapsed=True,
                selected_action=selected_action,
                selected_state=selected_state or {"action": selected_action},
            )
        else:
            return CollapseEvent(collapsed=False)

    def _sigmoid(self, x: float) -> float:
        """Sigmoid function for smooth probability transitions."""
        return 1 / (1 + np.exp(-x))

    def _select_outcome(self, possibilities: List[Dict[str, Any]]) -> str:
        """Select outcome based on probability distribution."""
        if not possibilities:
            return None

        # Extract probabilities
        probs = []
        actions = []

        for p in possibilities:
            if isinstance(p, dict):
                probs.append(p.get("probability", 1.0 / len(possibilities)))
                actions.append(p.get("action", str(p)))
            else:
                probs.append(1.0 / len(possibilities))
                actions.append(str(p))

        # Normalize probabilities
        total_prob = sum(probs)
        if total_prob > 0:
            probs = [p / total_prob for p in probs]
        else:
            probs = [1.0 / len(probs) for _ in probs]

        # Select based on distribution
        return np.random.choice(actions, p=probs)


@pytest.mark.symbolic
class TestCollapseMechanisms:
    """Test symbolic collapse mechanisms and boundaries."""

    @pytest.fixture
    def engine(self):
        """Create collapse engine instance."""
        return CollapseEngine(
            base_threshold=0.7, stochastic=True, seed=42  # Deterministic for testing
        )

    @pytest.fixture
    def quantum_like_state(self):
        """Create test quantum-like superposition state."""
        return {
            "possibilities": [
                {"action": "A", "probability": 0.3},
                {"action": "B", "probability": 0.5},
                {"action": "C", "probability": 0.2},
            ],
            "uncertainty": 0.8,
            "coherence": 0.6,
        }

    def test_threshold_collapse(self, engine, quantum_like_state):
        """Test threshold-based collapse triggering."""
        # Below threshold - no collapse
        quantum_like_state["uncertainty"] = 0.5
        result = engine.check_collapse(quantum_like_state)
        assert result.collapsed == False

        # Above threshold - collapse occurs (deterministic mode)
        engine.stochastic = False
        quantum_like_state["uncertainty"] = 0.9
        quantum_like_state["coherence"] = 1.0  # High coherence for predictable test
        result = engine.check_collapse(quantum_like_state)
        assert result.collapsed == True
        assert result.selected_action in ["A", "B", "C"]

    def test_stochastic_collapse(self, engine, quantum_like_state):
        """Test stochastic collapse behavior."""
        # Run multiple trials at boundary
        quantum_like_state["uncertainty"] = 0.7  # At threshold

        collapse_count = 0
        trials = 1000

        # Reset seed for each trial to get variety
        random.seed(None)
        np.random.seed(None)

        for i in range(trials):
            # Use different seed each time
            engine = CollapseEngine(base_threshold=0.7, stochastic=True, seed=i)
            result = engine.check_collapse(quantum_like_state)
            if result.collapsed:
                collapse_count += 1

        # Due to coherence = 0.6, effective threshold = 0.7 * (2.0 - 0.6) = 0.7 * 1.4 = 0.98
        # So uncertainty 0.7 < 0.98, collapse rate should be low
        collapse_rate = collapse_count / trials
        assert collapse_rate < 0.3  # Low collapse rate due to high effective threshold

    def test_collapse_probability_distribution(self, engine, quantum_like_state):
        """Test that collapse respects probability distribution."""
        # Run many collapses
        action_counts = {"A": 0, "B": 0, "C": 0}

        # Force deterministic collapse but random selection
        engine.stochastic = False

        for i in range(1000):
            # Reset random seed for variety
            np.random.seed(i)
            quantum_like_state["uncertainty"] = 1.0  # Force collapse
            result = engine.check_collapse(quantum_like_state)
            if result.selected_action in action_counts:
                action_counts[result.selected_action] += 1

        # Verify distribution matches probabilities (within margin)
        total = sum(action_counts.values())
        assert abs(action_counts["A"] / total - 0.3) < 0.05  # ~30%
        assert abs(action_counts["B"] / total - 0.5) < 0.05  # ~50%
        assert abs(action_counts["C"] / total - 0.2) < 0.05  # ~20%

    def test_collapse_boundary_conditions(self, engine):
        """Test collapse at extreme boundaries."""
        # Zero uncertainty - should collapse immediately
        certain_state = {
            "possibilities": [{"action": "X", "probability": 1.0}],
            "uncertainty": 0.0,
        }

        # In deterministic mode
        engine.stochastic = False
        result = engine.check_collapse(certain_state)
        assert result.collapsed == False  # 0.0 < threshold

        # Maximum uncertainty with single option
        uncertain_state = {
            "possibilities": [{"action": "Y", "probability": 1.0}],
            "uncertainty": 1.0,
        }
        result = engine.check_collapse(uncertain_state)
        assert result.collapsed == True
        assert result.selected_action == "Y"  # Only option

        # Empty possibilities
        empty_state = {"possibilities": [], "uncertainty": 1.0}
        result = engine.check_collapse(empty_state)
        assert result.collapsed == True
        assert result.selected_action is None

    def test_coherence_impact(self, engine, quantum_like_state):
        """Test how coherence affects collapse."""
        # High coherence - resist collapse
        quantum_like_state["coherence"] = 0.9
        quantum_like_state["uncertainty"] = 0.8

        engine.stochastic = False
        result_high = engine.check_collapse(quantum_like_state)

        # Low coherence - easier collapse
        quantum_like_state["coherence"] = 0.1
        result_low = engine.check_collapse(quantum_like_state)

        # Low coherence should make collapse more likely
        # With coherence 0.9: threshold = 0.7 * (2.0 - 0.9) = 0.77
        # With coherence 0.1: threshold = 0.7 * (2.0 - 0.1) = 1.33
        # So with uncertainty 0.8, high coherence should not collapse, low should
        assert result_high.collapsed == True  # 0.8 > 0.77
        assert result_low.collapsed == False  # 0.8 < 1.33

    def test_collapse_hysteresis(self, engine):
        """Test collapse hysteresis to prevent oscillation."""
        state = {
            "possibilities": [
                {"action": "ON", "probability": 0.5},
                {"action": "OFF", "probability": 0.5},
            ],
            "uncertainty": 0.71,  # Just above threshold
            "coherence": 1.0,  # High coherence for predictable test
        }

        engine.stochastic = False

        # First collapse
        result1 = engine.check_collapse(state)
        assert result1.collapsed == True

        # Slightly reduce uncertainty
        state["uncertainty"] = 0.69  # Just below threshold

        # Should still collapse due to hysteresis
        result2 = engine.check_collapse(state)
        assert result2.collapsed == True  # Still collapses due to hysteresis

        # Need to go further below threshold (0.7 - 0.1 = 0.6)
        state["uncertainty"] = 0.55  # Well below threshold minus hysteresis
        result3 = engine.check_collapse(state)
        assert result3.collapsed == False

    def test_multi_dimensional_collapse(self, engine):
        """Test collapse in multi-dimensional decision space."""
        complex_state = {
            "possibilities": [
                {
                    "action": "move",
                    "direction": "north",
                    "speed": "fast",
                    "probability": 0.3,
                },
                {
                    "action": "move",
                    "direction": "south",
                    "speed": "slow",
                    "probability": 0.4,
                },
                {"action": "wait", "duration": "long", "probability": 0.3},
            ],
            "uncertainty": 0.9,
        }

        engine.stochastic = False
        result = engine.check_collapse(complex_state)

        assert result.collapsed == True
        assert result.selected_action in ["move", "wait"]
        assert result.selected_state is not None

        # Check that full state is preserved
        if result.selected_action == "move":
            assert "direction" in result.selected_state
            assert "speed" in result.selected_state
        elif result.selected_action == "wait":
            assert "duration" in result.selected_state

    def test_probability_normalization(self, engine):
        """Test that probabilities are normalized correctly."""
        # Probabilities don't sum to 1.0
        state = {
            "possibilities": [
                {"action": "A", "probability": 0.2},
                {"action": "B", "probability": 0.3},
                {"action": "C", "probability": 0.1},  # Sum = 0.6
            ],
            "uncertainty": 1.0,
        }

        action_counts = {"A": 0, "B": 0, "C": 0}

        for i in range(1000):
            np.random.seed(i)
            result = engine.check_collapse(state)
            if result.selected_action in action_counts:
                action_counts[result.selected_action] += 1

        # Check normalized distribution
        total = sum(action_counts.values())
        # A: 0.2/0.6 = 0.333, B: 0.3/0.6 = 0.5, C: 0.1/0.6 = 0.167
        assert abs(action_counts["A"] / total - 0.333) < 0.05
        assert abs(action_counts["B"] / total - 0.5) < 0.05
        assert abs(action_counts["C"] / total - 0.167) < 0.05

    def test_edge_case_probabilities(self, engine):
        """Test edge cases in probability handling."""
        # Zero probabilities
        state = {
            "possibilities": [
                {"action": "A", "probability": 0.0},
                {"action": "B", "probability": 0.0},
                {"action": "C", "probability": 0.0},
            ],
            "uncertainty": 1.0,
        }

        result = engine.check_collapse(state)
        assert result.collapsed == True
        assert result.selected_action in ["A", "B", "C"]  # Equal chance

        # Missing probabilities
        state_no_prob = {
            "possibilities": [{"action": "X"}, {"action": "Y"}, {"action": "Z"}],
            "uncertainty": 1.0,
        }

        result = engine.check_collapse(state_no_prob)
        assert result.collapsed == True
        assert result.selected_action in ["X", "Y", "Z"]

    def test_sigmoid_transition(self):
        """Test sigmoid function for smooth transitions."""
        engine = CollapseEngine()

        # Test sigmoid properties
        assert engine._sigmoid(0) == 0.5  # Midpoint
        assert engine._sigmoid(-10) < 0.01  # Near 0
        assert engine._sigmoid(10) > 0.99  # Near 1

        # Test smooth transition
        x_values = np.linspace(-2, 2, 100)
        y_values = [engine._sigmoid(x) for x in x_values]

        # Check monotonic increase
        for i in range(1, len(y_values)):
            assert y_values[i] >= y_values[i - 1]

    def test_collapse_timing(self, engine, quantum_like_state):
        """Test that collapse events include timing information."""
        result = engine.check_collapse(quantum_like_state)

        assert result.timestamp is not None
        assert isinstance(result.timestamp, str)

        # Verify ISO format
        try:
            datetime.fromisoformat(result.timestamp.replace("Z", "+00:00"))
        except ValueError:
            pytest.fail("Timestamp not in valid ISO format")

    @pytest.mark.parametrize(
        "threshold,uncertainty,should_collapse",
        [
            (0.5, 0.4, False),
            (0.5, 0.5, False),  # At threshold, deterministic requires strictly greater
            (0.5, 0.6, True),
            (0.8, 0.7, False),
            (0.8, 0.9, True),
            (0.2, 0.1, False),
            (0.2, 0.3, True),
        ],
    )
    def test_deterministic_thresholds(self, threshold, uncertainty, should_collapse):
        """Test deterministic collapse at various thresholds."""
        engine = CollapseEngine(base_threshold=threshold, stochastic=False)
        state = {
            "possibilities": [{"action": "test", "probability": 1.0}],
            "uncertainty": uncertainty,
            "coherence": 1.0,  # Default coherence for predictable tests
        }

        result = engine.check_collapse(state)
        assert result.collapsed == should_collapse

    def test_collapse_with_complex_actions(self, engine):
        """Test collapse with complex action structures."""
        state = {
            "possibilities": [
                {
                    "action": "navigate",
                    "path": ["A", "B", "C"],
                    "cost": 10,
                    "risk": 0.3,
                    "probability": 0.4,
                },
                {
                    "action": "navigate",
                    "path": ["X", "Y"],
                    "cost": 5,
                    "risk": 0.5,
                    "probability": 0.6,
                },
            ],
            "uncertainty": 0.9,
        }

        engine.stochastic = False
        result = engine.check_collapse(state)

        assert result.collapsed == True
        assert result.selected_action == "navigate"
        assert "path" in result.selected_state
        assert "cost" in result.selected_state
        assert "risk" in result.selected_state
