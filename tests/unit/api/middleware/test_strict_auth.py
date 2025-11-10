
import pytest
import time
from fastapi import FastAPI, Request, Response
from httpx import AsyncClient, ASGITransport

# Adjust the import path based on the actual location of the middleware
from lukhas_website.lukhas.api.middleware.strict_auth import StrictAuthMiddleware

# Import the authentication system to generate tokens for testing
from labs.core.security.auth import get_auth_system, EnhancedAuthenticationSystem

# --- Test Setup ---

# A simple endpoint to capture the state attached by the middleware
async def capture_state_endpoint(request: Request):
    return Response(
        status_code=200,
        content=str(getattr(request.state, "user_id", "anonymous")),
    )

# A simple health check endpoint that should bypass auth
async def health_check_endpoint(request: Request):
    return Response(status_code=200, content="OK")

# Create a fixture for the auth system to ensure a fresh instance for each test
@pytest.fixture(scope="function")
def auth_system() -> EnhancedAuthenticationSystem:
    # Use a new instance with a fresh, random secret for each test run
    # to guarantee test isolation.
    return EnhancedAuthenticationSystem()

# Create a fixture for the FastAPI app with the middleware applied
@pytest.fixture(scope="function")
def test_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(StrictAuthMiddleware)

    # Add routes for testing different scenarios
    app.add_route("/v1/protected", capture_state_endpoint)
    app.add_route("/api/protected", capture_state_endpoint)
    app.add_route("/legacy/route", capture_state_endpoint)
    app.add_route("/healthz", health_check_endpoint)
    app.add_route("/metrics", health_check_endpoint)
    return app

# --- Test Cases ---

@pytest.mark.asyncio
async def test_health_endpoints_bypass_auth(test_app: FastAPI, monkeypatch):
    """(1/12) Health endpoints should bypass authentication."""
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        response = await client.get("/healthz")
        assert response.status_code == 200
        response = await client.get("/metrics")
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_v1_paths_require_bearer_token(test_app: FastAPI, monkeypatch):
    """(2/12) /v1/* paths must have a Bearer token; missing token returns 401."""
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        response = await client.get("/v1/protected")
        assert response.status_code == 401
        assert "Authorization header is missing" in response.json()["error"]["message"]

@pytest.mark.asyncio
async def test_missing_token_returns_401(test_app: FastAPI, monkeypatch):
    """(3/12) Explicitly test that a missing token returns 401."""
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        response = await client.get("/api/protected") # Also test /api prefix
        assert response.status_code == 401
        assert "Authorization header is missing" in response.json()["error"]["message"]

@pytest.mark.asyncio
async def test_invalid_token_returns_401(test_app: FastAPI, monkeypatch, auth_system):
    """(4/12) An invalid or malformed token returns 401."""
    monkeypatch.setattr(
        "lukhas_website.lukhas.api.middleware.strict_auth.get_auth_system",
        lambda: auth_system,
    )
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        headers = {"Authorization": "Bearer an-invalid-token"}
        response = await client.get("/v1/protected", headers=headers)
        assert response.status_code == 401
        assert "JWT is invalid" in response.json()["error"]["message"]

@pytest.mark.asyncio
async def test_expired_token_returns_401(auth_system: EnhancedAuthenticationSystem, test_app: FastAPI, monkeypatch):
    """(5/12) An expired token returns 401."""
    monkeypatch.setattr(
        "lukhas_website.lukhas.api.middleware.strict_auth.get_auth_system",
        lambda: auth_system,
    )
    # Configure the auth system to generate a token that expires instantly
    auth_system.jwt_expiry_hours = -1
    expired_token = auth_system.generate_jwt("user1")

    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        headers = {"Authorization": f"Bearer {expired_token}"}
        # We might need to wait a second to ensure the token is truly expired
        time.sleep(1)
        response = await client.get("/v1/protected", headers=headers)
        assert response.status_code == 401
        assert "JWT is invalid" in response.json()["error"]["message"]

@pytest.mark.asyncio
async def test_valid_token_attaches_user_id(auth_system: EnhancedAuthenticationSystem, test_app: FastAPI, monkeypatch):
    """(6/12) A valid token attaches the user_id to request.state."""
    monkeypatch.setattr(
        "lukhas_website.lukhas.api.middleware.strict_auth.get_auth_system",
        lambda: auth_system,
    )
    user_id = "test-user-123"
    token = auth_system.generate_jwt(user_id)
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get("/v1/protected", headers=headers)
        assert response.status_code == 200
        # The endpoint returns the user_id from the state
        assert response.text == user_id

