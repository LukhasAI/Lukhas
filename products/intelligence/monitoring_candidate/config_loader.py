#!/usr/bin/env python3
"""
LUKHAS  Monitoring Configuration Loader
==========================================
Loads monitoring configuration with environment variable overrides
"""
import os
from pathlib import Path
from typing import Any, Optional, Union

import yaml


def load_config(config_path: Optional[str] = None) -> dict[str, Any]:
    """
    Load monitoring configuration with environment variable overrides.

    Args:
        config_path: Path to the YAML config file. If None, uses default.

    Returns:
        Dict containing the complete configuration with overrides applied
    """
    # Default config path
    if config_path is None:
        config_path = Path(__file__).parent / "monitoring_config.yaml"

    # Load base configuration from YAML
    config = {}
    if Path(config_path).exists():
        with open(config_path) as f:
            config = yaml.safe_load(f) or {}

    # Apply environment variable overrides
    config = _apply_environment_overrides(config)

    return config


def _apply_environment_overrides(config: dict[str, Any]) -> dict[str, Any]:
    """Apply environment variable overrides to configuration."""

    # Dashboard Configuration
    config.setdefault("unified_dashboard", {})
    config["unified_dashboard"]["host"] = os.getenv(
        "LUKHAS_DASHBOARD_HOST", config["unified_dashboard"].get("host", "0.0.0.0")
    )
    config["unified_dashboard"]["port"] = int(
        os.getenv("LUKHAS_DASHBOARD_PORT", str(config["unified_dashboard"].get("port", 3000)))
    )
    config["unified_dashboard"]["refresh_rate"] = int(
        os.getenv(
            "LUKHAS_DASHBOARD_REFRESH",
            str(config["unified_dashboard"].get("refresh_rate", 5)),
        )
    )
    config["unified_dashboard"]["enable_auth"] = _str_to_bool(
        os.getenv(
            "LUKHAS_DASHBOARD_AUTH",
            str(config["unified_dashboard"].get("enable_auth", False)),
        )
    )

    # Meta Dashboard Configuration
    config.setdefault("meta_dashboard", {})
    config["meta_dashboard"]["port"] = int(
        os.getenv(
            "LUKHAS_META_DASHBOARD_PORT",
            str(config["meta_dashboard"].get("port", 5042)),
        )
    )
    config["meta_dashboard"]["refresh_rate"] = int(
        os.getenv("LUKHAS_META_REFRESH", str(config["meta_dashboard"].get("refresh_rate", 15)))
    )

    # Metrics Collection
    config.setdefault("metrics_collection", {})
    config["metrics_collection"]["enabled"] = _str_to_bool(
        os.getenv(
            "LUKHAS_METRICS_ENABLED",
            str(config["metrics_collection"].get("enabled", True)),
        )
    )
    config["metrics_collection"]["interval"] = int(
        os.getenv(
            "LUKHAS_METRICS_INTERVAL",
            str(config["metrics_collection"].get("interval", 1)),
        )
    )
    config["metrics_collection"]["retention_hours"] = int(
        os.getenv(
            "LUKHAS_METRICS_RETENTION",
            str(config["metrics_collection"].get("retention_hours", 24)),
        )
    )

    # Security Configuration
    config.setdefault("security", {})
    config["security"]["api_key_required"] = _str_to_bool(
        os.getenv(
            "LUKHAS_API_KEY_REQUIRED",
            str(config["security"].get("api_key_required", False)),
        )
    )
    config["security"]["api_key"] = os.getenv("LUKHAS_MONITORING_API_KEY", config["security"].get("api_key", ""))

    # Rate limits
    config["security"].setdefault("rate_limits", {})
    config["security"]["rate_limits"]["api_requests_per_minute"] = int(
        os.getenv(
            "LUKHAS_RATE_LIMIT_API",
            str(config["security"]["rate_limits"].get("api_requests_per_minute", 1000)),
        )
    )

    # Database Configuration
    config.setdefault("performance", {})
    config["performance"].setdefault("database", {})
    config["performance"]["database"]["url"] = os.getenv(
        "LUKHAS_DATABASE_URL",
        config["performance"]["database"].get("url", "sqlite:///monitoring.db"),
    )
    config["performance"]["database"]["pool_size"] = int(
        os.getenv(
            "LUKHAS_DB_POOL_SIZE",
            str(config["performance"]["database"].get("pool_size", 10)),
        )
    )

    # Logging Configuration
    config.setdefault("logging", {})
    config["logging"]["level"] = os.getenv("LUKHAS_LOG_LEVEL", config["logging"].get("level", "INFO")).upper()

    # File paths with environment overrides
    config["logging"].setdefault("files", {})
    config["logging"]["files"]["main"] = os.getenv(
        "LUKHAS_LOG_FILE", config["logging"]["files"].get("main", "logs/monitoring.log")
    )

    # Data Storage
    config.setdefault("data_storage", {})
    config["data_storage"]["metrics_file"] = os.getenv(
        "LUKHAS_METRICS_FILE",
        config["data_storage"].get("metrics_file", "data/metrics.jsonl"),
    )
    config["data_storage"]["alerts_file"] = os.getenv(
        "LUKHAS_ALERTS_FILE",
        config["data_storage"].get("alerts_file", "data/alerts.jsonl"),
    )

    # Integration Configurations
    config.setdefault("integrations", {})

    # Prometheus
    config["integrations"].setdefault("prometheus", {})
    config["integrations"]["prometheus"]["enabled"] = _str_to_bool(
        os.getenv(
            "LUKHAS_PROMETHEUS_ENABLED",
            str(config["integrations"]["prometheus"].get("enabled", False)),
        )
    )
    config["integrations"]["prometheus"]["port"] = int(
        os.getenv(
            "LUKHAS_PROMETHEUS_PORT",
            str(config["integrations"]["prometheus"].get("port", 9090)),
        )
    )

    # Grafana
    config["integrations"].setdefault("grafana", {})
    config["integrations"]["grafana"]["enabled"] = _str_to_bool(
        os.getenv(
            "LUKHAS_GRAFANA_ENABLED",
            str(config["integrations"]["grafana"].get("enabled", False)),
        )
    )
    config["integrations"]["grafana"]["host"] = os.getenv(
        "LUKHAS_GRAFANA_HOST",
        config["integrations"]["grafana"].get("host", "localhost"),
    )
    config["integrations"]["grafana"]["port"] = int(
        os.getenv(
            "LUKHAS_GRAFANA_PORT",
            str(config["integrations"]["grafana"].get("port", 3001)),
        )
    )

    # External Services
    config["integrations"].setdefault("datadog", {})
    config["integrations"]["datadog"]["enabled"] = _str_to_bool(
        os.getenv(
            "LUKHAS_DATADOG_ENABLED",
            str(config["integrations"]["datadog"].get("enabled", False)),
        )
    )
    config["integrations"]["datadog"]["api_key"] = os.getenv(
        "DATADOG_API_KEY", config["integrations"]["datadog"].get("api_key", "")
    )

    # Slack
    config["integrations"].setdefault("slack", {})
    config["integrations"]["slack"]["enabled"] = _str_to_bool(
        os.getenv(
            "LUKHAS_SLACK_ENABLED",
            str(config["integrations"]["slack"].get("enabled", False)),
        )
    )
    config["integrations"]["slack"]["webhook_url"] = os.getenv(
        "SLACK_WEBHOOK_URL", config["integrations"]["slack"].get("webhook_url", "")
    )
    config["integrations"]["slack"]["channel"] = os.getenv(
        "SLACK_CHANNEL",
        config["integrations"]["slack"].get("channel", "#lukhas-alerts"),
    )

    # PagerDuty
    config["integrations"].setdefault("pagerduty", {})
    config["integrations"]["pagerduty"]["enabled"] = _str_to_bool(
        os.getenv(
            "LUKHAS_PAGERDUTY_ENABLED",
            str(config["integrations"]["pagerduty"].get("enabled", False)),
        )
    )
    config["integrations"]["pagerduty"]["routing_key"] = os.getenv(
        "PAGERDUTY_ROUTING_KEY",
        config["integrations"]["pagerduty"].get("routing_key", ""),
    )

    # Development/Production Environment Detection
    environment = os.getenv("LUKHAS_ENV", "development").lower()

    if environment == "production":
        # Apply production overrides
        config.setdefault("production", {})
        config["production"]["ssl_enabled"] = _str_to_bool(
            os.getenv(
                "LUKHAS_SSL_ENABLED",
                str(config["production"].get("ssl_enabled", False)),
            )
        )
        config["production"]["ssl_cert"] = os.getenv("LUKHAS_SSL_CERT", config["production"].get("ssl_cert", ""))
        config["production"]["ssl_key"] = os.getenv("LUKHAS_SSL_KEY", config["production"].get("ssl_key", ""))

        # Production defaults (security-focused)
        config["security"]["api_key_required"] = True
        config["unified_dashboard"]["enable_auth"] = True
        config["security"]["cors"]["allowed_origins"] = os.getenv(
            "LUKHAS_CORS_ORIGINS", "https://yourdomain.com"
        ).split(",")

    # Development mode overrides
    config.setdefault("development", {})
    config["development"]["debug_mode"] = _str_to_bool(
        os.getenv("LUKHAS_DEBUG", str(config["development"].get("debug_mode", False)))
    )
    config["development"]["mock_data"] = _str_to_bool(
        os.getenv("LUKHAS_MOCK_DATA", str(config["development"].get("mock_data", False)))
    )

    return config


