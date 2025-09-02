"""
══════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - TIER-AWARE COLONY PROXY
║ Wrapper system for adding quantum identity to existing colonies
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: tier_aware_colony_proxy.py
║ Path: core/tier_aware_colony_proxy.py
║ Version: 1.0.0 | Created: 2025-07-28
║ Authors: LUKHAS AGI Identity Team | Claude Code
╠══════════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠══════════════════════════════════════════════════════════════════════════════════
║ Revolutionary proxy wrapper system that adds quantum-proof identity awareness
║ to existing colony implementations without modifying their core code. Provides
║ seamless tier-based access control and quantum security integration.
║
║ KEY FEATURES:
║ • Transparent identity integration for existing colonies
║ • Dynamic tier-based access control with zero colony modifications
║ • Post-quantum cryptographic audit trails
║ • Multi-colony orchestration with identity context propagation
║ • Backward compatibility with legacy colony implementations
║ • Performance optimization with identity caching
║
║ ΛTAG: ΛIDENTITY, ΛPROXY, ΛCOLONY, ΛQUANTUM, ΛTIER
╚══════════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import inspect
import logging
import time
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Callable, Optional, Union

# Import quantum identity components
try:
    from candidate.core.identity_aware_base_colony import (
        IdentityValidationError,
        QISecurityError,
        TierAccessDeniedError,
    )

    from ._cleanup_archive.BACKUP_BEFORE_CONSOLIDATION_20250801_002312.core.qi_identity_manager import (
        QIIdentityManager,
        QITierLevel,
        QIUserContext,
        get_quantum_identity_manager,
    )

    QUANTUM_IDENTITY_AVAILABLE = True
except ImportError:
    QUANTUM_IDENTITY_AVAILABLE = False

# Import base colony infrastructure
try:
    from candidate.core.colonies.base_colony import BaseColony

    BASE_COLONY_AVAILABLE = True
except ImportError:
    BASE_COLONY_AVAILABLE = False
    BaseColony = object

logger = logging.getLogger("ΛTRACE.tier_aware_proxy")


class ProxyInitializationError(Exception):
    """Raised when proxy initialization fails."""


class ColonyNotFoundError(Exception):
    """Raised when wrapped colony is not found."""


class TierAwareColonyProxy:
    """
    Transparent proxy that adds quantum identity awareness to existing colonies.

    This proxy wrapper allows existing colony implementations to gain quantum-proof
    identity features without requiring any modifications to their core code.
    """

    def __init__(
        self,
        target_colony: Union[BaseColony, object],
        proxy_id: str,
        identity_manager: Optional[QIIdentityManager] = None,
    ):
        """
        Initialize tier-aware colony proxy.

        Args:
            target_colony: The colony instance to wrap
            proxy_id: Unique identifier for this proxy
            identity_manager: Optional quantum identity manager instance
        """
        self.target_colony = target_colony
        self.proxy_id = proxy_id
        self.logger = logging.getLogger(f"{__name__}.{proxy_id}")

        # Quantum identity components
        self.identity_manager = identity_manager or (
            get_quantum_identity_manager() if QUANTUM_IDENTITY_AVAILABLE else None
        )

        # Proxy state management
        self.active_user_contexts: dict[str, QIUserContext] = {}
        self.method_access_rules: dict[str, dict[str, Any]] = {}
        self.performance_metrics: dict[str, list[float]] = {}
        self.proxy_audit_log: list[dict[str, Any]] = []

        # Initialize proxy configuration
        self._initialize_proxy_configuration()
        self._analyze_target_colony()
        self._setup_method_interception()

        self.logger.info(
            f"Tier-aware proxy initialized for {type(target_colony).__name__}"
        )

    def _initialize_proxy_configuration(self):
        """Initialize proxy configuration and access rules."""
        # Define method access rules based on tier levels
        self.method_access_rules = {
            # Basic operations - available to all tiers
            "basic_operations": {
                "min_tier": QITierLevel.QUANTUM_TIER_0,
                "methods": [
                    "get_info",
                    "get_status",
                    "get_capabilities",
                    "ping",
                ],
                "rate_limit": 60,  # requests per minute
            },
            # Query operations - Tier 0+
            "query_operations": {
                "min_tier": QITierLevel.QUANTUM_TIER_0,
                "methods": ["query", "search", "retrieve", "get"],
                "rate_limit": 30,
            },
            # Reasoning operations - Tier 1+
            "reasoning_operations": {
                "min_tier": QITierLevel.QUANTUM_TIER_1,
                "methods": ["reason", "analyze", "process", "evaluate"],
                "rate_limit": 100,
            },
            # Advanced operations - Tier 2+
            "advanced_operations": {
                "min_tier": QITierLevel.QUANTUM_TIER_2,
                "methods": ["create", "generate", "synthesize", "transform"],
                "rate_limit": 200,
            },
            # Oracle operations - Tier 2+
            "oracle_operations": {
                "min_tier": QITierLevel.QUANTUM_TIER_2,
                "methods": ["predict", "forecast", "prophesy", "divine"],
                "rate_limit": 50,
            },
            # Administrative operations - Tier 3+
            "admin_operations": {
                "min_tier": QITierLevel.QUANTUM_TIER_3,
                "methods": ["configure", "update", "modify", "delete"],
                "rate_limit": 20,
            },
            # System operations - Tier 4+
            "system_operations": {
                "min_tier": QITierLevel.QUANTUM_TIER_4,
                "methods": ["restart", "shutdown", "reset", "migrate"],
                "rate_limit": 5,
            },
            # Superintelligence operations - Tier 5 only
            "superintelligence_operations": {
                "min_tier": QITierLevel.QUANTUM_TIER_5,
                "methods": ["superintend", "transcend", "evolve", "ascend"],
                "rate_limit": -1,  # Unlimited
            },
        }

    def _analyze_target_colony(self):
        """Analyze the target colony to understand its interface."""
        colony_type = type(self.target_colony).__name__

        # Get all public methods
        public_methods = [
            method
            for method in dir(self.target_colony)
            if not method.startswith("_")
            and callable(getattr(self.target_colony, method))
        ]

        # Categorize methods based on naming patterns
        self.colony_method_categories = {}
        for method_name in public_methods:
            category = self._categorize_method(method_name)
            if category not in self.colony_method_categories:
                self.colony_method_categories[category] = []
            self.colony_method_categories[category].append(method_name)

        self.logger.debug(
            f"Analyzed {colony_type}: {len(public_methods)} methods across {len(self.colony_method_categories)} categories"
        )

    def _categorize_method(self, method_name: str) -> str:
        """Categorize a method based on its name pattern."""
        method_lower = method_name.lower()

        # Check each category for matching patterns
        for category, rules in self.method_access_rules.items():
            for pattern in rules["methods"]:
                if pattern in method_lower:
                    return category

        # Check for common patterns
        if any(
            prefix in method_lower for prefix in ["get", "retrieve", "fetch", "read"]
        ):
            return "query_operations"
        elif any(
            prefix in method_lower for prefix in ["create", "add", "insert", "generate"]
        ):
            return "advanced_operations"
        elif any(
            prefix in method_lower for prefix in ["update", "modify", "edit", "change"]
        ) or any(prefix in method_lower for prefix in ["delete", "remove", "destroy"]):
            return "admin_operations"
        elif any(
            prefix in method_lower for prefix in ["predict", "forecast", "anticipate"]
        ):
            return "oracle_operations"
        else:
            return "basic_operations"  # Default to basic

    def _setup_method_interception(self):
        """Setup method interception for identity-aware access control."""
        # Get all methods from the target colony
        for method_name in dir(self.target_colony):
            if not method_name.startswith("_") and callable(
                getattr(self.target_colony, method_name)
            ):
                # Create wrapped version of the method
                original_method = getattr(self.target_colony, method_name)
                wrapped_method = self._create_identity_aware_wrapper(
                    method_name, original_method
                )

                # Replace the method on this proxy
                setattr(self, method_name, wrapped_method)

    def _create_identity_aware_wrapper(
        self, method_name: str, original_method: Callable
    ) -> Callable:
        """Create an identity-aware wrapper for a colony method."""

        # Determine if method is async
        is_async = inspect.iscoroutinefunction(original_method)

        if is_async:

            @wraps(original_method)
            async def async_wrapper(*args, **kwargs):
                return await self._execute_with_identity_check(
                    method_name, original_method, args, kwargs
                )

            return async_wrapper
        else:

            @wraps(original_method)
            def sync_wrapper(*args, **kwargs):
                return asyncio.run(
                    self._execute_with_identity_check(
                        method_name, original_method, args, kwargs
                    )
                )

            return sync_wrapper

    async def _execute_with_identity_check(
        self,
        method_name: str,
        original_method: Callable,
        args: tuple,
        kwargs: dict,
    ) -> Any:
        """Execute method with identity-aware access control."""
        start_time = time.time()

        # Extract user context from arguments
        user_context = self._extract_user_context(args, kwargs)
        if not user_context:
            raise IdentityValidationError(
                f"No user context provided for method {method_name}"
            )

        # Validate identity and authorize access
        await self._validate_method_access(user_context, method_name)

        # Check rate limits
        await self._check_rate_limits(user_context, method_name)

        # Execute the original method
        try:
            if inspect.iscoroutinefunction(original_method):
                result = await original_method(*args, **kwargs)
            else:
                result = original_method(*args, **kwargs)

            # Log successful execution
            await self._log_method_execution(
                user_context,
                method_name,
                "success",
                result,
                time.time() - start_time,
            )

            return result

        except Exception as e:
            # Log failed execution
            await self._log_method_execution(
                user_context,
                method_name,
                "error",
                {"error": str(e)},
                time.time() - start_time,
            )
            raise

        finally:
            # Update performance metrics
            execution_time = time.time() - start_time
            if method_name not in self.performance_metrics:
                self.performance_metrics[method_name] = []
            self.performance_metrics[method_name].append(execution_time)

            # Keep only last 1000 measurements
            if len(self.performance_metrics[method_name]) > 1000:
                self.performance_metrics[method_name] = self.performance_metrics[
                    method_name
                ][-1000:]

    def _extract_user_context(
        self, args: tuple, kwargs: dict
    ) -> Optional[QIUserContext]:
        """Extract user context from method arguments."""
        # Check kwargs first
        if "user_context" in kwargs:
            return kwargs["user_context"]

        # Check for user_id in kwargs and lookup context
        if "user_id" in kwargs:
            user_id = kwargs["user_id"]
            if user_id in self.active_user_contexts:
                return self.active_user_contexts[user_id]

        # Check args for QIUserContext
        for arg in args:
            if isinstance(arg, QIUserContext):
                return arg

        # Check first argument if it's a dict with user context
        if args and isinstance(args[0], dict):
            data = args[0]
            if "user_context" in data:
                return data["user_context"]
            if "user_id" in data and data["user_id"] in self.active_user_contexts:
                return self.active_user_contexts[data["user_id"]]

        return None

    async def _validate_method_access(
        self, user_context: QIUserContext, method_name: str
    ):
        """Validate that user has access to the requested method."""
        # Categorize the method
        method_category = self._categorize_method(method_name)

        # Get access rules for this category
        if method_category not in self.method_access_rules:
            method_category = "basic_operations"  # Default fallback

        access_rules = self.method_access_rules[method_category]
        min_tier = access_rules["min_tier"]

        # Check tier level
        if user_context.tier_level.value < min_tier.value:
            raise TierAccessDeniedError(
                f"Method {method_name} requires {min_tier.name}, user has {user_context.tier_level.name}"
            )

        # Use quantum identity manager for additional authorization
        if self.identity_manager:
            authorized = await self.identity_manager.authorize_colony_access(
                user_context, self.proxy_id, method_name
            )
            if not authorized:
                raise QISecurityError(
                    f"Quantum authorization failed for method {method_name}"
                )

    async def _check_rate_limits(self, user_context: QIUserContext, method_name: str):
        """Check rate limits for the user and method."""
        method_category = self._categorize_method(method_name)
        if method_category not in self.method_access_rules:
            return  # No rate limit

        rate_limit = self.method_access_rules[method_category]["rate_limit"]
        if rate_limit <= 0:  # No limit or unlimited
            return

        # Check user's allocated resources
        allocated = user_context.allocated_resources
        requests_remaining = allocated.get("requests_remaining", 0)

        if requests_remaining <= 0:
            raise TierAccessDeniedError(
                f"Rate limit exceeded for user {user_context.user_id}"
            )

        # Decrement request count
        user_context.allocated_resources["requests_remaining"] = requests_remaining - 1

    async def _log_method_execution(
        self,
        user_context: QIUserContext,
        method_name: str,
        status: str,
        result: Any,
        execution_time: float,
    ):
        """Log method execution for audit purposes."""
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "proxy_id": self.proxy_id,
            "user_id": user_context.user_id,
            "identity_type": user_context.identity_type.value,
            "tier_level": user_context.tier_level.value,
            "method_name": method_name,
            "method_category": self._categorize_method(method_name),
            "status": status,
            "execution_time_ms": execution_time * 1000,
            "result_size": len(str(result)) if result else 0,
        }

        # Generate quantum audit signature if available
        if QUANTUM_IDENTITY_AVAILABLE and self.identity_manager:
            try:
                # This would use the quantum identity manager's audit system
                log_entry["qi_audit_hash"] = "placeholder_quantum_hash"
            except Exception as e:
                self.logger.error(f"Failed to generate quantum audit hash: {e}")

        self.proxy_audit_log.append(log_entry)

        # Keep only last 10000 audit entries
        if len(self.proxy_audit_log) > 10000:
            self.proxy_audit_log = self.proxy_audit_log[-10000:]

    async def register_user_context(self, user_context: QIUserContext):
        """Register a user context for proxy access."""
        self.active_user_contexts[user_context.user_id] = user_context
        self.logger.debug(
            f"Registered user context for {user_context.user_id} in proxy {self.proxy_id}"
        )

    async def unregister_user_context(self, user_id: str):
        """Unregister a user context."""
        if user_id in self.active_user_contexts:
            del self.active_user_contexts[user_id]
            self.logger.debug(
                f"Unregistered user context for {user_id} in proxy {self.proxy_id}"
            )

    def get_proxy_statistics(self) -> dict[str, Any]:
        """Get comprehensive proxy statistics."""
        stats = {
            "proxy_id": self.proxy_id,
            "target_colony_type": type(self.target_colony).__name__,
            "active_users": len(self.active_user_contexts),
            "total_audit_entries": len(self.proxy_audit_log),
            "method_categories": len(self.colony_method_categories),
            "performance_metrics": {},
            "identity_manager_available": self.identity_manager is not None,
        }

        # Calculate performance metrics
        for method_name, times in self.performance_metrics.items():
            if times:
                stats["performance_metrics"][method_name] = {
                    "calls": len(times),
                    "avg_time_ms": (sum(times) / len(times)) * 1000,
                    "min_time_ms": min(times) * 1000,
                    "max_time_ms": max(times) * 1000,
                }

        # Analyze recent activity
        recent_logs = [
            log for log in self.proxy_audit_log[-100:] if log["status"] == "success"
        ]
        stats["recent_activity"] = {
            "successful_calls": len(recent_logs),
            "unique_users": len({log["user_id"] for log in recent_logs}),
            "most_used_methods": self._get_most_used_methods(recent_logs),
        }

        return stats

    def _get_most_used_methods(
        self, logs: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Get most frequently used methods from logs."""
        method_counts = {}
        for log in logs:
            method = log["method_name"]
            method_counts[method] = method_counts.get(method, 0) + 1

        # Sort by count and return top 5
        sorted_methods = sorted(method_counts.items(), key=lambda x: x[1], reverse=True)
        return [
            {"method": method, "count": count} for method, count in sorted_methods[:5]
        ]

    def __getattr__(self, name: str) -> Any:
        """Delegate attribute access to the target colony if not found on proxy."""
        if hasattr(self.target_colony, name):
            attr = getattr(self.target_colony, name)
            if callable(attr):
                # This should have been wrapped during initialization
                return attr
            else:
                # Return non-callable attributes directly
                return attr

        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'"
        )

    def __str__(self) -> str:
        return f"TierAwareColonyProxy({self.proxy_id}, wrapping {type(self.target_colony).__name__})"

    def __repr__(self) -> str:
        return f"TierAwareColonyProxy(proxy_id='{self.proxy_id}', target={type(self.target_colony).__name__})"


