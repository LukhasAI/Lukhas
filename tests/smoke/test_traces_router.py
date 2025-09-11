"""
Smoke tests for MATRIZ traces router.
Part of Stream B implementation for issue #185.
"""

import json
import os
import sys
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


@pytest.fixture
def test_client():
    """Create test client for traces router."""
    from fastapi import FastAPI

    # Import router lazily from file to avoid sys.path issues under some runners
    root = Path(__file__).parent.parent.parent
    module_path = root / "matriz" / "traces_router.py"
    import importlib.util as _ilu

    spec = _ilu.spec_from_file_location("_matriz_traces_router", str(module_path))
    assert spec and spec.loader
    mod = _ilu.module_from_spec(spec)
    spec.loader.exec_module(mod)
    router = mod.router

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
    """Smoke test: verify /traces/ list endpoint exists and returns metadata."""
    response = test_client.get("/traces/")
    assert response.status_code == 200
    data = response.json()
    # New shape: total/offset/limit/next_offset/traces
    assert {"total", "offset", "limit", "next_offset", "traces"}.issubset(data.keys())
    assert isinstance(data["traces"], list)


def test_golden_trace_fallback(test_client, tmp_path, monkeypatch):
    """Test that golden traces are used as fallback when ENV/LIVE are empty."""
    # Point GOLD to a temp dir with a single file
    gold_dir = tmp_path / "gold"
    gold_dir.mkdir()
    p = gold_dir / "gold.json"
    _write_json(p, {"trace_id": "test_golden_trace", "timestamp": int(time.time())})

    # Ensure ENV is unset, and LIVE points to empty
    monkeypatch.delenv("MATRIZ_TRACES_DIR", raising=False)

    # Patch module constants in the same module instance used by the app
    # Load module instance as in fixture
    root = Path(__file__).parent.parent.parent
    module_path = root / "matriz" / "traces_router.py"
    import importlib.util as _ilu

    spec = _ilu.spec_from_file_location("_matriz_traces_router", str(module_path))
    mod = _ilu.module_from_spec(spec)
    spec.loader.exec_module(mod)

    monkeypatch.setattr(mod, "TRACES_BASE_PATH", tmp_path / "live_empty", raising=True)
    monkeypatch.setattr(mod, "GOLDEN_TRACES_PATH", gold_dir, raising=True)

    # Build a fresh app using this module's router to bind its globals
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    app = FastAPI()
    app.include_router(mod.router)
    client = TestClient(app)

    response = client.get("/traces/latest")
    assert response.status_code == 200
    data = response.json()
    assert data.get("trace_id") == "test_golden_trace"
    assert data.get("source") == "golden_fallback"


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


def test_env_override_dir_for_latest(test_client, monkeypatch):
    """When MATRIZ_TRACES_DIR is set, router should read traces from that directory.

    We point the override to the repository's golden traces and expect a 200
    with a trace_id in the returned JSON.
    """
    # Use repo-relative path to goldens
    override_dir = str(Path("tests/golden/tier1").resolve())
    monkeypatch.setenv("MATRIZ_TRACES_DIR", override_dir)

    response = test_client.get("/traces/latest")
    assert response.status_code == 200
    data = response.json()
    assert "trace_id" in data and isinstance(data["trace_id"], str) and data["trace_id"]


def _write_json(p: Path, data: dict) -> None:
    p.write_text(json.dumps(data), encoding="utf-8")


def test_latest_precedence_env_over_live_over_gold(test_client, tmp_path, monkeypatch):
    # Create a newer file in ENV dir
    env_dir = tmp_path / "env"
    env_dir.mkdir()
    trace_env = env_dir / "env_trace.json"
    _write_json(
        trace_env,
        {"trace_id": "env_latest", "timestamp": int(time.time()), "op": "x"},
    )
    # Set ENV to override
    monkeypatch.setenv("MATRIZ_TRACES_DIR", str(env_dir))

    # Even if LIVE/GOLD have files, ENV should win
    response = test_client.get("/traces/latest")
    assert response.status_code == 200
    assert response.json()["trace_id"] == "env_latest"


def test_latest_uses_mtime_desc_tiebreak_name(test_client, tmp_path, monkeypatch):
    env_dir = tmp_path / "env2"
    env_dir.mkdir()
    # Two files with identical mtime; a.json should win by tiebreak (name asc)
    a = env_dir / "a.json"
    b = env_dir / "b.json"
    now = int(time.time())
    _write_json(a, {"trace_id": "A_ID", "timestamp": now})
    _write_json(b, {"trace_id": "B_ID", "timestamp": now})
    # Force same mtime
    os.utime(a, (now, now))
    os.utime(b, (now, now))
    monkeypatch.setenv("MATRIZ_TRACES_DIR", str(env_dir))

    r = test_client.get("/traces/latest")
    assert r.status_code == 200
    assert r.json()["trace_id"] == "A_ID"


