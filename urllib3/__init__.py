"""Minimal urllib3 stub for offline pytest warning filters."""

from typing import Optional, Type

from . import exceptions  # noqa: F401


def disable_warnings(_: Optional[Type[Warning]] = None) -> None:  # pragma: no cover
    """Stubbed disable_warnings function."""
    return None
