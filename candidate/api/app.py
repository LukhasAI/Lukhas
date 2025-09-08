from __future__ import annotations

import os

from fastapi import Depends, FastAPI, Header, HTTPException

from lukhas.api.admin import router as admin_router
from lukhas.api.audit import router as audit_router
from lukhas.api.dna import router as dna_router
from lukhas.api.feedback import router as feedback_router
from lukhas.api.incidents import router as incidents_router
from lukhas.api.metrics import router as metrics_router
from lukhas.api.ops import router as ops_router
from lukhas.api.perf import router as perf_router
from lukhas.api.tools import router as tools_router

# --- app metadata ---
app = FastAPI(
title="LUKHΛS  API",
version="1.0.0",
description="Governed tool loop, auditability, feedback LUT, and safety modes.",
contact={"name": "LUKHAS", "url": "https://lukhas.ai"},
license_info={"name": "Proprietary"},
)


# --- simple header-based API key (optional; keep public endpoints unguarded) ---
def require_api_key(x_api_key: str | None = Header(default=None)):
    required = os.getenv("LUKHAS_API_KEY", "")
    if required and x_api_key != required:
        raise HTTPException(status_code=401, detail="Unauthorized")


# Include routers - some with API key protection, some public
app.include_router(audit_router, dependencies=[Depends(require_api_key)])
app.include_router(feedback_router)  # leave public
app.include_router(tools_router, dependencies=[Depends(require_api_key)])
app.include_router(incidents_router, dependencies=[Depends(require_api_key)])
app.include_router(metrics_router)  # leave public
app.include_router(dna_router)  # optional DNA monitoring endpoints

# Mount Admin Dashboard always; routes enforce flag at request-time and require API key.
app.include_router(admin_router, dependencies=[Depends(require_api_key)])
app.include_router(ops_router, dependencies=[Depends(require_api_key)])
app.include_router(perf_router)  # Perf ingestion (has its own auth check)


# --- raw OpenAPI export (for CI artifact) ---
@app.get("/openapi.json", include_in_schema=False)
def openapi_export():
    return app.openapi()
