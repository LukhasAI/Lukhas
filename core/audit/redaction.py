"""PII redaction for audit logs."""
import re
from typing import Dict, Any


# Redaction patterns
EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
PHONE_PATTERN = re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b')
SSN_PATTERN = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
CREDIT_CARD_PATTERN = re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b')


def redact_email(text: str) -> str:
    """Redact email addresses."""
    return EMAIL_PATTERN.sub('[EMAIL_REDACTED]', text)


def redact_phone(text: str) -> str:
    """Redact phone numbers."""
    return PHONE_PATTERN.sub('[PHONE_REDACTED]', text)


def redact_ssn(text: str) -> str:
    """Redact SSNs."""
    return SSN_PATTERN.sub('[SSN_REDACTED]', text)


def redact_credit_card(text: str) -> str:
    """Redact credit card numbers."""
    return CREDIT_CARD_PATTERN.sub('[CC_REDACTED]', text)


def redact_pii(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply PII redaction to audit event before write.

    Args:
        event: Event dictionary to redact

    Returns:
        Redacted event dictionary
    """
    import json

    # Convert to JSON string for easier processing
    event_str = json.dumps(event)

    # Apply redactions
    event_str = redact_email(event_str)
    event_str = redact_phone(event_str)
    event_str = redact_ssn(event_str)
    event_str = redact_credit_card(event_str)

    # Parse back to dict
    return json.loads(event_str)


if __name__ == "__main__":
    print("=== PII Redaction Demo ===\n")

    event = {
        "user": "john@example.com",
        "message": "Call me at 555-123-4567",
        "ssn": "123-45-6789",
        "card": "4111-1111-1111-1111"
    }

    print("Original:", event)
    redacted = redact_pii(event)
    print("Redacted:", redacted)
