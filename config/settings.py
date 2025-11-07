"""LUKHAS Configuration Settings Integration

This module provides centralized access to LUKHAS configuration settings,
integrating with the main settings.json file and providing typed access
to configuration parameters across the LUKHAS ecosystem.
"""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Default settings file path
DEFAULT_SETTINGS_PATH = Path(__file__).parent / "settings.json"


@dataclass
class MemoryConfig:
    """Memory configuration settings."""

    allow_forgetting: bool = True
    hash_qrg_by_default: bool = True
    log_path: str = "logs/lukhas_memory_log.jsonl"


@dataclass
class PrivacyConfig:
    """Privacy configuration settings."""

    consent_required: bool = True
    memory_visible_to_user: bool = True
    data_retention_period_days: int = 365
    data_export_enabled: bool = True
    user_analytics_logging: bool = False


@dataclass
class InterfaceConfig:
    """Interface configuration settings."""

    voice_enabled: bool = False
    dashboard_active: bool = True


@dataclass
class EngineConfig:
    """Engine configuration settings."""

    core_model: str = "gpt-4"
    voice_engine: str = "openai-tts"
    image_engine: str = "dalle-2"
    supports_qr_stamps: bool = True
    multiverse_ready: bool = False


@dataclass
class LUKHASSettings:
    """Main LUKHAS configuration settings container."""

    version: str = "v1.0"
    gdpr_enabled: bool = True
    default_tone: str = "symbolic"
    default_language: str = "en"
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    privacy: PrivacyConfig = field(default_factory=PrivacyConfig)
    interface: InterfaceConfig = field(default_factory=InterfaceConfig)
    engine: EngineConfig = field(default_factory=EngineConfig)
    raw_config: dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value with dot notation support."""
        keys = key.split(".")
        value = self.raw_config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value


class ConfigurationManager:
    """Manages LUKHAS configuration settings."""

    def __init__(self, settings_path: Optional[Path] = None):
        self.settings_path = settings_path or DEFAULT_SETTINGS_PATH
        self._settings: Optional[LUKHASSettings] = None
        self.load_settings()

    def load_settings(self) -> LUKHASSettings:
        """Load settings from the configuration file."""
        try:
            if not self.settings_path.exists():
                logger.warning(f"Settings file not found at {self.settings_path}, using defaults")
                self._settings = LUKHASSettings()
                return self._settings

            with open(self.settings_path, encoding="utf-8") as f:
                config_data = json.load(f)

            # Create typed configuration objects
            memory_config = MemoryConfig(**config_data.get("memory", {}))
            privacy_config = PrivacyConfig(**config_data.get("privacy", {}))
            interface_config = InterfaceConfig(**config_data.get("interface", {}))
            engine_config = EngineConfig(**config_data.get("engine", {}))

            self._settings = LUKHASSettings(
                version=config_data.get("version", "v1.0"),
                gdpr_enabled=config_data.get("gdpr_enabled", True),
                default_tone=config_data.get("default_tone", "symbolic"),
                default_language=config_data.get("default_language", "en"),
                memory=memory_config,
                privacy=privacy_config,
                interface=interface_config,
                engine=engine_config,
                raw_config=config_data,
            )

            logger.info(f"Loaded LUKHAS settings from {self.settings_path}")
            return self._settings

        except Exception as e:
            logger.error(f"Error loading settings from {self.settings_path}: {e}")
            self._settings = LUKHASSettings()
            return self._settings

    @property
    def settings(self) -> LUKHASSettings:
        """Get the current settings."""
        if self._settings is None:
            self.load_settings()
        return self._settings

    def reload(self) -> None:
        """Reload settings from file."""
        self.load_settings()

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a specific setting value."""
        return self.settings.get(key, default)


# Global configuration manager instance
config_manager = ConfigurationManager()


# Convenience functions for common settings access
def get_settings() -> LUKHASSettings:
    """Get the global settings instance."""
    return config_manager.settings


def get_setting(key: str, default: Any = None) -> Any:
    """Get a specific setting value."""
    return config_manager.get_setting(key, default)


def reload_settings() -> None:
    """Reload settings from file."""
    config_manager.reload()


# Export main classes and functions
__all__ = [
    "ConfigurationManager",
    "EngineConfig",
    "InterfaceConfig",
    "LUKHASSettings",
    "MemoryConfig",
    "PrivacyConfig",
    "config_manager",
    "get_setting",
    "get_settings",
    "reload_settings",
]
