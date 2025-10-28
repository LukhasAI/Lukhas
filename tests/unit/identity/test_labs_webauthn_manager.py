import base64

import pytest

from labs.governance.identity.core.auth import webauthn_manager


class FakeEnum(str):
    def __new__(cls, value: str):
        obj = str.__new__(cls, value)
        obj.value = value
        return obj


class FakeStructs:
    class UserVerificationRequirement:
        REQUIRED = FakeEnum("required")
        PREFERRED = FakeEnum("preferred")

    class ResidentKeyRequirement:
        REQUIRED = FakeEnum("required")
        PREFERRED = FakeEnum("preferred")

    class AttestationConveyancePreference:
        DIRECT = FakeEnum("direct")
        NONE = FakeEnum("none")

    class AuthenticatorAttachment:
        PLATFORM = FakeEnum("platform")
        CROSS_PLATFORM = FakeEnum("cross-platform")

    class AuthenticatorSelectionCriteria:
        def __init__(self, authenticator_attachment=None, resident_key=None, user_verification=None):
            self.authenticator_attachment = authenticator_attachment
            self.resident_key = resident_key
            self.user_verification = user_verification

    class PublicKeyCredentialDescriptor:
        def __init__(self, *, type, id, transports=None):  # noqa: A002 - match library signature
            self.type = type
            self.id = id
            self.transports = transports

    class RegistrationExtensionInputs(dict):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

    class AuthenticationExtensionsClientInputs(dict):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)


class FakeOptions:
    def __init__(self, payload: dict[str, object]):
        self._payload = payload

    def model_dump(self) -> dict[str, object]:
        return self._payload


@pytest.fixture(name="fake_structs")
def fake_structs_fixture():
    return FakeStructs()


def test_generate_authentication_options_without_library(monkeypatch):
    manager = webauthn_manager.WebAuthnManager()

    monkeypatch.setattr(webauthn_manager, "WEBAUTHN_AVAILABLE", False)
    monkeypatch.setattr(webauthn_manager, "_generate_authentication_options", None)
    monkeypatch.setattr(webauthn_manager, "_generate_registration_options", None)
    monkeypatch.setattr(webauthn_manager, "structs", None)

    result = manager.generate_authentication_options(user_id="user-12345678", tier_level=2)

    assert result["success"] is True
    auth_id = result["authentication_id"]
    cached = manager.pending_authentications[auth_id]
    challenge_b64 = result["options"]["challenge"]
    assert cached["challenge_b64"] == challenge_b64
    assert base64.urlsafe_b64encode(cached["challenge"]).decode().rstrip("=") == challenge_b64


def test_generate_options_with_webauthn_library(monkeypatch, fake_structs):
    captured = {}

    def fake_registration(**kwargs):
        captured["registration"] = kwargs
        challenge_bytes = kwargs["challenge"]
        payload = {
            "challenge": base64.urlsafe_b64encode(challenge_bytes).decode().rstrip("="),
            "rp": {"id": kwargs["rp_id"], "name": kwargs["rp_name"]},
            "user": {
                "id": "ignored",
                "name": kwargs["user_name"],
                "displayName": kwargs["user_display_name"],
            },
            "excludeCredentials": [{"id": "lib-cred", "type": "public-key"}],
            "authenticatorSelection": {
                "userVerification": fake_structs.UserVerificationRequirement.REQUIRED,
            },
        }
        return FakeOptions(payload)

    def fake_authentication(**kwargs):
        captured["authentication"] = kwargs
        challenge_bytes = kwargs["challenge"]
        payload = {
            "challenge": base64.urlsafe_b64encode(challenge_bytes).decode().rstrip("="),
            "rpId": f"lib-{kwargs['rp_id']}",
            "allowCredentials": [{"id": "lib-auth-cred", "type": "public-key"}],
            "userVerification": fake_structs.UserVerificationRequirement.PREFERRED,
        }
        return FakeOptions(payload)

    monkeypatch.setattr(webauthn_manager, "WEBAUTHN_AVAILABLE", True)
    monkeypatch.setattr(webauthn_manager, "structs", fake_structs, raising=False)
    monkeypatch.setattr(webauthn_manager, "_generate_registration_options", fake_registration)
    monkeypatch.setattr(webauthn_manager, "_generate_authentication_options", fake_authentication)

    manager = webauthn_manager.WebAuthnManager()

    registration = manager.generate_registration_options(
        "user-abcdef01",
        "user@example.com",
        "User Example",
        user_tier=3,
    )

    assert registration["success"] is True
    assert registration["options"]["rp"]["id"] == manager.rp_id
    assert registration["options"]["excludeCredentials"][0]["id"] == "lib-cred"
    assert captured["registration"]["rp_id"] == manager.rp_id
    assert isinstance(captured["registration"]["challenge"], bytes)

    manager.credentials["user-abcdef01"] = [
        webauthn_manager.WebAuthnCredential(
            {
                "credential_id": "cred-001",
                "user_id": "user-abcdef01",
                "tier_level": 3,
                "authenticator_data": {"transports": ["usb"]},
            }
        )
    ]

    authentication = manager.generate_authentication_options("user-abcdef01", tier_level=2)

    assert authentication["success"] is True
    assert authentication["options"]["rpId"] == f"lib-{manager.rp_id}"
    assert authentication["options"]["allowCredentials"][0]["id"] == "lib-auth-cred"
    assert captured["authentication"]["rp_id"] == manager.rp_id
    assert isinstance(captured["authentication"]["challenge"], bytes)

    pending = manager.pending_authentications[authentication["authentication_id"]]
    assert base64.urlsafe_b64encode(pending["challenge"]).decode().rstrip("=") == authentication["options"]["challenge"]
