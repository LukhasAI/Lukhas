"""
Registration wrapper with proper security implementation
Routes to identity_core.py with password hashing and user storage
"""

import hashlib
import secrets
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from .identity_core import AccessTier, identity_core


def _hash_password(password: str, salt: bytes) -> bytes:
    """Hash password using PBKDF2-SHA256 with salt"""
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)


def _store_user_data(user_id: str, user_data: Dict[str, Any]) -> None:
    """Store user data securely to file system"""
    # Create users directory if it doesn't exist
    users_dir = Path("data/users")
    users_dir.mkdir(parents=True, exist_ok=True)
    
    # Store user data as JSON file
    user_file = users_dir / f"{user_id}.json"
    with open(user_file, 'w') as f:
        json.dump(user_data, f, indent=2)


def register_user(
    email: str, password: str, requested_tier: Optional[str] = None
) -> Dict[str, Any]:
    """Secure registration function with proper password hashing and user storage"""
    
    # Implement secure password hashing
    salt = secrets.token_bytes(32)
    password_hash = _hash_password(password, salt)
    
    # Implement proper user storage
    user_data = {
        "email": email,
        "password_hash": password_hash.hex(),
        "salt": salt.hex(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "is_active": True,
        "login_attempts": 0,
        "last_login": None
    }
    
    # Store user securely
    user_id = email.split("@")[0].replace(".", "_").lower()
    _store_user_data(user_id, user_data)

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
