import base64
import json
from datetime import datetime, timedelta, timezone

import pytest
from labs.governance.identity.core.auth import webauthn_manager


def _encode_base64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def _build_client_data(challenge: str, origin: str) -> str:
    client_data = {"type": "webauthn.get", "challenge": challenge, "origin": origin}
    return _encode_base64url(json.dumps(client_data).encode())


def _make_basic_response(credential_id: str, challenge_b64: str, origin: str) -> dict:
    return {
        "id": credential_id,
        "rawId": credential_id,
        "type": "public-key",
        "response": {
            "clientDataJSON": _build_client_data(challenge_b64, origin),
            "authenticatorData": _encode_base64url(b"authenticator"),
            "signature": _encode_base64url(b"signature"),
        },
        "transports": ["internal"],
    }


class _FakeVerification:
    def __init__(self, verified: bool = True, new_sign_count: int = 9):
        self.verified = verified
        self.new_sign_count = new_sign_count
        self.backup_state = False
        self.backup_eligible = True


def test_verify_authentication_response_uses_library(monkeypatch):
    manager = webauthn_manager.WebAuthnManager({"origin": "https://ai", "rp_id": "ai"})

    user_id = "user_identity_01"
    credential_id = "credential-123"
    public_key_bytes = b"public-key"
    public_key = _encode_base64url(public_key_bytes)

    credential = webauthn_manager.WebAuthnCredential(
        {
            "credential_id": credential_id,
            "public_key": public_key,
            "sign_count": 5,
            "user_id": user_id,
            "authenticator_data": {"transports": ["internal"]},
            "tier_level": 2,
            "device_type": "platform_authenticator",
        }
    )

    manager.credentials[user_id] = [credential]

    challenge_bytes = b"challenge-bytes"
    challenge_b64 = _encode_base64url(challenge_bytes)
    auth_id = "auth_123"
    manager.pending_authentications[auth_id] = {
        "challenge": challenge_bytes,
        "challenge_b64": challenge_b64,
        "user_id": user_id,
        "tier_level": 2,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat(),
    }

    captured = {}

    def fake_parse(payload: str):
        captured["parsed"] = json.loads(payload)
        return {"parsed": True}

    def fake_verify(**kwargs):
        captured["verify"] = kwargs
        return _FakeVerification()

    monkeypatch.setattr(webauthn_manager, "WEBAUTHN_AVAILABLE", True, raising=False)
    monkeypatch.setattr(
        webauthn_manager,
        "parse_authentication_credential_json",
        fake_parse,
        raising=False,
    )
    monkeypatch.setattr(
        webauthn_manager,
        "webauthn_verify_authentication_response",
        fake_verify,
        raising=False,
    )

    response = _make_basic_response(credential_id, challenge_b64, manager.origin)

    result = manager.verify_authentication_response(auth_id, response)

    assert result["success"] is True
    assert result["library_verified"] is True
    assert result["sign_count"] == 9
    assert result["backup_eligible"] is True
    assert credential.sign_count == 9

    assert captured["parsed"]["id"] == credential_id
    assert captured["verify"]["expected_challenge"] == challenge_bytes
    assert captured["verify"]["expected_origin"] == manager.origin
    assert captured["verify"]["expected_rp_id"] == manager.rp_id
    assert captured["verify"]["credential_current_sign_count"] == 5


def test_verify_authentication_response_falls_back_without_public_key(monkeypatch):
    manager = webauthn_manager.WebAuthnManager({"origin": "https://ai", "rp_id": "ai"})

    user_id = "user_identity_02"
    credential_id = "credential-456"

    credential = webauthn_manager.WebAuthnCredential(
        {
            "credential_id": credential_id,
            "public_key": "",
            "sign_count": 1,
            "user_id": user_id,
            "authenticator_data": {"transports": ["internal"]},
            "tier_level": 1,
            "device_type": "platform_authenticator",
        }
    )

    manager.credentials[user_id] = [credential]

    challenge_bytes = b"fallback-challenge"
    challenge_b64 = _encode_base64url(challenge_bytes)
    auth_id = "auth_456"
    manager.pending_authentications[auth_id] = {
        "challenge": challenge_bytes,
        "challenge_b64": challenge_b64,
        "user_id": user_id,
        "tier_level": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat(),
    }

    monkeypatch.setattr(webauthn_manager, "WEBAUTHN_AVAILABLE", True, raising=False)
    monkeypatch.setattr(
        webauthn_manager,
        "webauthn_verify_authentication_response",
        lambda **_: pytest.fail("Library verification should not be called without key"),
        raising=False,
    )
    monkeypatch.setattr(
        webauthn_manager,
        "parse_authentication_credential_json",
        lambda payload: {"parsed": payload},
        raising=False,
    )

    response = _make_basic_response(credential_id, challenge_b64, manager.origin)

    result = manager.verify_authentication_response(auth_id, response)

    assert result["success"] is True
    assert result["library_verified"] is False
    assert result["sign_count"] == 2
    assert credential.sign_count == 2
