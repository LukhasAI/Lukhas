from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from candidate.core.swarm import SwarmHub

# TAG:bridge
# TAG:api
# TAG:neuroplastic
# TAG:colony

router = APIRouter(prefix="/colonies", tags=["colonies"])


class ColonySpawnRequest(BaseModel):
    colony_type: str
    size: int
    capabilities: Optional[list[str]] = None
    config: Optional[dict[str, Any]] = None


class ColonyTaskRequest(BaseModel):
    task_type: str
    payload: dict[str, Any]
    timeout: Optional[float] = 30.0


@router.post("/spawn")
async def spawn_colony(request: ColonySpawnRequest):
    try:
        swarm = SwarmHub()
        if request.colony_type == "reasoning":
            from candidate.core.colonies.reasoning_colony import ReasoningColony

            colony = ReasoningColony(f"dynamic-reasoning-{datetime.now().timestamp()}")
        else:
            raise ValueError("Unknown colony type")
        await colony.start()
        swarm.register_colony(colony.colony_id, "auto")
        return {"colony_id": colony.colony_id, "status": "active"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{colony_id}")
async def terminate_colony(colony_id: str):
    try:
        swarm = SwarmHub()
        colony = swarm.get_colony(colony_id)
        if not colony:
            raise HTTPException(status_code=404, detail="Colony not found")
        await colony.stop()
        return {"colony_id": colony_id, "status": "terminated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
