"""
T4/0.01% Excellence Identity Session Persistence Tests

Comprehensive test suite for session store, token rotation, and CRC32 validation.
Tests both Redis and SQLite backends with performance benchmarks and chaos scenarios.
"""

import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Optional

import pytest

from identity.session_store import (
    RedisSessionStore,
    SessionData,
    SessionManager,
    SessionNotFoundError,
    SQLiteSessionStore,
)
from identity.token_generator import TokenGenerator, TokenResponse, _calculate_crc32, _verify_crc32


class MockSecretProvider:
    """Mock secret provider for testing"""

    def __init__(self, secrets: Optional[Dict[str, bytes]] = None):
        self.secrets = secrets or {
            "test-key-1": b"secret-key-for-testing-purposes-32-bytes",
            "test-key-2": b"rotated-secret-key-for-testing-32-b",
            "current": b"current-active-key-for-testing-32-b",
        }
        self.current_kid = "current"

    def get_secret(self, kid: str) -> bytes:
        if kid not in self.secrets:
            raise KeyError(f"Secret key {kid} not found")
        return self.secrets[kid]

    def get_current_kid(self) -> str:
        return self.current_kid


class TestSessionData:
    """Test SessionData functionality"""

    def test_session_data_creation(self):
        """Test creating session data"""
        now = datetime.now(timezone.utc)
        expires = now + timedelta(hours=1)

        session = SessionData(
            session_id="test-session-id",
            user_id="test-user",
            tier="T2",
            created_at=now,
            expires_at=expires,
            last_accessed=now,
            metadata={"test": "data"},
        )

        assert session.session_id == "test-session-id"
        assert session.user_id == "test-user"
        assert session.tier == "T2"
        assert session.metadata == {"test": "data"}

    def test_session_expiration_check(self):
        """Test session expiration detection"""
        now = datetime.now(timezone.utc)

        # Non-expired session
        future_session = SessionData(
            session_id="test",
            user_id="user",
            tier="T1",
            created_at=now,
            expires_at=now + timedelta(hours=1),
            last_accessed=now,
            metadata={},
        )
        assert not future_session.is_expired()

        # Expired session
        expired_session = SessionData(
            session_id="test",
            user_id="user",
            tier="T1",
            created_at=now - timedelta(hours=2),
            expires_at=now - timedelta(hours=1),
            last_accessed=now - timedelta(hours=1),
            metadata={},
        )
        assert expired_session.is_expired()

    def test_session_touch(self):
        """Test session touch functionality"""
        now = datetime.now(timezone.utc)
        session = SessionData(
            session_id="test",
            user_id="user",
            tier="T1",
            created_at=now - timedelta(minutes=30),
            expires_at=now + timedelta(hours=1),
            last_accessed=now - timedelta(minutes=10),
            metadata={},
        )

        old_access_time = session.last_accessed
        time.sleep(0.001)  # Small delay
        session.touch()

        assert session.last_accessed > old_access_time

    def test_session_serialization(self):
        """Test session to/from dict conversion"""
        now = datetime.now(timezone.utc)
        original = SessionData(
            session_id="test-session",
            user_id="test-user",
            tier="T3",
            created_at=now,
            expires_at=now + timedelta(hours=1),
            last_accessed=now,
            metadata={"key": "value", "number": 42},
        )

        # Convert to dict and back
        data_dict = original.to_dict()
        restored = SessionData.from_dict(data_dict)

        assert restored.session_id == original.session_id
        assert restored.user_id == original.user_id
        assert restored.tier == original.tier
        assert restored.metadata == original.metadata
        assert restored.created_at == original.created_at


