"""
Core Ethics Bridge - Canonical Public API
Bridge to candidate.core.ethics (single source of truth)

Foundational ethical models, safety constraints, and evaluation mechanisms.
Constellation Framework: ⚛️🧠🛡️

Uses lazy loading to avoid import-time dependencies on labs.
"""
import importlib
from typing import Any


def __getattr__(name: str) -> Any:
    """Lazy-load ethics module from labs.core on attribute access.

    This defers the import of labs.core.ethics until actually needed,
    removing hard dependency at import time.

    Args:
        name: Attribute name to retrieve

    Returns:
        Requested attribute from labs.core.ethics

    Raises:
        AttributeError: If attribute doesn't exist in ethics module
    """
    if name == "ethics":
        try:
            return importlib.import_module("labs.core.ethics")
        except ImportError as e:
            raise ImportError(
                f"Cannot import labs.core.ethics: {e}. "
                "Ensure labs is installed and available."
            ) from e
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    """Return available attributes including lazily-loaded ones."""
    return ["ethics"]


__all__ = ["ethics"]
