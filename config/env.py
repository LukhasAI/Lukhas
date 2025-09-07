"""
🔒 LUKHAS AI - Centralized Environment Configuration
Secure environment variable loading with validation and optional YAML support

Copyright (c) 2025 LUKHAS AI. All rights reserved.
"""

import logging
import os
from pathlib import Path
from typing import Any, Optional

import yaml

logger = logging.getLogger(__name__)


class EnvironmentConfig:
    """Centralized environment configuration with validation and YAML support"""

    def __init__(self, yaml_path: Optional[str] = None):
        """
        Initialize environment configuration

        Args:
            yaml_path: Optional path to YAML configuration file
        """
        self._yaml_config: dict[str, Any] = {}
        self._required_vars: list[str] = []
        self._optional_vars: dict[str, Any] = {}

        if yaml_path and Path(yaml_path).exists():
            self._load_yaml_config(yaml_path)

    def _load_yaml_config(self, yaml_path: str) -> None:
        """Load configuration from YAML file"""
        try:
            with open(yaml_path) as file:
                self._yaml_config = yaml.safe_load(file) or {}
                logger.info(f"Loaded configuration from {yaml_path}")
        except Exception as e:
            logger.warning(f"Failed to load YAML config from {yaml_path}: {e}")
            self._yaml_config = {}

    def get(self, key: str, default: Any = None, required: bool = False) -> Any:
        """
        Get environment variable with fallback to YAML config

        Args:
            key: Environment variable name
            default: Default value if not found
            required: Whether this variable is required

        Returns:
            Environment variable value or default

        Raises:
            ValueError: If required variable is missing
        """
        # First try environment variables
        value = os.environ.get(key)

        # Fallback to YAML config
        if value is None and key in self._yaml_config:
            value = self._yaml_config[key]

        # Use default if still None
        if value is None:
            value = default

        # Check required variables
        if required and (value is None or value == ""):
            raise ValueError(f"Required environment variable '{key}' is not set")

        # Track required/optional vars for validation
        if required:
            self._required_vars.append(key)
        else:
            self._optional_vars[key] = default

        return value

    def get_bool(self, key: str, default: bool = False, required: bool = False) -> bool:
        """Get boolean environment variable"""
        value = self.get(key, default, required)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ("true", "1", "yes", "on")
        return bool(value)

    def get_int(self, key: str, default: int = 0, required: bool = False) -> int:
        """Get integer environment variable"""
        value = self.get(key, default, required)
        try:
            return int(value)
        except (ValueError, TypeError):
            if required:
                raise ValueError(f"Environment variable '{key}' must be an integer, got: {value}")
            return default

    def get_float(self, key: str, default: float = 0.0, required: bool = False) -> float:
        """Get float environment variable"""
        value = self.get(key, default, required)
        try:
            return float(value)
        except (ValueError, TypeError):
            if required:
                raise ValueError(f"Environment variable '{key}' must be a float, got: {value}")
            return default

    def get_list(
        self, key: str, default: Optional[list] = None, separator: str = ",", required: bool = False
    ) -> list[str]:
        """Get list from comma-separated environment variable"""
        if default is None:
            default = []

        value = self.get(key, "", required)
        if not value:
            return default

        return [item.strip() for item in str(value).split(separator) if item.strip()]

    def validate_required(self) -> None:
        """Validate all required environment variables are set"""
        missing = []
        for var in self._required_vars:
            if not os.environ.get(var) and var not in self._yaml_config:
                missing.append(var)

        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing}")

    def get_status(self) -> dict[str, Any]:
        """Get configuration status summary"""
        return {
            "required_vars": len(self._required_vars),
            "optional_vars": len(self._optional_vars),
            "yaml_config_loaded": bool(self._yaml_config),
            "yaml_keys": list(self._yaml_config.keys()) if self._yaml_config else [],
        }


# Global configuration instance
_config_instance: Optional[EnvironmentConfig] = None


