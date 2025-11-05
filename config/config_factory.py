#!/usr/bin/env python3
"""LUKHAS API Optimization - Configuration Factory

Centralized configuration management for all deployment environments
with dynamic environment detection, secrets management, and validation.

# ΛTAG: configuration_management, deployment_infrastructure, environment_configuration
"""

import logging
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Union

import yaml

logger = logging.getLogger(__name__)


class DeploymentEnvironment(Enum):
    """Supported deployment environments"""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    HIGH_PERFORMANCE = "high_performance"
    RESOURCE_CONSERVATIVE = "resource_conservative"


@dataclass
class RedisConfig:
    """Redis configuration"""

    url: str = "redis://localhost:6379/0"
    password: Optional[str] = None
    pool_size: int = 10
    timeout_seconds: int = 5
    retry_attempts: int = 3
    ssl_enabled: bool = False


@dataclass
class OptimizationConfig:
    """API optimization configuration"""

    strategy: str = "balanced"
    enable_rate_limiting: bool = True
    enable_caching: bool = True
    enable_analytics: bool = True
    cache_ttl_seconds: int = 3600
    rate_limit_window_seconds: int = 60
    max_cache_size_mb: int = 256
    max_concurrent_requests: int = 1000


@dataclass
class MiddlewareConfig:
    """Middleware pipeline configuration"""

    enable_security: bool = True
    enable_validation: bool = True
    enable_analytics: bool = True
    enable_optimization: bool = True
    max_request_size_mb: int = 10
    request_timeout_seconds: int = 30
    enable_compression: bool = False


@dataclass
class AnalyticsConfig:
    """Analytics and monitoring configuration"""

    enable_metrics: bool = True
    enable_alerts: bool = False
    enable_intelligence: bool = False
    retention_days: int = 7
    batch_size: int = 100
    export_interval_seconds: int = 60


@dataclass
class IntegrationConfig:
    """Main integration configuration"""

    mode: str = "development"
    enable_optimizer: bool = True
    enable_middleware: bool = True
    enable_analytics: bool = True
    enable_intelligent_routing: bool = False
    enable_predictive_caching: bool = False
    enable_auto_scaling: bool = False


@dataclass
class LoggingConfig:
    """Logging configuration"""

    level: str = "INFO"
    format: str = "structured"
    output: str = "console"
    file_path: Optional[str] = None
    rotation: str = "daily"
    retention_days: int = 30


@dataclass
class MonitoringConfig:
    """Monitoring and observability configuration"""

    prometheus_enabled: bool = False
    prometheus_port: int = 9090
    jaeger_enabled: bool = False
    jaeger_endpoint: Optional[str] = None
    health_check_interval_seconds: int = 30


@dataclass
class SecurityConfig:
    """Security configuration"""

    jwt_secret_key: Optional[str] = None
    api_key_salt: Optional[str] = None
    encryption_key: Optional[str] = None
    token_expiry_hours: int = 24
    max_failed_attempts: int = 5
    lockout_duration_minutes: int = 30


@dataclass
class LUKHASAPIOptimizationConfig:
    """Complete LUKHAS API Optimization configuration"""

    integration: IntegrationConfig
    optimization: OptimizationConfig
    middleware: MiddlewareConfig
    analytics: AnalyticsConfig
    redis: RedisConfig
    logging: LoggingConfig
    monitoring: MonitoringConfig
    security: SecurityConfig

    # Metadata
    environment: str = "development"
    version: str = "1.0.0"
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


