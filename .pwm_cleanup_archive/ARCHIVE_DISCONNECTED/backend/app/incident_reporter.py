"""
╭──────────────────────────────────────────────────────────────╮
│ MODULE      : incident_reporter.py                           │
│ DESCRIPTION : Symbolic detection of security incidents       │
│ TYPE        : Incident Monitoring                            │
│ AUTHOR      : Lukhas Systems                                  │
│ UPDATED     : 2025-04-29                                     │
╰──────────────────────────────────────────────────────────────╯
"""

from datetime import datetime

# ── Symbolic In-Memory Incident List (for demo) ─────────────────

incident_reports = []


def detect_suspicious_activity(event: dict):
    """
    Analyze an event for symbolic signs of risk.
    Example: unusual Tier changes, rapid logins, vault access spikes.
    """
    if event.get("action") == "TIER_UPGRADE" and event.get("tier_change") > 1:
        report_incident(
            user_id=event["user_id"], reason="⚠️ Unusual rapid tier escalation"
        )

    if event.get("action") == "VAULT_DOWNLOAD" and event.get("downloads") > 10:
        report_incident(user_id=event["user_id"], reason="⚠️ Excessive vault downloads")


def report_incident(user_id: int, reason: str):
    """
    Symbolically log an incident for further review.
    """
    incident = {
        "timestamp": str(datetime.utcnow()),
        "user_id": user_id,
        "reason": reason,
    }
    incident_reports.append(incident)
    print(f"🚨 Incident reported: {incident}")


def get_all_incidents():
    """
    Retrieve all symbolic incident reports.
    """
    return incident_reports
