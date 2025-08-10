"""
╭──────────────────────────────────────────────────────────────╮
│ MODULE      : email_logs.py                                  │
│ DESCRIPTION : Symbolic log archive for outbound emails       │
│ TYPE        : Email Audit Trail                              │
│ AUTHOR      : Lukhas Systems                                  │
│ UPDATED     : 2025-04-29                                     │
╰──────────────────────────────────────────────────────────────╯
"""

from datetime import datetime

# ── In-memory symbolic email log (to be migrated to DB later) ──

email_log = []


def log_email_event(to_email: str, subject: str, purpose: str = "N/A"):
    """
    Record an outbound symbolic email event.
    """
    entry = {
        "timestamp": str(datetime.utcnow()),
        "to": to_email,
        "subject": subject,
        "purpose": purpose,
    }
    email_log.append(entry)
    print(f"📬 Email log entry: {entry}")
    return entry


def get_all_email_logs():
    """
    Retrieve all symbolic email logs.
    """
    return email_log


def get_user_email_logs(email: str):
    """
    Retrieve symbolic email logs sent to a specific address.
    """
    return [entry for entry in email_log if entry["to"] == email]
