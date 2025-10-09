"""Stub OIDC module for API tests."""

from __future__ import annotations

__all__ = ["get_correlation_id", "router", "security_check_dependency"]
__path__ = []  # allow namespace-like behaviour


def get_correlation_id() -> str:
    return "corr-api"


class _Router:
    def add_api_route(self, *args, **kwargs):
        return None


router = _Router()


def security_check_dependency(*args, **kwargs):
    return True