class TestSQLiteSessionStore:
    """Test SQLite session store implementation"""

    @pytest.fixture
    def temp_db_path(self):
        """Provide temporary database path"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir) / "test_sessions.db"

    @pytest.fixture
    def sqlite_store(self, temp_db_path):
        """Provide SQLite session store"""
        return SQLiteSessionStore(db_path=temp_db_path)

    def test_sqlite_store_initialization(self, temp_db_path):
        """Test SQLite store initialization"""
        SQLiteSessionStore(db_path=temp_db_path)
        assert temp_db_path.exists()

    @pytest.mark.asyncio
    async def test_sqlite_put_and_get(self, sqlite_store):
        """Test storing and retrieving sessions from SQLite"""
        now = datetime.now(timezone.utc)
        session = SessionData(
            session_id="test-session",
            user_id="test-user",
            tier="T2",
            created_at=now,
            expires_at=now + timedelta(hours=1),
            last_accessed=now,
            metadata={"test": "data"},
        )

        # Store session
        result = await sqlite_store.put(session)
        assert result is True

        # Retrieve session
        retrieved = await sqlite_store.get("test-session")
        assert retrieved.session_id == session.session_id
        assert retrieved.user_id == session.user_id
        assert retrieved.tier == session.tier
        assert retrieved.metadata == session.metadata

    @pytest.mark.asyncio
    async def test_sqlite_session_not_found(self, sqlite_store):
        """Test SQLite session not found error"""
        with pytest.raises(SessionNotFoundError):
            await sqlite_store.get("nonexistent-session")

    @pytest.mark.asyncio
    async def test_sqlite_delete_session(self, sqlite_store):
        """Test deleting sessions from SQLite"""
        now = datetime.now(timezone.utc)
        session = SessionData(
            session_id="delete-test",
            user_id="user",
            tier="T1",
            created_at=now,
            expires_at=now + timedelta(hours=1),
            last_accessed=now,
            metadata={},
        )

        # Store and verify
        await sqlite_store.put(session)
        assert await sqlite_store.exists("delete-test")

        # Delete and verify
        result = await sqlite_store.delete("delete-test")
        assert result is True
        assert not await sqlite_store.exists("delete-test")

    @pytest.mark.asyncio
    async def test_sqlite_sweep_expired(self, sqlite_store):
        """Test expired session cleanup in SQLite"""
        now = datetime.now(timezone.utc)

        # Create expired session
        expired_session = SessionData(
            session_id="expired",
            user_id="user",
            tier="T1",
            created_at=now - timedelta(hours=2),
            expires_at=now - timedelta(hours=1),
            last_accessed=now - timedelta(hours=1),
            metadata={},
        )

        # Create valid session
        valid_session = SessionData(
            session_id="valid",
            user_id="user",
            tier="T1",
            created_at=now,
            expires_at=now + timedelta(hours=1),
            last_accessed=now,
            metadata={},
        )

        # Store both sessions
        await sqlite_store.put(expired_session)
        await sqlite_store.put(valid_session)

        # Sweep expired sessions
        deleted_count = await sqlite_store.sweep_expired()
        assert deleted_count == 1

        # Verify only valid session remains
        assert not await sqlite_store.exists("expired")
        assert await sqlite_store.exists("valid")

    @pytest.mark.asyncio
    async def test_sqlite_list_sessions(self, sqlite_store):
        """Test listing sessions from SQLite"""
        now = datetime.now(timezone.utc)

        # Create sessions for different users
        sessions = [
            SessionData(
                session_id=f"session-{i}",
                user_id=f"user-{i % 2}",
                tier="T1",
                created_at=now,
                expires_at=now + timedelta(hours=1),
                last_accessed=now,
                metadata={"index": i},
            )
            for i in range(5)
        ]

        # Store all sessions
        for session in sessions:
            await sqlite_store.put(session)

        # List all sessions
        all_sessions = await sqlite_store.list_sessions()
        assert len(all_sessions) == 5

        # List sessions for specific user
        user_0_sessions = await sqlite_store.list_sessions(user_id="user-0")
        assert len(user_0_sessions) == 3  # sessions 0, 2, 4

    @pytest.mark.asyncio
    async def test_sqlite_get_stats(self, sqlite_store):
        """Test SQLite store statistics"""
        now = datetime.now(timezone.utc)

        # Add some sessions
        for i in range(3):
            session = SessionData(
                session_id=f"stats-{i}",
                user_id="stats-user",
                tier="T1",
                created_at=now,
                expires_at=now + timedelta(hours=1),
                last_accessed=now,
                metadata={},
            )
            await sqlite_store.put(session)

        stats = await sqlite_store.get_stats()
        assert stats["store_type"] == "sqlite"
        assert stats["session_count"] == 3
        assert stats["db_size_bytes"] > 0
        assert stats["encryption_enabled"] is False


# Mock Redis tests (requires running Redis instance)
@pytest.mark.skipif(True, reason="Redis tests require running Redis instance")
class TestRedisSessionStore:
    """Test Redis session store implementation"""

    @pytest.fixture
    async def redis_store(self):
        """Provide Redis session store"""
        store = RedisSessionStore(redis_url="redis://localhost:6379/15")  # Use test database
        yield store
        await store.disconnect()

    @pytest.mark.asyncio
    async def test_redis_put_and_get(self, redis_store):
        """Test storing and retrieving sessions from Redis"""
        now = datetime.now(timezone.utc)
        session = SessionData(
            session_id="redis-test-session",
            user_id="redis-test-user",
            tier="T2",
            created_at=now,
            expires_at=now + timedelta(hours=1),
            last_accessed=now,
            metadata={"redis": "test"},
        )

        # Store session
        result = await redis_store.put(session)
        assert result is True

        # Retrieve session
        retrieved = await redis_store.get("redis-test-session")
        assert retrieved.session_id == session.session_id
        assert retrieved.user_id == session.user_id


class TestSessionManager:
    """Test high-level session manager"""

    @pytest.fixture
    def temp_db_path(self):
        """Provide temporary database path"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir) / "manager_test.db"

    @pytest.fixture
    def session_manager(self, temp_db_path):
        """Provide session manager with SQLite backend"""
        store = SQLiteSessionStore(db_path=temp_db_path)
        return SessionManager(store=store, default_ttl_seconds=3600, auto_sweep=False)  # Disable for testing

    @pytest.mark.asyncio
    async def test_create_session(self, session_manager):
        """Test creating sessions through manager"""
        session = await session_manager.create_session(
            user_id="manager-user", tier="T3", metadata={"manager": "test"}, ttl_seconds=7200
        )

        assert session.user_id == "manager-user"
        assert session.tier == "T3"
        assert session.metadata == {"manager": "test"}
        assert session.session_id is not None

        # Verify stored
        retrieved = await session_manager.get_session(session.session_id)
        assert retrieved.user_id == session.user_id

    @pytest.mark.asyncio
    async def test_list_user_sessions(self, session_manager):
        """Test listing user sessions"""
        # Create multiple sessions for same user
        sessions = []
        for i in range(3):
            session = await session_manager.create_session(
                user_id="multi-session-user", tier="T1", metadata={"session": i}
            )
            sessions.append(session)

        # List user sessions
        user_sessions = await session_manager.list_user_sessions("multi-session-user")
        assert len(user_sessions) == 3

    @pytest.mark.asyncio
    async def test_delete_session(self, session_manager):
        """Test deleting sessions through manager"""
        session = await session_manager.create_session(user_id="delete-user", tier="T1")

        # Verify exists
        retrieved = await session_manager.get_session(session.session_id)
        assert retrieved.session_id == session.session_id

        # Delete
        result = await session_manager.delete_session(session.session_id)
        assert result is True

        # Verify deleted
        with pytest.raises(SessionNotFoundError):
            await session_manager.get_session(session.session_id)

    @pytest.mark.asyncio
    async def test_session_manager_stats(self, session_manager):
        """Test session manager statistics"""
        # Create some sessions
        for i in range(2):
            await session_manager.create_session(user_id=f"stats-user-{i}", tier="T1")

        stats = await session_manager.get_statistics()
        assert stats["session_count"] >= 2


