"""
Bridge for `lukhas.core.common.exceptions`.
Search order: candidate → core (root) → website; minimal stubs otherwise.
"""
from __future__ import annotations
from importlib import import_module

try:
    # Richest to leanest
    _m = None
    for _mod in (
        "candidate.core.common.exceptions",
        "core.common.exceptions",
        "lukhas_website.lukhas.core.common.exceptions",
    ):
        try:
            _m = import_module(_mod)
            break
        except Exception:
            continue

    if _m:
        for _name in dir(_m):
            if not _name.startswith("_"):
                globals()[_name] = getattr(_m, _name)
        __all__ = [n for n in dir(_m) if not n.startswith("_")]
    else:
        raise ImportError("No backend found")
except Exception:
    class LukhasError(Exception): ...
    class ConfigurationError(LukhasError): ...
    class DependencyMissing(LukhasError): ...
    __all__ = ["LukhasError", "ConfigurationError", "DependencyMissing"]

# Additional exception types for test compatibility
if "GLYPHTokenError" not in globals():
    class GLYPHTokenError(LukhasError):
        """Error in GLYPH token processing."""
        pass
    __all__.append("GLYPHTokenError")