def test_by_id_matches_trace_id_field_over_filename(test_client, tmp_path, monkeypatch):
    env_dir = tmp_path / "env3"
    env_dir.mkdir()
    f = env_dir / "filename_is_different.json"
    _write_json(f, {"trace_id": "RID123", "timestamp": int(time.time())})
    monkeypatch.setenv("MATRIZ_TRACES_DIR", str(env_dir))

    r = test_client.get("/traces/RID123")
    assert r.status_code == 200
    assert r.json()["trace_id"] == "RID123"


def test_404_when_empty_everywhere(test_client, tmp_path, monkeypatch):
    # Build isolated app with module constants pointing to empty dirs
    live = tmp_path / "live"
    gold = tmp_path / "gold"
    live.mkdir()
    gold.mkdir()

    monkeypatch.delenv("MATRIZ_TRACES_DIR", raising=False)

    root = Path(__file__).parent.parent.parent
    module_path = root / "matriz" / "traces_router.py"
    import importlib.util as _ilu

    spec = _ilu.spec_from_file_location("_matriz_traces_router_empty", str(module_path))
    mod = _ilu.module_from_spec(spec)
    spec.loader.exec_module(mod)
    monkeypatch.setattr(mod, "TRACES_BASE_PATH", live, raising=True)
    monkeypatch.setattr(mod, "GOLDEN_TRACES_PATH", gold, raising=True)

    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    app = FastAPI()
    app.include_router(mod.router)
    client = TestClient(app)

    r = client.get("/traces/latest")
    assert r.status_code == 404


def test_413_when_file_too_large(test_client, tmp_path, monkeypatch):
    env_dir = tmp_path / "big"
    env_dir.mkdir()
    big = env_dir / "big.json"
    # Create a >5MiB JSON file (approximately 5.1MiB)
    payload = {"trace_id": "BIG", "timestamp": int(time.time()), "pad": "x" * (6 * 1024 * 1024)}
    _write_json(big, payload)
    monkeypatch.setenv("MATRIZ_TRACES_DIR", str(env_dir))

    r = test_client.get("/traces/latest")
    assert r.status_code == 413


def test_422_on_malformed_json(test_client, tmp_path, monkeypatch):
    env_dir = tmp_path / "bad"
    env_dir.mkdir()
    bad = env_dir / "bad.json"
    bad.write_text("{" "not json" "}", encoding="utf-8")
    monkeypatch.setenv("MATRIZ_TRACES_DIR", str(env_dir))

    r = test_client.get("/traces/latest")
    assert r.status_code == 422


def test_env_var_points_to_file_not_dir(test_client, tmp_path, monkeypatch):
    file_path = tmp_path / "just_a_file.json"
    _write_json(file_path, {"trace_id": "X", "timestamp": int(time.time())})
    monkeypatch.setenv("MATRIZ_TRACES_DIR", str(file_path))

    r = test_client.get("/traces/latest")
    assert r.status_code == 400
    assert r.json().get("detail", {}).get("error") == "invalid_dir"


def test_path_traversal_rejected(test_client):
    # Encode slashes so it remains a single path segment
    # Use invalid character in ID to trigger bad_id
    r = test_client.get("/traces/abc$def")
    assert r.status_code == 400
    assert r.json().get("detail", {}).get("error") == "bad_id"


def test_list_paging_and_total(test_client, tmp_path, monkeypatch):
    # Build isolated module/app with only ENV directory populated
    env_dir = tmp_path / "envlist"
    live_dir = tmp_path / "live_empty"
    gold_dir = tmp_path / "gold_empty"
    env_dir.mkdir()
    live_dir.mkdir()
    gold_dir.mkdir()
    now = int(time.time())
    for i in range(5):
        p = env_dir / f"t{i}.json"
        _write_json(p, {"trace_id": f"ID{i}", "timestamp": now + i})
        os.utime(p, (now + i, now + i))

    root = Path(__file__).parent.parent.parent
    module_path = root / "matriz" / "traces_router.py"
    import importlib.util as _ilu

    spec = _ilu.spec_from_file_location("_matriz_traces_router_list", str(module_path))
    mod = _ilu.module_from_spec(spec)
    spec.loader.exec_module(mod)
    monkeypatch.setenv("MATRIZ_TRACES_DIR", str(env_dir))
    monkeypatch.setattr(mod, "TRACES_BASE_PATH", live_dir, raising=True)
    monkeypatch.setattr(mod, "GOLDEN_TRACES_PATH", gold_dir, raising=True)

    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    app = FastAPI()
    app.include_router(mod.router)
    client = TestClient(app)

    r = client.get("/traces/?offset=1&limit=2")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 5
    assert data["offset"] == 1
    assert data["limit"] == 2
    assert data["next_offset"] == 3
    # Expect IDs in order: latest first (ID4, ID3, ID2, ...)
    returned_ids = [t["id"] for t in data["traces"]]
    assert returned_ids == ["ID3", "ID2"]


