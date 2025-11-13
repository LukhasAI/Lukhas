"""
Configuration Resolver
======================
Resolves configuration for provider instances at runtime.
Supports environment-based configuration and testing overrides.
"""

import os
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class Config:
    """Runtime configuration for providers."""

    environment: str = field(default_factory=lambda: os.getenv("LUKHAS_ENV", "development"))
    openai_api_key: Optional[str] = field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    openai_model: str = field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4"))
    openai_temperature: float = field(default_factory=lambda: float(os.getenv("OPENAI_TEMPERATURE", "0.7")))

    # Testing/mocking support
    mock_providers: bool = field(default_factory=lambda: os.getenv("LUKHAS_MOCK_PROVIDERS", "false").lower() == "true")

    # Additional configuration
    extra: dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return getattr(self, key, self.extra.get(key, default))

    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        if hasattr(self, key):
            setattr(self, key, value)
        else:
            self.extra[key] = value


def make_resolver() -> Config:
    """
    Factory function to create configuration resolver.

    Returns:
        Config instance with environment-based settings
    """
    return Config()
