#!/usr/bin/env python3
"""
════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - IDENTITY-AWARE BASE CLASSES
║ Base classes for services that require user identity and tier validation
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠═══════════════════════════════════════════════════════════════════════════════
║ Module: identity_aware_base.py
║ Path: lukhas/core/identity_aware_base.py
║ Version: 1.0.0 | Created: 2025-07-26 | Modified: 2025-07-26
║ Authors: LUKHAS AI Core Team
╠═══════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠═══════════════════════════════════════════════════════════════════════════════
║ Provides base classes for all LUKHAS services that need user identity
║ integration. This ensures consistent tier validation, activity logging,
║ and user context management across all modules.
╚═══════════════════════════════════════════════════════════════════════════════
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Callable, Optional

import structlog

from lukhas.governance.identity.interface import IdentityClient

logger = structlog.get_logger(__name__)


class IdentityAwareService(ABC):
    """
    Base class for all LUKHAS services that require user identity integration.

    This class provides:
    - Automatic identity client initialization
    - Tier validation helpers
    - Activity logging with user context
    - Consent checking utilities
    - User-specific caching support
    """

    def __init__(self, service_name: str, fallback_mode: bool = False):
        """
        Initialize identity-aware service.

        Args:
            service_name: Name of the service for logging
            fallback_mode: Whether to use fallback identity client if unavailable
        """
        self.service_name = service_name
        self.fallback_mode = fallback_mode
        self._identity_client = None
        self._user_cache: dict[str, dict[str, Any]] = {}
        self._initialize_identity()

    def _initialize_identity(self):
        """Initialize identity client with fallback handling."""
        try:
            self._identity_client = IdentityClient()
            logger.info(f"Identity client initialized for {self.service_name}")
        except Exception as e:
            if self.fallback_mode:
                logger.warning(
                    f"Identity client unavailable for {self.service_name}, using fallback",
                    error=str(e),
                )
                self._identity_client = self._create_fallback_client()
            else:
                raise RuntimeError(f"Failed to initialize identity client: {e}")

    def _create_fallback_client(self):
        """Create a fallback identity client for development."""

        class FallbackIdentityClient:
            def verify_user_access(self, user_id, tier):
                logger.debug(f"FALLBACK: Granting {tier} access to {user_id}")
                return True

            def check_consent(self, user_id, action):
                logger.debug(f"FALLBACK: Granting consent for {action} to {user_id}")
                return True

            def log_activity(self, activity, user_id, metadata):
                logger.debug(f"FALLBACK: {activity}", user_id=user_id, metadata=metadata)

        return FallbackIdentityClient()

    @property
    def identity_client(self) -> IdentityClient:
        """Get the identity client instance."""
        if not self._identity_client:
            self._initialize_identity()
        return self._identity_client

    def validate_user_tier(self, user_id: str, required_tier: str) -> bool:
        """
        Validate that a user has the required tier level.

        Args:
            user_id: The user's Lambda ID
            required_tier: Required tier (e.g., "LAMBDA_TIER_2")

        Returns:
            bool: True if user has sufficient access
        """
        try:
            return self.identity_client.verify_user_access(user_id, required_tier)
        except Exception as e:
            logger.error(
                f"Tier validation error in {self.service_name}",
                user_id=user_id,
                required_tier=required_tier,
                error=str(e),
            )
            return False

    def check_user_consent(self, user_id: str, action: str, scope: str = "default") -> bool:
        """
        Check if user has given consent for an action.

        Args:
            user_id: The user's Lambda ID
            action: The action requiring consent
            scope: Consent scope

        Returns:
            bool: True if consent is granted
        """
        return self.identity_client.check_consent(user_id, action, scope)

    def log_user_activity(
        self,
        user_id: str,
        activity_type: str,
        metadata: Optional[dict[str, Any]] = None,
    ):
        """
        Log user activity with service context.

        Args:
            user_id: The user's Lambda ID
            activity_type: Type of activity
            metadata: Additional activity metadata
        """
        enhanced_metadata = {
            "service": self.service_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **(metadata or {}),
        }

        self.identity_client.log_activity(activity_type, user_id, enhanced_metadata)

    def get_user_context(self, user_id: str) -> Optional[dict[str, Any]]:
        """
        Get cached user context or fetch from identity service.

        Args:
            user_id: The user's Lambda ID

        Returns:
            Dict containing user tier, permissions, and metadata
        """
        if user_id in self._user_cache:
            return self._user_cache[user_id]

        try:
            from lukhas.governance.identity.core.user_tier_mapping import (
                get_tier_mapping_service,
            )

            service = get_tier_mapping_service()
            profile = service.get_user_profile(user_id)

            if profile:
                self._user_cache[user_id] = profile
                return profile
        except Exception as e:
            logger.error("Failed to get user context", user_id=user_id, error=str(e))

        return None

    def clear_user_cache(self, user_id: Optional[str] = None):
        """Clear user context cache."""
        if user_id:
            self._user_cache.pop(user_id, None)
        else:
            self._user_cache.clear()

    @abstractmethod
    def get_service_info(self) -> dict[str, Any]:
        """
        Get service information including capabilities and tier requirements.

        Must be implemented by subclasses to describe their tier requirements.
        """


class TieredOperationMixin:
    """
    Mixin class that provides tier-based operation variants.

    Allows services to provide different functionality based on user tier.
    """

    def execute_tiered_operation(
        self,
        user_id: str,
        operation_map: dict[str, Callable],
        default_operation: Optional[Callable] = None,
        **kwargs,
    ) -> Any:
        """
        Execute different operations based on user tier.

        Args:
            user_id: The user's Lambda ID
            operation_map: Map of tier names to operations
            default_operation: Fallback operation if no tier match
            **kwargs: Arguments passed to the operation

        Returns:
            Result of the executed operation

        Example:
            result = self.execute_tiered_operation(
                user_id,
                {
                    "LAMBDA_TIER_1": self.basic_search,
                    "LAMBDA_TIER_2": self.advanced_search,
                    "LAMBDA_TIER_3": self.premium_search
                },
                query=query
            )
        """
        if not hasattr(self, "get_user_context"):
            raise AttributeError("TieredOperationMixin requires IdentityAwareService")

        user_context = self.get_user_context(user_id)
        if not user_context:
            if default_operation:
                return default_operation(**kwargs)
            raise PermissionError(f"No user context found for {user_id}")

        user_tier = user_context.get("current_tier", "LAMBDA_TIER_0")

        # Find the highest tier operation the user can access
        tier_levels = [
            "LAMBDA_TIER_5",
            "LAMBDA_TIER_4",
            "LAMBDA_TIER_3",
            "LAMBDA_TIER_2",
            "LAMBDA_TIER_1",
            "LAMBDA_TIER_0",
        ]

        user_tier_index = tier_levels.index(user_tier) if user_tier in tier_levels else -1

        for tier in tier_levels[user_tier_index:]:
            if tier in operation_map:
                operation = operation_map[tier]
                logger.debug(
                    f"Executing {tier} operation",
                    user_id=user_id,
                    operation=operation.__name__,
                )
                return operation(**kwargs)

        if default_operation:
            return default_operation(**kwargs)

        raise PermissionError(f"No suitable operation found for tier {user_tier}")


class ResourceLimitedService(IdentityAwareService):
    """
    Extended base class for services that need resource limits based on tier.
    """

    # Default resource limits by tier
    DEFAULT_RESOURCE_LIMITS = {
        "LAMBDA_TIER_0": {
            "requests_per_minute": 10,
            "storage_mb": 10,
            "compute_units": 1,
        },
        "LAMBDA_TIER_1": {
            "requests_per_minute": 60,
            "storage_mb": 100,
            "compute_units": 5,
        },
        "LAMBDA_TIER_2": {
            "requests_per_minute": 300,
            "storage_mb": 1000,
            "compute_units": 20,
        },
        "LAMBDA_TIER_3": {
            "requests_per_minute": 1000,
            "storage_mb": 10000,
            "compute_units": 100,
        },
        "LAMBDA_TIER_4": {
            "requests_per_minute": 10000,
            "storage_mb": 100000,
            "compute_units": 1000,
        },
        "LAMBDA_TIER_5": {
            "requests_per_minute": float("inf"),
            "storage_mb": float("inf"),
            "compute_units": float("inf"),
        },
    }

    def __init__(self, service_name: str, custom_limits: Optional[dict] = None, **kwargs):
        super().__init__(service_name, **kwargs)
        self.resource_limits = custom_limits or self.DEFAULT_RESOURCE_LIMITS
        self._user_usage: dict[str, dict[str, Any]] = {}

    def get_user_resource_limits(self, user_id: str) -> dict[str, Any]:
        """Get resource limits for a user based on their tier."""
        user_context = self.get_user_context(user_id)
        if not user_context:
            return self.resource_limits.get("LAMBDA_TIER_0", {})

        user_tier = user_context.get("current_tier", "LAMBDA_TIER_0")
        return self.resource_limits.get(user_tier, self.resource_limits["LAMBDA_TIER_0"])

    def check_resource_availability(self, user_id: str, resource_type: str, amount: float = 1.0) -> bool:
        """
        Check if user has available resources.

        Args:
            user_id: The user's Lambda ID
            resource_type: Type of resource (e.g., "compute_units")
            amount: Amount of resource needed

        Returns:
            bool: True if resource is available
        """
        limits = self.get_user_resource_limits(user_id)
        limit = limits.get(resource_type, 0)

        if limit == float("inf"):
            return True

        # Check current usage (simplified - real implementation would track over time)
        current_usage = self._user_usage.get(user_id, {}).get(resource_type, 0)
        return (current_usage + amount) <= limit

    def consume_resource(self, user_id: str, resource_type: str, amount: float = 1.0) -> bool:
        """
        Consume user resources if available.

        Args:
            user_id: The user's Lambda ID
            resource_type: Type of resource
            amount: Amount to consume

        Returns:
            bool: True if resource was consumed
        """
        if not self.check_resource_availability(user_id, resource_type, amount):
            self.log_user_activity(
                user_id,
                "resource_limit_exceeded",
                {"resource_type": resource_type, "requested": amount},
            )
            return False

        if user_id not in self._user_usage:
            self._user_usage[user_id] = {}

        current = self._user_usage[user_id].get(resource_type, 0)
        self._user_usage[user_id][resource_type] = current + amount

        return True


# Decorator for methods that require tier validation


def tier_required(required_tier: str):
    """
    Decorator for methods that require tier validation.

    Use this on methods of IdentityAwareService subclasses.

    Args:
        required_tier: The minimum tier required (e.g., "LAMBDA_TIER_2")

    Example:
        @tier_required("LAMBDA_TIER_3")

        def premium_feature(self, user_id: str, **kwargs):
            # Method implementation
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, user_id: str, *args, **kwargs):
            if not isinstance(self, IdentityAwareService):
                raise TypeError("tier_required can only be used on IdentityAwareService methods")

            if not self.validate_user_tier(user_id, required_tier):
                self.log_user_activity(
                    user_id,
                    "access_denied",
                    {"method": func.__name__, "required_tier": required_tier},
                )
                raise PermissionError(f"This operation requires {required_tier} access")

            return func(self, user_id, *args, **kwargs)

        return wrapper

    return decorator
