"""
T4/0.01% Excellence Identity Session Store

Production-ready session persistence with Redis/SQLite adapters, TTL management,
crash recovery, and comprehensive audit logging for LUKHAS λID system.

Performance targets:
- Session write: <5ms p95
- Session read: <3ms p95
- TTL sweep: <100ms for 10k sessions
- Crash recovery: <1s for full session restore
"""

import asyncio
import json
import sqlite3
import time
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Union
from uuid import uuid4

import aioredis
from cryptography.fernet import Fernet

from core.logging import get_logger
from observability.metrics import get_metrics_collector

logger = get_logger(__name__)
metrics = get_metrics_collector()


@dataclass
class SessionData:
    """T4 session data structure with comprehensive metadata"""
    session_id: str
    user_id: str
    tier: str  # T1-T5
    created_at: datetime
    expires_at: datetime
    last_accessed: datetime
    metadata: Dict[str, any]
    encrypted_data: Optional[bytes] = None

    def to_dict(self) -> Dict[str, any]:
        """Convert to dictionary for storage"""
        data = asdict(self)
        # Convert datetimes to ISO strings for JSON serialization
        for key in ['created_at', 'expires_at', 'last_accessed']:
            if isinstance(data[key], datetime):
                data[key] = data[key].isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, any]) -> 'SessionData':
        """Create from dictionary"""
        # Convert ISO strings back to datetimes
        for key in ['created_at', 'expires_at', 'last_accessed']:
            if isinstance(data[key], str):
                data[key] = datetime.fromisoformat(data[key])
        return cls(**data)

    def is_expired(self) -> bool:
        """Check if session has expired"""
        return datetime.now(timezone.utc) > self.expires_at

    def touch(self) -> None:
        """Update last accessed timestamp"""
        self.last_accessed = datetime.now(timezone.utc)


class SessionStoreError(Exception):
    """Base exception for session store operations"""
    pass


class SessionNotFoundError(SessionStoreError):
    """Session not found in store"""
    pass


class SessionExpiredError(SessionStoreError):
    """Session has expired"""
    pass


class AbstractSessionStore(ABC):
    """Abstract base class for session storage backends"""

    @abstractmethod
    async def put(self, session: SessionData) -> bool:
        """Store session data"""
        pass

    @abstractmethod
    async def get(self, session_id: str) -> SessionData:
        """Retrieve session data"""
        pass

    @abstractmethod
    async def delete(self, session_id: str) -> bool:
        """Delete session"""
        pass

    @abstractmethod
    async def exists(self, session_id: str) -> bool:
        """Check if session exists"""
        pass

    @abstractmethod
    async def sweep_expired(self) -> int:
        """Remove expired sessions, return count deleted"""
        pass

    @abstractmethod
    async def list_sessions(self, user_id: Optional[str] = None) -> List[SessionData]:
        """List sessions, optionally filtered by user"""
        pass

    @abstractmethod
    async def get_stats(self) -> Dict[str, any]:
        """Get storage statistics"""
        pass


