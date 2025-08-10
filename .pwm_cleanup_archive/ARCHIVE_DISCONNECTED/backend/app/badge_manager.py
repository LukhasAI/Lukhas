"""
╭──────────────────────────────────────────────────────────────╮
│ MODULE      : badge_manager.py                               │
│ DESCRIPTION : Symbolic badge issuer for LucasID mesh users   │
│ TYPE        : Badge Manager                                  │
│ AUTHOR      : Lukhas Systems                                  │
│ UPDATED     : 2025-04-29                                     │
╰──────────────────────────────────────────────────────────────╯
"""

import json
from datetime import datetime
from pathlib import Path

# ── Load Badge Definitions ────────────────────────────────────

BADGE_REGISTRY_PATH = Path(__file__).parent.parent / "data" / "badge_registry.json"

with open(BADGE_REGISTRY_PATH) as f:
    BADGES = json.load(f)

# ── Badge Management Functions ─────────────────────────────────


def assign_badge(user_id: int, badge_code: str) -> dict:
    """
    Assign a symbolic badge to a LucasID user.
    """
    if badge_code not in BADGES:
        raise ValueError("Invalid badge code.")

    awarded = {
        "user_id": user_id,
        "badge_code": badge_code,
        "badge_name": BADGES[badge_code]["label"],
        "tier_required": BADGES[badge_code]["tier_required"],
        "awarded_at": datetime.utcnow(),
    }
    print(f"🏅 Badge '{BADGES[badge_code]['label']}' assigned to user {user_id}.")
    return awarded


def list_available_badges() -> dict:
    """
    List all symbolic badges available.
    """
    return BADGES
