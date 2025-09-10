import os
import json
from pathlib import Path
from fastapi import APIRouter, HTTPException

router = APIRouter()

# Define default directories
GOLDEN_DIR = Path("tests/golden/tier1")
LIVE_DIR_DEFAULT = Path("reports/matriz/traces")

def get_live_dir() -> Path:
    """Gets the live trace directory, allowing override from environment variable."""
    dir_path = os.environ.get("MATRIZ_TRACES_DIR")
    return Path(dir_path) if dir_path else LIVE_DIR_DEFAULT

def find_trace_file(trace_id: str) -> Path | None:
    """Finds a trace file by ID in live or golden directories."""
    live_dir = get_live_dir()

    # Check live directory first
    if live_dir.is_dir():
        live_file = live_dir / f"{trace_id}.json"
        if live_file.is_file():
            return live_file

    # Fallback to golden directory
    golden_file = GOLDEN_DIR / f"{trace_id}.json"
    if golden_file.is_file():
        return golden_file

    return None

@router.get("/traces/latest")
async def get_latest_trace():
    """
    Retrieves the latest trace by modification time from the live directory.
    Falls back to a default golden trace if the live directory is empty or absent.
    """
    live_dir = get_live_dir()
    latest_trace_file = None

    if live_dir.is_dir():
        # Find the most recently modified JSON file in the live directory
        json_files = list(live_dir.glob("*.json"))
        if json_files:
            latest_trace_file = max(json_files, key=lambda f: f.stat().st_mtime)

    # If no file was found in the live directory, fall back to the default golden trace
    if not latest_trace_file:
        latest_trace_file = GOLDEN_DIR / "consciousness_golden_trace.json"

    if not latest_trace_file.is_file():
        raise HTTPException(status_code=404, detail="Could not find a latest trace file.")

    try:
        with open(latest_trace_file, "r") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading latest trace file: {e}")

@router.get("/traces/{trace_id}")
async def get_trace_by_id(trace_id: str):
    """
    Retrieves a specific trace by its ID.
    Searches for the trace in the live directory first, then falls back to the golden directory.
    """
    trace_file = find_trace_file(trace_id)

    if not trace_file:
        raise HTTPException(status_code=404, detail=f"Trace with ID '{trace_id}' not found")

    try:
        with open(trace_file, "r") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading trace file: {e}")
