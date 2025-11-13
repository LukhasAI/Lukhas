"""Configuration Resolver for Provider Registry.

Provides configuration lookup with fallback defaults and
environment variable support.

Usage:
    from core.adapters.config_resolver import make_resolver

    config = make_resolver()
    value = config.get("providers.openai.module")
"""

import os
from typing import Any, Optional


class ConfigResolver:
    """Configuration resolver with fallback support."""

    def __init__(self, config_dict: Optional[Dict[str, Any]] = None):
        """Initialize resolver with optional config dictionary.

        Args:
            config_dict: Configuration dictionary (defaults to empty dict)
        """
        self._config = config_dict or {}
        self._defaults = {
            "providers.openai.module": "labs.providers.openai",
            "providers.openai.class": "OpenAIProvider",
            "providers.anthropic.module": "labs.providers.anthropic",
            "providers.anthropic.class": "AnthropicProvider",
            "providers.memory.module": "labs.memory.fold_system.memory_fold_system",
            "providers.memory.class": "MemoryFoldSystem",
            "providers.guardian.module": "labs.governance.guardian_sentinel",
            "providers.guardian.class": "GuardianSentinel",
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with fallback.

        Resolution order:
        1. Environment variable (key with dots replaced by underscores, uppercase)
        2. Config dictionary
        3. Default values
        4. Provided default parameter

        Args:
            key: Configuration key (dot-separated path)
            default: Default value if not found

        Returns:
            Configuration value
        """
        # Try environment variable
        env_key = key.replace(".", "_").upper()
        env_value = os.environ.get(env_key)
        if env_value is not None:
            return env_value

        # Try config dictionary (support nested keys)
        value = self._get_nested(self._config, key)
        if value is not None:
            return value

        # Try defaults
        if key in self._defaults:
            return self._defaults[key]

        return default

    def set(self, key: str, value: Any):
        """Set configuration value.

        Args:
            key: Configuration key
            value: Configuration value
        """
        self._set_nested(self._config, key, value)

    def _get_nested(self, d: Dict, key: str) -> Any:
        """Get value from nested dictionary using dot notation.

        Args:
            d: Dictionary to search
            key: Dot-separated key path

        Returns:
            Value or None if not found
        """
        keys = key.split(".")
        current = d

        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return None

        return current

    def _set_nested(self, d: Dict, key: str, value: Any):
        """Set value in nested dictionary using dot notation.

        Args:
            d: Dictionary to modify
            key: Dot-separated key path
            value: Value to set
        """
        keys = key.split(".")
        current = d

        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        current[keys[-1]] = value


def make_resolver(config_dict: Optional[Dict[str, Any]] = None) -> ConfigResolver:
    """Factory function to create ConfigResolver.

    Args:
        config_dict: Optional configuration dictionary

    Returns:
        ConfigResolver instance
    """
    return ConfigResolver(config_dict)
