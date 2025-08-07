"""
╭──────────────────────────────────────────────────────────────╮
│ MODULE      : users.py                                       │
│ DESCRIPTION : Symbolic user profile API for LUKHASID          │
│ TYPE        : Public Profile + Identity Slug Resolver        │
│ AUTHOR      : Lukhas Systems                                  │
│ UPDATED     : 2025-04-29                                     │
╰──────────────────────────────────────────────────────────────╯
"""

from fastapi import APIRouter, HTTPException
from backend.database.models import User
from backend.database.crud import get_user_by_slug

router = APIRouter()

@router.get("/users/{username_slug}")
def get_user_profile(username_slug: str):
    """
    Return public symbolic LUKHASID profile data for a user.
    """
    user = get_user_by_slug(username_slug)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "username": user.username_slug,
        "identity_legacy_code": user.lukhas_id_code,
        "entity_type": user.entity_type,
        "tier": user.tier,
        "qrglyph_url": user.qrglyph_url,
        "created_at": user.created_at
    }
