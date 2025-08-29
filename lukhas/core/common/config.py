"""
⚙️ Common Configuration Loader
=============================
Centralized configuration management for LUKHAS modules.
"""

import json
import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

import yaml


@dataclass
class ModuleConfig:
    """Configuration for a LUKHAS module"""

    name: str
    enabled: bool = True
    version: str = "1.0.0"
    settings: dict[str, Any] = field(default_factory=dict)
    dependencies: list[str] = field(default_factory=list)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with dot notation support"""
        keys = key.split(".")
        value = self.settings

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """Set configuration value with dot notation support"""
        keys = key.split(".")
        target = self.settings

        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]

        target[keys[-1]] = value


class ConfigLoader:
    """Centralized configuration loader"""

    def __init__(self, root_path: Optional[Path] = None):
        self.root_path = root_path or self._find_project_root()
        self.configs: dict[str, ModuleConfig] = {}
        self._env_loaded = False

    def _find_project_root(self) -> Path:
        """Find project root by looking for marker files"""
        current = Path.cwd()

        while current != current.parent:
            if (current / "lukhas_config.yaml").exists():
                return current
            if (current / "requirements.txt").exists() and (current / "core").exists():
                return current
            current = current.parent

        return Path.cwd()

    def load_env(self) -> None:
        """Load environment variables from .env file"""
        if self._env_loaded:
            return

        env_file = self.root_path / ".env"
        if env_file.exists():
            with open(env_file) as f:
                for raw_line in f:
                    line = raw_line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        os.environ[key.strip()] = value.strip()

        self._env_loaded = True

    def load_module_config(self, module_name: str) -> ModuleConfig:
        """Load configuration for a specific module"""
        if module_name in self.configs:
            return self.configs[module_name]

        # Load environment variables first
        self.load_env()

        # Try multiple config locations
        config_paths = [
            self.root_path / f"{module_name}/config.yaml",
            self.root_path / f"{module_name}/config.yml",
            self.root_path / f"{module_name}/config.json",
            self.root_path / f"config/{module_name}.yaml",
            self.root_path / f"config/{module_name}.yml",
            self.root_path / f"config/{module_name}.json",
        ]

        config = ModuleConfig(name=module_name)

        # Load from file
        for path in config_paths:
            if path.exists():
                if path.suffix in [".yaml", ".yml"]:
                    with open(path) as f:
                        data = yaml.safe_load(f) or {}
                elif path.suffix == ".json":
                    with open(path) as f:
                        data = json.load(f)
                else:
                    continue

                config.enabled = data.get("enabled", True)
                config.version = data.get("version", "1.0.0")
                config.settings = data.get("settings", {})
                config.dependencies = data.get("dependencies", [])
                break

        # Override with environment variables
        self._apply_env_overrides(config)

        # Cache and return
        self.configs[module_name] = config
        return config

    def _apply_env_overrides(self, config: ModuleConfig) -> None:
        """Apply environment variable overrides"""
        prefix = f"LUKHAS_{config.name.upper()}_"

        for key, value in os.environ.items():
            if key.startswith(prefix):
                # Convert LUKHAS_MODULE_SETTING_NAME to setting.name
                setting_key = key[len(prefix) :].lower().replace("_", ".")

                # Try to parse value
                try:
                    parsed_value = json.loads(value)
                except json.JSONDecodeError:
                    # Keep as string if not valid JSON
                    parsed_value = value

                config.set(setting_key, parsed_value)

    def load_global_config(self) -> dict[str, Any]:
        """Load global LUKHAS configuration"""
        self.load_env()

        global_config = {
            "project_root": str(self.root_path),
            "environment": os.getenv("LUKHAS_ENV", "development"),
            "debug": os.getenv("LUKHAS_DEBUG", "false").lower() == "true",
            "log_level": os.getenv("LUKHAS_LOG_LEVEL", "INFO"),
        }

        # Load from main config file
        main_config_paths = [
            self.root_path / "lukhas_config.yaml",
            self.root_path / "lukhas_config.yml",
            self.root_path / "lukhas_config.json",
            self.root_path / "config.yaml",
            self.root_path / "config.yml",
            self.root_path / "config.json",
        ]

        for path in main_config_paths:
            if path.exists():
                if path.suffix in [".yaml", ".yml"]:
                    with open(path) as f:
                        data = yaml.safe_load(f) or {}
                elif path.suffix == ".json":
                    with open(path) as f:
                        data = json.load(f)
                else:
                    continue

                global_config.update(data)
                break

        return global_config

    def get_database_config(self) -> dict[str, Any]:
        """Get database configuration"""
        self.load_env()

        return {
            "host": os.getenv("POSTGRES_HOST", "localhost"),
            "port": int(os.getenv("POSTGRES_PORT", "5432")),
            "database": os.getenv("POSTGRES_DB", "lukhas"),
            "user": os.getenv("POSTGRES_USER", "lukhas"),
            "password": os.getenv("POSTGRES_PASSWORD", ""),
        }

    def get_redis_config(self) -> dict[str, Any]:
        """Get Redis configuration"""
        self.load_env()

        return {
            "host": os.getenv("REDIS_HOST", "localhost"),
            "port": int(os.getenv("REDIS_PORT", "6379")),
            "password": os.getenv("REDIS_PASSWORD", ""),
            "db": int(os.getenv("REDIS_DB", "0")),
        }

    def get_guardian_config(self) -> dict[str, Any]:
        """Get Guardian system configuration"""
        self.load_env()

        return {
            "ethics_level": os.getenv("GUARDIAN_ETHICS_LEVEL", "STRICT"),
            "consensus_required": int(os.getenv("GUARDIAN_CONSENSUS_REQUIRED", "3")),
            "timeout_seconds": int(os.getenv("GUARDIAN_TIMEOUT", "30")),
            "cache_ttl": int(os.getenv("GUARDIAN_CACHE_TTL", "60")),
        }


# Global instance
_config_loader: Optional[ConfigLoader] = None


def get_config_loader() -> ConfigLoader:
    """Get global config loader instance"""
    global _config_loader  # noqa: PLW0603
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader


@lru_cache(maxsize=128)
def get_config(module_name: str) -> ModuleConfig:
    """Get configuration for a module (cached)"""
    return get_config_loader().load_module_config(module_name)


def get_global_config() -> dict[str, Any]:
    """Get global LUKHAS configuration"""
    return get_config_loader().load_global_config()


def get_setting(key: str, default: Any = None, module: Optional[str] = None) -> Any:
    """
    Get a configuration setting.

    Args:
        key: Setting key (supports dot notation)
        default: Default value if not found
        module: Module name (if None, searches global config)

    Returns:
        Configuration value
    """
    if module:
        config = get_config(module)
        return config.get(key, default)
    else:
        global_config = get_global_config()
        keys = key.split(".")
        value = global_config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value


# Create default instances that imports expect
config = get_config_loader()
settings = get_global_config()
