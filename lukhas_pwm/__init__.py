"""LUKHAS PWM - Pulse Width Modulation System
🎭 LUKHAS Trinity Framework (🎭🌈🎓) integration point

Note:
- The package namespace is transitioning from `lukhas_pwm` to `lukhas`.
- Existing imports continue to work. Prefer `import lukhas...` going forward.
"""

from __future__ import annotations

import importlib
import importlib.abc
import importlib.machinery
import os
import sys
import warnings
from importlib.machinery import PathFinder
from types import ModuleType

if os.environ.get("LUKHAS_SILENCE_IMPORT_NOTICE", "0") not in {"1", "true", "TRUE"}:
    warnings.warn(
        "Namespace notice: `lukhas_pwm` is kept for compatibility; please migrate imports to `lukhas`.",
        DeprecationWarning,
        stacklevel=2,
    )


class _ReverseAliasImportLoader(importlib.abc.Loader):
    """Loader that imports from `lukhas.*` and exposes as `lukhas_pwm.*`."""

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


class _ReverseAliasFinder(importlib.abc.MetaPathFinder):
    """Maps `lukhas_pwm.*` -> `lukhas.*` if the original module is missing and the target exists.

    This enables legacy imports to keep working after the codebase is migrated to the
    `lukhas` package. If `lukhas_pwm.*` exists, we return None to allow normal loading.
    """

    _SRC_PREFIX = "lukhas_pwm"
    _DST_PREFIX = "lukhas"

    def find_spec(self, fullname: str, path=None, target=None):  # type: ignore[override]
        # Only handle submodules under lukhas_pwm.*
        if not fullname.startswith(self._SRC_PREFIX + "."):
            return None

        # If the real module still exists (pre-rename), let default importers load it
        if PathFinder.find_spec(fullname, path) is not None:
            return None

        # Otherwise, try mapping to lukhas.*
        suffix = fullname[len(self._SRC_PREFIX) :]
        target_name = self._DST_PREFIX + suffix
        target_spec = PathFinder.find_spec(target_name, path)
        if target_spec is None:
            return None
        is_pkg = target_spec.submodule_search_locations is not None
        return importlib.machinery.ModuleSpec(
            name=fullname,
            loader=_ReverseAliasImportLoader(target_name),
            is_package=is_pkg,
        )


# Install reverse finder (first to take effect only when original modules are absent)
if not any(isinstance(f, _ReverseAliasFinder) for f in sys.meta_path):
    sys.meta_path.insert(0, _ReverseAliasFinder())
