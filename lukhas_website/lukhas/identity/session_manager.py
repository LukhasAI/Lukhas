"""
I.6 Session Management & Device Registry - Device binding and session lifecycle
Comprehensive session management with device binding, lifecycle tracking, and security controls.
"""

import uuid
import time
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field
from enum import Enum
import asyncio

from lukhas.identity.token_generator import TokenGenerator
from lukhas.identity.observability import IdentityObservability

logger = logging.getLogger(__name__)


class SessionState(Enum):
    """Session lifecycle states"""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUSPENDED = "suspended"


class DeviceType(Enum):
    """Supported device types for registry"""
    DESKTOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"
    WEB = "web"
    API = "api"
    IOT = "iot"


@dataclass
class DeviceInfo:
    """Device registration information"""
    device_id: str
    device_type: DeviceType
    device_name: str
    user_agent: str
    fingerprint: str
    ip_address: str
    registered_at: datetime
    last_seen: datetime
    trust_level: float = 0.5  # 0.0 to 1.0
    capabilities: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SessionInfo:
    """Session lifecycle information"""
    session_id: str
    lambda_id: str
    device_id: str
    state: SessionState
    created_at: datetime
    last_activity: datetime
    expires_at: datetime
    ip_address: str
    user_agent: str
    tier_level: int
    scopes: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_valid(self) -> bool:
        """Check if session is currently valid"""
        return (
            self.state == SessionState.ACTIVE and
            self.expires_at > datetime.utcnow()
        )

    @property
    def remaining_ttl(self) -> int:
        """Get remaining session TTL in seconds"""
        if not self.is_valid:
            return 0
        return int((self.expires_at - datetime.utcnow()).total_seconds())


