import pytest
import asyncio
from unittest.mock import MagicMock, patch
import time
import json
from datetime import datetime, timedelta, timezone

# Mock redis before importing the module
import sys
mock_redis_lib = MagicMock()
mock_redis_client = MagicMock()
mock_redis_lib.from_url.return_value = mock_redis_client
sys.modules['redis'] = mock_redis_lib

# Mock pyotp and qrcode for consistent testing
sys.modules['pyotp'] = MagicMock()
sys.modules['qrcode'] = MagicMock()

from labs.core.security.auth import EnhancedAuthenticationSystem, get_auth_system, AuthMethod

@pytest.fixture
def auth_system():
    """Fixture for a fresh EnhancedAuthenticationSystem instance (no redis)."""
    import labs.core.security.auth
    labs.core.security.auth._auth_system = None
    # Explicitly pass redis_url=None
    return get_auth_system(redis_url=None)

@pytest.fixture
def auth_system_with_redis():
    """Fixture for a fresh EnhancedAuthenticationSystem instance with a mock redis client."""
    import labs.core.security.auth
    labs.core.security.auth._auth_system = None
    # Reset mock client state for test isolation
    mock_redis_client.reset_mock()
    # Ensure exists returns an int
    mock_redis_client.exists.return_value = 0
    return get_auth_system(redis_url="redis://mock")

@pytest.mark.asyncio
async def test_jwt_generation_and_verification(auth_system):
    """Test that a JWT can be generated and successfully verified."""
    user_id = "test_user"
    token = auth_system.generate_jwt(user_id)
    payload = auth_system.verify_jwt(token)
    assert payload is not None
    assert payload["user_id"] == user_id

@pytest.mark.asyncio
async def test_jwt_expiration(auth_system):
    """Test that an expired JWT fails verification."""
    auth_system.jwt_expiry_hours = 0
    user_id = "test_user_expired"
    token = auth_system.generate_jwt(user_id)
    time.sleep(1.1) # Sleep to ensure expiry
    payload = auth_system.verify_jwt(token)
    assert payload is None

@pytest.mark.asyncio
async def test_jwt_revocation(auth_system):
    """Test that a revoked JWT fails verification."""
    user_id = "test_user_revoked"
    token = auth_system.generate_jwt(user_id)
    payload = auth_system.verify_jwt(token)
    jti = payload.get("jti")
    auth_system.revoke_jwt(jti)
    assert auth_system.verify_jwt(token) is None

@pytest.mark.asyncio
async def test_jwt_revocation_with_redis(auth_system_with_redis):
    """Test JWT revocation using the redis path."""
    user_id = "test_user_revoked_redis"
    token = auth_system_with_redis.generate_jwt(user_id)

    # Before revocation
    mock_redis_client.exists.return_value = 0
    payload = auth_system_with_redis.verify_jwt(token)
    assert payload is not None

    # Revoke
    jti = payload.get("jti")
    auth_system_with_redis.revoke_jwt(jti)
    mock_redis_client.setex.assert_called_once()

    # After revocation
    mock_redis_client.exists.return_value = 1
    assert auth_system_with_redis.verify_jwt(token) is None

@pytest.mark.asyncio
async def test_session_management(auth_system):
    """Test session creation, validation, and termination."""
    user_id = "session_user"
    session = await auth_system.create_session(user_id, "127.0.0.1", "test-agent")
    validated_session = await auth_system.validate_session(session.session_id)
    assert validated_session.user_id == user_id
    await auth_system.terminate_session(session.session_id)
    assert await auth_system.validate_session(session.session_id) is None

@pytest.mark.asyncio
async def test_session_management_with_redis(auth_system_with_redis):
    """Test session management using the redis path."""
    user_id = "session_user_redis"
    session = await auth_system_with_redis.create_session(user_id, "127.0.0.1", "test-agent")
    mock_redis_client.setex.assert_called_once()

    # Simulate session not in memory, but in redis
    auth_system_with_redis.sessions = {}
    session_data = {
        "user_id": user_id, "ip_address": "127.0.0.1", "user_agent": "test-agent",
        "created_at": datetime.now(timezone.utc).isoformat(), "mfa_verified": False
    }
    mock_redis_client.get.return_value = json.dumps(session_data)

    validated_session = await auth_system_with_redis.validate_session(session.session_id)
    assert validated_session is not None
    mock_redis_client.expire.assert_called_once()

    await auth_system_with_redis.terminate_session(session.session_id)
    mock_redis_client.delete.assert_called_once()

@pytest.mark.asyncio
async def test_session_timeout(auth_system):
    """Test that a session correctly times out."""
    user_id = "timeout_user"
    session = await auth_system.create_session(user_id, "127.0.0.1", "test-agent")
    # Manually set last_activity to be in the past
    auth_system.sessions[session.session_id].last_activity = datetime.now(timezone.utc) - timedelta(minutes=auth_system.session_timeout_minutes + 1)
    assert await auth_system.validate_session(session.session_id) is None

