import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

try:
    from interfaces.api.v1.common.errors import APIError
except ImportError:
    # Create placeholder if the module doesn't exist

    class APIError(Exception):
        def __init__(self, message: str, status_code: int = 500):
            self.message = message
            self.status_code = status_code
            super().__init__(message)


from interfaces.api import API_PREFIX
from interfaces.api.v1.rest.routers import (
    health_router,
    metrics_router,
    process_router,
    tasks_router,
)

app = FastAPI(
    title="LUKHAS Cognitive AI API",
    description="Enterprise Cognitive Artificial Intelligence System",
    version="1.0.0",
    docs_url=f"{API_PREFIX}/docs",
    redoc_url=f"{API_PREFIX}/redoc",
    openapi_url=f"{API_PREFIX}/openapi.json",
)

# Shared event bus instance for coordination announcements
event_bus = EventBus()
app.state.event_bus = event_bus

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(APIError)
async def api_error_handler(request: Request, exc: APIError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


app.include_router(process_router, prefix=f"{API_PREFIX}/process")
app.include_router(health_router, prefix=f"{API_PREFIX}/health")
app.include_router(metrics_router, prefix=f"{API_PREFIX}/metrics")
app.include_router(tasks_router, prefix=f"{API_PREFIX}/tasks")


@app.on_event("startup")
async def startup_event():
    logging.info("LUKHAS Cognitive AI API starting up...")


@app.on_event("shutdown")
async def shutdown_event():
    logging.info("LUKHAS Cognitive AI API shutting down...")
