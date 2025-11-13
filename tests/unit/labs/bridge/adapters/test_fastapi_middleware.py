import pytest
import os
from fastapi.testclient import TestClient
from labs.bridge.adapters.main import app, jwt_adapter
from labs.bridge.adapters.api_framework import JWTAdapter, JWTAlgorithm
from datetime import datetime, timedelta, timezone
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# Generate RSA keys for testing
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
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

os.environ['JWT_PUBLIC_KEY'] = public_pem
os.environ['JWT_PRIVATE_KEY'] = private_pem

client = TestClient(app)

def test_unprotected_route():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "This is a public endpoint."}

def test_protected_route_no_token():
    response = client.get("/protected")
    assert response.status_code == 401
    assert response.json()["detail"] == "Authorization header missing"

def test_protected_route_invalid_header_format():
    response = client.get("/protected", headers={"Authorization": "Bearer"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid Authorization header format"

def test_protected_route_invalid_token():
    response = client.get("/protected", headers={"Authorization": "Bearer invalidtoken"})
    assert response.status_code == 401
    assert response.json()["error_code"] == "DECODE_ERROR"

def test_protected_route_expired_token():
    expired_token = jwt_adapter.create_token(subject="testuser", custom_ttl=-1)
    response = client.get(
        "/protected", headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401
    assert response.json()["error_code"] == "TOKEN_EXPIRED"

def test_protected_route_valid_token():
    token = jwt_adapter.create_token(subject="testuser")
    response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "This is a protected endpoint."
    assert data["user"]["sub"] == "testuser"

def test_token_generation():
    response = client.post("/token", params={"user_id": "newuser"})
    assert response.status_code == 200

def test_protected_route_valid_token_rs256():
    # Create a new app instance for this test
    from fastapi import FastAPI, Depends, Request
    from labs.bridge.adapters.api_framework import TokenClaims
    from labs.bridge.adapters.fastapi_middleware import JWTAuthMiddleware

    rs256_adapter = JWTAdapter(algorithm=JWTAlgorithm.RS256, leeway=0)

    test_app = FastAPI()
    test_app.add_middleware(JWTAuthMiddleware, jwt_adapter=rs256_adapter)

    async def get_current_user(request: Request) -> TokenClaims:
        return request.scope["auth"]

    @test_app.get("/protected")
    async def read_protected(current_user: TokenClaims = Depends(get_current_user)):
        return {"message": "This is a protected endpoint.", "user": current_user}

    token = rs256_adapter.create_token(subject="rs256user")

    with TestClient(test_app) as client:
        response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "This is a protected endpoint."
    assert data["user"]["sub"] == "rs256user"
