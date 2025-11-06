import pytest
from datetime import datetime, timezone
from core.colonies.ethics_swarm_colony import (
    EthicalDecisionRequest,
    EthicalDecisionType,
    EthicalSignal,
    EthicsSwarmColony,
)


def test_ethical_decision_request_creation():
    """Test EthicalDecisionRequest dataclass initialization."""
    request = EthicalDecisionRequest(
        agent_id="test_agent",
        decision_type=EthicalDecisionType.ESCALATED,
        context={"risk": "high"},
    )
    assert request.agent_id == "test_agent"
    assert request.decision_type == EthicalDecisionType.ESCALATED
    assert request.context == {"risk": "high"}
    assert isinstance(request.timestamp, datetime)
    assert request.request_id is not None


def test_ethical_signal_creation():
    """Test EthicalSignal dataclass initialization."""
    signal = EthicalSignal(
        source="test_source", value=0.7, weight=1.5, tags={"test"}
    )
    assert signal.source == "test_source"
    assert signal.value == 0.7
    assert signal.weight == 1.5
    assert signal.tags == {"test"}
    assert isinstance(signal.timestamp, datetime)


def test_ethics_swarm_colony_initialization():
    """Test EthicsSwarmColony initialization."""
    colony = EthicsSwarmColony(max_history=100, drift_threshold=0.7, escalation_penalty=0.1)
    assert colony.drift_threshold == 0.7
    assert colony.escalation_penalty == 0.1
    assert len(colony.recent_signals()) == 0


def test_ethics_swarm_colony_register_signal():
    """Test signal registration and normalization."""
    colony = EthicsSwarmColony()
    colony.register_signal(EthicalSignal(source="s1", value=0.8))
    colony.register_signal(EthicalSignal(source="s2", value=1.2))  # Should be capped at 1.0
    colony.register_signal(EthicalSignal(source="s3", value=-0.1)) # Should be capped at 0.0

    signals = colony.recent_signals()
    assert len(signals) == 3
    assert signals[0].value == 0.8
    assert signals[1].value == 1.0
    assert signals[2].value == 0.0


def test_ethics_swarm_colony_evaluate_decision_approved():
    """Test a decision evaluation that should be approved."""
    colony = EthicsSwarmColony(drift_threshold=0.8)
    colony.register_signal(EthicalSignal(source="s1", value=0.6, weight=1.0))
    colony.register_signal(EthicalSignal(source="s2", value=0.7, weight=1.0))

    request = EthicalDecisionRequest(agent_id="test_agent")
    response = colony.evaluate_decision(request)

    assert response.approved
    assert response.reason == "guardian aligned"
    assert response.drift_score == pytest.approx(0.65)


def test_ethics_swarm_colony_evaluate_decision_denied():
    """Test a decision evaluation that should be denied due to high drift."""
    colony = EthicsSwarmColony(drift_threshold=0.5)
    colony.register_signal(EthicalSignal(source="s1", value=0.8, weight=1.0))
    colony.register_signal(EthicalSignal(source="s2", value=0.9, weight=1.0))

    request = EthicalDecisionRequest(agent_id="test_agent")
    response = colony.evaluate_decision(request)

    assert not response.approved
    assert "drift threshold exceeded" in response.reason
    assert response.drift_score == pytest.approx(0.85)


def test_ethics_swarm_colony_decision_floor_logic():
    """Test the logic for calculating the decision floor."""
    colony = EthicsSwarmColony(drift_threshold=0.7, escalation_penalty=0.1)

    # Standard decision
    assert colony._decision_floor(EthicalDecisionType.STANDARD, "normal") == 0.7

    # Escalated decision
    assert colony._decision_floor(EthicalDecisionType.ESCALATED, "normal") == pytest.approx(0.6)

    # Emergency decision
    assert colony._decision_floor(EthicalDecisionType.EMERGENCY, "normal") == pytest.approx(0.5)

    # High risk
    assert colony._decision_floor(EthicalDecisionType.STANDARD, "high") == pytest.approx(0.65)

    # Critical risk
    assert colony._decision_floor(EthicalDecisionType.STANDARD, "critical") == pytest.approx(0.65)

    # Emergency risk
    assert colony._decision_floor(EthicalDecisionType.STANDARD, "emergency") == pytest.approx(0.6)


def test_ethics_swarm_colony_clear():
    """Test clearing the internal state of the colony."""
    colony = EthicsSwarmColony()
    colony.register_signal(EthicalSignal(source="s1", value=0.5))
    assert len(colony.recent_signals()) == 1
    colony.clear()
    assert len(colony.recent_signals()) == 0


def test_evaluate_decision_with_no_signals():
    """Test decision evaluation with no signals registered."""
    colony = EthicsSwarmColony()
    request = EthicalDecisionRequest(agent_id="test_agent")
    response = colony.evaluate_decision(request)
    assert response.approved
    assert response.drift_score == 0.0

def test_calculate_affect_delta_no_signals():
    """Test affect delta calculation with no signals."""
    colony = EthicsSwarmColony()
    assert colony._calculate_affect_delta() == 0.0

def test_decision_floor_risk_levels():
    """Test decision floor adjustments for different risk levels."""
    colony = EthicsSwarmColony(drift_threshold=0.8)
    assert colony._decision_floor(EthicalDecisionType.STANDARD, "high") < 0.8
    assert colony._decision_floor(EthicalDecisionType.STANDARD, "critical") < 0.8
    assert colony._decision_floor(EthicalDecisionType.STANDARD, "emergency") < 0.8
