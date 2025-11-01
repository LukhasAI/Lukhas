"""Utilities for bridging canonical implementations across repository lanes."""
from __future__ import annotations

import warnings
from importlib import import_module
from types import ModuleType
from typing import Callable, Iterable, Mapping

__all__ = [
    "bridge",
    "bridge_from_candidates",
    "deprecate",
    "export_from",
    "resolve_first",
    "safe_guard",
]


def resolve_first(paths: Iterable[str]) -> ModuleType:
    """Return the first successfully imported module from *paths*."""

    last_err: Exception | None = None
    for path in paths:
        try:
            return import_module(path)
        except Exception as exc:  # pragma: no cover - passthrough for diagnostics
            last_err = exc
    raise ModuleNotFoundError(f"None of {list(paths)} importable") from last_err


def export_from(mod: ModuleType, names: Iterable[str] | None = None) -> Mapping[str, object]:
    """Build a mapping of exported names for *mod* using ``__all__`` when available."""

    selected = list(names) if names is not None else list(getattr(mod, "__all__", ()))
    if not selected:
        selected = [name for name in dir(mod) if not name.startswith("_")]
    return {name: getattr(mod, name) for name in selected}


def deprecate(name_or_msg: str, msg: str | None = None) -> None:
    """Emit a deprecation warning using a stable stacklevel."""

    if msg is None:
        warnings.warn(name_or_msg, DeprecationWarning, stacklevel=3)
    else:
        warnings.warn(f"{name_or_msg}: {msg}", DeprecationWarning, stacklevel=3)


def safe_guard(name: str, exports: Iterable[str]) -> None:
    """Warn when the resolved backend exposes no public symbols."""

    if not list(exports):
        warnings.warn(f"{name}: No exports found in backend", UserWarning, stacklevel=2)


def bridge(
    candidates: Iterable[str],
    *,
    deprecation: str | None = None,
    names: Iterable[str] | None = None,
    post: Callable[[ModuleType], None] | None = None,
) -> tuple[ModuleType, dict[str, object], list[str]]:
    """Resolve the first importable module from *candidates* and expose selected names."""

    if deprecation:
        deprecate(deprecation)
    module = resolve_first(candidates)
    if post:
        post(module)
    exports = dict(export_from(module, names))
    return module, exports, list(exports.keys())


def bridge_from_candidates(
    *candidates: str,
    deprecated: bool = False,
    stacklevel: int = 3,
) -> tuple[list[str], dict[str, object]]:
    """Return ``(__all__, exports)`` from the first successfully imported backend."""

    backend: ModuleType | None = None
    for path in candidates:
        try:
            backend = __import__(path, fromlist=["*"])
            break
        except (ImportError, ModuleNotFoundError):
            continue

    if backend is None:
        return [], {}

    if deprecated:
        warnings.warn(
            "Importing from this location is deprecated. Use the canonical path instead.",
            DeprecationWarning,
            stacklevel=stacklevel,
        )

    exported = getattr(backend, "__all__", None)
    names = list(exported) if exported else [name for name in dir(backend) if not name.startswith("_")]
    mapping = {name: getattr(backend, name) for name in names}

    return names, mapping
