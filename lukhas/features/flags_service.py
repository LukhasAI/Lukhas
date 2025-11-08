"""
Privacy-first feature flags service for LUKHAS AI.

This service provides controlled rollouts, A/B testing, and safe experimentation
without third-party dependencies or user tracking.

PRIVACY REQUIREMENTS:
- NO user tracking without consent
- Flag evaluations logged only in aggregate
- User targeting via privacy-preserving hashes (SHA-256)
- No third-party services
- Local-first evaluation

SUPPORTED FLAG TYPES:
1. Boolean (on/off)
2. Percentage rollout (0-100%)
3. User targeting (email domain, user ID hash)
4. Time-based (enable after date, disable after date)
5. Environment-based (dev/staging/prod)
"""

import hashlib
import logging
import os
import time
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml

logger = logging.getLogger(__name__)


class FlagType(str, Enum):
    """Supported feature flag types."""

    BOOLEAN = "boolean"
    PERCENTAGE = "percentage"
    USER_TARGETING = "user_targeting"
    TIME_BASED = "time_based"
    ENVIRONMENT = "environment"


class FlagEvaluationContext:
    """Context for evaluating feature flags."""

    def __init__(
        self,
        user_id: Optional[str] = None,
        email: Optional[str] = None,
        environment: Optional[str] = None,
        timestamp: Optional[datetime] = None,
    ):
        """
        Initialize flag evaluation context.

        Args:
            user_id: User ID for targeting (will be hashed for privacy)
            email: User email for domain-based targeting
            environment: Current environment (dev/staging/prod)
            timestamp: Current timestamp (defaults to now)
        """
        self.user_id = user_id
        self.email = email
        self.environment = environment or os.getenv("LUKHAS_ENV", "dev")
        self.timestamp = timestamp or datetime.now(timezone.utc)

    def get_user_hash(self) -> str:
        """
        Get privacy-preserving hash of user ID.

        Returns:
            SHA-256 hash of user ID as hex string
        """
        if not self.user_id:
            return ""
        return hashlib.sha256(self.user_id.encode()).hexdigest()

    def get_email_domain(self) -> str:
        """
        Get email domain for domain-based targeting.

        Returns:
            Email domain (e.g., "lukhas.ai")
        """
        if not self.email or "@" not in self.email:
            return ""
        return self.email.split("@")[1].lower()


class FeatureFlag:
    """Represents a feature flag configuration."""

    def __init__(self, name: str, config: Dict[str, Any]):
        """
        Initialize feature flag.

        Args:
            name: Flag name
            config: Flag configuration dictionary
        """
        self.name = name
        self.enabled = config.get("enabled", False)
        self.flag_type = FlagType(config.get("type", "boolean"))
        self.description = config.get("description", "")
        self.owner = config.get("owner", "")
        self.created_at = config.get("created_at", "")
        self.jira_ticket = config.get("jira_ticket", "")

        # Type-specific configuration
        self.percentage = config.get("percentage", 0)
        self.allowed_domains = config.get("allowed_domains", [])
        self.allowed_user_hashes = config.get("allowed_user_hashes", [])
        self.enable_after = config.get("enable_after")
        self.disable_after = config.get("disable_after")
        self.allowed_environments = config.get("allowed_environments", [])

        # Fallback value for errors
        self.fallback = config.get("fallback", False)

    def evaluate(self, context: FlagEvaluationContext) -> bool:
        """
        Evaluate flag based on type and context.

        Args:
            context: Evaluation context with user/environment info

        Returns:
            True if flag is enabled for this context
        """
        try:
            # Check if flag is globally disabled
            if not self.enabled:
                return False

            # Evaluate based on flag type
            if self.flag_type == FlagType.BOOLEAN:
                return self._evaluate_boolean()

            elif self.flag_type == FlagType.PERCENTAGE:
                return self._evaluate_percentage(context)

            elif self.flag_type == FlagType.USER_TARGETING:
                return self._evaluate_user_targeting(context)

            elif self.flag_type == FlagType.TIME_BASED:
                return self._evaluate_time_based(context)

            elif self.flag_type == FlagType.ENVIRONMENT:
                return self._evaluate_environment(context)

            else:
                logger.warning(f"Unknown flag type: {self.flag_type}")
                return self.fallback

        except Exception as e:
            logger.error(f"Error evaluating flag {self.name}: {e}")
            return self.fallback

    def _evaluate_boolean(self) -> bool:
        """Evaluate boolean flag."""
        return self.enabled

    def _evaluate_percentage(self, context: FlagEvaluationContext) -> bool:
        """
        Evaluate percentage-based rollout.

        Uses consistent hashing to ensure same user always gets same result.
        """
        if not context.user_id:
            # No user ID, use random-ish fallback
            return False

        # Hash user ID + flag name for consistent rollout
        combined = f"{context.user_id}:{self.name}"
        hash_value = int(hashlib.sha256(combined.encode()).hexdigest()[:8], 16)
        bucket = hash_value % 100

        return bucket < self.percentage

    def _evaluate_user_targeting(self, context: FlagEvaluationContext) -> bool:
        """Evaluate user targeting flag."""
        # Check email domain targeting
        if self.allowed_domains:
            domain = context.get_email_domain()
            if domain and domain in self.allowed_domains:
                return True

        # Check user hash targeting (privacy-preserving)
        if self.allowed_user_hashes:
            user_hash = context.get_user_hash()
            if user_hash and user_hash in self.allowed_user_hashes:
                return True

        return False

    def _evaluate_time_based(self, context: FlagEvaluationContext) -> bool:
        """Evaluate time-based flag."""
        now = context.timestamp

        # Check enable_after
        if self.enable_after:
            enable_dt = datetime.fromisoformat(self.enable_after.replace("Z", "+00:00"))
            if now < enable_dt:
                return False

        # Check disable_after
        if self.disable_after:
            disable_dt = datetime.fromisoformat(
                self.disable_after.replace("Z", "+00:00")
            )
            if now >= disable_dt:
                return False

        return True

    def _evaluate_environment(self, context: FlagEvaluationContext) -> bool:
        """Evaluate environment-based flag."""
        if not self.allowed_environments:
            return True

        return context.environment in self.allowed_environments