@pytest.mark.asyncio
async def test_max_concurrent_sessions(auth_system):
    """Test that the oldest session is terminated when max sessions is reached."""
    user_id = "max_session_user"
    auth_system.max_concurrent_sessions = 2

    session1 = await auth_system.create_session(user_id, "1.1.1.1", "agent1")
    time.sleep(0.1) # ensure creation times are different
    session2 = await auth_system.create_session(user_id, "2.2.2.2", "agent2")

    assert session1.session_id in auth_system.sessions
    assert session2.session_id in auth_system.sessions

    # This should terminate session1
    session3 = await auth_system.create_session(user_id, "3.3.3.3", "agent3")

    assert session1.session_id not in auth_system.sessions
    assert session2.session_id in auth_system.sessions
    assert session3.session_id in auth_system.sessions

@pytest.mark.asyncio
async def test_totp_setup_and_verification(auth_system):
    """Test TOTP setup and verification."""
    user_id = "totp_user"
    mock_totp_instance = MagicMock()
    mock_totp_instance.verify.return_value = True
    mock_totp_instance.provisioning_uri.return_value = "otpauth://totp/test"

    with patch('labs.core.security.auth.pyotp.TOTP', return_value=mock_totp_instance):
        setup_info = await auth_system.setup_totp(user_id)
        assert "secret" in setup_info

        assert await auth_system.verify_totp(user_id, "123456")
        assert auth_system.mfa_setups[user_id][AuthMethod.TOTP].verified

@pytest.mark.asyncio
async def test_sms_mfa_flow_failures(auth_system):
    """Test failure modes for SMS MFA."""
    user_id = "sms_fail_user"
    await auth_system.setup_sms_mfa(user_id, "1234567890")

    # Test wrong code
    assert not await auth_system.verify_sms_code(user_id, "wrong_code")

    # Test max attempts
    for i in range(3):
        assert not await auth_system.verify_sms_code(user_id, f"wrong_{i}")
    assert f"sms:{user_id}" not in auth_system.pending_mfa # Should be deleted after 3 failures

    # Test expiry
    await auth_system.setup_sms_mfa(user_id, "1234567890")
    auth_system.pending_mfa[f"sms:{user_id}"]["created"] = datetime.now(timezone.utc) - timedelta(minutes=10)
    assert not await auth_system.verify_sms_code(user_id, "any_code")
    assert f"sms:{user_id}" not in auth_system.pending_mfa

@pytest.mark.asyncio
async def test_backup_code_verification(auth_system):
    """Test backup code verification."""
    user_id = "backup_user"
    with patch('labs.core.security.auth.pyotp.TOTP'):
        setup_info = await auth_system.setup_totp(user_id)
        backup_codes = setup_info["backup_codes"]

    assert await auth_system.verify_backup_code(user_id, backup_codes[0])
    assert not await auth_system.verify_backup_code(user_id, backup_codes[0])
    assert not await auth_system.verify_backup_code(user_id, "invalid-code")

@pytest.mark.asyncio
async def test_api_key_management(auth_system):
    """Test API key generation, verification, and revocation."""
    user_id = "api_user"
    scopes = ["read", "write"]
    key_id, key_secret = auth_system.generate_api_key(user_id, scopes)

    result = await auth_system.verify_api_key(key_id, key_secret)
    assert result["user_id"] == user_id

    # Test invalid secret
    assert await auth_system.verify_api_key(key_id, "wrong_secret") is None

    await auth_system.revoke_api_key(key_id)
    assert await auth_system.verify_api_key(key_id, key_secret) is None

@pytest.mark.asyncio
async def test_api_key_management_with_redis(auth_system_with_redis):
    """Test API key management using the redis path."""
    user_id = "api_user_redis"
    key_id, key_secret = auth_system_with_redis.generate_api_key(user_id, ["read"])

    key_data = json.loads(mock_redis_client.hset.call_args[0][2])
    revoked_key_data = key_data.copy()
    revoked_key_data['active'] = False

    # Configure hget to return the active key first, then the revoked one, then None
    mock_redis_client.hget.side_effect = [
        json.dumps(key_data),
        json.dumps(revoked_key_data),
        None
    ]

    assert await auth_system_with_redis.verify_api_key(key_id, key_secret) is not None
    await auth_system_with_redis.revoke_api_key(key_id)
    assert await auth_system_with_redis.verify_api_key(key_id, key_secret) is None


@pytest.mark.asyncio
async def test_rate_limiting(auth_system):
    """Test rate limiting logic."""
    identifier = "rate_limited_user"
    for _ in range(auth_system.max_login_attempts):
        await auth_system.record_failed_attempt(identifier)

    assert not await auth_system.check_rate_limit(identifier)

    await auth_system.clear_failed_attempts(identifier)
    assert await auth_system.check_rate_limit(identifier)
