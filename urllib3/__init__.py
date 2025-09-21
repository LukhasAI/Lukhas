"""Minimal urllib3 stub for offline pytest warning filters."""

from . import exceptions  # noqa: F401


def disable_warnings(_: type[Warning] | None = None) -> None:  # pragma: no cover
    """Stubbed disable_warnings function."""
    return None
