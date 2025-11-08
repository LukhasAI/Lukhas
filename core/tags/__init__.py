# TODO: migrate to ProviderRegistry
"""
Lazy proxy for LUKHAS Tag System from labs.core.tags

This is an interim safety pattern that provides lazy loading of tag system
components from labs.core.tags without importing them at module import time.
"""
import importlib
from typing import Any, List


def __getattr__(name: str) -> Any:
    """Lazy-load the tag system implementation on demand."""
    try:
        _mod = importlib.import_module("labs.core.tags")
    except Exception:
        raise AttributeError(f"module 'core.tags' has no attribute {name}")  # TODO[T4-ISSUE]: {"code": "B904", "ticket": "GH-1031", "owner": "consciousness-team", "status": "planned", "reason": "Exception re-raise pattern - needs review for proper chaining (raise...from)", "estimate": "15m", "priority": "medium", "dependencies": "none", "id": "core_tags___init___py_L17"}
    return getattr(_mod, name)


def __dir__() -> list[str]:
    """Provide directory listing that includes lazily-loaded tag system exports."""
    try:
        _mod = importlib.import_module("labs.core.tags")
        mod_names = [n for n in dir(_mod) if not n.startswith("_")]
    except Exception:
        mod_names = []
    return list(globals().keys()) + mod_names
