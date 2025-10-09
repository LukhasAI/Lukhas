"""Bridge module for lukhas.api.oidc."""

from __future__ import annotations

try:
    from api.oidc import (  # type: ignore[attr-defined]
        get_correlation_id as _get_correlation_id,
        router as _router,
        security_check_dependency as _security_check_dependency,
    )
except Exception:
    def _get_correlation_id() -> str:
        return "corr-stub"

    class _Router:
        def add_api_route(self, *args, **kwargs):
            return None

    def _security_check_dependency(*args, **kwargs):
        return True

    _router = _Router()
    _security_check_dependency.__name__ = "security_check_dependency"


def get_correlation_id() -> str:  # type: ignore[misc]
    return _get_correlation_id()


def security_check_dependency(*args, **kwargs):  # type: ignore[misc]
    return _security_check_dependency(*args, **kwargs)


router = _router


__all__ = ["get_correlation_id", "router", "security_check_dependency"]
