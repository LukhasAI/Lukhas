"""
╭──────────────────────────────────────────────────────────────╮
│ MODULE      : admin_tools.py                                 │
│ DESCRIPTION : Admin-level utilities for LUKHASID system       │
│ TYPE        : Admin Tools + Control Panel API                │
│ AUTHOR      : Lukhas Systems                                  │
│ UPDATED     : 2025-04-29                                     │
╰──────────────────────────────────────────────────────────────╯
"""

from backend.app.tier_manager import downgrade_tier, upgrade_tier
from backend.app.token_handler import create_access_token
from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.post("/admin/upgrade/{user_id}")
def force_upgrade(user_id: int, current_tier: int):
    """
    Admin function to force upgrade a user's tier (if compliant).
    """
    try:
        new_tier = upgrade_tier(current_tier)
        print(f"🛡️ Admin upgraded user {user_id} to Tier {new_tier}")
        return {"message": f"User {user_id} upgraded to Tier {new_tier}"}
    except HTTPException as e:
        raise e


@router.post("/admin/downgrade/{user_id}")
def force_downgrade(user_id: int, current_tier: int):
    """
    Admin function to downgrade a user's tier.
    """
    try:
        new_tier = downgrade_tier(current_tier)
        print(f"⚠️ Admin downgraded user {user_id} to Tier {new_tier}")
        return {"message": f"User {user_id} downgraded to Tier {new_tier}"}
    except HTTPException as e:
        raise e


@router.get("/admin/token/{user_id}")
def generate_admin_token(user_id: int):
    """
    Admin-only: generate access token manually for a user.
    """
    token = create_access_token({"user_id": user_id, "admin_override": True})
    return {"token": token}
