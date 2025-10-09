"""Bridge for lukhas.orchestration.externalized_orchestrator."""

from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module

for _candidate in (
    "lukhas_website.lukhas.orchestration.externalized_orchestrator",
    "candidate.orchestration.externalized_orchestrator",
):
    try:
        _mod = import_module(_candidate)
    except Exception:
        continue
    globals().update({k: getattr(_mod, k) for k in dir(_mod) if not k.startswith("_")})
    break


@dataclass
class OrchestrationRequest:  # type: ignore[misc]
    request_id: str
    payload: dict


class RequestType:
    SYNCHRONOUS = "sync"
    ASYNCHRONOUS = "async"


class ExternalizedOrchestrator:  # type: ignore[misc]
    def execute(self, request: OrchestrationRequest) -> dict:
        return {"request_id": request.request_id, "status": "handled"}
