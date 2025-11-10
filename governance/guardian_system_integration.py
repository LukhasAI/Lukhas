"""Shim: governance.guardian_system_integration → governance.guardian_system_integration."""
import importlib as _importlib

try:
    from governance.guardian_system_integration import GuardianSystemIntegrator, integrate_guardian_system
    __all__ = ["GuardianSystemIntegrator", "integrate_guardian_system"]
except ImportError:
    try:
        _mod = _importlib.import_module("labs.governance.guardian_system_integration")
        _names = getattr(_mod, "__all__", None)
        if _names is None:
            _names = [n for n in dir(_mod) if not n.startswith("_")]
        for _name in _names:
            globals()[_name] = getattr(_mod, _name)
        __all__ = list(_names)  # type: ignore[name-defined]
    except Exception:
        pass
