"""
LUKHAS Dreams API Endpoints
============================

Production API routes for dream simulation and parallel processing.
All endpoints are feature-flag gated (LUKHAS_DREAMS_ENABLED).

Endpoints:
- POST /api/v1/dreams/simulate - Simulate a single dream
- POST /api/v1/dreams/mesh - Run parallel dream mesh
- GET /api/v1/dreams/{dream_id} - Retrieve dream by ID
"""
# ruff: noqa: B008
import logging
import time
from typing import Any, ClassVar, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from identity.tier_system import PermissionScope, TierLevel
from lukhas_website.lukhas.api.auth_helpers import get_current_user, lukhas_tier_required
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Import wrapper module
try:
    from lukhas.dream import (
        get_dream_by_id,
        is_enabled,
        is_parallel_enabled,
        parallel_dream_mesh,
        simulate_dream,
    )
    DREAMS_WRAPPER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Dreams wrapper unavailable: {e}")
    DREAMS_WRAPPER_AVAILABLE = False


# Pydantic models for request/response validation
class DreamSimulationRequest(BaseModel):
    """Request model for dream simulation"""
    seed: str = Field(..., min_length=1, max_length=500, description="Dream seed/prompt")
    context: Optional[dict[str, Any]] = Field(default=None, description="Optional context dictionary")
    parallel: bool = Field(default=False, description="Use parallel processing")

    class Config:
        json_schema_extra: ClassVar[dict[str, object]] = {
            "example": {
                "seed": "morning_reflection",
                "context": {"mood": "calm", "time": "06:00"},
                "parallel": False
            }
        }


class DreamSimulationResponse(BaseModel):
    """Response model for dream simulation"""
    success: bool
    dream_id: Optional[str] = None
    seed: str
    result: Optional[dict[str, Any]] = None
    metadata: Optional[dict[str, Any]] = None
    error: Optional[str] = None


class ParallelDreamMeshRequest(BaseModel):
    """Request model for parallel dream mesh"""
    seeds: list[str] = Field(..., min_items=2, max_items=10, description="List of dream seeds (2-10)")
    consensus_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Consensus threshold")

    class Config:
        json_schema_extra: ClassVar[dict[str, object]] = {
            "example": {
                "seeds": ["morning_gratitude", "evening_reflection", "midday_clarity"],
                "consensus_threshold": 0.7
            }
        }


class ParallelDreamMeshResponse(BaseModel):
    """Response model for parallel dream mesh"""
    success: bool
    mesh_id: Optional[str] = None
    seeds: list[str]
    consensus_threshold: float
    dreams: list[dict[str, Any]] = Field(default_factory=list)
    consensus: Optional[dict[str, Any]] = None
    metadata: Optional[dict[str, Any]] = None
    error: Optional[str] = None


# Create router
router = APIRouter(
    prefix="/api/v1/dreams",
    tags=["Dreams"],
)


@router.post("/simulate", response_model=DreamSimulationResponse, status_code=status.HTTP_200_OK)
@lukhas_tier_required(TierLevel.AUTHENTICATED, PermissionScope.MEMORY_FOLD)
async def create_dream_simulation(
    request: DreamSimulationRequest,
    current_user: dict = Depends(get_current_user)
) -> DreamSimulationResponse:
    """
    Simulate a dream based on seed and context.

    Requires: LUKHAS_DREAMS_ENABLED=1
    For parallel processing: LUKHAS_PARALLEL_DREAMS=1

    Returns simulation results with dream_id for retrieval.
    """
    if not DREAMS_WRAPPER_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Dreams wrapper module unavailable"
        )

    if not is_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Dreams subsystem not enabled. Set LUKHAS_DREAMS_ENABLED=1"
        )

    if request.parallel and not is_parallel_enabled():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Parallel dreams not enabled. Set LUKHAS_PARALLEL_DREAMS=1"
        )

    try:
        start_time = time.time()
        result = simulate_dream(
            seed=request.seed,
            context=request.context,
            parallel=request.parallel
        )

        duration = time.time() - start_time
        logger.info(f"Dream simulation completed in {duration:.3f}s: {result.get('dream_id')}")

        return DreamSimulationResponse(**result)

    except Exception as e:
        logger.error(f"Error in dream simulation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Dream simulation failed: {e!s}"
        )


@router.post("/mesh", response_model=ParallelDreamMeshResponse, status_code=status.HTTP_200_OK)
@lukhas_tier_required(TierLevel.AUTHENTICATED, PermissionScope.MEMORY_FOLD)
async def create_parallel_dream_mesh(
    request: ParallelDreamMeshRequest,
    current_user: dict = Depends(get_current_user)
) -> ParallelDreamMeshResponse:
    """
    Run parallel dream mesh with multiple seeds and consensus.

    Requires: LUKHAS_DREAMS_ENABLED=1 AND LUKHAS_PARALLEL_DREAMS=1

    Returns mesh results with consensus data.
    """
    if not DREAMS_WRAPPER_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Dreams wrapper module unavailable"
        )

    if not is_parallel_enabled():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Parallel dreams not enabled. Set LUKHAS_PARALLEL_DREAMS=1"
        )

    try:
        start_time = time.time()
        result = parallel_dream_mesh(
            seeds=request.seeds,
            consensus_threshold=request.consensus_threshold
        )

        duration = time.time() - start_time
        logger.info(f"Parallel dream mesh completed in {duration:.3f}s: {result.get('mesh_id')}")

        return ParallelDreamMeshResponse(**result)

    except Exception as e:
        logger.error(f"Error in parallel dream mesh: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Parallel dream mesh failed: {e!s}"
        )


@router.get("/{dream_id}", status_code=status.HTTP_200_OK)
@lukhas_tier_required(TierLevel.AUTHENTICATED, PermissionScope.MEMORY_FOLD)
async def get_dream(
    dream_id: str,
    current_user: dict = Depends(get_current_user)
) -> dict[str, Any]:
    """
    Retrieve a dream by its ID.

    Requires: LUKHAS_DREAMS_ENABLED=1

    Returns dream data if found, 404 otherwise.
    """
    if not DREAMS_WRAPPER_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Dreams wrapper module unavailable"
        )

    if not is_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Dreams subsystem not enabled. Set LUKHAS_DREAMS_ENABLED=1"
        )

    try:
        dream = get_dream_by_id(dream_id)

        if dream is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dream not found: {dream_id}"
            )

        # Security check: Ensure user can only access their own dreams
        if dream.get("owner_id") != current_user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this resource"
            )

        return dream

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving dream {dream_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve dream: {e!s}"
        )


@router.get("/", status_code=status.HTTP_200_OK)
async def health_check() -> dict[str, Any]:
    """
    Health check endpoint for dreams subsystem.

    Returns subsystem status and feature flags.
    """
    return {
        "service": "dreams",
        "wrapper_available": DREAMS_WRAPPER_AVAILABLE,
        "enabled": is_enabled() if DREAMS_WRAPPER_AVAILABLE else False,
        "parallel_enabled": is_parallel_enabled() if DREAMS_WRAPPER_AVAILABLE else False,
        "version": "0.1.0-alpha"
    }
