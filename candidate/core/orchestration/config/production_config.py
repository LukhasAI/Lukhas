"""
Production Configuration for LUKHAS Orchestrators
Provides production-ready configuration management with environment-specific settings
"""

import json
import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Union

logger = logging.getLogger(__name__)


class Environment(Enum):
    """Deployment environments"""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(Enum):
    """Logging levels"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class DatabaseConfig:
    """Database configuration settings"""

    host: str = "localhost"
    port: int = 5432
    database: str = "lukhas"
    username: str = "lukhas_user"
    password: str = ""
    ssl_mode: str = "prefer"
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600


@dataclass
class RedisConfig:
    """Redis configuration for caching and messaging"""

    host: str = "localhost"
    port: int = 6379
    database: int = 0
    password: Optional[str] = None
    ssl: bool = False
    max_connections: int = 100
    socket_timeout: float = 5.0
    socket_connect_timeout: float = 5.0


@dataclass
class MonitoringConfig:
    """Monitoring and observability configuration"""

    enable_metrics: bool = True
    enable_tracing: bool = True
    enable_logging: bool = True

    # Prometheus metrics
    metrics_port: int = 8090
    metrics_path: str = "/metrics"

    # Jaeger tracing
    jaeger_agent_host: str = "localhost"
    jaeger_agent_port: int = 6831

    # Log configuration
    log_level: LogLevel = LogLevel.INFO
    log_format: str = "json"
    log_file: Optional[str] = None

    # Health checks
    health_check_enabled: bool = True
    health_check_port: int = 8091
    health_check_path: str = "/health"


@dataclass
class SecurityConfig:
    """Security and authentication configuration"""

    enable_auth: bool = True
    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 24

    # Rate limiting
    enable_rate_limiting: bool = True
    rate_limit_per_minute: int = 100
    rate_limit_burst: int = 200

    # CORS
    enable_cors: bool = True
    cors_origins: list[str] = field(default_factory=lambda: ["*"])

    # Encryption
    encryption_key: str = ""
    hash_algorithm: str = "bcrypt"


@dataclass
class PerformanceConfig:
    """Performance and scaling configuration"""

    # Worker configuration
    worker_processes: int = 4
    worker_threads: int = 8
    worker_timeout: int = 30

    # Queue configuration
    max_queue_size: int = 1000
    queue_timeout: int = 60

    # Caching
    enable_caching: bool = True
    cache_ttl_seconds: int = 3600
    cache_max_size: int = 10000

    # Circuit breaker
    circuit_breaker_failure_threshold: int = 5
    circuit_breaker_recovery_timeout: int = 60
    circuit_breaker_expected_exception: str = "Exception"


@dataclass
class OrchestrationConfig:
    """Orchestrator-specific configuration"""

    # Global orchestrator settings
    enable_orchestration: bool = True
    orchestrator_timeout: int = 300
    max_concurrent_orchestrators: int = 50

    # Specific orchestrator configurations
    brain_orchestrator_enabled: bool = True
    memory_orchestrator_enabled: bool = True
    ethics_orchestrator_enabled: bool = True
    process_orchestrator_enabled: bool = True

    # Orchestrator resource limits
    max_memory_mb: int = 2048
    max_cpu_percent: int = 80
    max_execution_time: int = 600

    # Migration settings
    migration_mode: str = "gradual"
    rollback_enabled: bool = True
    health_check_interval: int = 30


@dataclass
class ProductionOrchestratorConfig:
    """Complete production configuration for LUKHAS orchestrators"""

    # Environment settings
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = False

    # Core configuration sections
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    orchestration: OrchestrationConfig = field(default_factory=OrchestrationConfig)

    # Application settings
    app_name: str = "LUKHAS-Orchestrator"
    app_version: str = "1.0.0"
    api_prefix: str = "/api/v1"

    # File paths
    data_dir: str = "./data"
    logs_dir: str = "./logs"
    temp_dir: str = "./tmp"
    config_dir: str = "./config"

    @classmethod
    def load_from_env(cls) -> "ProductionOrchestratorConfig":
        """Load configuration from environment variables"""
        config = cls()

        # Environment
        env_name = os.getenv("LUKHAS_ENVIRONMENT", "development").lower()
        try:
            config.environment = Environment(env_name)
        except ValueError:
            logger.warning(f"Unknown environment '{env_name}', using development")
            config.environment = Environment.DEVELOPMENT

        config.debug = os.getenv("LUKHAS_DEBUG", "false").lower() in (
            "true",
            "1",
            "yes",
        )

        # Database configuration
        if os.getenv("DATABASE_URL"):
            # Parse DATABASE_URL if provided
            db_url = os.getenv("DATABASE_URL")
            # Simple parsing - in production, use urllib.parse
            if db_url.startswith("postgresql://"):
                config.database.host = os.getenv("DB_HOST", config.database.host)
                config.database.port = int(
                    os.getenv("DB_PORT", str(config.database.port))
                )
                config.database.database = os.getenv(
                    "DB_NAME", config.database.database
                )
                config.database.username = os.getenv(
                    "DB_USER", config.database.username
                )
                config.database.password = os.getenv(
                    "DB_PASSWORD", config.database.password
                )

        # Redis configuration
        config.redis.host = os.getenv("REDIS_HOST", config.redis.host)
        config.redis.port = int(os.getenv("REDIS_PORT", str(config.redis.port)))
        config.redis.password = os.getenv("REDIS_PASSWORD", config.redis.password)

        # Security configuration
        config.security.jwt_secret_key = os.getenv(
            "JWT_SECRET_KEY", config.security.jwt_secret_key
        )
        config.security.encryption_key = os.getenv(
            "ENCRYPTION_KEY", config.security.encryption_key
        )

        # Performance configuration
        config.performance.worker_processes = int(
            os.getenv("WORKER_PROCESSES", str(config.performance.worker_processes))
        )
        config.performance.worker_threads = int(
            os.getenv("WORKER_THREADS", str(config.performance.worker_threads))
        )

        # Monitoring configuration
        config.monitoring.enable_metrics = os.getenv(
            "ENABLE_METRICS", "true"
        ).lower() in (
            "true",
            "1",
            "yes",
        )
        config.monitoring.metrics_port = int(
            os.getenv("METRICS_PORT", str(config.monitoring.metrics_port))
        )

        log_level_name = os.getenv("LOG_LEVEL", "INFO").upper()
        try:
            config.monitoring.log_level = LogLevel(log_level_name)
        except ValueError:
            logger.warning(f"Unknown log level '{log_level_name}', using INFO")
            config.monitoring.log_level = LogLevel.INFO

        # Orchestration configuration
        config.orchestration.enable_orchestration = os.getenv(
            "ENABLE_ORCHESTRATION", "true"
        ).lower() in (
            "true",
            "1",
            "yes",
        )
        config.orchestration.max_concurrent_orchestrators = int(
            os.getenv(
                "MAX_CONCURRENT_ORCHESTRATORS",
                str(config.orchestration.max_concurrent_orchestrators),
            )
        )

        # File paths
        config.data_dir = os.getenv("DATA_DIR", config.data_dir)
        config.logs_dir = os.getenv("LOGS_DIR", config.logs_dir)
        config.temp_dir = os.getenv("TEMP_DIR", config.temp_dir)
        config.config_dir = os.getenv("CONFIG_DIR", config.config_dir)

        return config

    @classmethod
    def load_from_file(
        cls, config_path: Union[str, Path]
    ) -> "ProductionOrchestratorConfig":
        """Load configuration from JSON file"""
        config_path = Path(config_path)

        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        try:
            with open(config_path) as f:
                config_data = json.load(f)

            return cls.from_dict(config_data)

        except Exception as e:
            logger.error(f"Failed to load configuration from {config_path}: {e}")
            raise

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProductionOrchestratorConfig":
        """Create configuration from dictionary"""
        config = cls()

        # Handle nested configurations
        if "database" in data:
            config.database = DatabaseConfig(**data["database"])

        if "redis" in data:
            config.redis = RedisConfig(**data["redis"])

        if "monitoring" in data:
            monitoring_data = data["monitoring"].copy()
            if "log_level" in monitoring_data:
                monitoring_data["log_level"] = LogLevel(monitoring_data["log_level"])
            config.monitoring = MonitoringConfig(**monitoring_data)

        if "security" in data:
            config.security = SecurityConfig(**data["security"])

        if "performance" in data:
            config.performance = PerformanceConfig(**data["performance"])

        if "orchestration" in data:
            config.orchestration = OrchestrationConfig(**data["orchestration"])

        # Handle top-level fields
        if "environment" in data:
            config.environment = Environment(data["environment"])

        for field_name in [
            "debug",
            "app_name",
            "app_version",
            "api_prefix",
            "data_dir",
            "logs_dir",
            "temp_dir",
            "config_dir",
        ]:
            if field_name in data:
                setattr(config, field_name, data[field_name])

        return config

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary"""
        result = {
            "environment": self.environment.value,
            "debug": self.debug,
            "app_name": self.app_name,
            "app_version": self.app_version,
            "api_prefix": self.api_prefix,
            "data_dir": self.data_dir,
            "logs_dir": self.logs_dir,
            "temp_dir": self.temp_dir,
            "config_dir": self.config_dir,
            "database": {
                "host": self.database.host,
                "port": self.database.port,
                "database": self.database.database,
                "username": self.database.username,
                "password": self.database.password,
                "ssl_mode": self.database.ssl_mode,
                "pool_size": self.database.pool_size,
                "max_overflow": self.database.max_overflow,
                "pool_timeout": self.database.pool_timeout,
                "pool_recycle": self.database.pool_recycle,
            },
            "redis": {
                "host": self.redis.host,
                "port": self.redis.port,
                "database": self.redis.database,
                "password": self.redis.password,
                "ssl": self.redis.ssl,
                "max_connections": self.redis.max_connections,
                "socket_timeout": self.redis.socket_timeout,
                "socket_connect_timeout": self.redis.socket_connect_timeout,
            },
            "monitoring": {
                "enable_metrics": self.monitoring.enable_metrics,
                "enable_tracing": self.monitoring.enable_tracing,
                "enable_logging": self.monitoring.enable_logging,
                "metrics_port": self.monitoring.metrics_port,
                "metrics_path": self.monitoring.metrics_path,
                "jaeger_agent_host": self.monitoring.jaeger_agent_host,
                "jaeger_agent_port": self.monitoring.jaeger_agent_port,
                "log_level": self.monitoring.log_level.value,
                "log_format": self.monitoring.log_format,
                "log_file": self.monitoring.log_file,
                "health_check_enabled": self.monitoring.health_check_enabled,
                "health_check_port": self.monitoring.health_check_port,
                "health_check_path": self.monitoring.health_check_path,
            },
            "security": {
                "enable_auth": self.security.enable_auth,
                "jwt_secret_key": self.security.jwt_secret_key,
                "jwt_algorithm": self.security.jwt_algorithm,
                "jwt_expiry_hours": self.security.jwt_expiry_hours,
                "enable_rate_limiting": self.security.enable_rate_limiting,
                "rate_limit_per_minute": self.security.rate_limit_per_minute,
                "rate_limit_burst": self.security.rate_limit_burst,
                "enable_cors": self.security.enable_cors,
                "cors_origins": self.security.cors_origins,
                "encryption_key": self.security.encryption_key,
                "hash_algorithm": self.security.hash_algorithm,
            },
            "performance": {
                "worker_processes": self.performance.worker_processes,
                "worker_threads": self.performance.worker_threads,
                "worker_timeout": self.performance.worker_timeout,
                "max_queue_size": self.performance.max_queue_size,
                "queue_timeout": self.performance.queue_timeout,
                "enable_caching": self.performance.enable_caching,
                "cache_ttl_seconds": self.performance.cache_ttl_seconds,
                "cache_max_size": self.performance.cache_max_size,
                "circuit_breaker_failure_threshold": self.performance.circuit_breaker_failure_threshold,
                "circuit_breaker_recovery_timeout": self.performance.circuit_breaker_recovery_timeout,
                "circuit_breaker_expected_exception": self.performance.circuit_breaker_expected_exception,
            },
            "orchestration": {
                "enable_orchestration": self.orchestration.enable_orchestration,
                "orchestrator_timeout": self.orchestration.orchestrator_timeout,
                "max_concurrent_orchestrators": self.orchestration.max_concurrent_orchestrators,
                "brain_orchestrator_enabled": self.orchestration.brain_orchestrator_enabled,
                "memory_orchestrator_enabled": self.orchestration.memory_orchestrator_enabled,
                "ethics_orchestrator_enabled": self.orchestration.ethics_orchestrator_enabled,
                "process_orchestrator_enabled": self.orchestration.process_orchestrator_enabled,
                "max_memory_mb": self.orchestration.max_memory_mb,
                "max_cpu_percent": self.orchestration.max_cpu_percent,
                "max_execution_time": self.orchestration.max_execution_time,
                "migration_mode": self.orchestration.migration_mode,
                "rollback_enabled": self.orchestration.rollback_enabled,
                "health_check_interval": self.orchestration.health_check_interval,
            },
        }
        return result

    def save_to_file(self, config_path: Union[str, Path]) -> None:
        """Save configuration to JSON file"""
        config_path = Path(config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(config_path, "w") as f:
                json.dump(self.to_dict(), f, indent=2)

            logger.info(f"Configuration saved to {config_path}")

        except Exception as e:
            logger.error(f"Failed to save configuration to {config_path}: {e}")
            raise

    def validate(self) -> list[str]:
        """Validate configuration and return list of issues"""
        issues = []

        # Validate database configuration
        if not self.database.host:
            issues.append("Database host is required")
        if not self.database.database:
            issues.append("Database name is required")
        if not self.database.username:
            issues.append("Database username is required")

        # Validate security configuration
        if self.security.enable_auth and not self.security.jwt_secret_key:
            issues.append("JWT secret key is required when authentication is enabled")

        # Validate file paths
        for path_name, path_value in [
            ("data_dir", self.data_dir),
            ("logs_dir", self.logs_dir),
            ("temp_dir", self.temp_dir),
            ("config_dir", self.config_dir),
        ]:
            try:
                Path(path_value).mkdir(parents=True, exist_ok=True)
            except Exception as e:
                issues.append(
                    f"Cannot create {path_name} directory '{path_value}': {e}"
                )

        # Validate port numbers
        ports = [
            ("Database port", self.database.port),
            ("Redis port", self.redis.port),
            ("Metrics port", self.monitoring.metrics_port),
            ("Health check port", self.monitoring.health_check_port),
        ]

        for port_name, port_value in ports:
            if not (1 <= port_value <= 65535):
                issues.append(
                    f"{port_name} must be between 1 and 65535, got {port_value}"
                )

        return issues

    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment == Environment.PRODUCTION

    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment == Environment.DEVELOPMENT