def test_list_filter_source_env_live_golden(test_client, tmp_path, monkeypatch):
    # Isolated app: only ENV populated
    env_dir = tmp_path / "envfilter"
    env_dir.mkdir()
    live_dir = tmp_path / "live_empty"
    live_dir.mkdir()
    gold_dir = tmp_path / "gold_empty"
    gold_dir.mkdir()
    _write_json(env_dir / "a.json", {"trace_id": "ENV1", "timestamp": int(time.time())})

    root = Path(__file__).parent.parent.parent
    module_path = root / "matriz" / "traces_router.py"
    import importlib.util as _ilu

    spec = _ilu.spec_from_file_location("_matriz_traces_router_filter", str(module_path))
    mod = _ilu.module_from_spec(spec)
    spec.loader.exec_module(mod)
    monkeypatch.setenv("MATRIZ_TRACES_DIR", str(env_dir))
    monkeypatch.setattr(mod, "TRACES_BASE_PATH", live_dir, raising=True)
    monkeypatch.setattr(mod, "GOLDEN_TRACES_PATH", gold_dir, raising=True)
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    app = FastAPI()
    app.include_router(mod.router)
    client = TestClient(app)

    r_env = client.get("/traces/?source=env")
    assert r_env.status_code == 200
    d_env = r_env.json()
    assert d_env["total"] >= 1
    assert all(item["source"] == "env" for item in d_env["traces"]) or d_env["total"] == 0

    r_live = client.get("/traces/?source=live")
    assert r_live.status_code == 200
    d_live = r_live.json()
    # With only ENV populated, filtering live should be empty
    assert d_live["total"] == 0


def test_list_query_matches_id_and_filename(test_client, tmp_path, monkeypatch):
    env_dir = tmp_path / "envq"
    env_dir.mkdir()
    a = env_dir / "alpha_file.json"
    b = env_dir / "beta_file.json"
    _write_json(a, {"trace_id": "ALPHA_ID", "timestamp": int(time.time())})
    _write_json(b, {"trace_id": "BETA_ID", "timestamp": int(time.time())})
    monkeypatch.setenv("MATRIZ_TRACES_DIR", str(env_dir))

    r1 = test_client.get("/traces/?q=alpha")
    assert r1.status_code == 200
    ids1 = [t["id"] for t in r1.json()["traces"]]
    assert any("ALPHA" in i for i in ids1) or any("alpha_file" in i for i in ids1)

    r2 = test_client.get("/traces/?q=beta_file")
    assert r2.status_code == 200
    ids2 = [t["id"] for t in r2.json()["traces"]]
    # query matches filename substring; id returned is trace_id value
    assert any(i == "BETA_ID" for i in ids2)


def test_list_stable_ordering_with_paging(test_client, tmp_path, monkeypatch):
    env_dir = tmp_path / "envorder"
    env_dir.mkdir()
    now = int(time.time())
    # Same mtime for two files; name asc tie-break means a.json before b.json
    a = env_dir / "a.json"
    b = env_dir / "b.json"
    _write_json(a, {"trace_id": "A", "timestamp": now})
    _write_json(b, {"trace_id": "B", "timestamp": now})
    os.utime(a, (now, now))
    os.utime(b, (now, now))
    monkeypatch.setenv("MATRIZ_TRACES_DIR", str(env_dir))

    page1 = test_client.get("/traces/?offset=0&limit=1").json()
    page2 = test_client.get("/traces/?offset=1&limit=1").json()
    # page1 should be A then page2 B due to filename tie-break
    assert page1["traces"][0]["id"] == "A"
    assert page2["traces"][0]["id"] == "B"


if __name__ == "__main__":
    # Run smoke tests directly
    import subprocess
    import sys

    result = subprocess.run([sys.executable, "-m", "pytest", __file__, "-v", "--tb=short"], check=False)
    sys.exit(result.returncode)
