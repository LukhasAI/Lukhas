"""Smoke test for Quantum Decision Superposition feature.

Quick sanity check that quantum decision functionality is working.
"""

import pytest
from core.consciousness.bridge import (
    DecisionMakingBridge,
    QuantumDecisionEngine,
    UtilityMaximizationStrategy,
)


def test_quantum_decision_basic_smoke():
    """Basic smoke test for quantum decision functionality."""
    # Create engine
    engine = QuantumDecisionEngine()

    # Create strategies
    strategies = [UtilityMaximizationStrategy()]

    # Create superposition
    state = engine.create_superposition(strategies)

    # Verify superposition created
    assert state is not None
    assert len(state.strategies) == 1

    # Verify can collapse
    chosen, confidence = state.measure()
    assert chosen is not None
    assert 0.0 <= confidence <= 1.0


def test_quantum_bridge_integration_smoke():
    """Smoke test for quantum integration with DecisionMakingBridge."""
    bridge = DecisionMakingBridge()

    strategies = [UtilityMaximizationStrategy()]
    context = {"ethical_alignment": {}, "risk_level": {}}

    # Should not crash
    chosen_strategy, confidence, metadata = bridge.evaluate_with_quantum_superposition(
        decision_id="smoke_test", strategies=strategies, context=context
    )

    assert chosen_strategy is not None
    assert 0.0 <= confidence <= 1.0
    assert "parallel_evaluation" in metadata


if __name__ == "__main__":
    # Allow running smoke tests directly
    test_quantum_decision_basic_smoke()
    test_quantum_bridge_integration_smoke()
    print("✅ All quantum decision smoke tests passed!")
