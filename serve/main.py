"""Entry point for LUKHAS commercial API"""

import logging
from typing import Any, Optional

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

try:
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False

    class MockInstrumentor:
        @staticmethod
        def instrument_app(app: FastAPI) -> None:
            pass

    FastAPIInstrumentor = MockInstrumentor

try:
    from enterprise.observability.instantiate import obs_stack
except Exception:  # pragma: no cover - optional enterprise package
    class _ObsStack:
        opentelemetry_enabled = False


    obs_stack = _ObsStack()

try:
    from config.env import get as env_get
except Exception:
    import os as _os

    def env_get(key: str, default: Optional[str] = None) -> Optional[str]:
        return _os.getenv(key, default)


import os


# Guard optional internal routers so tests can import this module in minimal envs
def _safe_import_router(module_path: str, attr: str = "router") -> Optional[Any]:
    try:
        mod = __import__(module_path, fromlist=[attr])
        return getattr(mod, attr)
    except Exception:
        # Return None when optional/internal module isn't available
        return None


consciousness_router = _safe_import_router(".consciousness_api", "router")
feedback_router = _safe_import_router(".feedback_routes", "router")
guardian_router = _safe_import_router(".guardian_api", "router")
identity_router = _safe_import_router(".identity_api", "router")
openai_router = _safe_import_router(".openai_routes", "router")
orchestration_router = _safe_import_router(".orchestration_routes", "router")
routes_router = _safe_import_router(".routes", "router")
traces_router = _safe_import_router(".routes_traces", "router")

logging.basicConfig(level=logging.INFO)


# Optional API key authentication
def require_api_key(x_api_key: Optional[str] = Header(default=None)) -> Optional[str]:
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
frontend_origin = env_get("FRONTEND_ORIGIN", "http://localhost:3000") or "http://localhost:3000"
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if routes_router is not None:
    app.include_router(routes_router)
if openai_router is not None:
    app.include_router(openai_router)
if feedback_router is not None:
    app.include_router(feedback_router)
if traces_router is not None:
    app.include_router(traces_router)
if orchestration_router is not None:
    app.include_router(orchestration_router)

# Instrument FastAPI app with OpenTelemetry
if OPENTELEMETRY_AVAILABLE and getattr(obs_stack, "opentelemetry_enabled", False):
    FastAPIInstrumentor.instrument_app(app)
if identity_router is not None:
    app.include_router(identity_router)
if consciousness_router is not None:
    app.include_router(consciousness_router)
if guardian_router is not None:
    app.include_router(guardian_router)


# Lightweight voice probe: try to import voice subsystem modules; return False if unavailable
def voice_core_available() -> bool:
    try:
        # import-time probe only; do not trigger heavy initialization
        __import__("voice_core")
        return True
    except Exception:
        # PERF203: intentional simple import probe pattern
        return False


@app.get("/healthz")
def healthz() -> dict[str, Any]:
    """Health check endpoint for monitoring.

    Behavior:
    - Always returns HTTP 200 for readiness consumers.
    - When LUKHAS_VOICE_REQUIRED=true and the lightweight probe fails,
      include 'voice' in `degraded_reasons` and set `voice_mode` to 'degraded'.
    """
    status: dict[str, Any] = {"status": "ok"}

    required = os.getenv("LUKHAS_VOICE_REQUIRED", "false").lower() == "true"
    voice_ok = voice_core_available()
    status["voice_mode"] = "normal" if voice_ok else "degraded"
    if required and not voice_ok:
        # Avoid setdefault typing issues: explicitly manage the list
        existing = status.get("degraded_reasons")
        if existing is None:
            status["degraded_reasons"] = ["voice"]
        else:
            # mypy: existing may be Any; assume list and append
            if isinstance(existing, list):
                existing.append("voice")
            else:
                # Fallback: overwrite with new list
                status["degraded_reasons"] = ["voice"]

    return status


# Expose raw OpenAPI for artifacting
@app.get("/openapi.json", include_in_schema=False)
def openapi_export() -> dict[str, Any]:
    """Export OpenAPI specification as JSON"""
    return app.openapi()


if __name__ == "__main__":
    import os

    import uvicorn

    host = os.getenv("LUKHAS_BIND_HOST", "127.0.0.1")
    port = int(os.getenv("LUKHAS_BIND_PORT", "8000"))
    uvicorn.run(app, host=host, port=port)
