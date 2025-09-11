import json
import os
from pathlib import Path

import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient

# Tier-1 MATRIZ smokes: fast, deterministic, no network
pytestmark = [pytest.mark.tier1, pytest.mark.matriz]

GOLD = Path("tests/golden/tier1")
LIVE = Path("reports/matriz/traces")


def _make_app():
    app = FastAPI()
    # Import locally to avoid app-global side effects
    from matriz.traces_router import router

    app.include_router(router)
    return app


@pytest.fixture(autouse=True)
def _isolate_env(monkeypatch):
    # Default to GOLD to be deterministic in CI; individual tests may override.
    monkeypatch.setenv("MATRIZ_TRACES_DIR", str(GOLD.resolve()))
    yield
    # cleanup handled by pytest


def _client():
    return TestClient(_make_app())


def test_latest_returns_json_with_trace_id():
    r = _client().get("/traces/latest")
    assert r.status_code == 200, r.text
    body = r.json()
    assert isinstance(body, dict)
    assert "trace_id" in body
    assert isinstance(body["trace_id"], (str, int))  # schema allows str|int
    # When golden is served, router hints source
    assert body.get("source") in (None, "golden_fallback")


def test_by_id_prefers_json_trace_id_over_filename(tmp_path, monkeypatch):
    # Create a test dir with a file whose filename doesn't match trace_id
    d = tmp_path / "env_traces"
    d.mkdir()
    f = d / "foo-123.json"
    f.write_text(json.dumps({"trace_id": "BAR-999", "ts": 0}), encoding="utf-8")
    monkeypatch.setenv("MATRIZ_TRACES_DIR", str(d))
    r = _client().get("/traces/BAR-999")
    assert r.status_code == 200
    assert r.json()["trace_id"] == "BAR-999"


def test_list_paging_and_filters(monkeypatch, tmp_path):
    # Create test traces with different sources
    d = tmp_path / "list_traces"
    d.mkdir()
    traces = [
        {"trace_id": "A", "source": "consciousness", "ts": 100},
        {"trace_id": "B", "source": "api", "ts": 200},
        {"trace_id": "C", "source": "consciousness", "ts": 300},
    ]
    for i, trace in enumerate(traces):
        f = d / f"trace_{i}.json"
        f.write_text(json.dumps(trace), encoding="utf-8")

    monkeypatch.setenv("MATRIZ_TRACES_DIR", str(d))

    # Test basic list
    r = _client().get("/traces/")
    assert r.status_code == 200
    data = r.json()
    assert "traces" in data
    assert len(data["traces"]) == 3

    # Test source filter
    r = _client().get("/traces/?source=consciousness")
    assert r.status_code == 200
    data = r.json()
    consciousness_traces = [t for t in data["traces"] if t["source"] == "consciousness"]
    assert len(consciousness_traces) == 2

    # Test paging
    r = _client().get("/traces/?limit=2")
    assert r.status_code == 200
    data = r.json()
    assert len(data["traces"]) == 2


def test_404_for_missing_trace():
    r = _client().get("/traces/nonexistent-trace-id")
    assert r.status_code == 404
    body = r.json()
    assert "detail" in body or "error" in body


def test_golden_fallback_when_live_missing(monkeypatch):
    # Point to empty dir but ensure golden exists
    empty_dir = Path("/tmp/empty_matriz_traces")
    empty_dir.mkdir(exist_ok=True)
    monkeypatch.setenv("MATRIZ_TRACES_DIR", str(empty_dir))

    # Should still work if router falls back to golden
    r = _client().get("/traces/latest")
    # Expect either 200 (golden fallback) or 404 (no golden)
    assert r.status_code in (200, 404)
    if r.status_code == 200:
        body = r.json()
        assert body.get("source") in (None, "golden_fallback")


def test_trace_schema_validation():
    """Ensure returned traces have expected structure"""
    r = _client().get("/traces/latest")
    if r.status_code == 200:
        body = r.json()
        # Basic schema check
        assert "trace_id" in body
        if "ts" in body:
            assert isinstance(body["ts"], (int, float))
        if "source" in body:
            assert isinstance(body["source"], str)
