"""
LUKHAS Global Tier System Definitions

This module provides a single source of truth for the global LUKHAS tier system,
intended for cross-module integration and tier mapping.
"""
from enum import Enum


class TierMappingError(ValueError):
    """Custom exception for errors in mapping local tiers to global tiers."""

    pass


class GlobalTier(Enum):
    """
    Global LUKHAS Tier System.

    This enum defines the standardized, hierarchical tier levels with increasing
    privileges across the entire LUKHAS system.
    """

    PUBLIC = 0
    AUTHENTICATED = 1
    ELEVATED = 2
    PRIVILEGED = 3
    ADMIN = 4
    SYSTEM = 5


def get_tier(user_id: str) -> int:
    """
    Returns the tier of the user.
    This is a stub function for backward compatibility.
    """
    return 1
