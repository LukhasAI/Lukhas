from starlette.testclient import TestClient
from lukhas.adapters.openai.api import get_app

def test_responses_minimal(authz_headers):
    client = TestClient(get_app())
    payload = {"input": "hello lukhas", "lukhas.tools": []}
    headers = dict(authz_headers)
    r = client.post("/v1/responses", json=payload, headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert body.get("id") and body.get("output", {}).get("text")
    assert body.get("model")  # e.g., "lukhas-matriz"

def test_models_list(authz_headers):
    client = TestClient(get_app())
    headers = dict(authz_headers)
    r = client.get("/v1/models", headers=headers)
    assert r.status_code == 200
    ids = [m.get("id") for m in r.json().get("data", [])]
    assert any(ids), "should expose at least one model id"
