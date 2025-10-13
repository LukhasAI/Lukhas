from starlette.testclient import TestClient
from lukhas.adapters.openai.api import get_app

def test_dreams_minimal():
    client = TestClient(get_app())
    payload = {"seed": "labyrinth under starlight", "constraints": {"length": "short"}}
    headers = {"Authorization": "Bearer sk-lukhas-test-1234567890abcdef"}
    r = client.post("/v1/dreams", json=payload, headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data.get("id", "").startswith("dream_")
    assert isinstance(data.get("traces", []), list)
