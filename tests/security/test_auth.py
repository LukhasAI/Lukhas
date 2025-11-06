import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta, timezone

# Mock external dependencies before import
# This is important to avoid ImportError if the libraries are not installed
MOCK_PYOTP = MagicMock()
MOCK_QRCODE = MagicMock()
MOCK_JWT = MagicMock()
MOCK_REDIS = MagicMock()

with patch.dict('sys.modules', {
    'pyotp': MOCK_PYOTP,
    'qrcode': MOCK_QRCODE,
    'jwt': MOCK_JWT,
    'redis': MOCK_REDIS,
}):
    from core.security.auth import EnhancedAuthenticationSystem, get_auth_system, AuthSession

@pytest.fixture
def auth_system():
    """Fixture to create a new EnhancedAuthenticationSystem instance for each test."""
    # Reset the singleton for isolation
    import core.security.auth
    core.security.auth._auth_system = None
    # Reset mocks for each test
    MOCK_JWT.reset_mock()
    MOCK_REDIS.reset_mock()
    MOCK_PYOTP.reset_mock()
    MOCK_QRCODE.reset_mock()
    return get_auth_system()

class TestAuthJWT:
    """Tests for JWT functionality in EnhancedAuthenticationSystem."""

    def test_generate_jwt(self, auth_system):
        """Test successful JWT generation."""
        user_id = "test_user"
        MOCK_JWT.encode.return_value = "test_token"

        token = auth_system.generate_jwt(user_id)

        assert token == "test_token"
        MOCK_JWT.encode.assert_called_once()
        payload = MOCK_JWT.encode.call_args[0][0]
        assert payload["user_id"] == user_id
        assert "iat" in payload
        assert "exp" in payload
        assert "jti" in payload

    def test_verify_jwt_success(self, auth_system):
        """Test successful JWT verification."""
        test_payload = {"user_id": "test_user", "jti": "test_jti"}
        MOCK_JWT.decode.return_value = test_payload

        payload = auth_system.verify_jwt("test_token")

        assert payload == test_payload
        MOCK_JWT.decode.assert_called_once_with("test_token", auth_system.jwt_secret, algorithms=[auth_system.jwt_algorithm])

    def test_verify_jwt_expired(self, auth_system):
        """Test JWT verification failure for an expired token."""
        MOCK_JWT.decode.side_effect = MOCK_JWT.ExpiredSignatureError

        payload = auth_system.verify_jwt("expired_token")

        assert payload is None

    def test_verify_jwt_invalid(self, auth_system):
        """Test JWT verification failure for an invalid token."""
        MOCK_JWT.decode.side_effect = MOCK_JWT.InvalidTokenError

        payload = auth_system.verify_jwt("invalid_token")

        assert payload is None

    def test_revoke_jwt(self, auth_system):
        """Test JWT revocation."""
        jti_to_revoke = "test_jti"
        auth_system.revoke_jwt(jti_to_revoke)

        # In memory fallback
        assert jti_to_revoke in auth_system._revoked_jtis

    def test_verify_revoked_jwt(self, auth_system):
        """Test that a revoked JWT cannot be verified."""
        jti_to_revoke = "revoked_jti"
        revoked_payload = {"user_id": "test_user", "jti": jti_to_revoke}

        # Revoke the token
        auth_system.revoke_jwt(jti_to_revoke)

        # Mock decode to return the payload of the revoked token
        MOCK_JWT.decode.return_value = revoked_payload

        payload = auth_system.verify_jwt("revoked_token")

        assert payload is None

