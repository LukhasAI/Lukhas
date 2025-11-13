"""API key registry cache for the REST middleware."""
from __future__ import annotations

import hashlib
import json
import logging
import os
import threading
import time
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any

try:  # pragma: no cover - structlog is optional in some test environments
    import structlog
except ImportError:  # pragma: no cover
    structlog = SimpleNamespace(get_logger=lambda name=None: logging.getLogger(name or __name__))

logger = structlog.get_logger(__name__)

# Environment variables that control registry loading
_REGISTRY_PATH_ENV = "LUKHAS_API_KEY_REGISTRY_PATH"
_REGISTRY_PAYLOAD_ENV = "LUKHAS_API_KEY_REGISTRY"
_HASH_FALLBACK_ENV = "LUKHAS_API_KEY_HASHES"
_REFRESH_ENV = "LUKHAS_API_KEY_REFRESH_SECONDS"


@dataclass
class ApiKeyMetadata:
    """Metadata describing a provisioned API key."""

    key_hash: str
    user_id: str
    tier: int = 1
    scopes: tuple[str, ...] = ()
    expires_at: datetime | None = None
    revoked: bool = False
    attributes: dict[str, Any] = field(default_factory=dict)

    # ΛTAG: auth_cache - ensure tier decisions remain deterministic.
    def is_expired(self, reference: datetime | None = None) -> bool:
        """Return ``True`` when the key is past its expiry window."""

        if not self.expires_at:
            return False

        reference_dt = reference or datetime.now(timezone.utc)
        return self.expires_at <= reference_dt

    def is_active(self, reference: datetime | None = None) -> bool:
        """Return ``True`` when the key is neither revoked nor expired."""

        if self.revoked:
            return False
        return not self.is_expired(reference=reference)


