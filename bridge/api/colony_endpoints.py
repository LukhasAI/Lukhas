from datetime import datetime
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from core.swarm import SwarmHub


#TAG:bridge
#TAG:api
#TAG:neuroplastic
#TAG:colony


router = APIRouter(prefix="/colonies", tags=["colonies"])


class ColonySpawnRequest(BaseModel):
    colony_type: str
    size: int
    capabilities: Optional[List[str]] = None
    config: Optional[Dict[str, Any]] = None


class ColonyTaskRequest(BaseModel):
    task_type: str
    payload: Dict[str, Any]
    timeout: Optional[float] = 30.0


@router.post("/spawn")
async def spawn_colony(request: ColonySpawnRequest):
    try:
        swarm = SwarmHub()
        if request.colony_type == "reasoning":
            from core.colonies.reasoning_colony import ReasoningColony
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
