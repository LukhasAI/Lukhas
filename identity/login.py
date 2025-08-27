"""
LUKHAS AI Login System
=====================

Enhanced login and signup functionality with database persistence.
Integrates with the existing identity_core system and symbolic authentication.

Trinity Framework: ⚛️ (Identity), 🧠 (Consciousness), 🛡️ (Guardian)
"""

import re
import logging
from typing import Any, Optional

from .identity_core import AccessTier, identity_core
from .store import create_user, verify_user, User

logger = logging.getLogger(__name__)

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


def normalize_email(email: str) -> str:
    """
    Normalize email address for consistent processing.
    
    Args:
        email: Raw email address
        
    Returns:
        Normalized email address
    """
    if not email or "@" not in email:
        raise ValueError("Invalid email format")
    
    # Basic email validation
    parts = email.split("@")
    if len(parts) != 2 or not parts[0] or not parts[1] or "." not in parts[1]:
        raise ValueError("Invalid email format")
    
    return email.lower().strip()


def signup(email: str, password: str) -> dict[str, Any]:
    """
    Create a new user account with email and password.
    
    Args:
        email: User email address
        password: Plain text password
        
    Returns:
        Dictionary with success status and user/token info
    """
    try:
        # Normalize email
        normalized_email = normalize_email(email)
        
        # Validate password strength
        is_valid, error_message = validate_password(password)
        if not is_valid:
            return {
                "success": False,
                "error": f"Password validation failed: {error_message}",
                "user_id": None,
                "token": None
            }
        
        # Create user in database
        try:
            user = create_user(normalized_email, password)
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                return {
                    "success": False,
                    "error": f"User with email {normalized_email} already exists",
                    "user_id": None,
                    "token": None
                }
            raise
        
        if not user:
            return {
                "success": False,
                "error": "Failed to create user account",
                "user_id": None,
                "token": None
            }
        
        # Generate user_id for token (backward compatibility)
        user_id = normalized_email.split("@")[0].replace(".", "_").lower()
        
        # Create metadata for token
        metadata = {
            "email": normalized_email,
            "user_db_id": user.id,
            "consent": True,
            "trinity_score": 0.5,
            "drift_score": 0.0,
            "password_validated": True,
            "crypto_available": CRYPTO_AVAILABLE,
            "security_level": "enhanced" if CRYPTO_AVAILABLE else "basic",
            "mfa_level": user.mfa_level,
        }
        
        # Create JWT token using existing identity_core
        token = identity_core.create_token(user_id, AccessTier.T2, metadata)
        
        logger.info(f"User signup successful: {normalized_email} (ID: {user.id})")
        
        return {
            "success": True,
            "token": token,
            "user_id": user_id,
            "user_db_id": user.id,
            "tier": "T2",
            "glyphs": identity_core.generate_identity_glyph(normalized_email),
        }
        
    except ValueError as e:
        logger.warning(f"Signup validation error: {e}")
        return {
            "success": False,
            "error": str(e),
            "user_id": None,
            "token": None
        }
    except Exception as e:
        logger.error(f"Signup error for {email}: {e}")
        return {
            "success": False,
            "error": "Internal server error during signup",
            "user_id": None,
            "token": None
        }


def login_user(email: str, password: str) -> dict[str, Any]:
    """
    Enhanced login function with database authentication.
    
    Args:
        email: User email address
        password: Plain text password
        
    Returns:
        Dictionary with success status and user/token info
    """
    try:
        # Normalize email
        normalized_email = normalize_email(email)
        
        # Authenticate against database
        user = verify_user(normalized_email, password)
        
        if not user:
            return {
                "success": False,
                "error": "Invalid email or password",
                "user_id": None,
                "token": None
            }
        
        # Generate user_id for token (backward compatibility)
        user_id = normalized_email.split("@")[0].replace(".", "_").lower()
        
        # Create metadata for token
        metadata = {
            "email": normalized_email,
            "user_db_id": user.id,
            "consent": True,
            "trinity_score": 0.5,
            "drift_score": 0.0,
            "password_validated": True,
            "crypto_available": CRYPTO_AVAILABLE,
            "security_level": "enhanced" if CRYPTO_AVAILABLE else "basic",
            "mfa_level": user.mfa_level,
        }
        
        # Create JWT token using existing identity_core
        token = identity_core.create_token(user_id, AccessTier.T2, metadata)
        
        logger.info(f"User login successful: {normalized_email} (ID: {user.id})")
        
        return {
            "success": True,
            "token": token,
            "user_id": user_id,
            "user_db_id": user.id,
            "tier": "T2",
            "glyphs": identity_core.generate_identity_glyph(normalized_email),
        }
        
    except ValueError as e:
        logger.warning(f"Login validation error: {e}")
        return {
            "success": False,
            "error": str(e),
            "user_id": None,
            "token": None
        }
    except Exception as e:
        logger.error(f"Login error for {email}: {e}")
        return {
            "success": False,
            "error": "Internal server error during login",
            "user_id": None,
            "token": None
        }


def logout_user(token: str) -> bool:
    """Legacy logout function - routes to identity_core"""
    return identity_core.revoke_token(token)
