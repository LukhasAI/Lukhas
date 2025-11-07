"""
Integration tests for the JWTAdapter with a live FastAPI application.
"""

import pytest
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPBearer
from fastapi.testclient import TestClient
from labs.bridge.adapters.api_framework import JWTAdapter, JWTAlgorithm

# Test setup
SECRET_KEY = "integration-test-secret"
ALGORITHM = "HS256"
API_AUDIENCE = "test-audience"

# Create a JWT adapter instance for testing
jwt_adapter = JWTAdapter(
    secret_key=SECRET_KEY,
    algorithm=JWTAlgorithm.HS256,
    issuer="test-issuer",
    audience=API_AUDIENCE,
)

# FastAPI app setup
app = FastAPI()
bearer_scheme = HTTPBearer()

def get_jwt_adapter():
    """Dependency to get the JWT adapter."""
    return jwt_adapter

def get_current_user(token: str = Depends(bearer_scheme), adapter: JWTAdapter = Depends(get_jwt_adapter)):
    """Dependency to verify JWT token and get user claims."""
    result = adapter.verify_token(token.credentials)
    if not result.valid:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return result.claims

@app.get("/protected")
def protected_route(claims: dict = Depends(get_current_user)):
    """A protected route that requires a valid JWT."""
    return {"message": f"Hello, {claims.sub}!"}

@app.get("/unprotected")
def unprotected_route():
    """An unprotected route."""
    return {"message": "This is an unprotected route."}

client = TestClient(app)

def test_unprotected_route_access():
    """Test that the unprotected route is accessible without a token."""
    response = client.get("/unprotected")
    assert response.status_code == 200
    assert response.json() == {"message": "This is an unprotected route."}

def test_protected_route_no_token():
    """Test that the protected route returns 403 without a token."""
    response = client.get("/protected")
    assert response.status_code == 403

def test_protected_route_with_valid_token():
    """Test that the protected route is accessible with a valid token."""
    token = jwt_adapter.create_token(subject="test-user")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/protected", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, test-user!"}

def test_protected_route_with_invalid_token():
    """Test that the protected route returns 401 with an invalid token."""
    headers = {"Authorization": "Bearer invalid-token"}
    response = client.get("/protected", headers=headers)
    assert response.status_code == 401


def test_protected_route_with_expired_token():
    """Test that the protected route returns 401 with an expired token."""
    expired_adapter = JWTAdapter(
        secret_key=SECRET_KEY,
        algorithm=JWTAlgorithm.HS256,
        issuer="test-issuer",
        audience=API_AUDIENCE,
        leeway=0,
    )
    app.dependency_overrides[get_jwt_adapter] = lambda: expired_adapter
    token = expired_adapter.create_token(subject="test-user", custom_ttl=-1)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/protected", headers=headers)
    assert response.status_code == 401
    app.dependency_overrides = {}


def test_protected_route_with_wrong_issuer():
    """Test that the protected route returns 401 with a token from the wrong issuer."""
    wrong_issuer_adapter = JWTAdapter(
        secret_key=SECRET_KEY,
        algorithm=JWTAlgorithm.HS256,
        issuer="wrong-issuer",
        audience=API_AUDIENCE,
    )
    token = wrong_issuer_adapter.create_token(subject="test-user")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/protected", headers=headers)
    assert response.status_code == 401


def test_protected_route_with_rs512_token():
    """Test that the protected route returns 401 with a token signed with a different algorithm."""
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')

    rs512_adapter = JWTAdapter(
        public_key=public_pem,
        private_key=private_pem,
        algorithm=JWTAlgorithm.RS512,
        issuer="test-issuer",
        audience=API_AUDIENCE,
    )
    token = rs512_adapter.create_token(subject="test-user")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/protected", headers=headers)
    assert response.status_code == 401
