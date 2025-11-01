import base64
import hashlib
import json

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from labs.core.identity.lambda_id_core import WebAuthnPasskeyManager


def _b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _register_passkey(manager: WebAuthnPasskeyManager, lid: str, private_key: ed25519.Ed25519PrivateKey) -> str:
    manager.initiate_registration(lid, "user@example.com")
    credential = {
        "id": "cred-" + lid,
        "response": {
            "publicKey": base64.b64encode(
                private_key.public_key().public_bytes(
                    encoding=serialization.Encoding.Raw,
                    format=serialization.PublicFormat.Raw,
                )
            ).decode("ascii")
        },
    }
    assert manager.complete_registration(lid, credential)
    return credential["id"]


def _build_assertion(private_key: ed25519.Ed25519PrivateKey, challenge: str, credential_id: str):
    client_data = {
        "type": "webauthn.get",
        "challenge": challenge,
        "origin": "https://ai",
    }
    client_data_bytes = json.dumps(client_data, separators=(",", ":")).encode("utf-8")
    authenticator_data = b"constellation-authenticator"
    signature_payload = authenticator_data + hashlib.sha256(client_data_bytes).digest()
    signature = private_key.sign(signature_payload)

    return {
        "id": credential_id,
        "response": {
            "clientDataJSON": _b64u(client_data_bytes),
            "authenticatorData": _b64u(authenticator_data),
            "signature": _b64u(signature),
        },
    }


def test_verify_authentication_success():
    manager = WebAuthnPasskeyManager()
    lid = "USR-test-1234"
    private_key = ed25519.Ed25519PrivateKey.generate()
    credential_id = _register_passkey(manager, lid, private_key)

    auth_options = manager.initiate_authentication(lid)
    challenge = auth_options["publicKey"]["challenge"]
    assertion = _build_assertion(private_key, challenge, credential_id)

    assert manager.verify_authentication(lid, assertion) is True
    assert lid not in manager.challenges
    assert manager._security_events[-1]["event_type"] == "authentication_success"


def test_verify_authentication_invalid_signature():
    manager = WebAuthnPasskeyManager()
    lid = "USR-test-invalid"
    private_key = ed25519.Ed25519PrivateKey.generate()
    credential_id = _register_passkey(manager, lid, private_key)

    auth_options = manager.initiate_authentication(lid)
    challenge = auth_options["publicKey"]["challenge"]
    assertion = _build_assertion(private_key, challenge, credential_id)

    # Corrupt the signature to simulate tampering
    tampered_signature = base64.urlsafe_b64encode(b"tampered-signature").rstrip(b"=").decode("ascii")
    assertion["response"]["signature"] = tampered_signature

    assert manager.verify_authentication(lid, assertion) is False
    assert lid not in manager.challenges
    assert manager._security_events[-1]["event_type"] == "authentication_failed"
