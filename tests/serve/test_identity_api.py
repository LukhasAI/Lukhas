import pytest
from fastapi.testclient import TestClient

from serve.main import app

client = TestClient(app)


def test_authenticate_identity():
    """
    Test the identity authenticate endpoint.
    """
    response = client.post("/api/v1/identity/authenticate")
    assert response.status_code == 200
    assert response.json() == {"status": "authenticated"}


def test_verify_identity():
    """
    Test the identity verify endpoint.
    """
    response = client.get("/api/v1/identity/verify")
    assert response.status_code == 200
    assert response.json() == {"status": "verified"}


def test_tier_check_identity():
    """
    Test the identity tier-check endpoint.
    """
    response = client.get("/api/v1/identity/tier-check")
    assert response.status_code == 200
    assert response.json() == {"tier": "premium"}
