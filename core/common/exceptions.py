"""
Bridge for `core.common.exceptions`.
Search order: candidate → core (root) → website; minimal stubs otherwise.
"""
from __future__ import annotations

from importlib import import_module

try:
    # Richest to leanest
    _m = None
    for _mod in (
        "labs.core.common.exceptions",
        "core.common.exceptions",
        "lukhas_website.core.common.exceptions",
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
    # Ensure LukhasError is available as base class
    if "LukhasError" not in globals():
        class LukhasError(Exception): ...
        if "LukhasError" not in __all__:
            __all__.append("LukhasError")
    class GLYPHTokenError(LukhasError):
        """Error in GLYPH token processing."""
        pass
    __all__.append("GLYPHTokenError")

# Add more exception stubs for test compatibility
_additional_exceptions = [
    "AuthenticationError",
    "AuthorizationError", 
    "CircuitBreakerError",
    "GuardianRejectionError",
    "MemoryDriftError",
    "ModuleTimeoutError",
    "ValidationError",
]

for _exc_name in _additional_exceptions:
    if _exc_name not in globals():
        if "LukhasError" not in globals():
            class LukhasError(Exception): ...
            __all__.append("LukhasError")
        # Create exception class dynamically
        globals()[_exc_name] = type(_exc_name, (LukhasError,), {
            "__doc__": f"{_exc_name} exception.",
            "__module__": __name__,
        })
        __all__.append(_exc_name)

# Add helper functions
if "raise_guardian_rejection" not in globals():
    def raise_guardian_rejection(message: str, suggestion: str = None):
        """Helper to raise GuardianRejectionError."""
        if "GuardianRejectionError" in globals():
            raise globals()["GuardianRejectionError"](message)
        raise Exception(message)
    __all__.append("raise_guardian_rejection")

if "raise_if_drift_excessive" not in globals():
    def raise_if_drift_excessive(memory_id: str, drift_level: float, threshold: float = 0.5):
        """Helper to check and raise MemoryDriftError if drift exceeds threshold."""
        if drift_level > threshold:
            if "MemoryDriftError" in globals():
                raise globals()["MemoryDriftError"](
                    f"Memory drift threshold exceeded for {memory_id}",
                    memory_id=memory_id,
                    drift_level=drift_level,
                    threshold=threshold
                )
            raise Exception(f"Memory drift threshold exceeded for {memory_id}")
    __all__.append("raise_if_drift_excessive")
