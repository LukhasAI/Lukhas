"""
Login wrapper for backward compatibility
Routes to identity_core.py
"""

import re
from typing import Any

from .identity_core import AccessTier, identity_core

# Try to import crypto for password validation
try:
    from core.security.enhanced_crypto import LukhaCryptoManager
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False


def validate_password(password: str):
    """
    Validate password strength and format
    Returns (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"

    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character"

    # Check for common weak patterns
    weak_patterns = [
        r"password", r"123456", r"qwerty", r"admin",
        r"letmein", r"welcome", r"monkey", r"dragon"
    ]

    for pattern in weak_patterns:
        if re.search(pattern, password, re.IGNORECASE):
            return False, f"Password contains common weak pattern: {pattern}"

    return True, "Password is valid"


def login_user(email: str, password: str) -> dict[str, Any]:
    """Enhanced login function with password validation"""
    # Validate password strength
    is_valid, error_message = validate_password(password)
    if not is_valid:
        return {
            "success": False,
            "error": f"Password validation failed: {error_message}",
            "user_id": None,
            "token": None
        }

    # Enhanced user ID generation with validation
    if "@" not in email or "." not in email.split("@")[1]:
        return {
            "success": False,
            "error": "Invalid email format",
            "user_id": None,
            "token": None
        }

    user_id = email.split("@")[0].replace(".", "_").lower()

    # Enhanced metadata with security info
    metadata = {
        "email": email,
        "consent": True,
        "trinity_score": 0.5,
        "drift_score": 0.0,
        "password_validated": True,
        "crypto_available": CRYPTO_AVAILABLE,
        "security_level": "enhanced" if CRYPTO_AVAILABLE else "basic"
    }

    token = identity_core.create_token(user_id, AccessTier.T2, metadata)

    return {
        "success": True,
        "token": token,
        "user_id": user_id,
        "tier": "T2",
        "glyphs": identity_core.generate_identity_glyph(email),
    }


def logout_user(token: str) -> bool:
    """Legacy logout function - routes to identity_core"""
    return identity_core.revoke_token(token)
