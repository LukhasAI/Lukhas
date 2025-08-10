"""
╭──────────────────────────────────────────────────────────────╮
│ MODULE      : logs.py                                        │
│ DESCRIPTION : Combined log utilities and live feed API       │
│ TYPE        : Log Access + Dashboard Hook                    │
│ AUTHOR      : Lukhas Systems                                  │
│ UPDATED     : 2025-04-29                                     │
╰──────────────────────────────────────────────────────────────╯
"""

from backend.app.audit_logger import get_audit_logs
from backend.app.email_logs import get_all_email_logs
from backend.app.logs_api import get_all_session_logs
from fastapi import APIRouter

router = APIRouter()


@router.get("/logs/live")
def get_all_logs_combined():
    """
    Return all symbolic logs combined for live dashboard view.
    """
    return {
        "sessions": get_all_session_logs(),
        "audit": get_audit_logs(),
        "emails": get_all_email_logs(),
    }
