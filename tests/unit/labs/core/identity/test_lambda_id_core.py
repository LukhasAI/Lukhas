import unittest
from unittest.mock import patch, MagicMock
import time
import jwt

from labs.core.identity.lambda_id_core import (
    LukhasIDGenerator,
    OIDCProvider,
    WebAuthnPasskeyManager,
    ΛIDError,
    InvalidNamespaceError,
    InvalidTokenError,
    AuthenticationError,
)

class TestLukhasIDGenerator(unittest.TestCase):

    def setUp(self):
        self.generator = LukhasIDGenerator()

    def test_generate_lid_user(self):
        """Test successful ΛID generation for the USER namespace."""
        metadata = {"email": "test@example.com", "display_name": "Test User", "consent_id": "consent123"}
        lid = self.generator.generate_lid("USER", metadata)
        self.assertTrue(lid.startswith("USR-"))
        self.assertEqual(len(lid.split('-')), 4)

    def test_generate_lid_agent(self):
        """Test successful ΛID generation for the AGENT namespace."""
        metadata = {"agent_type": "test_agent", "version": "1.0", "specialist_role": "tester"}
        lid = self.generator.generate_lid("AGENT", metadata)
        self.assertTrue(lid.startswith("AGT-"))
        self.assertEqual(len(lid.split('-')), 4)

    def test_generate_lid_invalid_namespace(self):
        """Test that generating a ΛID with an invalid namespace raises an error."""
        with self.assertRaises(InvalidNamespaceError):
            self.generator.generate_lid("INVALID", {})

    def test_generate_lid_missing_metadata(self):
        """Test that generating a ΛID with missing metadata raises an error."""
        with self.assertRaises(ΛIDError):
            self.generator.generate_lid("USER", {"email": "test@example.com"})

    def test_extract_namespace(self):
        """Test that the namespace can be successfully extracted from a valid ΛID."""
        metadata = {"email": "test@example.com", "display_name": "Test User", "consent_id": "consent123"}
        lid = self.generator.generate_lid("USER", metadata)
        namespace = self.generator.extract_namespace(lid)
        self.assertEqual(namespace, "user")

    def test_extract_namespace_invalid_lid(self):
        """Test that extracting a namespace from an invalid ΛID raises an error."""
        with self.assertRaises(ΛIDError):
            self.generator.extract_namespace("invalid-lid")

    def test_extract_namespace_unknown_prefix(self):
        """Test that extracting a namespace from a ΛID with an unknown prefix raises an error."""
        with self.assertRaises(ΛIDError):
            self.generator.extract_namespace("XXX-12345-abcde-fghij")


class TestOIDCProvider(unittest.TestCase):

    def setUp(self):
        self.provider = OIDCProvider(issuer="https://test.issuer")
        self.generator = LukhasIDGenerator()
        self.lid = self.generator.generate_lid("USER", {"email": "test@example.com", "display_name": "Test User", "consent_id": "consent123"})


    @patch('jwt.encode')
    def test_issue_id_token(self, mock_jwt_encode):
        """Test successful issuance of an ID token."""
        mock_jwt_encode.return_value = "test_token"
        token = self.provider.issue_id_token(self.lid, "test_client")
        self.assertEqual(token, "test_token")
        mock_jwt_encode.assert_called_once()

    def test_issue_id_token_invalid_lid(self):
        """Test that issuing an ID token with an invalid ΛID raises an error."""
        with self.assertRaises(InvalidTokenError):
            self.provider.issue_id_token("invalid-lid", "test_client")

    def test_issue_access_token(self):
        """Test successful issuance of an access token."""
        token_data = self.provider.issue_access_token(self.lid, ["openid"], "test_client")
        self.assertIn("access_token", token_data)
        self.assertEqual(token_data["token_type"], "Bearer")

    def test_issue_access_token_invalid_scope(self):
        """Test that issuing an access token with an invalid scope raises an error."""
        with self.assertRaises(InvalidTokenError):
            self.provider.issue_access_token(self.lid, ["invalid_scope"], "test_client")

    @patch('jwt.decode')
    def test_validate_token_valid(self, mock_jwt_decode):
        """Test validation of a valid token."""
        mock_jwt_decode.return_value = {"sub": self.lid}
        result = self.provider.validate_token("valid.jwt.token")
        self.assertTrue(result["valid"])
        self.assertEqual(result["type"], "id_token")

    @patch('jwt.decode')
    def test_validate_token_expired(self, mock_jwt_decode):
        """Test validation of an expired token."""
        mock_jwt_decode.side_effect = jwt.ExpiredSignatureError("Token expired")
        result = self.provider.validate_token("expired.jwt.token")
        self.assertFalse(result['valid'])
        self.assertEqual(result['error'], 'token_expired')


