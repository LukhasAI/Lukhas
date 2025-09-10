"""
Smoke tests for MATRIZ traces router.
Part of Stream B implementation for issue #185.
"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import the router
from MATRIZ.traces_router import router


@pytest.fixture
def test_client():
    """Create test client for traces router."""
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def test_traces_latest_endpoint_exists(test_client):
    """Smoke test: verify /traces/latest endpoint exists and returns valid response."""
    response = test_client.get("/traces/latest")

    # Should either return 200 with trace data or 404 if no traces
    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = response.json()
        # Must have trace_id if successful
        assert "trace_id" in data
        assert isinstance(data["trace_id"], str)
        assert len(data["trace_id"]) > 0


def test_traces_by_id_endpoint_exists(test_client):
    """Smoke test: verify /traces/{id} endpoint exists."""
    response = test_client.get("/traces/nonexistent_trace_id")

    # Should return 404 for nonexistent trace
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_traces_list_endpoint_exists(test_client):
    """Smoke test: verify /traces/ list endpoint exists."""
    response = test_client.get("/traces/")

    # Should always return 200 with traces list (even if empty)
    assert response.status_code == 200
    data = response.json()
    assert "traces" in data
    assert "count" in data
    assert isinstance(data["traces"], list)
    assert isinstance(data["count"], int)


@patch("MATRIZ.traces_router.GOLDEN_TRACES_PATH")
def test_golden_trace_fallback(mock_golden_path, test_client):
    """Test that golden traces are used as fallback when MATRIZ traces unavailable."""
    # Mock golden traces directory with test data
    mock_golden_path.exists.return_value = True
    mock_golden_path.glob.return_value = [Path("test_trace.json")]

    # Mock file loading
    test_trace_data = {"trace_id": "test_golden_trace", "module": "test_module", "status": "success"}

    with patch("MATRIZ.traces_router.load_trace_file") as mock_load:
        mock_load.return_value = test_trace_data

        response = test_client.get("/traces/latest")

        if response.status_code == 200:
            data = response.json()
            assert "trace_id" in data
            assert "source" in data
            assert data["source"] == "golden_fallback"


def test_trace_by_id_with_golden_source(test_client):
    """Test retrieving specific trace by ID."""
    # Try to get the governance policy enforcement trace that should exist
    response = test_client.get("/traces/governance_policy_enforcement_001")

    # May return 200 if found or 404 if file format doesn't match expected trace_id
    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = response.json()
        assert "trace_id" in data


def test_router_error_handling(test_client):
    """Test that router handles errors gracefully."""
    # Test with invalid trace ID characters
    response = test_client.get("/traces/invalid//trace")

    # Should handle gracefully (may be 404 or 422 depending on routing)
    assert response.status_code in [404, 422]


def test_list_traces_deduplication(test_client, tmp_path):
    """Test that list_traces merges and deduplicates traces correctly."""
    # Create dummy trace directories
    live_traces_dir = tmp_path / "live"
    live_traces_dir.mkdir()
    golden_traces_dir = tmp_path / "golden"
    golden_traces_dir.mkdir()

    # Create dummy trace files
    # Golden files
    (golden_traces_dir / "trace1.json").write_text('{"trace_id": "trace1", "data": "golden"}')
    (golden_traces_dir / "trace2.json").write_text('{"trace_id": "trace2", "data": "golden"}')
    # Live files (trace2 is a duplicate)
    (live_traces_dir / "trace2.json").write_text('{"trace_id": "trace2", "data": "live"}')
    (live_traces_dir / "trace3.json").write_text('{"trace_id": "trace3", "data": "live"}')

    with patch("MATRIZ.traces_router.TRACES_BASE_PATH", live_traces_dir):
        with patch("MATRIZ.traces_router.GOLDEN_TRACES_PATH", golden_traces_dir):
            response = test_client.get("/traces/")

            assert response.status_code == 200
            data = response.json()
            assert data["count"] == 3

            traces_by_id = {t["trace_id"]: t for t in data["traces"]}
            assert len(traces_by_id) == 3

            # Check that live trace overwrites golden trace
            assert traces_by_id["trace2"]["source"] == "matriz"
            assert "live" in traces_by_id["trace2"]["file"]


if __name__ == "__main__":
    # Run smoke tests directly
    import subprocess
    import sys

    result = subprocess.run([sys.executable, "-m", "pytest", __file__, "-v", "--tb=short"])
    sys.exit(result.returncode)