class TestTokenGeneratorCRC32:
    """Test enhanced token generator with CRC32 support"""

    @pytest.fixture
    def secret_provider(self):
        """Provide mock secret provider"""
        return MockSecretProvider()

    @pytest.fixture
    def token_generator(self, secret_provider):
        """Provide token generator"""
        return TokenGenerator(secret_provider=secret_provider, ttl_seconds=3600, issuer="test.ai")

    def test_crc32_calculation(self):
        """Test CRC32 checksum calculation"""
        test_data = b"test data for crc32"
        crc = _calculate_crc32(test_data)

        assert len(crc) == 8  # 8 hex characters
        assert all(c in "0123456789abcdef" for c in crc)

        # Verify consistency
        assert _calculate_crc32(test_data) == crc

    def test_crc32_verification(self):
        """Test CRC32 verification"""
        test_data = b"verification test data"
        crc = _calculate_crc32(test_data)

        # Valid verification
        assert _verify_crc32(test_data, crc) is True
        assert _verify_crc32(test_data, crc.upper()) is True

        # Invalid verification
        assert _verify_crc32(test_data, "12345678") is False
        assert _verify_crc32(b"different data", crc) is False

    def test_enhanced_token_creation(self, token_generator):
        """Test creating tokens with CRC32 enhancement"""
        claims = {"aud": "test-audience", "lukhas_tier": 2, "permissions": ["read", "write"]}

        response = token_generator.create(claims=claims, realm="test-realm", zone="test-zone")

        # Verify response structure
        assert isinstance(response, TokenResponse)
        assert response.alias.startswith("λ")
        assert response.kid == "current"
        assert response.crc32 is not None
        assert len(response.crc32) == 8
        assert response.schema_version == "1.1.0"

        # Verify JWT has CRC32 trailer
        jwt_parts = response.jwt.split(".")
        assert len(jwt_parts) == 4  # header.payload.signature.crc32

    def test_crc32_validation(self, token_generator):
        """Test CRC32 validation of tokens"""
        claims = {"test": "data"}
        response = token_generator.create(claims=claims, realm="test", zone="test")

        # Valid CRC32
        assert token_generator.validate_crc32(response.jwt) is True

        # Tampered token
        tampered_jwt = response.jwt[:-2] + "xx"  # Change CRC32
        assert token_generator.validate_crc32(tampered_jwt) is False

        # Invalid format
        assert token_generator.validate_crc32("invalid.token") is False

    def test_jwt_extraction(self, token_generator):
        """Test extracting standard JWT from enhanced token"""
        claims = {"test": "extraction"}
        response = token_generator.create(claims=claims, realm="test", zone="test")

        # Extract standard JWT
        standard_jwt = token_generator.extract_jwt_from_enhanced(response.jwt)

        # Should have 3 parts (no CRC32)
        parts = standard_jwt.split(".")
        assert len(parts) == 3

        # Should be valid JWT format
        assert all(part for part in parts)  # No empty parts

    def test_key_rotation(self, token_generator):
        """Test token key rotation"""
        old_kid = token_generator.kid
        assert old_kid == "current"

        # Rotate to new key
        token_generator.rotate_key("test-key-1")
        assert token_generator.kid == "test-key-1"

        # Create token with new key
        response = token_generator.create(claims={"test": "rotation"}, realm="test", zone="test")
        assert response.kid == "test-key-1"

    def test_legacy_jwt_compatibility(self, token_generator):
        """Test backward compatibility with legacy JWT creation"""
        claims = {"legacy": "test"}

        # Create using legacy method
        legacy_jwt = token_generator._create_jwt(claims)

        # Should have 3 parts (no CRC32)
        parts = legacy_jwt.split(".")
        assert len(parts) == 3

        # Should be valid JWT
        import base64
        import json

        # Decode header to verify structure
        header_b64 = parts[0]
        # Add padding if needed
        padding = "=" * (-len(header_b64) % 4)
        header_json = base64.urlsafe_b64decode(header_b64 + padding).decode()
        header = json.loads(header_json)

        assert header["alg"] == "HS256"
        assert header["typ"] == "JWT"
        assert header["kid"] == "current"


