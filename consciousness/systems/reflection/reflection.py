import json
from datetime import datetime
from pathlib import Path

# from Lukhas_ID.lid_ref import sign_with_lid  # Adjust import path based on actual project structure

AUDIT_LOG_PATH = Path(__file__).parent / "audits" / "audit_log.jsonl"


def write_reflection_event(event_type: str, details: dict, lid_signature: str = None):
    """Logs a symbolic AI event with timestamp and optional ΛiD trace signature."""
    """Logs a symbolic AI event with timestamp and optional Lukhas_ID trace signature."""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "details": details,
        "lid_signature": lid_signature or sign_with_lid(details),
    }

    with open(AUDIT_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")

    return log_entry
