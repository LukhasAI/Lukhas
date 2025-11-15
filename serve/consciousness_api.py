"""
Consciousness API - Full Implementation

Provides endpoints for consciousness system status monitoring,
awareness updates, drift detection, and performance metrics.

Integrates with:
- core.consciousness.drift_detector - Drift detection
- matriz.consciousness - MATRIZ cognitive core
- lukhas.governance.guardian - Policy enforcement
"""

import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator

from lukhas.api.auth_helpers import get_current_user_from_token, has_role

# Graceful imports for consciousness components
try:
    from core.consciousness.drift_detector import ConsciousnessDriftDetector
    DRIFT_DETECTOR_AVAILABLE = True
except ImportError:
    DRIFT_DETECTOR_AVAILABLE = False
    logging.warning("ConsciousnessDriftDetector not available - using fallback")

try:
    from matriz.consciousness.engine import ConsciousnessEngine
    MATRIZ_AVAILABLE = True
except ImportError:
    MATRIZ_AVAILABLE = False
    logging.warning("MATRIZ ConsciousnessEngine not available - using fallback")

try:
    from lukhas.governance.guardian.core import Guardian
    GUARDIAN_AVAILABLE = True
except ImportError:
    GUARDIAN_AVAILABLE = False
    logging.warning("Guardian not available - using fallback")


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/consciousness", tags=["consciousness"])


# --- Global State & Singletons ---
# In production, these would be injected via dependency injection
_drift_detector: Optional[ConsciousnessDriftDetector] = None
_consciousness_engine: Optional[Any] = None
_guardian: Optional[Any] = None
_awareness_level: float = 0.7  # Default awareness level
_awareness_update_log: list[Dict[str, Any]] = []


def get_drift_detector() -> ConsciousnessDriftDetector:
    """Get or create drift detector instance."""
    global _drift_detector
    if _drift_detector is None:
        if DRIFT_DETECTOR_AVAILABLE:
            _drift_detector = ConsciousnessDriftDetector(
                retention=12,
                archive_on_reset=True
            )
        else:
            # Fallback mock for testing
            _drift_detector = _MockDriftDetector()
    return _drift_detector


def get_consciousness_engine() -> Any:
    """Get or create consciousness engine instance."""
    global _consciousness_engine
    if _consciousness_engine is None:
        if MATRIZ_AVAILABLE:
            try:
                _consciousness_engine = ConsciousnessEngine()
            except Exception as e:
                logger.warning(f"Failed to initialize ConsciousnessEngine: {e}")
                _consciousness_engine = _MockConsciousnessEngine()
        else:
            _consciousness_engine = _MockConsciousnessEngine()
    return _consciousness_engine


def get_guardian() -> Any:
    """Get or create guardian instance."""
    global _guardian
    if _guardian is None:
        if GUARDIAN_AVAILABLE:
            try:
                _guardian = Guardian()
            except Exception as e:
                logger.warning(f"Failed to initialize Guardian: {e}")
                _guardian = _MockGuardian()
        else:
            _guardian = _MockGuardian()
    return _guardian


