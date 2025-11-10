"""
LUKHAS Drift Monitoring API Endpoints
======================================

Production API routes for Vivox drift monitoring and trend analysis.
All endpoints are feature-flag gated (LUKHAS_DRIFT_ENABLED).

Drift monitoring tracks intent vs. action alignment using cosine similarity
with EMA smoothing and per-lane thresholds.

Endpoints:
- GET /api/v1/drift/{user_id} - Get current drift score
- GET /api/v1/drift/{user_id}/trends - Get drift trend history
- POST /api/v1/drift/update - Update drift monitoring with new data
- GET /api/v1/drift/config - Get drift configuration for lane
"""
import logging
import os
import time
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Feature flag
_DRIFT_ENABLED = (os.getenv("LUKHAS_DRIFT_ENABLED", "0") or "0").strip() == "1"

# Import drift monitor safely
_DRIFT_AVAILABLE = False
try:
    from lukhas_website.lukhas.core.drift import DriftMonitor, LANE_CFG
    _DRIFT_AVAILABLE = True
except ImportError:
    try:
        from lukhas.core.drift import DriftMonitor, LANE_CFG
        _DRIFT_AVAILABLE = True
    except ImportError as e:
        logger.warning(f"Drift module unavailable: {e}")


# In-memory storage for drift monitors (per user)
# TODO: Replace with persistent storage
_user_drift_monitors: dict[str, DriftMonitor] = {}
_user_drift_history: dict[str, list[dict[str, Any]]] = {}


# Pydantic models
class DriftUpdateRequest(BaseModel):
    """Request model for drift update"""
    user_id: str = Field(..., min_length=1, max_length=100, description="User identifier")
    intent: list[float] = Field(..., min_items=1, max_items=1000, description="Intent vector")
    action: list[float] = Field(..., min_items=1, max_items=1000, description="Action vector")
    lane: Optional[str] = Field(default=None, description="Lane (experimental/candidate/prod)")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "intent": [1.0, 0.0, 0.5],
                "action": [0.9, 0.1, 0.4],
                "lane": "experimental"
            }
        }


class DriftUpdateResponse(BaseModel):
    """Response model for drift update"""
    success: bool
    user_id: str
    drift: float
    ema: float
    guardian: str
    lane: str
    timestamp: float
    error: Optional[str] = None


class DriftScoreResponse(BaseModel):
    """Response model for current drift score"""
    user_id: str
    drift_ema: float
    guardian_status: str
    lane: str
    sample_count: int
    last_updated: Optional[float] = None


class DriftTrendsResponse(BaseModel):
    """Response model for drift trends"""
    user_id: str
    lane: str
    history: list[dict[str, Any]]
    stats: dict[str, Any]


class DriftConfigResponse(BaseModel):
    """Response model for drift configuration"""
    lane: str
    warn_threshold: float
    block_threshold: float
    alpha: float
    window: int


# Create router
router = APIRouter(
    prefix="/api/v1/drift",
    tags=["Drift Monitoring"],
)


def _get_or_create_monitor(user_id: str, lane: Optional[str] = None) -> DriftMonitor:
    """Get or create drift monitor for user"""
    if user_id not in _user_drift_monitors:
        _user_drift_monitors[user_id] = DriftMonitor(lane=lane)
        _user_drift_history[user_id] = []
    return _user_drift_monitors[user_id]


@router.post("/update", response_model=DriftUpdateResponse, status_code=status.HTTP_200_OK)
async def update_drift(request: DriftUpdateRequest) -> DriftUpdateResponse:
    """
    Update drift monitoring with new intent/action pair.

    Requires: LUKHAS_DRIFT_ENABLED=1

    Calculates drift score, updates EMA, and determines guardian action.
    """
    if not _DRIFT_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Drift monitoring not enabled. Set LUKHAS_DRIFT_ENABLED=1"
        )

    if not _DRIFT_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Drift module unavailable"
        )

    # Validate vector lengths match
    if len(request.intent) != len(request.action):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Intent and action vectors must have same length (got {len(request.intent)} vs {len(request.action)})"
        )

    try:
        monitor = _get_or_create_monitor(request.user_id, request.lane)
        result = monitor.update(
            intent=request.intent,
            action=request.action
        )

        # Store in history
        timestamp = time.time()
        history_entry = {
            **result,
            "timestamp": timestamp,
            "user_id": request.user_id
        }
        _user_drift_history[request.user_id].append(history_entry)

        # Limit history size (keep last 1000 entries)
        if len(_user_drift_history[request.user_id]) > 1000:
            _user_drift_history[request.user_id].pop(0)

        logger.info(f"Drift updated for {request.user_id}: ema={result['ema']:.3f}, guardian={result['guardian']}")

        return DriftUpdateResponse(
            success=True,
            user_id=request.user_id,
            drift=result["drift"],
            ema=result["ema"],
            guardian=result["guardian"],
            lane=result["lane"],
            timestamp=timestamp
        )

    except Exception as e:
        logger.error(f"Error updating drift for {request.user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Drift update failed: {str(e)}"
        )


