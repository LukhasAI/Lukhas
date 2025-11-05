#!/usr/bin/env python3

"""
════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - TIER UNIFICATION ADAPTER
║ Adapts different tier systems (Oneiric, EmotionalTier) to unified LAMBDA_TIER
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠════════════════════════════════════════════════════════════════════════════════
║ Module: tier_unification_adapter.py
║ Path: lukhas/core/tier_unification_adapter.py
║ Version: 1.0.0 | Created: 2025-07-26
║ Authors: LUKHAS AI Core Team
╠════════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠════════════════════════════════════════════════════════════════════════════════
║ This adapter provides seamless integration between different tier systems:
║ - Oneiric Dream Engine (database tiers 1-5)
║ - DreamSeed Emotions (EmotionalTier T0-T5)
║ - Central Identity System (LAMBDA_TIER_0 through LAMBDA_TIER_5)
╚════════════════════════════════════════════════════════════════════════════════
"""

from __future__ import annotations

import logging

from abc import ABC, abstractmethod
from functools import wraps
from typing import Any, Callable, Union

import structlog
from core.identity_integration import TierMappingConfig, get_identity_client

logger = logging.getLogger(__name__)



logger = structlog.get_logger(__name__)


class TierSystemAdapter(ABC):
    """Abstract base class for tier system adapters."""

    @abstractmethod
    def to_lambda_tier(self, tier: Any) -> str:
        """Convert system-specific tier to LAMBDA_TIER format."""

    @abstractmethod
    def from_lambda_tier(self, lambda_tier: str) -> Any:
        """Convert LAMBDA_TIER to system-specific format."""

    @abstractmethod
    def validate_access(self, user_id: str, required_tier: Any) -> bool:
        """Validate user access for system-specific tier."""


class OneiricTierAdapter(TierSystemAdapter):
    """Adapter for Oneiric Dream Engine tier system."""

    def __init__(self):
        self.client = get_identity_client()

    def to_lambda_tier(self, tier: Union[int, str]) -> str:
        """Convert Oneiric tier (1-5) to LAMBDA_TIER."""
        if isinstance(tier, str) and tier.isdigit():
            tier = int(tier)
        return TierMappingConfig.normalize_tier(tier)

    def from_lambda_tier(self, lambda_tier: str) -> int:
        """Convert LAMBDA_TIER to Oneiric tier (1-5)."""
        mapping = TierMappingConfig.LAMBDA_TO_ONEIRIC
        # Special handling for LAMBDA_TIER_0
        if lambda_tier == "LAMBDA_TIER_0":
            return 1  # Map base tier to Oneiric tier 1
        return mapping.get(lambda_tier, 1)

    def validate_access(self, user_id: str, required_tier: Union[int, str]) -> bool:
        """Validate user access using central identity system."""
        if not self.client:
            logger.warning("Identity client not available, granting access by default")
            return True

        lambda_tier = self.to_lambda_tier(required_tier)
        return self.client.verify_user_access(user_id, lambda_tier)

    def create_middleware(self, required_tier: int):
        """Create FastAPI middleware for Oneiric endpoints."""

        def middleware(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Extract user from Oneiric auth pattern
                user = kwargs.get("user")
                if not user:
                    raise ValueError("User object required for Oneiric middleware")

                user_id = getattr(user, "identity_legacy", None) or getattr(user, "id", None)
                if not user_id:
                    raise ValueError("User ID not found in user object")

                # Validate tier access
                if not self.validate_access(user_id, required_tier):
                    from fastapi import HTTPException, status

                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Insufficient tier level. Required: {required_tier}",
                    )

                return await func(*args, **kwargs)

            return wrapper

        return middleware


