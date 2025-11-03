"""Bridge: memory (namespace) with preserved submodule search path."""
from __future__ import annotations

from importlib import import_module
from collections.abc import Iterable
from pathlib import Path

__all__: list[str] = []

_CANDIDATES: tuple[str, ...] = (
    "lukhas_website.memory",
    "labs.memory",
    "memory",
)


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
    current_dir = Path(__file__).resolve().parent
    for extra in (current_dir, current_dir / "backends"):
        extra_str = str(extra)
        if extra_str not in search_locations:
            search_locations.append(extra_str)
    if search_locations:
        __path__ = search_locations  # type: ignore[assignment]
