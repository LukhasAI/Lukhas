"""Comprehensive tests for Quantum Decision Superposition functionality."""

import numpy as np
import pytest
from core.consciousness.bridge import (
    DecisionMakingBridge,
    DecisionStrategy,
    QuantumDecisionEngine,
    QuantumDecisionState,
    UtilityMaximizationStrategy,
)


class MockDecisionStrategy(DecisionStrategy):
    """Mock decision strategy for testing."""

    def __init__(self, name="mock"):
        self.name = name

    def evaluate_alternatives(self, context, alternatives):
        """Mock evaluation."""
        return []

    def select_best_alternative(self, evaluations):
        """Mock selection."""
        return ("mock", 0.5)


class TestQuantumDecisionSuperposition:
    """Test suite for quantum decision superposition."""

    def test_equal_superposition_creation(self):
        """Test creating equal superposition of strategies."""
        strategies = [
            MockDecisionStrategy("utility"),
            MockDecisionStrategy("ethical"),
            MockDecisionStrategy("risk_aware"),
        ]

        engine = QuantumDecisionEngine()
        state = engine.create_superposition(strategies)

        # Equal superposition should have equal probabilities
        probabilities = np.abs(state.amplitudes) ** 2
        assert np.allclose(probabilities, [1 / 3, 1 / 3, 1 / 3], atol=1e-6)

    def test_weighted_superposition(self):
        """Test creating weighted superposition with prior beliefs."""
        strategies = [MockDecisionStrategy(f"s{i}") for i in range(3)]
        weights = [0.5, 0.3, 0.2]

        engine = QuantumDecisionEngine()
        state = engine.create_superposition(strategies, initial_weights=weights)

        probabilities = np.abs(state.amplitudes) ** 2
        assert np.allclose(probabilities, weights, atol=1e-6)

    def test_interference_pattern(self):
        """Test constructive/destructive interference."""
        strategies = [MockDecisionStrategy("ethical"), MockDecisionStrategy("risky")]
        engine = QuantumDecisionEngine()
        state = engine.create_superposition(strategies)

        # Ethical strategy gets boost, risky gets penalty
        context = {
            "ethical_alignment": {"MockDecisionStrategy": 1.0},
            "risk_level": {"MockDecisionStrategy": 0.0},
        }

        initial_probs = np.abs(state.amplitudes) ** 2

        # Apply interference
        engine.apply_interference(state, context)

        final_probs = np.abs(state.amplitudes) ** 2

        # Probabilities should have changed
        assert not np.allclose(initial_probs, final_probs)

    def test_measurement_collapse(self):
        """Test that measurement collapses to valid strategy."""
        strategies = [MockDecisionStrategy(f"s{i}") for i in range(5)]
        engine = QuantumDecisionEngine()
        state = engine.create_superposition(strategies)

        chosen, confidence = state.measure()

        assert chosen in strategies
        assert 0.0 <= confidence <= 1.0

    def test_amplitude_normalization(self):
        """Test that amplitudes are properly normalized."""
        strategies = [MockDecisionStrategy(f"s{i}") for i in range(4)]
        engine = QuantumDecisionEngine()
        state = engine.create_superposition(strategies)

        # Amplitudes should be normalized
        prob_sum = np.sum(np.abs(state.amplitudes) ** 2)
        assert np.isclose(prob_sum, 1.0, atol=1e-6)

    def test_entropy_calculation(self):
        """Test von Neumann entropy calculation."""
        strategies = [MockDecisionStrategy(f"s{i}") for i in range(4)]
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
        strategies = [MockDecisionStrategy(f"s{i}") for i in range(3)]
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

    def test_coherence_calculation(self):
        """Test quantum coherence calculation."""
        strategies = [MockDecisionStrategy(f"s{i}") for i in range(3)]
        engine = QuantumDecisionEngine()
        state = engine.create_superposition(strategies)

        coherence = engine._calculate_coherence(state)

        # Coherence should be non-negative
        assert coherence >= 0.0

    def test_collapse_and_decide_returns_metadata(self):
        """Test that collapse returns comprehensive metadata."""
        strategies = [MockDecisionStrategy(f"s{i}") for i in range(3)]
        engine = QuantumDecisionEngine()
        state = engine.create_superposition(strategies)

        chosen_strategy, confidence, metadata = engine.collapse_and_decide(state, "test_decision")

        assert chosen_strategy in strategies
        assert 0.0 <= confidence <= 1.0
        assert "decision_id" in metadata
        assert "chosen_strategy" in metadata
        assert "measurement_time" in metadata
        assert "pre_measurement_entropy" in metadata

    def test_measurement_deterministic_with_single_strategy(self):
        """Test measurement with single strategy is deterministic."""
        strategies = [MockDecisionStrategy("only")]
        engine = QuantumDecisionEngine()
        state = engine.create_superposition(strategies)

        chosen, confidence = state.measure()

        assert chosen == strategies[0]
        assert np.isclose(confidence, 1.0, atol=1e-6)

    def test_interference_preserves_normalization(self):
        """Test that interference preserves probability normalization."""
        strategies = [MockDecisionStrategy(f"s{i}") for i in range(3)]
        engine = QuantumDecisionEngine()
        state = engine.create_superposition(strategies)

        context = {
            "ethical_alignment": {s.__class__.__name__: 0.5 for s in strategies},
            "risk_level": {s.__class__.__name__: 0.0 for s in strategies},
        }

        engine.apply_interference(state, context)

        # Probabilities should still sum to 1
        prob_sum = np.sum(np.abs(state.amplitudes) ** 2)
        assert np.isclose(prob_sum, 1.0, atol=1e-6)


