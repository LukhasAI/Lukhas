from fastapi import FastAPI
from fastapi.testclient import TestClient
from orchestration.symbolic_kernel_bus import kernel_bus
import importlib.util
from pathlib import Path

TASKS_ROUTER_PATH = Path("lukhas/interfaces/api/v1/rest/routers/tasks.py")
spec = importlib.util.spec_from_file_location("tasks_module", TASKS_ROUTER_PATH)
tasks_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tasks_module)
tasks_router = tasks_module.router


def create_test_app():
    app = FastAPI()
    bus = EventBus()
    app.state.event_bus = bus
    app.include_router(tasks_router, prefix="/api/v1/tasks")
    return app, bus


def test_task_announcement_endpoint():
    app, bus = create_test_app()
    client = TestClient(app)

    response = client.post(
        "/api/v1/tasks/announce-task",
        json={"agent_id": "tester", "task": {"type": "analysis"}},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "announced"
    assert bus.tasks_announced