class RedisSessionStore(AbstractSessionStore):
    """Redis-based session store with high performance and clustering support"""

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379/0",
        key_prefix: str = "lukhas:session:",
        encryption_key: Optional[bytes] = None,
        ttl_buffer_seconds: int = 300  # 5 minutes buffer for TTL cleanup
    ):
        self.redis_url = redis_url
        self.key_prefix = key_prefix
        self.ttl_buffer = ttl_buffer_seconds
        self.redis: Optional[aioredis.Redis] = None

        # Initialize encryption if key provided
        self.fernet = Fernet(encryption_key) if encryption_key else None

    async def connect(self) -> None:
        """Establish Redis connection"""
        if not self.redis:
            self.redis = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                retry_on_timeout=True,
                health_check_interval=30
            )

    async def disconnect(self) -> None:
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()
            self.redis = None

    def _make_key(self, session_id: str) -> str:
        """Generate Redis key for session"""
        return f"{self.key_prefix}{session_id}"

    def _encrypt_data(self, data: bytes) -> bytes:
        """Encrypt session data if encryption enabled"""
        return self.fernet.encrypt(data) if self.fernet else data

    def _decrypt_data(self, data: bytes) -> bytes:
        """Decrypt session data if encryption enabled"""
        return self.fernet.decrypt(data) if self.fernet else data

    async def put(self, session: SessionData) -> bool:
        """Store session in Redis with TTL"""
        start_time = time.perf_counter()

        try:
            await self.connect()

            # Calculate TTL in seconds
            ttl_seconds = int((session.expires_at - datetime.now(timezone.utc)).total_seconds())
            if ttl_seconds <= 0:
                raise SessionExpiredError(f"Session {session.session_id} already expired")

            # Serialize session data
            data_json = json.dumps(session.to_dict())
            data_bytes = data_json.encode('utf-8')

            # Encrypt if enabled
            if self.fernet:
                data_bytes = self._encrypt_data(data_bytes)
                session.encrypted_data = data_bytes

            # Store in Redis with TTL
            key = self._make_key(session.session_id)
            result = await self.redis.setex(key, ttl_seconds, data_json)

            # Record metrics
            duration = time.perf_counter() - start_time
            metrics.record_histogram("session_store_put_duration_ms", duration * 1000)
            metrics.increment_counter("session_store_put_total")

            # Audit log
            logger.info(
                "Session stored",
                session_id=session.session_id,
                user_id=session.user_id,
                tier=session.tier,
                ttl_seconds=ttl_seconds,
                duration_ms=duration * 1000
            )

            return bool(result)

        except Exception as e:
            metrics.increment_counter("session_store_put_errors")
            logger.error(
                "Failed to store session",
                session_id=session.session_id,
                error=str(e),
                duration_ms=(time.perf_counter() - start_time) * 1000
            )
            raise SessionStoreError(f"Failed to store session: {e}") from e

    async def get(self, session_id: str) -> SessionData:
        """Retrieve session from Redis"""
        start_time = time.perf_counter()

        try:
            await self.connect()

            key = self._make_key(session_id)
            data_json = await self.redis.get(key)

            if not data_json:
                raise SessionNotFoundError(f"Session {session_id} not found")

            # Decrypt if enabled
            if self.fernet and isinstance(data_json, bytes):
                data_json = self._decrypt_data(data_json).decode('utf-8')

            # Parse session data
            data_dict = json.loads(data_json)
            session = SessionData.from_dict(data_dict)

            # Check expiration
            if session.is_expired():
                await self.delete(session_id)  # Cleanup expired session
                raise SessionExpiredError(f"Session {session_id} has expired")

            # Touch session (update last accessed)
            session.touch()
            await self.put(session)  # Update with new timestamp

            # Record metrics
            duration = time.perf_counter() - start_time
            metrics.record_histogram("session_store_get_duration_ms", duration * 1000)
            metrics.increment_counter("session_store_get_total")

            return session

        except (SessionNotFoundError, SessionExpiredError):
            raise
        except Exception as e:
            metrics.increment_counter("session_store_get_errors")
            logger.error(
                "Failed to retrieve session",
                session_id=session_id,
                error=str(e),
                duration_ms=(time.perf_counter() - start_time) * 1000
            )
            raise SessionStoreError(f"Failed to retrieve session: {e}") from e

    async def delete(self, session_id: str) -> bool:
        """Delete session from Redis"""
        start_time = time.perf_counter()

        try:
            await self.connect()

            key = self._make_key(session_id)
            result = await self.redis.delete(key)

            # Record metrics
            duration = time.perf_counter() - start_time
            metrics.record_histogram("session_store_delete_duration_ms", duration * 1000)
            metrics.increment_counter("session_store_delete_total")

            # Audit log
            logger.info(
                "Session deleted",
                session_id=session_id,
                duration_ms=duration * 1000
            )

            return bool(result)

        except Exception as e:
            metrics.increment_counter("session_store_delete_errors")
            logger.error(
                "Failed to delete session",
                session_id=session_id,
                error=str(e),
                duration_ms=(time.perf_counter() - start_time) * 1000
            )
            raise SessionStoreError(f"Failed to delete session: {e}") from e

    async def exists(self, session_id: str) -> bool:
        """Check if session exists in Redis"""
        try:
            await self.connect()
            key = self._make_key(session_id)
            return bool(await self.redis.exists(key))
        except Exception as e:
            logger.error("Failed to check session existence", session_id=session_id, error=str(e))
            return False

    async def sweep_expired(self) -> int:
        """Redis handles TTL automatically, but we can clean up any missed entries"""
        start_time = time.perf_counter()
        deleted_count = 0

        try:
            await self.connect()

            # Scan for session keys
            pattern = f"{self.key_prefix}*"
            async for key in self.redis.scan_iter(match=pattern, count=100):
                try:
                    data_json = await self.redis.get(key)
                    if data_json:
                        data_dict = json.loads(data_json)
                        session = SessionData.from_dict(data_dict)

                        if session.is_expired():
                            await self.redis.delete(key)
                            deleted_count += 1
                except Exception:
                    # Skip malformed entries
                    continue

            # Record metrics
            duration = time.perf_counter() - start_time
            metrics.record_histogram("session_store_sweep_duration_ms", duration * 1000)
            metrics.increment_counter("session_store_sweep_total")
            metrics.record_gauge("session_store_swept_count", deleted_count)

            logger.info(
                "Session sweep completed",
                deleted_count=deleted_count,
                duration_ms=duration * 1000
            )

            return deleted_count

        except Exception as e:
            logger.error("Failed to sweep expired sessions", error=str(e))
            return 0

    async def list_sessions(self, user_id: Optional[str] = None) -> List[SessionData]:
        """List sessions from Redis"""
        sessions = []

        try:
            await self.connect()

            pattern = f"{self.key_prefix}*"
            async for key in self.redis.scan_iter(match=pattern, count=100):
                try:
                    data_json = await self.redis.get(key)
                    if data_json:
                        data_dict = json.loads(data_json)
                        session = SessionData.from_dict(data_dict)

                        # Filter by user_id if specified
                        if user_id is None or session.user_id == user_id:
                            sessions.append(session)
                except Exception:
                    # Skip malformed entries
                    continue

            return sessions

        except Exception as e:
            logger.error("Failed to list sessions", error=str(e))
            return []

    async def get_stats(self) -> Dict[str, any]:
        """Get Redis session store statistics"""
        try:
            await self.connect()

            # Count sessions
            pattern = f"{self.key_prefix}*"
            session_count = 0
            async for _ in self.redis.scan_iter(match=pattern, count=100):
                session_count += 1

            # Redis info
            info = await self.redis.info()
            memory_usage = info.get('used_memory', 0)

            return {
                "store_type": "redis",
                "session_count": session_count,
                "memory_usage_bytes": memory_usage,
                "redis_version": info.get('redis_version', 'unknown'),
                "connected_clients": info.get('connected_clients', 0),
                "total_commands_processed": info.get('total_commands_processed', 0),
                "encryption_enabled": self.fernet is not None
            }

        except Exception as e:
            logger.error("Failed to get Redis stats", error=str(e))
            return {"store_type": "redis", "error": str(e)}