class ApiKeyCache:
    """In-memory cache for API key metadata loaded from configuration."""

    def __init__(
        self,
        registry_path: str | None = None,
        refresh_interval: int | None = None,
    ) -> None:
        self._registry_path = Path(registry_path) if registry_path else None
        env_refresh = int(os.getenv(_REFRESH_ENV, "60"))
        self._refresh_interval = refresh_interval if refresh_interval is not None else env_refresh
        self._cache: dict[str, ApiKeyMetadata] = {}
        self._configured = False
        self._last_loaded = 0.0
        self._lock = threading.RLock()

    def lookup(self, api_key: str) -> ApiKeyMetadata | None:
        """Lookup API key metadata using a constant-time hash."""

        key_hash = hashlib.sha256(api_key.encode("utf-8")).hexdigest()
        with self._lock:
            self._ensure_cache_loaded()
            metadata = self._cache.get(key_hash)

        if metadata and metadata.is_active():
            logger.debug(
                "api_key_cache_hit",
                key_hash=key_hash[:12],
                tier=metadata.tier,
                scopes=list(metadata.scopes),
            )
            return metadata

        if metadata and not metadata.is_active():
            logger.debug(
                "api_key_cache_inactive",
                key_hash=key_hash[:12],
                revoked=metadata.revoked,
                expires_at=metadata.expires_at.isoformat() if metadata.expires_at else None,
            )
            return metadata

        logger.debug("api_key_cache_miss", key_hash=key_hash[:12])
        return None

    def invalidate(self) -> None:
        """Force the cache to reload on the next lookup."""

        with self._lock:
            self._last_loaded = 0.0

    def is_configured(self) -> bool:
        """Return ``True`` when a registry source is configured."""

        with self._lock:
            self._ensure_cache_loaded()
            return self._configured

    # ΛTAG: auth_cache - deterministic reload behaviour for tier enforcement.
    def _ensure_cache_loaded(self) -> None:
        now = time.time()
        if self._cache and now - self._last_loaded < max(self._refresh_interval, 0):
            return

        self._cache, self._configured = self._load_registry()
        self._last_loaded = now

    def _load_registry(self) -> tuple[dict[str, ApiKeyMetadata], bool]:
        cache: dict[str, ApiKeyMetadata] = {}
        configured = False

        # Load from JSON file path when provided.
        registry_path = self._registry_path or self._get_env_path()
        if registry_path:
            configured = True
            try:
                payload = json.loads(Path(registry_path).read_text(encoding="utf-8"))
                cache.update(self._parse_registry(payload, source="file"))
            except FileNotFoundError:
                logger.warning("api_key_registry_missing", path=str(registry_path))
            except json.JSONDecodeError:
                logger.error("api_key_registry_invalid_json", path=str(registry_path))

        # Load from JSON payload stored in environment.
        registry_payload = os.getenv(_REGISTRY_PAYLOAD_ENV)
        if registry_payload:
            configured = True
            try:
                payload = json.loads(registry_payload)
                cache.update(self._parse_registry(payload, source="env"))
            except json.JSONDecodeError:
                logger.error("api_key_registry_env_invalid_json")

        # Fallback: hashed API keys via validators configuration.
        hash_payload = os.getenv(_HASH_FALLBACK_ENV)
        if hash_payload:
            configured = True
            for hash_str in hash_payload.split(","):
                hash_value = hash_str.strip().lower()
                if hash_value:
                    cache.setdefault(
                        hash_value,
                        ApiKeyMetadata(
                            key_hash=hash_value,
                            user_id="env_api_user",
                            tier=1,
                            scopes=(),
                            attributes={"source": "env_hash"},
                        ),
                    )

        return cache, configured

    def _parse_registry(self, payload: Any, source: str) -> dict[str, ApiKeyMetadata]:
        records: dict[str, ApiKeyMetadata] = {}
        if not isinstance(payload, dict):
            logger.warning("api_key_registry_unexpected_payload", source=source)
            return records

        entries = payload.get("api_keys")
        if not isinstance(entries, Iterable):
            logger.warning("api_key_registry_missing_entries", source=source)
            return records

        for raw_entry in entries:
            if not isinstance(raw_entry, dict):
                continue

            metadata = self._build_metadata(raw_entry, source=source)
            if metadata:
                records[metadata.key_hash] = metadata

        return records

    def _build_metadata(self, entry: dict[str, Any], *, source: str) -> ApiKeyMetadata | None:
        raw_hash = entry.get("hash")
        raw_key = entry.get("key")

        if raw_hash:
            key_hash = str(raw_hash).strip().lower()
        elif raw_key:
            key_hash = hashlib.sha256(str(raw_key).encode("utf-8")).hexdigest()
        else:
            logger.warning("api_key_registry_entry_missing_identifier", source=source)
            return None

        user_id = str(entry.get("user_id", f"api_user_{key_hash[:8]}"))
        tier = int(entry.get("tier", 1))
        scopes = tuple(entry.get("scopes", ()))
        revoked = bool(entry.get("revoked", False))
        expires_at = self._parse_expiry(entry.get("expires_at"))

        attributes = {
            "source": source,
            **{k: v for k, v in entry.items() if k not in {"hash", "key", "user_id", "tier", "scopes", "revoked", "expires_at"}},
        }

        return ApiKeyMetadata(
            key_hash=key_hash,
            user_id=user_id,
            tier=tier,
            scopes=scopes,
            revoked=revoked,
            expires_at=expires_at,
            attributes=attributes,
        )

    def _parse_expiry(self, value: Any) -> datetime | None:
        if value in (None, ""):
            return None

        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(float(value), tz=timezone.utc)

        if isinstance(value, str):
            try:
                parsed = datetime.fromisoformat(value)
            except ValueError:
                logger.warning("api_key_registry_invalid_expiry", value=value)
                return None

            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed.astimezone(timezone.utc)

        logger.warning("api_key_registry_unsupported_expiry", type=type(value).__name__)
        return None

    def _get_env_path(self) -> Path | None:
        path_value = os.getenv(_REGISTRY_PATH_ENV)
        if not path_value:
            return None
        return Path(path_value)


# Shared cache instance for application usage
api_key_cache = ApiKeyCache()

__all__ = ["ApiKeyCache", "ApiKeyMetadata", "api_key_cache"]
