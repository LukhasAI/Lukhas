# tests/orchestration/test_arbitration.py
from labs.core.orchestration.consensus_arbitrator import Proposal, choose


def test_arbitration_ethics_gate():
    p1 = Proposal(id="safe", confidence=0.7, ts=0.0, ethics_risk=0.1, role_weight=0.5)
    p2 = Proposal(id="risky", confidence=0.9, ts=0.0, ethics_risk=0.95, role_weight=0.5)
    winner, rationale = choose([p1, p2])
    assert winner.id == "safe"
    assert any(pid == "safe" for pid, _ in rationale["ranking"])
