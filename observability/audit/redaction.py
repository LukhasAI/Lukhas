"""
PII redaction and consent-aware data masking utilities.
"""
import re

# PII detection patterns
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE = re.compile(r"\b(?:\+\d{1,3}[ -]?)?(?:\(?\d{2,4}\)?[ -]?)?\d{3,4}[ -]?\d{4}\b")
IBAN = re.compile(r"\b[A-Z]{2}[0-9]{2}[A-Z0-9]{1,30}\b")
SSN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
CREDIT_CARD = re.compile(r"\b\d{4}[ -]?\d{4}[ -]?\d{4}[ -]?\d{4}\b")

MASK = "█" * 6


def mask_pii(text: str) -> str:
    """
    Mask common PII patterns in text.

    Args:
        text: Input text that may contain PII

    Returns:
        Text with PII patterns replaced with █████

    Example:
        >>> mask_pii("Contact me at john@example.com or 555-1234")
        'Contact me at ██████ or ██████'
    """
    text = EMAIL.sub(MASK, text)
    text = PHONE.sub(MASK, text)
    text = IBAN.sub(MASK, text)
    text = SSN.sub(MASK, text)
    text = CREDIT_CARD.sub(MASK, text)
    return text


def viewer_allows_scope(viewer_scopes: list[str], evidence_scope: str) -> bool:
    """
    Check if viewer's scopes allow access to evidence scope.

    Args:
        viewer_scopes: List of viewer's access scopes
        evidence_scope: Required scope for evidence

    Returns:
        True if viewer has required scope or "allow" scope

    Example:
        >>> viewer_allows_scope(["default", "pii"], "pii")
        True
        >>> viewer_allows_scope(["default"], "tenant")
        False
    """
    scopes = {s.lower() for s in viewer_scopes}

    # "allow" grants access to everything
    if "allow" in scopes:
        return True

    # Check if evidence scope is in viewer scopes
    return evidence_scope.lower() in scopes


def redact_for_viewer(text: str, viewer_scopes: list[str], evidence_scope: str) -> tuple[str, bool]:
    """
    Redact text based on viewer scopes and evidence requirements.

    Args:
        text: Original text
        viewer_scopes: Viewer's access scopes
        evidence_scope: Required scope for this evidence

    Returns:
        Tuple of (redacted_text, was_redacted)

    Example:
        >>> redact_for_viewer("Email: test@example.com", ["default"], "pii")
        ("Email: ██████", True)
    """
    if viewer_allows_scope(viewer_scopes, evidence_scope):
        return text, False

    # Viewer doesn't have required scope - mask PII
    redacted = mask_pii(text)
    return redacted, True
