"""
╭──────────────────────────────────────────────────────────────╮
│ MODULE      : journey_log_manager.py                         │
│ DESCRIPTION : Symbolic journey and location memory tracker   │
│ TYPE        : Travel Log + Symbolic Mapping Manager          │
│ AUTHOR      : Lukhas Systems                                  │
│ UPDATED     : 2025-04-29                                     │
╰──────────────────────────────────────────────────────────────╯
"""

import json
from datetime import datetime
from pathlib import Path

JOURNEY_LOG_PATH = Path("journey_logs.jsonl")


def record_journey_event(user_id: int, location_name: str, symbolic_reflection: str):
    """
    Log a symbolic journey event with a location and memory reflection.
    """
    event = {
        "timestamp": str(datetime.utcnow()),
        "user_id": user_id,
        "location_name": location_name,
        "symbolic_reflection": symbolic_reflection,
    }

    JOURNEY_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(JOURNEY_LOG_PATH, "a") as f:
        f.write(json.dumps(event) + "\n")

    print(f"🗺️ Journey memory recorded: {event}")
    return event


def get_user_journey_logs(user_id: int):
    """
    Retrieve all symbolic journey logs for a user.
    """
    journeys = []
    if JOURNEY_LOG_PATH.exists():
        with open(JOURNEY_LOG_PATH) as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if entry["user_id"] == user_id:
                        journeys.append(entry)
                except json.JSONDecodeError:
                    continue
    return journeys


# ===============================================================
# 💾 HOW TO USE
# ===============================================================
# ▶️ IMPORT THIS MODULE:
#     from backend.app.journey_log_manager import record_journey_event, get_user_journey_logs
#
# 🧠 WHAT THIS MODULE DOES:
# - Symbolically records user journeys, places, and emotional reflections
# - Allows retrieval of symbolic travel history
#
# 🧑‍🏫 GOOD FOR:
# - Personal journey mapping
# - Dream-linked location memory replays
# - Symbolic path visualization for LucasID Mesh
# ===============================================================
