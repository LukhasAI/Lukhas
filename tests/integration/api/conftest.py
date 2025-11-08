import pytest
from fastapi.testclient import TestClient
from serve.main import app as main_app
from serve.reference_api.public_api_reference import app as dreams_app, verify_api_key
from labs.core.security.auth import get_auth_system
from unittest.mock import patch

@pytest.fixture(scope="session")
def client():
    """Provides a test client for the main API."""
    with TestClient(main_app) as c:
        yield c

@pytest.fixture(scope="session")
def dreams_client():
    """Provides a test client for the dreams API."""
    with TestClient(dreams_app) as c:
        yield c

@pytest.fixture(scope="session")
def auth_headers():
    """Provides authorization headers for testing."""
    auth_system = get_auth_system()
    token = auth_system.generate_jwt("test_user")
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def mock_dreams_auth():
    """Mocks the authentication for the dreams endpoint."""
    with patch("serve.reference_api.public_api_reference.verify_api_key") as mock_verify_api_key:
        mock_verify_api_key.return_value = {"user_id": "test_user"}
        dreams_app.dependency_overrides[verify_api_key] = lambda: {"user_id": "test_user"}
        yield
        dreams_app.dependency_overrides = {}
