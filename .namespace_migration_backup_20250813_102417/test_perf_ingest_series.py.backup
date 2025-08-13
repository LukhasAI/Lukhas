"""Tests for performance ingestion and series API."""

from fastapi.testclient import TestClient


def test_perf_ingest_and_series(monkeypatch, tmp_path):
    """Test k6 summary ingestion and series retrieval."""
    monkeypatch.setenv("FLAG_OPS_PERF_INGEST", "true")
    monkeypatch.setenv("LUKHAS_API_KEY", "dev")
    monkeypatch.setenv("LUKHAS_PERF_DIR", str(tmp_path))

    # Import after setting env vars
    from lukhas.api.app import app

    c = TestClient(app)

    # Minimal synthetic k6 summary
    payload = {
        "metrics": {
            "http_req_duration{endpoint:health}": {"values": {"p(95)": 101}},
            "http_req_duration{endpoint:tools}": {"values": {"p(95)": 205}},
        }
    }

    # Test ingestion
    r = c.post("/ops/perf/k6", headers={"x-api-key": "dev"}, json=payload)
    assert r.status_code == 200
    result = r.json()
    assert result["ok"] is True
    assert result["saved"] is True
    assert result["points"] == 2

    # Test series retrieval
    r2 = c.get("/ops/perf/series", params={"endpoint": "health", "hours": 24})
    assert r2.status_code == 200
    pts = r2.json()["points"]
    assert len(pts) >= 1
    assert "p95" in pts[-1]
    assert pts[-1]["p95"] == 101

    # Test series for tools endpoint
    r3 = c.get("/ops/perf/series", params={"endpoint": "tools", "hours": 24})
    assert r3.status_code == 200
    pts = r3.json()["points"]
    assert len(pts) >= 1
    assert pts[-1]["p95"] == 205


def test_perf_auth_required(monkeypatch, tmp_path):
    """Test that perf endpoints require authentication."""
    monkeypatch.setenv("FLAG_OPS_PERF_INGEST", "true")
    monkeypatch.setenv("LUKHAS_API_KEY", "secret123")
    monkeypatch.setenv("LUKHAS_PERF_DIR", str(tmp_path))

    from lukhas.api.app import app

    c = TestClient(app)

    # Test without API key
    r = c.post("/ops/perf/k6", json={})
    assert r.status_code == 401

    # Test with wrong API key
    r = c.post("/ops/perf/k6", headers={"x-api-key": "wrong"}, json={})
    assert r.status_code == 401

    # Test with correct API key
    r = c.post("/ops/perf/k6", headers={"x-api-key": "secret123"}, json={"metrics": {}})
    assert r.status_code == 200


def test_perf_disabled_by_flag(monkeypatch, tmp_path):
    """Test that perf endpoints return 404 when disabled."""
    monkeypatch.setenv("FLAG_OPS_PERF_INGEST", "false")
    monkeypatch.setenv("LUKHAS_PERF_DIR", str(tmp_path))

    from lukhas.api.app import app

    c = TestClient(app)

    r = c.post("/ops/perf/k6", json={})
    assert r.status_code == 404
    assert "disabled" in r.json()["detail"].lower()
