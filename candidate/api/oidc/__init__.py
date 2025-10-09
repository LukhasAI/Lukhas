"""Stub candidate.api.oidc module."""

from __future__ import annotations

__all__ = ["get_correlation_id", "router", "security_check_dependency"]


def get_correlation_id() -> str:
    return "corr-candidate"


class _Router:
    def add_api_route(self, *args, **kwargs):
        return None


router = _Router()


def security_check_dependency(*args, **kwargs):
    return True