def _str_to_bool(value: Union[str, bool]) -> bool:
    """Convert string to boolean, handling common string representations."""
    if isinstance(value, bool):
        return value
    return str(value).lower() in ("true", "1", "yes", "on", "enabled")


def get_config_value(config: dict[str, Any], key_path: str, default: Any = None) -> Any:
    """
    Get a nested configuration value using dot notation.

    Args:
        config: Configuration dictionary
        key_path: Dot-separated path (e.g., "unified_dashboard.port")
        default: Default value if key not found

    Returns:
        Configuration value or default
    """
    keys = key_path.split(".")
    current = config

    try:
        for key in keys:
            current = current[key]
        return current
    except (KeyError, TypeError):
        return default


def validate_config(config: dict[str, Any]) -> dict[str, Any]:
    """
    Validate configuration and return validation results.

    Args:
        config: Configuration to validate

    Returns:
        Dict with validation status and any issues found
    """
    issues = []
    warnings = []

    # Validate required fields
    required_paths = [
        "unified_dashboard.port",
        "meta_dashboard.port",
        "logging.level",
    ]

    for path in required_paths:
        if get_config_value(config, path) is None:
            issues.append(f"Missing required configuration: {path}")

    # Check for common configuration issues
    dashboard_port = get_config_value(config, "unified_dashboard.port")
    meta_port = get_config_value(config, "meta_dashboard.port")

    if dashboard_port and meta_port and dashboard_port == meta_port:
        issues.append("unified_dashboard and meta_dashboard cannot use the same port")

    # Security checks
    if get_config_value(config, "security.api_key_required") and not get_config_value(config, "security.api_key"):
        warnings.append("API key is required but not configured")

    # Production readiness checks
    if os.getenv("LUKHAS_ENV", "development").lower() == "production":
        if not get_config_value(config, "unified_dashboard.enable_auth"):
            warnings.append("Authentication should be enabled in production")

        cors_origins = get_config_value(config, "security.cors.allowed_origins", [])
        if "*" in cors_origins:
            warnings.append("CORS should be restricted in production (not '*')")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "config_summary": {
            "dashboard_port": dashboard_port,
            "meta_port": meta_port,
            "auth_enabled": get_config_value(config, "unified_dashboard.enable_auth"),
            "metrics_enabled": get_config_value(config, "metrics_collection.enabled"),
            "environment": os.getenv("LUKHAS_ENV", "development"),
        },
    }


