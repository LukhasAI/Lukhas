"""
Environment Manager - BATCH 7 Completion
"""
import os
from enum import Enum
from typing import Dict, Any
from pathlib import Path

class Environment(Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

class EnvironmentManager:
    """Manage environment-specific configurations"""

    def __init__(self):
        self.current_env = self._detect_environment()
        self.config_dir = Path("candidate/config/environments")
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def _detect_environment(self) -> Environment:
        """Detect current environment"""
        env_name = os.getenv("LUKHAS_ENV", "development").lower()
        try:
            return Environment(env_name)
        except ValueError:
            return Environment.DEVELOPMENT

    def get_environment_config(self) -> Dict[str, Any]:
        """Get environment-specific configuration"""
        config_file = self.config_dir / f"{self.current_env.value}.json"

        if config_file.exists():
            import json
            with open(config_file, 'r') as f:
                return json.load(f)

        # Default configurations
        return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for current environment"""
        base_config = {
            "logging_level": "INFO",
            "debug_mode": False,
            "features": {
                "ai_analysis": True,
                "matrix_instrumentation": True
            }
        }

        if self.current_env == Environment.DEVELOPMENT:
            base_config.update({
                "logging_level": "DEBUG",
                "debug_mode": True,
                "features": {"ai_analysis": True}
            })
        elif self.current_env == Environment.PRODUCTION:
            base_config.update({
                "logging_level": "WARNING",
                "debug_mode": False,
                "features": {"performance_monitoring": True}
            })

        return base_config

    def set_environment(self, env: Environment):
        """Set current environment"""
        self.current_env = env
        os.environ["LUKHAS_ENV"] = env.value

# Usage example
if __name__ == "__main__":
    env_manager = EnvironmentManager()
    config = env_manager.get_environment_config()
    print(f"Environment: {env_manager.current_env}")
    print(f"Config: {config}")
