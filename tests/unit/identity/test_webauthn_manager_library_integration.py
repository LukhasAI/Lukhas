"""Tests for WebAuthnManager when the real webauthn library is available."""

from __future__ import annotations

import base64
import importlib
import json
import sys
import types

import pytest
from typing import Dict

FAKE_REG_CHALLENGE = base64.urlsafe_b64encode(b"library-registration-challenge").decode().rstrip("=")
FAKE_AUTH_CHALLENGE = base64.urlsafe_b64encode(b"library-authentication-challenge").decode().rstrip("=")


@pytest.fixture()
def fake_webauthn(monkeypatch):
    """Install a fake webauthn implementation for testing."""

    call_log: Dict[str, dict] = {}

    fake_webauthn = types.ModuleType("webauthn")

    class FakeRegistrationOptions:
        def __init__(self, data: Dict[str, object]):
            self._data = data

        def model_dump(self) -> Dict[str, object]:
            return dict(self._data)

    class FakeAuthenticationOptions:
        def __init__(self, data: Dict[str, object]):
            self._data = data

        def model_dump(self) -> Dict[str, object]:
            return dict(self._data)

    def generate_registration_options(**kwargs):
        call_log["registration"] = kwargs
        user_id = kwargs.get("user_id", b"")
        user_id_bytes = user_id.encode() if isinstance(user_id, str) else user_id
        user_struct = {
            "id": base64.urlsafe_b64encode(user_id_bytes).decode().rstrip("="),
            "name": kwargs.get("user_name", ""),
            "displayName": kwargs.get("user_display_name", ""),
        }
        return FakeRegistrationOptions(
            {
                "challenge": FAKE_REG_CHALLENGE,
                "rp": {"name": kwargs.get("rp_name"), "id": kwargs.get("rp_id")},
                "user": user_struct,
                "timeout": kwargs.get("timeout", 60000),
            }
        )

    def generate_authentication_options(**kwargs):
        call_log["authentication"] = kwargs
        return FakeAuthenticationOptions(
            {
                "challenge": FAKE_AUTH_CHALLENGE,
                "rpId": kwargs.get("rp_id"),
                "allowCredentials": kwargs.get("allow_credentials", []),
                "timeout": kwargs.get("timeout", 60000),
            }
        )

    def verify_registration_response(**kwargs):
        call_log["verify_registration"] = kwargs

        class Result:
            verified = True
            credential_id = b"cred"
            credential_public_key = b"pub"
            sign_count = 1

        return Result()

    def verify_authentication_response(**kwargs):
        call_log["verify_authentication"] = kwargs

        class Result:
            verified = True
            new_sign_count = kwargs.get("credential_current_sign_count", 0) + 1

        return Result()

    fake_webauthn.generate_registration_options = generate_registration_options
    fake_webauthn.generate_authentication_options = generate_authentication_options
    fake_webauthn.verify_registration_response = verify_registration_response
    fake_webauthn.verify_authentication_response = verify_authentication_response

    helpers_module = types.ModuleType("webauthn.helpers")
    structs_module = types.ModuleType("webauthn.helpers.structs")
    helpers_module.structs = structs_module

    def parse_registration_credential_json(payload: str):
        call_log["parse_registration"] = json.loads(payload)
        return {"payload": payload}

    def parse_authentication_credential_json(payload: str):
        call_log["parse_authentication"] = json.loads(payload)
        return {"payload": payload}

    helpers_module.parse_registration_credential_json = parse_registration_credential_json
    helpers_module.parse_authentication_credential_json = parse_authentication_credential_json

    monkeypatch.setitem(sys.modules, "webauthn", fake_webauthn)
    monkeypatch.setitem(sys.modules, "webauthn.helpers", helpers_module)
    monkeypatch.setitem(sys.modules, "webauthn.helpers.structs", structs_module)

    yield call_log

    for module_name in ["webauthn", "webauthn.helpers", "webauthn.helpers.structs"]:
        sys.modules.pop(module_name, None)


def test_webauthn_manager_prefers_library(fake_webauthn):
    module_name = "labs.governance.identity.core.auth.webauthn_manager"
    sys.modules.pop(module_name, None)

    manager_module = importlib.import_module(module_name)
    manager = manager_module.WebAuthnManager()

    assert manager_module.WEBAUTHN_AVAILABLE is True

    registration_result = manager.generate_registration_options(
        "user-12345678",
        "constellation-user",
        "Constellation User",
        user_tier=3,
    )

    assert registration_result["success"] is True
    assert registration_result["options"]["challenge"] == FAKE_REG_CHALLENGE

    registration_call = fake_webauthn["registration"]
    assert isinstance(registration_call["challenge"], bytes)
    assert registration_call["rp_id"] == manager.rp_id

    registration_id = registration_result["registration_id"]
    stored_registration = manager.pending_registrations[registration_id]
    assert stored_registration["challenge_b64"] == FAKE_REG_CHALLENGE

    verification_response = {"id": "ignored", "response": {}, "transports": ["internal"]}
    verification_result = manager.verify_registration_response(registration_id, verification_response)
    assert verification_result["success"] is True

    expected_credential_id = base64.urlsafe_b64encode(b"cred").decode().rstrip("=")
    stored_credentials = manager.credentials[verification_result["user_id"]]
    assert stored_credentials[0].credential_id == expected_credential_id

    verify_call = fake_webauthn["verify_registration"]
    assert verify_call["expected_challenge"] == FAKE_REG_CHALLENGE.encode()

    auth_result = manager.generate_authentication_options(verification_result["user_id"], tier_level=1)
    assert auth_result["success"] is True
    assert auth_result["options"]["challenge"] == FAKE_AUTH_CHALLENGE

    auth_id = auth_result["authentication_id"]
    auth_response = {
        "id": stored_credentials[0].credential_id,
        "response": {},
    }

    auth_verification = manager.verify_authentication_response(auth_id, auth_response)
    assert auth_verification["success"] is True
    assert auth_verification["sign_count"] == 2

    verify_auth_call = fake_webauthn["verify_authentication"]
    assert verify_auth_call["expected_challenge"] == FAKE_AUTH_CHALLENGE.encode()
    assert verify_auth_call["expected_rp_id"] == manager.rp_id
    assert verify_auth_call["expected_origin"] == manager.origin