class SessionManager:
    """
    I.6 Session Management & Device Registry
    Manages session lifecycle, device binding, and security controls
    """

    def __init__(self,
                 token_generator: TokenGenerator,
                 observability: IdentityObservability,
                 session_ttl: int = 3600,  # 1 hour default
                 device_trust_threshold: float = 0.7,
                 max_sessions_per_device: int = 5,
                 max_devices_per_user: int = 10):
        self.token_generator = token_generator
        self.observability = observability
        self.session_ttl = session_ttl
        self.device_trust_threshold = device_trust_threshold
        self.max_sessions_per_device = max_sessions_per_device
        self.max_devices_per_user = max_devices_per_user

        # In-memory stores (production would use Redis/PostgreSQL)
        self.sessions: Dict[str, SessionInfo] = {}
        self.devices: Dict[str, DeviceInfo] = {}
        self.user_sessions: Dict[str, Set[str]] = {}  # lambda_id -> session_ids
        self.user_devices: Dict[str, Set[str]] = {}   # lambda_id -> device_ids
        self.device_sessions: Dict[str, Set[str]] = {}  # device_id -> session_ids

        # Cleanup task
        self._cleanup_task: Optional[asyncio.Task] = None

    async def start(self):
        """Start session manager background tasks"""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def stop(self):
        """Stop session manager background tasks"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None

    async def register_device(self,
                            lambda_id: str,
                            device_type: DeviceType,
                            device_name: str,
                            user_agent: str,
                            ip_address: str,
                            capabilities: Optional[Set[str]] = None) -> DeviceInfo:
        """Register a new device for a user"""

        # Check device limits
        user_device_count = len(self.user_devices.get(lambda_id, set()))
        if user_device_count >= self.max_devices_per_user:
            raise ValueError(f"Device limit exceeded: {user_device_count}/{self.max_devices_per_user}")

        # Generate device fingerprint
        fingerprint_data = f"{user_agent}:{ip_address}:{device_name}:{device_type.value}"
        fingerprint = hashlib.sha256(fingerprint_data.encode()).hexdigest()[:16]

        # Check for existing device with same fingerprint
        for device in self.devices.values():
            if device.fingerprint == fingerprint and device.device_id in self.user_devices.get(lambda_id, set()):
                logger.info(f"Device already registered: {device.device_id}")
                return device

        # Create new device
        device_id = f"dev_{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()

        device_info = DeviceInfo(
            device_id=device_id,
            device_type=device_type,
            device_name=device_name,
            user_agent=user_agent,
            fingerprint=fingerprint,
            ip_address=ip_address,
            registered_at=now,
            last_seen=now,
            trust_level=0.3,  # New devices start with low trust
            capabilities=capabilities or set(),
            metadata={"registration_ip": ip_address}
        )

        # Store device
        self.devices[device_id] = device_info
        if lambda_id not in self.user_devices:
            self.user_devices[lambda_id] = set()
        self.user_devices[lambda_id].add(device_id)

        # Record metrics
        await self.observability.record_device_registration(lambda_id, device_type.value)

        logger.info(f"Device registered: {device_id} for user {lambda_id}")
        return device_info

    async def create_session(self,
                           lambda_id: str,
                           device_id: str,
                           ip_address: str,
                           user_agent: str,
                           tier_level: int,
                           scopes: Optional[Set[str]] = None,
                           custom_ttl: Optional[int] = None) -> SessionInfo:
        """Create a new session for authenticated user"""

        # Validate device ownership
        if device_id not in self.user_devices.get(lambda_id, set()):
            raise ValueError(f"Device {device_id} not registered for user {lambda_id}")

        # Check session limits per device
        device_session_count = len(self.device_sessions.get(device_id, set()))
        if device_session_count >= self.max_sessions_per_device:
            # Clean up oldest sessions for this device
            await self._cleanup_device_sessions(device_id)

        # Update device last seen
        if device_id in self.devices:
            self.devices[device_id].last_seen = datetime.utcnow()
            self.devices[device_id].ip_address = ip_address

        # Create session
        session_id = f"ses_{uuid.uuid4().hex}"
        now = datetime.utcnow()
        ttl = custom_ttl or self.session_ttl
        expires_at = now + timedelta(seconds=ttl)

        session_info = SessionInfo(
            session_id=session_id,
            lambda_id=lambda_id,
            device_id=device_id,
            state=SessionState.ACTIVE,
            created_at=now,
            last_activity=now,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent,
            tier_level=tier_level,
            scopes=scopes or set(),
            metadata={"creation_ip": ip_address}
        )

        # Store session
        self.sessions[session_id] = session_info

        # Update indexes
        if lambda_id not in self.user_sessions:
            self.user_sessions[lambda_id] = set()
        self.user_sessions[lambda_id].add(session_id)

        if device_id not in self.device_sessions:
            self.device_sessions[device_id] = set()
        self.device_sessions[device_id].add(session_id)

        # Record metrics
        await self.observability.record_session_created(lambda_id, tier_level)

        logger.info(f"Session created: {session_id} for user {lambda_id} on device {device_id}")
        return session_info

    async def validate_session(self, session_id: str) -> Optional[SessionInfo]:
        """Validate and refresh session if valid"""
        session = self.sessions.get(session_id)
        if not session:
            return None

        # Check expiration and state
        if not session.is_valid:
            if session.state == SessionState.ACTIVE:
                session.state = SessionState.EXPIRED
            return None

        # Update last activity
        session.last_activity = datetime.utcnow()

        # Record activity
        await self.observability.record_session_activity(session.lambda_id)

        return session

    async def refresh_session(self, session_id: str, extend_ttl: Optional[int] = None) -> bool:
        """Refresh session expiration"""
        session = self.sessions.get(session_id)
        if not session or session.state != SessionState.ACTIVE:
            return False

        # Extend session
        ttl = extend_ttl or self.session_ttl
        session.expires_at = datetime.utcnow() + timedelta(seconds=ttl)
        session.last_activity = datetime.utcnow()

        logger.info(f"Session refreshed: {session_id}")
        return True

    async def revoke_session(self, session_id: str, reason: str = "manual_revocation") -> bool:
        """Revoke a specific session"""
        session = self.sessions.get(session_id)
        if not session:
            return False

        session.state = SessionState.REVOKED
        session.metadata["revocation_reason"] = reason
        session.metadata["revoked_at"] = datetime.utcnow().isoformat()

        # Record metrics
        await self.observability.record_session_revoked(session.lambda_id, reason)

        logger.info(f"Session revoked: {session_id}, reason: {reason}")
        return True

    async def revoke_all_user_sessions(self, lambda_id: str, reason: str = "user_logout") -> int:
        """Revoke all sessions for a user"""
        user_sessions = self.user_sessions.get(lambda_id, set()).copy()
        revoked_count = 0

        for session_id in user_sessions:
            if await self.revoke_session(session_id, reason):
                revoked_count += 1

        logger.info(f"Revoked {revoked_count} sessions for user {lambda_id}")
        return revoked_count

    async def revoke_device_sessions(self, device_id: str, reason: str = "device_compromised") -> int:
        """Revoke all sessions for a device"""
        device_sessions = self.device_sessions.get(device_id, set()).copy()
        revoked_count = 0

        for session_id in device_sessions:
            if await self.revoke_session(session_id, reason):
                revoked_count += 1

        logger.info(f"Revoked {revoked_count} sessions for device {device_id}")
        return revoked_count

    async def unregister_device(self, lambda_id: str, device_id: str) -> bool:
        """Unregister a device and revoke its sessions"""
        if device_id not in self.user_devices.get(lambda_id, set()):
            return False

        # Revoke all device sessions
        await self.revoke_device_sessions(device_id, "device_unregistered")

        # Remove device
        if device_id in self.devices:
            del self.devices[device_id]

        self.user_devices[lambda_id].discard(device_id)
        if device_id in self.device_sessions:
            del self.device_sessions[device_id]

        logger.info(f"Device unregistered: {device_id} for user {lambda_id}")
        return True

    async def get_user_sessions(self, lambda_id: str, active_only: bool = True) -> List[SessionInfo]:
        """Get all sessions for a user"""
        user_sessions = self.user_sessions.get(lambda_id, set())
        sessions = []

        for session_id in user_sessions:
            session = self.sessions.get(session_id)
            if session:
                if not active_only or session.is_valid:
                    sessions.append(session)

        return sorted(sessions, key=lambda s: s.last_activity, reverse=True)

    async def get_user_devices(self, lambda_id: str) -> List[DeviceInfo]:
        """Get all registered devices for a user"""
        user_devices = self.user_devices.get(lambda_id, set())
        devices = []

        for device_id in user_devices:
            device = self.devices.get(device_id)
            if device:
                devices.append(device)

        return sorted(devices, key=lambda d: d.last_seen, reverse=True)

    async def update_device_trust(self, device_id: str, trust_delta: float, reason: str) -> bool:
        """Update device trust level"""
        device = self.devices.get(device_id)
        if not device:
            return False

        old_trust = device.trust_level
        device.trust_level = max(0.0, min(1.0, device.trust_level + trust_delta))

        device.metadata[f"trust_update_{int(time.time())}"] = {
            "old_trust": old_trust,
            "new_trust": device.trust_level,
            "delta": trust_delta,
            "reason": reason
        }

        logger.info(f"Device trust updated: {device_id}, {old_trust:.3f} -> {device.trust_level:.3f} ({reason})")
        return True

    async def _cleanup_device_sessions(self, device_id: str):
        """Clean up oldest sessions for a device"""
        device_sessions = self.device_sessions.get(device_id, set())
        sessions = []

        for session_id in device_sessions:
            session = self.sessions.get(session_id)
            if session:
                sessions.append(session)

        # Sort by last activity and revoke oldest
        sessions.sort(key=lambda s: s.last_activity)
        to_revoke = len(sessions) - self.max_sessions_per_device + 1

        for session in sessions[:to_revoke]:
            await self.revoke_session(session.session_id, "session_limit_exceeded")

    async def _cleanup_loop(self):
        """Background cleanup of expired sessions"""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                await self._cleanup_expired_sessions()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Session cleanup error: {e}")
                await asyncio.sleep(60)  # Wait before retry

    async def _cleanup_expired_sessions(self):
        """Remove expired and revoked sessions"""
        now = datetime.utcnow()
        expired_sessions = []

        for session_id, session in self.sessions.items():
            if session.expires_at < now and session.state == SessionState.ACTIVE:
                session.state = SessionState.EXPIRED

            if session.state in [SessionState.EXPIRED, SessionState.REVOKED]:
                # Keep sessions for 24 hours for audit purposes
                if session.expires_at < now - timedelta(hours=24):
                    expired_sessions.append(session_id)

        # Clean up expired sessions
        for session_id in expired_sessions:
            session = self.sessions.pop(session_id, None)
            if session:
                # Remove from indexes
                self.user_sessions.get(session.lambda_id, set()).discard(session_id)
                self.device_sessions.get(session.device_id, set()).discard(session_id)

        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")

    async def get_session_stats(self) -> Dict[str, Any]:
        """Get session management statistics"""
        now = datetime.utcnow()
        active_sessions = sum(1 for s in self.sessions.values() if s.is_valid)

        return {
            "total_sessions": len(self.sessions),
            "active_sessions": active_sessions,
            "total_devices": len(self.devices),
            "total_users": len(self.user_sessions),
            "session_states": {
                state.value: sum(1 for s in self.sessions.values() if s.state == state)
                for state in SessionState
            },
            "device_types": {
                dtype.value: sum(1 for d in self.devices.values() if d.device_type == dtype)
                for dtype in DeviceType
            },
            "trusted_devices": sum(1 for d in self.devices.values() if d.trust_level >= self.device_trust_threshold)
        }


class SessionRegistry:
    """Global session registry for distributed deployments"""

    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager
        self._lock = asyncio.Lock()

    async def register_session_manager(self, instance_id: str):
        """Register this session manager instance"""
        # Implementation would handle distributed coordination
        pass

    async def sync_session_state(self, session_id: str, state_update: Dict[str, Any]):
        """Synchronize session state across instances"""
        # Implementation would handle cross-instance sync
        pass