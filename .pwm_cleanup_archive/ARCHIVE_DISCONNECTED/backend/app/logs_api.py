"""
╭──────────────────────────────────────────────────────────────╮
│ MODULE      : logs_api.py                                    │
│ DESCRIPTION : Symbolic session and audit log retrieval       │
│ TYPE        : Logs Access API                                │
│ AUTHOR      : Lukhas Systems                                  │
│ UPDATED     : 2025-04-29                                     │
╰──────────────────────────────────────────────────────────────╯
"""

from datetime import datetime

from fastapi import APIRouter, HTTPException

router = APIRouter()

# ── Simulated In-Memory Logs (to replace with real DB queries) ──

session_logs = [
    {"user_id": 1, "action": "LOGIN", "timestamp": str(datetime.utcnow())},
    {"user_id": 1, "action": "UPLOAD_VAULT", "timestamp": str(datetime.utcnow())},
    {"user_id": 2, "action": "DOWNLOAD_VAULT", "timestamp": str(datetime.utcnow())},
]


@router.get("/logs/sessions")
def get_all_session_logs():
    """
    Retrieve all symbolic session logs.
    """
    return session_logs


@router.get("/logs/sessions/{user_id}")
def get_user_session_logs(user_id: int):
    """
    Retrieve symbolic session logs for a specific LucasID user.
    """
    filtered_logs = [log for log in session_logs if log["user_id"] == user_id]
    if not filtered_logs:
        raise HTTPException(status_code=404, detail="No logs found for this user.")
    return filtered_logs
