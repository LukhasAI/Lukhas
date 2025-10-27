"""
Smoke test for MATRIZ traces router

Exercises GET /traces/latest using golden fixtures. Deterministic, no network.
"""

from pathlib import Path

import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient


def _make_app() -> FastAPI:
    app = FastAPI()
    # Import locally to avoid app-global side effects
    from MATRIZ.traces_router import router

    app.include_router(router)
    return app


@pytest.fixture(autouse=True)
def _golden_env(monkeypatch):
    # Point to golden traces to make the smoke deterministic
    golden = Path("tests/golden/tier1").resolve()
    monkeypatch.setenv("MATRIZ_TRACES_DIR", str(golden))
    yield


@pytest.mark.smoke
@pytest.mark.matriz
def test_traces_latest_smoke():
    client = TestClient(_make_app())
    r = client.get("/traces/latest")
    assert r.status_code == 200, r.text
    body = r.json()
    assert isinstance(body, dict)
    assert "trace_id" in body


@pytest.mark.smoke
@pytest.mark.matriz
def test_traces_by_id_smoke():
    client = TestClient(_make_app())
    r = client.get("/traces/GOLD-0001")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body.get("trace_id") == "GOLD-0001"


@pytest.mark.smoke
@pytest.mark.matriz
def test_traces_list_smoke():
    client = TestClient(_make_app())
    r = client.get("/traces/?limit=5")
    assert r.status_code == 200, r.text
    data = r.json()
    assert isinstance(data, dict)
    assert "traces" in data
    traces = data["traces"]
    assert isinstance(traces, list)
    assert len(traces) >= 1
    first = traces[0]
    for key in ("id", "source", "size_bytes", "mtime", "path"):
        assert key in first
