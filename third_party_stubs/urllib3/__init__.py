"""Stub urllib3 package for testing environment."""
from . import exceptions

__version__ = "0.0-stub"


def disable_warnings(category: type[Warning] | None = None) -> None:
    """Stub disable_warnings to satisfy test harness."""


__all__ = ["exceptions", "disable_warnings", "__version__"]
