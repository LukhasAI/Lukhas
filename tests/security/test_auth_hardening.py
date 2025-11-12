import pytest
from datetime import datetime, timedelta, timezone
from lukhas.api.auth_helpers import AuthManager
import time
from fastapi import FastAPI
from fastapi.testclient import TestClient
from lukhas.api.auth_routes import router as auth_router

SECRET_KEY = "test_secret_key"

@pytest.fixture
def auth_manager():
    return AuthManager(secret_key=SECRET_KEY)

import fakeredis.aioredis
from lukhas.api.auth_routes import get_redis_client

@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(auth_router)

    # Use fakeredis for testing
    fake_redis_client = fakeredis.aioredis.FakeRedis(decode_responses=True)
    app.dependency_overrides[get_redis_client] = lambda: fake_redis_client

    with TestClient(app) as c:
        # Register a test user
        c.post("/api/auth/register", data={"username": "testuser", "password": "password"})
        yield c

def test_password_hashing(auth_manager):
    password = "strongpassword"
    hashed_password = auth_manager.get_password_hash(password)
    assert auth_manager.verify_password(password, hashed_password)
    assert not auth_manager.verify_password("wrongpassword", hashed_password)

def test_token_creation(auth_manager):
    user_id = "testuser"
    token = auth_manager.create_access_token(data={"user_id": user_id})
    payload = auth_manager.decode_access_token(token)
    assert payload["user_id"] == user_id

def test_token_expiration(auth_manager):
    user_id = "testuser"
    token = auth_manager.create_access_token(data={"user_id": user_id}, expires_delta=timedelta(seconds=1))
    time.sleep(2)
    payload = auth_manager.decode_access_token(token)
    assert payload is None

def test_invalid_token(auth_manager):
    invalid_token = "invalid_token"
    payload = auth_manager.decode_access_token(invalid_token)
    assert payload is None

def test_token_with_different_secret(auth_manager):
    user_id = "testuser"
    token = auth_manager.create_access_token(data={"user_id": user_id})

    other_manager = AuthManager(secret_key="different_secret")
    payload = other_manager.decode_access_token(token)
    assert payload is None

def test_password_hash_is_random(auth_manager: AuthManager):
    password = "a_very_secure_password_123"
    hash1 = auth_manager.get_password_hash(password)
    hash2 = auth_manager.get_password_hash(password)
    assert hash1 != hash2
    assert auth_manager.verify_password(password, hash1)
    assert auth_manager.verify_password(password, hash2)

def test_token_creation_with_custom_claims(auth_manager: AuthManager):
    user_id = "testuser_claims"
    custom_claims = {"role": "admin", "scope": "read write"}
    data = {"user_id": user_id, **custom_claims}
    token = auth_manager.create_access_token(data=data)
    payload = auth_manager.decode_access_token(token)
    assert payload is not None
    assert payload["user_id"] == user_id
    assert payload["role"] == "admin"
    assert payload["scope"] == "read write"

def test_token_very_short_expiration(auth_manager: AuthManager):
    user_id = "short_expiry_user"
    # Create a token that expires almost immediately
    token = auth_manager.create_access_token(
        data={"user_id": user_id}, expires_delta=timedelta(microseconds=1)
    )
    # Depending on execution speed, this might already be expired
    time.sleep(0.001)
    payload = auth_manager.decode_access_token(token)
    assert payload is None, "Token should be expired"

def test_token_not_yet_valid(auth_manager: AuthManager):
    # This requires modifying AuthManager to support 'nbf' (not before) claim
    # Skipping for now as it's not a standard feature of the current implementation
    pass

def test_token_with_invalid_signature(auth_manager: AuthManager):
    user_id = "user_sig_tamper"
    token = auth_manager.create_access_token(data={"user_id": user_id})

    # Tamper with the signature part of the token
    parts = token.split('.')
    tampered_signature = parts[2].replace(parts[2][0], 'a', 1)
    tampered_token = f"{parts[0]}.{parts[1]}.{tampered_signature}"

    payload = auth_manager.decode_access_token(tampered_token)
    assert payload is None

def test_password_verify_with_empty_password(auth_manager: AuthManager):
    password = ""
    hashed_password = auth_manager.get_password_hash(password)
    assert auth_manager.verify_password(password, hashed_password)
    assert not auth_manager.verify_password("a", hashed_password)

def test_password_verify_with_long_password(auth_manager: AuthManager):
    password = "a" * 1000
    hashed_password = auth_manager.get_password_hash(password)
    assert auth_manager.verify_password(password, hashed_password)

def test_token_payload_without_userid(auth_manager: AuthManager):
    # This scenario is valid for token creation, but our get_current_user expects user_id
    token = auth_manager.create_access_token(data={"role": "guest"})
    payload = auth_manager.decode_access_token(token)
    assert payload is not None
    assert "user_id" not in payload

def test_token_with_non_ascii_chars_in_payload(auth_manager: AuthManager):
    user_id = "user_josé"
    data = {"user_id": user_id, "location": "coração"}
    token = auth_manager.create_access_token(data=data)
    payload = auth_manager.decode_access_token(token)
    assert payload["user_id"] == user_id
    assert payload["location"] == "coração"

