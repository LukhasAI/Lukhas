import json
import time
from pathlib import Path
from fastapi import FastAPI
from fastapi.testclient import TestClient
import os
import shutil

from matriz.traces_router import router

# Setup the test app
app = FastAPI()
app.include_router(router)
client = TestClient(app)

LIVE_DIR = Path("reports/matriz/traces")

def setup_function():
    """Create a clean live directory for tests."""
    if LIVE_DIR.exists():
        shutil.rmtree(LIVE_DIR)
    LIVE_DIR.mkdir(parents=True, exist_ok=True)

def teardown_function():
    """Remove the live directory after tests."""
    if LIVE_DIR.exists():
        shutil.rmtree(LIVE_DIR)

def test_get_latest_trace_fallback_to_golden():
    """
    Tests the /traces/latest endpoint when the live directory is empty.
    It should return the default golden trace.
    """
    response = client.get("/traces/latest")
    assert response.status_code == 200
    data = response.json()
    assert data["trace_id"] == "consciousness_20250910_001"

def test_get_latest_trace_from_live_dir():
    """
    Tests the /traces/latest endpoint when there are files in the live directory.
    """
    # Create some dummy trace files
    trace1_data = {"trace_id": "live_trace_1"}
    trace2_data = {"trace_id": "live_trace_2"}

    (LIVE_DIR / "trace1.json").write_text(json.dumps(trace1_data))
    time.sleep(0.1) # Ensure modification times are different
    (LIVE_DIR / "trace2.json").write_text(json.dumps(trace2_data))

    response = client.get("/traces/latest")
    assert response.status_code == 200
    data = response.json()
    assert data["trace_id"] == "live_trace_2"

def test_get_trace_by_valid_id():
    """
    Tests retrieving a specific trace by a valid ID from the golden directory.
    """
    trace_id = "memory_golden_trace"
    response = client.get(f"/traces/{trace_id}")
    assert response.status_code == 200
    data = response.json()

    from pathlib import Path
    golden_file = Path(f"tests/golden/tier1/{trace_id}.json")
    with open(golden_file, "r") as f:
        golden_data = json.load(f)

    assert data == golden_data

def test_get_trace_by_invalid_id():
    """
    Tests retrieving a trace with an ID that does not exist.
    """
    trace_id = "this-trace-does-not-exist"
    response = client.get(f"/traces/{trace_id}")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == f"Trace with ID '{trace_id}' not found"