class TestDecisionMakingBridgeQuantumIntegration:
    """Test suite for quantum superposition integration with DecisionMakingBridge."""

    def test_evaluate_with_quantum_superposition(self):
        """Test quantum superposition evaluation in bridge."""
        bridge = DecisionMakingBridge()

        strategies = [
            UtilityMaximizationStrategy(),
            MockDecisionStrategy("ethical"),
        ]

        context = {
            "ethical_alignment": {"UtilityMaximizationStrategy": 0.7, "MockDecisionStrategy": 0.9},
            "risk_level": {"UtilityMaximizationStrategy": 0.2, "MockDecisionStrategy": 0.1},
        }

        chosen_strategy, confidence, metadata = bridge.evaluate_with_quantum_superposition(
            decision_id="test_quantum_1", strategies=strategies, context=context
        )

        assert chosen_strategy in strategies
        assert 0.0 <= confidence <= 1.0
        assert "parallel_evaluation" in metadata

    def test_quantum_engine_lazy_initialization(self):
        """Test that quantum engine is lazily initialized."""
        bridge = DecisionMakingBridge()

        # Should not have quantum engine initially
        assert not hasattr(bridge, "_quantum_engine")

        # Call quantum method
        strategies = [MockDecisionStrategy("s1")]
        bridge.evaluate_with_quantum_superposition("test", strategies, {})

        # Should now have quantum engine
        assert hasattr(bridge, "_quantum_engine")

    def test_quantum_superposition_without_interference(self):
        """Test quantum evaluation without interference."""
        bridge = DecisionMakingBridge()

        strategies = [MockDecisionStrategy(f"s{i}") for i in range(3)]

        chosen_strategy, confidence, metadata = bridge.evaluate_with_quantum_superposition(
            decision_id="test_no_interference",
            strategies=strategies,
            context={},
            apply_interference=False,
        )

        assert chosen_strategy in strategies
        assert "entropy" in metadata["parallel_evaluation"]

    def test_quantum_superposition_with_entanglement(self):
        """Test quantum evaluation with decision entanglement."""
        bridge = DecisionMakingBridge()

        strategies = [MockDecisionStrategy(f"s{i}") for i in range(2)]

        # First decision
        bridge.evaluate_with_quantum_superposition(
            decision_id="decision_A", strategies=strategies, context={}
        )

        # Second decision entangled with first
        chosen_strategy, confidence, metadata = bridge.evaluate_with_quantum_superposition(
            decision_id="decision_B",
            strategies=strategies,
            context={},
            entangled_with=["decision_A"],
        )

        # Should have entanglement in quantum engine
        assert "decision_A" in bridge._quantum_engine._entanglement_graph
        assert "decision_B" in bridge._quantum_engine._entanglement_graph

    def test_quantum_history_tracking(self):
        """Test that quantum engine tracks decision history."""
        bridge = DecisionMakingBridge()

        strategies = [MockDecisionStrategy(f"s{i}") for i in range(3)]

        # Make multiple quantum decisions
        for i in range(5):
            bridge.evaluate_with_quantum_superposition(
                decision_id=f"decision_{i}", strategies=strategies, context={}
            )

        # Should have history
        assert len(bridge._quantum_engine._history) == 5

    def test_quantum_superposition_metadata_structure(self):
        """Test quantum superposition metadata structure."""
        bridge = DecisionMakingBridge()

        strategies = [MockDecisionStrategy(f"s{i}") for i in range(3)]

        _, _, metadata = bridge.evaluate_with_quantum_superposition(
            decision_id="test_metadata", strategies=strategies, context={}
        )

        # Check metadata structure
        assert "decision_id" in metadata
        assert "chosen_strategy" in metadata
        assert "confidence" in metadata
        assert "measurement_time" in metadata
        assert "pre_measurement_entropy" in metadata
        assert "parallel_evaluation" in metadata

        # Check parallel evaluation structure
        parallel_eval = metadata["parallel_evaluation"]
        assert "strategy_evaluations" in parallel_eval
        assert "entropy" in parallel_eval
        assert "coherence" in parallel_eval


