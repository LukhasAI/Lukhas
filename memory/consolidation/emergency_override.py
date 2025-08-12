# TAG:memory
# TAG:consolidation
# TAG:neuroplastic
# TAG:colony


import json
import os
from datetime import datetime

from settings_loader import get_setting

emergency_override.py

# ════════════════════════════════════════════════════════════════════════
# 📁 FILE: emergency_override.py
# 🛡️ PURPOSE: Lukhas emergency response handler for failsafe shutdown, alerts, and audits
# 🔄 CONNECTS TO: lukhas_settings.json, settings_loader.py, memory systems
# 🏛️ COMPLIANCE: Institutional and legal compliance aware; logs GDPR and audit readiness on incidents.
# ════════════════════════════════════════════════════════════════════════


EMERGENCY_LOG_PATH = "logs/emergency_log.jsonl"


def check_safety_flags(user_context=None):
    """
    Checks safety flags and tier permissions based on user context.
    """
    safe_mode = get_setting("system_behavior.safe_mode", False)
    refuse_unknown = get_setting("system_behavior.refuse_non_identified", True)
    user_tier = user_context.get("tier", 1) if user_context else 1

    if safe_mode or (refuse_unknown and user_tier < 2):
        print("🚨 Emergency triggered due to insufficient tier or unknown user.")
        if not user_context or user_context.get("tier", 1) < 2:
            print("⚠️ WARNING: Emergency triggered by unknown/unauthorized actor.")
        return True
    return False


def shutdown_systems(reason="Unspecified emergency condition"):
    """
    Symbolic shutdown placeholder. In a real deployment, this could cut access to speech, internet, etc.
    """
    print("🚨 Emergency Override Triggered")
    print(f"Reason: {reason}")
    print("Disabling voice output, internet queries, and proactive actions.")


def log_incident(reason, user_context=None):
    """
    Append emergency incident details to a secure audit log, including compliance flags.
    """
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "reason": reason,
        "source": "lukhas_emergency_override",
        "user": user_context.get("user", "unknown") if user_context else "unknown",
        "tier": user_context.get("tier", 0) if user_context else 0,
        "institutional_compliance": {
            "gdpr": True,
            "audit_ready": True,
            "access_logged": True,
        },
        "actions_taken": ["voice_disabled", "internet_disabled", "proactivity_off"],
    }
    os.makedirs("logs", exist_ok=True)
    with open(EMERGENCY_LOG_PATH, "a") as f:
        f.write(json.dumps(log_entry) + "\n")