class ConfigurationFactory:
    """Factory for creating environment-specific configurations"""

    def __init__(self, config_dir: Path = Path("config")):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self._base_config = self._load_base_config()

        # Setup logging
        logging.basicConfig(level=logging.INFO)

    def _load_base_config(self) -> dict[str, Any]:
        """Load base configuration shared across environments"""
        base_file = self.config_dir / "base.yaml"
        if base_file.exists():
            try:
                with open(base_file) as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                logger.warning(f"Failed to load base config: {e}")
        return {}

    def create_config(self,
                     environment: Union[str, DeploymentEnvironment],
                     overrides: Optional[dict[str, Any]] = None) -> LUKHASAPIOptimizationConfig:
        """Create configuration for specific environment"""
        if isinstance(environment, str):
            try:
                environment = DeploymentEnvironment(environment)
            except ValueError:
                logger.warning(f"Unknown environment: {environment}, using development")
                environment = DeploymentEnvironment.DEVELOPMENT

        logger.info(f"Creating configuration for environment: {environment.value}")

        # Start with base config
        config_dict = self._base_config.copy()

        # Apply environment-specific settings
        env_config = self._get_environment_config(environment)
        config_dict = self._deep_merge(config_dict, env_config)

        # Apply any overrides
        if overrides:
            config_dict = self._deep_merge(config_dict, overrides)

        # Apply environment variable overrides
        env_overrides = self._get_env_overrides()
        config_dict = self._deep_merge(config_dict, env_overrides)

        # Create structured configuration
        return self._create_structured_config(config_dict, environment.value)

    def _get_environment_config(self, environment: DeploymentEnvironment) -> dict[str, Any]:
        """Get configuration for specific environment"""
        configs = {
            DeploymentEnvironment.DEVELOPMENT: {
                "integration": {
                    "mode": "development",
                    "enable_intelligent_routing": False,
                    "enable_predictive_caching": False,
                    "enable_auto_scaling": False,
                },
                "optimization": {
                    "strategy": "balanced",
                    "cache_ttl_seconds": 300,
                    "max_cache_size_mb": 128,
                    "max_concurrent_requests": 100,
                },
                "middleware": {
                    "max_request_size_mb": 5,
                    "request_timeout_seconds": 15,
                    "enable_compression": False,
                },
                "analytics": {
                    "enable_alerts": False,
                    "enable_intelligence": False,
                    "retention_days": 3,
                    "batch_size": 50,
                },
                "redis": {
                    "pool_size": 5,
                    "timeout_seconds": 3,
                },
                "logging": {
                    "level": "DEBUG",
                    "format": "structured",
                    "output": "console",
                },
                "monitoring": {
                    "prometheus_enabled": False,
                    "jaeger_enabled": False,
                },
            },

            DeploymentEnvironment.TESTING: {
                "integration": {
                    "mode": "testing",
                    "enable_intelligent_routing": False,
                    "enable_predictive_caching": False,
                    "enable_auto_scaling": False,
                },
                "optimization": {
                    "strategy": "balanced",
                    "cache_ttl_seconds": 60,
                    "max_cache_size_mb": 64,
                    "max_concurrent_requests": 50,
                },
                "analytics": {
                    "enable_alerts": False,
                    "enable_intelligence": False,
                    "retention_days": 1,
                    "batch_size": 10,
                },
                "redis": {
                    "url": "redis://localhost:6379/1",  # Different DB for testing
                    "pool_size": 3,
                    "timeout_seconds": 2,
                },
                "logging": {
                    "level": "WARNING",
                    "format": "json",
                    "output": "console",
                },
            },

            DeploymentEnvironment.PRODUCTION: {
                "integration": {
                    "mode": "production",
                    "enable_intelligent_routing": True,
                    "enable_predictive_caching": True,
                    "enable_auto_scaling": True,
                },
                "optimization": {
                    "strategy": "high_throughput",
                    "cache_ttl_seconds": 3600,
                    "max_cache_size_mb": 1024,
                    "max_concurrent_requests": 2000,
                },
                "middleware": {
                    "max_request_size_mb": 50,
                    "request_timeout_seconds": 60,
                    "enable_compression": True,
                },
                "analytics": {
                    "enable_alerts": True,
                    "enable_intelligence": True,
                    "retention_days": 30,
                    "batch_size": 1000,
                    "export_interval_seconds": 30,
                },
                "redis": {
                    "pool_size": 50,
                    "timeout_seconds": 10,
                    "retry_attempts": 5,
                },
                "logging": {
                    "level": "INFO",
                    "format": "json",
                    "output": "file",
                    "file_path": "/var/log/lukhas/api-optimization.log",
                    "rotation": "daily",
                    "retention_days": 30,
                },
                "monitoring": {
                    "prometheus_enabled": True,
                    "prometheus_port": 9090,
                    "jaeger_enabled": True,
                    "jaeger_endpoint": "http://jaeger:14268/api/traces",
                    "health_check_interval_seconds": 15,
                },
            },

            DeploymentEnvironment.HIGH_PERFORMANCE: {
                "integration": {
                    "mode": "high_performance",
                    "enable_intelligent_routing": True,
                    "enable_predictive_caching": True,
                    "enable_auto_scaling": True,
                },
                "optimization": {
                    "strategy": "aggressive_cache",
                    "cache_ttl_seconds": 7200,
                    "max_cache_size_mb": 2048,
                    "max_concurrent_requests": 5000,
                },
                "middleware": {
                    "max_request_size_mb": 100,
                    "request_timeout_seconds": 120,
                    "enable_compression": True,
                },
                "analytics": {
                    "enable_intelligence": True,
                    "retention_days": 90,
                    "batch_size": 2000,
                    "export_interval_seconds": 10,
                },
                "redis": {
                    "pool_size": 100,
                    "timeout_seconds": 15,
                },
                "monitoring": {
                    "prometheus_enabled": True,
                    "jaeger_enabled": True,
                    "health_check_interval_seconds": 10,
                },
            },

            DeploymentEnvironment.RESOURCE_CONSERVATIVE: {
                "integration": {
                    "mode": "resource_conservative",
                    "enable_intelligent_routing": False,
                    "enable_predictive_caching": False,
                    "enable_auto_scaling": False,
                },
                "optimization": {
                    "strategy": "resource_conservation",
                    "cache_ttl_seconds": 1800,
                    "max_cache_size_mb": 64,
                    "max_concurrent_requests": 200,
                },
                "middleware": {
                    "max_request_size_mb": 10,
                    "request_timeout_seconds": 30,
                    "enable_compression": False,
                },
                "analytics": {
                    "enable_intelligence": False,
                    "retention_days": 7,
                    "batch_size": 100,
                    "export_interval_seconds": 300,
                },
                "redis": {
                    "pool_size": 10,
                    "timeout_seconds": 5,
                },
                "monitoring": {
                    "prometheus_enabled": False,
                    "jaeger_enabled": False,
                    "health_check_interval_seconds": 60,
                },
            },
        }

        return configs.get(environment, configs[DeploymentEnvironment.DEVELOPMENT])

    def _get_env_overrides(self) -> dict[str, Any]:
        """Get configuration overrides from environment variables"""
        overrides = {}

        # Redis configuration
        if redis_url := os.getenv("LUKHAS_REDIS_URL"):
            overrides.setdefault("redis", {})["url"] = redis_url
        if redis_password := os.getenv("LUKHAS_REDIS_PASSWORD"):
            overrides.setdefault("redis", {})["password"] = redis_password

        # Logging configuration
        if log_level := os.getenv("LUKHAS_LOG_LEVEL"):
            overrides.setdefault("logging", {})["level"] = log_level
        if log_file := os.getenv("LUKHAS_LOG_FILE"):
            overrides.setdefault("logging", {})["file_path"] = log_file

        # Performance tuning
        if cache_ttl := os.getenv("LUKHAS_CACHE_TTL_DEFAULT"):
            overrides.setdefault("optimization", {})["cache_ttl_seconds"] = int(cache_ttl)
        if max_requests := os.getenv("LUKHAS_MAX_CONCURRENT_REQUESTS"):
            overrides.setdefault("optimization", {})["max_concurrent_requests"] = int(max_requests)

        # Security configuration
        if jwt_secret := os.getenv("LUKHAS_JWT_SECRET_KEY"):
            overrides.setdefault("security", {})["jwt_secret_key"] = jwt_secret
        if api_salt := os.getenv("LUKHAS_API_KEY_SALT"):
            overrides.setdefault("security", {})["api_key_salt"] = api_salt
        if encryption_key := os.getenv("LUKHAS_ENCRYPTION_KEY"):
            overrides.setdefault("security", {})["encryption_key"] = encryption_key

        # Monitoring configuration
        if prometheus_port := os.getenv("LUKHAS_PROMETHEUS_PORT"):
            overrides.setdefault("monitoring", {})["prometheus_port"] = int(prometheus_port)
        if jaeger_endpoint := os.getenv("LUKHAS_JAEGER_ENDPOINT"):
            overrides.setdefault("monitoring", {})["jaeger_endpoint"] = jaeger_endpoint

        return overrides

    def _create_structured_config(self, config_dict: dict[str, Any], environment: str) -> LUKHASAPIOptimizationConfig:
        """Create structured configuration from dictionary"""

        # Helper function to create dataclass from dict
        def create_dataclass(cls, data: dict[str, Any]):
            # Filter data to only include fields that exist in the dataclass
            field_names = {f.name for f in cls.__dataclass_fields__.values()}
            filtered_data = {k: v for k, v in data.items() if k in field_names}
            return cls(**filtered_data)

        # Create component configurations
        integration = create_dataclass(IntegrationConfig, config_dict.get("integration", {}))
        optimization = create_dataclass(OptimizationConfig, config_dict.get("optimization", {}))
        middleware = create_dataclass(MiddlewareConfig, config_dict.get("middleware", {}))
        analytics = create_dataclass(AnalyticsConfig, config_dict.get("analytics", {}))
        redis = create_dataclass(RedisConfig, config_dict.get("redis", {}))
        logging_config = create_dataclass(LoggingConfig, config_dict.get("logging", {}))
        monitoring = create_dataclass(MonitoringConfig, config_dict.get("monitoring", {}))
        security = create_dataclass(SecurityConfig, config_dict.get("security", {}))

        # Create main configuration
        return LUKHASAPIOptimizationConfig(
            integration=integration,
            optimization=optimization,
            middleware=middleware,
            analytics=analytics,
            redis=redis,
            logging=logging_config,
            monitoring=monitoring,
            security=security,
            environment=environment,
        )

    def _deep_merge(self, base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
        """Deep merge two dictionaries"""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def save_config(self, config: LUKHASAPIOptimizationConfig, filename: Optional[str] = None) -> Path:
        """Save configuration to file"""
        if not filename:
            filename = f"{config.environment}.yaml"

        filepath = self.config_dir / filename
        config_dict = asdict(config)

        with open(filepath, "w") as f:
            yaml.dump(config_dict, f, default_flow_style=False, indent=2)

        logger.info(f"Configuration saved to {filepath}")
        return filepath

    def load_config(self, filename: str) -> LUKHASAPIOptimizationConfig:
        """Load configuration from file"""
        filepath = self.config_dir / filename

        with open(filepath) as f:
            config_dict = yaml.safe_load(f)

        environment = config_dict.get("environment", "development")
        return self._create_structured_config(config_dict, environment)

    def validate_config(self, config: LUKHASAPIOptimizationConfig) -> dict[str, Any]:
        """Validate configuration and return validation results"""
        issues = []
        warnings = []

        # Validate Redis configuration
        if not config.redis.url:
            issues.append("Redis URL is required")

        # Validate security configuration for production
        if config.environment == "production":
            if not config.security.jwt_secret_key:
                issues.append("JWT secret key is required for production")
            if not config.security.api_key_salt:
                warnings.append("API key salt should be configured for production")
            if not config.security.encryption_key:
                warnings.append("Encryption key should be configured for production")

        # Validate performance settings
        if config.optimization.max_concurrent_requests > 10000:
            warnings.append("Very high concurrent request limit may impact performance")

        if config.optimization.cache_ttl_seconds > 86400:  # 24 hours
            warnings.append("Very long cache TTL may lead to stale data")

        # Validate logging configuration
        if config.logging.output == "file" and not config.logging.file_path:
            issues.append("Log file path is required when output is set to 'file'")

        # Validate monitoring configuration
        if config.monitoring.jaeger_enabled and not config.monitoring.jaeger_endpoint:
            issues.append("Jaeger endpoint is required when Jaeger is enabled")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "summary": f"Configuration validation: {len(issues)} errors, {len(warnings)} warnings",
        }


