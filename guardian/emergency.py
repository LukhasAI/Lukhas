#!/usr/bin/env python3
"""Guardian Emergency Kill-Switch System"""

import logging
import os
import stat
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def _allowed_owner_uids() -> set[int]:
    """Return the set of acceptable owner UIDs for kill-switch artifacts."""

    current_uid = os.getuid()
    uids = {current_uid}
    # Root-owned files are acceptable when running with elevated privileges.
    if current_uid != 0:
        uids.add(0)
    return uids


_ALLOWED_OWNER_UIDS = _allowed_owner_uids()


def _prepare_secure_directory(directory: Path) -> Path:
    """Ensure the directory exists with restrictive permissions."""

    directory = directory.expanduser()
    directory.mkdir(parents=True, exist_ok=True)
    try:
        stat_result = directory.stat()
    except FileNotFoundError as exc:  # pragma: no cover - defensive guard
        raise PermissionError(f"Secure directory {directory} is not accessible") from exc

    if stat_result.st_uid not in _ALLOWED_OWNER_UIDS:
        raise PermissionError(f"Secure directory {directory} is not owned by an allowed user")

    desired_mode = 0o700
    current_mode = stat.S_IMODE(stat_result.st_mode)
    if current_mode != desired_mode:
        directory.chmod(desired_mode)
        current_mode = stat.S_IMODE(directory.stat().st_mode)
        if current_mode != desired_mode:
            raise PermissionError(f"Unable to enforce permissions on {directory}")

    return directory


def _resolve_secure_directory() -> Path:
    """Resolve a secure storage directory for kill-switch artifacts."""

    configured = os.environ.get("GUARDIAN_EMERGENCY_STATE_DIR")
    candidates = []
    if configured:
        candidates.append(Path(configured))
    candidates.extend(
        [
            Path("/var/lib/guardian/emergency"),
            Path("/var/run/guardian/emergency"),
            Path.home() / ".guardian" / "emergency",
        ]
    )

    errors: list[str] = []
    for directory in candidates:
        try:
            return _prepare_secure_directory(directory)
        except PermissionError as exc:
            errors.append(f"{directory}: {exc}")
        except OSError as exc:  # pragma: no cover - defensive guard
            errors.append(f"{directory}: {exc}")

    raise RuntimeError(
        "Unable to initialize a secure directory for Guardian kill-switch state. "
        + "; ".join(errors)
    )


SECURE_STATE_DIR = _resolve_secure_directory()
KILL_SWITCH_FILE = SECURE_STATE_DIR / "guardian_emergency_disable"
KILL_SWITCH_REASON_FILE = SECURE_STATE_DIR / "guardian_emergency_reason.txt"


def _ensure_secure_file(path: Path, *, create: bool = False) -> None:
    """Validate ownership and permissions for a kill-switch file.

    Args:
        path: The file path to validate.
        create: If True, the file will be created if it does not exist.
    """

    try:
        stat_result = path.stat()
    except FileNotFoundError:
        if create:
            flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
            fd = os.open(str(path), flags, 0o600)
            try:
                os.fchmod(fd, 0o600)
            finally:
                os.close(fd)
        return

    if stat_result.st_uid not in _ALLOWED_OWNER_UIDS:
        raise PermissionError(f"Kill-switch file {path} is not owned by an allowed user")

    desired_mode = 0o600
    current_mode = stat.S_IMODE(stat_result.st_mode)
    if current_mode != desired_mode:
        path.chmod(desired_mode)
        current_mode = stat.S_IMODE(path.stat().st_mode)
        if current_mode != desired_mode:
            raise PermissionError(f"Unable to enforce permissions on {path}")


def _write_secure_text(path: Path, content: str) -> None:
    """Write text to a file with restricted permissions."""

    _ensure_secure_file(path)
    with os.fdopen(
        os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600),
        "w",
        encoding="utf-8",
    ) as handle:
        os.fchmod(handle.fileno(), 0o600)
        handle.write(content)


def trigger_kill_switch(reason: str, activated_by: Optional[str] = None) -> dict:
    """Activate the Guardian emergency kill-switch."""
    try:
        timestamp = datetime.now(timezone.utc)
        _ensure_secure_file(KILL_SWITCH_FILE, create=True)
        reason_data = f"""Kill-Switch Activated
Timestamp: {timestamp.isoformat()}
Reason: {reason}
Activated By: {activated_by or 'unknown'}
"""
        _write_secure_text(KILL_SWITCH_REASON_FILE, reason_data)
        logger.critical("GUARDIAN KILL-SWITCH ACTIVATED", extra={"reason": reason})
        return {"success": True, "timestamp": timestamp.isoformat(), "reason": reason, "activated_by": activated_by}
    except Exception as e:
        logger.error(f"Failed to activate kill-switch: {e}")
        return {"success": False, "error": str(e)}


def is_kill_switch_active() -> bool:
    """Check if the Guardian kill-switch is currently active."""
    try:
        _ensure_secure_file(KILL_SWITCH_FILE)
    except PermissionError as exc:
        logger.critical("Kill-switch tampering detected", extra={"error": str(exc)})
        return True
    return KILL_SWITCH_FILE.exists()


def get_kill_switch_reason() -> Optional[dict]:
    """Get the reason and metadata for the current kill-switch activation."""
    if not is_kill_switch_active():
        return None
    try:
        _ensure_secure_file(KILL_SWITCH_REASON_FILE)
        if KILL_SWITCH_REASON_FILE.exists():
            reason_text = KILL_SWITCH_REASON_FILE.read_text(encoding="utf-8")
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
            _ensure_secure_file(KILL_SWITCH_FILE)
            KILL_SWITCH_FILE.unlink()
        if KILL_SWITCH_REASON_FILE.exists():
            _ensure_secure_file(KILL_SWITCH_REASON_FILE)
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