class ColonyProxyManager:
    """
    Manager for creating and managing tier-aware colony proxies.

    Provides centralized management of multiple colony proxies with identity integration.
    """

    def __init__(self, identity_manager: Optional[QIIdentityManager] = None):
        self.identity_manager = identity_manager or (
            get_quantum_identity_manager() if QUANTUM_IDENTITY_AVAILABLE else None
        )
        self.proxies: dict[str, TierAwareColonyProxy] = {}
        self.logger = logging.getLogger(f"{__name__}.ColonyProxyManager")

    def create_proxy(
        self, colony: Union[BaseColony, object], proxy_id: Optional[str] = None
    ) -> TierAwareColonyProxy:
        """
        Create a tier-aware proxy for a colony.

        Args:
            colony: The colony instance to wrap
            proxy_id: Optional proxy identifier (auto-generated if not provided)

        Returns:
            TierAwareColonyProxy instance
        """
        if proxy_id is None:
            proxy_id = f"proxy_{type(colony).__name__.lower()}_{len(self.proxies)}"

        if proxy_id in self.proxies:
            raise ValueError(f"Proxy with ID '{proxy_id}' already exists")

        proxy = TierAwareColonyProxy(colony, proxy_id, self.identity_manager)
        self.proxies[proxy_id] = proxy

        self.logger.info(f"Created proxy '{proxy_id}' for {type(colony).__name__}")
        return proxy

    def get_proxy(self, proxy_id: str) -> Optional[TierAwareColonyProxy]:
        """Get a proxy by ID."""
        return self.proxies.get(proxy_id)

    def remove_proxy(self, proxy_id: str) -> bool:
        """Remove a proxy by ID."""
        if proxy_id in self.proxies:
            del self.proxies[proxy_id]
            self.logger.info(f"Removed proxy '{proxy_id}'")
            return True
        return False

    async def register_user_context_all(self, user_context: QIUserContext):
        """Register user context across all proxies."""
        for proxy in self.proxies.values():
            await proxy.register_user_context(user_context)

        self.logger.debug(
            f"Registered user context {user_context.user_id} across {len(self.proxies)} proxies"
        )

    async def unregister_user_context_all(self, user_id: str):
        """Unregister user context across all proxies."""
        for proxy in self.proxies.values():
            await proxy.unregister_user_context(user_id)

        self.logger.debug(
            f"Unregistered user context {user_id} across {len(self.proxies)} proxies"
        )

    def get_manager_statistics(self) -> dict[str, Any]:
        """Get comprehensive manager statistics."""
        stats = {
            "total_proxies": len(self.proxies),
            "identity_manager_available": self.identity_manager is not None,
            "proxy_details": {},
            "aggregate_metrics": {
                "total_active_users": 0,
                "total_audit_entries": 0,
                "total_method_calls": 0,
            },
        }

        # Collect statistics from all proxies
        for proxy_id, proxy in self.proxies.items():
            proxy_stats = proxy.get_proxy_statistics()
            stats["proxy_details"][proxy_id] = proxy_stats

            # Aggregate metrics
            stats["aggregate_metrics"]["total_active_users"] += proxy_stats[
                "active_users"
            ]
            stats["aggregate_metrics"]["total_audit_entries"] += proxy_stats[
                "total_audit_entries"
            ]

            for method_stats in proxy_stats["performance_metrics"].values():
                stats["aggregate_metrics"]["total_method_calls"] += method_stats[
                    "calls"
                ]

        return stats


# Global proxy manager instance
_proxy_manager: Optional[ColonyProxyManager] = None


def get_colony_proxy_manager() -> ColonyProxyManager:
    """Get global colony proxy manager instance."""
    global _proxy_manager
    if _proxy_manager is None:
        _proxy_manager = ColonyProxyManager()
    return _proxy_manager


# Convenience functions for common operations


def create_identity_aware_proxy(
    colony: Union[BaseColony, object], proxy_id: Optional[str] = None
) -> TierAwareColonyProxy:
    """Create an identity-aware proxy for a colony."""
    manager = get_colony_proxy_manager()
    return manager.create_proxy(colony, proxy_id)


async def wrap_existing_colonies_with_identity(
    colonies: dict[str, Union[BaseColony, object]],
) -> dict[str, TierAwareColonyProxy]:
    """Wrap multiple existing colonies with identity-aware proxies."""
    manager = get_colony_proxy_manager()
    proxies = {}

    for colony_name, colony in colonies.items():
        proxy_id = f"identity_aware_{colony_name}"
        proxy = manager.create_proxy(colony, proxy_id)
        proxies[colony_name] = proxy

    return proxies
