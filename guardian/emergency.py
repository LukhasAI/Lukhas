#!/usr/bin/env python3
"""Guardian Emergency Kill-Switch System"""

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

KILL_SWITCH_FILE = Path("/tmp/guardian_emergency_disable")
KILL_SWITCH_REASON_FILE = Path("/tmp/guardian_emergency_reason.txt")


def trigger_kill_switch(reason: str, activated_by: Optional[str] = None) -> dict:
    """Activate the Guardian emergency kill-switch."""
    try:
        timestamp = datetime.now(timezone.utc)
        KILL_SWITCH_FILE.touch()
        reason_data = f"""Kill-Switch Activated
Timestamp: {timestamp.isoformat()}
Reason: {reason}
Activated By: {activated_by or 'unknown'}
"""
        KILL_SWITCH_REASON_FILE.write_text(reason_data)
        logger.critical("GUARDIAN KILL-SWITCH ACTIVATED", extra={"reason": reason})
        return {"success": True, "timestamp": timestamp.isoformat(), "reason": reason, "activated_by": activated_by}
    except Exception as e:
        logger.error(f"Failed to activate kill-switch: {e}")
        return {"success": False, "error": str(e)}


def is_kill_switch_active() -> bool:
    """Check if the Guardian kill-switch is currently active."""
    return KILL_SWITCH_FILE.exists()


def get_kill_switch_reason() -> Optional[dict]:
    """Get the reason and metadata for the current kill-switch activation."""
    if not is_kill_switch_active():
        return None
    try:
        if KILL_SWITCH_REASON_FILE.exists():
            reason_text = KILL_SWITCH_REASON_FILE.read_text()
            lines = reason_text.strip().split('\n')
            data = {}
            for line in lines[1:]:
                if ':' in line:
                    key, value = line.split(':', 1)
                    data[key.strip().lower().replace(' ', '_')] = value.strip()
            return {
                "active": True,
                "reason": data.get("reason", "Unknown"),
                "activated_by": data.get("activated_by", "Unknown"),
                "timestamp": data.get("timestamp", "Unknown"),
            }
        else:
            return {"active": True, "reason": "Kill-switch active but no reason file found"}
    except Exception as e:
        logger.error(f"Failed to read kill-switch reason: {e}")
        return {"active": True, "reason": f"Error reading reason: {e}"}


def clear_kill_switch(cleared_by: Optional[str] = None) -> dict:
    """Clear the Guardian kill-switch and restore normal operations."""
    try:
        timestamp = datetime.now(timezone.utc)
        was_active = is_kill_switch_active()
        if KILL_SWITCH_FILE.exists():
            KILL_SWITCH_FILE.unlink()
        if KILL_SWITCH_REASON_FILE.exists():
            KILL_SWITCH_REASON_FILE.unlink()
        if was_active:
            logger.warning("GUARDIAN KILL-SWITCH CLEARED", extra={"cleared_by": cleared_by})
        return {"success": True, "timestamp": timestamp.isoformat(), "cleared_by": cleared_by, "was_active": was_active}
    except Exception as e:
        logger.error(f"Failed to clear kill-switch: {e}")
        return {"success": False, "error": str(e)}


def get_emergency_status() -> dict:
    """Get the current emergency status of the Guardian system."""
    if is_kill_switch_active():
        reason_info = get_kill_switch_reason()
        return reason_info if reason_info else {"active": True}
    else:
        return {"active": False}
