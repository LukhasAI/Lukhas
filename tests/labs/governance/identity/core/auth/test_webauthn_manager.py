import base64
import json
from datetime import datetime, timedelta, timezone

import pytest

from labs.governance.identity.core.auth import webauthn_manager


def _setup_manager_with_pending():
    manager = webauthn_manager.WebAuthnManager(
        {"origin": "https://identity.lukhas.ai", "rp_id": "identity.lukhas.ai"}
    )
    challenge = b"test-challenge"
    challenge_b64 = base64.urlsafe_b64encode(challenge).decode().rstrip("=")
    registration_id = "reg_test"

    manager.pending_registrations[registration_id] = {
        "challenge": challenge,
        "challenge_b64": challenge_b64,
        "user_id": "user-123",
        "user_tier": 2,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat(),
    }

    return manager, registration_id, challenge, challenge_b64


def _build_registration_response(challenge_b64: str, origin: str) -> dict:
    client_data = {
        "type": "webauthn.create",
        "challenge": challenge_b64,
        "origin": origin,
        "crossOrigin": False,
    }

    return {
        "id": "credential-id",
        "rawId": "credential-id",
        "type": "public-key",
        "response": {
            "clientDataJSON": base64.urlsafe_b64encode(json.dumps(client_data).encode()).decode().rstrip("="),
            "attestationObject": base64.urlsafe_b64encode(b"attestation").decode().rstrip("="),
        },
        "transports": ["usb"],
        "clientExtensionResults": {},
    }


@pytest.mark.identity
@pytest.mark.governance
def test_verify_registration_response_uses_webauthn_library(monkeypatch):
    manager, registration_id, challenge, challenge_b64 = _setup_manager_with_pending()
    response = _build_registration_response(challenge_b64, manager.origin)

    parsed_marker = object()
    captured = {}

    def fake_parse(json_payload: str):
        captured["parse_called"] = True
        captured["parse_payload"] = json.loads(json_payload)
        return parsed_marker

    class FakeVerification:
        verified = True
        credential_id = b"verified-id"
        credential_public_key = b"verified-key"
        sign_count = 7

    def fake_verify(*, credential, expected_challenge, expected_origin, expected_rp_id):
        captured["verify_called"] = True
        captured["credential"] = credential
        captured["expected_challenge"] = expected_challenge
        captured["expected_origin"] = expected_origin
        captured["expected_rp_id"] = expected_rp_id
        return FakeVerification()

    monkeypatch.setattr(webauthn_manager, "parse_registration_credential_json", fake_parse)
    monkeypatch.setattr(webauthn_manager, "verify_registration_response", fake_verify)
    monkeypatch.setattr(webauthn_manager, "WEBAUTHN_AVAILABLE", True)

    result = manager.verify_registration_response(registration_id, response)

    assert result["success"] is True
    assert captured.get("parse_called") is True
    assert captured.get("verify_called") is True
    assert captured["credential"] is parsed_marker
    assert captured["expected_challenge"] == challenge
    assert captured["expected_origin"] == manager.origin
    assert captured["expected_rp_id"] == manager.rp_id

    stored_credential = manager.credentials["user-123"][0]
    expected_credential_id = base64.urlsafe_b64encode(b"verified-id").decode().rstrip("=")
    expected_public_key = base64.urlsafe_b64encode(b"verified-key").decode().rstrip("=")

    assert stored_credential.credential_id == expected_credential_id
    assert stored_credential.public_key == expected_public_key
    assert stored_credential.sign_count == 7


@pytest.mark.identity
@pytest.mark.governance
def test_verify_registration_response_handles_webauthn_rejection(monkeypatch):
    manager, registration_id, _challenge, challenge_b64 = _setup_manager_with_pending()
    response = _build_registration_response(challenge_b64, manager.origin)

    class FakeVerification:
        verified = False

    monkeypatch.setattr(
        webauthn_manager,
        "parse_registration_credential_json",
        lambda payload: object(),
    )
    monkeypatch.setattr(
        webauthn_manager,
        "verify_registration_response",
        lambda **_kwargs: FakeVerification(),
    )
    monkeypatch.setattr(webauthn_manager, "WEBAUTHN_AVAILABLE", True)

    result = manager.verify_registration_response(registration_id, response)

    assert result == {
        "success": False,
        "error": "WebAuthn library rejected registration",
    }
    assert "user-123" not in manager.credentials
