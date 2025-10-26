from __future__ import annotations

"""Core identity vault integration utilities."""

import asyncio
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import structlog

logger = structlog.get_logger(__name__)

try:
    from identity.tier_system import TierLevel  # type: ignore
except ImportError:  # pragma: no cover - fallback when memory lane unavailable
    from enum import IntEnum

    class TierLevel(IntEnum):
        """Fallback tier levels when the canonical tier system is unavailable."""

        PUBLIC = 0
        AUTHENTICATED = 1
        ELEVATED = 2
        PRIVILEGED = 3
        ADMIN = 4
        SYSTEM = 5


# ΛTAG: identity_profile_model
@dataclass(slots=True)
class IdentityProfile:
    """Represents a cached identity record sourced from the vault."""

    user_id: str
    tier_level: int
    attributes: dict[str, Any] = field(default_factory=dict)
    scopes: set[str] = field(default_factory=set)
    api_keys: set[str] = field(default_factory=set)
    last_refreshed: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        """Return a serialisable view of the identity profile."""

        return {
            "user_id": self.user_id,
            "tier_level": self.tier_level,
            "attributes": dict(self.attributes),
            "scopes": sorted(self.scopes),
            "api_keys": sorted(self.api_keys),
            "last_refreshed": self.last_refreshed.isoformat(),
        }


@dataclass(slots=True)
class AccessLogEntry:
    """Structured log entry for vault access events."""

    user_id: str
    memory_id: str
    tier_level: int
    action: str
    timestamp: datetime
    metadata: dict[str, Any] = field(default_factory=dict)


class IdentityVerificationError(Exception):
    """Raised when identity verification fails."""


class IdentityRateLimitExceeded(IdentityVerificationError):
    """Raised when a caller exceeds their tier-based rate limits."""


