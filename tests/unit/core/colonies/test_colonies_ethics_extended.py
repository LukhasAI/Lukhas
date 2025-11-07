import pytest

from core.colonies.ethics_swarm_colony import (
    EthicalDecisionType,
    EthicsSwarmColony,
)


def test_ethics_swarm_colony_decision_floor_edge_cases():
    """Test edge cases for the decision floor logic."""
    colony = EthicsSwarmColony(drift_threshold=0.7, escalation_penalty=0.1)

    # Test with an unknown risk level, should default to 0.7
    assert colony._decision_floor(EthicalDecisionType.STANDARD, "unknown") == 0.7

    # Test with a very high escalation penalty
    colony_high_penalty = EthicsSwarmColony(drift_threshold=0.7, escalation_penalty=0.8)
    assert colony_high_penalty._decision_floor(EthicalDecisionType.ESCALATED, "normal") == 0.2
