import os
from typing import Dict, Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

router = APIRouter()

class DreamRequest(BaseModel):
    seed: Optional[str] = None
    constraints: Optional[Dict] = None

def require_api_key(x_api_key: str = Header(...)):
    if x_api_key != os.getenv("LUKHAS_API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid API Key")

@router.post("/v1/dreams", dependencies=[Depends(require_api_key)])
async def dreams(request: DreamRequest):
    return {
        "id": "dream_12345",
        "traces": [
            {"step": 1, "content": f"quantum superposition based on seed: {request.seed}"},
            {"step": 2, "content": "lucid dream"},
            {"step": 3, "content": "ocean waves"}
        ],
        "model": "lukhas-consciousness",
        "seed": request.seed,
        "constraints": request.constraints
    }
