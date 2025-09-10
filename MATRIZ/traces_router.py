"""
MATRIZ Traces Router
Provides API endpoints for retrieving golden traces and execution artifacts.
Part of Stream B implementation for issue #185.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/traces", tags=["traces"])

# Base paths for trace data
TRACES_BASE_PATH = Path("reports/matriz/traces")
GOLDEN_TRACES_PATH = Path("tests/golden/tier1")


def load_trace_file(file_path: Path) -> Optional[Dict[str, Any]]:
    """Load and validate a trace JSON file."""
    try:
        if not file_path.exists():
            return None

        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

        # Ensure trace_id is present
        if "trace_id" not in data:
            data["trace_id"] = f"trace_{file_path.stem}"

        return data
    except (OSError, json.JSONDecodeError) as e:
        logger.error(f"Failed to load trace file {file_path}: {e}")
        return None


@router.get("/latest")
async def get_latest_trace() -> JSONResponse:
    """
    Retrieve the most recent trace from the MATRIZ traces directory.

    Returns:
        JSON trace data with trace_id, or 404 if no traces available
    """
    try:
        # Look for trace files in reports/matriz/traces/
        if TRACES_BASE_PATH.exists():
            trace_files = list(TRACES_BASE_PATH.glob("*.json"))
            if trace_files:
                # Get most recent by modification time
                latest_file = max(trace_files, key=lambda p: p.stat().st_mtime)
                trace_data = load_trace_file(latest_file)

                if trace_data:
                    return JSONResponse(content=trace_data, status_code=status.HTTP_200_OK)

        # Fallback to golden traces if no MATRIZ traces
        if GOLDEN_TRACES_PATH.exists():
            golden_files = list(GOLDEN_TRACES_PATH.glob("*.json"))
            if golden_files:
                # Use first golden trace as fallback
                fallback_file = golden_files[0]
                trace_data = load_trace_file(fallback_file)

                if trace_data:
                    trace_data["source"] = "golden_fallback"
                    return JSONResponse(content=trace_data, status_code=status.HTTP_200_OK)

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No traces available")

    except Exception as e:
        logger.error(f"Error retrieving latest trace: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error retrieving trace"
        )


@router.get("/{trace_id}")
async def get_trace_by_id(trace_id: str) -> JSONResponse:
    """
    Retrieve a specific trace by its ID.

    Args:
        trace_id: The trace identifier

    Returns:
        JSON trace data, or 404 if trace not found
    """
    try:
        # Search in MATRIZ traces first
        if TRACES_BASE_PATH.exists():
            for trace_file in TRACES_BASE_PATH.glob("*.json"):
                trace_data = load_trace_file(trace_file)
                if trace_data and trace_data.get("trace_id") == trace_id:
                    return JSONResponse(content=trace_data, status_code=status.HTTP_200_OK)

        # Search in golden traces
        if GOLDEN_TRACES_PATH.exists():
            for golden_file in GOLDEN_TRACES_PATH.glob("*.json"):
                trace_data = load_trace_file(golden_file)
                if trace_data and trace_data.get("trace_id") == trace_id:
                    trace_data["source"] = "golden"
                    return JSONResponse(content=trace_data, status_code=status.HTTP_200_OK)

        # Try direct file lookup by trace_id
        potential_files = [TRACES_BASE_PATH / f"{trace_id}.json", GOLDEN_TRACES_PATH / f"{trace_id}.json"]

        for file_path in potential_files:
            trace_data = load_trace_file(file_path)
            if trace_data:
                if "source" not in trace_data:
                    trace_data["source"] = "direct_lookup"
                return JSONResponse(content=trace_data, status_code=status.HTTP_200_OK)

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Trace '{trace_id}' not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving trace {trace_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error retrieving trace"
        )


@router.get("/")
async def list_traces() -> JSONResponse:
    """
    List all available traces, merging live and golden traces.

    Returns:
        JSON list of available trace IDs and metadata
    """
    try:
        traces_by_id = {}

        # Collect from golden traces first
        if GOLDEN_TRACES_PATH.exists():
            for golden_file in GOLDEN_TRACES_PATH.glob("*.json"):
                trace_data = load_trace_file(golden_file)
                if trace_data:
                    trace_id = trace_data.get("trace_id", golden_file.stem)
                    traces_by_id[trace_id] = {
                        "trace_id": trace_id,
                        "source": "golden",
                        "file": str(golden_file),
                        "size": golden_file.stat().st_size,
                    }

        # Collect from MATRIZ traces, overwriting golden traces
        if TRACES_BASE_PATH.exists():
            for trace_file in TRACES_BASE_PATH.glob("*.json"):
                trace_data = load_trace_file(trace_file)
                if trace_data:
                    trace_id = trace_data.get("trace_id", trace_file.stem)
                    traces_by_id[trace_id] = {
                        "trace_id": trace_id,
                        "source": "matriz",
                        "file": str(trace_file),
                        "size": trace_file.stat().st_size,
                    }

        traces = list(traces_by_id.values())
        return JSONResponse(content={"traces": traces, "count": len(traces)}, status_code=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error listing traces: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error listing traces"
        )