class EmotionalTierAdapter(TierSystemAdapter):
    """Adapter for DreamSeed Emotional tier system."""

    def __init__(self):
        self.client = get_identity_client()
        # Import EmotionalTier enum if available
        try:
            from emotion.dreamseed_upgrade import EmotionalTier

            self.EmotionalTier = EmotionalTier
        except ImportError:
            self.EmotionalTier = None
            logger.warning("EmotionalTier not available")

    def to_lambda_tier(self, tier: Union[str, EmotionalTier]) -> str:
        """Convert EmotionalTier (T0-T5) to LAMBDA_TIER."""
        if self.EmotionalTier and hasattr(tier, "name"):
            # Handle EmotionalTier enum
            tier = tier.name
        return TierMappingConfig.normalize_tier(str(tier))

    def from_lambda_tier(self, lambda_tier: str) -> str:
        """Convert LAMBDA_TIER to EmotionalTier format."""
        mapping = TierMappingConfig.LAMBDA_TO_EMOTIONAL
        return mapping.get(lambda_tier, "T1")

    def validate_access(self, user_id: str, required_tier: Union[str, EmotionalTier]) -> bool:
        """Validate user access using central identity system."""
        if not self.client:
            logger.warning("Identity client not available, granting access by default")
            return True

        lambda_tier = self.to_lambda_tier(required_tier)
        return self.client.verify_user_access(user_id, lambda_tier)

    def get_emotional_access_matrix(self, user_id: str) -> dict[str, Any]:
        """Get user's emotional access matrix based on their tier."""
        if not self.client:
            # Return default T1 access
            return {
                "memory_depth": 24,
                "symbolic_access": False,
                "dream_influence": False,
                "co_dreaming": False,
                "temporal_range": "recent",
                "emotional_granularity": "basic",
            }

        # Get user's lambda tier
        user_tier = "LAMBDA_TIER_1"  # Default
        try:
            from governance.identity.core.user_tier_mapping import get_user_tier

            user_tier = get_user_tier(user_id)
        except BaseException:
            pass

        # Map to emotional tier
        emotional_tier = self.from_lambda_tier(user_tier)

        # Define access matrix
        access_matrices = {
            "T0": {  # System only
                "memory_depth": float("inf"),
                "symbolic_access": True,
                "dream_influence": True,
                "co_dreaming": True,
                "temporal_range": "unlimited",
                "emotional_granularity": "quantum",
            },
            "T1": {  # Basic
                "memory_depth": 24,
                "symbolic_access": False,
                "dream_influence": False,
                "co_dreaming": False,
                "temporal_range": "recent",
                "emotional_granularity": "basic",
            },
            "T2": {  # Standard
                "memory_depth": 168,
                "symbolic_access": False,
                "dream_influence": True,
                "co_dreaming": False,
                "temporal_range": "week",
                "emotional_granularity": "standard",
            },
            "T3": {  # Enhanced
                "memory_depth": 720,
                "symbolic_access": True,
                "dream_influence": True,
                "co_dreaming": False,
                "temporal_range": "month",
                "emotional_granularity": "enhanced",
            },
            "T4": {  # Advanced
                "memory_depth": 8760,
                "symbolic_access": True,
                "dream_influence": True,
                "co_dreaming": True,
                "temporal_range": "year",
                "emotional_granularity": "advanced",
            },
            "T5": {  # Full
                "memory_depth": float("inf"),
                "symbolic_access": True,
                "dream_influence": True,
                "co_dreaming": True,
                "temporal_range": "unlimited",
                "emotional_granularity": "full",
            },
        }

        return access_matrices.get(emotional_tier, access_matrices["T1"])


