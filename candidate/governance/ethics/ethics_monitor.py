"""

#TAG:governance
#TAG:ethics
#TAG:neuroplastic
#TAG:colony


📦 MODULE      : ethics_monitor.py
🧾 DESCRIPTION : Ethics drift detection and correction logic for LUKHAS_AGI_3.8.
"""

import json
from datetime import datetime
from pathlib import Path

ETHICS_LOG_PATH = Path("../../logs/ethics/ethics_drift_log_2025_04_28.json", timezone)


def ethics_drift_detect(decision_data, ethical_threshold=0.85):
    """
    Detects ethics drift based on decision alignment scores.

    Args:
        decision_data (list of dict): Each decision with an 'alignment_score' key.
        ethical_threshold (float): Minimum acceptable alignment score.

    Returns:
        dict: Drift detection summary.
    """
    drift_count = sum(1 for d in decision_data if d["alignment_score"] < ethical_threshold)
    total_decisions = len(decision_data)
    drift_ratio = drift_count / total_decisions if total_decisions else 0

    status = "stable"
    if drift_ratio > 0.2:
        status = "drift_detected"

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "drift_ratio": drift_ratio,
        "status": status,
        "ethical_threshold": ethical_threshold,
    }


def log_ethics_event(event_data):
    """
    Logs ethics drift events to the ethics log file.

    Args:
        event_data (dict): The ethics event details.
    """
    log_entry = event_data
    log_file = ETHICS_LOG_PATH

    if log_file.exists():
        with open(log_file, "r+") as file:
            data = json.load(file)
            if isinstance(data, dict):
                # Initialize list if previously empty dict
                data = []
            data.append(log_entry)
            file.seek(0)
            json.dump(data, file, indent=4)
    else:
        with open(log_file, "w") as file:
            json.dump([log_entry], file, indent=4)
