"""Bridge package for governance.ethics."""

from __future__ import annotations

import importlib
import os
import pkgutil
from types import ModuleType
__all__: list[str] = []
__path__: list[str] = [os.path.dirname(__file__)]  # type: ignore[assignment]

_BACKEND: ModuleType | None = None
_CANDIDATES = [
    "lukhas_website.governance.ethics",
    "governance.ethics",
    "labs.governance.ethics",
]


def _bind_backend() -> None:
    global _BACKEND, __all__
    for name in _CANDIDATES:
        try:
            backend = importlib.import_module(name)
        except Exception:
            continue
        _BACKEND = backend
        for attr in dir(backend):
            if attr.startswith("_"):
                continue
            value = getattr(backend, attr)
            globals()[attr] = value
            if attr not in __all__:
                __all__.append(attr)
        _export_submodules(backend)
        break


def _export_submodules(package: ModuleType) -> None:
    paths = getattr(package, "__path__", None)
    if not paths:
        return
    for finder, submodule_name, _ in pkgutil.iter_modules(paths):
        full_name = f"{package.__name__}.{submodule_name}"
        try:
            module = importlib.import_module(full_name)
        except Exception:
            continue
        globals()[submodule_name] = module
        if submodule_name not in __all__:
            __all__.append(submodule_name)


_bind_backend()


def __getattr__(name: str):
    if _BACKEND and hasattr(_BACKEND, name):
        value = getattr(_BACKEND, name)
        globals()[name] = value
        if name not in __all__:
            __all__.append(name)
        return value
    for module_name in (
        "lukhas_website.governance.ethics",
        "governance.ethics",
        "labs.governance.ethics",
    ):
        try:
            module = importlib.import_module(module_name)
        except Exception:
            continue
        if hasattr(module, name):
            value = getattr(module, name)
            globals()[name] = value
            if name not in __all__:
                __all__.append(name)
            return value
    raise AttributeError(name)