@pytest.mark.asyncio
async def test_valid_token_attaches_user_tier(auth_system: EnhancedAuthenticationSystem, test_app: FastAPI, monkeypatch):
    """(7/12) A valid token attaches the user_tier to request.state."""
    monkeypatch.setattr(
        "lukhas_website.lukhas.api.middleware.strict_auth.get_auth_system",
        lambda: auth_system,
    )
    async def get_tier(request): return Response(str(request.state.user_tier))
    test_app.add_route("/v1/get-tier", get_tier)

    token = auth_system.generate_jwt("user-tier-test", claims={"tier": 5})
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get("/v1/get-tier", headers=headers)
        assert response.status_code == 200
        assert response.text == "5"

@pytest.mark.asyncio
async def test_valid_token_attaches_user_permissions(auth_system: EnhancedAuthenticationSystem, test_app: FastAPI, monkeypatch):
    """(8/12) A valid token attaches user_permissions to request.state."""
    monkeypatch.setattr(
        "lukhas_website.lukhas.api.middleware.strict_auth.get_auth_system",
        lambda: auth_system,
    )
    async def get_perms(request): return Response(",".join(request.state.user_permissions))
    test_app.add_route("/v1/get-permissions", get_perms)

    permissions = ["read:data", "write:data"]
    token = auth_system.generate_jwt("user-perms-test", claims={"permissions": permissions})
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get("/v1/get-permissions", headers=headers)
        assert response.status_code == 200
        assert response.text == "read:data,write:data"

@pytest.mark.asyncio
async def test_non_v1_or_api_paths_bypass_auth(test_app: FastAPI, monkeypatch):
    """(9/12) Non-/v1/* or /api/* paths bypass authentication."""
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        response = await client.get("/legacy/route")
        assert response.status_code == 200
        assert response.text == "anonymous"

@pytest.mark.asyncio
async def test_bearer_token_with_wrong_signature_returns_401(auth_system: EnhancedAuthenticationSystem, test_app: FastAPI, monkeypatch):
    """(10/12) A token with an incorrect signature returns 401."""
    monkeypatch.setattr(
        "lukhas_website.lukhas.api.middleware.strict_auth.get_auth_system",
        lambda: auth_system,
    )
    token = auth_system.generate_jwt("user-sig-test")

    # Create another auth system with a different secret to simulate a wrong signature
    attacker_auth_system = EnhancedAuthenticationSystem()
    assert auth_system.jwt_secret != attacker_auth_system.jwt_secret

    # The middleware uses `auth_system`, so a token from `attacker_auth_system` will be invalid
    invalid_token = attacker_auth_system.generate_jwt("user-sig-test")

    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        headers = {"Authorization": f"Bearer {invalid_token}"}
        response = await client.get("/v1/protected", headers=headers)
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_bearer_token_with_tampered_payload_returns_401(auth_system: EnhancedAuthenticationSystem, test_app: FastAPI, monkeypatch):
    """(11/12) A token with a tampered payload is invalid because the signature won't match."""
    monkeypatch.setattr(
        "lukhas_website.lukhas.api.middleware.strict_auth.get_auth_system",
        lambda: auth_system,
    )
    import base64
    import json
    token = auth_system.generate_jwt("user-tamper-test")
    parts = token.split('.')
    header, payload, signature = parts

    # Decode, tamper, and re-encode the payload
    decoded_payload = json.loads(base64.urlsafe_b64decode(payload + "==").decode())
    decoded_payload["user_id"] = "attacker"
    tampered_payload = base64.urlsafe_b64encode(json.dumps(decoded_payload).encode()).decode().rstrip("=")

    # Reassemble the token with the original signature, which is now invalid
    tampered_token = f"{header}.{tampered_payload}.{signature}"

    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        headers = {"Authorization": f"Bearer {tampered_token}"}
        response = await client.get("/v1/protected", headers=headers)
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_request_state_user_id_matches_jwt_claim(auth_system: EnhancedAuthenticationSystem, test_app: FastAPI, monkeypatch):
    """(12/12) The user_id on request.state must match the 'user_id' claim from the JWT."""
    monkeypatch.setattr(
        "lukhas_website.lukhas.api.middleware.strict_auth.get_auth_system",
        lambda: auth_system,
    )
    # This test re-validates test #6 but is explicitly named to match the requirement.
    user_id = "specific-user-for-claim-test"
    token = auth_system.generate_jwt(user_id)
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get("/v1/protected", headers=headers)
        assert response.status_code == 200
        assert response.text == user_id
