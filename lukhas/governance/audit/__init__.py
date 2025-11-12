"""Audit logging system for SOC 2 compliance and security event tracking.

This module provides comprehensive audit logging capabilities for LUKHAS AI,
including security events, data access tracking, and compliance reporting.

OWASP A09 Mitigation: Security Logging and Monitoring Failures
SOC 2 Compliance: Security event tracking and retention

Usage:
    from lukhas.governance.audit import AuditLogger, AuditEventType, AuditEvent

    logger = AuditLogger()
    logger.log_authentication_event(
        user_id="user_abc",
        event_type=AuditEventType.LOGIN_SUCCESS,
        ip_address="203.0.113.1"
    )
"""

from lukhas.governance.audit.config import AuditConfig
from lukhas.governance.audit.events import AuditEvent, AuditEventType
from lukhas.governance.audit.logger import AuditLogger
from lukhas.governance.audit.storage import AuditStorage, FileAuditStorage, InMemoryAuditStorage

__all__ = [
    "AuditConfig",
    "AuditEvent",
    "AuditEventType",
    "AuditLogger",
    "AuditStorage",
    "FileAuditStorage",
    "InMemoryAuditStorage",
]
