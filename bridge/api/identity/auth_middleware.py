"""Identity auth middleware shim for Oneiric Core API tests."""
from __future__ import annotations

from importlib import import_module
from typing import Any

__all__ = ["AuthContext", "AuthUser", "get_current_user"]

_MODULES = (
    "lukhas_website.api.identity.auth_middleware",
    "candidate.api.identity.auth_middleware",
    "bridge.api.identity",
)


def _find(name: str) -> Any | None:
    for module in _MODULES:
        try:
            mod = import_module(module)
        except Exception:
            continue
        value = getattr(mod, name, None)
        if value is not None:
            return value
    return None


AuthUser = _find("AuthUser")
AuthContext = _find("AuthContext")
get_current_user = _find("get_current_user")


if AuthUser is None:
    class AuthUser:  # type: ignore[misc]
        def __init__(self, id: str = "test-user", tier: str = "experimental", lukhas_id: str | None = None) -> None:
            self.id = id
            self.tier = tier
            self.lukhas_id = lukhas_id or "lukhas-test-id"


if AuthContext is None:
    class AuthContext:  # type: ignore[misc]
        def __init__(self, user: AuthUser | None = None) -> None:
            self.user = user or AuthUser()


if get_current_user is None:
    def get_current_user() -> AuthUser:
        return AuthUser()
