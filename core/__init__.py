"""Compatibility shim exposing `lukhas.core` under legacy `core`.
Supports:
 - `import core.trace` / `from core.trace import X`
 - `from core import trace`
Fail-closed, no optional deps at import time.
"""
from __future__ import annotations
import sys, types, importlib
import importlib.util, importlib.machinery, importlib.abc

_TARGET = "lukhas.core"
_THIS = __name__  # "core"

def _install_aliases() -> None:
    """Map base package and preload common submodules used by tests."""
    target_pkg = importlib.import_module(_TARGET)
    # Alias base package
    sys.modules.setdefault(_THIS, sys.modules[_TARGET])
    m = sys.modules[_THIS]
    m.__package__ = _THIS
    m.__path__ = getattr(sys.modules[_TARGET], "__path__", [])
    # Preload frequent submodules so `import core.X` works immediately
    _preload = (
        "trace", "clock", "ring", "bridge",
        "symbolic", "orchestration", "monitoring", "constraints",
    )
    for sub in _preload:
        src, dst = f"{_TARGET}.{sub}", f"{_THIS}.{sub}"
        try:
            mod = importlib.import_module(src)
            sys.modules.setdefault(dst, mod)
        except Exception:
            # best-effort: ignore optional/missing subpackages
            pass

class _CoreAliasFinder(importlib.abc.MetaPathFinder):
    """Redirect unresolved `core.*` imports to `lukhas.core.*`."""
    def find_spec(self, fullname, path=None, target=None):
        if fullname == _THIS or not fullname.startswith(_THIS + "."):
            return None
        target_name = fullname.replace(_THIS, _TARGET, 1)
        spec = importlib.util.find_spec(target_name)
        if spec is None:
            return None
        # Loader that registers the real module under the legacy name
        def _loader_exec(module):
            real = importlib.import_module(target_name)
            sys.modules[fullname] = real
        loader = types.SimpleNamespace(create_module=lambda s: None, exec_module=_loader_exec)
        return importlib.machinery.ModuleSpec(
            fullname, loader,
            is_package=spec.submodule_search_locations is not None
        )

def __getattr__(name: str):
    """Enable `from core import trace`."""
    try:
        mod = importlib.import_module(f"{_TARGET}.{name}")
        sys.modules.setdefault(f"{_THIS}.{name}", mod)
        return mod
    except Exception as e:
        raise AttributeError(name) from e

def __dir__():
    base = dir(importlib.import_module(_TARGET))
    return sorted(set(globals()) | set(base))

# Idempotent install
if not any(isinstance(f, _CoreAliasFinder) for f in sys.meta_path):
    _install_aliases()
    sys.meta_path.insert(0, _CoreAliasFinder())

# Reversible deprecation toggle
import os, warnings
if os.getenv("LUKHAS_WARN_LEGACY_CORE", "0") == "1":
    warnings.filterwarnings("default", category=ImportWarning)
    warnings.warn(
        "Legacy 'core' import in use; prefer 'lukhas.core' (set LUKHAS_WARN_LEGACY_CORE=0 to silence).",
        ImportWarning,
        stacklevel=2,
    )