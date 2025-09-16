"""Session replay management utilities for Lambda ID paired devices."""

from __future__ import annotations

import hashlib
import secrets
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Any


class SessionReplayManager:
    """Manage session replay lifecycles for paired devices."""

    def __init__(self, config: dict[str, Any]):
        self.config = config or {}
        self.active_sessions: dict[str, dict[str, Any]] = {}

    def _session_ttl(self) -> timedelta:
        """Get session time-to-live."""

        ttl_minutes = self.config.get("replay_ttl_minutes", 15)
        return timedelta(minutes=max(1, int(ttl_minutes)))

    def _build_session_id(self, user_id: str, device_pair: tuple[str, str]) -> str:
        """Create deterministic yet unique session identifier."""

        salt = self.config.get("session_salt", "ΛSESSION")
        fingerprint = "|".join(sorted(device_pair))
        payload = f"{user_id}|{fingerprint}|{salt}|{secrets.token_hex(8)}"
        return f"QRSR_{hashlib.sha256(payload.encode()).hexdigest()[:32]}"

    def create_replay_session(self, user_id: str, device_pair: tuple[str, str]) -> dict[str, Any]:
        """Create a new replay session for paired devices."""

        if not user_id:
            raise ValueError("user_id is required for session creation")

        if not device_pair or len(device_pair) != 2:
            raise ValueError("device_pair must contain exactly two device identifiers")

        now = datetime.now(timezone.utc)
        expires_at = now + self._session_ttl()

        session_id = self._build_session_id(user_id, device_pair)
        session_record = {
            "session_id": session_id,
            "user_id": user_id,
            "device_pair": tuple(device_pair),
            "created_at": now.isoformat(),
            "expires_at": expires_at.isoformat(),
            "status": "active",
            "replay_token": secrets.token_urlsafe(24),
        }

        # ΛTAG: session_creation – deterministic trace for replay flows
        self.active_sessions[session_id] = session_record

        return deepcopy(session_record)

    def restore_session(self, session_id: str, target_device: str) -> dict[str, Any]:
        """Restore a session on a target device."""

        session = self.active_sessions.get(session_id)
        if not session:
            raise KeyError("session not found")

        if session["status"] != "active":
            raise RuntimeError("session is no longer active")

        now = datetime.now(timezone.utc)
        if datetime.fromisoformat(session["expires_at"]) <= now:
            session["status"] = "expired"
            raise RuntimeError("session has expired")

        if target_device not in session["device_pair"]:
            raise PermissionError("target device not authorized for replay")

        session["restored_at"] = now.isoformat()
        session.setdefault("restoration_events", []).append(
            {
                "device_id": target_device,
                "timestamp": now.isoformat(),
            }
        )

        # ΛTAG: session_restore – maintain audit friendly copy
        return deepcopy(session)

    def invalidate_session(self, session_id: str) -> dict[str, Any]:
        """Invalidate a replay session."""

        session = self.active_sessions.get(session_id)
        if not session:
            raise KeyError("session not found")

        session["status"] = "invalidated"
        session["invalidated_at"] = datetime.now(timezone.utc).isoformat()

        # ΛTAG: session_invalidate – ensure downstream consumers receive copy
        return deepcopy(session)