def get_config(yaml_path: Optional[str] = None) -> EnvironmentConfig:
    """Get global configuration instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = EnvironmentConfig(yaml_path)
    return _config_instance


# LUKHAS AI Specific Configuration Getters
class LUKHASConfig:
    """LUKHAS AI specific configuration with validation"""

    def __init__(self, config: Optional[EnvironmentConfig] = None):
        self.config = config or get_config()

    # API Keys (Required in production)
    @property
    def openai_api_key(self) -> str:
        """OpenAI API key for LLM integration"""
        return self.config.get("OPENAI_API_KEY", "", required=self.is_production)

    @property
    def anthropic_api_key(self) -> str:
        """Anthropic API key for Claude integration"""
        return self.config.get("ANTHROPIC_API_KEY", "", required=False)

    @property
    def google_api_key(self) -> str:
        """Google API key for Gemini integration"""
        return self.config.get("GOOGLE_API_KEY", "", required=False)

    @property
    def perplexity_api_key(self) -> str:
        """Perplexity API key for search integration"""
        return self.config.get("PERPLEXITY_API_KEY", "", required=False)

    # Security & Identity
    @property
    def lukhas_id_secret(self) -> str:
        """LUKHAS ID secret key for identity system"""
        return self.config.get("LUKHAS_ID_SECRET", required=True)

    @property
    def jwt_secret(self) -> str:
        """JWT signing secret"""
        return self.config.get("JWT_SECRET", required=True)

    @property
    def encryption_key(self) -> str:
        """Encryption key for sensitive data"""
        return self.config.get("ENCRYPTION_KEY", required=True)

    # Database URLs
    @property
    def database_url(self) -> str:
        """Primary database connection URL"""
        return self.config.get("DATABASE_URL", "sqlite:///lukhas.db")

    @property
    def redis_url(self) -> str:
        """Redis connection URL for caching"""
        return self.config.get("REDIS_URL", "redis://localhost:6379/0")

    @property
    def mongodb_url(self) -> str:
        """MongoDB connection URL for document storage"""
        return self.config.get("MONGODB_URL", "mongodb://localhost:27017/lukhas")

    # System Configuration
    @property
    def environment(self) -> str:
        """Current environment (development, staging, production)"""
        return self.config.get("ENVIRONMENT", "development")

    @property
    def is_production(self) -> bool:
        """Whether running in production environment"""
        return self.environment.lower() == "production"

    @property
    def debug(self) -> bool:
        """Debug mode enabled"""
        return self.config.get_bool("DEBUG", default=not self.is_production)

    @property
    def log_level(self) -> str:
        """Logging level"""
        return self.config.get("LOG_LEVEL", "INFO" if self.is_production else "DEBUG")

    # Feature Flags
    @property
    def consciousness_active(self) -> bool:
        """Consciousness system active"""
        return self.config.get_bool("CONSCIOUSNESS_ACTIVE", True)

    @property
    def vivox_active(self) -> bool:
        """VIVOX consciousness system active"""
        return self.config.get_bool("VIVOX_ACTIVE", True)

    @property
    def emotion_active(self) -> bool:
        """Emotion processing active"""
        return self.config.get_bool("EMOTION_ACTIVE", True)

    # Guardian System
    @property
    def ethics_enforcement_level(self) -> str:
        """Ethics enforcement level (strict, moderate, lenient)"""
        return self.config.get("ETHICS_ENFORCEMENT_LEVEL", "moderate")

    @property
    def guardian_drift_threshold(self) -> float:
        """Guardian drift detection threshold"""
        return self.config.get_float("GUARDIAN_DRIFT_THRESHOLD", 0.15)

    # Performance Settings
    @property
    def max_memory_folds(self) -> int:
        """Maximum number of memory folds"""
        return self.config.get_int("MAX_MEMORY_FOLDS", 1000)

    @property
    def api_rate_limit_per_minute(self) -> int:
        """API rate limit per minute"""
        return self.config.get_int("API_RATE_LIMIT_PER_MINUTE", 1000)

    # External Services
    @property
    def github_token(self) -> str:
        """GitHub token for automation"""
        return self.config.get("GITHUB_TOKEN", "")

    def validate(self) -> None:
        """Validate all required configuration"""
        self.config.validate_required()

        # Additional LUKHAS-specific validation
        if self.is_production:
            # Ensure critical secrets are set in production
            if not self.openai_api_key:
                raise ValueError("OPENAI_API_KEY required in production")
            if len(self.lukhas_id_secret) < 32:
                raise ValueError("LUKHAS_ID_SECRET must be at least 32 characters")
            if len(self.jwt_secret) < 32:
                raise ValueError("JWT_SECRET must be at least 32 characters")


# Global LUKHAS config instance
def get_lukhas_config() -> LUKHASConfig:
    """Get global LUKHAS configuration instance"""
    return LUKHASConfig()


# Backward compatibility functions
def get(key: str, default=None):
    """Return env var value or default. (Legacy compatibility)"""
    return os.getenv(key, default)


def require(key: str):
    """Return env var value or raise if missing. (Legacy compatibility)"""
    value = os.getenv(key)
    if not value:
        raise RuntimeError(f"Missing required env var: {key}")
    return value


# Convenience functions for new unified interface
def get_env(key: str, default: Any = None, required: bool = False) -> Any:
    """Get environment variable (convenience function)"""
    return get_config().get(key, default, required)


def get_env_bool(key: str, default: bool = False) -> bool:
    """Get boolean environment variable (convenience function)"""
    return get_config().get_bool(key, default)


def get_env_int(key: str, default: int = 0) -> int:
    """Get integer environment variable (convenience function)"""
    return get_config().get_int(key, default)
