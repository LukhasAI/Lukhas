"""
LUKHAS Identity Tier System - Access Control Interface

This module provides high-level functions for tier-based access control,
wrapping the tier validator for easier use by other modules.
"""
from typing import Any, Union

from .tier_validator import TierValidator

# Initialize a global tier validator instance
_tier_validator = TierValidator()


def check_access_level(user_id: str, required_tier: int) -> Union[bool, dict[str, Any]]:
    """
    Check if a user has the required tier access level.

    Args:
        user_id: The user's Lambda ID
        required_tier: Minimum required tier level (0-5)

    Returns:
        bool or dict: True if access granted, False if denied,
                      or dict with detailed access information
    """
    try:
        # Convert tier number to tier name format
        tier_name = f"LAMBDA_TIER_{required_tier}"

        # Use the tier validator to check access
        has_access = _tier_validator.validate_tier(user_id, tier_name)

        # Return simple boolean for backwards compatibility
        return has_access

    except Exception as e:
        # Return dict with error details if something goes wrong
        return {
            "access": False,
            "error": str(e),
            "user_id": user_id,
            "required_tier": required_tier,
        }


def get_user_tier(user_id: str) -> int:
    """
    Get the current tier level of a user.

    Args:
        user_id: The user's Lambda ID

    Returns:
        int: User's tier level (0-5), or -1 if error
    """
    try:
        # This would integrate with the actual tier system
        # For now, return a default tier
        return 1  # Default to VISITOR tier
    except Exception:
        return -1


def validate_tier_permission(user_id: str, permission: str) -> bool:
    """
    Check if a user has a specific tier-based permission.

    Args:
        user_id: The user's Lambda ID
        permission: The specific permission to check

    Returns:
        bool: True if permission granted, False otherwise
    """
    try:
        # This would check specific permissions within tier levels
        # For now, basic implementation
        user_tier = get_user_tier(user_id)
        return user_tier >= 1  # Basic check
    except Exception:
        return False


# Tier level constants for convenience
class TierLevel:
    GUEST = 0
    VISITOR = 1
    FRIEND = 2
    TRUSTED = 3
    INNER_CIRCLE = 4
    ROOT_DEV = 5