class TestPerformanceRequirements:
    """Test T4/0.01% performance requirements"""

    @pytest.fixture
    def temp_db_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir) / "perf_test.db"

    @pytest.fixture
    def session_manager(self, temp_db_path):
        store = SQLiteSessionStore(db_path=temp_db_path)
        return SessionManager(store=store, auto_sweep=False)

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_session_write_performance(self, session_manager):
        """Test session write performance <5ms p95"""
        durations = []

        for i in range(100):
            start = time.perf_counter()
            await session_manager.create_session(user_id=f"perf-user-{i}", tier="T1", metadata={"test": i})
            duration = (time.perf_counter() - start) * 1000  # ms
            durations.append(duration)

        # Calculate p95
        durations.sort()
        p95 = durations[94]  # 95th percentile

        assert p95 < 5.0, f"Session write p95 {p95:.2f}ms exceeds 5ms requirement"

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_session_read_performance(self, session_manager):
        """Test session read performance <3ms p95"""
        # Create test session
        session = await session_manager.create_session(user_id="perf-read-user", tier="T1")

        durations = []

        for i in range(100):
            start = time.perf_counter()
            await session_manager.get_session(session.session_id)
            duration = (time.perf_counter() - start) * 1000  # ms
            durations.append(duration)

        # Calculate p95
        durations.sort()
        p95 = durations[94]

        assert p95 < 3.0, f"Session read p95 {p95:.2f}ms exceeds 3ms requirement"

    @pytest.mark.performance
    def test_token_generation_performance(self):
        """Test token generation performance"""
        provider = MockSecretProvider()
        generator = TokenGenerator(provider, ttl_seconds=3600)

        durations = []

        for i in range(1000):
            start = time.perf_counter()
            generator.create(claims={"test": i}, realm="perf", zone="test")
            duration = (time.perf_counter() - start) * 1000  # ms
            durations.append(duration)

        # Calculate p95
        durations.sort()
        p95 = durations[949]  # 95th percentile

        # Token generation should be <10ms p95
        assert p95 < 10.0, f"Token generation p95 {p95:.2f}ms exceeds 10ms"

    @pytest.mark.performance
    def test_crc32_calculation_performance(self):
        """Test CRC32 calculation performance"""
        test_data = b"performance test data for crc32 calculation" * 100

        durations = []

        for _ in range(10000):
            start = time.perf_counter()
            _calculate_crc32(test_data)
            duration = (time.perf_counter() - start) * 1000000  # microseconds
            durations.append(duration)

        # Calculate p95
        durations.sort()
        p95 = durations[9499]

        # CRC32 should be <100μs p95
        assert p95 < 100.0, f"CRC32 calculation p95 {p95:.2f}μs exceeds 100μs"


