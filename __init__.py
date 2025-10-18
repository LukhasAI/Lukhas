"""
AUTO-GENERATED COMPATIBILITY LAYER
Maps `lukhas.<module>` to flat-root modules (e.g., `qi`, `core`, …),
and can bridge to `candidate.<module>` temporarily when needed.

This avoids rewriting thousands of imports during consolidation.
Remove once all modules are fully promoted and imports are updated.
"""
from __future__ import annotations

import importlib
import importlib.util
import pathlib
import pkgutil
import sys
import types

# Provide lightweight pandas shim if missing or incomplete
try:
    import pandas  # type: ignore

    if not hasattr(pandas, "_pandas_datetime_CAPI"):
        pandas._pandas_datetime_CAPI = None  # type: ignore[attr-defined]
except ImportError:
    pandas_stub = types.ModuleType("pandas")
    pandas_stub._pandas_datetime_CAPI = None  # type: ignore[attr-defined]
    sys.modules.setdefault("pandas", pandas_stub)

# Discover top-level modules that sit at repo root
ROOT = pathlib.Path(__file__).resolve().parents[1]  # points to repo root/Lukhas
CANDIDATE = ROOT / "labs"

# Any directory at repo root that looks like a Python package is a candidate module
def _root_packages():
    for p in ROOT.iterdir():
        if p.is_dir() and (p / "__init__.py").exists() and p.name not in {"lukhas", "labs", ".git", "artifacts"}:
            yield p.name

# Bridge table: module -> import path to use (root or candidate)
# Filled on first access; cached afterwards.
_BRIDGE: dict[str, str] = {}

def _resolve_target(modname: str) -> str | None:
    """
    Decide where to load from:
    - Prefer real root module `<modname>` if it exists.
    - Else fall back to `candidate.<modname>` if it exists.
    """
    if modname in _BRIDGE:
        return _BRIDGE[modname]
    # Prefer root
    try:
        importlib.import_module(modname)
        _BRIDGE[modname] = modname
        return modname
    except Exception:
        pass
    # Try candidate
    if (CANDIDATE / modname).exists():
        try:
            importlib.import_module(f"candidate.{modname}")
            _BRIDGE[modname] = f"candidate.{modname}"
            return _BRIDGE[modname]
        except Exception:
            return None
    return None

def __getattr__(name: str) -> types.ModuleType:
    """
    Support: `import qi` and `from qi.qi_entanglement import X`
    We alias:
      sys.modules["lukhas.<name>"] = real module
      On submodule access, we import underlying `<target>.<sub>` and alias
    """
    # Prefer real lukhas.<name> submodules before bridging to legacy locations.
    spec = importlib.util.find_spec(f"{__name__}.{name}")
    if spec is not None:
        mod = importlib.import_module(f"{__name__}.{name}")
        sys.modules[f"{__name__}.{name}"] = mod
        return mod

    target = _resolve_target(name)
    if not target:
        raise AttributeError(f"lukhas.{name} not found in root or candidate")
    mod = importlib.import_module(target)
    # Alias parent
    sys.modules[f"{__name__}.{name}"] = mod

    # Provide lazy submodule loader for `lukhas.<name>.<sub>`
    def _load_submodule(sub: str):
        real = f"{target}.{sub}"
        m = importlib.import_module(real)
        sys.modules[f"{__name__}.{name}.{sub}"] = m
        return getattr(m, "__dict__", {}).get(sub, m)

    # PEP 562 for subattribute access
    def __getattr_sub(sub):
        return _load_submodule(sub)

    # Attach a minimal proxy package that resolves submodules dynamically
    proxy = types.ModuleType(f"{__name__}.{name}")
    proxy.__dict__.update(mod.__dict__)
    proxy.__getattr__ = __getattr_sub  # type: ignore[attr-defined]
    sys.modules[f"{__name__}.{name}"] = proxy
    return proxy

# Make `import lukhas` a proper package in pkgutil
def __dir__():
    return sorted(set(list(globals().keys()) + list(_root_packages())))
