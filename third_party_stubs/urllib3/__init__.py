"""Stub urllib3 package for testing environment."""
from . import exceptions


def disable_warnings(category: type[Warning] | None = None) -> None:
    """Stub disable_warnings to satisfy test harness."""


__all__ = ["exceptions", "disable_warnings"]
