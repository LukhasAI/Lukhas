"""
Login wrapper for backward compatibility
Routes to identity_core.py
"""

from typing import Any, Dict

from .identity_core import AccessTier, identity_core


def login_user(email: str, password: str) -> Dict[str, Any]:
    """Legacy login function - routes to identity_core"""
    # TODO: Implement proper password validation
    # For now, create a token with default T2 tier
    user_id = email.split("@")[0].replace(".", "_").lower()
    metadata = {
        "email": email,
        "consent": True,
        "trinity_score": 0.5,
        "drift_score": 0.0,
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