@router.get("/{user_id}", response_model=DriftScoreResponse, status_code=status.HTTP_200_OK)
async def get_drift_score(user_id: str) -> DriftScoreResponse:
    """
    Get current drift score for a user.

    Requires: LUKHAS_DRIFT_ENABLED=1

    Returns current EMA, guardian status, and sample count.
    """
    if not _DRIFT_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Drift monitoring not enabled. Set LUKHAS_DRIFT_ENABLED=1"
        )

    if not _DRIFT_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Drift module unavailable"
        )

    if user_id not in _user_drift_monitors:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No drift data for user: {user_id}"
        )

    try:
        monitor = _user_drift_monitors[user_id]
        history = _user_drift_history.get(user_id, [])

        # Determine guardian status based on current EMA
        guardian_status = "allow"
        if monitor.ema >= monitor.cfg.block_threshold:
            guardian_status = "block"
        elif monitor.ema >= monitor.cfg.warn_threshold:
            guardian_status = "warn"

        last_updated = history[-1]["timestamp"] if history else None

        return DriftScoreResponse(
            user_id=user_id,
            drift_ema=monitor.ema,
            guardian_status=guardian_status,
            lane=monitor.lane,
            sample_count=len(monitor._raw),
            last_updated=last_updated
        )

    except Exception as e:
        logger.error(f"Error getting drift score for {user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get drift score: {str(e)}"
        )


@router.get("/{user_id}/trends", response_model=DriftTrendsResponse, status_code=status.HTTP_200_OK)
async def get_drift_trends(
    user_id: str,
    limit: int = 100,
    offset: int = 0
) -> DriftTrendsResponse:
    """
    Get drift trend history for a user.

    Requires: LUKHAS_DRIFT_ENABLED=1

    Returns paginated history with summary statistics.
    """
    if not _DRIFT_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Drift monitoring not enabled. Set LUKHAS_DRIFT_ENABLED=1"
        )

    if not _DRIFT_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Drift module unavailable"
        )

    if user_id not in _user_drift_history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No drift history for user: {user_id}"
        )

    try:
        history = _user_drift_history[user_id]
        monitor = _user_drift_monitors.get(user_id)

        # Paginate history
        total = len(history)
        start = min(offset, total)
        end = min(start + limit, total)
        paginated = history[start:end]

        # Calculate statistics
        if history:
            drift_values = [entry["drift"] for entry in history]
            ema_values = [entry["ema"] for entry in history]

            stats = {
                "total_samples": total,
                "returned_samples": len(paginated),
                "offset": offset,
                "limit": limit,
                "current_ema": monitor.ema if monitor else ema_values[-1],
                "avg_drift": sum(drift_values) / len(drift_values),
                "max_drift": max(drift_values),
                "min_drift": min(drift_values),
                "avg_ema": sum(ema_values) / len(ema_values),
                "warn_count": sum(1 for e in history if e["guardian"] == "warn"),
                "block_count": sum(1 for e in history if e["guardian"] == "block"),
            }
        else:
            stats = {"total_samples": 0}

        return DriftTrendsResponse(
            user_id=user_id,
            lane=monitor.lane if monitor else "unknown",
            history=paginated,
            stats=stats
        )

    except Exception as e:
        logger.error(f"Error getting drift trends for {user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get drift trends: {str(e)}"
        )


@router.get("/config/{lane}", response_model=DriftConfigResponse, status_code=status.HTTP_200_OK)
async def get_drift_config(lane: str) -> DriftConfigResponse:
    """
    Get drift configuration for a specific lane.

    Does NOT require LUKHAS_DRIFT_ENABLED (config always available).

    Returns thresholds and EMA parameters for the lane.
    """
    if not _DRIFT_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Drift module unavailable"
        )

    lane = lane.lower()
    if lane not in LANE_CFG:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown lane: {lane}. Available: {list(LANE_CFG.keys())}"
        )

    try:
        cfg = LANE_CFG[lane]
        return DriftConfigResponse(
            lane=lane,
            warn_threshold=cfg.warn_threshold,
            block_threshold=cfg.block_threshold,
            alpha=cfg.alpha,
            window=cfg.window
        )

    except Exception as e:
        logger.error(f"Error getting drift config for {lane}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get drift config: {str(e)}"
        )


@router.get("/", status_code=status.HTTP_200_OK)
async def health_check() -> dict[str, Any]:
    """
    Health check endpoint for drift monitoring subsystem.

    Returns subsystem status and active monitors count.
    """
    return {
        "service": "drift",
        "enabled": _DRIFT_ENABLED,
        "available": _DRIFT_AVAILABLE,
        "active_monitors": len(_user_drift_monitors),
        "total_history_entries": sum(len(h) for h in _user_drift_history.values()),
        "version": "2.0.0"
    }
