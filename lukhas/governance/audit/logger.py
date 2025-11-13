"""Audit event logger with structured JSON logging."""

# T4: code=UP035 | ticket=ruff-cleanup | owner=lukhas-cleanup-team | status=resolved
# reason: Modernizing deprecated typing imports to native Python 3.9+ types for audit logger
# estimate: 10min | priority: high | dependencies: none

import time
from typing import Any, Optional

from lukhas.governance.audit.config import AuditConfig
from lukhas.governance.audit.events import AuditEvent, AuditEventType
from lukhas.governance.audit.storage import AuditStorage, FileAuditStorage, InMemoryAuditStorage


class AuditLogger:
    """Audit logger for security events and compliance tracking.

    Provides structured logging of security-relevant events with:
    - JSON structured logging for analysis
    - Configurable storage backends (file, in-memory)
    - Automatic log rotation and retention
    - SOC 2 compliance support

    Usage:
        logger = AuditLogger(config=AuditConfig())

        # Log authentication event
        logger.log_authentication_event(
            user_id="user_abc",
            event_type=AuditEventType.LOGIN_SUCCESS,
            ip_address="203.0.113.1",
            user_agent="Mozilla/5.0 ..."
        )

        # Log data access event
        logger.log_data_access_event(
            user_id="user_abc",
            event_type=AuditEventType.DATA_READ,
            resource_type="feedback_card",
            resource_id="card_123",
            ip_address="203.0.113.1"
        )

        # Query audit logs
        events = logger.get_events(
            user_id="user_abc",
            start_time=time.time() - 86400,  # Last 24 hours
            event_types=[AuditEventType.DATA_READ, AuditEventType.DATA_UPDATE]
        )
    """

    def __init__(self, config: Optional[AuditConfig] = None, storage: Optional[AuditStorage] = None):
        """Initialize audit logger.

        Args:
            config: Audit configuration (uses defaults if None)
            storage: Storage backend (creates default if None)
        """
        self.config = config or AuditConfig()

        if storage:
            self.storage = storage
        elif self.config.log_file_path:
            self.storage = FileAuditStorage(self.config)
        else:
            self.storage = InMemoryAuditStorage(self.config)

    def log_event(self, event: AuditEvent) -> None:
        """Log an audit event.

        Args:
            event: Audit event to log
        """
        if not self.config.enabled:
            return

        self.storage.store_event(event)

    def log_authentication_event(
        self,
        user_id: str,
        event_type: AuditEventType,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """Log an authentication event.

        Args:
            user_id: User ID
            event_type: Type of authentication event
            ip_address: Client IP address
            user_agent: Client user agent
            success: Whether authentication succeeded
            error_message: Error message if failed
            metadata: Additional context
        """
        if not self.config.log_authentication:
            return

        event = AuditEvent(
            event_type=event_type,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            action=f"Authentication: {event_type.value}",
            success=success,
            error_message=error_message,
            metadata=metadata or {},
        )

        self.log_event(event)

    def log_data_access_event(
        self,
        user_id: str,
        event_type: AuditEventType,
        resource_type: str,
        resource_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """Log a data access event.

        Args:
            user_id: User ID accessing data
            event_type: Type of data access event
            resource_type: Type of resource (e.g., "feedback_card")
            resource_id: ID of resource
            ip_address: Client IP address
            user_agent: Client user agent
            success: Whether access succeeded
            error_message: Error message if failed
            metadata: Additional context
        """
        if not self.config.log_data_access:
            return

        event = AuditEvent(
            event_type=event_type,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            resource_type=resource_type,
            resource_id=resource_id,
            action=f"Data access: {event_type.value} on {resource_type}:{resource_id}",
            success=success,
            error_message=error_message,
            metadata=metadata or {},
        )

        self.log_event(event)

    def log_security_event(
        self,
        event_type: AuditEventType,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """Log a security event.

        Args:
            event_type: Type of security event
            user_id: User ID (if applicable)
            ip_address: Client IP address
            user_agent: Client user agent
            resource_type: Type of resource (if applicable)
            resource_id: ID of resource (if applicable)
            success: Whether the security check passed
            error_message: Error message if failed
            metadata: Additional context
        """
        if not self.config.log_security_events:
            return

        event = AuditEvent(
            event_type=event_type,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            resource_type=resource_type,
            resource_id=resource_id,
            action=f"Security event: {event_type.value}",
            success=success,
            error_message=error_message,
            metadata=metadata or {},
        )

        self.log_event(event)

    def log_admin_action(
        self,
        user_id: str,
        event_type: AuditEventType,
        action: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """Log an administrative action.

        Args:
            user_id: Admin user ID
            event_type: Type of admin event
            action: Human-readable action description
            ip_address: Client IP address
            user_agent: Client user agent
            resource_type: Type of resource (if applicable)
            resource_id: ID of resource (if applicable)
            success: Whether action succeeded
            error_message: Error message if failed
            metadata: Additional context
        """
        if not self.config.log_admin_actions:
            return

        event = AuditEvent(
            event_type=event_type,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            success=success,
            error_message=error_message,
            metadata=metadata or {},
        )

        self.log_event(event)

    def get_events(
        self,
        user_id: Optional[str] = None,
        event_types: Optional[list[AuditEventType]] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        success: Optional[bool] = None,
        limit: int = 1000,
    ) -> list[AuditEvent]:
        """Query audit events with filters.

        Args:
            user_id: Filter by user ID
            event_types: Filter by event types
            start_time: Filter by start timestamp
            end_time: Filter by end timestamp
            resource_type: Filter by resource type
            resource_id: Filter by resource ID
            success: Filter by success status
            limit: Maximum number of events to return

        Returns:
            List of matching audit events
        """
        return self.storage.get_events(
            user_id=user_id,
            event_types=event_types,
            start_time=start_time,
            end_time=end_time,
            resource_type=resource_type,
            resource_id=resource_id,
            success=success,
            limit=limit,
        )

    def cleanup_old_logs(self, retention_days: Optional[int] = None) -> int:
        """Remove audit logs older than retention period.

        Args:
            retention_days: Number of days to retain (uses config default if None)

        Returns:
            Number of events removed
        """
        retention_days = retention_days or self.config.retention_days
        cutoff_time = time.time() - (retention_days * 86400)

        return self.storage.cleanup_old_events(cutoff_time)

    def get_statistics(
        self,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
    ) -> dict[str, Any]:
        """Get audit log statistics for monitoring.

        Args:
            start_time: Start timestamp for statistics
            end_time: End timestamp for statistics

        Returns:
            Dictionary with audit statistics
        """
        return self.storage.get_statistics(start_time, end_time)
