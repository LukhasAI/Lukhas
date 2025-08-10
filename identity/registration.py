"""
Registration wrapper for backward compatibility
Routes to identity_core.py
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from .identity_core import AccessTier, identity_core


def register_user(
    email: str, password: str, requested_tier: Optional[str] = None
) -> Dict[str, Any]:
    """Legacy registration function - routes to identity_core"""
    # TODO: Implement proper user storage and password hashing

    # Determine tier (default to T2 for new users)
    tier_map = {
        "T1": AccessTier.T1,
        "T2": AccessTier.T2,
        "T3": AccessTier.T3,
        "T4": AccessTier.T4,
        "T5": AccessTier.T5,
    }
    tier = tier_map.get(requested_tier, AccessTier.T2)

    user_id = email.split("@")[0].replace(".", "_").lower()
    metadata = {
        "email": email,
        "consent": True,
        "trinity_score": 0.3,
        "drift_score": 0.0,
        "cultural_profile": "universal",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    token = identity_core.create_token(user_id, tier, metadata)
    glyphs = identity_core.generate_identity_glyph(email)

    return {
        "success": True,
        "user_id": user_id,
        "token": token,
        "tier": tier.value,
        "glyphs": glyphs,
        "message": f"User registered with tier {tier.value}",
    }
