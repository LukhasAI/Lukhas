"""
Secure Logging Utilities for LUKHAS AI
=====================================
Provides security-aware logging that automatically redacts sensitive information
and follows security best practices for audit trails and compliance.
"""
import time
import streamlit as st

import hashlib
import logging
import re
from typing import Any, Optional


class SecurityLogFilter(logging.Filter):
    """
    Logging filter that redacts sensitive information from log messages.
    Implements security best practices for PII and credential protection.
    """

    # Patterns for sensitive data detection
    SENSITIVE_PATTERNS = [
        # API Keys and tokens
        (r'api[_-]?key["\s]*[:=]["\s]*([a-zA-Z0-9_-]+)', r"api_key=***REDACTED***"),
        (r'token["\s]*[:=]["\s]*([a-zA-Z0-9_.-]+)', r"token=***REDACTED***"),
        (r'secret["\s]*[:=]["\s]*([a-zA-Z0-9_.-]+)', r"secret=***REDACTED***"),
        (r'password["\s]*[:=]["\s]*([a-zA-Z0-9_.-]+)', r"password=***REDACTED***"),
        # Email addresses (partial redaction)
        (r"([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", lambda m: f"{m.group(1)[:3]}***@{m.group(2)}"),
        # Phone numbers (show only last 4 digits)
        (r"\+?[\d\s()-]{10,15}", lambda m: f"***-***-{m.group()}[-4:]}"),
        # JWT tokens
        (r"eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*", r"***JWT_TOKEN***"),
        # Credit card numbers
        (r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b", r"****-****-****-****"),
        # SSN patterns
        (r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b", r"***-**-****"),
        # IP addresses (partial redaction)
        (r"\b(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})\b", lambda m: f"{m.group(1)}.{m.group(2)}.***.***."),
    ]

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter and redact sensitive information from log records."""
        # Redact sensitive data from message
        if hasattr(record, "msg") and isinstance(record.msg, str):
            record.msg = self._redact_sensitive_data(record.msg)

        # Redact from args if present
        if hasattr(record, "args") and record.args:
            record.args = tuple(
                self._redact_sensitive_data(str(arg)) if isinstance(arg, str) else arg for arg in record.args
            )

        return True

    def _redact_sensitive_data(self, text: str) -> str:
        """Redact sensitive data from text using pattern matching."""
        redacted_text = text

        for pattern, replacement in self.SENSITIVE_PATTERNS:
            if callable(replacement):
                # Use lambda replacement function
                redacted_text = re.sub(pattern, replacement, redacted_text, flags=re.IGNORECASE)
            else:
                # Use string replacement
                redacted_text = re.sub(pattern, replacement, redacted_text, flags=re.IGNORECASE)

        return redacted_text


class SecurityAwareLogger:
    """
    Security-aware logger with built-in redaction and audit capabilities.
    Follows security best practices for sensitive data handling.
    """

    def __init__(self, name: str, audit_trail: bool = True):
        """Initialize security-aware logger."""
        self.logger = logging.getLogger(name)
        self.audit_trail = audit_trail

        # Add security filter if not already present
        security_filter = SecurityLogFilter()
        if not any(isinstance(f, SecurityLogFilter) for f in self.logger.filters):
            self.logger.addFilter(security_filter)

    def log_authentication_attempt(
        self,
        user_id: str,
        success: bool,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        method: str = "password",
    ) -> None:
        """Log authentication attempt with security context."""
        # Hash user_id for privacy
        user_hash = hashlib.sha256(user_id.encode()).hexdigest()[:8]

        # Redact IP (show only first 3 octets)
        safe_ip = self._redact_ip(ip_address) if ip_address else "unknown"

        status = "SUCCESS" if success else "FAILURE"

        self.logger.info(
            f"Authentication {status}: user_hash={user_hash}, "
            f"method={method}, ip={safe_ip}, "
            f"user_agent={user_agent[:50] if user_agent else 'unknown'}"
        )

        # Log security event for failures
        if not success:
            self.log_security_event(
                "AUTH_FAILURE",
                f"Failed authentication attempt for user hash {user_hash}",
                {"user_hash": user_hash, "ip": safe_ip, "method": method},
            )

    def log_mfa_event(self, user_id: str, method: str, success: bool) -> None:
        """Log MFA events without exposing codes."""
        user_hash = hashlib.sha256(user_id.encode()).hexdigest()[:8]
        status = "SUCCESS" if success else "FAILURE"

        self.logger.info(f"MFA {status}: user_hash={user_hash}, method={method}")

    def log_api_key_usage(self, key_id: str, endpoint: str, success: bool) -> None:
        """Log API key usage events."""
        # Show only first 8 chars of key ID
        safe_key_id = key_id[:8] + "..." if len(key_id) > 8 else key_id
        status = "SUCCESS" if success else "FAILURE"

        self.logger.info(f"API Key {status}: key_id={safe_key_id}, endpoint={endpoint}")

    def log_security_event(self, event_type: str, message: str, context: Optional[dict[str, Any]] = None) -> None:
        """Log security events with structured context."""
        self.logger.warning(
            f"SECURITY_EVENT: {event_type} - {message}",
            extra={"security_event": True, "event_type": event_type, "context": context or {},
        )

    def log_data_access(self, user_id: str, resource: str, operation: str) -> None:
        """Log data access for compliance and audit."""
        user_hash = hashlib.sha256(user_id.encode()).hexdigest()[:8]

        self.logger.info(
            f"DATA_ACCESS: user_hash={user_hash}, resource={resource}, operation={operation}",
            extra={"audit_trail": True},
        )

    def log_consent_event(self, user_id: str, consent_type: str, granted: bool) -> None:
        """Log consent events for GDPR compliance."""
        user_hash = hashlib.sha256(user_id.encode()).hexdigest()[:8]
        status = "GRANTED" if granted else "DENIED"

        self.logger.info(f"CONSENT_{status}: user_hash={user_hash}, type={consent_type}", extra={"compliance": True})

    def _redact_ip(self, ip_address: str) -> str:
        """Redact IP address to show only network portion."""
        parts = ip_address.split(".")
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.***.***.***"
        return "***IP***"

    def debug(self, message: str, *args, **kwargs) -> None:
        """Debug logging with security filtering."""
        self.logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs) -> None:
        """Info logging with security filtering."""
        self.logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs) -> None:
        """Warning logging with security filtering."""
        self.logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs) -> None:
        """Error logging with security filtering."""
        self.logger.error(message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs) -> None:
        """Critical logging with security filtering."""
        self.logger.critical(message, *args, **kwargs)


def get_security_logger(name: str, audit_trail: bool = True) -> SecurityAwareLogger:
    """Get or create a security-aware logger instance."""
    return SecurityAwareLogger(name, audit_trail)


# Configure root logger with security filter
def configure_secure_logging():
    """Configure the root logging system with security filters."""
    # Add security filter to root logger
    root_logger = logging.getLogger()
    security_filter = SecurityLogFilter()

    if not any(isinstance(f, SecurityLogFilter) for f in root_logger.filters):
        root_logger.addFilter(security_filter)

    # Configure formatter for security logging
    security_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Apply to all handlers
    for handler in root_logger.handlers:
        handler.setFormatter(security_formatter)


# Example usage and testing
if __name__ == "__main__":
    # Configure secure logging
    configure_secure_logging()

    # Create security logger
    sec_logger = get_security_logger("lukhas.security.test")

    # Test various logging scenarios
    print("Testing secure logging...")

    # Test authentication logging
    sec_logger.log_authentication_attempt(
        "user123@example.com", success=True, ip_address="192.168.1.100", method="password"
    )

    # Test MFA logging (should not expose codes)
    sec_logger.log_mfa_event("user123@example.com", "totp", True)

    # Test sensitive data redaction
    sec_logger.info("API key is: api_key=sk-1234567890abcdef")
    sec_logger.info("User password: password=secret123")
    sec_logger.info(
        "JWT token: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
    )

    # Test security event logging
    sec_logger.log_security_event(
        "SUSPICIOUS_ACTIVITY", "Multiple failed login attempts", {"attempts": 5, "timeframe": "5 minutes"}
    )

    print("✅ Secure logging test completed")
