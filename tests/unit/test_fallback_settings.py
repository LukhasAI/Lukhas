"""Validation tests for the fallback configuration system."""

from __future__ import annotations

from typing import Callable

from config import env as config_env, fallback_settings


def _simulate_import_error() -> Callable[[], None]:
    """Return a callable that raises ImportError for fallback validation tests."""

    def _raise() -> None:
        raise ImportError("Simulated centralized config failure")

    return _raise


def test_fallback_settings_applies_safe_defaults(monkeypatch, caplog) -> None:
    """Fallback settings should normalize unsafe environment overrides."""

    # ΛTAG: fallback_validation
    monkeypatch.setattr(config_env, "get_lukhas_config", _simulate_import_error())
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("DATABASE_URL", "")
    monkeypatch.setenv("REDIS_URL", "")
    monkeypatch.setenv("LOG_LEVEL", "trace")

    with caplog.at_level("WARNING"):
        fallback = fallback_settings.FallbackSettings()

    assert fallback.LOG_LEVEL == "WARNING"
    assert fallback.DATABASE_URL == "sqlite:///lukhas_fallback.db"
    assert fallback.REDIS_URL == "redis://localhost:6379"
    assert fallback.OPENAI_API_KEY is None

    summary = fallback.validation_summary
    assert summary["fallback_mode"] is True
    assert summary["log_level"] == "WARNING"
    assert summary["openai_configured"] is False
    assert summary["database_configured"] is False
    assert summary["redis_configured"] is False

    assert fallback.degraded_components == (
        "openai_configured",
        "database_configured",
        "redis_configured",
    )

    warning_messages = [record.message for record in caplog.records]
    assert any("Centralized config not available" in message for message in warning_messages)
    assert any("Fallback configuration degraded states detected" in message for message in warning_messages)


def test_fallback_settings_reports_stable_configuration(monkeypatch) -> None:
    """Fallback validation should report no degradation when inputs are healthy."""

    # ΛTAG: fallback_validation
    monkeypatch.setattr(config_env, "get_lukhas_config", _simulate_import_error())
    monkeypatch.setenv("OPENAI_API_KEY", "lukhas-test-key")
    monkeypatch.setenv("DATABASE_URL", "postgresql://lukhas-db.example.com:5432/lukhas")
    monkeypatch.setenv("REDIS_URL", "redis://cache.example.com:6379/0")
    monkeypatch.setenv("LOG_LEVEL", "info")

    fallback = fallback_settings.FallbackSettings()

    assert fallback.LOG_LEVEL == "INFO"
    assert fallback.degraded_components == ()

    summary = fallback.validation_summary
    assert summary["openai_configured"] is True
    assert summary["database_configured"] is True
    assert summary["redis_configured"] is True
    assert summary["log_level"] == "INFO"