# Convenience functions
def create_config(environment: str,
                 overrides: Optional[dict[str, Any]] = None,
                 config_dir: Optional[Path] = None) -> LUKHASAPIOptimizationConfig:
    """Create configuration for environment"""
    factory = ConfigurationFactory(config_dir or Path("config"))
    return factory.create_config(environment, overrides)


def load_config_from_file(filename: str, config_dir: Optional[Path] = None) -> LUKHASAPIOptimizationConfig:
    """Load configuration from file"""
    factory = ConfigurationFactory(config_dir or Path("config"))
    return factory.load_config(filename)


def validate_config(config: LUKHASAPIOptimizationConfig) -> dict[str, Any]:
    """Validate configuration"""
    factory = ConfigurationFactory()
    return factory.validate_config(config)


def auto_detect_environment() -> str:
    """Auto-detect deployment environment from environment variables"""
    # Check explicit environment variable
    env = os.getenv("LUKHAS_ENVIRONMENT", "").lower()
    if env in [e.value for e in DeploymentEnvironment]:
        return env

    # Check common deployment indicators
    if os.getenv("KUBERNETES_SERVICE_HOST"):
        return "production"
    elif os.getenv("DOCKER_CONTAINER"):
        return "staging"
    elif os.getenv("CI") or os.getenv("GITHUB_ACTIONS"):
        return "testing"
    elif os.getenv("DEBUG") == "true":
        return "development"

    # Default to development
    return "development"


