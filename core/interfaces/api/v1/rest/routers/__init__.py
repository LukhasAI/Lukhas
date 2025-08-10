from .health import router as health_router
from .metrics import router as metrics_router
from .process import router as process_router
from .tasks import router as tasks_router

__all__ = ["process_router", "health_router", "metrics_router", "tasks_router"]
