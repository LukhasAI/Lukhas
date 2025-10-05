"""
Signed permalink generation and verification for audit trails.
Provides short-lived HMAC tokens tied to viewer identity.
"""
import hmac
import os
import time
from hashlib import sha256
from typing import Dict, Tuple

SECRET = (os.getenv("AUDIT_LINK_SECRET") or "dev-secret").encode()


def _sig(payload: str) -> str:
    """Generate HMAC-SHA256 signature for payload."""
    return hmac.new(SECRET, payload.encode(), sha256).hexdigest()


def mint_signed_query(trace_id: str, viewer_id: str, ttl_seconds: int = 300) -> str:
    """
    Generate a signed query string for audit trail access.

    Args:
        trace_id: Trace ID to grant access to
        viewer_id: Viewer identity (from ΛID or auth system)
        ttl_seconds: Time-to-live in seconds (default 5 minutes)

    Returns:
        Signed query string: trace=...&viewer=...&exp=...&sig=...

    Example:
        >>> query = mint_signed_query("abc123", "user@example.com", 300)
        >>> # Returns: "trace=abc123&viewer=user@example.com&exp=1234567890&sig=..."
    """
    exp = int(time.time()) + int(ttl_seconds)
    payload = f"trace={trace_id}&viewer={viewer_id}&exp={exp}"
    sig = _sig(payload)
    return payload + "&sig=" + sig


def verify_signed_query(trace_id: str, params: Dict[str, str]) -> Tuple[bool, str]:
    """
    Verify a signed query string.

    Args:
        trace_id: Expected trace ID
        params: Query parameters dict (trace, viewer, exp, sig)

    Returns:
        Tuple of (is_valid, reason)

    Example:
        >>> ok, reason = verify_signed_query("abc123", {"trace": "abc123", ...})
        >>> if not ok:
        ...     print(f"Invalid: {reason}")
    """
    viewer = params.get("viewer")
    exp = params.get("exp")
    sig = params.get("sig")

    if not (viewer and exp and sig):
        return False, "missing params"

    try:
        exp_i = int(exp)
    except ValueError:
        return False, "bad exp"

    if time.time() > exp_i:
        return False, "expired"

    payload = f"trace={trace_id}&viewer={viewer}&exp={exp_i}"
    if not hmac.compare_digest(_sig(payload), sig):
        return False, "bad signature"

    return True, "ok"
