"""Audit logging configuration for SOC 2 compliance."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class AuditConfig:
    """Configuration for audit logging system.

    SOC 2 Requirements:
    - Event logging for security-relevant actions
    - Log retention for compliance (default 7 years)
    - Tamper-evident logging (append-only)
    - Structured logging for analysis

    Attributes:
        enabled: Enable/disable audit logging
        log_file_path: Path to audit log file (None for in-memory only)
        retention_days: Number of days to retain audit logs (default 2555 = 7 years)
        max_file_size_mb: Maximum log file size before rotation (default 100MB)
        max_backup_count: Number of backup files to keep (default 10)
        include_request_body: Log request bodies for data access events
        include_response_body: Log response bodies for data access events
        log_authentication: Enable authentication event logging
        log_data_access: Enable data access event logging
        log_admin_actions: Enable administrative action logging
        log_security_events: Enable security event logging
        async_logging: Use async logging for performance (default True)
    """

    enabled: bool = True
    log_file_path: Optional[Path] = None
    retention_days: int = 2555  # 7 years for SOC 2 compliance
    max_file_size_mb: int = 100
    max_backup_count: int = 10
    include_request_body: bool = False
    include_response_body: bool = False
    log_authentication: bool = True
    log_data_access: bool = True
    log_admin_actions: bool = True
    log_security_events: bool = True
    async_logging: bool = True

    # Alert thresholds
    failed_login_threshold: int = 5  # Alert after 5 failed logins
    rate_limit_threshold: int = 10  # Alert after 10 rate limit hits

    def __post_init__(self):
        """Validate configuration."""
        if self.retention_days < 1:
            raise ValueError("retention_days must be at least 1")

        if self.max_file_size_mb <= 0:
            raise ValueError("max_file_size_mb must be positive")

        if self.max_backup_count < 0:
            raise ValueError("max_backup_count must be non-negative")

        if self.log_file_path:
            self.log_file_path = Path(self.log_file_path)
            # Create parent directory if it doesn't exist
            self.log_file_path.parent.mkdir(parents=True, exist_ok=True)


def get_default_config() -> AuditConfig:
    """Get default audit configuration for production use.

    Returns:
        AuditConfig with production-safe defaults
    """
    return AuditConfig(
        enabled=True,
        log_file_path=Path("logs/audit/audit.jsonl"),
        retention_days=2555,  # 7 years
        max_file_size_mb=100,
        max_backup_count=10,
        include_request_body=False,  # Don't log request bodies by default
        include_response_body=False,  # Don't log response bodies by default
        log_authentication=True,
        log_data_access=True,
        log_admin_actions=True,
        log_security_events=True,
        async_logging=True,
    )


def get_development_config() -> AuditConfig:
    """Get audit configuration for development use.

    Returns:
        AuditConfig with development-friendly settings
    """
    return AuditConfig(
        enabled=True,
        log_file_path=Path("logs/audit/audit-dev.jsonl"),
        retention_days=30,  # 30 days for dev
        max_file_size_mb=10,
        max_backup_count=3,
        include_request_body=True,  # Include bodies for debugging
        include_response_body=True,
        log_authentication=True,
        log_data_access=True,
        log_admin_actions=True,
        log_security_events=True,
        async_logging=False,  # Sync for easier debugging
    )


def get_testing_config() -> AuditConfig:
    """Get audit configuration for testing.

    Returns:
        AuditConfig with testing-friendly settings (in-memory only)
    """
    return AuditConfig(
        enabled=True,
        log_file_path=None,  # In-memory only for tests
        retention_days=1,
        max_file_size_mb=1,
        max_backup_count=0,
        include_request_body=True,
        include_response_body=True,
        log_authentication=True,
        log_data_access=True,
        log_admin_actions=True,
        log_security_events=True,
        async_logging=False,  # Sync for deterministic tests
    )
