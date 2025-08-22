"""
Feature Flags System for LUKHAS
Minimal implementation to satisfy tests and control feature rollout
"""

import functools
import os
import warnings
from pathlib import Path
from typing import Callable, Dict

import yaml


class FeatureFlags:
    """Centralized feature flag management"""

    _instance = None
    _flags: Dict[str, bool] = {}
    _overrides: Dict[str, bool] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_flags()
        return cls._instance

    def _load_flags(self):
        """Load flags from environment and optional YAML"""
        # Default flags
        self._flags = {
            "experimental_colonies": False,
            "adaptive_ai": True,
            "quantum_processing": False,
            "dream_engine": True,
            "guardian_system": True,
            "feature_flags": True,  # Meta flag
        }

        # Load from environment variables (LUKHAS_FLAG_*)
        for key in os.environ:
            if key.startswith("LUKHAS_FLAG_"):
                flag_name = key[12:].lower()  # Remove prefix
                self._flags[flag_name] = os.environ[key].lower() in ("true", "1", "yes")

        # Load from YAML if exists
        yaml_path = Path("lukhas_flags.yaml")
        if yaml_path.exists():
            try:
                with open(yaml_path) as f:
                    yaml_flags = yaml.safe_load(f)
                    if yaml_flags and isinstance(yaml_flags, dict):
                        self._flags.update(yaml_flags)
            except Exception as e:
                warnings.warn(f"Failed to load flags from YAML: {e}")

    def get(self, name: str, default: bool = False) -> bool:
        """Get flag value with optional default"""
        # Check overrides first (for testing)
        if name in self._overrides:
            return self._overrides[name]
        return self._flags.get(name, default)

    def set_override(self, name: str, value: bool):
        """Set temporary override (mainly for testing)"""
        self._overrides[name] = value

    def clear_override(self, name: str):
        """Clear a temporary override"""
        self._overrides.pop(name, None)

    def clear_all_overrides(self):
        """Clear all temporary overrides"""
        self._overrides.clear()

    def all_flags(self) -> Dict[str, bool]:
        """Get all flags with overrides applied"""
        result = self._flags.copy()
        result.update(self._overrides)
        return result


# Singleton instance
_flags = FeatureFlags()


def get_flags() -> Dict[str, bool]:
    """Get all current feature flags"""
    return _flags.all_flags()


def require_feature(name: str) -> None:
    """
    Require a feature to be enabled, raise if not.

    Args:
        name: Feature flag name

    Raises:
        RuntimeError: If feature is not enabled
    """
    if not _flags.get(name):
        raise RuntimeError(
            f"Feature '{name}' is not enabled. "
            f"Enable with LUKHAS_FLAG_{name.upper()}=true or in lukhas_flags.yaml"
        )


def when_enabled(name: str) -> Callable:
    """
    Decorator to conditionally execute based on feature flag.

    Args:
        name: Feature flag name

    Returns:
        Decorator that skips function if feature is disabled
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not _flags.get(name):
                # Skip execution, return None or raise
                if hasattr(func, "__unittest_skip__"):
                    # For test methods, skip
                    import unittest

                    raise unittest.SkipTest(f"Feature '{name}' is disabled")
                else:
                    # For regular functions, return None with warning
                    warnings.warn(
                        f"Skipping {func.__name__}: feature '{name}' is disabled",
                        category=UserWarning,
                    )
                    return None
            return func(*args, **kwargs)

        # Mark for test frameworks
        if not _flags.get(name):
            wrapper.__unittest_skip__ = True
            wrapper.__unittest_skip_why__ = f"Feature '{name}' is disabled"

        return wrapper

    return decorator


def is_enabled(name: str) -> bool:
    """Check if a feature is enabled"""
    return _flags.get(name, False)


class FeatureFlagContext:
    """Context manager for temporary feature flag overrides"""

    def __init__(self, **flags):
        self.flags = flags
        self.original = {}

    def __enter__(self):
        """Store original values and apply overrides"""
        for name, value in self.flags.items():
            self.original[name] = _flags.get(name)
            _flags.set_override(name, value)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Restore original values"""
        for name in self.flags:
            _flags.clear_override(name)


# Convenience exports
__all__ = [
    "get_flags",
    "require_feature",
    "when_enabled",
    "is_enabled",
    "FeatureFlagContext",
]
