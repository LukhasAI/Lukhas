"""Tests for LUKHAS Hybrid Registry Prototype."""
import json
import pathlib

from fastapi.testclient import TestClient

from services.registry.main import app

client = TestClient(app)


def load_sample_nodespec():
    """Load memory_adapter.json example."""
    p = pathlib.Path("docs/schemas/examples/memory_adapter.json")
    return json.loads(p.read_text())


def test_register_and_query():
    """Test full register→query workflow."""
    ns = load_sample_nodespec()
    r = client.post("/api/v1/registry/register", json=ns)
    assert r.status_code == 200
    regid = r.json()["registry_id"]
    assert "checkpoint_sig" in r.json()

    # Query by signal
    q = client.get("/api/v1/registry/query?signal=memory_stored")
    assert q.status_code == 200
    assert any(regid == x["registry_id"] for x in q.json()["results"])


def test_validate_ok():
    """Test NodeSpec validation endpoint."""
    ns = load_sample_nodespec()
    r = client.post("/api/v1/registry/validate", json=ns)
    assert r.status_code == 200
    assert r.json()["valid"] is True


def test_validate_fail():
    """Test validation with invalid NodeSpec."""
    bad_spec = {"node_type": "test", "metadata": {}}  # Missing required fields
    r = client.post("/api/v1/registry/validate", json=bad_spec)
    # Validation failures return 400 status code
    assert r.status_code == 400
    assert r.json()["valid"] is False
    assert "error" in r.json()


def test_register_requires_glymph():
    """Test that registration requires GLYMPH provenance."""
    ns = load_sample_nodespec()
    ns["provenance_manifest"]["glymph_enabled"] = False
    r = client.post("/api/v1/registry/register", json=ns)
    assert r.status_code == 403
    assert "GLYMPH" in r.json()["detail"]


def test_query_by_capability():
    """Test querying by capability."""
    ns = load_sample_nodespec()
    r = client.post("/api/v1/registry/register", json=ns)
    assert r.status_code == 200

    q = client.get("/api/v1/registry/query?capability=memory/episodic")
    assert q.status_code == 200
    results = q.json()["results"]
    assert len(results) >= 1


def test_deregister():
    """Test node deregistration."""
    ns = load_sample_nodespec()
    r = client.post("/api/v1/registry/register", json=ns)
    regid = r.json()["registry_id"]

    # Deregister
    d = client.delete(f"/api/v1/registry/{regid}")
    assert d.status_code == 200
    assert d.json()["status"] == "deregistered"

    # Verify it's gone
    d2 = client.delete(f"/api/v1/registry/{regid}")
    assert d2.status_code == 404
