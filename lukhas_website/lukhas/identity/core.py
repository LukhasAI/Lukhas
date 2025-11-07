"""Centralized IdentitySystem implementation for performance tests."""

from __future__ import annotations

import logging
import os
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict

from core.common.config import get_config, get_setting

logger = logging.getLogger(__name__)


@dataclass
class IdentityUser:
    """In-memory representation of a registered identity user."""

    username: str
    email: str
    password: str
    user_id: str
    registered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_authenticated_at: datetime | None = None
    last_token: str | None = None


# ΛTAG:identity_auth
class IdentitySystem:
    """Lightweight identity system backed by centralized configuration.

    The implementation focuses on deterministic behaviour for the test suite
    while honouring the centralized configuration loader used across LUKHAS.
    """

    def __init__(
        self,
        database_url: str | None = None,
        jwt_secret: str | None = None,
        config_override: dict[str, Any] | None = None,
    ) -> None:
        self._config = self._load_configuration(config_override)
        self.database_url = database_url or self._config.get("database_url", "sqlite:///:memory:")
        self.jwt_secret = jwt_secret or self._config.get("jwt_secret", os.getenv("JWT_SECRET", "test-secret"))

        self._users: dict[str, IdentityUser] = {}
        self._metrics = {"registrations": 0, "authentications": 0, "failures": 0}

        logger.info("IdentitySystem initialized with database=%s", self.database_url)

    def _load_configuration(self, override: dict[str, Any] | None) -> dict[str, Any]:
        """Load module configuration using the shared config loader."""

        configuration: dict[str, Any] = {}
        try:
            module_config = get_config("identity")
            configuration.update(module_config.settings)
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.debug("Identity configuration unavailable: %s", exc)

        configuration.setdefault("database_url", get_setting("identity.database_url", "sqlite:///:memory:"))
        configuration.setdefault("jwt_secret", get_setting("identity.jwt_secret", os.getenv("JWT_SECRET", "test-secret")))

        if override:
            configuration.update(override)

        return configuration

    async def register_user(self, profile: dict[str, Any]) -> dict[str, Any]:
        """Register or update a user profile."""

        username = profile.get("username")
        password = profile.get("password")
        if not username or not password:
            self._metrics["failures"] += 1
            return {"success": False, "error": "invalid_profile"}

        email = profile.get("email", f"{username}@example.com")
        user = self._users.get(username)
        if user is None:
            user = IdentityUser(username=username, email=email, password=password, user_id=username)
            self._users[username] = user
            logger.debug("Registered new identity user %s", username)
        else:
            user.email = email
            user.password = password
            logger.debug("Updated identity profile for %s", username)

        self._metrics["registrations"] += 1
        return {
            "success": True,
            "user_id": user.user_id,
            "registered_at": user.registered_at,
        }

    async def authenticate_user(self, credentials: dict[str, Any]) -> dict[str, Any]:
        """Authenticate a user using stored credentials."""

        username = credentials.get("username")
        password = credentials.get("password")
        user = self._users.get(username or "")

        if not user or user.password != password:
            self._metrics["failures"] += 1
            return {"success": False, "error": "invalid_credentials"}

        token = secrets.token_hex(16)
        user.last_authenticated_at = datetime.now(timezone.utc)
        user.last_token = token
        self._metrics["authentications"] += 1

        return {
            "success": True,
            "user_id": user.user_id,
            "token": token,
            "authenticated_at": user.last_authenticated_at,
        }

    def get_metrics(self) -> dict[str, int]:
        """Expose registration/authentication counters for diagnostics."""

        return dict(self._metrics)

    def get_registered_users(self) -> dict[str, IdentityUser]:
        """Return a copy of registered user data for inspection."""

        return dict(self._users)
