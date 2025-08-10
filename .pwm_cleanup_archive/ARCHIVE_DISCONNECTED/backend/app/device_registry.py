"""
╭──────────────────────────────────────────────────────────────╮
│ MODULE      : device_registry.py                             │
│ DESCRIPTION : Symbolic device fingerprint and session tracking│
│ TYPE        : Device + App Linkage                           │
│ AUTHOR      : Lukhas Systems                                  │
│ UPDATED     : 2025-04-29                                     │
╰──────────────────────────────────────────────────────────────╯
"""

import json
from datetime import datetime
from pathlib import Path

DEVICE_REGISTRY_PATH = Path("device_registry.jsonl")


def register_device(user_id: int, device_fingerprint: str, app_type: str = "universal"):
    """
    Register a symbolic device or app interaction for a LucasID user.
    """
    entry = {
        "timestamp": str(datetime.utcnow()),
        "user_id": user_id,
        "device_fingerprint": device_fingerprint,
        "app_type": app_type,
    }

    DEVICE_REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(DEVICE_REGISTRY_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")

    print(f"🖥️ Device registered: {entry}")
    return entry


def get_user_devices(user_id: int):
    """
    Retrieve all symbolic devices linked to a specific LucasID user.
    """
    devices = []
    if DEVICE_REGISTRY_PATH.exists():
        with open(DEVICE_REGISTRY_PATH) as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if entry["user_id"] == user_id:
                        devices.append(entry)
                except json.JSONDecodeError:
                    continue
    return devices
