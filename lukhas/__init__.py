"""
Lukhas compatibility shim.

Conditionally map missing `lukhas.*` submodules to their legacy counterparts
under `lukhas_pwm.*`. If a real `lukhas.*` module exists, it is always
preferred and loaded normally.

Safe to remove once the codebase fully resides under `lukhas/`.
"""

from __future__ import annotations

import importlib
import importlib.abc
import importlib.machinery
import importlib.util
from importlib.machinery import PathFinder
import sys
from types import ModuleType

_ALIASED_PREFIX = "lukhas"
_TARGET_PREFIX = "lukhas_pwm"


class _AliasImportLoader(importlib.abc.Loader):
    def __init__(self, target_name: str) -> None:
        self._target_name = target_name

    def create_module(self, spec):  # type: ignore[override]
        return None

    def exec_module(self, module: ModuleType) -> None:  # type: ignore[override]
        real = importlib.import_module(self._target_name)
        sys.modules[module.__name__] = real
        if getattr(real, "__path__", None) is not None:
            module.__path__ = real.__path__  # type: ignore[attr-defined]
        module.__package__ = module.__name__


class _AliasFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname: str, path=None, target=None):  # type: ignore[override]
        # Only handle submodules under lukhas.*
        if not fullname.startswith(_ALIASED_PREFIX + "."):
            return None
    # If the real `lukhas.*` exists, do nothing
    if PathFinder.find_spec(fullname, path) is not None:
            return None
        # Map to legacy `lukhas_pwm.*` if available
        suffix = fullname[len(_ALIASED_PREFIX) :]
        target_name = _TARGET_PREFIX + suffix
        target_spec = importlib.util.find_spec(target_name)
        if target_spec is None:
            return None
        is_pkg = target_spec.submodule_search_locations is not None
        return importlib.machinery.ModuleSpec(
            name=fullname,
            loader=_AliasImportLoader(target_name),
            is_package=is_pkg,
        )


# Install finder once when `lukhas` is imported
if not any(isinstance(f, _AliasFinder) for f in sys.meta_path):
    sys.meta_path.insert(0, _AliasFinder())
