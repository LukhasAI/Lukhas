"""
LUKHAS Governance Identity Core Module - Bridge Package
======================================================

This module provides core identity management capabilities for the LUKHAS AI system.
This is a bridge module for backwards compatibility with candidate modules.
"""

# Import our stub implementations
from .id_service import IdentityManager, get_identity_manager
from .user_tier_mapping import TierLevel, get_user_tier, map_user_to_tier

# Make them available at package level
__all__ = [
    "IdentityManager",
    "TierLevel",
    "get_identity_manager",
    "get_user_tier",
    "map_user_to_tier",
]
