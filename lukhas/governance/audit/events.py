"""Audit event definitions and types."""

import json
import time
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, Optional
from uuid import uuid4


class AuditEventType(str, Enum):
    """Audit event types for categorization and filtering.

    Authentication Events:
        LOGIN_SUCCESS: Successful user login
        LOGIN_FAILURE: Failed login attempt
        LOGOUT: User logout
        TOKEN_REFRESH: JWT token refresh
        TOKEN_REVOKED: JWT token revocation
        PASSWORD_CHANGE: Password change event
        MFA_ENABLED: Multi-factor authentication enabled
        MFA_DISABLED: Multi-factor authentication disabled

    Data Access Events:
        DATA_READ: Data read operation
        DATA_CREATE: Data creation operation
        DATA_UPDATE: Data update operation
        DATA_DELETE: Data deletion operation
        BULK_EXPORT: Bulk data export (GDPR)
        BULK_DELETE: Bulk data deletion (GDPR)

    Security Events:
        RATE_LIMIT_EXCEEDED: Rate limit threshold exceeded
        IP_BLOCKED: IP address blocked
        UNAUTHORIZED_ACCESS: Unauthorized access attempt
        PERMISSION_DENIED: Permission denied
        SUSPICIOUS_ACTIVITY: Suspicious activity detected
        SECURITY_SCAN: Security scan performed

    Administrative Events:
        CONFIG_CHANGE: Configuration change
        USER_CREATED: User account created
        USER_DELETED: User account deleted
        USER_ROLE_CHANGED: User role/permissions changed
        FEATURE_TOGGLE: Feature flag toggled
        SYSTEM_STARTUP: System startup
        SYSTEM_SHUTDOWN: System shutdown
    """

    # Authentication events
    LOGIN_SUCCESS = "auth.login.success"
    LOGIN_FAILURE = "auth.login.failure"
    LOGOUT = "auth.logout"
    TOKEN_REFRESH = "auth.token.refresh"
    TOKEN_REVOKED = "auth.token.revoked"
    PASSWORD_CHANGE = "auth.password.change"
    MFA_ENABLED = "auth.mfa.enabled"
    MFA_DISABLED = "auth.mfa.disabled"

    # Data access events
    DATA_READ = "data.read"
    DATA_CREATE = "data.create"
    DATA_UPDATE = "data.update"
    DATA_DELETE = "data.delete"
    BULK_EXPORT = "data.bulk_export"
    BULK_DELETE = "data.bulk_delete"

    # Security events
    RATE_LIMIT_EXCEEDED = "security.rate_limit_exceeded"
    IP_BLOCKED = "security.ip_blocked"
    UNAUTHORIZED_ACCESS = "security.unauthorized_access"
    PERMISSION_DENIED = "security.permission_denied"
    SUSPICIOUS_ACTIVITY = "security.suspicious_activity"
    SECURITY_SCAN = "security.scan"

    # Administrative events
    CONFIG_CHANGE = "admin.config.change"
    USER_CREATED = "admin.user.created"
    USER_DELETED = "admin.user.deleted"
    USER_ROLE_CHANGED = "admin.user.role_changed"
    FEATURE_TOGGLE = "admin.feature.toggle"
    SYSTEM_STARTUP = "admin.system.startup"
    SYSTEM_SHUTDOWN = "admin.system.shutdown"


@dataclass
class AuditEvent:
    """Structured audit event for SOC 2 compliance.

    SOC 2 Requirements Met:
    - Unique event identifier (event_id)
    - Timestamp with millisecond precision
    - Event classification (event_type)
    - Actor identification (user_id)
    - Source tracking (ip_address, user_agent)
    - Resource identification (resource_type, resource_id)
    - Outcome tracking (success)
    - Detailed context (metadata)

    Attributes:
        event_id: Unique event identifier (UUID)
        timestamp: Event timestamp (Unix epoch with milliseconds)
        event_type: Type of event (from AuditEventType enum)
        user_id: User ID performing the action (None for system events)
        ip_address: Client IP address (None for system events)
        user_agent: Client user agent string
        resource_type: Type of resource accessed (e.g., "feedback_card", "trace")
        resource_id: ID of resource accessed (e.g., card ID, trace ID)
        action: Human-readable action description
        success: Whether the action succeeded
        error_message: Error message if action failed
        metadata: Additional context (request body, response, etc.)
    """

    event_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: float = field(default_factory=time.time)
    event_type: AuditEventType = AuditEventType.DATA_READ
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    action: str = ""
    success: bool = True
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert audit event to dictionary for JSON serialization.

        Returns:
            Dictionary representation of audit event
        """
        data = asdict(self)
        # Convert enum to string
        data["event_type"] = self.event_type.value
        return data

    def to_json(self) -> str:
        """Convert audit event to JSON string.

        Returns:
            JSON string representation of audit event
        """
        return json.dumps(self.to_dict(), default=str)
