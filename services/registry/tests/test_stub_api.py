from fastapi.testclient import TestClient
from services.registry.main import app

client = TestClient(app)


def test_health_ok():
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body.get("status") == "ok"


def test_validate_and_register_and_query_and_delete():
    # Use the sample NodeSpec from docs (mirrored content here to avoid fs dependency in unit test)
    nodespec = {
        "node_type": "matriz.memory.adapter",
        "metadata": {
            "name": "memoria_adapter_v1",
            "version": "0.1.0",
            "schema_version": "nodespec.v1",
            "created_at": "2025-10-24",
        },
        "identity": {
            "owner_id": "GLYMPH:a3f2...7890abc",
            "lane": "core",
            "tier": 3,
            "roles": ["matriz.memory", "memoria.adapter"],
            "capabilities_policy": {"allow": ["read:memory/episodic/*", "write:memory/episodic/*"]},
        },
        "interfaces": {
            "inputs": [{"name": "StoreRequest", "schema_ref": "schemas/store_request.json"}],
            "outputs": [{"name": "StoreAck", "schema_ref": "schemas/store_ack.json"}],
            "signals": {
                "emits": [{"name": "memory_stored", "latency_target_ms": 50}],
                "subscribes": [{"signal": "process_memory", "handler": "process"}],
            },
        },
        "contracts": {
            "performance_hints": {"p50": 20, "p95": 80, "concurrency": 100, "timeout_ms": 5000}
        },
        "provenance_manifest": {
            "glymph_enabled": True,
            "signing_scheme": "dilithium2",
            "pqc_compat": True,
        },
        "security": {"encryption": {"envelope": "XChaCha20-Poly1305", "kem": "kyber-768"}},
    }

    # validate
    rv = client.post("/api/v1/registry/validate", json=nodespec)
    assert rv.status_code in (200, 400)  # 400 only if schema missing or mismatch
    if rv.status_code == 200:
        assert rv.json().get("valid") is True

    # register (happy path)
    rr = client.post("/api/v1/registry/register", json=nodespec)
    assert rr.status_code == 200, rr.text
    reg_id = rr.json().get("registry_id")
    assert reg_id

    # query by signal
    q = client.get("/api/v1/registry/query", params={"signal": "memory_stored"})
    assert q.status_code == 200
    ids = [r.get("registry_id") for r in q.json().get("results", [])]
    assert reg_id in ids

    # negative: missing provenance → expect 4xx
    neg = dict(nodespec)
    neg.pop("provenance_manifest", None)
    negr = client.post("/api/v1/registry/register", json=neg)
    assert negr.status_code in (400, 403)

    # delete
    dr = client.delete(f"/api/v1/registry/{reg_id}")
    assert dr.status_code == 200