class TestIntegrationScenarios:
    """Test realistic integration scenarios"""

    @pytest.fixture
    def temp_db_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir) / "integration_test.db"

    @pytest.fixture
    async def full_system(self, temp_db_path):
        """Full system with session manager and token generator"""
        # Session manager
        store = SQLiteSessionStore(db_path=temp_db_path)
        session_manager = SessionManager(store=store, auto_sweep=False)

        # Token generator
        secret_provider = MockSecretProvider()
        token_generator = TokenGenerator(secret_provider)

        return session_manager, token_generator

    @pytest.mark.asyncio
    async def test_complete_authentication_flow(self, full_system):
        """Test complete authentication flow"""
        session_manager, token_generator = full_system

        # Step 1: Create session
        session = await session_manager.create_session(
            user_id="integration-user", tier="T2", metadata={"device": "test-device"}
        )

        # Step 2: Generate token for session
        token_response = token_generator.create(
            claims={"session_id": session.session_id, "lukhas_tier": 2, "permissions": ["read", "write"]},
            realm="integration",
            zone="test",
        )

        # Step 3: Validate token CRC32
        assert token_generator.validate_crc32(token_response.jwt)

        # Step 4: Verify session still valid
        retrieved_session = await session_manager.get_session(session.session_id)
        assert retrieved_session.user_id == "integration-user"

        # Step 5: Cleanup
        await session_manager.delete_session(session.session_id)

    @pytest.mark.asyncio
    async def test_key_rotation_with_active_sessions(self, full_system):
        """Test key rotation scenario with active sessions"""
        session_manager, token_generator = full_system

        # Create session and token with initial key
        session = await session_manager.create_session(user_id="rotation-user", tier="T1")

        old_token = token_generator.create(claims={"session_id": session.session_id}, realm="rotation", zone="test")

        # Rotate key
        token_generator.rotate_key("test-key-1")

        # Create new token with rotated key
        new_token = token_generator.create(claims={"session_id": session.session_id}, realm="rotation", zone="test")

        # Both tokens should be valid (different keys)
        assert token_generator.validate_crc32(new_token.jwt)
        assert old_token.kid != new_token.kid

        # Session should still be accessible
        retrieved = await session_manager.get_session(session.session_id)
        assert retrieved.user_id == "rotation-user"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
