"""
LUKHAS Identity Session Service
==============================
Dedicated service for user session management with in-memory and persistent storage.
Implements SessionManagerInterface for T4 architecture compliance.
"""

import logging
import time
import asyncio
import uuid
from typing import Any, Optional, Dict
from collections import defaultdict
from dataclasses import dataclass, asdict

from ..facades.authentication_facade import SessionManagerInterface

logger = logging.getLogger(__name__)


@dataclass
class Session:
    """Session data structure"""
    session_id: str
    user_id: str
    username: str
    created_at: float
    last_accessed: float
    expires_at: float
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        self.metadata = self.metadata or {}

    def is_expired(self) -> bool:
        """Check if session is expired"""
        return time.time() > self.expires_at

    def refresh(self, extend_by: int = 3600):
        """Refresh session expiry"""
        self.last_accessed = time.time()
        self.expires_at = self.last_accessed + extend_by

    def to_dict(self) -> dict:
        """Convert session to dictionary"""
        return asdict(self)


class SessionService(SessionManagerInterface):
    """
    In-memory session service with optional persistence
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """Initialize session service"""
        self.config = config or {}
        self.sessions: Dict[str, Session] = {}
        self.user_sessions: Dict[str, set[str]] = defaultdict(set)

        # Configuration
        self.default_ttl = self.config.get("session_ttl_seconds", 3600)  # 1 hour
        self.max_sessions_per_user = self.config.get("max_sessions_per_user", 10)
        self.cleanup_interval = self.config.get("cleanup_interval_seconds", 300)  # 5 minutes

        # Start background cleanup
        asyncio.create_task(self._cleanup_loop())

        logger.info("Session service initialized")

    async def create_session(self, user_id: str, **kwargs) -> str:
        """Create new user session"""
        try:
            session_id = str(uuid.uuid4())
            now = time.time()

            session = Session(
                session_id=session_id,
                user_id=user_id,
                username=kwargs.get("username", "unknown"),
                created_at=now,
                last_accessed=now,
                expires_at=now + kwargs.get("ttl", self.default_ttl),
                ip_address=kwargs.get("ip_address"),
                user_agent=kwargs.get("user_agent"),
                metadata=kwargs.get("metadata", {})
            )

            # Enforce max sessions per user
            await self._enforce_session_limits(user_id)

            # Store session
            self.sessions[session_id] = session
            self.user_sessions[user_id].add(session_id)

            logger.info(f"Created session {session_id} for user {user_id}")
            return session_id

        except Exception as e:
            logger.error(f"Session creation failed: {e}")
            raise

    async def get_session(self, session_id: str, **kwargs) -> Optional[dict[str, Any]]:
        """Get session information"""
        try:
            session = self.sessions.get(session_id)
            if not session:
                return None

            # Check if expired
            if session.is_expired():
                await self.destroy_session(session_id)
                return None

            # Refresh session if requested
            if kwargs.get("refresh", True):
                session.refresh(kwargs.get("extend_by", self.default_ttl))

            return session.to_dict()

        except Exception as e:
            logger.error(f"Session retrieval failed: {e}")
            return None

    async def destroy_session(self, session_id: str, **kwargs) -> bool:
        """Destroy user session"""
        try:
            session = self.sessions.get(session_id)
            if not session:
                return False

            # Remove from storage
            del self.sessions[session_id]
            self.user_sessions[session.user_id].discard(session_id)

            # Cleanup empty user session sets
            if not self.user_sessions[session.user_id]:
                del self.user_sessions[session.user_id]

            logger.info(f"Destroyed session {session_id}")
            return True

        except Exception as e:
            logger.error(f"Session destruction failed: {e}")
            return False

    async def destroy_user_sessions(self, user_id: str) -> int:
        """Destroy all sessions for a user"""
        try:
            session_ids = self.user_sessions.get(user_id, set()).copy()
            destroyed_count = 0

            for session_id in session_ids:
                if await self.destroy_session(session_id):
                    destroyed_count += 1

            logger.info(f"Destroyed {destroyed_count} sessions for user {user_id}")
            return destroyed_count

        except Exception as e:
            logger.error(f"User session destruction failed: {e}")
            return 0

    async def list_user_sessions(self, user_id: str) -> list[dict[str, Any]]:
        """List all active sessions for a user"""
        try:
            session_ids = self.user_sessions.get(user_id, set())
            sessions = []

            for session_id in session_ids.copy():  # Copy to avoid modification during iteration
                session = self.sessions.get(session_id)
                if session:
                    if session.is_expired():
                        await self.destroy_session(session_id)
                    else:
                        sessions.append(session.to_dict())

            return sessions

        except Exception as e:
            logger.error(f"Session listing failed: {e}")
            return []

    async def validate_session(self, session_id: str) -> bool:
        """Validate if session exists and is active"""
        session_data = await self.get_session(session_id, refresh=False)
        return session_data is not None

    async def _enforce_session_limits(self, user_id: str):
        """Enforce maximum sessions per user"""
        try:
            session_ids = list(self.user_sessions.get(user_id, set()))

            if len(session_ids) >= self.max_sessions_per_user:
                # Sort by last_accessed and remove oldest sessions
                sessions_with_time = []
                for sid in session_ids:
                    session = self.sessions.get(sid)
                    if session:
                        sessions_with_time.append((session.last_accessed, sid))

                sessions_with_time.sort()  # Oldest first

                # Remove excess sessions
                to_remove = len(sessions_with_time) - self.max_sessions_per_user + 1
                for i in range(to_remove):
                    _, old_session_id = sessions_with_time[i]
                    await self.destroy_session(old_session_id)
                    logger.info(f"Removed old session {old_session_id} to enforce limits")

        except Exception as e:
            logger.error(f"Session limit enforcement failed: {e}")

    async def _cleanup_loop(self):
        """Background task to cleanup expired sessions"""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._cleanup_expired_sessions()
            except Exception as e:
                logger.error(f"Session cleanup failed: {e}")

    async def _cleanup_expired_sessions(self):
        """Remove expired sessions"""
        try:
            now = time.time()
            expired_sessions = []

            for session_id, session in self.sessions.items():
                if session.is_expired():
                    expired_sessions.append(session_id)

            for session_id in expired_sessions:
                await self.destroy_session(session_id)

            if expired_sessions:
                logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")

        except Exception as e:
            logger.error(f"Session cleanup failed: {e}")

    def get_health_status(self) -> dict[str, Any]:
        """Get service health status"""
        return {
            "active_sessions": len(self.sessions),
            "active_users": len(self.user_sessions),
            "default_ttl": self.default_ttl,
            "max_sessions_per_user": self.max_sessions_per_user,
            "cleanup_interval": self.cleanup_interval
        }

    async def get_stats(self) -> dict[str, Any]:
        """Get detailed session statistics"""
        try:
            now = time.time()
            expired_count = sum(1 for s in self.sessions.values() if s.is_expired())

            # Calculate session duration stats
            durations = [(now - s.created_at) for s in self.sessions.values() if not s.is_expired()]
            avg_duration = sum(durations) / len(durations) if durations else 0

            return {
                "total_sessions": len(self.sessions),
                "expired_sessions": expired_count,
                "active_sessions": len(self.sessions) - expired_count,
                "unique_users": len(self.user_sessions),
                "average_session_duration_seconds": avg_duration,
                "sessions_per_user": {
                    user_id: len(sessions)
                    for user_id, sessions in self.user_sessions.items()
                }
            }
        except Exception as e:
            logger.error(f"Stats calculation failed: {e}")
            return {}


# Factory function
def create_session_service(config: Optional[dict[str, Any]] = None) -> SessionService:
    """Create session service instance"""
    return SessionService(config)