class SQLiteSessionStore(AbstractSessionStore):
    """SQLite-based session store for development and single-instance deployments"""

    def __init__(
        self,
        db_path: Union[str, Path] = "lukhas_sessions.db",
        encryption_key: Optional[bytes] = None
    ):
        self.db_path = Path(db_path)
        self.fernet = Fernet(encryption_key) if encryption_key else None
        self._init_db()

    def _init_db(self) -> None:
        """Initialize SQLite database and tables"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    tier TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    last_accessed TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    encrypted_data BLOB,
                    INDEX(user_id),
                    INDEX(expires_at)
                )
            """)
            conn.commit()

    def _encrypt_data(self, data: bytes) -> bytes:
        """Encrypt session data if encryption enabled"""
        return self.fernet.encrypt(data) if self.fernet else data

    def _decrypt_data(self, data: bytes) -> bytes:
        """Decrypt session data if encryption enabled"""
        return self.fernet.decrypt(data) if self.fernet else data

    async def put(self, session: SessionData) -> bool:
        """Store session in SQLite"""
        start_time = time.perf_counter()

        try:
            # Encrypt metadata if encryption enabled
            metadata_json = json.dumps(session.metadata)
            encrypted_data = None

            if self.fernet:
                encrypted_data = self._encrypt_data(metadata_json.encode('utf-8'))

            with sqlite3.connect(str(self.db_path)) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO sessions
                    (session_id, user_id, tier, created_at, expires_at, last_accessed, metadata, encrypted_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session.session_id,
                    session.user_id,
                    session.tier,
                    session.created_at.isoformat(),
                    session.expires_at.isoformat(),
                    session.last_accessed.isoformat(),
                    metadata_json,
                    encrypted_data
                ))
                conn.commit()

            # Record metrics
            duration = time.perf_counter() - start_time
            metrics.record_histogram("session_store_put_duration_ms", duration * 1000)
            metrics.increment_counter("session_store_put_total")

            return True

        except Exception as e:
            metrics.increment_counter("session_store_put_errors")
            logger.error(
                "Failed to store session in SQLite",
                session_id=session.session_id,
                error=str(e),
                duration_ms=(time.perf_counter() - start_time) * 1000
            )
            raise SessionStoreError(f"Failed to store session: {e}") from e

    async def get(self, session_id: str) -> SessionData:
        """Retrieve session from SQLite"""
        start_time = time.perf_counter()

        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    "SELECT * FROM sessions WHERE session_id = ?",
                    (session_id,)
                )
                row = cursor.fetchone()

                if not row:
                    raise SessionNotFoundError(f"Session {session_id} not found")

                # Decrypt metadata if encrypted
                metadata_json = row['metadata']
                if row['encrypted_data'] and self.fernet:
                    metadata_json = self._decrypt_data(row['encrypted_data']).decode('utf-8')

                session = SessionData(
                    session_id=row['session_id'],
                    user_id=row['user_id'],
                    tier=row['tier'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    expires_at=datetime.fromisoformat(row['expires_at']),
                    last_accessed=datetime.fromisoformat(row['last_accessed']),
                    metadata=json.loads(metadata_json),
                    encrypted_data=row['encrypted_data']
                )

                # Check expiration
                if session.is_expired():
                    await self.delete(session_id)
                    raise SessionExpiredError(f"Session {session_id} has expired")

                # Touch session
                session.touch()
                await self.put(session)

                # Record metrics
                duration = time.perf_counter() - start_time
                metrics.record_histogram("session_store_get_duration_ms", duration * 1000)
                metrics.increment_counter("session_store_get_total")

                return session

        except (SessionNotFoundError, SessionExpiredError):
            raise
        except Exception as e:
            metrics.increment_counter("session_store_get_errors")
            logger.error(
                "Failed to retrieve session from SQLite",
                session_id=session_id,
                error=str(e),
                duration_ms=(time.perf_counter() - start_time) * 1000
            )
            raise SessionStoreError(f"Failed to retrieve session: {e}") from e

    async def delete(self, session_id: str) -> bool:
        """Delete session from SQLite"""
        start_time = time.perf_counter()

        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.execute(
                    "DELETE FROM sessions WHERE session_id = ?",
                    (session_id,)
                )
                conn.commit()

                deleted = cursor.rowcount > 0

                # Record metrics
                duration = time.perf_counter() - start_time
                metrics.record_histogram("session_store_delete_duration_ms", duration * 1000)
                metrics.increment_counter("session_store_delete_total")

                return deleted

        except Exception as e:
            metrics.increment_counter("session_store_delete_errors")
            logger.error(
                "Failed to delete session from SQLite",
                session_id=session_id,
                error=str(e),
                duration_ms=(time.perf_counter() - start_time) * 1000
            )
            raise SessionStoreError(f"Failed to delete session: {e}") from e

    async def exists(self, session_id: str) -> bool:
        """Check if session exists in SQLite"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.execute(
                    "SELECT 1 FROM sessions WHERE session_id = ? LIMIT 1",
                    (session_id,)
                )
                return cursor.fetchone() is not None
        except Exception as e:
            logger.error("Failed to check session existence in SQLite", session_id=session_id, error=str(e))
            return False

    async def sweep_expired(self) -> int:
        """Remove expired sessions from SQLite"""
        start_time = time.perf_counter()

        try:
            now_iso = datetime.now(timezone.utc).isoformat()

            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.execute(
                    "DELETE FROM sessions WHERE expires_at < ?",
                    (now_iso,)
                )
                conn.commit()

                deleted_count = cursor.rowcount

                # Record metrics
                duration = time.perf_counter() - start_time
                metrics.record_histogram("session_store_sweep_duration_ms", duration * 1000)
                metrics.increment_counter("session_store_sweep_total")
                metrics.record_gauge("session_store_swept_count", deleted_count)

                logger.info(
                    "SQLite session sweep completed",
                    deleted_count=deleted_count,
                    duration_ms=duration * 1000
                )

                return deleted_count

        except Exception as e:
            logger.error("Failed to sweep expired sessions from SQLite", error=str(e))
            return 0

    async def list_sessions(self, user_id: Optional[str] = None) -> List[SessionData]:
        """List sessions from SQLite"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.row_factory = sqlite3.Row

                if user_id:
                    cursor = conn.execute(
                        "SELECT * FROM sessions WHERE user_id = ? ORDER BY last_accessed DESC",
                        (user_id,)
                    )
                else:
                    cursor = conn.execute(
                        "SELECT * FROM sessions ORDER BY last_accessed DESC"
                    )

                sessions = []
                for row in cursor.fetchall():
                    # Decrypt metadata if encrypted
                    metadata_json = row['metadata']
                    if row['encrypted_data'] and self.fernet:
                        metadata_json = self._decrypt_data(row['encrypted_data']).decode('utf-8')

                    session = SessionData(
                        session_id=row['session_id'],
                        user_id=row['user_id'],
                        tier=row['tier'],
                        created_at=datetime.fromisoformat(row['created_at']),
                        expires_at=datetime.fromisoformat(row['expires_at']),
                        last_accessed=datetime.fromisoformat(row['last_accessed']),
                        metadata=json.loads(metadata_json),
                        encrypted_data=row['encrypted_data']
                    )
                    sessions.append(session)

                return sessions

        except Exception as e:
            logger.error("Failed to list sessions from SQLite", error=str(e))
            return []

    async def get_stats(self) -> Dict[str, any]:
        """Get SQLite session store statistics"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                # Count total sessions
                cursor = conn.execute("SELECT COUNT(*) FROM sessions")
                session_count = cursor.fetchone()[0]

                # Count expired sessions
                now_iso = datetime.now(timezone.utc).isoformat()
                cursor = conn.execute("SELECT COUNT(*) FROM sessions WHERE expires_at < ?", (now_iso,))
                expired_count = cursor.fetchone()[0]

                # Database file size
                db_size = self.db_path.stat().st_size if self.db_path.exists() else 0

                return {
                    "store_type": "sqlite",
                    "session_count": session_count,
                    "expired_count": expired_count,
                    "db_size_bytes": db_size,
                    "db_path": str(self.db_path),
                    "encryption_enabled": self.fernet is not None
                }

        except Exception as e:
            logger.error("Failed to get SQLite stats", error=str(e))
            return {"store_type": "sqlite", "error": str(e)}


class SessionManager:
    """High-level session manager with multiple backend support"""

    def __init__(
        self,
        store: AbstractSessionStore,
        default_ttl_seconds: int = 24 * 60 * 60,  # 24 hours
        sweep_interval_seconds: int = 60 * 60,    # 1 hour
        auto_sweep: bool = True
    ):
        self.store = store
        self.default_ttl = default_ttl_seconds
        self.sweep_interval = sweep_interval_seconds
        self.auto_sweep = auto_sweep
        self._sweep_task: Optional[asyncio.Task] = None

        if auto_sweep:
            self._start_sweep_task()

    def _start_sweep_task(self) -> None:
        """Start automatic sweep task"""
        if not self._sweep_task or self._sweep_task.done():
            self._sweep_task = asyncio.create_task(self._sweep_loop())

    async def _sweep_loop(self) -> None:
        """Automatic sweep loop"""
        while True:
            try:
                await asyncio.sleep(self.sweep_interval)
                await self.store.sweep_expired()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in sweep loop", error=str(e))

    async def create_session(
        self,
        user_id: str,
        tier: str,
        metadata: Optional[Dict[str, any]] = None,
        ttl_seconds: Optional[int] = None
    ) -> SessionData:
        """Create new session"""
        now = datetime.now(timezone.utc)
        ttl = ttl_seconds or self.default_ttl

        session = SessionData(
            session_id=str(uuid4()),
            user_id=user_id,
            tier=tier,
            created_at=now,
            expires_at=now + timedelta(seconds=ttl),
            last_accessed=now,
            metadata=metadata or {}
        )

        await self.store.put(session)
        logger.info(
            "Session created",
            session_id=session.session_id,
            user_id=user_id,
            tier=tier,
            ttl_seconds=ttl
        )

        return session

    async def get_session(self, session_id: str) -> SessionData:
        """Get session by ID"""
        return await self.store.get(session_id)

    async def delete_session(self, session_id: str) -> bool:
        """Delete session"""
        return await self.store.delete(session_id)

    async def list_user_sessions(self, user_id: str) -> List[SessionData]:
        """List sessions for specific user"""
        return await self.store.list_sessions(user_id)

    async def cleanup_expired(self) -> int:
        """Manual cleanup of expired sessions"""
        return await self.store.sweep_expired()

    async def get_statistics(self) -> Dict[str, any]:
        """Get session store statistics"""
        return await self.store.get_stats()

    async def shutdown(self) -> None:
        """Shutdown session manager"""
        if self._sweep_task:
            self._sweep_task.cancel()
            try:
                await self._sweep_task
            except asyncio.CancelledError:
                pass

        if hasattr(self.store, 'disconnect'):
            await self.store.disconnect()


# Factory functions for common configurations
def create_redis_session_manager(
    redis_url: str = "redis://localhost:6379/0",
    encryption_key: Optional[bytes] = None,
    **kwargs
) -> SessionManager:
    """Create session manager with Redis backend"""
    store = RedisSessionStore(redis_url=redis_url, encryption_key=encryption_key)
    return SessionManager(store, **kwargs)


def create_sqlite_session_manager(
    db_path: Union[str, Path] = "lukhas_sessions.db",
    encryption_key: Optional[bytes] = None,
    **kwargs
) -> SessionManager:
    """Create session manager with SQLite backend"""
    store = SQLiteSessionStore(db_path=db_path, encryption_key=encryption_key)
    return SessionManager(store, **kwargs)
