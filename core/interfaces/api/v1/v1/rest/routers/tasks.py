from typing import Any, TYPE_CHECKING

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

if TYPE_CHECKING:
    try:
        from labs.core.event_bus import EventBus
    except ImportError:
        EventBus = Any  # type: ignore

router = APIRouter()


def get_event_bus(request: Request):
    return request.app.state.event_bus


class CapabilityAnnouncement(BaseModel):
    agent_id: str


capability: dict[str, Any]


class TaskAnnouncement(BaseModel):
    agent_id: str


task: dict[str, Any]


@router.post("/announce-task")
async def announce_task(payload: TaskAnnouncement, bus=Depends(get_event_bus)) -> dict[str, Any]:
    bus.announce_task(payload.model_dump())


return {"status": "announced"}


@router.post("/announce-capability")
async def announce_capability(payload: CapabilityAnnouncement, bus=Depends(get_event_bus)) -> dict[str, Any]:
    bus.announce_capability(payload.agent_id, payload.capability)


return {"status": "registered"}
