"""Unit tests for the core ethics swarm colony engine."""
from __future__ import annotations

import logging

import pytest

from core.colonies import (
    EthicalDecisionRequest,
    EthicalDecisionResponse,
    EthicalDecisionType,
    EthicalSignal,
    EthicsSwarmColony,
)


@pytest.fixture()
def colony() -> EthicsSwarmColony:
    """Create a colony with deterministic thresholds for testing."""

    return EthicsSwarmColony(max_history=8, drift_threshold=0.6, escalation_penalty=0.1)


def test_swarm_colony_approves_low_risk(caplog: pytest.LogCaptureFixture, colony: EthicsSwarmColony) -> None:
    """Low risk contexts with positive signals should be approved."""

    colony.extend_signals(
        [
            EthicalSignal(source="guardian", value=0.2, weight=1.0, tags={"oversight"}),
            EthicalSignal(source="ethics", value=0.3, weight=1.5, tags={"ethics"}),
        ]
    )

    request = EthicalDecisionRequest(agent_id="guardian", context={"risk_level": "low"})

    with caplog.at_level(logging.INFO):
        response = colony.evaluate_decision(request)

    assert isinstance(response, EthicalDecisionResponse)
    assert response.approved is True
    assert 0.0 <= response.drift_score <= 1.0
    assert response.affect_delta >= 0.0
    assert len(response.collapse_hash) == 64
    assert "guardian aligned" in response.reason
    assert any(record.message == "EthicsSwarm decision" for record in caplog.records)


def test_swarm_colony_blocks_high_risk(colony: EthicsSwarmColony) -> None:
    """High risk escalated contexts should require low drift to pass."""

    colony.extend_signals(
        [
            EthicalSignal(source="monitor", value=0.9, weight=1.0),
            EthicalSignal(source="compliance", value=0.85, weight=1.2),
        ]
    )

    request = EthicalDecisionRequest(
        agent_id="guardian",
        decision_type=EthicalDecisionType.ESCALATED,
        context={"risk_level": "critical"},
    )

    response = colony.evaluate_decision(request)

    assert response.approved is False
    assert response.drift_score > response.diagnostics["decision_floor"]
    assert "drift threshold exceeded" in response.reason
    assert response.affect_delta > 0.0


def test_swarm_colony_signal_normalisation(colony: EthicsSwarmColony) -> None:
    """Signals outside the expected range are clamped for stability."""

    colony.register_signal(EthicalSignal(source="guardian", value=5.0, weight=0.5))
    colony.register_signal(EthicalSignal(source="guardian", value=-1.0, weight=0.5))

    response = colony.evaluate_decision(EthicalDecisionRequest(agent_id="guardian"))

    assert 0.0 <= response.drift_score <= 1.0
    assert response.diagnostics["signals"][0]["value"] == 1.0
    assert response.diagnostics["signals"][1]["value"] == 0.0
