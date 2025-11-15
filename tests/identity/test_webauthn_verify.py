#!/usr/bin/env python3
import unittest
import base64
import hashlib
import struct
from unittest.mock import patch, MagicMock
from lukhas.identity.webauthn_verify import verify_assertion, InvalidSignatureError, _base64url_decode, InvalidAssertionError

# Helper to create authenticator data
def create_auth_data(rp_id_hash, flags, sign_count):
    return rp_id_hash + flags.to_bytes(1, 'big') + sign_count.to_bytes(4, 'big')

# Helper to base64url encode
def b64_encode(data):
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

class TestWebAuthnVerify(unittest.TestCase):
    def setUp(self):
        self.user_id = "test_user"
        self.credential_id = "test_cred_id"
        self.expected_origin = "https://example.com"
        self.expected_rp_id = "example.com"
        self.expected_challenge = "test_challenge_string"

        self.rp_id_hash = hashlib.sha256(self.expected_rp_id.encode('utf-8')).digest()

        self.mock_credential = {
            "user_id": self.user_id,
            "credential_id": self.credential_id,
            "public_key": b64_encode(b"fake_public_key"),
            "counter": 10
        }

    def _create_test_assertion(self, client_data_json, auth_data_bytes, signature_bytes):
        return {
            "id": self.credential_id,
            "rawId": b64_encode(self.credential_id.encode('utf-8')),
            "response": {
                "clientDataJSON": b64_encode(client_data_json),
                "authenticatorData": b64_encode(auth_data_bytes),
                "signature": b64_encode(signature_bytes)
            },
            "type": "public-key"
        }

    @patch('lukhas.identity.webauthn_verify._verify_signature_rs256', side_effect=InvalidSignatureError("RS256 fail"))
    @patch('lukhas.identity.webauthn_verify._verify_signature_es256', return_value=None)
    def test_verify_assertion_success_es256(self, mock_verify_es256, mock_verify_rs256):
        client_data_json = f'{{"type": "webauthn.get", "challenge": "{self.expected_challenge}", "origin": "{self.expected_origin}"}}'.encode('utf-8')
        auth_data_bytes = create_auth_data(self.rp_id_hash, flags=0x01, sign_count=11)

        assertion = self._create_test_assertion(client_data_json, auth_data_bytes, b"valid_sig")
        result = verify_assertion(assertion, self.mock_credential, self.expected_challenge, self.expected_origin, self.expected_rp_id)

        self.assertTrue(result["success"])
        self.assertEqual(result["user_id"], self.user_id)
        self.assertEqual(result["new_sign_count"], 11)
        mock_verify_es256.assert_called_once()
        mock_verify_rs256.assert_not_called()

    @patch('lukhas.identity.webauthn_verify._verify_signature_es256', side_effect=InvalidSignatureError("ES256 fail"))
    @patch('lukhas.identity.webauthn_verify._verify_signature_rs256', return_value=None)
    def test_verify_assertion_success_rs256_fallback(self, mock_verify_rs256, mock_verify_es256):
        client_data_json = f'{{"type": "webauthn.get", "challenge": "{self.expected_challenge}", "origin": "{self.expected_origin}"}}'.encode('utf-8')
        auth_data_bytes = create_auth_data(self.rp_id_hash, flags=0x01, sign_count=11)

        assertion = self._create_test_assertion(client_data_json, auth_data_bytes, b"valid_sig")
        result = verify_assertion(assertion, self.mock_credential, self.expected_challenge, self.expected_origin, self.expected_rp_id)

        self.assertTrue(result["success"])
        mock_verify_es256.assert_called_once()
        mock_verify_rs256.assert_called_once()

    def test_invalid_challenge(self):
        client_data_json = f'{{"type": "webauthn.get", "challenge": "wrong_challenge", "origin": "{self.expected_origin}"}}'.encode('utf-8')
        auth_data_bytes = create_auth_data(self.rp_id_hash, flags=0x01, sign_count=11)
        assertion = self._create_test_assertion(client_data_json, auth_data_bytes, b"sig")

        result = verify_assertion(assertion, self.mock_credential, self.expected_challenge, self.expected_origin, self.expected_rp_id)
        self.assertFalse(result["success"])
        self.assertIn("Challenge verification failed", result["error"])

    def test_replay_attack(self):
        client_data_json = f'{{"type": "webauthn.get", "challenge": "{self.expected_challenge}", "origin": "{self.expected_origin}"}}'.encode('utf-8')
        # New sign count is not greater than the stored one
        auth_data_bytes = create_auth_data(self.rp_id_hash, flags=0x01, sign_count=10)
        assertion = self._create_test_assertion(client_data_json, auth_data_bytes, b"sig")

        result = verify_assertion(assertion, self.mock_credential, self.expected_challenge, self.expected_origin, self.expected_rp_id)
        self.assertFalse(result["success"])
        self.assertIn("Sign counter did not increment", result["error"])

    def test_invalid_origin(self):
        client_data_json = f'{{"type": "webauthn.get", "challenge": "{self.expected_challenge}", "origin": "https://evil.com"}}'.encode('utf-8')
        auth_data_bytes = create_auth_data(self.rp_id_hash, flags=0x01, sign_count=11)
        assertion = self._create_test_assertion(client_data_json, auth_data_bytes, b"sig")

        result = verify_assertion(assertion, self.mock_credential, self.expected_challenge, self.expected_origin, self.expected_rp_id)
        self.assertFalse(result["success"])
        self.assertIn("Origin mismatch", result["error"])

    @patch('lukhas.identity.webauthn_verify._verify_signature_es256', side_effect=InvalidSignatureError("ES256 fail"))
    @patch('lukhas.identity.webauthn_verify._verify_signature_rs256', side_effect=InvalidSignatureError("RS256 fail"))
    def test_signature_verification_fails(self, mock_verify_rs256, mock_verify_es256):
        client_data_json = f'{{"type": "webauthn.get", "challenge": "{self.expected_challenge}", "origin": "{self.expected_origin}"}}'.encode('utf-8')
        auth_data_bytes = create_auth_data(self.rp_id_hash, flags=0x01, sign_count=11)

        assertion = self._create_test_assertion(client_data_json, auth_data_bytes, b"invalid_sig")
        result = verify_assertion(assertion, self.mock_credential, self.expected_challenge, self.expected_origin, self.expected_rp_id)

        self.assertFalse(result["success"])
        self.assertIn("Signature verification failed", result["error"])

    def test_missing_response_field(self):
        assertion = {"id": "test"} # Missing 'response'
        result = verify_assertion(assertion, self.mock_credential, self.expected_challenge, self.expected_origin, self.expected_rp_id)
        self.assertFalse(result["success"])
        self.assertIn("Missing 'response' field", result["error"])

    def test_missing_client_data_json(self):
        assertion = {"id": "test", "response": {}}
        result = verify_assertion(assertion, self.mock_credential, self.expected_challenge, self.expected_origin, self.expected_rp_id)
        self.assertFalse(result["success"])
        self.assertIn("Missing 'clientDataJSON'", result["error"])

    def test_malformed_client_data_json(self):
        auth_data_bytes = create_auth_data(self.rp_id_hash, flags=0x01, sign_count=11)
        assertion = self._create_test_assertion(b"{not-json", auth_data_bytes, b"sig")
        result = verify_assertion(assertion, self.mock_credential, self.expected_challenge, self.expected_origin, self.expected_rp_id)
        self.assertFalse(result['success'])
        self.assertIn("Failed to parse clientDataJSON", result['error'])

    @patch('lukhas.identity.webauthn_verify.hashlib.sha256')
    def test_rp_id_hash_mismatch(self, mock_sha256):
        mock_sha256.return_value.digest.return_value = b"wrong_hash"
        client_data_json = f'{{"type": "webauthn.get", "challenge": "{self.expected_challenge}", "origin": "{self.expected_origin}"}}'.encode('utf-8')
        auth_data_bytes = create_auth_data(self.rp_id_hash, flags=0x01, sign_count=11)
        assertion = self._create_test_assertion(client_data_json, auth_data_bytes, b"sig")

        result = verify_assertion(assertion, self.mock_credential, self.expected_challenge, self.expected_origin, "wrong_rp_id")
        self.assertFalse(result['success'])
        self.assertIn("RP ID hash mismatch", result['error'])

if __name__ == "__main__":
    unittest.main()