@pytest.mark.asyncio
class TestAuthSession:
    """Tests for session management in EnhancedAuthenticationSystem."""

    async def test_create_session_success(self, auth_system):
        """Test successful session creation."""
        user_id = "test_user"
        ip_address = "127.0.0.1"
        user_agent = "pytest"

        session = await auth_system.create_session(user_id, ip_address, user_agent)

        assert isinstance(session, AuthSession)
        assert session.user_id == user_id
        assert session.ip_address == ip_address
        assert session.user_agent == user_agent
        assert session.session_id in auth_system.sessions

    async def test_validate_session_success(self, auth_system):
        """Test successful session validation."""
        session = await auth_system.create_session("test_user", "127.0.0.1", "pytest")

        validated_session = await auth_system.validate_session(session.session_id)

        assert validated_session is not None
        assert validated_session.session_id == session.session_id

    async def test_validate_session_not_found(self, auth_system):
        """Test validation of a non-existent session."""
        validated_session = await auth_system.validate_session("non_existent_session")

        assert validated_session is None

    async def test_validate_session_expired(self, auth_system):
        """Test that an expired session is not validated."""
        session = await auth_system.create_session("test_user", "127.0.0.1", "pytest")

        # Manually expire the session
        auth_system.sessions[session.session_id].last_activity = \
            datetime.now(timezone.utc) - timedelta(minutes=auth_system.session_timeout_minutes + 1)

        validated_session = await auth_system.validate_session(session.session_id)

        assert validated_session is None
        assert session.session_id not in auth_system.sessions  # Should be terminated

    async def test_terminate_session(self, auth_system):
        """Test session termination."""
        session = await auth_system.create_session("test_user", "127.0.0.1", "pytest")
        assert session.session_id in auth_system.sessions

        await auth_system.terminate_session(session.session_id)

        assert session.session_id not in auth_system.sessions

    async def test_concurrent_session_limit(self, auth_system):
        """Test that the oldest session is terminated when the concurrent session limit is reached."""
        user_id = "test_user"
        auth_system.max_concurrent_sessions = 2

        session1 = await auth_system.create_session(user_id, "127.0.0.1", "pytest")
        session2 = await auth_system.create_session(user_id, "127.0.0.1", "pytest")

        # This one should trigger the termination of session1
        session3 = await auth_system.create_session(user_id, "127.0.0.1", "pytest")

        assert session1.session_id not in auth_system.sessions
        assert session2.session_id in auth_system.sessions
        assert session3.session_id in auth_system.sessions

@pytest.mark.asyncio
class TestAuthMFA:
    """Tests for MFA functionality in EnhancedAuthenticationSystem."""

    async def test_setup_totp(self, auth_system):
        """Test TOTP setup."""
        user_id = "test_user"

        # Mock pyotp
        mock_totp_instance = MagicMock()
        mock_totp_instance.provisioning_uri.return_value = "otpauth://totp/..."
        MOCK_PYOTP.TOTP.return_value = mock_totp_instance
        MOCK_PYOTP.random_base32.return_value = "TESTSECRET"

        # Mock qrcode
        mock_qr_instance = MagicMock()
        mock_img_instance = MagicMock()
        mock_qr_instance.make_image.return_value = mock_img_instance
        MOCK_QRCODE.QRCode.return_value = mock_qr_instance

        result = await auth_system.setup_totp(user_id)

        assert "secret" in result
        assert "qr_code" in result
        assert "backup_codes" in result
        assert len(result["backup_codes"]) == auth_system.backup_code_count
        MOCK_PYOTP.TOTP.assert_called_once_with("TESTSECRET")

    async def test_verify_totp_success(self, auth_system):
        """Test successful TOTP verification."""
        user_id = "test_user"
        await auth_system.setup_totp(user_id) # Setup first

        # Mock pyotp verification
        mock_totp_instance = MagicMock()
        mock_totp_instance.verify.return_value = True
        MOCK_PYOTP.TOTP.return_value = mock_totp_instance

        is_valid = await auth_system.verify_totp(user_id, "123456")

        assert is_valid is True

    async def test_verify_totp_failure(self, auth_system):
        """Test failed TOTP verification."""
        user_id = "test_user"
        await auth_system.setup_totp(user_id)

        mock_totp_instance = MagicMock()
        mock_totp_instance.verify.return_value = False
        MOCK_PYOTP.TOTP.return_value = mock_totp_instance

        is_valid = await auth_system.verify_totp(user_id, "wrong_code")

        assert is_valid is False

    async def test_verify_backup_code_success(self, auth_system):
        """Test successful backup code verification."""
        user_id = "test_user"
        setup_result = await auth_system.setup_totp(user_id)
        backup_code = setup_result["backup_codes"][0]

        is_valid = await auth_system.verify_backup_code(user_id, backup_code)

        assert is_valid is True
        # Ensure the code is marked as used
        assert backup_code in auth_system.used_backup_codes

    async def test_verify_backup_code_failure(self, auth_system):
        """Test failed backup code verification with a wrong code."""
        user_id = "test_user"
        await auth_system.setup_totp(user_id)

        is_valid = await auth_system.verify_backup_code(user_id, "wrong_code")

        assert is_valid is False

    async def test_verify_backup_code_already_used(self, auth_system):
        """Test that a backup code can only be used once."""
        user_id = "test_user"
        setup_result = await auth_system.setup_totp(user_id)
        backup_code = setup_result["backup_codes"][0]

        # First use should be successful
        assert await auth_system.verify_backup_code(user_id, backup_code) is True

        # Second use should fail
        assert await auth_system.verify_backup_code(user_id, backup_code) is False

