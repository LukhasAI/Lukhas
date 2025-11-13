from fastapi import APIRouter
from interfaces.api.v1.rest.models import HealthStatus

router = APIRouter()


@router.get("/", response_model=HealthStatus)
async def get_health() -> HealthStatus:
    return HealthStatus(
        status="healthy",
        version="1.0.0",
        uptime_seconds=0.0,
        components={"core": True},
    )
