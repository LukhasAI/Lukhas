"""Simplified Lukhas identity vault access control for core lane."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Iterable, List, Optional

logger = logging.getLogger("lukhas_id")

# ΛTAG: driftScore - tier levels for symbolic access decisions
_TIER_LEVELS: Dict[str, int] = {
    "public": 0,
    "resident": 1,
    "guardian": 2,
    "root": 3,
}


@dataclass
class IdentityAccessLog:
    """Record of a single access event within the vault."""

    user_id: str
    action: str
    memory_id: str
    tier: str
    driftScore: float = 0.0
    affect_delta: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)


class IdentityRegistry:
    """In-memory registry for user tiers."""

    def __init__(self) -> None:
        self._tiers: Dict[str, str] = {}
        logger.debug("IdentityRegistry initialized", extra={"registered_users": 0})

    def register(self, user_id: str, tier: str) -> None:
        if tier not in _TIER_LEVELS:
            raise ValueError(f"Unknown tier '{tier}'")
        self._tiers[user_id] = tier
        logger.debug("User tier registered", extra={"user_id": user_id, "tier": tier})

    def get_tier(self, user_id: str) -> str:
        return self._tiers.get(user_id, "public")

    def users(self) -> Iterable[str]:
        return self._tiers.keys()

    def has_access(self, user_id: str, required_tier: str) -> bool:
        user_tier = self.get_tier(user_id)
        required_level = _TIER_LEVELS.get(required_tier, 0)
        user_level = _TIER_LEVELS.get(user_tier, 0)
        return user_level >= required_level


class IdentityClient:
    """High level helper that wraps registry interactions."""

    def __init__(self, registry: Optional[IdentityRegistry] = None) -> None:
        self._registry = registry or _GLOBAL_REGISTRY

    def register_user(self, user_id: str, tier: str) -> None:
        self._registry.register(user_id, tier)

    def has_access(self, user_id: str, required_tier: str) -> bool:
        return self._registry.has_access(user_id, required_tier)


_GLOBAL_REGISTRY = IdentityRegistry()
_ACCESS_LOG: List[IdentityAccessLog] = []


def has_access(*, user_id: str, memory_id: str, required_tier: str) -> bool:
    """Check whether a user may access a specific memory strand."""

    allowed = _GLOBAL_REGISTRY.has_access(user_id, required_tier)
    logger.debug(
        "Access check performed",
        extra={
            "user_id": user_id,
            "memory_id": memory_id,
            "required_tier": required_tier,
            "allowed": allowed,
        },
    )
    return allowed


def log_access(*, user_id: str, action: str, memory_id: str, tier: str) -> None:
    """Log a vault access event for audit purposes."""

    entry = IdentityAccessLog(user_id=user_id, action=action, memory_id=memory_id, tier=tier)
    _ACCESS_LOG.append(entry)
    logger.info(
        "Vault access recorded",
        extra={
            "user_id": user_id,
            "action": action,
            "memory_id": memory_id,
            "tier": tier,
            "driftScore": entry.driftScore,
            "affect_delta": entry.affect_delta,
        },
    )
    # ✅ TODO: persist audit trail once storage bridge is connected


def get_access_log() -> List[IdentityAccessLog]:
    """Expose access logs for diagnostics and testing."""

    return list(_ACCESS_LOG)


def reset_registry(*, tiers: Optional[Dict[str, str]] = None) -> None:
    """Utility used by tests to reset registry state."""

    _GLOBAL_REGISTRY._tiers.clear()
    if tiers:
        for user_id, tier in tiers.items():
            _GLOBAL_REGISTRY.register(user_id, tier)
    _ACCESS_LOG.clear()
    logger.debug("Identity registry reset", extra={"user_count": len(_GLOBAL_REGISTRY._tiers)})
