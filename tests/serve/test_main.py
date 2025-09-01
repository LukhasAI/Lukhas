import pytest
from fastapi.testclient import TestClient

from serve.main import app

client = TestClient(app)


def test_healthz():
    """
    Test the health check endpoint to ensure the API is running.
    """
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_openapi_json():
    """
    Test the openapi.json endpoint to ensure it's available.
    """
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "openapi" in response.json()
