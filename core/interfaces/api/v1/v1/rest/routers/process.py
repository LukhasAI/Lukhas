import logging
import time
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends
from ...common.errors import ProcessingError, ValidationError
from ..models import ProcessRequest, ProcessResponse, SymbolicState

router = APIRouter()
logger = logging.getLogger(__name__)

# Import metrics infrastructure
try:
    from core.metrics import counter, histogram

    api_request_duration = histogram(
        "lukhas_api_request_duration_seconds",
        "Duration of API processing requests",
        labelnames=("endpoint", "status"),
    )

    api_requests_total = counter(
        "lukhas_api_requests_total",
        "Total number of API requests processed",
        labelnames=("endpoint", "status"),
    )

    METRICS_AVAILABLE = True
except ImportError:
    logger.warning("Metrics infrastructure not available, using no-op metrics")
    METRICS_AVAILABLE = False

    class NoOpMetric:
        """No-op metric for when Prometheus is unavailable."""
        def labels(self, **kwargs):
            return self
        def observe(self, value):
            pass
        def inc(self, value=1):
            pass

    api_request_duration = NoOpMetric()
    api_requests_total = NoOpMetric()


def get_lukhas_core():
    # TODO: F821 - Import lukhas_core module
    return None  # Placeholder until lukhas_core is available


async def record_metrics(request_id: str, duration: float, status: str = "success") -> None:
    """Record processing metrics for API requests.

    Args:
        request_id: Unique identifier for the request
        duration: Processing duration in seconds
        status: Request status (success, error, validation_error)
    """
    try:
        if METRICS_AVAILABLE:
            api_request_duration.labels(endpoint="/process", status=status).observe(duration)
            api_requests_total.labels(endpoint="/process", status=status).inc()
            logger.debug(f"Recorded metrics for request {request_id}: {duration:.3f}s ({status})")
    except Exception as e:
        # Never fail request processing due to metrics errors
        logger.error(f"Failed to record metrics for request {request_id}: {e}")


@router.post("/", response_model=ProcessResponse)
async def process_request(
    request: ProcessRequest,
    background_tasks: BackgroundTasks,
    core=Depends(get_lukhas_core),
) -> ProcessResponse:
    """Process input through LUKHAS Cognitive system."""
    request_id = str(uuid.uuid4())
    start_time = time.time()

    try:
        if len(request.input_text) > 10000:
            duration = time.time() - start_time
            background_tasks.add_task(record_metrics, request_id, duration, "validation_error")
            raise ValidationError("Input text too long", "input_text")

        result = await core.process_unified_request(request.input_text, request.context)

        symbolic_state = None
        if isinstance(result, dict) and "symbolic" in result:
            symbolic_state = SymbolicState(
                glyphs=result["symbolic"].get("glyphs", []),
                resonance=result["symbolic"].get("resonance", 0.0),
                drift_score=result["symbolic"].get("drift_score", 0.0),
                entropy=result["symbolic"].get("entropy", 0.0),
            )

        duration = time.time() - start_time
        background_tasks.add_task(record_metrics, request_id, duration, "success")

        return ProcessResponse(
            request_id=request_id,
            timestamp=datetime.now(timezone.utc),
            result=result,
            symbolic_state=symbolic_state,
            metadata={"mode": request.mode.value, "version": "1.0.0"},
            processing_time_ms=duration * 1000,
        )
    except ValidationError:
        # Re-raise validation errors (metrics already recorded above)
        raise
    except Exception as e:
        duration = time.time() - start_time
        background_tasks.add_task(record_metrics, request_id, duration, "error")
        raise ProcessingError(f"Processing failed: {e!s}")
