from __future__ import annotations

import asyncio

from bridge.examples.basic.example import simulate_governance_flow


def test_simulate_governance_flow_approves_low_risk():
    decision = asyncio.run(simulate_governance_flow("publish", risk_score=0.2, tags={"internal"}))

    assert decision.approved is True
    assert decision.route == "governance-check"
    assert decision.monitor_summary["completed_tasks"] == 1
    assert "risk and classification checks passed" in decision.reasons


def test_simulate_governance_flow_blocks_restricted():
    decision = asyncio.run(simulate_governance_flow("export", risk_score=0.3, tags={"restricted"}))

    assert decision.approved is False
    assert "restricted" in decision.reasons[0]


def test_simulate_governance_flow_blocks_high_risk():
    decision = asyncio.run(simulate_governance_flow("share", risk_score=0.95, tags={"partner"}))

    assert decision.approved is False
    assert any("risk score" in reason for reason in decision.reasons)
