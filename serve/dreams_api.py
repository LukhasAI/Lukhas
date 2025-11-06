from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
import os
from fastapi import Header

router = APIRouter()

class DreamRequest(BaseModel):
    seed: Optional[str] = None
    constraints: Optional[Dict] = None

def require_api_key(x_api_key: str = Header(...)):
    if x_api_key != os.getenv("LUKHAS_API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid API Key")

@router.post(
    "/v1/dreams",
    dependencies=[Depends(require_api_key)],
    summary="Create a new dream",
    description="This endpoint generates a new dream sequence based on an optional seed and constraints.",
    responses={
        200: {
            "description": "Dream sequence generated successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "id": "dream_12345",
                        "traces": [
                            {"step": 1, "content": "quantum superposition based on seed: example_seed"},
                            {"step": 2, "content": "lucid dream"},
                            {"step": 3, "content": "ocean waves"}
                        ],
                        "model": "lukhas-consciousness",
                        "seed": "example_seed",
                        "constraints": {"max_steps": 3}
                    }
                }
            },
        },
        401: {"description": "Invalid API Key"},
    },
)
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