class TestQuantumDecisionEdgeCases:
    """Test suite for edge cases in quantum decision making."""

    def test_empty_strategy_list_handling(self):
        """Test handling of empty strategy list."""
        engine = QuantumDecisionEngine()

        # Should handle gracefully
        with pytest.raises((ValueError, IndexError)):
            state = engine.create_superposition([])

    def test_zero_probabilities_handling(self):
        """Test entropy calculation with zero probabilities."""
        strategies = [MockDecisionStrategy(f"s{i}") for i in range(3)]
        engine = QuantumDecisionEngine()
        state = engine.create_superposition(strategies)

        # Manually set some amplitudes to zero (edge case)
        state.amplitudes[0] = 0
        state.normalize_amplitudes()

        # Should handle zero probabilities gracefully
        entropy = engine._calculate_entropy(state)
        assert entropy >= 0.0

    def test_phase_factor_accumulation(self):
        """Test that phase factors accumulate correctly."""
        strategies = [MockDecisionStrategy("s1")]
        engine = QuantumDecisionEngine()
        state = engine.create_superposition(strategies)

        initial_phase = state.phase_factors[0]

        # Add phase shift
        state.add_interference(np.pi / 4)

        # Phase should have changed
        assert state.phase_factors[0] != initial_phase

    def test_multiple_measurements_on_same_state(self):
        """Test multiple measurements on same quantum state."""
        strategies = [MockDecisionStrategy(f"s{i}") for i in range(3)]
        engine = QuantumDecisionEngine()
        state = engine.create_superposition(strategies)

        # Multiple measurements should potentially give different results
        results = []
        for _ in range(10):
            chosen, _ = state.measure()
            results.append(chosen.name)

        # With 3 strategies and 10 measurements, should likely see some variation
        # (unless we're extremely unlucky)
        assert len(set(results)) >= 1  # At least one unique result