if __name__ == "__main__":
    """CLI interface for configuration management"""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="LUKHAS API Optimization Configuration Manager")
    parser.add_argument("--environment", "-e", default="development",
                       help="Deployment environment")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--validate", "-v", action="store_true",
                       help="Validate configuration")
    parser.add_argument("--format", "-f", choices=["yaml", "json"], default="yaml",
                       help="Output format")
    parser.add_argument("--auto-detect", "-a", action="store_true",
                       help="Auto-detect environment")

    args = parser.parse_args()

    # Auto-detect environment if requested
    if args.auto_detect:
        args.environment = auto_detect_environment()
        print(f"Auto-detected environment: {args.environment}")

    # Create configuration
    factory = ConfigurationFactory()
    config = factory.create_config(args.environment)

    # Validate if requested
    if args.validate:
        validation = factory.validate_config(config)
        print("\nValidation Results:")
        print(f"Valid: {validation['valid']}")
        if validation["issues"]:
            print("Issues:")
            for issue in validation["issues"]:
                print(f"  ❌ {issue}")
        if validation["warnings"]:
            print("Warnings:")
            for warning in validation["warnings"]:
                print(f"  ⚠️  {warning}")

    # Output configuration
    if args.output:
        if args.format == "json":
            with open(args.output, "w") as f:
                json.dump(asdict(config), f, indent=2)
        else:
            factory.save_config(config, args.output)
        print(f"Configuration saved to {args.output}")
    elif args.format == "json":
        print(json.dumps(asdict(config), indent=2))
    else:
        print(yaml.dump(asdict(config), default_flow_style=False, indent=2))