# --- Mock Implementations for Fallback ---
class _MockDriftDetector:
    """Fallback drift detector for testing."""
    def summarize_layers(self) -> dict:
        return {
            "layers": {
                "reasoning": {"driftScore": 0.12, "affect_delta": 0.05, "samples": 10.0},
                "memory": {"driftScore": 0.08, "affect_delta": 0.03, "samples": 10.0},
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def query_archived_snapshots(self, **kwargs) -> list:
        return []

    def record_snapshot(self, layer_id: str, driftScore: float,
                       affect_delta: float, **kwargs):
        pass


class _MockConsciousnessEngine:
    """Fallback consciousness engine for testing."""
    def get_status(self) -> dict:
        return {
            "active": True,
            "threads": 3,
            "subsystems": {
                "reasoning": True,
                "memory": True,
                "learning": True,
            }
        }

    def get_metrics(self) -> dict:
        return {
            "processing_time_ms": 150,
            "memory_usage_mb": 512,
            "active_threads": 3,
        }


class _MockGuardian:
    """Fallback guardian for testing."""
    def is_active(self) -> bool:
        return True

    def check_policy(self, action: str) -> dict:
        return {"allowed": True, "reason": "mock guardian"}


# --- Pydantic Models ---
class ConsciousnessStatus(BaseModel):
    """Current consciousness system status."""
    status: str = Field(..., description="System status: active, idle, or degraded")
    awareness_level: float = Field(..., ge=0.0, le=1.0, description="Current awareness level (0.0-1.0)")
    active_threads: int = Field(..., ge=0, description="Number of active processing threads")
    last_update: datetime = Field(..., description="Timestamp of last status update")
    subsystems: Dict[str, bool] = Field(..., description="Subsystem status map")
    drift_score: float = Field(..., ge=0.0, description="Current drift level")


class AwarenessUpdate(BaseModel):
    """Request to update awareness level."""
    new_level: float = Field(..., ge=0.0, le=1.0, description="New awareness level (0.0-1.0)")
    reason: str = Field(..., min_length=1, description="Reason for awareness update")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @field_validator('new_level')
    @classmethod
    def validate_awareness_level(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError("Awareness level must be between 0.0 and 1.0")
        return v


class DriftDetectionRequest(BaseModel):
    """Request for drift detection analysis."""
    baseline_state: Dict[str, Any] = Field(..., description="Baseline state for comparison")
    current_state: Dict[str, Any] = Field(..., description="Current state to compare")


class DriftDetectionResponse(BaseModel):
    """Response from drift detection."""
    drift_score: float = Field(..., description="Calculated drift score")
    drift_details: Dict[str, Any] = Field(..., description="Detailed drift analysis")
    threshold_exceeded: bool = Field(..., description="Whether drift exceeds warning threshold")
    recommendation: str = Field(..., description="Recommended action")


class MetricsResponse(BaseModel):
    """Consciousness system performance metrics."""
    processing_time_avg_ms: float
    memory_usage_mb: float
    active_threads: int
    drift_history: list[Dict[str, Any]]
    uptime_seconds: float
    total_requests: int


# --- Admin Authorization Dependency ---
def require_admin(current_user: dict = Depends(get_current_user_from_token)) -> dict:
    """
    Dependency to require admin role for sensitive operations.

    Raises:
        HTTPException: If user does not have admin role
    """
    user_role = current_user.get("role", "guest")

    if not has_role(user_role, "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Admin role required. Current role: {user_role}",
        )

    return current_user


# --- Endpoints ---
@router.get("/status", response_model=ConsciousnessStatus)
async def get_consciousness_status() -> ConsciousnessStatus:
    """
    Get current consciousness system status.

    Returns comprehensive status including:
    - Overall system status (active/idle/degraded)
    - Current awareness level
    - Active processing threads
    - Subsystem health
    - Current drift score
    """
    try:
        # 1. Query consciousness subsystems
        engine = get_consciousness_engine()
        engine_status = engine.get_status()

        # 2. Get current awareness level
        global _awareness_level

        # 3. Check drift detector
        drift_detector = get_drift_detector()
        drift_summary = drift_detector.summarize_layers()

        # Calculate average drift score across layers
        layers = drift_summary.get("layers", {})
        if layers:
            avg_drift = sum(layer.get("driftScore", 0.0) for layer in layers.values()) / len(layers)
        else:
            avg_drift = 0.0

        # 4. Determine overall status
        if avg_drift > 0.3:
            overall_status = "degraded"
        elif engine_status.get("active", False):
            overall_status = "active"
        else:
            overall_status = "idle"

        # 5. Return comprehensive status
        return ConsciousnessStatus(
            status=overall_status,
            awareness_level=_awareness_level,
            active_threads=engine_status.get("threads", 0),
            last_update=datetime.now(timezone.utc),
            subsystems=engine_status.get("subsystems", {}),
            drift_score=avg_drift,
        )

    except Exception as e:
        logger.error(f"Error getting consciousness status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get consciousness status: {str(e)}"
        )


@router.post("/awareness/update")
async def update_awareness(
    data: AwarenessUpdate,
    user: dict = Depends(require_admin)
) -> Dict[str, Any]:
    """
    Update system awareness level (admin only).

    Args:
        data: Awareness update request with new level and reason
        user: Current user (must have admin role)

    Returns:
        Confirmation with old and new awareness levels
    """
    global _awareness_level, _awareness_update_log

    try:
        # 1. Validate new level (already validated by Pydantic)
        old_level = _awareness_level
        new_level = data.new_level

        # 2. Update consciousness system
        _awareness_level = new_level

        # Update consciousness engine if available
        engine = get_consciousness_engine()
        if hasattr(engine, "set_awareness_level"):
            engine.set_awareness_level(new_level)

        # 3. Log change
        update_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user": user.get("username"),
            "old_level": old_level,
            "new_level": new_level,
            "reason": data.reason,
            "metadata": data.metadata,
        }
        _awareness_update_log.append(update_record)

        logger.info(
            f"Awareness level updated by {user.get('username')}: "
            f"{old_level:.2f} -> {new_level:.2f} (reason: {data.reason})"
        )

        # 4. Return confirmation
        return {
            "success": True,
            "old_level": old_level,
            "new_level": new_level,
            "updated_by": user.get("username"),
            "timestamp": update_record["timestamp"],
            "reason": data.reason,
        }

    except Exception as e:
        logger.error(f"Error updating awareness: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update awareness: {str(e)}"
        )


@router.get("/metrics", response_model=MetricsResponse)
async def get_consciousness_metrics() -> MetricsResponse:
    """
    Get consciousness performance metrics.

    Returns:
        Performance metrics including processing time, memory usage,
        active threads, and drift history.
    """
    try:
        # Get engine metrics
        engine = get_consciousness_engine()
        engine_metrics = engine.get_metrics()

        # Get drift history
        drift_detector = get_drift_detector()
        drift_summary = drift_detector.summarize_layers()

        # Build drift history
        drift_history = []
        for layer_id, layer_data in drift_summary.get("layers", {}).items():
            drift_history.append({
                "layer_id": layer_id,
                "drift_score": layer_data.get("driftScore", 0.0),
                "affect_delta": layer_data.get("affect_delta", 0.0),
                "samples": int(layer_data.get("samples", 0)),
            })

        # Calculate uptime (placeholder - would track actual start time in production)
        uptime = engine_metrics.get("uptime_seconds", 3600.0)

        return MetricsResponse(
            processing_time_avg_ms=engine_metrics.get("processing_time_ms", 0.0),
            memory_usage_mb=engine_metrics.get("memory_usage_mb", 0.0),
            active_threads=engine_metrics.get("active_threads", 0),
            drift_history=drift_history,
            uptime_seconds=uptime,
            total_requests=engine_metrics.get("total_requests", 0),
        )

    except Exception as e:
        logger.error(f"Error getting metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get metrics: {str(e)}"
        )


@router.post("/drift/detect", response_model=DriftDetectionResponse)
async def detect_drift(request: DriftDetectionRequest) -> DriftDetectionResponse:
    """
    Trigger drift detection between baseline and current state.

    Args:
        request: Baseline and current state for comparison

    Returns:
        Drift score, detailed analysis, and recommendations
    """
    try:
        start_time = time.time()

        # 1. Call drift detector
        drift_detector = get_drift_detector()

        # 2. Compare baseline vs current
        # Calculate drift score based on state differences
        baseline = request.baseline_state
        current = request.current_state

        # Simple drift calculation: compare key metrics
        drift_components = {}
        total_drift = 0.0
        num_components = 0

        # Compare common keys
        all_keys = set(baseline.keys()) | set(current.keys())
        for key in all_keys:
            baseline_val = baseline.get(key, 0)
            current_val = current.get(key, 0)

            # Convert to float for comparison
            try:
                if isinstance(baseline_val, (int, float)) and isinstance(current_val, (int, float)):
                    # Normalized difference
                    max_val = max(abs(baseline_val), abs(current_val), 1.0)
                    component_drift = abs(baseline_val - current_val) / max_val
                    drift_components[key] = {
                        "baseline": baseline_val,
                        "current": current_val,
                        "drift": component_drift,
                    }
                    total_drift += component_drift
                    num_components += 1
            except (TypeError, ValueError):
                # Skip non-numeric comparisons
                continue

        # Average drift score
        drift_score = total_drift / num_components if num_components > 0 else 0.0

        # Record snapshot in drift detector
        drift_detector.record_snapshot(
            layer_id="api_triggered",
            driftScore=drift_score,
            affect_delta=drift_score,
            metadata={
                "baseline_keys": list(baseline.keys()),
                "current_keys": list(current.keys()),
                "components_compared": num_components,
            }
        )

        # 3. Determine if threshold exceeded
        WARNING_THRESHOLD = 0.15
        CRITICAL_THRESHOLD = 0.30

        threshold_exceeded = drift_score > WARNING_THRESHOLD

        # 4. Generate recommendation
        if drift_score > CRITICAL_THRESHOLD:
            recommendation = "CRITICAL: Immediate attention required. Consider resetting to baseline."
        elif drift_score > WARNING_THRESHOLD:
            recommendation = "WARNING: Monitor closely. Review recent changes."
        else:
            recommendation = "OK: Drift within acceptable range."

        processing_time = (time.time() - start_time) * 1000

        return DriftDetectionResponse(
            drift_score=drift_score,
            drift_details={
                "components": drift_components,
                "num_components": num_components,
                "processing_time_ms": processing_time,
                "thresholds": {
                    "warning": WARNING_THRESHOLD,
                    "critical": CRITICAL_THRESHOLD,
                },
            },
            threshold_exceeded=threshold_exceeded,
            recommendation=recommendation,
        )

    except Exception as e:
        logger.error(f"Error detecting drift: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to detect drift: {str(e)}"
        )


@router.get("/awareness/history")
async def get_awareness_history(
    limit: int = 10,
    user: dict = Depends(require_admin)
) -> Dict[str, Any]:
    """
    Get awareness update history (admin only).

    Args:
        limit: Maximum number of records to return
        user: Current user (must have admin role)

    Returns:
        List of recent awareness updates
    """
    global _awareness_update_log

    return {
        "total_updates": len(_awareness_update_log),
        "updates": _awareness_update_log[-limit:],
        "current_level": _awareness_level,
    }


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Simple health check endpoint.

    Returns:
        Health status of consciousness API
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "components": {
            "drift_detector": DRIFT_DETECTOR_AVAILABLE,
            "consciousness_engine": MATRIZ_AVAILABLE,
            "guardian": GUARDIAN_AVAILABLE,
        },
    }


# Export router
__all__ = ["router"]
