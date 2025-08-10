import os
from fastapi import FastAPI, Depends, HTTPException, Header
from typing import Optional
from lukhas_pwm.api.audit import router as audit_router
from lukhas_pwm.api.feedback import router as feedback_router
from lukhas_pwm.api.tools import router as tools_router
from lukhas_pwm.api.incidents import router as incidents_router
from lukhas_pwm.api.metrics import router as metrics_router

# --- app metadata ---
app = FastAPI(
    title="LUKHΛS PWM API",
    version="1.0.0",
    description="Governed tool loop, auditability, feedback LUT, and safety modes.",
    contact={"name": "LUKHAS", "url": "https://lukhas.ai"},
    license_info={"name": "Proprietary"},
)

# --- simple header-based API key (optional; keep public endpoints unguarded) ---
def require_api_key(x_api_key: Optional[str] = Header(default=None)):
    required = os.getenv("LUKHAS_API_KEY", "")
    if required and x_api_key != required:
        raise HTTPException(status_code=401, detail="Unauthorized")

# Include routers - some with API key protection, some public
app.include_router(audit_router, dependencies=[Depends(require_api_key)])
app.include_router(feedback_router)  # leave public
app.include_router(tools_router, dependencies=[Depends(require_api_key)])
app.include_router(incidents_router, dependencies=[Depends(require_api_key)])
app.include_router(metrics_router)  # leave public

# --- raw OpenAPI export (for CI artifact) ---
@app.get("/openapi.json", include_in_schema=False)
def openapi_export():
    return app.openapi()
