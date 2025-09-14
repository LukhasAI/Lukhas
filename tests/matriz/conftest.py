"""MATRIZ test configuration and fixtures."""

import os
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def matriz_test_data_dir():
    """Directory containing test trace data."""
    return Path(__file__).parent.parent.parent / "tests" / "golden" / "tier1"


@pytest.fixture
def clean_matriz_env(monkeypatch):
    """Clean MATRIZ environment variables for isolated testing."""
    # Clear any existing MATRIZ env vars
    for key in list(os.environ.keys()):
        if key.startswith("MATRIZ_"):
            monkeypatch.delenv(key, raising=False)
    yield


@pytest.fixture
def temp_traces_dir(tmp_path):
    """Temporary directory for test traces."""
    traces_dir = tmp_path / "traces"
    traces_dir.mkdir()
    return traces_dir


@pytest.fixture
def sample_trace_data():
    """Sample trace data for testing."""
    return {
        "trace_id": "test-trace-001",
        "source": "test",
        "ts": 1694097600,
        "data": {"action": "test_action", "result": "success"},
    }
