"""
Bridge utility helpers for DRY bridge module creation.

Provides safe fallback resolution, explicit exports, and deprecation warnings.
"""
from __future__ import annotations

import warnings
from importlib import import_module
from types import ModuleType
from typing import Callable, Iterable


def resolve_first(paths: Iterable[str]) -> ModuleType:
    """Try importing from candidate paths, return first success."""
    last_err: Exception | None = None
    for p in paths:
        try:
            return import_module(p)
        except Exception as e:  # noqa: BLE001
            last_err = e
    raise ModuleNotFoundError(f"None of {list(paths)} importable") from last_err


def export_from(mod: ModuleType, names: Iterable[str] | None = None) -> dict:
    """Extract exports from module, respecting __all__ or using public attrs."""
    if names is None:
        names = getattr(mod, "__all__", [])
        if not names:
            # fallback to public attrs
            names = [n for n in dir(mod) if not n.startswith("_")]
    return {n: getattr(mod, n) for n in names}


def deprecate(msg: str) -> None:
    """Emit deprecation warning with proper stacklevel."""
    warnings.warn(msg, DeprecationWarning, stacklevel=3)


def bridge(
    candidates: Iterable[str],
    *,
    deprecation: str | None = None,
    names: Iterable[str] | None = None,
    post: Callable[[ModuleType], None] | None = None,
) -> tuple[ModuleType, dict, list[str]]:
    """
    Create a bridge to canonical implementation with fallback resolution.

    Args:
        candidates: Module paths to try in order
        deprecation: Optional deprecation message to emit
        names: Explicit symbol names to export (None = use __all__ or public)
        post: Optional callback to run after module loaded

    Returns:
        (resolved_module, exports_dict, __all__ list)
    """
    if deprecation:
        deprecate(deprecation)
    mod = resolve_first(candidates)
    if post:
        post(mod)
    exports = export_from(mod, names)
    return mod, exports, list(exports.keys())


def bridge_from_candidates(
    *candidates: str,
    deprecated: bool = False,
    stacklevel: int = 3,
) -> tuple[list[str], dict[str, object]]:
    """Import from first available candidate module (ChatGPT explicit-API pattern).

    Uses __import__() with explicit fromlist=["*"] for proper submodule loading.

    Args:
        *candidates: Module paths to try in order (e.g., "candidate.X", "lukhas_website.lukhas.X")
        deprecated: Emit DeprecationWarning if True
        stacklevel: Stack level for warnings (default 3 for caller's caller)

    Returns:
        (__all__, globals_dict) tuple for use in bridge __init__.py

    Example:
        # In lukhas/foo/__init__.py
        from lukhas._bridgeutils import bridge_from_candidates
        _CANDIDATES = ("candidate.foo", "lukhas_website.lukhas.foo")
        __all__, _exports = bridge_from_candidates(*_CANDIDATES)
        globals().update(_exports)
    """
    backend = None
    for path in candidates:
        try:
            backend = __import__(path, fromlist=["*"])
            break
        except (ImportError, ModuleNotFoundError):
            continue

    if backend is None:
        return ([], {})

    if deprecated:
        warnings.warn(
            f"Importing from this location is deprecated. Use the canonical path instead.",
            DeprecationWarning,
            stacklevel=stacklevel,
        )

    __all__ = getattr(backend, "__all__", [n for n in dir(backend) if not n.startswith("_")])
    globals_dict = {name: getattr(backend, name) for name in __all__}

    return (list(__all__), globals_dict)
