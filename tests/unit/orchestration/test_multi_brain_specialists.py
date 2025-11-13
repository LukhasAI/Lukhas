"""Unit tests for MultiBrain specialist coordination."""

from __future__ import annotations

from datetime import datetime
from typing import Dict, Optional

import pytest
from core.orchestration.brain.integration.brain_integration import MultiBrain


class DummySpecialist:
    def __init__(self, name: str):
        self.name = name
        self.messages = []

    def handle_message(self, message: Dict, origin: Optional[str] = None):
        self.messages.append((message, origin, datetime.now()))
        return {"handled_by": self.name, "origin": origin}


def test_multibrain_register_and_metrics():
    multi_brain = MultiBrain()
    specialist_id = multi_brain.register_specialist(
        "symbolic",
        DummySpecialist("symbolic"),
        capabilities={"reasoning", "symbolic"},
    )

    multi_brain.update_specialist_metrics(
        specialist_id,
        latency_ms=12.5,
        throughput=4.0,
        accuracy=0.92,
        drift_score=0.1,
        affect_delta=0.02,
        collapse_hash="abc123",
    )

    snapshot = multi_brain.get_specialist_snapshot(specialist_id)
    assert snapshot["specialist_id"] == specialist_id
    assert pytest.approx(snapshot["avg_latency_ms"], rel=1e-3) == 12.5
    assert pytest.approx(snapshot["avg_throughput"], rel=1e-3) == 4.0
    assert pytest.approx(snapshot["avg_accuracy"], rel=1e-3) == 0.92
    assert snapshot["driftScore"] == pytest.approx(0.1)
    assert snapshot["affect_delta"] == pytest.approx(0.02)
    assert snapshot["collapseHash"] == "abc123"


def test_multibrain_routing_prefers_contextual_specialist():
    multi_brain = MultiBrain()
    sym_id = multi_brain.register_specialist(
        "symbolic",
        DummySpecialist("symbolic"),
        capabilities={"reasoning", "analysis"},
    )
    neu_id = multi_brain.register_specialist(
        "neural",
        DummySpecialist("neural"),
        capabilities={"pattern", "analysis"},
    )

    multi_brain.update_specialist_metrics(sym_id, latency_ms=25.0, accuracy=0.80, throughput=1.0)
    multi_brain.update_specialist_metrics(neu_id, latency_ms=10.0, accuracy=0.95, throughput=2.0)

    decision = multi_brain.route_task(
        {
            "type": "pattern",
            "complexity": "high",
            "context": ["pattern", "signal"],
        }
    )

    assert decision["specialist_type"] == "neural"
    assert decision["specialist_id"].startswith("neural-")

    # Completing the task should reduce load
    multi_brain.complete_task(decision["specialist_id"])
    snapshot = multi_brain.get_specialist_snapshot(decision["specialist_id"])
    assert snapshot["specialist_id"] == decision["specialist_id"]


def test_multibrain_message_passing():
    multi_brain = MultiBrain()
    symbolic = DummySpecialist("symbolic")
    neural = DummySpecialist("neural")
    multi_brain.register_specialist("symbolic", symbolic, capabilities={"reasoning"})
    multi_brain.register_specialist("neural", neural, capabilities={"pattern"})

    responses = multi_brain.broadcast_message({"topic": "synchronise"}, origin="tester")

    assert len(responses) == 2
    assert all(response["status"] == "ok" for response in responses)
    assert symbolic.messages and neural.messages

    relay_response = multi_brain.relay_between_specialists("symbolic", "neural", {"topic": "handoff"})
    assert relay_response[0]["status"] == "ok"
    assert neural.messages[-1][0]["message"]["topic"] == "handoff"
