"""Entry point for Lukhas commercial API"""

import logging
import os
from typing import Optional

from fastapi import FastAPI, Header, HTTPException

from .feedback_routes import router as feedback_router
from .openai_routes import router as openai_router
from .routes import router

logging.basicConfig(level=logging.INFO)


# Optional API key authentication
def require_api_key(x_api_key: Optional[str] = Header(default=None)):
    """Simple API key security for protected endpoints"""
    expected_key = os.getenv("LUKHAS_API_KEY", "")
    if expected_key and x_api_key != expected_key:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return x_api_key


app = FastAPI(
    title="LUKHΛS  API",
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

app.include_router(router)
app.include_router(openai_router)
app.include_router(feedback_router)


# Expose raw OpenAPI for artifacting
@app.get("/openapi.json", include_in_schema=False)
def openapi_export():
    """Export OpenAPI specification as JSON"""
    return app.openapi()