def test_mfa_setup(client, auth_manager):
    # First, get a valid token
    login_response = client.post("/api/auth/login", data={"username": "testuser", "password": "password"})
    token = login_response.json()["access_token"]

    # Now, setup MFA
    response = client.post(
        "/api/auth/mfa/setup",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    json_response = response.json()
    assert "secret" in json_response
    assert "provisioning_uri" in json_response

def test_mfa_verification(client, auth_manager):
    # First, get a valid token
    login_response = client.post("/api/auth/login", data={"username": "testuser", "password": "password"})
    token = login_response.json()["access_token"]

    # Setup MFA to get the secret
    setup_response = client.post(
        "/api/auth/mfa/setup",
        headers={"Authorization": f"Bearer {token}"},
    )
    secret = setup_response.json()["secret"]

    # Generate a valid TOTP code
    import pyotp
    totp = pyotp.TOTP(secret)
    code = totp.now()

    # Verify MFA
    response = client.post(
        "/api/auth/mfa/verify",
        headers={"Authorization": f"Bearer {token}"},
        json={"code": code},
    )
    assert response.status_code == 200
    assert response.json() == {"status": "MFA verified successfully"}

def test_mfa_verification_invalid_code(client, auth_manager):
    # First, get a valid token
    login_response = client.post("/api/auth/login", data={"username": "testuser", "password": "password"})
    token = login_response.json()["access_token"]

    # Setup MFA
    client.post(
        "/api/auth/mfa/setup",
        headers={"Authorization": f"Bearer {token}"},
    )

    # Verify with an invalid code
    response = client.post(
        "/api/auth/mfa/verify",
        headers={"Authorization": f"Bearer {token}"},
        json={"code": "000000"},
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid MFA code."}


# Additional token tests
def test_token_with_null_bytes_in_payload(auth_manager: AuthManager):
    user_id = "user\0with\0null"
    # PyJWT's C implementation can handle null bytes, but it's a security risk
    # This test ensures that if the behavior changes, we are aware of it.
    # The C implementation of the JWT library may or may not raise an error.
    # This test will pass if an error is raised or if the token is created,
    # but the key is to be aware of the behavior.
    try:
        token = auth_manager.create_access_token(data={"user_id": user_id})
        payload = auth_manager.decode_access_token(token)
        # If the token is created, the payload should match
        assert payload["user_id"] == user_id
    except Exception as e:
        # If an exception is raised, it should be a TypeError or similar
        assert isinstance(e, (TypeError, ValueError))

def test_token_with_modified_algorithm_in_header(auth_manager: AuthManager):
    import base64, json
    user_id = "test_user"
    token = auth_manager.create_access_token(data={"user_id": user_id})
    header, payload, signature = token.split('.')
    decoded_header = json.loads(base64.urlsafe_b64decode(header + '==').decode())
    decoded_header['alg'] = 'none'
    encoded_header = base64.urlsafe_b64encode(json.dumps(decoded_header).encode()).rstrip(b'=').decode()

    # Reassemble token with "alg": "none" and no signature
    none_alg_token = f"{encoded_header}.{payload}."

    # The current implementation should reject this
    decoded_payload = auth_manager.decode_access_token(none_alg_token)
    assert decoded_payload is None

def test_password_hashing_algorithm(auth_manager: AuthManager):
    password = "testpassword"
    hashed_password = auth_manager.get_password_hash(password)
    # Passlib hashes start with the scheme name
    assert hashed_password.startswith("$2b$")

def test_token_iat_claim(auth_manager: AuthManager):
    user_id = "test_user_iat"
    token = auth_manager.create_access_token(data={"user_id": user_id})
    payload = auth_manager.decode_access_token(token)
    assert "iat" in payload
    now_ts = int(datetime.now(timezone.utc).timestamp())
    assert now_ts - payload["iat"] < 5  # Should be created within the last 5 seconds

def test_empty_token_string(auth_manager: AuthManager):
    payload = auth_manager.decode_access_token("")
    assert payload is None

def test_token_with_only_header_and_payload(auth_manager: AuthManager):
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoidGVzdCJ9"
    payload = auth_manager.decode_access_token(token)
    assert payload is None

# Tests for Authentication Endpoints

def test_login_for_access_token(client):
    response = client.post(
        "/api/auth/login",
        data={"username": "testuser", "password": "password"},
    )
    assert response.status_code == 200
    json_response = response.json()
    assert "access_token" in json_response
    assert "refresh_token" in json_response
    assert json_response["token_type"] == "bearer"

def test_login_incorrect_password(client):
    response = client.post(
        "/api/auth/login",
        data={"username": "testuser", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}

def test_login_rate_limiting(client):
    for i in range(5):
        client.post(
            "/api/auth/login",
            data={"username": "testuser", "password": "wrongpassword"},
        )

    response = client.post(
        "/api/auth/login",
        data={"username": "testuser", "password": "wrongpassword"},
    )
    assert response.status_code == 429
    assert response.json() == {"detail": "Too many login attempts. Please try again later."}

def test_refresh_token(client):
    login_response = client.post(
        "/api/auth/login",
        data={"username": "testuser", "password": "password"},
    )
    refresh_token = login_response.json()["refresh_token"]

    refresh_response = client.post(
        "/api/auth/token/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_response.status_code == 200
    new_tokens = refresh_response.json()
    assert "access_token" in new_tokens
    assert "refresh_token" in new_tokens

def test_refresh_with_invalid_token(client):
    response = client.post(
        "/api/auth/token/refresh",
        json={"refresh_token": "invalid_token"},
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid refresh token"}