class TestWebAuthnPasskeyManager(unittest.TestCase):

    def setUp(self):
        self.manager = WebAuthnPasskeyManager()
        self.generator = LukhasIDGenerator()
        self.lid = self.generator.generate_lid("USER", {"email": "test@example.com", "display_name": "Test User", "consent_id": "consent123"})


    @patch('secrets.token_bytes', return_value=b'test_challenge')
    def test_initiate_registration(self, mock_token_bytes):
        """Test successful initiation of a WebAuthn registration."""
        result = self.manager.initiate_registration(self.lid, "test@example.com")
        self.assertIn("publicKey", result)
        self.assertIn("challenge", result["publicKey"])

    def test_initiate_registration_invalid_email(self):
        """Test that initiating a registration with an invalid email raises an error."""
        with self.assertRaises(AuthenticationError):
            self.manager.initiate_registration(self.lid, "invalid-email")


    def test_complete_registration(self):
        """Test successful completion of a WebAuthn registration."""
        self.manager.challenges[self.lid] = {"challenge": "test", "timestamp": time.time()}
        credential = {"id": "test_cred", "response": {"publicKey": "key"}}
        self.assertTrue(self.manager.complete_registration(self.lid, credential))
        self.assertIn(self.lid, self.manager.credentials)

    def test_complete_registration_no_challenge(self):
        """Test that completing a registration without a challenge fails."""
        credential = {"id": "test_cred", "response": {"publicKey": "key"}}
        self.assertFalse(self.manager.complete_registration(self.lid, credential))

    @patch('secrets.token_bytes', return_value=b'test_challenge')
    def test_initiate_authentication(self, mock_token_bytes):
        """Test successful initiation of a WebAuthn authentication."""
        result = self.manager.initiate_authentication(self.lid)
        self.assertIn("publicKey", result)
        self.assertIn("challenge", result["publicKey"])

    @patch('labs.core.identity.lambda_id_core.WebAuthnPasskeyManager._decode_base64', return_value=b'decoded')
    @patch('labs.core.identity.lambda_id_core.WebAuthnPasskeyManager._load_public_key')
    @patch('labs.core.identity.lambda_id_core.WebAuthnPasskeyManager._verify_signature')
    @patch('json.loads', return_value={'challenge': 'dGVzdA=='})
    def test_verify_authentication_success(self, mock_json_loads, mock_verify_sig, mock_load_pk, mock_decode_b64):
        """Test successful verification of a WebAuthn authentication."""
        self.manager.challenges[self.lid] = {'challenge': 'dGVzdA==', 'timestamp': time.time()}
        self.manager.credentials[self.lid] = {'credential_id': 'test_cred', 'public_key': 'key'}

        assertion = {
            'id': 'test_cred',
            'response': {
                'clientDataJSON': 'e30=',
                'authenticatorData': 'e30=',
                'signature': 'e30='
            }
        }

        self.assertTrue(self.manager.verify_authentication(self.lid, assertion))

    def test_verify_authentication_no_challenge(self):
        """Test that verifying an authentication without a challenge fails."""
        assertion = {'response': {}}
        self.assertFalse(self.manager.verify_authentication(self.lid, assertion))


if __name__ == "__main__":
    unittest.main()
