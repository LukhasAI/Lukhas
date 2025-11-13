import pytest
import base64
import hashlib
import time
import json
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

# Adhering to LUKHAS import rules
from core.security.auth import get_auth_system, EnhancedAuthenticationSystem, AuthMethod
from lukhas.identity.webauthn_credential import WebAuthnCredentialStore, WebAuthnCredential
from lukhas.identity.webauthn_verify import verify_assertion, InvalidSignatureError, InvalidAssertionError

# Fixtures for testing
@pytest.fixture
def credential_store() -> WebAuthnCredentialStore:
    """Returns a new, empty WebAuthnCredentialStore for each test."""
    return WebAuthnCredentialStore()

@pytest.fixture
def sample_credential() -> dict:
    """Returns a dictionary with valid sample credential data."""
    return {
        "credential_id": "test_cred_id_123",
        "public_key": "public_key_abc",
        "counter": 0,
        "created_at": datetime.now().isoformat(),
        "device_name": "Test Key",
    }

class TestWebAuthnCredentialStore:
    """Tests for the in-memory WebAuthnCredentialStore."""

    def test_store_and_get_credential(self, credential_store: WebAuthnCredentialStore, sample_credential: dict):
        user_id = "user-1"
        credential_store.store_credential(user_id, sample_credential)
        retrieved = credential_store.get_credential(sample_credential["credential_id"])
        assert retrieved is not None
        assert retrieved["user_id"] == user_id

    def test_store_duplicate_credential_raises_error(self, credential_store: WebAuthnCredentialStore, sample_credential: dict):
        user_id = "user-1"
        credential_store.store_credential(user_id, sample_credential)
        with pytest.raises(ValueError, match="already exists"):
            credential_store.store_credential(user_id, sample_credential)

    @pytest.mark.parametrize("missing_field", ["credential_id", "public_key", "counter", "created_at"])
    def test_store_credential_with_missing_field_raises_error(self, credential_store: WebAuthnCredentialStore, sample_credential: dict, missing_field: str):
        del sample_credential[missing_field]
        with pytest.raises(ValueError, match="Missing required field"):
            credential_store.store_credential("user-1", sample_credential)

    @pytest.mark.parametrize("field, value, expected_error", [
        ("credential_id", "", TypeError), ("credential_id", 123, TypeError),
        ("public_key", 123, TypeError), ("counter", "abc", TypeError),
        ("created_at", 123, TypeError)
    ])
    def test_store_credential_with_invalid_types_raises_error(self, credential_store: WebAuthnCredentialStore, sample_credential: dict, field: str, value, expected_error):
        sample_credential[field] = value
        with pytest.raises(expected_error):
            credential_store.store_credential("user-1", sample_credential)

    def test_update_credential_with_invalid_types_raises_error(self, credential_store: WebAuthnCredentialStore, sample_credential: dict):
        credential_store.store_credential("user-1", sample_credential)
        with pytest.raises(TypeError):
            credential_store.update_credential(sample_credential["credential_id"], {"counter": "not-an-int"})
        with pytest.raises(TypeError):
            credential_store.update_credential(sample_credential["credential_id"], {"last_used": 123})
        with pytest.raises(TypeError):
            credential_store.update_credential(sample_credential["credential_id"], {"device_name": 123})


    def test_get_nonexistent_credential_returns_none(self, credential_store: WebAuthnCredentialStore):
        assert credential_store.get_credential("nonexistent_id") is None

    def test_list_credentials_for_user(self, credential_store: WebAuthnCredentialStore, sample_credential: dict):
        user_id = "user-1"
        cred2 = sample_credential.copy(); cred2["credential_id"] = "cred-2"
        credential_store.store_credential(user_id, sample_credential)
        credential_store.store_credential(user_id, cred2)
        credential_store.store_credential("user-2", {"credential_id": "cred-3", "public_key": "pk", "counter": 0, "created_at": "ts"})
        user1_creds = credential_store.list_credentials(user_id)
        assert len(user1_creds) == 2
        assert {c["credential_id"] for c in user1_creds} == {"test_cred_id_123", "cred-2"}

    def test_list_credentials_for_user_with_no_credentials(self, credential_store: WebAuthnCredentialStore):
        assert credential_store.list_credentials("user-with-no-creds") == []

    def test_delete_credential(self, credential_store: WebAuthnCredentialStore, sample_credential: dict):
        user_id, cred_id = "user-1", sample_credential["credential_id"]
        credential_store.store_credential(user_id, sample_credential)
        assert credential_store.get_credential(cred_id) is not None
        assert credential_store.delete_credential(cred_id) is True
        assert credential_store.get_credential(cred_id) is None

    def test_delete_nonexistent_credential(self, credential_store: WebAuthnCredentialStore):
        assert credential_store.delete_credential("nonexistent_id") is False

    def test_update_credential(self, credential_store: WebAuthnCredentialStore, sample_credential: dict):
        user_id, cred_id = "user-1", sample_credential["credential_id"]
        credential_store.store_credential(user_id, sample_credential)
        updates = {"counter": 10, "device_name": "New Name"}
        assert credential_store.update_credential(cred_id, updates) is True
        retrieved = credential_store.get_credential(cred_id)
        assert retrieved["counter"] == 10
        assert retrieved["device_name"] == "New Name"

    def test_update_nonexistent_credential(self, credential_store: WebAuthnCredentialStore):
        assert credential_store.update_credential("nonexistent_id", {"counter": 1}) is False

    @pytest.mark.parametrize("immutable_field", ["credential_id", "user_id"])
    def test_update_immutable_fields_raises_error(self, credential_store: WebAuthnCredentialStore, sample_credential: dict, immutable_field: str):
        credential_store.store_credential("user-1", sample_credential)
        with pytest.raises(ValueError, match=f"Cannot update {immutable_field}"):
            credential_store.update_credential(sample_credential["credential_id"], {immutable_field: "new_value"})

    def test_count_credentials(self, credential_store: WebAuthnCredentialStore, sample_credential: dict):
        credential_store.store_credential("user-1", sample_credential)
        assert credential_store.count_credentials() == 1
        assert credential_store.count_credentials("user-1") == 1

    def test_get_credential_by_user_and_id(self, credential_store: WebAuthnCredentialStore, sample_credential: dict):
        user_id, cred_id = "user-1", sample_credential["credential_id"]
        credential_store.store_credential(user_id, sample_credential)
        assert credential_store.get_credential_by_user_and_id(user_id, cred_id) is not None
        assert credential_store.get_credential_by_user_and_id("user-2", cred_id) is None

