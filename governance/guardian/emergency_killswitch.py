"""
Guardian Emergency Kill-Switch
==============================

Critical safety mechanism for immediately disabling Guardian enforcement.

## Purpose
Provides an emergency override for the Guardian system that can be activated
without code changes, API calls, or system restarts. Used for:
- Production incidents where Guardian blocks critical operations
- Testing and debugging Guardian behavior
- Emergency maintenance windows
- Recovery from Guardian misconfiguration

## Usage

### Activate Kill-Switch
```bash
# Create the kill-switch file
touch /tmp/guardian_emergency_disable
echo "Incident #123: Emergency release deployment" > /tmp/guardian_emergency_disable
```

### Deactivate Kill-Switch
```bash
# Remove the kill-switch file
rm /tmp/guardian_emergency_disable
```

### Check Status
```python
from governance.guardian.emergency_killswitch import is_emergency_killswitch_active

if is_emergency_killswitch_active():
    print("⚠️ Guardian is DISABLED by emergency kill-switch")
```

## Security Considerations
- Kill-switch file path is hardcoded to prevent accidental activation
- All kill-switch activations are logged with timestamp
- File contents are logged for audit trail
- Recommended: Monitor kill-switch status in production alerting

## Monitoring
Set up alerts for:
```bash
# Alert if kill-switch is active for > 5 minutes
test -f /tmp/guardian_emergency_disable && \
  find /tmp/guardian_emergency_disable -mmin +5 && \
  echo "⚠️ Guardian kill-switch active for extended period"
```
"""

from __future__ import annotations

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

# Kill-switch file path - DO NOT CHANGE without updating runbooks
KILLSWITCH_PATH = "/tmp/guardian_emergency_disable"

logger = logging.getLogger(__name__)


def is_emergency_killswitch_active() -> bool:
    """
    Check if the Guardian emergency kill-switch is currently active.

    Returns:
        bool: True if kill-switch file exists, False otherwise

    Example:
        >>> if is_emergency_killswitch_active():
        ...     print("Guardian is disabled!")
    """
    killswitch_exists = os.path.exists(KILLSWITCH_PATH)

    if killswitch_exists:
        # Log every check to create audit trail
        reason = read_killswitch_reason()
        logger.warning(
            "⚠️ Guardian emergency kill-switch is ACTIVE",
            extra={
                "killswitch_path": KILLSWITCH_PATH,
                "reason": reason,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    return killswitch_exists


def read_killswitch_reason() -> str | None:
    """
    Read the reason for kill-switch activation from the file contents.

    Returns:
        Optional[str]: File contents (reason for activation) or None if empty

    Example:
        >>> reason = read_killswitch_reason()
        >>> if reason:
        ...     print(f"Kill-switch reason: {reason}")
    """
    try:
        if os.path.exists(KILLSWITCH_PATH):
            with open(KILLSWITCH_PATH) as f:
                contents = f.read().strip()
                return contents if contents else None
    except Exception as e:
        logger.error(f"Failed to read kill-switch reason: {e}")
    return None


def activate_killswitch(reason: str = "Emergency Guardian disable") -> bool:
    """
    Programmatically activate the Guardian emergency kill-switch.

    ⚠️ WARNING: This disables all Guardian safety checks!

    Args:
        reason: Reason for activation (logged for audit trail)

    Returns:
        bool: True if successfully activated

    Example:
        >>> activate_killswitch("Incident #123: Production deployment blocked")
        True
    """
    try:
        Path(KILLSWITCH_PATH).write_text(f"{reason}\nActivated: {datetime.utcnow().isoformat()}\n")
        logger.critical(
            "🚨 Guardian emergency kill-switch ACTIVATED",
            extra={
                "killswitch_path": KILLSWITCH_PATH,
                "reason": reason,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )
        return True
    except Exception as e:
        logger.error(f"Failed to activate kill-switch: {e}")
        return False


def deactivate_killswitch() -> bool:
    """
    Programmatically deactivate the Guardian emergency kill-switch.

    Returns:
        bool: True if successfully deactivated or already inactive

    Example:
        >>> deactivate_killswitch()
        True
    """
    try:
        if os.path.exists(KILLSWITCH_PATH):
            reason = read_killswitch_reason()
            os.remove(KILLSWITCH_PATH)
            logger.info(
                "✅ Guardian emergency kill-switch DEACTIVATED",
                extra={
                    "killswitch_path": KILLSWITCH_PATH,
                    "previous_reason": reason,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )
        return True
    except Exception as e:
        logger.error(f"Failed to deactivate kill-switch: {e}")
        return False


def get_killswitch_status() -> dict[str, any]:
    """
    Get comprehensive kill-switch status information.

    Returns:
        dict: Kill-switch status including active state, reason, and metadata

    Example:
        >>> status = get_killswitch_status()
        >>> print(f"Active: {status['active']}")
        >>> if status['active']:
        ...     print(f"Reason: {status['reason']}")
    """
    active = is_emergency_killswitch_active()
    status = {
        "active": active,
        "killswitch_path": KILLSWITCH_PATH,
        "timestamp": datetime.utcnow().isoformat(),
    }

    if active:
        status["reason"] = read_killswitch_reason()
        try:
            stat = os.stat(KILLSWITCH_PATH)
            status["activated_at"] = datetime.fromtimestamp(stat.st_ctime).isoformat()
            status["modified_at"] = datetime.fromtimestamp(stat.st_mtime).isoformat()
        except Exception as e:
            logger.error(f"Failed to read kill-switch file metadata: {e}")

    return status
