from __future__ import annotations

import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from products.intelligence.lens.lens_core import ΛLens
from products.intelligence.lens.renderers.web2d_renderer import Web2DRenderer
from products.intelligence.lens.renderers.xr_renderer import XRRenderer
from products.intelligence.lens.widgets.widget_factory import WidgetFactory


class JobRequest(BaseModel):
    file_type: Optional[str] = None
    content: Optional[str] = None
    options: Optional[dict[str, Any]] = None


class JobResponse(BaseModel):
    job_id: str
    status: str
    message: str
    result: Optional[dict[str, Any]] = None


class PhotonDocument(BaseModel):
    id: str
    title: str
    content: str
    symbols: list[dict[str, Any]]
    widgets: list[dict[str, Any]]
    metadata: dict[str, Any]


lens_engine = ΛLens()
web_renderer = Web2DRenderer()
xr_renderer = XRRenderer()
widget_factory = WidgetFactory()

jobs: dict[str, dict[str, Any]] = {}

app = FastAPI(
    title="ΛLens API",
    description="Symbolic File Transformation and Dashboard Generation API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict[str, Any]:
    """Root endpoint with API information"""
    return {
        "message": "ΛLens API - Symbolic File Transformation Service",
        "version": "1.0.0",
        "endpoints": [
            "/docs - API Documentation",
            "/health - Health Check",
            "/transform - File Transformation",
            "/jobs/{job_id} - Job Status",
        ],
    }


@app.get("/health")
async def health_check() -> dict[str, Any]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "components": {
            "lens_core": "active",
            "symbol_generator": isinstance(lens_engine.symbol_generator, object),
            "widget_factory": "active",
            "renderers": "active",
        },
    }


@app.post("/transform", response_model=JobResponse)
async def transform_file(file: UploadFile = File(...)) -> JobResponse:
    """Transform uploaded file into symbolic dashboard"""
    try:
        job_id = str(uuid.uuid4())
        content = await file.read()

        jobs[job_id] = {
            "status": "processing",
            "file_type": Path(file.filename or "").suffix.lower().lstrip("."),
            "filename": file.filename,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        result = await process_file_async(content, file.filename or f"upload_{job_id}", job_id)

        jobs[job_id].update(
            {"status": "completed", "result": result, "completed_at": datetime.now(timezone.utc).isoformat()}
        )

        return JobResponse(job_id=job_id, status="completed", message=f"Successfully transformed {file.filename}", result=result)

    except Exception as exc:
        if "job_id" in locals():
            jobs[job_id].update(
                {"status": "failed", "error": str(exc), "failed_at": datetime.now(timezone.utc).isoformat()}
            )

        raise HTTPException(status_code=500, detail=f"Transformation failed: {exc!s}")


@app.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job_status(job_id: str) -> JobResponse:
    """Get job status and result"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]
    return JobResponse(job_id=job_id, status=job["status"], message=f"Job {job['status']}", result=job.get("result"))


# ΛTAG: lens_pipeline
async def process_file_async(
    content: bytes, filename: str, job_id: str, options: Optional[dict[str, Any]] = None
) -> dict[str, Any]:
    """Process file content asynchronously using the ΛLens engine."""

    suffix = Path(filename).suffix or ".tmp"
    options = options or {}

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        tmp_file.write(content)
        temp_path = Path(tmp_file.name)

    try:
        dashboard = await lens_engine.transform(str(temp_path), options)

        symbols = [symbol.to_dict() for symbol in dashboard.symbols]
        widgets = widget_factory.suggest_widgets(dashboard.symbols)
        web_dashboard = await web_renderer.render(dashboard)
        xr_scene = await xr_renderer.render(dashboard)

        return {
            "job_id": job_id,
            "dashboard": {
                "id": dashboard.id,
                "source_file": dashboard.source_file,
                "lambda_signature": dashboard.lambda_signature,
                "metadata": dashboard.metadata,
                "symbols": symbols,
                "relationships": dashboard.relationships,
            },
            "widgets": widgets,
            "web_dashboard": web_dashboard,
            "xr_scene": xr_scene,
            "processed_at": datetime.now(timezone.utc).isoformat(),
        }

    finally:
        temp_path.unlink(missing_ok=True)


if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting ΛLens API Server...")
    print("🔗 API will be available at: http://localhost:8000")
    print("📚 Documentation at: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