class UnifiedTierAdapter:
    """Central adapter that manages all tier system conversions."""

    def __init__(self):
        self.oneiric = OneiricTierAdapter()
        self.emotional = EmotionalTierAdapter()
        self.client = get_identity_client()

    def normalize_any_tier(self, tier: Any, system_hint: str | None = None) -> str:
        """
        Normalize any tier format to LAMBDA_TIER.

        Args:
            tier: Tier in any format
            system_hint: Optional hint about which system ("oneiric", "emotional")

        Returns:
            str: Normalized LAMBDA_TIER
        """
        # If system hint provided, use specific adapter
        if system_hint:
            if system_hint.lower() == "oneiric":
                return self.oneiric.to_lambda_tier(tier)
            elif system_hint.lower() == "emotional":
                return self.emotional.to_lambda_tier(tier)

        # Otherwise use general normalization
        return TierMappingConfig.normalize_tier(tier)

    def create_unified_decorator(self, required_tier: Any, system: str | None = None):
        """
        Create a unified decorator that works with any tier system.

        Args:
            required_tier: Required tier in any format
            system: Optional system hint

        Example:
            @unified_adapter.create_unified_decorator(3, "oneiric")
            async def dream_endpoint(user: User):
                pass

            @unified_adapter.create_unified_decorator("T3", "emotional")
            async def emotion_endpoint(user_id: str):
                pass
        """
        normalized_tier = self.normalize_any_tier(required_tier, system)

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Try multiple user ID extraction strategies
                user_id = None

                # Strategy 1: Direct user_id parameter
                user_id = kwargs.get("user_id") or kwargs.get("lambda_id")

                # Strategy 2: User object (Oneiric style)
                if not user_id and "user" in kwargs:
                    user_obj = kwargs["user"]
                    user_id = getattr(user_obj, "identity_legacy", None) or getattr(user_obj, "id", None)

                # Strategy 3: First positional arg
                if not user_id and args and isinstance(args[0], str) and args[0].startswith("Λ"):
                    user_id = args[0]

                if not user_id:
                    raise ValueError("Could not extract user ID from function arguments")

                # Use central identity validation
                if self.client and not self.client.verify_user_access(user_id, normalized_tier):
                    raise PermissionError(f"Insufficient tier level. Required: {normalized_tier}",
                    )

                return await func(*args, **kwargs)

            return wrapper

        return decorator


# Singleton instance
_unified_adapter: UnifiedTierAdapter | None = None


def get_unified_adapter() -> UnifiedTierAdapter:
    """Get or create the unified tier adapter instance."""
    global _unified_adapter
    if _unified_adapter is None:
        _unified_adapter = UnifiedTierAdapter()
    return _unified_adapter


# Convenience decorators


def oneiric_tier_required(tier: int):
    """Decorator for Oneiric Dream Engine tier requirements."""
    adapter = get_unified_adapter()
    return adapter.create_unified_decorator(tier, "oneiric")


def emotional_tier_required(tier: Union[str, EmotionalTier]):
    """Decorator for DreamSeed Emotional tier requirements."""
    adapter = get_unified_adapter()
    return adapter.create_unified_decorator(tier, "emotional")


class TierUnificationAdapter:
    """
    Main adapter class for tier system unification.

    This class provides a unified interface to work with different tier systems
    across the LUKHAS AI ecosystem.
    """

    def __init__(self, config: dict | None = None):
        """Initialize the tier unification adapter"""
        self.config = config or {}
        self.unified_adapter = get_unified_adapter()
        logger.info("TierUnificationAdapter initialized")

    def normalize_tier(self, tier: Any, source_system: str = "lambda") -> str:
        """Normalize a tier from any system to LAMBDA_TIER format"""
        return self.unified_adapter.normalize_tier(tier, source_system)

    def validate_access(self, user_id: str, required_tier: Any, system: str = "lambda") -> bool:
        """Validate user access for a given tier requirement"""
        try:
            normalized_tier = self.normalize_tier(required_tier, system)
            return self.unified_adapter.client.verify_user_access(user_id, normalized_tier)
        except Exception as e:
            logger.error(f"Access validation failed: {e}")
            return False

    def create_decorator(self, tier: Any, system: str = "lambda"):
        """Create a tier requirement decorator"""
        return self.unified_adapter.create_unified_decorator(tier, system)


# Export all classes and functions
__all__ = [
    "TierUnificationAdapter",
    "UnifiedTierAdapter",
    "emotional_tier_required",
    "get_unified_adapter",
    "oneiric_tier_required",
]

# Export all key components
__all__ = [
    "EmotionalTierAdapter",
    "OneiricTierAdapter",
    "TierSystemAdapter",
    "UnifiedTierAdapter",
    "emotional_tier_required",
    "get_unified_adapter",
    "oneiric_tier_required",
]
