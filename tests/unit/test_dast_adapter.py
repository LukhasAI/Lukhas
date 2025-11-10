from __future__ import annotations

from typing import Any

import pytest

from lukhas.adapters.dast_adapter import DASTAdapter, DASTOrchestrator


class _RecordingOrchestrator:
    def __init__(self, response: dict[str, Any]) -> None:
        self._response = response
        self.messages: list[dict[str, Any]] = []

    def dispatch(self, message: dict[str, Any]) -> dict[str, Any]:  # pragma: no cover - Protocol compatibility
        self.messages.append(message)
        return self._response


class _InvalidResponseOrchestrator:
    def dispatch(self, message: dict[str, Any]) -> dict[str, Any]:  # pragma: no cover - Protocol compatibility
        return {}


def test_send_task_merges_metadata() -> None:
    orchestrator = _RecordingOrchestrator(
        {"task_id": "task-123", "status": "accepted", "result": {"accepted": True}}
    )
    adapter = DASTAdapter(orchestrator, default_metadata={"channel": "dast", "priority": 1})

    result = adapter.send_task(
        {
            "task_id": "task-123",
            "payload": {"action": "scan"},
            "metadata": {"priority": 2, "labels": ["eqnox"]},
        }
    )

    assert orchestrator.messages[0]["metadata"] == {
        "channel": "dast",
        "priority": 2,
        "labels": ["eqnox"],
    }
    assert result == {
        "task_id": "task-123",
        "status": "accepted",
        "result": {"accepted": True},
    }


def test_send_task_requires_identifiers() -> None:
    orchestrator: DASTOrchestrator = _RecordingOrchestrator({"task_id": "x", "status": "ok"})
    adapter = DASTAdapter(orchestrator)

    with pytest.raises(ValueError):
        adapter.send_task({"payload": {}})

    with pytest.raises(ValueError):
        adapter.send_task({"task_id": "missing-payload"})


def test_send_task_validates_response_payload() -> None:
    adapter = DASTAdapter(_InvalidResponseOrchestrator())

    with pytest.raises(ValueError):
        adapter.send_task({"task_id": "task-42", "payload": {}})
