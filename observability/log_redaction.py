"""
Log redaction filter to prevent secret leakage.

Automatically redacts patterns that look like secrets from log messages:
- OpenAI-style tokens (sk-...)
- Bearer tokens
- Other sensitive patterns

Phase 3: Added as part of security hardening.
"""

import logging
import re
from re import Pattern

# Secret patterns to redact
_SECRET_PATTERNS: list[Pattern] = [
    re.compile(r"\bsk-[A-Za-z0-9]{10,}\b"),  # OpenAI-like tokens
    re.compile(r"\bBearer\s+[A-Za-z0-9._-]{8,}\b", re.I),  # Bearer tokens
    re.compile(r"\bAPIKEY[=:]\s*[A-Za-z0-9._-]{8,}\b", re.I),  # API key assignments
]


class RedactingFilter(logging.Filter):
    """
    Logging filter that redacts secrets from log messages.

    Usage:
        import logging
        from observability.log_redaction import RedactingFilter

        logger = logging.getLogger()
        logger.addFilter(RedactingFilter())
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Redact secrets from the log record message.

        Args:
            record: The log record to filter

        Returns:
            True (always allows the log record through, just modifies it)
        """
        msg = str(record.getMessage())
        redacted = msg

        # Apply all redaction patterns
        for pat in _SECRET_PATTERNS:
            redacted = pat.sub("[REDACTED]", redacted)

        # If we redacted anything, update the record
        if redacted != msg:
            record.msg = redacted
            record.args = ()  # Clear args to prevent re-formatting

        return True


def install_global_redaction() -> None:
    """
    Install redaction filter on the root logger.

    Call this once during application startup to ensure all logs
    are redacted for secrets.
    """
    root = logging.getLogger()
    root.addFilter(RedactingFilter())
