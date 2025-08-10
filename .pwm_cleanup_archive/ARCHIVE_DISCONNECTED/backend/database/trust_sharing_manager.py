"""
╭──────────────────────────────────────────────────────────────╮
│ MODULE      : trust_sharing_manager.py                       │
│ DESCRIPTION : Manage symbolic trusted vault sharing requests │
│ TYPE        : Trust Mesh Core                                │
│ AUTHOR      : Lukhas Systems                                  │
│ UPDATED     : 2025-04-29                                     │
╰──────────────────────────────────────────────────────────────╯
"""

import json
from datetime import datetime
from pathlib import Path

TRUST_SHARING_REGISTRY = Path("trust_sharing_registry.jsonl")


def initiate_vault_share(
    grantor_id: int, grantee_id: int, share_type: str, vault_reference: str
):
    """
    Create a symbolic record of a vault sharing request.
    """
    entry = {
        "timestamp": str(datetime.utcnow()),
        "grantor_id": grantor_id,
        "grantee_id": grantee_id,
        "share_type": share_type,  # full_access | partial | locked
        "vault_reference": vault_reference,
        "status": "pending",
    }

    TRUST_SHARING_REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    with open(TRUST_SHARING_REGISTRY, "a") as f:
        f.write(json.dumps(entry) + "\n")

    print(f"🤝 Vault sharing initiated: {entry}")
    return entry


def list_trust_shares_for_user(user_id: int):
    """
    Retrieve all symbolic vault shares where user is the grantee.
    """
    shares = []
    if TRUST_SHARING_REGISTRY.exists():
        with open(TRUST_SHARING_REGISTRY) as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if entry["grantee_id"] == user_id:
                        shares.append(entry)
                except json.JSONDecodeError:
                    continue
    return shares


# ===============================================================
# 💾 HOW TO USE
# ===============================================================
# ▶️ IMPORT THIS MODULE:
#     from backend.database.trust_sharing_manager import initiate_vault_share, list_trust_shares_for_user
#
# 🧠 WHAT THIS MODULE DOES:
# - Initiates symbolic trusted vault sharing between LucasID users
# - Tracks full/partial/locked vault share offers
#
# 🧑‍🏫 GOOD FOR:
# - Symbolic trust bonding
# - Personal vault backups across the mesh
# - Emergency symbolic recoverability
# ===============================================================
