#!/usr/bin/env python3
import logging
import streamlit as st
import time
from consciousness.qi import qi
logger = logging.getLogger(__name__)
"""
════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - IDENTITY INTEGRATION MODULE
║ Provides identity integration utilities for tier-gated access control
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠═══════════════════════════════════════════════════════════════════════════════
║ Module: identity_integration.py
║ Path: lukhas/core/identity_integration.py
║ Version: 1.0.0 | Created: 2025-07-26 | Modified: 2025-07-26
║ Authors: LUKHAS AI Core Team
╠═══════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠═══════════════════════════════════════════════════════════════════════════════
║ This module provides utilities for integrating the identity system with
║ tier-based access control across all LUKHAS modules. It includes decorators,
║ context managers, and helper functions for identity validation.
╚═══════════════════════════════════════════════════════════════════════════════
"""

import functools
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Optional, Union

import structlog

logger = structlog.get_logger(__name__)

# Try to import identity client
try:
    from lukhas.governance.identity.interface import IdentityClient

    IDENTITY_AVAILABLE = True
except ImportError:
    IDENTITY_AVAILABLE = False
    logger.warning("Identity system not available - running without identity validation")

# Global identity client instance
_identity_client: Optional["IdentityClient"] = None

# Lambda Tier Definitions
LAMBDA_TIERS = [
    "LAMBDA_TIER_0",  # Base access
    "LAMBDA_TIER_1",  # Basic features
    "LAMBDA_TIER_2",  # Standard features
    "LAMBDA_TIER_3",  # Enhanced features
    "LAMBDA_TIER_4",  # Advanced features
    "LAMBDA_TIER_5",  # Full access
]


class TierMappingConfig:
    """Centralized tier mapping configuration for unifying different tier systems."""

    # Map Oneiric database tiers (1-5) to LAMBDA_TIER system
    ONEIRIC_TO_LAMBDA = {
        1: "LAMBDA_TIER_1",
        2: "LAMBDA_TIER_2",
        3: "LAMBDA_TIER_3",
        4: "LAMBDA_TIER_4",
        5: "LAMBDA_TIER_5",
    }

    # Map EmotionalTier (T0-T5) to LAMBDA_TIER system
    EMOTIONAL_TO_LAMBDA = {
        "T0": "LAMBDA_TIER_5",  # System access maps to highest tier
        "T1": "LAMBDA_TIER_1",
        "T2": "LAMBDA_TIER_2",
        "T3": "LAMBDA_TIER_3",
        "T4": "LAMBDA_TIER_4",
        "T5": "LAMBDA_TIER_5",
    }

    # Reverse mappings
    LAMBDA_TO_ONEIRIC = {v: k for k, v in ONEIRIC_TO_LAMBDA.items()}
    LAMBDA_TO_EMOTIONAL = {v: k for k, v in EMOTIONAL_TO_LAMBDA.items()}

    @classmethod
    def normalize_tier(cls, tier: Union[str, int, "Enum"]) -> str:
        """Normalize any tier representation to LAMBDA_TIER format.

        Args:
            tier: Tier in any supported format (str, int, Enum)

        Returns:
            str: Normalized LAMBDA_TIER string
        """
        # Handle Enum types
        if hasattr(tier, "value"):
            tier = tier.value

        if isinstance(tier, str):
            # Already in LAMBDA_TIER format
            if tier in LAMBDA_TIERS:
                return tier
            # EmotionalTier format
            if tier in cls.EMOTIONAL_TO_LAMBDA:
                return cls.EMOTIONAL_TO_LAMBDA[tier]
            # Try to extract tier number
            if tier.startswith("TIER_"):
                try:
                    num = int(tier.split("_")[1])
                    return f"LAMBDA_TIER_{num}"
                except BaseException:
                    pass
        elif isinstance(tier, int):
            # Oneiric database tier
            if tier in cls.ONEIRIC_TO_LAMBDA:
                return cls.ONEIRIC_TO_LAMBDA[tier]
            # Direct tier number
            if 0 <= tier <= 5:
                return f"LAMBDA_TIER_{tier}"

        # Default to base tier
        logger.warning(f"Unknown tier format: {tier}, defaulting to LAMBDA_TIER_0")
        return "LAMBDA_TIER_0"

    @classmethod
    def get_tier_index(cls, tier: Union[str, int]) -> int:
        """Get numeric index for tier comparison."""
        normalized = cls.normalize_tier(tier)
        try:
            return LAMBDA_TIERS.index(normalized)
        except ValueError:
            return 0  # Default to base tier


def get_identity_client() -> Optional["IdentityClient"]:
    """Get or create the global identity client instance."""
    global _identity_client

    if not IDENTITY_AVAILABLE:
        return None

    if _identity_client is None:
        try:
            _identity_client = IdentityClient()
            logger.info("Identity client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize identity client: {e}")
            return None

    return _identity_client


