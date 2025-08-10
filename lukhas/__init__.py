"""
Lukhas package alias.

This package provides a drop-in import alias for the existing
`lukhas_pwm` package so code can import `lukhas` without refactors:

    from lukhas.branding.terminology import normalize_output

Internally, it maps submodule imports to `lukhas_pwm.*` on demand.
Safe to remove once the codebase is fully migrated.
"""
from __future__ import annotations

import importlib
import importlib.abc
import importlib.machinery
import importlib.util
import sys
from types import ModuleType

_ALIASED_PREFIX = "lukhas"
_TARGET_PREFIX = "lukhas_pwm"


class _AliasRootLoader(importlib.abc.Loader):
    def create_module(self, spec):  # type: ignore[override]
        # Use default module creation
        return None

    def exec_module(self, module: ModuleType) -> None:  # type: ignore[override]
        # Mark as a package to allow submodule imports
        if not hasattr(module, "__path__"):
            module.__path__ = []  # type: ignore[attr-defined]
        module.__package__ = _ALIASED_PREFIX


class _AliasImportLoader(importlib.abc.Loader):
    def __init__(self, target_name: str) -> None:
        self._target_name = target_name

    def create_module(self, spec):  # type: ignore[override]
        # Defer to default
        return None

    def exec_module(self, module: ModuleType) -> None:  # type: ignore[override]
        # Import the real target and alias it in sys.modules
        real = importlib.import_module(self._target_name)
        # Copy reference so subsequent imports see the same module
        sys.modules[module.__name__] = real
        # Ensure package-ness matches target for subpackages
        if getattr(real, "__path__", None) is not None:
            module.__path__ = real.__path__  # type: ignore[attr-defined]
        module.__package__ = module.__name__


class _AliasFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname: str, path=None, target=None):  # type: ignore[override]
        # Root package: return a package spec
        if fullname == _ALIASED_PREFIX:
            return importlib.machinery.ModuleSpec(
                name=_ALIASED_PREFIX,
                loader=_AliasRootLoader(),
                is_package=True,
            )
        # Submodules: map `lukhas.*` -> `lukhas_pwm.*`
        if fullname.startswith(_ALIASED_PREFIX + "."):
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
        return None


# Install finder once when `lukhas` is imported
if not any(isinstance(f, _AliasFinder) for f in sys.meta_path):
    sys.meta_path.insert(0, _AliasFinder())
