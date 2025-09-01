import pytest
from fastapi.testclient import TestClient

from serve.main import app

client = TestClient(app)


def test_validate_guardian():
    """
    Test the guardian validate endpoint.
    """
    response = client.post("/api/v1/guardian/validate")
    assert response.status_code == 200
    assert response.json() == {"status": "validated", "drift_score": 0.05}


def test_audit_guardian():
    """
    Test the guardian audit endpoint.
    """
    response = client.get("/api/v1/guardian/audit")
    assert response.status_code == 200
    assert response.json() == {"audit_log_entries": 100, "last_audit": "2025-08-27T22:00:00Z"}


def test_drift_check_guardian():
    """
    Test the guardian drift-check endpoint.
    """
    response = client.get("/api/v1/guardian/drift-check")
    assert response.status_code == 200
    assert response.json() == {"drift_status": "normal", "drift_score": 0.02}
