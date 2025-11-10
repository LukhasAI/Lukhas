from __future__ import annotations

from typing import Annotated, Any

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from lukhas.adapters.dast_adapter import DASTAdapter, DASTOrchestrator

app = FastAPI()


def get_orchestrator() -> DASTOrchestrator:
    raise RuntimeError("dependency override required for orchestrator")


OrchestratorDep = Annotated[DASTOrchestrator, Depends(get_orchestrator)]


def get_adapter(orchestrator: OrchestratorDep) -> DASTAdapter:
    return DASTAdapter(orchestrator, default_metadata={"channel": "eqnox"})


AdapterDep = Annotated[DASTAdapter, Depends(get_adapter)]


@app.post("/tasks")
def send_task_endpoint(
    task: dict[str, Any],
    adapter: AdapterDep,
) -> dict[str, Any]:
    return adapter.send_task(task)


def test_dependency_override_for_dast_adapter() -> None:
    class _OverridableOrchestrator:
        def __init__(self) -> None:
            self.dispatched: list[dict[str, Any]] = []

        def dispatch(self, message: dict[str, Any]) -> dict[str, Any]:  # pragma: no cover - Protocol compatibility
            self.dispatched.append(message)
            return {
                "task_id": message["task_id"],
                "status": "queued",
                "metadata": {"received_by": "integration"},
            }

    orchestrator = _OverridableOrchestrator()
    app.dependency_overrides[get_orchestrator] = lambda: orchestrator

    client = TestClient(app)
    try:
        response = client.post(
            "/tasks",
            json={"task_id": "integration-1", "payload": {"kind": "scan"}},
        )
    finally:
        app.dependency_overrides = {}

    assert response.status_code == 200
    assert response.json() == {
        "task_id": "integration-1",
        "status": "queued",
        "metadata": {"received_by": "integration"},
    }
    assert orchestrator.dispatched[0]["metadata"] == {"channel": "eqnox"}
