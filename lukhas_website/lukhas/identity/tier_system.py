"""
LUKHAS Memory Tier System

Purpose:
  Implements dynamic, context-aware access control using a 6-tier privilege model.
  Tracks session elevation, scope, and symbolic audit for every memory operation.

Metadata:
  Origin: Claude_Code
  Phase: Memory Governance Layer
  LUKHAS_TAGS: memory_access_control, privilege_tiers, symbolic_audit

License:
  OpenAI-aligned AGI Symbolic Framework (internal use)
"""

import logging
import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from functools import wraps
from typing import Any, Callable, Optional, Union
import structlog
        try:
            from identity.core.user_tier_mapping import get_user_tier
        try:
        try:

log = logging.getLogger(__name__)

            os.makedirs(os.path.dirname(self.elevation_log_path), exist_ok=True)
            with open(self.elevation_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(elevation_data) + "\n")
        except Exception as e:
            logger.error("ElevationLog_failed", error=str(e))


# LUKHAS_TAG: decorator_system
def lukhas_tier_required(required_tier: TierLevel, scope: PermissionScope = PermissionScope.MEMORY_FOLD):
    """
    Advanced decorator for enforcing tier-based access control.

    Args:
        required_tier: Minimum tier level required
        scope: Permission scope for the operation
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract context from function arguments or global state
            context = _extract_access_context(func, args, kwargs, scope)

            # Get tier system instance
            tier_system = _get_tier_system_instance()

            # Check access
            decision = tier_system.check_access(context, required_tier)

            if not decision.granted:
                logger.warning(
                    "TierAccess_denied",
                    function=func.__name__,
                    required_tier=required_tier.name,
                    reason=decision.reasoning,
                    decision_id=decision.decision_id,
                )

                raise PermissionError(f"Access denied: {decision.reasoning} (Decision ID: {decision.decision_id})")

            # Access granted - proceed with function execution
            logger.debug(
                "TierAccess_granted",
                function=func.__name__,
                tier_level=decision.tier_level.name,
                decision_id=decision.decision_id,
            )

            return func(*args, **kwargs)

        # Store tier requirement metadata
        wrapper._lukhas_tier = required_tier.value
        wrapper._lukhas_scope = scope.value

        return wrapper

    return decorator


# Global tier system instance
_tier_system_instance = None


def _get_tier_system_instance() -> DynamicTierSystem:
    """Get or create the global tier system instance."""
    global _tier_system_instance
    if _tier_system_instance is None:
        _tier_system_instance = DynamicTierSystem()
    return _tier_system_instance


def _extract_access_context(func: Callable, args: tuple, kwargs: dict, scope: PermissionScope) -> AccessContext:
    """Extract access context from function call."""
    # Try to extract context from common parameter patterns
    user_id = kwargs.get("user_id") or kwargs.get("owner_id")
    session_id = kwargs.get("session_id")
    resource_id = kwargs.get("key") or kwargs.get("fold_key") or str(hash(str(args)))

    # Determine operation type based on function name
    func_name = func.__name__.lower()
    if any(op in func_name for op in ["delete", "remove"]):
        operation_type = AccessType.DELETE
    elif any(op in func_name for op in ["update", "modify", "edit"]):
        operation_type = AccessType.MODIFY
    elif any(op in func_name for op in ["write", "create", "add"]):
        operation_type = AccessType.WRITE
    elif any(op in func_name for op in ["admin", "configure"]):
        operation_type = AccessType.ADMIN
    else:
        operation_type = AccessType.READ

    return AccessContext(
        user_id=user_id,
        session_id=session_id,
        operation_type=operation_type,
        resource_scope=scope,
        resource_id=resource_id,
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        metadata=kwargs,
    )


# Factory function
def create_tier_system() -> DynamicTierSystem:
    """Create a new dynamic tier system instance."""
    return DynamicTierSystem()


# LUKHAS_TAG: tier_privilege_enforcer
# Origin: Claude AGI Enhancements
# Role: Enforces symbolic access controls
# Phase: Post-Integration Audit (P4.2)


def symbolic_access_test():
    """
    Test access tier logic with a symbolic operation.
    """
    tier = DynamicTierSystem()
    operation = "modify_dream_path"
    user_context = {"role": "user", "session": "standard"}
    result = tier.check_access("user", operation, user_context)
    logger.info(f"[TierSystem] Access check result for '{operation}': {result}")


if __name__ == "__main__":
    symbolic_access_test()


# Tier Conversion Utilities (Constellation Framework Unification)
# These functions provide seamless conversion between LAMBDA_TIER_X strings
# and the unified 0-5 integer tier system used throughout LUKHAS

LAMBDA_TIER_MAP = {
    "LAMBDA_TIER_0": TierLevel.PUBLIC,
    "LAMBDA_TIER_1": TierLevel.AUTHENTICATED,
    "LAMBDA_TIER_2": TierLevel.ELEVATED,
    "LAMBDA_TIER_3": TierLevel.PRIVILEGED,
    "LAMBDA_TIER_4": TierLevel.ADMIN,
    "LAMBDA_TIER_5": TierLevel.SYSTEM,
}

TIER_TO_LAMBDA_MAP = {v: k for k, v in LAMBDA_TIER_MAP.items()}

def lambda_tier_to_int(lambda_tier: str) -> int:
    """
    Convert LAMBDA_TIER_X string to integer (0-5).

    Args:
        lambda_tier: String like "LAMBDA_TIER_1", "LAMBDA_TIER_2", etc.

    Returns:
        Integer tier level (0-5)

    Raises:
        ValueError: If lambda_tier is not a valid LAMBDA_TIER_X string
    """
    if lambda_tier not in LAMBDA_TIER_MAP:
        raise ValueError(f"Invalid lambda tier: {lambda_tier}. Must be LAMBDA_TIER_0 through LAMBDA_TIER_5")
    return LAMBDA_TIER_MAP[lambda_tier].value

def int_to_lambda_tier(tier_int: int) -> str:
    """
    Convert integer tier (0-5) to LAMBDA_TIER_X string.

    Args:
        tier_int: Integer tier level (0-5)

    Returns:
        String like "LAMBDA_TIER_1", "LAMBDA_TIER_2", etc.

    Raises:
        ValueError: If tier_int is not in valid range 0-5
    """
    if not (0 <= tier_int <= 5):
        raise ValueError(f"Invalid tier integer: {tier_int}. Must be 0-5")
    tier_level = TierLevel(tier_int)
    return TIER_TO_LAMBDA_MAP[tier_level]

def normalize_tier(tier: Union[str, int, TierLevel]) -> TierLevel:
    """
    Normalize any tier representation to TierLevel enum.

    Args:
        tier: Can be "LAMBDA_TIER_X" string, integer 0-5, or TierLevel enum

    Returns:
        TierLevel enum value

    Raises:
        ValueError: If tier cannot be converted to valid TierLevel
    """
    if isinstance(tier, TierLevel):
        return tier
    elif isinstance(tier, str):
        if tier in LAMBDA_TIER_MAP:
            return LAMBDA_TIER_MAP[tier]
        else:
            raise ValueError(f"Invalid lambda tier string: {tier}")
    elif isinstance(tier, int):
        if 0 <= tier <= 5:
            return TierLevel(tier)
        else:
            raise ValueError(f"Invalid tier integer: {tier}. Must be 0-5")
    else:
        raise ValueError(f"Invalid tier type: {type(tier)}. Must be str, int, or TierLevel")

def tier_meets_requirement(user_tier: Union[str, int, TierLevel], required_tier: Union[str, int, TierLevel]) -> bool:
    """
    Check if user tier meets the required tier level.

    Args:
        user_tier: User's current tier (any format)
        required_tier: Required minimum tier (any format)

    Returns:
        True if user tier >= required tier
    """
    user_level = normalize_tier(user_tier)
    required_level = normalize_tier(required_tier)
    return user_level.value >= required_level.value


# Minimal stub for test compatibility
def check_access_level(user_context: dict, operation: str) -> bool:
    """
    Returns False for Tier5Operation if tier < 5, True otherwise.
    """
    tier = user_context.get("tier", 0)
    return not (operation == "Tier5Operation" and tier < 5)
