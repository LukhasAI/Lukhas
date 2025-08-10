"""
╭──────────────────────────────────────────────────────────────╮
│ MODULE      : audit_logger.py                                │
│ DESCRIPTION : Symbolic audit logging for LUKHASID actions     │
│ TYPE        : Audit Logger                                   │
│ AUTHOR      : Lukhas Systems                                  │
│ UPDATED     : 2025-04-29                                     │
╰──────────────────────────────────────────────────────────────╯
"""

from datetime import datetime

# ── Symbolic Audit Log Store (In-memory for now) ─────────────────

audit_logs = []


def log_action(user_id: int, action: str, details: str = "N/A"):
    """
    Record a symbolic audit entry for important LUKHASID events.
    """
    entry = {
        "timestamp": str(datetime.utcnow()),
        "user_id": user_id,
        "action": action,
        "details": details,
    }
    audit_logs.append(entry)
    print(f"📝 Audit Log: {entry}")


def get_audit_logs():
    """
    Retrieve all symbolic audit logs.
    """
    return audit_logs


def get_user_audit_logs(user_id: int):
    """
    Retrieve all symbolic audit logs for a specific user.
    """
    return [log for log in audit_logs if log["user_id"] == user_id]
