import pytest
from serve.main import app
from starlette.testclient import TestClient
import os

from tests.smoke.fixtures import GOLDEN_AUTH_HEADERS

def test_dreams_minimal(client):
    payload = {"seed": "labyrinth under starlight", "constraints": {"length": "short"}}
    headers = {"X-API-Key": "test_api_key"}
    r = client.post("/v1/dreams", json=payload, headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data.get("id", "").startswith("dream_")
    assert isinstance(data.get("traces", []), list)
