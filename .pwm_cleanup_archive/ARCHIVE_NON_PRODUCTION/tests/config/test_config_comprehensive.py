"""Comprehensive tests for LUKHAS config module."""

import pytest

from config import (
    Settings,
    settings,
    validate_config,
    validate_optional_config,
)


class TestSettings:
    """Test the Settings class."""

    def test_default_values(self):
        """Test that default values are set correctly."""
        s = Settings()
        assert s.DATABASE_URL == "postgresql://user:pass@localhost/db"
        assert s.REDIS_URL == "redis://localhost:6379"
        assert s.LOG_LEVEL == "INFO"
        assert s.DEBUG is False
        assert s.OPENAI_API_KEY is None

    def test_custom_values(self):
        """Test initialization with custom values."""
        s = Settings(
            OPENAI_API_KEY="test-key",
            DATABASE_URL="sqlite:///test.db",
            DEBUG=True,
            LOG_LEVEL="DEBUG",
        )
        assert s.OPENAI_API_KEY == "test-key"
        assert s.DATABASE_URL == "sqlite:///test.db"
        assert s.DEBUG is True
        assert s.LOG_LEVEL == "DEBUG"

    def test_environment_override(self, monkeypatch):
        """Test that environment variables override defaults."""
        monkeypatch.setenv("OPENAI_API_KEY", "env-key")
        monkeypatch.setenv("DATABASE_URL", "sqlite:///env.db")
        monkeypatch.setenv("DEBUG", "true")
        monkeypatch.setenv("LOG_LEVEL", "WARNING")

        s = Settings()
        assert s.OPENAI_API_KEY == "env-key"
        assert s.DATABASE_URL == "sqlite:///env.db"
        assert s.DEBUG is True
        assert s.LOG_LEVEL == "WARNING"

    def test_debug_parsing(self, monkeypatch):
        """Test that DEBUG environment variable is parsed correctly."""
        test_cases = [
            ("true", True),
            ("True", True),
            ("TRUE", True),
            ("false", False),
            ("False", False),
            ("FALSE", False),
            ("", False),
            ("invalid", False),
        ]

        for env_value, expected in test_cases:
            monkeypatch.setenv("DEBUG", env_value)
            s = Settings()
            assert expected == s.DEBUG, f"Failed for DEBUG={env_value}"


class TestValidation:
    """Test validation functions."""

    def test_validate_config_success(self):
        """Test successful config validation."""
        s = Settings(
            OPENAI_API_KEY="test-key",
            DATABASE_URL="postgresql://prod:pass@db.example.com/lukhas",
            REDIS_URL="redis://redis.example.com:6379",
        )
        # Should not raise any exception
        validate_config(s)

    def test_validate_config_missing_openai_key(self):
        """Test validation failure when OPENAI_API_KEY is missing."""
        s = Settings(OPENAI_API_KEY=None)
        with pytest.raises(ValueError, match="OPENAI_API_KEY must be set"):
            validate_config(s)

    def test_validate_config_empty_database_url(self):
        """Test validation failure when DATABASE_URL is empty."""
        s = Settings(OPENAI_API_KEY="test", DATABASE_URL="")
        with pytest.raises(ValueError, match="DATABASE_URL must be set"):
            validate_config(s)

    def test_validate_config_empty_redis_url(self):
        """Test validation failure when REDIS_URL is empty."""
        s = Settings(OPENAI_API_KEY="test", REDIS_URL="")
        with pytest.raises(ValueError, match="REDIS_URL must be set"):
            validate_config(s)

    def test_validate_optional_config_defaults(self):
        """Test optional config validation with defaults."""
        s = Settings()
        status = validate_optional_config(s)

        expected = {
            "openai_configured": False,
            "database_configured": False,  # localhost in URL
            "redis_configured": False,  # localhost in URL
            "debug_mode": False,
            "log_level": "INFO",
        }
        assert status == expected

    def test_validate_optional_config_production(self):
        """Test optional config validation with production settings."""
        s = Settings(
            OPENAI_API_KEY="sk-prod-key",
            DATABASE_URL="postgresql://user:pass@prod-db.example.com/lukhas",
            REDIS_URL="redis://prod-redis.example.com:6379",
            DEBUG=True,
            LOG_LEVEL="DEBUG",
        )
        status = validate_optional_config(s)

        expected = {
            "openai_configured": True,
            "database_configured": True,
            "redis_configured": True,
            "debug_mode": True,
            "log_level": "DEBUG",
        }
        assert status == expected


class TestGlobalSettings:
    """Test the global settings instance."""

    def test_global_settings_instance(self):
        """Test that the global settings instance works."""
        # Global settings should be accessible
        assert hasattr(settings, "DATABASE_URL")
        assert hasattr(settings, "REDIS_URL")
        assert hasattr(settings, "LOG_LEVEL")
        assert hasattr(settings, "DEBUG")

    def test_global_settings_type(self):
        """Test that global settings is a Settings instance."""
        assert isinstance(settings, Settings)


class TestIntegration:
    """Integration tests for config system."""

    def test_full_config_flow(self, monkeypatch):
        """Test complete configuration workflow."""
        # Set up production-like environment
        monkeypatch.setenv("OPENAI_API_KEY", "sk-prod-123")
        monkeypatch.setenv(
            "DATABASE_URL", "postgresql://lukhas:secret@db.prod.com/lukhas_db"
        )
        monkeypatch.setenv("REDIS_URL", "redis://cache.prod.com:6379")
        monkeypatch.setenv("LOG_LEVEL", "WARNING")
        monkeypatch.setenv("DEBUG", "false")

        # Create new settings instance
        prod_settings = Settings()

        # Validate configuration
        validate_config(prod_settings)

        # Check optional config status
        status = validate_optional_config(prod_settings)

        assert status["openai_configured"] is True
        assert status["database_configured"] is True
        assert status["redis_configured"] is True
        assert status["debug_mode"] is False
        assert status["log_level"] == "WARNING"

    def test_development_config_flow(self, monkeypatch):
        """Test development configuration workflow."""
        # Clear environment
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        # Create development settings
        dev_settings = Settings(DEBUG=True, LOG_LEVEL="DEBUG")

        # Should fail validation (no API key)
        with pytest.raises(ValueError):
            validate_config(dev_settings)

        # Check status
        status = validate_optional_config(dev_settings)
        assert status["openai_configured"] is False
        assert status["debug_mode"] is True
        assert status["log_level"] == "DEBUG"
