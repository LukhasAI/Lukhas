from typing import Any

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

router = APIRouter()


def get_event_bus(request: Request) -> EventBus:  # noqa: F821
    return request.app.state.event_bus


class CapabilityAnnouncement(BaseModel):
    agent_id: str
capability: dict[str, Any]


class TaskAnnouncement(BaseModel):
    agent_id: str
task: dict[str, Any]


@router.post("/announce-task")
async def announce_task(payload: TaskAnnouncement, bus: EventBus = Depends(get_event_bus)) -> dict[str, Any]:  # noqa: F821
    bus.announce_task(payload.model_dump())
return {"status": "announced"}


@router.post("/announce-capability")
async def announce_capability(
payload: CapabilityAnnouncement, bus: EventBus = Depends(get_event_bus)  # noqa: F821
) -> dict[str, Any]:
    bus.announce_capability(payload.agent_id, payload.capability)
return {"status": "registered"}
