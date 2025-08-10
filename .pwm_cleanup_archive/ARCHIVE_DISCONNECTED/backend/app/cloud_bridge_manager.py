"""
╭──────────────────────────────────────────────────────────────╮
│ MODULE      : cloud_bridge_manager.py                        │
│ DESCRIPTION : Universal symbolic cloud bridge handler        │
│ TYPE        : Cloud Bridge Engine                            │
│ AUTHOR      : Lukhas Systems                                  │
│ UPDATED     : 2025-04-29                                     │
╰──────────────────────────────────────────────────────────────╯
"""

import shutil
from datetime import datetime
from pathlib import Path

# ── Tier-Based Cloud Directories ───────────────────────────────

BASE_CLOUD_STORAGE = {
    1: "cloud_storage_tier1",
    2: "cloud_storage_tier2",
    3: "cloud_storage_tier3",
    4: "cloud_storage_tier4",
}

# ── Universal Cloud Bridge Core Functions ──────────────────────


def upload_to_bridge(user_id: int, vault_type: str, file_path: str, user_tier: int):
    """
    Upload a file to the symbolic cloud bridge, routed by tier and app type.
    """
    base_dir = BASE_CLOUD_STORAGE.get(user_tier)
    if not base_dir:
        raise ValueError("Invalid user tier.")

    destination = Path(base_dir) / str(user_id) / vault_type
    destination.mkdir(parents=True, exist_ok=True)

    filename = f"{vault_type}_{datetime.utcnow().timestamp()}.bin"
    shutil.copy(file_path, destination / filename)

    print(f"🌉 Cloud bridge upload complete: {destination}/{filename}")
    return str(destination / filename)


def sync_from_bridge(user_id: int, app_target: str, user_tier: int):
    """
    Retrieve available files for a specific app backup (e.g., Apple, WhatsApp).
    """
    base_dir = BASE_CLOUD_STORAGE.get(user_tier)
    if not base_dir:
        raise ValueError("Invalid user tier.")

    target_dir = Path(base_dir) / str(user_id) / app_target
    if not target_dir.exists():
        raise FileNotFoundError(f"No symbolic backups found for {app_target}.")

    files = [f.name for f in target_dir.iterdir() if f.is_file()]
    return files


def list_bridge_assets(user_id: int, user_tier: int):
    """
    List all vault_types the user has symbolic backups for.
    """
    base_dir = BASE_CLOUD_STORAGE.get(user_tier)
    if not base_dir:
        raise ValueError("Invalid user tier.")

    user_dir = Path(base_dir) / str(user_id)
    if not user_dir.exists():
        return []

    apps = [d.name for d in user_dir.iterdir() if d.is_dir()]
    return apps


# ── Optional Device Registry Integration (Phase 2) ──────────────

DEVICE_REGISTRY_PATH = Path("device_registry.jsonl")


def register_device(user_id: int, device_fingerprint: str):
    """
    Register a symbolic device fingerprint linked to this LucasID.
    """
    entry = {
        "user_id": user_id,
        "device": device_fingerprint,
        "registered_at": str(datetime.utcnow()),
    }

    DEVICE_REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(DEVICE_REGISTRY_PATH, "a") as f:
        f.write(str(entry) + "\n")

    print(f"🖥️ Device registered for symbolic mesh: {device_fingerprint}")
    return entry