class FeatureFlagsService:
    """
    Privacy-first feature flags service.

    Provides controlled rollouts, A/B testing, and safe experimentation
    without third-party dependencies.
    """

    def __init__(
        self,
        config_path: Optional[str] = None,
        cache_ttl: int = 60,
    ):
        """
        Initialize feature flags service.

        Args:
            config_path: Path to flags YAML config (defaults to branding/features/flags.yaml)
            cache_ttl: Cache time-to-live in seconds (default: 60)
        """
        self.config_path = config_path or self._get_default_config_path()
        self.cache_ttl = cache_ttl
        self.flags: Dict[str, FeatureFlag] = {}
        self._cache_timestamp: float = 0
        self._load_flags()

    def _get_default_config_path(self) -> str:
        """Get default config path relative to repository root."""
        # Try to find repo root
        current = Path(__file__).resolve()
        for parent in [current] + list(current.parents):
            if (parent / "branding" / "features").exists():
                return str(parent / "branding" / "features" / "flags.yaml")

        # Fallback to relative path
        return "branding/features/flags.yaml"

    def _load_flags(self) -> None:
        """Load flags from YAML configuration."""
        try:
            if not os.path.exists(self.config_path):
                logger.warning(f"Flags config not found: {self.config_path}")
                self.flags = {}
                return

            with open(self.config_path, "r") as f:
                config = yaml.safe_load(f)

            # Parse flags
            flags_config = config.get("flags", {})
            self.flags = {
                name: FeatureFlag(name, flag_config)
                for name, flag_config in flags_config.items()
            }

            self._cache_timestamp = time.time()
            logger.info(f"Loaded {len(self.flags)} feature flags from {self.config_path}")

        except Exception as e:
            logger.error(f"Error loading flags config: {e}")
            self.flags = {}

    def _should_reload(self) -> bool:
        """Check if cache has expired and flags should be reloaded."""
        return time.time() - self._cache_timestamp > self.cache_ttl

    def is_enabled(
        self,
        flag_name: str,
        context: Optional[FlagEvaluationContext] = None,
    ) -> bool:
        """
        Check if a feature flag is enabled.

        Args:
            flag_name: Name of the flag to check
            context: Evaluation context (user, environment, etc.)

        Returns:
            True if flag is enabled, False otherwise
        """
        # Reload flags if cache expired
        if self._should_reload():
            self._load_flags()

        # Get flag
        flag = self.flags.get(flag_name)
        if not flag:
            logger.warning(f"Flag not found: {flag_name}")
            return False

        # Evaluate flag
        ctx = context or FlagEvaluationContext()
        result = flag.evaluate(ctx)

        # Log evaluation (aggregate only, no PII)
        logger.debug(
            f"Flag evaluation: {flag_name} = {result} "
            f"(type={flag.flag_type}, env={ctx.environment})"
        )

        return result

    def get_flag(self, flag_name: str) -> Optional[FeatureFlag]:
        """
        Get flag configuration.

        Args:
            flag_name: Name of the flag

        Returns:
            FeatureFlag object or None if not found
        """
        if self._should_reload():
            self._load_flags()

        return self.flags.get(flag_name)

    def list_flags(self) -> List[str]:
        """
        List all flag names.

        Returns:
            List of flag names
        """
        if self._should_reload():
            self._load_flags()

        return list(self.flags.keys())

    def get_all_flags(self) -> Dict[str, FeatureFlag]:
        """
        Get all flag configurations.

        Returns:
            Dictionary of flag name to FeatureFlag object
        """
        if self._should_reload():
            self._load_flags()

        return self.flags.copy()

    def reload(self) -> None:
        """Force reload flags from configuration file."""
        self._load_flags()


# Global service instance
_service: Optional[FeatureFlagsService] = None


def get_service() -> FeatureFlagsService:
    """
    Get global feature flags service instance.

    Returns:
        FeatureFlagsService instance
    """
    global _service
    if _service is None:
        _service = FeatureFlagsService()
    return _service


def is_enabled(flag_name: str, context: Optional[FlagEvaluationContext] = None) -> bool:
    """
    Convenience function to check if a flag is enabled.

    Args:
        flag_name: Name of the flag to check
        context: Evaluation context

    Returns:
        True if flag is enabled
    """
    return get_service().is_enabled(flag_name, context)
