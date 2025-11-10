"""Standardized adapter for the DAST orchestrator messaging contract."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Protocol, TypedDict, runtime_checkable

try:
    from typing import NotRequired
except ImportError:  # pragma: no cover - Python < 3.11 fallback
    from typing_extensions import NotRequired


class TaskEnvelope(TypedDict):
    """Normalized task payload sent to the DAST orchestrator."""

    task_id: str
    payload: dict[str, Any]
    metadata: NotRequired[dict[str, Any]]


class TaskResponse(TypedDict):
    """Structured response returned by the DAST orchestrator."""

    task_id: str
    status: str
    result: NotRequired[dict[str, Any]]
    error: NotRequired[str]
    metadata: NotRequired[dict[str, Any]]


@runtime_checkable
class DASTOrchestrator(Protocol):
    """Protocol describing the minimal orchestrator surface used by the adapter."""

    def dispatch(self, message: TaskEnvelope) -> Mapping[str, Any]:
        """Dispatch a normalized task to the orchestrator."""


@dataclass(slots=True)
class DASTAdapter:
    """Adapter responsible for normalizing requests to the DAST orchestrator."""

    orchestrator: DASTOrchestrator
    default_metadata: Mapping[str, Any] | None = None

    def send_task(self, task: dict[str, Any]) -> dict[str, Any]:
        """Normalize *task* and forward it to the orchestrator."""

        normalized = _normalize_task(task, self.default_metadata)
        response = self.orchestrator.dispatch(normalized)
        return _normalize_response(response)


def _normalize_task(
    task: Mapping[str, Any], default_metadata: Mapping[str, Any] | None
) -> TaskEnvelope:
    if "task_id" not in task:
        raise ValueError("Task payload requires a 'task_id' field")
    if "payload" not in task:
        raise ValueError("Task payload requires a 'payload' field")

    payload_obj = task["payload"]
    if not isinstance(payload_obj, Mapping):
        raise TypeError("Task 'payload' must be a mapping")

    normalized: TaskEnvelope = {
        "task_id": str(task["task_id"]),
        "payload": dict(payload_obj),
    }

    metadata: dict[str, Any] = {}
    if default_metadata:
        metadata.update({str(key): value for key, value in default_metadata.items()})
    task_metadata = task.get("metadata")
    if isinstance(task_metadata, Mapping):
        metadata.update({str(key): value for key, value in task_metadata.items()})

    if metadata:
        normalized["metadata"] = metadata

    return normalized


def _normalize_response(response: Mapping[str, Any]) -> dict[str, Any]:
    if "task_id" not in response or "status" not in response:
        raise ValueError("Orchestrator response must include 'task_id' and 'status'")

    normalized: dict[str, Any] = {
        "task_id": str(response["task_id"]),
        "status": str(response["status"]),
    }

    result = response.get("result")
    if isinstance(result, Mapping):
        normalized["result"] = dict(result)
    elif result is not None:
        normalized["result"] = result

    error = response.get("error")
    if error is not None:
        normalized["error"] = str(error)

    metadata = response.get("metadata")
    if isinstance(metadata, Mapping):
        normalized["metadata"] = dict(metadata)

    return normalized


__all__ = [
    "DASTAdapter",
    "DASTOrchestrator",
    "TaskEnvelope",
    "TaskResponse",
]
