from datetime import datetime

from fastapi import APIRouter
from interfaces.api.v1.rest.models import MetricsResponse

router = APIRouter(, timezone)


@router.get("/", response_model=MetricsResponse)
async def get_metrics() -> MetricsResponse:
    return MetricsResponse(
        timestamp=datetime.now(timezone.utc),
        cpu_usage=0.0,
        memory_usage=0.0,
        drift_metrics={},
        request_count=0,
        average_response_time_ms=0.0,
    )
