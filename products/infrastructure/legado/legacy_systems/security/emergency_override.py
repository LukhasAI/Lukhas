"""Emergency override utilities for the legacy security stack."""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Optional

from .secure_utils import SecurityError, sanitize_input

logger = logging.getLogger("ΛTRACE.products.legacy.security.emergency")


@dataclass
class SafetyProfile:
    """Runtime-configurable safety profile for Guardian overrides."""

    safe_mode: bool = False
    refuse_unknown: bool = True
    minimum_tier: int = 2

    # ΛTAG: guardian_profile_builder
    @classmethod
    def from_mapping(cls, data: Optional[Mapping[str, Any]]) -> "SafetyProfile":
        if not data:
            return cls()
        return cls(
            safe_mode=bool(data.get("safe_mode", False)),
            refuse_unknown=bool(data.get("refuse_unknown", True)),
            minimum_tier=int(data.get("minimum_tier", 2)),
        )


_DEFAULT_LOG_PATH = Path("logs/emergency_log.jsonl")


# ΛTAG: guardian_flag_eval
def check_safety_flags(
    user_context: Optional[Mapping[str, Any]] = None,
    safety_profile: Optional[Mapping[str, Any]] = None,
) -> bool:
    """Evaluate Guardian safety flags for the provided user context."""

    profile = SafetyProfile.from_mapping(safety_profile)
    user_tier = int(user_context.get("tier", 0)) if user_context else 0
    is_unknown = not user_context or not user_context.get("user")

    triggered = profile.safe_mode or (profile.refuse_unknown and user_tier < profile.minimum_tier)

    if triggered:
        logger.warning(
            "Guardian safety flags triggered",
            extra={
                "tier": user_tier,
                "safe_mode": profile.safe_mode,
                "refuse_unknown": profile.refuse_unknown,
                "minimum_tier": profile.minimum_tier,
                "unknown_actor": is_unknown,
            },
        )

    return triggered


def _prepare_log_entry(
    reason: str, user_context: Optional[Mapping[str, Any]], profile: SafetyProfile
) -> Mapping[str, Any]:
    sanitized_reason = sanitize_input(reason)
    user_info = {
        "user": sanitize_input(user_context.get("user", "unknown")) if user_context else "unknown",
        "tier": int(user_context.get("tier", 0)) if user_context else 0,
    }

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "reason": sanitized_reason,
        "user": user_info,
        "profile": asdict(profile),
        "system_state": {
            "safe_mode": profile.safe_mode,
            "refuse_unknown": profile.refuse_unknown,
        },
    }


# ΛTAG: guardian_incident_log
def log_incident(
    reason: str,
    user_context: Optional[Mapping[str, Any]] = None,
    *,
    safety_profile: Optional[Mapping[str, Any]] = None,
    log_path: Optional[Path] = None,
) -> Path:
    """Persist an emergency incident entry to the Guardian audit log."""

    profile = SafetyProfile.from_mapping(safety_profile)
    entry = _prepare_log_entry(reason, user_context, profile)

    target_path = (log_path or _DEFAULT_LOG_PATH).resolve()
    target_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with target_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry) + "\n")
    except OSError as exc:  # pragma: no cover - protective logging
        logger.error("Failed to persist Guardian incident", extra={"error": str(exc), "path": str(target_path)})
        raise SecurityError("Unable to persist emergency incident") from exc

    return target_path


# ΛTAG: guardian_shutdown
def shutdown_systems(
    reason: str = "Unspecified emergency condition",
    *,
    user_context: Optional[Mapping[str, Any]] = None,
    safety_profile: Optional[Mapping[str, Any]] = None,
    log_path: Optional[Path] = None,
) -> Path:
    """Trigger a symbolic system shutdown and record the incident."""

    profile = SafetyProfile.from_mapping(safety_profile)
    logger.critical(
        "Guardian shutdown initiated",
        extra={
            "reason": sanitize_input(reason),
            "tier": int(user_context.get("tier", 0)) if user_context else 0,
            "profile": asdict(profile),
        },
    )

    return log_incident(reason, user_context, safety_profile=profile.__dict__, log_path=log_path)


__all__ = [
    "SafetyProfile",
    "check_safety_flags",
    "log_incident",
    "shutdown_systems",
]