# --- Tests for WebAuthn Assertion Verification ---

def b64_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

@pytest.fixture
def webauthn_credential() -> WebAuthnCredential:
    return {"user_id": "test-user", "credential_id": "cred-id-123", "public_key": b64_encode(b"fake_public_key"), "counter": 5, "created_at": datetime.now().isoformat()}

def create_valid_assertion(cred_id: str, challenge: str, origin: str, rp_id: str, sign_count: int, user_present: bool = True) -> dict:
    client_data = {"type": "webauthn.get", "challenge": challenge, "origin": origin}
    client_data_json_bytes = json.dumps(client_data).encode('utf-8')
    rp_id_hash = hashlib.sha256(rp_id.encode('utf-8')).digest()
    flags = b'\x01' if user_present else b'\x00'
    sign_count_bytes = sign_count.to_bytes(4, 'big')
    authenticator_data_bytes = rp_id_hash + flags + sign_count_bytes
    return {"id": cred_id, "response": {"clientDataJSON": b64_encode(client_data_json_bytes), "authenticatorData": b64_encode(authenticator_data_bytes), "signature": b64_encode(b"sig")}}

@patch('lukhas.identity.webauthn_verify._verify_signature_rs256')
@patch('lukhas.identity.webauthn_verify._verify_signature_es256')
class TestWebAuthnVerification:
    EXPECTED_CHALLENGE = "u_xbS893sL-2tZojzHsCgw"
    EXPECTED_ORIGIN = "https://lukhas.ai"
    EXPECTED_RP_ID = "lukhas.ai"

    def test_verify_assertion_success_es256(self, mock_v_es256, mock_v_rs256, webauthn_credential):
        mock_v_es256.return_value = None
        new_sign_count = webauthn_credential["counter"] + 1
        assertion = create_valid_assertion(webauthn_credential["credential_id"], self.EXPECTED_CHALLENGE, self.EXPECTED_ORIGIN, self.EXPECTED_RP_ID, new_sign_count)
        result = verify_assertion(assertion, webauthn_credential, self.EXPECTED_CHALLENGE, self.EXPECTED_ORIGIN, self.EXPECTED_RP_ID)
        assert result["success"] is True

    def test_verify_assertion_success_rs256_fallback(self, mock_v_es256, mock_v_rs256, webauthn_credential):
        mock_v_es256.side_effect = InvalidSignatureError("ES256 failed")
        mock_v_rs256.return_value = None
        new_sign_count = webauthn_credential["counter"] + 1
        assertion = create_valid_assertion(webauthn_credential["credential_id"], self.EXPECTED_CHALLENGE, self.EXPECTED_ORIGIN, self.EXPECTED_RP_ID, new_sign_count)
        result = verify_assertion(assertion, webauthn_credential, self.EXPECTED_CHALLENGE, self.EXPECTED_ORIGIN, self.EXPECTED_RP_ID)
        assert result["success"] is True

    def test_verify_assertion_all_signatures_fail(self, mock_v_es256, mock_v_rs256, webauthn_credential):
        mock_v_es256.side_effect = InvalidSignatureError("ES256 failed")
        mock_v_rs256.side_effect = InvalidSignatureError("RS256 failed")
        assertion = create_valid_assertion(webauthn_credential["credential_id"], self.EXPECTED_CHALLENGE, self.EXPECTED_ORIGIN, self.EXPECTED_RP_ID, webauthn_credential["counter"] + 1)
        result = verify_assertion(assertion, webauthn_credential, self.EXPECTED_CHALLENGE, self.EXPECTED_ORIGIN, self.EXPECTED_RP_ID)
        assert result["success"] is False and "Signature verification failed" in result["error"]

    def test_verify_assertion_unexpected_error(self, mock_v_es256, webauthn_credential):
        mock_v_es256.side_effect = Exception("Unexpected crypto error")
        assertion = create_valid_assertion(webauthn_credential["credential_id"], self.EXPECTED_CHALLENGE, self.EXPECTED_ORIGIN, self.EXPECTED_RP_ID, 10)
        result = verify_assertion(assertion, webauthn_credential, self.EXPECTED_CHALLENGE, self.EXPECTED_ORIGIN, self.EXPECTED_RP_ID)
        assert result["success"] is False and "Unexpected verification error" in result["error"]

    @patch('lukhas.identity.webauthn_verify._parse_client_data_json', side_effect=InvalidAssertionError("bad json"))
    def test_verify_assertion_bad_client_json(self, mock_parse, mock_v_es256, mock_v_rs256, webauthn_credential):
        assertion = create_valid_assertion(webauthn_credential["credential_id"], "c", "o", "r", 10)
        result = verify_assertion(assertion, webauthn_credential, "c", "o", "r")
        assert result["success"] is False and "bad json" in result["error"]

