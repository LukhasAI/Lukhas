"""Shim: governance.identity → governance.identity or candidate.governance.identity."""
import importlib as _importlib

try:
    from governance.identity import GovernanceIdentity, IdentityGovernor, govern_identity
    __all__ = ["GovernanceIdentity", "IdentityGovernor", "govern_identity"]
except ImportError:
    try:
        _mod = _importlib.import_module("labs.governance.identity")
        _names = getattr(_mod, "__all__", None)
        if _names is None:
            _names = [n for n in dir(_mod) if not n.startswith("_")]
        for _name in _names:
            globals()[_name] = getattr(_mod, _name)
        __all__ = list(_names)  # type: ignore[name-defined]
    except Exception:
        pass
