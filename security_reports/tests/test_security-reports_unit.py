"""Unit tests for the security_reports configuration helpers."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from security_reports import SecurityReportsConfig, load_config
from security_reports.configuration import SecurityConfigurationError


CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "config.yaml"


def test_load_config_returns_secure_defaults():
    config = load_config(CONFIG_PATH)

    assert isinstance(config, SecurityReportsConfig)
    assert config.name == "security_reports"
    assert config.version == "1.0.0"
    assert config.performance_monitoring is True
    assert config.is_secure()


def test_load_config_disallows_debug_mode(temp_dir: Path) -> None:
    insecure_payload = {
        "module": {"name": "security_reports", "version": "1.0.0", "description": "test"},
        "runtime": {"log_level": "INFO", "debug_mode": True, "performance_monitoring": True},
    }

    insecure_config = temp_dir / "config.yaml"
    insecure_config.write_text(yaml.safe_dump(insecure_payload), encoding="utf-8")

    with pytest.raises(SecurityConfigurationError):
        load_config(insecure_config)


def test_is_secure_flags_low_log_levels():
    config = SecurityReportsConfig(
        name="security_reports",
        version="1.0.0",
        description="test",
        log_level="INFO",
        debug_mode=False,
        performance_monitoring=True,
    )

    assert config.is_secure()

    insecure = SecurityReportsConfig(
        name="security_reports",
        version="1.0.0",
        description="test",
        log_level="DEBUG",
        debug_mode=False,
        performance_monitoring=True,
    )

    assert not insecure.is_secure()
