"""
Unit tests for the LUKHAS API Expansion module.
"""

from fastapi.testclient import TestClient
from api.expansion_api import app

client = TestClient(app)


def test_root():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "LUKHAS API Expansion"


# Consciousness API Tests
def test_get_consciousness_status():
    """Test the get_consciousness_status endpoint."""
    response = client.get("/consciousness/status")
    assert response.status_code == 200
    assert response.json()["state"] == "aware"


def test_get_awareness_level():
    """Test the get_awareness_level endpoint."""
    response = client.get("/consciousness/awareness")
    assert response.status_code == 200
    assert response.json()["level"] == 0.85


def test_set_awareness_level():
    """Test the set_awareness_level endpoint."""
    response = client.post("/consciousness/awareness", json={"level": 0.9})
    assert response.status_code == 200
    assert response.json()["level"] == 0.9


def test_query_memory():
    """Test the query_memory endpoint."""
    response = client.post("/consciousness/memory/query", json={"query": "test query"})
    assert response.status_code == 200
    assert "Result for query: test query" in response.json()["results"]


def test_start_dream():
    """Test the start_dream endpoint."""
    response = client.post("/consciousness/dream/start", json={"topic": "test dream", "duration_minutes": 10})
    assert response.status_code == 200
    assert response.json()["topic"] == "test dream"


def test_get_dream_status():
    """Test the get_dream_status endpoint."""
    response = client.get("/consciousness/dream/status/dream_123")
    assert response.status_code == 200
    assert response.json()["dream_id"] == "dream_123"


# Identity API Tests
def test_create_user():
    """Test the create_user endpoint."""
    response = client.post(
        "/identity/users", json={"username": "newuser", "email": "new@example.com", "password": "password"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "newuser"


def test_get_user():
    """Test the get_user endpoint."""
    response = client.get("/identity/users/user_123")
    assert response.status_code == 200
    assert response.json()["user_id"] == "user_123"


def test_update_user():
    """Test the update_user endpoint."""
    response = client.put("/identity/users/user_123", json={"username": "updateduser"})
    assert response.status_code == 200
    assert response.json()["username"] == "updateduser"


def test_delete_user():
    """Test the delete_user endpoint."""
    response = client.delete("/identity/users/user_123")
    assert response.status_code == 200
    assert response.json()["status"] == "deleted"


def test_get_token():
    """Test the get_token endpoint."""
    response = client.post("/identity/auth/token", json={"username": "testuser", "password": "password"})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_authorize():
    """Test the authorize endpoint."""
    response = client.post("/identity/auth/authorize", json={"token": "dummy_token", "resource": "test_resource"})
    assert response.status_code == 200
    assert response.json()["allowed"] is True


def test_consolidate_users():
    """Test the consolidate_users endpoint."""
    response = client.post(
        "/identity/consolidate", json={"primary_user_id": "user_123", "secondary_user_id": "user_456"}
    )
    assert response.status_code == 200
    assert response.json()["user_id"] == "user_123"


# Guardian API Tests
def test_get_safety_protocols():
    """Test the get_safety_protocols endpoint."""
    response = client.get("/guardian/safety/protocols")
    assert response.status_code == 200
    assert "protocols" in response.json()


def test_get_ethics_monitor_data():
    """Test the get_ethics_monitor_data endpoint."""
    response = client.get("/guardian/ethics/monitor")
    assert response.status_code == 200
    assert "monitoring_status" in response.json()


def test_check_compliance():
    """Test the check_compliance endpoint."""
    response = client.post("/guardian/compliance/check", json={"system": "test_system", "level": "test_level"})
    assert response.status_code == 200
    assert response.json()["compliant"] is True


def test_get_audit_trail():
    """Test the get_audit_trail endpoint."""
    response = client.get("/guardian/audit/trail")
    assert response.status_code == 200
    assert "logs" in response.json()