def require_identity(
    required_tier: Union[str, int] = "LAMBDA_TIER_1",
    check_consent: Optional[str] = None,
):
    """
    Decorator that enforces identity validation and tier requirements.

    Args:
        required_tier: Minimum tier level required (default: LAMBDA_TIER_1)
        check_consent: Optional consent action to check (e.g., "memory_access")

    Example:
        @require_identity(required_tier="LAMBDA_TIER_3", check_consent="dream_generation")

        def generate_dream(user_id: str, dream_params: dict):
            # Function implementation
            pass
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Normalize the required tier
            normalized_tier = TierMappingConfig.normalize_tier(required_tier)

            # Extract user_id from various possible locations
            user_id = kwargs.get("user_id") or kwargs.get("lambda_id") or kwargs.get("identity_legacy")

            # Try to get from first positional arg if it looks like a user ID
            if not user_id and args and isinstance(args[0], str) and args[0].startswith("Λ"):
                user_id = args[0]

            # Check for Oneiric-style user object
            if not user_id and "user" in kwargs:
                user_obj = kwargs["user"]
                if hasattr(user_obj, "identity_legacy"):
                    user_id = user_obj.lukhas_id
                elif hasattr(user_obj, "id"):
                    user_id = user_obj.id

            if not user_id:
                logger.error(f"No user_id provided for {func.__name__}")
                raise ValueError("user_id is required for identity validation")

            # Get identity client
            client = get_identity_client()
            if not client:
                logger.warning(f"Identity validation skipped for {func.__name__} - client not available")
                return func(*args, **kwargs)

            # Verify tier access
            if not client.verify_user_access(user_id, normalized_tier):
                logger.warning(
                    f"Access denied for {func.__name__}",
                    user_id=user_id,
                    required_tier=normalized_tier,
                )
                raise PermissionError(f"Insufficient tier level. Required: {normalized_tier}")

            # Check consent if specified
            if check_consent and not client.check_consent(user_id, check_consent):
                logger.warning(
                    f"Consent denied for {func.__name__}",
                    user_id=user_id,
                    consent_action=check_consent,
                )
                raise PermissionError(f"Consent not granted for: {check_consent}")

            # Log activity
            client.log_activity(
                activity_type=func.__name__,
                user_id=user_id,
                metadata={
                    "module": func.__module__,
                    "required_tier": normalized_tier,
                    "original_tier": str(required_tier),
                    "consent_checked": check_consent,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )

            # Execute function
            return func(*args, **kwargs)

        return wrapper

    return decorator


class IdentityContext:
    """
    Context manager for identity-aware operations.

    Example:
        with IdentityContext(user_id, "LAMBDA_TIER_2") as ctx:
            if ctx.has_access:
                # Perform tier-gated operations
                pass
    """

    def __init__(self, user_id: str, required_tier: Union[str, int] = "LAMBDA_TIER_1"):
        self.user_id = user_id
        self.required_tier = TierMappingConfig.normalize_tier(required_tier)
        self.client = get_identity_client()
        self.has_access = False

    def __enter__(self):
        if self.client:
            self.has_access = self.client.verify_user_access(self.user_id, self.required_tier)
            if self.has_access:
                self.client.log_activity(
                    "context_enter",
                    self.user_id,
                    {"required_tier": self.required_tier},
                )
        else:
            # No client available, grant access by default
            self.has_access = True

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.client and self.has_access:
            self.client.log_activity(
                "context_exit",
                self.user_id,
                {
                    "required_tier": self.required_tier,
                    "error": str(exc_val) if exc_val else None,
                },
            )


def validate_and_log(user_id: str, activity: str, metadata: Optional[dict[str, Any]] = None) -> bool:
    """
    Quick validation and logging helper.

    Args:
        user_id: User's lambda ID
        activity: Activity to log
        metadata: Optional metadata

    Returns:
        bool: True if user has basic access
    """
    client = get_identity_client()
    if not client:
        return True  # No validation if client unavailable

    if client.verify_user_access(user_id, "LAMBDA_TIER_1"):
        client.log_activity(activity, user_id, metadata or {})
        return True

    return False


# Example integration patterns for different modules


class ModuleIntegrationExamples:
    """Examples of how to integrate identity into various module types."""

    @staticmethod
    @require_identity(required_tier="LAMBDA_TIER_2", check_consent="memory_access")
    def memory_operation_example(user_id: str, memory_key: str, operation: str):
        """Example of tier-gated memory operation."""
        logger.info(f"Performing memory {operation} for user {user_id} on key {memory_key}")
        # Actual memory operation would go here
        return {"status": "success", "operation": operation}

    @staticmethod
    @require_identity(required_tier="LAMBDA_TIER_3", check_consent="dream_generation")
    def dream_generation_example(user_id: str, dream_params: dict[str, Any]):
        """Example of tier-gated dream generation."""
        logger.info(f"Generating dream for user {user_id} with params {dream_params}")
        # Actual dream generation would go here
        return {"dream_id": "dream_123", "status": "generated"}

    @staticmethod
    @require_identity(required_tier="LAMBDA_TIER_4")
    def qi_operation_example(user_id: str, qi_like_state: Any):
        """Example of high-tier quantum operation."""
        logger.info(f"Performing quantum operation for user {user_id}")
        # Actual quantum operation would go here
        return {"qi_result": "entangled"}

    @staticmethod
    def context_manager_example(user_id: str, data: dict[str, Any]):
        """Example using context manager for tier validation."""
        # Basic tier operations
        with IdentityContext(user_id, "LAMBDA_TIER_1") as ctx:
            if ctx.has_access:
                logger.info(f"User {user_id} has basic access")
                # Perform basic operations

        # Advanced tier operations
        with IdentityContext(user_id, "LAMBDA_TIER_3") as ctx:
            if ctx.has_access:
                logger.info(f"User {user_id} has advanced access")
                # Perform advanced operations
            else:
                logger.warning(f"User {user_id} lacks advanced access")
                # Fall back to basic operations


# Export key functions and classes
__all__ = [
    "LAMBDA_TIERS",
    "IdentityContext",
    "ModuleIntegrationExamples",
    "TierMappingConfig",
    "get_identity_client",
    "require_identity",
    "validate_and_log",
]