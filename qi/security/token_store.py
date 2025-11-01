"""Persistent session token store utilities for QI components."""

from __future__ import annotations

import hashlib
import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from threading import RLock
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)


def _default_clock() -> datetime:
    """Return the current UTC time."""

    return datetime.now(timezone.utc)


def _default_state_dir() -> Path:
    """Return the default directory for persisted state."""

    state_env = os.environ.get("LUKHAS_STATE", os.path.expanduser("~/.lukhas/state"))
    return Path(os.path.expanduser(state_env))


@dataclass(slots=True)
class TokenMetadata:
    """Container representing persisted token information."""

    token_hash: str
    created_at: str
    expires_at: Optional[str]
    metadata: Dict[str, Any]
    last_validated_at: Optional[str] = None


class SessionTokenStore:
    """Simple persistent store for session token metadata."""

    SCHEMA_VERSION = 1

    def __init__(
        self,
        state_dir: Optional[Path | str] = None,
        filename: str = "session_tokens.json",
        clock: Optional[Callable[[], datetime]] = None,
    ) -> None:
        self._clock = clock or _default_clock
        self._lock = RLock()

        directory = Path(state_dir) if state_dir is not None else _default_state_dir()
        self._state_dir = directory.expanduser()
        self._state_dir.mkdir(parents=True, exist_ok=True)

        self._store_path = self._state_dir / filename
        self._tokens: Dict[str, TokenMetadata] = {}

        self._load()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def register_token(
        self,
        token: str,
        metadata: Optional[Dict[str, Any]] = None,
        ttl_seconds: Optional[int] = None,
    ) -> str:
        """Store a session token hash with optional metadata.

        Args:
            token: Raw session token to register.
            metadata: Optional metadata associated with the token.
            ttl_seconds: Optional lifetime for the token in seconds.

        Returns:
            The SHA-256 hash representing the token.
        """

        if not token:
            raise ValueError("Token must be a non-empty string")

        token_hash = self._hash_token(token)

        with self._lock:
            now_dt = self._clock()
            now = now_dt.isoformat()
            expires_at = None
            if ttl_seconds is not None:
                expires_at = (now_dt + timedelta(seconds=ttl_seconds)).isoformat()

            metadata_entry = TokenMetadata(
                token_hash=token_hash,
                created_at=now,
                expires_at=expires_at,
                metadata=dict(metadata or {}),
                last_validated_at=None,
            )

            self._tokens[token_hash] = metadata_entry
            self._save()

        return token_hash

    def validate_token(self, token: str) -> bool:
        """Check whether the provided token exists and is not expired."""

        if not token:
            return False

        token_hash = self._hash_token(token)

        with self._lock:
            self._prune_expired()
            entry = self._tokens.get(token_hash)
            if entry is None:
                return False

            entry.last_validated_at = self._clock().isoformat()
            self._save()
            return True

    def revoke_token(self, token: str) -> bool:
        """Remove a token from the store."""

        if not token:
            return False

        token_hash = self._hash_token(token)

        with self._lock:
            removed = self._tokens.pop(token_hash, None) is not None
            if removed:
                self._save()
            return removed

    def list_tokens(self) -> Dict[str, TokenMetadata]:
        """Return a shallow copy of stored token metadata."""

        with self._lock:
            return dict(self._tokens)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _hash_token(self, token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def _load(self) -> None:
        if not self._store_path.exists():
            return

        try:
            raw = json.loads(self._store_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            logger.error("Failed to parse session token store: %s", exc)
            return
        except OSError as exc:
            logger.error("Unable to read session token store: %s", exc)
            return

        tokens = raw.get("tokens", {})
        if not isinstance(tokens, dict):
            logger.error("Invalid token store format: expected mapping")
            return

        loaded: Dict[str, TokenMetadata] = {}
        for token_hash, info in tokens.items():
            if not isinstance(info, dict):
                continue

            metadata = TokenMetadata(
                token_hash=token_hash,
                created_at=info.get("created_at", self._clock().isoformat()),
                expires_at=info.get("expires_at"),
                metadata=dict(info.get("metadata", {})),
                last_validated_at=info.get("last_validated_at"),
            )
            loaded[token_hash] = metadata

        self._tokens = loaded
        self._prune_expired(save=False)

    def _save(self) -> None:
        payload = {
            "version": self.SCHEMA_VERSION,
            "tokens": {
                token_hash: {
                    "token_hash": meta.token_hash,
                    "created_at": meta.created_at,
                    "expires_at": meta.expires_at,
                    "metadata": meta.metadata,
                    "last_validated_at": meta.last_validated_at,
                }
                for token_hash, meta in self._tokens.items()
            },
        }

        self._state_dir.mkdir(parents=True, exist_ok=True)

        tmp_path = self._store_path.with_suffix(self._store_path.suffix + ".tmp")
        with tmp_path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.flush()
            os.fsync(handle.fileno())

        os.replace(tmp_path, self._store_path)

    def _prune_expired(self, save: bool = True) -> None:
        now = self._clock()
        removed = False

        for token_hash, meta in list(self._tokens.items()):
            if not meta.expires_at:
                continue

            expires_at = self._parse_datetime(meta.expires_at)
            if expires_at is None:
                logger.warning("Invalid expiry timestamp for token %s", token_hash)
                continue

            if now >= expires_at:
                removed = True
                self._tokens.pop(token_hash, None)

        if removed and save:
            self._save()

    def _parse_datetime(self, value: str) -> Optional[datetime]:
        try:
            normalized = value.replace("Z", "+00:00")
            return datetime.fromisoformat(normalized)
        except ValueError:
            return None