# --- Tests for EnhancedAuthenticationSystem ---

@pytest.fixture
def auth_system() -> EnhancedAuthenticationSystem:
    return get_auth_system()

class TestEnhancedAuthenticationSystem:
    def test_generate_and_verify_jwt_success(self, auth_system: EnhancedAuthenticationSystem):
        user_id = "jwt-user-1"
        token = auth_system.generate_jwt(user_id)
        payload = auth_system.verify_jwt(token)
        assert payload is not None and payload["user_id"] == user_id

    def test_jwt_with_custom_claims_namespaces(self, auth_system: EnhancedAuthenticationSystem):
        user_id = "jwt-user-2"
        claims = {"namespace": "billing", "roles": ["admin"]}
        token = auth_system.generate_jwt(user_id, claims=claims)
        payload = auth_system.verify_jwt(token)
        assert payload is not None and payload["namespace"] == "billing"

    def test_jwt_verification_expired_token(self, auth_system: EnhancedAuthenticationSystem):
        auth_system.jwt_expiry_hours = 0
        token = auth_system.generate_jwt("user-3")
        time.sleep(1.1)
        assert auth_system.verify_jwt(token) is None

    def test_jwt_verification_invalid_signature(self, auth_system: EnhancedAuthenticationSystem):
        token = auth_system.generate_jwt("user-4")
        tampered_token = token[:-5] + "tamper"
        assert auth_system.verify_jwt(tampered_token) is None

    def test_jwt_revocation(self, auth_system: EnhancedAuthenticationSystem):
        token = auth_system.generate_jwt("user-5")
        payload = auth_system.verify_jwt(token)
        assert payload is not None
        auth_system.revoke_jwt(payload["jti"])
        assert auth_system.verify_jwt(token) is None

    @pytest.mark.asyncio
    async def test_api_key_management(self, auth_system: EnhancedAuthenticationSystem):
        user_id = "api-user-1"
        key_id, key_secret = auth_system.generate_api_key(user_id, scopes=["read"])
        verification_result = await auth_system.verify_api_key(key_id, key_secret)
        assert verification_result is not None and verification_result["user_id"] == user_id
        await auth_system.revoke_api_key(key_id)
        assert await auth_system.verify_api_key(key_id, key_secret) is None

    @pytest.mark.asyncio
    async def test_session_management(self, auth_system: EnhancedAuthenticationSystem):
        user_id = "session-user-1"
        session = await auth_system.create_session(user_id, "127.0.0.1", "pytest")
        assert session is not None
        validated_session = await auth_system.validate_session(session.session_id)
        assert validated_session is not None and validated_session.user_id == user_id
        await auth_system.terminate_session(session.session_id)
        assert await auth_system.validate_session(session.session_id) is None

    @pytest.mark.asyncio
    async def test_mfa_totp_verification(self, auth_system: EnhancedAuthenticationSystem):
        user_id = "mfa-user-1"
        with patch('pyotp.TOTP') as mock_totp:
            mock_instance = mock_totp.return_value
            mock_instance.verify.return_value = True

            # Setup a fake MFA for the user
            await auth_system.setup_totp(user_id) # This will store a secret

            result = await auth_system.verify_totp(user_id, "123456")
            assert result is True
            mock_instance.verify.assert_called_with("123456", valid_window=1)
