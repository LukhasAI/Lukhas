#!/usr/bin/env python3
"""
ΛLens API Server - Standalone Version
Standalone server script to avoid relative import issues
"""

import sys
from pathlib import Path

# Add the project root to Python path (walk up to repository root)
# Use .resolve().parents to avoid incorrect relative counting
project_root = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(project_root))

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from products.lambda.lambda_products_pack.lambda_core.Lens.lens_core import ΛLens as LensCore

# Import our modules directly
from products.lambda.lambda_products_pack.lambda_core.Lens.parsers.code_parser import CodeParser
from products.lambda.lambda_products_pack.lambda_core.Lens.parsers.csv_parser import CSVParser
from products.lambda.lambda_products_pack.lambda_core.Lens.parsers.data_parser import DataParser
from products.lambda.lambda_products_pack.lambda_core.Lens.parsers.markdown_parser import MarkdownParser
from products.lambda.lambda_products_pack.lambda_core.Lens.parsers.pdf_parser import PDFParser
from products.lambda.lambda_products_pack.lambda_core.Lens.parsers.text_parser import TextParser
from products.lambda.lambda_products_pack.lambda_core.Lens.renderers.web2d_renderer import Web2DRenderer
from products.lambda.lambda_products_pack.lambda_core.Lens.renderers.xr_renderer import XRRenderer
from products.lambda.lambda_products_pack.lambda_core.Lens.symbols.symbol_generator import SymbolGenerator
from products.lambda.lambda_products_pack.lambda_core.Lens.widgets.widget_factory import WidgetFactory


# Pydantic models
class JobRequest(BaseModel):
    file_type: str
    content: Optional[str] = None
    options: Optional[dict[str, Any]] = {}


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


# Initialize components
lens_core = LensCore()
symbol_generator = SymbolGenerator()
widget_factory = WidgetFactory()
web_renderer = Web2DRenderer()
xr_renderer = XRRenderer()

# Job storage (in production, use a database)
jobs = {}

# Create FastAPI app
app = FastAPI(
    title="ΛLens API", description="Symbolic File Transformation and Dashboard Generation API", version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
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
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "components": {
            "lens_core": "active",
            "symbol_generator": "active",
            "widget_factory": "active",
            "renderers": "active",
        },
    }


@app.post("/transform", response_model=JobResponse)
async def transform_file(file: UploadFile = File(...), file_type: Optional[str] = None):
    """Transform uploaded file into symbolic dashboard"""
    try:
        # Generate job ID
        job_id = str(uuid.uuid4())

        # Read file content
        content = await file.read()
        content_str = content.decode("utf-8")

        # Determine file type if not provided
        if not file_type:
            file_extension = Path(file.filename).suffix.lower()
            file_type_map = {
                ".txt": "text",
                ".py": "code",
                ".js": "code",
                ".ts": "code",
                ".json": "data",
                ".csv": "csv",
                ".md": "markdown",
                ".pdf": "pdf",
            }
            file_type = file_type_map.get(file_extension, "text")

        # Store job
        jobs[job_id] = {
            "status": "processing",
            "file_type": file_type,
            "filename": file.filename,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        # Process file based on type
        result = await process_file_async(content_str, file_type, job_id)

        # Update job with result
        jobs[job_id].update(
            {"status": "completed", "result": result, "completed_at": datetime.now(timezone.utc).isoformat()}
        )

        return JobResponse(
            job_id=job_id, status="completed", message=f"Successfully transformed {file.filename}", result=result
        )

    except Exception as e:
        # Update job with error
        if "job_id" in locals():
            jobs[job_id].update(
                {"status": "failed", "error": str(e), "failed_at": datetime.now(timezone.utc).isoformat()}
            )

        raise HTTPException(status_code=500, detail=f"Transformation failed: {e!s}")


@app.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job_status(job_id: str):
    """Get job status and result"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]
    return JobResponse(job_id=job_id, status=job["status"], message=f"Job {job['status']}", result=job.get("result"))


async def process_file_async(content: str, file_type: str, job_id: str) -> dict[str, Any]:
    """Process file content asynchronously"""
    try:
        # Parse content based on type
        if file_type == "text":
            parser = TextParser()
        elif file_type == "code":
            parser = CodeParser()
        elif file_type == "data":
            parser = DataParser()
        elif file_type == "csv":
            parser = CSVParser()
        elif file_type == "markdown":
            parser = MarkdownParser()
        elif file_type == "pdf":
            parser = PDFParser()
        else:
            parser = TextParser()

        # Parse the content
        parsed_data = parser.parse(content)

        # Generate symbols
        symbols = symbol_generator.generate_symbols(parsed_data)

        # Create widgets
        widgets = widget_factory.create_widgets(symbols)

        # Generate dashboard
        dashboard = web_renderer.render_dashboard(
            {
                "title": f"ΛLens Dashboard - {file_type.upper(}}",
                "symbols": symbols,
                "widgets": widgets,
                "metadata": {"file_type": file_type, "processed_at": datetime.now(timezone.utc).isoformat(), "job_id": job_id},
            }
        )

        return {
            "dashboard": dashboard,
            "symbols_count": len(symbols),
            "widgets_count": len(widgets),
            "file_type": file_type,
            "processing_time": "completed",
        }

    except Exception as e:
        raise Exception(f"Processing failed: {e!s}")


if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting ΛLens API Server...")
    print("🔗 API will be available at: http://localhost:8000")
    print("📚 Documentation at: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
