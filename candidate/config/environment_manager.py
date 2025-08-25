import os
from pathlib import Path
from typing import Optional, Dict, Any

import structlog
from pydantic import ValidationError

from candidate.config.configuration_manager import ConfigurationManager
from candidate.config.settings_validator import LukhasSettings, validate_settings

logger = structlog.get_logger(__name__)


class EnvironmentManager:
    """
    Manages loading of environment-specific configurations.
    Detects the current environment and loads the corresponding configuration file,
    then validates it.
    """

    def __init__(self, config_dir: Path):
        """
        Initializes the EnvironmentManager with a directory containing config files.
        Args:
            config_dir: The path to the directory where config files (e.g., development.yaml) are stored.
        """
        if not config_dir.is_dir():
            logger.error("Configuration directory not found", path=str(config_dir))
            raise FileNotFoundError(f"Configuration directory not found: {config_dir}")
        self.config_dir = config_dir
        self.config_manager = ConfigurationManager()
        self.settings: Optional[LukhasSettings] = None

    def load_config(self, env: Optional[str] = None) -> LukhasSettings:
        """
        Loads and validates the configuration for a specific environment.
        The environment is determined by the 'env' parameter or the 'APP_ENV' environment variable.

        Args:
            env: The environment to load (e.g., 'development', 'production'). Defaults to `os.getenv("APP_ENV", "development")`.

        Returns:
            A validated LukhasSettings object.

        Raises:
            FileNotFoundError: If the configuration file for the environment is not found.
            ValidationError: If the configuration is invalid.
        """
        if env is None:
            env = os.getenv("APP_ENV", "development")

        logger.info("Loading configuration for environment", environment=env)

        config_file = self.config_dir / f"{env}.yaml"

        self.config_manager.load_config(config_file)

        try:
            # The config is stored in the private _config attribute
            config_dict = self.config_manager._config
            validated_settings = validate_settings(config_dict)
            self.settings = validated_settings
            logger.info("Configuration validated successfully for environment", environment=env)
            return self.settings
        except ValidationError as e:
            logger.error("Configuration validation failed", environment=env, errors=e.errors())
            raise
        except Exception as e:
            logger.error("An unexpected error occurred during configuration loading", error=str(e))
            raise

    def get_settings(self) -> Optional[LukhasSettings]:
        """
        Returns the currently loaded settings.
        """
        return self.settings


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

    # Create a dummy config directory and files for testing
    dummy_dir = Path("temp_config")
    dummy_dir.mkdir(exist_ok=True)

    # Create a dummy development.yaml
    # A simplified version for demonstration
    dummy_dev_config = """
    system:
      name: "LUKHAS-DEV"
      version: "1.0.0-dev"
      environment: "development"
    logging:
      level: "DEBUG"
      format: "text"
      outputs:
        - type: "stdout"
    # Faking the rest of the structure to pass validation
    agi: {self_improvement: {enabled: false, learning_rate: 0.0, improvement_cycle_minutes: 0, max_concurrent_goals: 0}, autonomous_learning: {enabled: false, curiosity_level: 0.0, risk_tolerance: 0.0, knowledge_validation_threshold: 0.0}, goal_alignment: {enabled: false, core_values: {beneficence: 0, non_maleficence: 0, autonomy: 0, justice: 0, transparency: 0}}, consciousness: {coherence_threshold: 0, awareness_update_hz: 0, reflection_depth: 0, stream_enabled: false, stream_port: 0}}
    performance: {max_workers: 1, batch_size: 1, cache_size_mb: 1, optimization: {jit_compilation: false, parallel_processing: false, gpu_acceleration: false}}
    memory: {storage_backend: "local", max_memory_gb: 1, episodic: {retention_days: 1, compression_enabled: false}, fold_system: {max_folds: 1, fold_threshold: 0.0}}
    security: {encryption: {algorithm: "none", key_rotation_days: 0}, authentication: {method: "none", token_expiry_hours: 0}, rate_limiting: {requests_per_minute: 0, burst_size: 0}, audit: {enabled: false, retention_days: 0}}
    telemetry: {enabled: false, metrics: {retention_hours: 0, aggregation_interval_seconds: 0}, alerts: {email_enabled: false}, exporters: []}
    api: {host: "localhost", port: 8000, cors: {enabled: false, allowed_origins: []}, rate_limits: {dream_generation: 0, memory_operations: 0, consciousness_queries: 0}}
    deployment: {replicas: 1, resources: {cpu_request: "0", cpu_limit: "0", memory_request: "0", memory_limit: "0"}, autoscaling: {enabled: false, min_replicas: 1, max_replicas: 1, target_cpu_utilization: 0}, health_checks: {liveness_probe: {path: "", interval_seconds: 0}, readiness_probe: {path: "", interval_seconds: 0}}}
    features: {personality_enhancement: false, quantum_processing: false, adversarial_learning: false, emergent_behavior_detection: false}
    database: {type: "sqlite", connection: {host: "localhost", port: 0, database: "dev.db", ssl_mode: "prefer"}, pool: {min_connections: 1, max_connections: 1}}
    cache: {type: "local", nodes: [], options: {}}
    queue: {type: "local", brokers: [], topics: {}}
    """
    (dummy_dir / "development.yaml").write_text(dummy_dev_config)

    print("--- Loading development environment ---")
    os.environ["APP_ENV"] = "development"
    env_manager = EnvironmentManager(dummy_dir)
    try:
        dev_settings = env_manager.load_config()
        print("Development settings loaded and validated successfully.")
        print(f"System Name: {dev_settings.system.name}")
        print(f"Log Level: {dev_settings.logging.level}")
    except (FileNotFoundError, ValidationError) as e:
        print(f"Error loading development settings: {e}")

    # Clean up
    (dummy_dir / "development.yaml").unlink()
    dummy_dir.rmdir()
    del os.environ["APP_ENV"]