# ΛTAG: identity_vault_core
class LukhasIdentityVault:
    """Asynchronous identity vault with symbolic tracing hooks."""

    def __init__(self) -> None:
        self._records: dict[str, IdentityProfile] = {}
        self._api_key_index: dict[str, str] = {}
        self._lock = asyncio.Lock()
        self._access_log: list[AccessLogEntry] = []
        self._stats: dict[str, int] = defaultdict(int)
        self._seed_demo_identities()

    async def get_identity(self, user_id: str, *, force_refresh: bool = False) -> IdentityProfile:
        """Fetch an identity profile, optionally forcing a refresh."""

        async with self._lock:
            profile = self._records.get(user_id)
            if force_refresh or profile is None:
                profile = await self._load_identity(user_id)
                self._records[user_id] = profile
                for api_key in profile.api_keys:
                    self._api_key_index[api_key] = profile.user_id
            profile.last_refreshed = datetime.now(timezone.utc)
            logger.debug(
                "identity_profile_loaded",
                user_id=user_id,
                tier_level=profile.tier_level,
                scopes=list(profile.scopes),
                driftScore=self._stats.get("drift_score", 0),  # Symbolic metric placeholder
            )
            return IdentityProfile(
                user_id=profile.user_id,
                tier_level=profile.tier_level,
                attributes=dict(profile.attributes),
                scopes=set(profile.scopes),
                api_keys=set(profile.api_keys),
                last_refreshed=profile.last_refreshed,
            )

    async def get_identity_by_api_key(self, api_key: str) -> Optional[IdentityProfile]:
        """Resolve an API key to an identity profile."""

        async with self._lock:
            user_id = self._api_key_index.get(api_key)
            if not user_id:
                return None
            profile = self._records[user_id]
            return IdentityProfile(
                user_id=profile.user_id,
                tier_level=profile.tier_level,
                attributes=dict(profile.attributes),
                scopes=set(profile.scopes),
                api_keys=set(profile.api_keys),
                last_refreshed=profile.last_refreshed,
            )

    def get_cached_identity(self, user_id: str) -> Optional[IdentityProfile]:
        """Return the cached identity without refreshing."""

        profile = self._records.get(user_id)
        if profile is None:
            return None
        return IdentityProfile(
            user_id=profile.user_id,
            tier_level=profile.tier_level,
            attributes=dict(profile.attributes),
            scopes=set(profile.scopes),
            api_keys=set(profile.api_keys),
            last_refreshed=profile.last_refreshed,
        )

    async def register_identity(self, profile: IdentityProfile) -> None:
        """Register or overwrite an identity profile inside the vault."""

        async with self._lock:
            self._records[profile.user_id] = profile
            for api_key in profile.api_keys:
                self._api_key_index[api_key] = profile.user_id
            logger.info(
                "identity_profile_registered",
                user_id=profile.user_id,
                tier_level=profile.tier_level,
                scopes=list(profile.scopes),
            )

    async def record_api_key(self, user_id: str, api_key: str) -> None:
        """Associate an API key with an identity."""

        async with self._lock:
            profile = self._records.setdefault(
                user_id,
                IdentityProfile(user_id=user_id, tier_level=TierLevel.PUBLIC.value),
            )
            profile.api_keys.add(api_key)
            self._api_key_index[api_key] = user_id
            logger.info("identity_api_key_registered", user_id=user_id)

    async def export_access_log(self) -> list[AccessLogEntry]:
        """Return a snapshot of access events."""

        async with self._lock:
            return list(self._access_log)

    def has_access(self, user_id: str, required_tier: int) -> bool:
        """Check whether the cached identity satisfies the tier requirement."""

        profile = self._records.get(user_id)
        if profile is None:
            return required_tier <= TierLevel.PUBLIC.value
        return profile.tier_level >= required_tier

    def log_access(
        self,
        *,
        user_id: str,
        memory_id: str,
        tier_level: int,
        action: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """Record an access event."""

        entry = AccessLogEntry(
            user_id=user_id,
            memory_id=memory_id,
            tier_level=tier_level,
            action=action,
            timestamp=datetime.now(timezone.utc),
            metadata=metadata or {},
        )
        self._access_log.append(entry)
        logger.info(
            "identity_access_logged",
            user_id=user_id,
            memory_id=memory_id,
            tier_level=tier_level,
            action=action,
            affect_delta=metadata.get("affect_delta") if metadata else None,
        )

    async def _load_identity(self, user_id: str) -> IdentityProfile:
        """Simulate loading an identity from an external service."""

        # ΛTAG: identity_vault_fetch
        await asyncio.sleep(0)  # Cooperative scheduling for async callers

        profile = self._records.get(user_id)
        if profile is not None:
            return profile

        # TODO: Replace with real Identity service lookup (# ΛTAG: identity_fetch_todo)
        inferred_tier = TierLevel.AUTHENTICATED.value if user_id else TierLevel.PUBLIC.value
        profile = IdentityProfile(
            user_id=user_id or "anonymous",
            tier_level=inferred_tier,
            attributes={"display_name": user_id or "Guest"},
            scopes={"core:read"} if inferred_tier > TierLevel.PUBLIC.value else set(),
            api_keys=set(),
        )
        return profile

    def _seed_demo_identities(self) -> None:
        """Seed deterministic demo identities for integration tests."""

        demo_profiles = [
            IdentityProfile(
                user_id="demo_admin",
                tier_level=TierLevel.ADMIN.value,
                attributes={"display_name": "Demo Admin"},
                scopes={"core:write", "identity:manage"},
                api_keys={"sk_live_admin_demo1234"},
            ),
            IdentityProfile(
                user_id="demo_user",
                tier_level=TierLevel.ELEVATED.value,
                attributes={"display_name": "Demo User"},
                scopes={"core:read"},
                api_keys={"sk_live_std_demo5678"},
            ),
        ]
        for profile in demo_profiles:
            self._records[profile.user_id] = profile
            for api_key in profile.api_keys:
                self._api_key_index[api_key] = profile.user_id


_DEFAULT_VAULT = LukhasIdentityVault()


def _coerce_required_tier(required_tier: int | TierLevel) -> int:
    if isinstance(required_tier, TierLevel):
        return int(required_tier.value)
    return int(required_tier)


def has_access(*, user_id: str, memory_id: str, required_tier: int | TierLevel) -> bool:
    """Module-level helper used by legacy integrations."""

    tier_requirement = _coerce_required_tier(required_tier)
    allowed = _DEFAULT_VAULT.has_access(user_id, tier_requirement)
    logger.debug(
        "identity_access_check",
        user_id=user_id,
        memory_id=memory_id,
        required_tier=tier_requirement,
        allowed=allowed,
    )
    return allowed


def log_access(
    *,
    user_id: str,
    action: str,
    memory_id: str,
    tier: int | TierLevel,
    metadata: Optional[dict[str, Any]] = None,
) -> None:
    """Record identity access using the shared vault instance."""

    tier_level = _coerce_required_tier(tier)
    _DEFAULT_VAULT.log_access(
        user_id=user_id,
        memory_id=memory_id,
        tier_level=tier_level,
        action=action,
        metadata=metadata,
    )


# ΛTAG: identity_manager_core
class IdentityManager:
    """High-level identity orchestrator bridging orchestration and API layers."""

    RATE_LIMITS_PER_MINUTE = {
        TierLevel.PUBLIC.value: 30,
        TierLevel.AUTHENTICATED.value: 60,
        TierLevel.ELEVATED.value: 120,
        TierLevel.PRIVILEGED.value: 240,
        TierLevel.ADMIN.value: 360,
        TierLevel.SYSTEM.value: 600,
    }

    def __init__(self, vault: Optional[LukhasIdentityVault] = None) -> None:
        self._vault = vault or _DEFAULT_VAULT
        self._rate_lock = asyncio.Lock()
        self._request_windows: dict[str, tuple[float, int]] = {}
        self._session_store: dict[str, dict[str, Any]] = {}

    async def get_user_identity(self, user_id: str, *, force_refresh: bool = False) -> IdentityProfile:
        """Load and cache identity information for a user."""

        profile = await self._vault.get_identity(user_id, force_refresh=force_refresh)
        self._session_store.setdefault(user_id, {"active_sessions": set()})
        return profile

    async def start_session(self, user_id: str, session_id: Optional[str] = None) -> dict[str, Any]:
        """Register a symbolic session for the given user."""

        profile = await self.get_user_identity(user_id)
        session_id = session_id or f"session::{user_id}::{datetime.now(timezone.utc).isoformat()}"
        session_data = {
            "session_id": session_id,
            "tier_level": profile.tier_level,
            "started_at": datetime.now(timezone.utc).isoformat(),
        }
        self._session_store.setdefault(user_id, {"active_sessions": set()})["active_sessions"].add(session_id)
        logger.info(
            "identity_session_started",
            user_id=user_id,
            session_id=session_id,
            tier_level=profile.tier_level,
        )
        return session_data

    async def authenticate_api_key(self, api_key: str) -> IdentityProfile:
        """Resolve and validate an API key against the identity vault."""

        profile = await self._vault.get_identity_by_api_key(api_key)
        if profile is None:
            logger.warning("identity_api_key_invalid", api_key=api_key[-8:])
            raise IdentityVerificationError("Unknown API key")

        await self._enforce_rate_limit(profile.user_id, profile.tier_level)
        log_access(
            user_id=profile.user_id,
            action="api_key_authenticate",
            memory_id="api_gateway",
            tier=profile.tier_level,
            metadata={"api_key_suffix": api_key[-6:]},
        )
        return profile

    async def ensure_permission(
        self,
        *,
        user_id: str,
        memory_id: str,
        required_tier: int | TierLevel,
        action: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Ensure the caller meets the required tier and log the attempt."""

        tier_requirement = _coerce_required_tier(required_tier)
        if not has_access(user_id=user_id, memory_id=memory_id, required_tier=tier_requirement):
            logger.warning(
                "identity_permission_denied",
                user_id=user_id,
                memory_id=memory_id,
                required_tier=tier_requirement,
            )
            raise IdentityVerificationError("Insufficient tier access")

        log_access(
            user_id=user_id,
            action=action,
            memory_id=memory_id,
            tier=tier_requirement,
            metadata=metadata,
        )

    async def _enforce_rate_limit(self, user_id: str, tier_level: int) -> None:
        """Apply tier-based rate limiting to protect shared resources."""

        limit = self.RATE_LIMITS_PER_MINUTE.get(tier_level, 30)
        now = datetime.now(timezone.utc).timestamp()
        async with self._rate_lock:
            window_start, count = self._request_windows.get(user_id, (now, 0))
            if now - window_start >= 60:
                window_start = now
                count = 0
            count += 1
            if count > limit:
                logger.error(
                    "identity_rate_limit_exceeded",
                    user_id=user_id,
                    tier_level=tier_level,
                    limit=limit,
                )
                raise IdentityRateLimitExceeded("Rate limit exceeded for identity operations")
            self._request_windows[user_id] = (window_start, count)

    async def describe_permissions(self, user_id: str) -> dict[str, Any]:
        """Return a structured view of the user's permissions."""

        profile = await self.get_user_identity(user_id)
        return {
            "user_id": profile.user_id,
            "tier_level": profile.tier_level,
            "scopes": sorted(profile.scopes),
            "attributes": dict(profile.attributes),
            "active_sessions": sorted(
                self._session_store.get(user_id, {}).get("active_sessions", set())
            ),
        }


__all__ = [
    "IdentityManager",
    "IdentityProfile",
    "IdentityRateLimitExceeded",
    "IdentityVerificationError",
    "LukhasIdentityVault",
    "AccessLogEntry",
    "has_access",
    "log_access",
]
