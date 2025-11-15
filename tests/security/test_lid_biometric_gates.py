
import unittest
import base64
import struct
from unittest.mock import patch

from lukhas.identity import (
    verify_assertion,
    WebAuthnCredential,
)

# Helper function to create realistic authenticator data
def create_mock_auth_data(rp_id_hash: bytes, flags: int, sign_count: int) -> bytes:
    """Creates a mock authenticator data structure."""
    return rp_id_hash + struct.pack(">BI", flags, sign_count)

# Helper function to create a mock credential
def create_mock_credential() -> WebAuthnCredential:
    """Creates a mock WebAuthnCredential for testing."""
    return {
        "user_id": "test_user",
        "credential_id": "test_credential_id",
        "public_key": base64.urlsafe_b64encode(b"test_public_key").decode('utf-8'),
        "counter": 0,
        "created_at": "2023-01-01T00:00:00Z",
    }

# Helper function to create a mock assertion
def create_mock_assertion(auth_data: bytes) -> dict:
    """Creates a mock WebAuthn assertion for testing."""
    return {
        "response": {
            "clientDataJSON": base64.urlsafe_b64encode(b'{"type": "webauthn.get", "challenge": "test_challenge", "origin": "https://example.com"}').decode('utf-8'),
            "authenticatorData": base64.urlsafe_b64encode(auth_data).decode('utf-8'),
            "signature": base64.urlsafe_b64encode(b"test_signature").decode('utf-8'),
        },
        "id": "test_credential_id",
    }

class TestLidBiometricGates(unittest.TestCase):

    def test_biometric_gate_user_verified_flag_set(self):
        """Tests that the user_verified flag is correctly parsed when set."""
        credential = create_mock_credential()
        auth_data = create_mock_auth_data(rp_id_hash=b"\x00" * 32, flags=0x05, sign_count=1) # 0x01 (user present) | 0x04 (user verified)
        assertion = create_mock_assertion(auth_data)

        with patch('lukhas.identity.webauthn_verify.hashlib.sha256') as mock_sha256:
            mock_sha256.return_value.digest.return_value = b"\x00" * 32
            with patch('lukhas.identity.webauthn_verify._verify_signature_es256'):
                result = verify_assertion(
                    assertion=assertion,
                    credential=credential,
                    expected_challenge="test_challenge",
                    expected_origin="https://example.com",
                    expected_rp_id="example.com",
                )
                self.assertTrue(result["success"])
                self.assertTrue(result["user_verified"])

    def test_biometric_gate_user_verified_flag_not_set(self):
        """Tests that the user_verified flag is correctly parsed when not set."""
        credential = create_mock_credential()
        auth_data = create_mock_auth_data(rp_id_hash=b"\x00" * 32, flags=0x01, sign_count=1) # 0x01 (user present)
        assertion = create_mock_assertion(auth_data)

        with patch('lukhas.identity.webauthn_verify.hashlib.sha256') as mock_sha256:
            mock_sha256.return_value.digest.return_value = b"\x00" * 32
            with patch('lukhas.identity.webauthn_verify._verify_signature_es256'):
                result = verify_assertion(
                    assertion=assertion,
                    credential=credential,
                    expected_challenge="test_challenge",
                    expected_origin="https://example.com",
                    expected_rp_id="example.com",
                )
                self.assertTrue(result["success"])
                self.assertNotIn("user_verified", result)

if __name__ == "__main__":
    unittest.main()
