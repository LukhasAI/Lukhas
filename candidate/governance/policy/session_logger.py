"""

#TAG:governance
#TAG:policy
#TAG:neuroplastic
#TAG:colony


┌────────────────────────────────────────────────────────────────────────────┐
│ 📦 MODULE      : session_logger.py                                         │
│ 🧾 DESCRIPTION : Logs session start/end for LUCΛSiD dashboards             │
│ 🧩 TYPE        : Compliance Utility     🔧 VERSION: v1.0.0                  │
│ 🖋️ AUTHOR      : LUCAS SYSTEMS          📅 UPDATED: 2025-05-05              │
├────────────────────────────────────────────────────────────────────────────┤
│ 📚 DEPENDENCIES:                                                           │
│   - datetime                                                              │
│   - json                                                                  │
│   - pathlib.Path                                                          │
│   - os                                                                    │
│   - pytz                                                                  │
└────────────────────────────────────────────────────────────────────────────┘
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import pytz

LOG_PATH = Path("logs/session_log.jsonl")
POLICY_PATH = Path("secure_context_policy.json")
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)


def is_access_allowed(user_id: str):
    now = datetime.now(pytz.timezone("Europe/Madrid"))
    with POLICY_PATH.open() as f:
        policy = json.load(f)

    # Working hours check
    start = policy["working_hours"]["start_hour"]
    end = policy["working_hours"]["end_hour"]
    allowed_days = policy["working_hours"]["allowed_days"]
    if now.strftime("%A") not in allowed_days:
        return False, "Access outside allowed days"
    if not (start <= now.hour < end):
        return False, "Access outside working hours"

    # Device check
    trusted = policy["trusted_devices"].get(user_id, [])
    device = os.environ.get("DEVICE_ID", "UNKNOWN_DEVICE")
    if device not in trusted:
        return False, "Unrecognized device"

    # Network security checks
    ip = os.environ.get("USER_IP", "0.0.0.0")
    vpn = os.environ.get("VPN_ENABLED", "false").lower() == "true"
    net_sec = policy.get("network_security", {})
    if ip not in net_sec.get("allowed_ips", []):
        return False, f"IP {ip} not allowed"
    if net_sec.get("vpn_required", False) and not vpn:
        return False, "VPN required but not enabled"

    # Session type rules
    session_type = os.environ.get("SESSION_TYPE", "unknown")
    session_rules = policy.get("session_types", {}).get(session_type)
    if not session_rules:
        return False, f"Unknown or unauthorized session type: {session_type}"
    if session_rules.get("requires_vpn", False) and not vpn:
        return False, f"{session_type} sessions require VPN"
    if device not in session_rules.get("allowed_devices", []):
        return False, f"Device not allowed for {session_type} session"

    return True, "Access allowed"


def log_session_event(user_id: str, event: str):
    """Log a session start or end event with policy enforcement."""
    allowed, reason = is_access_allowed(user_id)
    entry = {
        "user": user_id or "anonymous",
        "event": event,
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        "access_check": reason,
        "policy_compliant": allowed,
    }
    with LOG_PATH.open("a") as f:
        f.write(json.dumps(entry) + "\n")