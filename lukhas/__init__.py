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
    def __init__(self, alias_name: str, target_name: str) -> None:
        self._alias_name = alias_name
        self._target_name = target_name

    def create_module(self, spec):  # type: ignore[override]
        # Import the real target and ensure both alias and target map to the same object
        target_mod = importlib.import_module(self._target_name)
        sys.modules[self._target_name] = target_mod
        sys.modules[self._alias_name] = target_mod
        return target_mod

    def exec_module(self, module: ModuleType) -> None:  # type: ignore[override]
        # Nothing to do; module already initialized by target import in create_module
        return None


class _AliasFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname: str, path=None, target=None):  # type: ignore[override]
        # Only handle submodules under lukhas.* (not the top-level package itself)
        if not fullname.startswith(_ALIASED_PREFIX + "."):
            return None
        # If a spec exists, check if it's actually resolving via lukhas_pwm paths.
        # If it's a true lukhas module (not under lukhas_pwm), prefer it; otherwise coalesce to target.
        native_spec = PathFinder.find_spec(fullname, path)
        if native_spec is not None:
            origin = getattr(native_spec, "origin", None)
            search_locs = getattr(native_spec, "submodule_search_locations", None)

            def _is_under_pwm(p: str) -> bool:
                return p is not None and (
                    "/lukhas_pwm/" in p
                    or p.endswith("/lukhas_pwm")
                    or p.replace("\\", "/").rstrip("/").endswith("/lukhas_pwm")
                )

            under_pwm = False
            if origin and _is_under_pwm(str(origin)):
                under_pwm = True
            if not under_pwm and search_locs:
                for loc in search_locs:
                    if _is_under_pwm(str(loc)):
                        under_pwm = True
                        break
            if not under_pwm:
                # Real lukhas module exists; don't alias
                return None
        # Otherwise, try mapping to lukhas_pwm.*
        suffix = fullname[len(_ALIASED_PREFIX) :]
        target_name = _TARGET_PREFIX + suffix
        # Use util.find_spec for the legacy target to allow nested discovery
        target_spec = importlib.util.find_spec(target_name)
        if target_spec is None:
            return None
        is_pkg = target_spec.submodule_search_locations is not None
        return importlib.machinery.ModuleSpec(
            name=fullname,
            loader=_AliasImportLoader(alias_name=fullname, target_name=target_name),
            is_package=is_pkg,
        )


# Install finder once when `lukhas` is imported
if not any(isinstance(f, _AliasFinder) for f in sys.meta_path):
    sys.meta_path.insert(0, _AliasFinder())
