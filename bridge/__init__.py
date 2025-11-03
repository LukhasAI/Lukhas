"""Bridge package - external service integrations."""

from __future__ import annotations

from collections.abc import Iterable
from importlib import import_module

__all__: list[str] = []

_CANDIDATES: tuple[str, ...] = (
    "lukhas_website.bridge",
    "labs.bridge",
    "candidate.bridge",
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
        if _name in globals():
            continue
        globals()[_name] = getattr(_backend, _name)
        __all__.append(_name)

    backend_path = list(getattr(_backend, "__path__", []))
    search_locations = list(getattr(__spec__, "submodule_search_locations", []) or [])
    for _location in backend_path:
        if _location not in search_locations:
            search_locations.append(_location)
    if search_locations:
        __path__ = search_locations  # type: ignore[assignment]
