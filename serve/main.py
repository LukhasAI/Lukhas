"""Entry point for LUKHAS commercial API"""

import logging
from typing import Optional

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

try:
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False

    class MockInstrumentor:
        @staticmethod
        def instrument_app(app):
            pass

    FastAPIInstrumentor = MockInstrumentor

from enterprise.observability.instantiate import obs_stack

try:
    from config.env import get as env_get
except Exception:
    import os as _os

    def env_get(key: str, default=None):
        return _os.getenv(key, default)


from .consciousness_api import router as consciousness_router
from .feedback_routes import router as feedback_router
from .guardian_api import router as guardian_router
from .identity_api import router as identity_router
from .openai_routes import router as openai_router
from .orchestration_routes import router as orchestration_router
from .routes import router
from .routes_traces import r as traces_router

logging.basicConfig(level=logging.INFO)


# Optional API key authentication
def require_api_key(x_api_key: Optional[str] = Header(default=None)):
    """Simple API key security for protected endpoints"""
    expected_key = env_get("LUKHAS_API_KEY", "")
    if expected_key and x_api_key != expected_key:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return x_api_key


app = FastAPI(
    title="LUKHAS API",
    version="1.0.0",
    description="Governed tool loop, auditability, feedback LUT, and safety modes.",
    contact={
        "name": "LUKHAS AI Team",
        "url": "https://github.com/LukhasAI/Lukhas",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    servers=[
        {"url": "http://localhost:8000", "description": "Local development"},
        {"url": "https://api.lukhas.ai", "description": "Production"},
    ],
)

# CORS configuration from env
frontend_origin = env_get("FRONTEND_ORIGIN", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(openai_router)
app.include_router(feedback_router)
app.include_router(traces_router)
app.include_router(orchestration_router)

# Instrument FastAPI app with OpenTelemetry
if OPENTELEMETRY_AVAILABLE and obs_stack.opentelemetry_enabled:
    FastAPIInstrumentor.instrument_app(app)
app.include_router(identity_router)
app.include_router(consciousness_router)
app.include_router(guardian_router)


# Health check endpoint
@app.get("/healthz")
def healthz():
    """Health check endpoint for monitoring."""
    return {"status": "ok"}


# Expose raw OpenAPI for artifacting
@app.get("/openapi.json", include_in_schema=False)
def openapi_export():
    """Export OpenAPI specification as JSON"""
    return app.openapi()


if __name__ == "__main__":
    import os

    import uvicorn

    host = os.getenv("LUKHAS_BIND_HOST", "127.0.0.1")
    port = int(os.getenv("LUKHAS_BIND_PORT", "8000"))
    uvicorn.run(app, host=host, port=port)
