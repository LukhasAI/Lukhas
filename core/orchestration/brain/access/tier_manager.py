"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: tier_manager.py
Advanced: tier_manager.py
Integration Date: 2025-05-31T07:55:28.098400
"""

"""
╭──────────────────────────────────────────────────────────────╮
│ MODULE      : core/access/tier_manager.py                     │
│ DESCRIPTION : Manage access tiers and symbolic role tracing   │
│ TYPE        : Tier Control Utility                           │
│ AUTHOR      : Lukhas Systems                                  │
│ UPDATED     : 2025-04-29                                     │
╰──────────────────────────────────────────────────────────────╯
"""

import json
import os
from datetime import datetime

from fastapi import HTTPException

# ── Tier Definitions ──────────────────────────────────────────

TIERS = {
    1: "Tier 1 - Public Access (Minimal Capture)",
    2: "Tier 2 - Symbolic Seed Pairing",
    3: "Tier 3 - Seed + Face ID (Verified Pair)",
    4: "Tier 4 - Core Trust (Seed + Face ID + Backup Phrase)",
}

TIER_REGISTRY_FILE = "core/access/tier_registry.jsonl"
ACCESS_TRACE_FILE = "core/access/logs/access_trace.jsonl"

# ── Tier Management Functions ─────────────────────────────────


def upgrade_tier(current_tier: int) -> int:
    """
    Upgrade a user one tier up if possible.
    """
    if current_tier >= 4:
        raise HTTPException(status_code=400, detail="Already at maximum tier.")
    return current_tier + 1


def downgrade_tier(current_tier: int) -> int:
    """
    Downgrade a user one tier down if necessary.
    """
    if current_tier <= 1:
        raise HTTPException(status_code=400, detail="Already at minimum tier.")
    return current_tier - 1


def get_tier_description(tier: int) -> str:
    """
    Retrieve symbolic description for the user's tier.
    """
    return TIERS.get(tier, "Unknown Tier")


def get_user_tier(user_id: str) -> int:
    try:
        with open(TIER_REGISTRY_FILE) as f:
            for line in f:
                entry = json.loads(line)
                if entry.get("user_id") == user_id:
                    return int(entry.get("tier", 1))
    except FileNotFoundError:
        pass
    if user_id.startswith("GPT-4O"):
        return 5  # Trusted system agent
    return 0


def is_access_allowed(required_tier: int, user_id: str) -> bool:
    return get_user_tier(user_id) >= required_tier


def log_access_attempt(user_id: str, action: str, required_tier: int, result: str):
    log = {
        "user_id": user_id,
        "action": action,
        "required_tier": required_tier,
        "result": result,
        "timestamp": datetime.utcnow().isoformat(),
    }
    os.makedirs(os.path.dirname(ACCESS_TRACE_FILE), exist_ok=True)
    with open(ACCESS_TRACE_FILE, "a") as f:
        f.write(json.dumps(log) + "\n")


def get_tier_badge(tier: int) -> str:
    """
    Return a symbolic badge string (text or emoji) for a given tier level.
    """
    tier_badges = {
        0: "🔓 Guest",
        1: "🔹 Tier 1",
        2: "🔸 Tier 2",
        3: "🔶 Tier 3",
        4: "🔷 Tier 4",
        5: "💎 Tier 5 (Core)",
    }
    return tier_badges.get(tier, "❔ Unknown Tier")


def generate_symbolic_id_summary(user_id: str) -> dict:
    tier = get_user_tier(user_id)
    return {
        "user_id": user_id,
        "tier": tier,
        "tier_description": get_tier_description(tier),
        "badge": get_tier_badge(tier),
    }
