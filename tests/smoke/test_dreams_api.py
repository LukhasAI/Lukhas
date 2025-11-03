from serve.main import app
from starlette.testclient import TestClient
from tests.smoke.fixtures import GOLDEN_AUTH_HEADERS


def test_dreams_minimal():
    client = TestClient(app)
    payload = {"seed": "labyrinth under starlight", "constraints": {"length": "short"}}
    headers = GOLDEN_AUTH_HEADERS
    r = client.post("/v1/dreams", json=payload, headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data.get("id", "").startswith("dream_")
    assert isinstance(data.get("traces", []), list)
