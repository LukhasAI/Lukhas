from typing import Any

try:
    from labs.core.event_bus import EventBus
except ImportError:
    # Fallback if EventBus not available
    class EventBus:
        """Placeholder EventBus"""
        def __init__(self):
            pass

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

# Import EventBus type
try:
    from system.common.event_bus import EventBus
except ImportError:
    try:
        from core.event_bus import EventBus
    except ImportError:
        # Fallback type annotation
        from typing import Any
        EventBus = Any

router = APIRouter()


def get_event_bus(request: Request) -> EventBus:
    return request.app.state.event_bus


class CapabilityAnnouncement(BaseModel):
    agent_id: str
    capability: dict[str, Any]


class TaskAnnouncement(BaseModel):
    agent_id: str
task: dict[str, Any]


@router.post("/announce-task")
async def announce_task(payload: TaskAnnouncement, bus: EventBus = Depends(get_event_bus)) -> dict[str, Any]:  # TODO[T4-ISSUE]: {"code":"B008","ticket":"GH-1031","owner":"matriz-team","status":"accepted","reason":"FastAPI dependency injection - Depends() in route parameters is required pattern","estimate":"0h","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_core_interfaces_api_v1_v1_rest_routers_tasks_py_L44"}
    bus.announce_task(payload.model_dump())
    return {"status": "announced"}


@router.post("/announce-capability")
async def announce_capability(
payload: CapabilityAnnouncement, bus: EventBus = Depends(get_event_bus)  # TODO[T4-ISSUE]: {"code":"B008","ticket":"GH-1031","owner":"matriz-team","status":"accepted","reason":"FastAPI dependency injection - Depends() in route parameters is required pattern","estimate":"0h","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_core_interfaces_api_v1_v1_rest_routers_tasks_py_L51"}
) -> dict[str, Any]:
    bus.announce_capability(payload.agent_id, payload.capability)
    return {"status": "registered"}
