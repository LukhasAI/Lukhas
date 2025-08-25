import os
import re
import yaml
from pathlib import Path
from typing import Any, Dict, Optional

import structlog

logger = structlog.get_logger(__name__)

ENV_VAR_MATCHER = re.compile(r"\${([^}]+)}")


class ConfigurationManager:
    """
    A dynamic configuration manager that loads settings from YAML files,
    resolves environment variables, and provides easy access to configuration values.
    """

    def __init__(self, config_path: Optional[Path] = None):
        self._config: Dict[str, Any] = {}
        if config_path:
            self.load_config(config_path)

    def load_config(self, config_path: Path) -> None:
        """
        Loads a YAML configuration file from the given path.
        """
        logger.info("Loading configuration", path=str(config_path))
        if not config_path.is_file():
            logger.error("Configuration file not found", path=str(config_path))
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        try:
            with open(config_path, 'r') as f:
                raw_config = yaml.safe_load(f)
            self._config = self._resolve_env_vars(raw_config)
            logger.info("Configuration loaded successfully", path=str(config_path))
        except yaml.YAMLError as e:
            logger.error("Error parsing YAML file", path=str(config_path), error=str(e))
            raise
        except Exception as e:
            logger.error("Failed to load configuration", path=str(config_path), error=str(e))
            raise

    def _resolve_env_vars(self, config_item: Any) -> Any:
        """

        Recursively traverses the configuration and resolves environment variables.
        """
        if isinstance(config_item, dict):
            return {k: self._resolve_env_vars(v) for k, v in config_item.items()}
        elif isinstance(config_item, list):
            return [self._resolve_env_vars(i) for i in config_item]
        elif isinstance(config_item, str):
            return self._substitute_env_var(config_item)
        else:
            return config_item

    def _substitute_env_var(self, value: str) -> str:
        """
        Substitutes an environment variable placeholder in a string.
        Format: ${VAR_NAME} or ${VAR_NAME:default_value}
        """
        match = ENV_VAR_MATCHER.search(value)
        if not match:
            return value

        full_match, var_spec = match.group(0), match.group(1)
        var_name, _, default_value = var_spec.partition(':')

        env_value = os.getenv(var_name)
        if env_value is not None:
            return value.replace(full_match, env_value)
        elif default_value:
            return value.replace(full_match, default_value)
        else:
            logger.warning(
                "Environment variable not set and no default provided",
                variable=var_name,
            )
            return value

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieves a configuration value using dot notation.
        e.g., "database.connection.host"
        """
        keys = key.split('.')
        value = self._config
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def __getitem__(self, key: str) -> Any:
        """
        Allows dictionary-style access to configuration values.
        """
        value = self.get(key)
        if value is None:
            raise KeyError(f"Configuration key not found: {key}")
        return value

if __name__ == '__main__':
    # Example Usage
    structlog.configure(
        processors=[
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.dev.ConsoleRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Create a dummy config file for testing
    dummy_config_content = """
    database:
      host: ${DB_HOST:localhost}
      port: ${DB_PORT:5432}
      user: ${DB_USER}
    api:
      key: "some_static_key"
    """
    dummy_config_path = Path("dummy_config.yaml")
    with open(dummy_config_path, "w") as f:
        f.write(dummy_config_content)

    # Set some environment variables for the demo
    os.environ["DB_USER"] = "jules"
    os.environ["DB_PORT"] = "5433"

    print("--- Loading configuration ---")
    config_manager = ConfigurationManager(dummy_config_path)

    print("\n--- Accessing configuration ---")
    print(f"Database Host: {config_manager.get('database.host')}")
    print(f"Database Port: {config_manager.get('database.port')}")
    print(f"Database User: {config_manager['database.user']}")
    print(f"API Key: {config_manager.get('api.key')}")
    print(f"Non-existent key with default: {config_manager.get('non.existent', 'default_value')}")

    # Clean up dummy file and env vars
    dummy_config_path.unlink()
    del os.environ["DB_USER"]
    del os.environ["DB_PORT"]
