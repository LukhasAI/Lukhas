from starlette.testclient import TestClient
from lukhas.adapters.openai.api import get_app

def test_dreams_minimal():
    client = TestClient(get_app())
    payload = {"seed": "labyrinth under starlight", "constraints": {"length": "short"}}
    r = client.post("/v1/dreams", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data.get("id", "").startswith("dream_")
    assert isinstance(data.get("traces", []), list)