# Convenience function to load and validate config
def load_validated_config(
    config_path: Optional[str] = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Load configuration and return both config and validation results.

    Returns:
        Tuple of (config_dict, validation_dict)
    """
    config = load_config(config_path)
    validation = validate_config(config)
    return config, validation


if __name__ == "__main__":
    """CLI interface for configuration management."""
    import json
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--validate":
        config, validation = load_validated_config()

        print("LUKHAS  Monitoring Configuration Validation")
        print("=" * 50)

        if validation["valid"]:
            print("✅ Configuration is valid")
        else:
            print("❌ Configuration has issues:")
            for issue in validation["issues"]:
                print(f"  - {issue}")

        if validation["warnings"]:
            print("\n⚠️  Warnings:")
            for warning in validation["warnings"]:
                print(f"  - {warning}")

        print("\nConfiguration Summary:")
        print(json.dumps(validation["config_summary"], indent=2))

        sys.exit(0 if validation["valid"] else 1)

    elif len(sys.argv) > 1 and sys.argv[1] == "--show":
        config = load_config()
        print(json.dumps(config, indent=2))

    else:
        print("Usage:")
        print("  python config_loader.py --validate   # Validate configuration")
        print("  python config_loader.py --show       # Show current configuration")
        print("\nEnvironment Variables:")
        print("  LUKHAS_ENV                    # Environment: development/production")
        print("  LUKHAS_DASHBOARD_HOST         # Dashboard host")
        print("  LUKHAS_DASHBOARD_PORT         # Dashboard port")
        print("  LUKHAS_MONITORING_API_KEY     # API key for monitoring")
        print("  LUKHAS_DATABASE_URL           # Database connection string")
        print("  LUKHAS_LOG_LEVEL              # Logging level")
