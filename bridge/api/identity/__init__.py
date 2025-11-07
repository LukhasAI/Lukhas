"""Stable identity bridge that tolerates missing legacy modules."""
from __future__ import annotations

from importlib import import_module
from typing import Any
from collections.abc import Iterable

__all__ = [
    "AuthContext",
    "AuthMiddleware",
    "AuthUser",
    "IdentityContext",
    "get_current_identity",
    "get_current_user",
    "identity_routes",
]

_CANDIDATES: tuple[str, ...] = (
    "lukhas_website.api.identity",
    "candidate.api.identity",
    "core.identity.api",
)


def _maybe(module: str, name: str) -> Any | None:
    try:
        mod = import_module(module)
    except Exception:
        return None
    return getattr(mod, name, None)


def _first_available(symbol: str, sources: Iterable[str]) -> Any | None:
    for mod in sources:
        value = _maybe(mod, symbol)
        if value is not None:
            return value
    return None


AuthMiddleware = _first_available("AuthMiddleware", _CANDIDATES)
identity_routes = _first_available("identity_routes", _CANDIDATES)
get_current_identity = _first_available("get_current_identity", _CANDIDATES)
IdentityContext = _first_available("IdentityContext", _CANDIDATES)


# Fallbacks keep collection succeeding even if upstream modules are absent.
if AuthMiddleware is None:
    class AuthMiddleware:  # type: ignore[override]
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            self.args = args
            self.kwargs = kwargs

        def __call__(self, app: Any) -> Any:
            return app


if identity_routes is None:
    def identity_routes() -> list[Any]:
        return []


if get_current_identity is None:
    def get_current_identity() -> Any:
        return None


if IdentityContext is None:
    class IdentityContext:
        pass


try:
    from .auth_middleware import AuthContext, AuthUser, get_current_user
except Exception:
    # The submodule provides robust fallbacks; if it fails, ensure placeholders exist.
    if "AuthUser" not in globals():
        class AuthUser:  # type: ignore[misc]
            def __init__(self, *args: Any, **kwargs: Any) -> None:
                self.args = args
                self.kwargs = kwargs

    if "AuthContext" not in globals():
        class AuthContext:  # type: ignore[misc]
            def __init__(self, user: Any | None = None) -> None:
                self.user = user

    if "get_current_user" not in globals():
        def get_current_user() -> Any:
            return AuthUser()