@pytest.mark.asyncio
class TestAuthRateLimiting:
    """Tests for rate limiting functionality."""

    async def test_check_rate_limit_not_limited(self, auth_system):
        """Test that the rate limit is not hit for a few attempts."""
        identifier = "test_user"
        for _ in range(auth_system.max_login_attempts - 1):
            await auth_system.record_failed_attempt(identifier)

        assert await auth_system.check_rate_limit(identifier) is True

    async def test_check_rate_limit_limited(self, auth_system):
        """Test that the rate limit is hit after too many attempts."""
        identifier = "test_user"
        for _ in range(auth_system.max_login_attempts):
            await auth_system.record_failed_attempt(identifier)

        assert await auth_system.check_rate_limit(identifier) is False

    async def test_clear_failed_attempts(self, auth_system):
        """Test that failed attempts can be cleared."""
        identifier = "test_user"
        for _ in range(auth_system.max_login_attempts):
            await auth_system.record_failed_attempt(identifier)

        await auth_system.clear_failed_attempts(identifier)

        assert await auth_system.check_rate_limit(identifier) is True

class TestAuthAPIKeys:
    """Tests for API key management."""

    def test_generate_api_key(self, auth_system):
        """Test API key generation."""
        user_id = "api_user"
        scopes = ["read", "write"]

        key_id, key_secret = auth_system.generate_api_key(user_id, scopes)

        assert isinstance(key_id, str)
        assert isinstance(key_secret, str)
        assert key_id in auth_system._api_keys_mem
        assert auth_system._api_keys_mem[key_id]["user_id"] == user_id

    @pytest.mark.asyncio
    async def test_verify_api_key_success(self, auth_system):
        """Test successful API key verification."""
        user_id = "api_user"
        scopes = ["read"]
        key_id, key_secret = auth_system.generate_api_key(user_id, scopes)

        verification_result = await auth_system.verify_api_key(key_id, key_secret)

        assert verification_result is not None
        assert verification_result["user_id"] == user_id
        assert verification_result["scopes"] == scopes

    @pytest.mark.asyncio
    async def test_verify_api_key_failure_wrong_secret(self, auth_system):
        """Test API key verification failure with a wrong secret."""
        user_id = "api_user"
        scopes = ["read"]
        key_id, _ = auth_system.generate_api_key(user_id, scopes)

        verification_result = await auth_system.verify_api_key(key_id, "wrong_secret")

        assert verification_result is None

    @pytest.mark.asyncio
    async def test_revoke_api_key(self, auth_system):
        """Test API key revocation."""
        user_id = "api_user"
        scopes = ["read"]
        key_id, key_secret = auth_system.generate_api_key(user_id, scopes)

        await auth_system.revoke_api_key(key_id)

        verification_result = await auth_system.verify_api_key(key_id, key_secret)

        assert verification_result is None

class TestAuthFallback:
    """Tests for the fallback implementation in core.security.auth."""

    def test_fallback_implementation_is_minimal(self):
        """Test that the fallback get_auth_system works and returns a minimal object."""
        with patch.dict('sys.modules', {'labs.core.security.auth': None}):
            import importlib
            import core.security.auth
            importlib.reload(core.security.auth)

            fallback_system = core.security.auth.get_auth_system()

            # The real system has this method, the fallback does not.
            assert not hasattr(fallback_system, 'generate_jwt')
