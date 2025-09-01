#!/usr/bin/env python3
"""
ΛLens API Endpoints
FastAPI routes for ΛLens operations
"""

import os

# Import from parent directory
import sys
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from lens_core import ΛLens

from .schemas import JobRequest, JobResponse

# Create router
router = APIRouter()

# Initialize ΛLens engine
lens_engine = ΛLens()


@router.post("/jobs", response_model=JobResponse)
async def create_job(
    background_tasks: BackgroundTasks, file: UploadFile = File(...), request: Optional[JobRequest] = None
):
    """
    Create a new file transformation job

    Upload a file and get a symbolic dashboard
    """
    try:
        # Generate job ID
        job_id = str(uuid.uuid4())

        # Read file content
        content = await file.read()

        # Save file temporarily
        temp_path = f"/tmp/{job_id}_{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(content)

        # Process file in background
        background_tasks.add_task(process_file_job, job_id, temp_path, request)

        return JobResponse(job_id=job_id, status="accepted", message="File transformation job created successfully")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create job: {e!s}")


@router.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    """
    Get job status and results

    Returns the current status of a transformation job
    """
    try:
        # Check if job exists in cache
        dashboard = lens_engine.get_dashboard(job_id)

        if dashboard:
            return {
                "job_id": job_id,
                "status": "completed",
                "dashboard": {
                    "id": dashboard.id,
                    "symbols_count": len(dashboard.symbols),
                    "relationships_count": len(dashboard.relationships),
                    "lambda_signature": dashboard.lambda_signature,
                },
            }
        else:
            return {"job_id": job_id, "status": "processing", "message": "Job is still being processed"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job status: {e!s}")


@router.get("/jobs/{job_id}/photon")
async def get_photon_document(job_id: str):
    """
    Get the Photon document for a completed job

    Returns the interactive dashboard configuration
    """
    try:
        dashboard = lens_engine.get_dashboard(job_id)

        if not dashboard:
            raise HTTPException(status_code=404, detail="Job not found or not completed")

        # Convert dashboard to Photon format
        photon = dashboard_to_photon(dashboard)

        return JSONResponse(content=photon)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get Photon document: {e!s}")


@router.post("/jobs/{job_id}/export")
async def export_dashboard(job_id: str, format: str = "gltf"):
    """
    Export dashboard in specified format

    Supported formats: gltf, json
    """
    try:
        dashboard = lens_engine.get_dashboard(job_id)

        if not dashboard:
            raise HTTPException(status_code=404, detail="Job not found or not completed")

        if format == "gltf":
            # Export as glTF for AR/VR
            gltf_data = await lens_engine.ar_renderer.export_gltf(dashboard)
            return JSONResponse(content=gltf_data.decode("utf-8"))
        elif format == "json":
            # Export as JSON
            json_data = await lens_engine.web_renderer.export_json(dashboard, f"/tmp/{job_id}.json")
            with open(f"/tmp/{job_id}.json") as f:
                return JSONResponse(content=f.read())
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export dashboard: {e!s}")


async def process_file_job(job_id: str, file_path: str, request: Optional[JobRequest]):
    """
    Background task to process a file transformation job
    """
    try:
        # Determine options
        options = {}
        if request:
            options.update(request.dict())

        # Transform file
        dashboard = await lens_engine.transform(file_path, options)

        # Clean up temp file
        Path(file_path).unlink(missing_ok=True)

        print(f"Job {job_id} completed successfully")

    except Exception as e:
        print(f"Job {job_id} failed: {e!s}")


def dashboard_to_photon(dashboard) -> Dict[str, Any]:
    """
    Convert ΛLens dashboard to Photon document format
    """
    photon = {
        "photon_version": "1.0.0",
        "title": f"ΛLens Dashboard {dashboard.id}",
        "description": f"Symbolic representation of {dashboard.source_file}",
        "nodes": [],
        "edges": [],
        "layout": {"positions_2d": {}},
    }

    # Convert symbols to nodes
    for i, symbol in enumerate(dashboard.symbols):
        node = {
            "id": symbol.id,
            "kind": symbol.type.value,
            "label": symbol.content[:50],
            "properties": {"content": symbol.content, "confidence": symbol.confidence},
        }

        if symbol.metadata:
            node["properties"].update(symbol.metadata)

        photon["nodes"].append(node)

        # Add position
        if symbol.position:
            photon["layout"]["positions_2d"][symbol.id] = {
                "x": symbol.position[0] * 100,  # Scale for UI
                "y": symbol.position[1] * 100,
            }

    # Convert relationships to edges
    for rel in dashboard.relationships:
        edge = {
            "id": f"edge_{rel['source']}_{rel['target']}",
            "source": rel["source"],
            "target": rel["target"],
            "kind": rel.get("type", "related"),
            "label": rel.get("type", "related"),
        }
        photon["edges"].append(edge)

    return photon
