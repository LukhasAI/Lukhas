from unittest.mock import AsyncMock

from consent.api import ConsentService, get_consent_service, router
from fastapi import FastAPI
from fastapi.testclient import TestClient


def create_app():
    app = FastAPI()
    app.include_router(router)
    return app


def test_grant_consent():
    """Test the /consent/grant endpoint."""
    app = create_app()
    # Mock the consent service to avoid database connection
    mock_service = AsyncMock(spec=ConsentService)
    mock_service.grant_consent.return_value = (
        "grant_id",
        {
            "token": "test_token",
            "expires_at": "2025-01-01T00:00:00Z",
            "scopes": ["email.read.headers"],
            "caveats": {},
        },
    )

    async def override_get_consent_service():
        return mock_service

    app.dependency_overrides[get_consent_service] = override_get_consent_service

    client = TestClient(app)

    response = client.post(
        "/consent/grant",
        json={
            "lid": "gonzo",
            "service": "gmail",
            "scopes": ["email.read.headers"],
            "purpose_id": "essential_functionality",
            "ttl_minutes": 120,
        },
    )
    if response.status_code != 200:
        print(response.json())
    assert response.status_code == 200
    data = response.json()
    assert data["grant_id"] == "grant_id"
    assert data["capability_token"]["token"] == "test_token"

    app.dependency_overrides = {}


def test_get_consent_ledger():
    """Test the /consent/ledger endpoint."""
    app = create_app()
    # Mock the consent service to avoid database connection
    mock_service = AsyncMock(spec=ConsentService)
    mock_service.get_consent_ledger.return_value = []

    async def override_get_consent_service():
        return mock_service

    app.dependency_overrides[get_consent_service] = override_get_consent_service

    client = TestClient(app)

    response = client.get("/consent/ledger?lid=gonzo")
    assert response.status_code == 200
    data = response.json()
    assert data["total_entries"] == 0

    app.dependency_overrides = {}


def test_system_info():
    """Test the /consent/info endpoint."""
    app = create_app()
    client = TestClient(app)
    response = client.get("/consent/info")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "LUKHAS Consent Fabric"


if __name__ == "__main__":
    test_grant_consent()
    test_get_consent_ledger()
    test_system_info()
    print("All tests passed!")
