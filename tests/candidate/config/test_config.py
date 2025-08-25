import os
import yaml
import pytest
from pathlib import Path
from pydantic import ValidationError

from candidate.config.configuration_manager import ConfigurationManager
from candidate.config.settings_validator import LukhasSettings, validate_settings
from candidate.config.environment_manager import EnvironmentManager

@pytest.fixture(scope="module")
def config_dir(tmpdir_factory):
    """Creates a temporary directory with dummy config files for testing."""
    tmpdir = tmpdir_factory.mktemp("config")

    # Dummy development.yaml
    dev_config = {
        "system": {"name": "LUKHAS-DEV", "version": "1.0-dev", "environment": "development"},
        "logging": {"level": "DEBUG", "format": "text", "outputs": [{"type": "stdout"}]},
        "database": {"type": "sqlite", "connection": {"host": "${DB_HOST:localhost}", "port": 5432, "database": "dev.db", "ssl_mode": "prefer"}, "pool": {"min_connections": 1, "max_connections": 5}},
        # Add other sections with dummy data to satisfy the validator
        "agi": {"self_improvement": {"enabled": False, "learning_rate": 0.0, "improvement_cycle_minutes": 0, "max_concurrent_goals": 0}, "autonomous_learning": {"enabled": False, "curiosity_level": 0.0, "risk_tolerance": 0.0, "knowledge_validation_threshold": 0.0}, "goal_alignment": {"enabled": False, "core_values": {"beneficence": 0, "non_maleficence": 0, "autonomy": 0, "justice": 0, "transparency": 0}}, "consciousness": {"coherence_threshold": 0, "awareness_update_hz": 0, "reflection_depth": 0, "stream_enabled": False, "stream_port": 0}},
        "performance": {"max_workers": 1, "batch_size": 1, "cache_size_mb": 1, "optimization": {"jit_compilation": False, "parallel_processing": False, "gpu_acceleration": False}},
        "memory": {"storage_backend": "local", "max_memory_gb": 1, "episodic": {"retention_days": 1, "compression_enabled": False}, "fold_system": {"max_folds": 1, "fold_threshold": 0.0}},
        "security": {"encryption": {"algorithm": "none", "key_rotation_days": 0}, "authentication": {"method": "none", "token_expiry_hours": 0}, "rate_limiting": {"requests_per_minute": 0, "burst_size": 0}, "audit": {"enabled": False, "retention_days": 0}},
        "telemetry": {"enabled": False, "metrics": {"retention_hours": 0, "aggregation_interval_seconds": 0}, "alerts": {"email_enabled": False}, "exporters": []},
        "api": {"host": "localhost", "port": 8000, "cors": {"enabled": False, "allowed_origins": []}, "rate_limits": {"dream_generation": 0, "memory_operations": 0, "consciousness_queries": 0}},
        "deployment": {"replicas": 1, "resources": {"cpu_request": "0", "cpu_limit": "0", "memory_request": "0", "memory_limit": "0"}, "autoscaling": {"enabled": False, "min_replicas": 1, "max_replicas": 1, "target_cpu_utilization": 0}, "health_checks": {"liveness_probe": {"path": "", "interval_seconds": 0}, "readiness_probe": {"path": "", "interval_seconds": 0}}},
        "features": {"personality_enhancement": False, "quantum_processing": False, "adversarial_learning": False, "emergent_behavior_detection": False},
        "cache": {"type": "local", "nodes": [], "options": {}},
        "queue": {"type": "local", "brokers": [], "topics": {}},
    }
    with open(tmpdir.join("development.yaml"), "w") as f:
        yaml.dump(dev_config, f)

    # Dummy production.yaml
    prod_config = dev_config.copy()
    prod_config["system"]["environment"] = "production"
    prod_config["logging"]["level"] = "INFO"
    with open(tmpdir.join("production.yaml"), "w") as f:
        yaml.dump(prod_config, f)

    # Invalid config
    invalid_config = {"system": {"name": "invalid"}}
    with open(tmpdir.join("invalid.yaml"), "w") as f:
        yaml.dump(invalid_config, f)

    return Path(str(tmpdir))


class TestConfigurationManager:
    def test_load_config(self, config_dir):
        cm = ConfigurationManager()
        cm.load_config(config_dir / "development.yaml")
        assert cm.get("system.name") == "LUKHAS-DEV"

    def test_resolve_env_vars(self, config_dir):
        os.environ["DB_HOST"] = "test_host"
        cm = ConfigurationManager(config_dir / "development.yaml")
        assert cm.get("database.connection.host") == "test_host"
        del os.environ["DB_HOST"]

    def test_get_value(self, config_dir):
        cm = ConfigurationManager(config_dir / "development.yaml")
        assert cm["system.environment"] == "development"
        assert cm.get("database.pool.max_connections") == 5
        assert cm.get("non.existent.key", "default") == "default"

class TestSettingsValidator:
    def test_valid_settings(self, config_dir):
        with open(config_dir / "development.yaml") as f:
            config_dict = yaml.safe_load(f)

        settings = validate_settings(config_dict)
        assert isinstance(settings, LukhasSettings)
        assert settings.system.environment == "development"

    def test_invalid_settings(self, config_dir):
        with open(config_dir / "invalid.yaml") as f:
            config_dict = yaml.safe_load(f)

        with pytest.raises(ValidationError):
            validate_settings(config_dict)

class TestEnvironmentManager:
    def test_load_by_env_var(self, config_dir):
        os.environ["APP_ENV"] = "production"
        env_manager = EnvironmentManager(config_dir)
        settings = env_manager.load_config()
        assert settings.system.environment == "production"
        del os.environ["APP_ENV"]

    def test_load_by_param(self, config_dir):
        env_manager = EnvironmentManager(config_dir)
        settings = env_manager.load_config(env="development")
        assert settings.system.environment == "development"

    def test_file_not_found(self, config_dir):
        env_manager = EnvironmentManager(config_dir)
        with pytest.raises(FileNotFoundError):
            env_manager.load_config(env="staging")
