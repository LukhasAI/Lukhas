"""

#TAG:memory
#TAG:temporal
#TAG:neuroplastic
#TAG:colony


Enhanced Core TypeScript - Integrated from Advanced Systems
Original: dream_log.py
Advanced: dream_log.py
Integration Date: 2025-05-31T07:55:28.204794
"""

from datetime import timezone

"""
dream_log.py
------------
Handles symbolic dream memory logging for Lucʌs.

Each dream is stored as a JSON object in 'data/dream_log.jsonl',
supporting one dream per line for easy append-only memory streams.
"""

import json
import os
from datetime import datetime

LOG_PATH = "data/dream_log.jsonl"


def log_dream(dream_data: dict):
    """
    Appends a symbolic dream to the dream log as a JSON line.
    Adds a timestamp automatically if not present.
    """
    try:
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

        if "timestamp" not in dream_data:
            dream_data["timestamp"] = datetime.now(timezone.utc).isoformat()

        with open(LOG_PATH, "a", encoding="utf-8") as f:
            json.dump(dream_data, f)
            f.write("\n")

        print(f"📝 Dream logged at {dream_data['timestamp']}")

    except Exception as e:
        print(f"⚠️ Failed to log dream: {e}")
