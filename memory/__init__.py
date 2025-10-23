"""Bridge: memory (namespace) with preserved submodule search path."""
from __future__ import annotations

import logging
from importlib import import_module
from typing import Iterable

__all__: list[str] = []

_CANDIDATES: tuple[str, ...] = (
    "lukhas_website.memory",
    "labs.memory",
    "memory",
)


logger = logging.getLogger(__name__)


def _public_names(module: object) -> Iterable[str]:
    names = getattr(module, "__all__", None)
    if names:
        return list(names)
    return [name for name in dir(module) if not name.startswith("_")]


_backend = None
for _path in _CANDIDATES:
    try:
        _backend = import_module(_path)
    except Exception:
        continue
    else:
        break

if _backend is not None:
    for _name in _public_names(_backend):
        globals()[_name] = getattr(_backend, _name)
        __all__.append(_name)

    backend_path = list(getattr(_backend, "__path__", []))
    search_locations = list(getattr(__spec__, "submodule_search_locations", []) or [])
    for _location in backend_path:
        if _location not in search_locations:
            search_locations.append(_location)
    try:
        import memory as _root_memory  # pylint: disable=cyclic-import
    except Exception:
        _root_memory = None  # pragma: no cover - missing root package
    if _root_memory is not None:
        for _location in getattr(_root_memory, "__path__", []):
            if _location not in search_locations:
                search_locations.append(_location)
    if search_locations:
        __path__ = search_locations  # type: ignore[assignment]


try:
    from labs.memory import MemoryManager  # type: ignore[attr-defined]
except (ImportError, AttributeError) as exc:
    logger.warning(
        "ΛTRACE_MEMORY_FALLBACK: MemoryManager fallback activated. reason=%s",
        str(exc),
    )

    # ΛTAG: memory_bridge
    # TODO: Replace fallback with integrated MemoryManager once dependency chain is stabilized.
    class MemoryManager:  # type: ignore[empty-body]
        """Minimal stub MemoryManager to maintain import compatibility."""

        def __init__(self, *args, **kwargs) -> None:
            logger.info(
                "ΛTRACE_MEMORY_FALLBACK: Stub MemoryManager initialized args=%s kwargs=%s",
                args,
                kwargs,
            )

else:
    logger.info("ΛTRACE_MEMORY_BRIDGE: Using labs.memory MemoryManager implementation.")


if "MemoryManager" not in __all__:
    __all__.append("MemoryManager")
