"""Bridge to candidate collective.

Uses lazy loading to avoid import-time dependency on labs.core.collective.
All attributes from labs.core.collective are dynamically accessible.
"""
from __future__ import annotations
import importlib
from typing import Any


def __getattr__(name: str) -> Any:
    """Lazy-load attributes from labs.core.collective on demand.

    Args:
        name: Attribute name to retrieve

    Returns:
        Requested attribute from labs.core.collective

    Raises:
        ImportError: If labs.core.collective cannot be imported
        AttributeError: If attribute doesn't exist in collective module
    """
    try:
        mod = importlib.import_module("labs.core.collective")
        try:
            return getattr(mod, name)
        except AttributeError as e:
            raise AttributeError(
                f"module 'labs.core.collective' has no attribute {name!r}"
            ) from e
    except ImportError as e:
        raise ImportError(
            f"Cannot import labs.core.collective: {e}. "
            "Ensure labs is installed and available."
        ) from e


def __dir__() -> list[str]:
    """Return available attributes from labs.core.collective.

    Returns:
        List of public attributes, or empty list if module unavailable
    """
    try:
        mod = importlib.import_module("labs.core.collective")
        return [n for n in dir(mod) if not n.startswith("_")]
    except ImportError:
        return []


__all__: list[str] = []  # Populated dynamically via __dir__()
