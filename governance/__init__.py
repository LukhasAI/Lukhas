"""
Lazy-loading proxy for core governance modules.
This __init__.py defers the import of heavy modules like the Guardian
and EthicsEngine until they are accessed, improving application startup time.
It also provides fallback stubs for optional dependencies.
"""
import importlib
from typing import Any

# --- Stubs for Graceful Degradation ---

class _Guardian_stub:
    """A stub for the Guardian system when the real module is not available."""
    def __init__(self, *args, **kwargs):
        print("Warning: Using stub for Guardian. Real implementation not found.")

    def validate(self, *args, **kwargs) -> bool:
        """Always returns True in stub mode."""
        return True

class _EthicsEngine_stub:
    """A stub for the EthicsEngine when the real module is not available."""
    def __init__(self, *args, **kwargs):
        print("Warning: Using stub for EthicsEngine. Real implementation not found.")

    def evaluate(self, *args, **kwargs) -> dict:
        """Returns a neutral evaluation in stub mode."""
        return {"risk": 0.0, "alignment": 1.0, "decision": "proceed"}

# --- Lazy Loading Implementation ---

_loaded_modules = {}

def __getattr__(name: str) -> Any:
    """
    Lazily loads governance sub-modules and their attributes on first access.
    """
    if name in _loaded_modules:
        return _loaded_modules[name]

    if name == "Guardian":
        try:
            # Assumes the primary implementation is in labs.governance.guardian
            module = importlib.import_module("labs.governance.guardian")
            Guardian = module.Guardian
            _loaded_modules[name] = Guardian
            return Guardian
        except (ImportError, AttributeError):
            _loaded_modules[name] = _Guardian_stub
            return _Guardian_stub

    if name == "EthicsEngine":
        try:
            # Assumes the primary implementation is in labs.governance.ethics
            module = importlib.import_module("labs.governance.ethics.engine")
            EthicsEngine = module.EthicsEngine
            _loaded_modules[name] = EthicsEngine
            return EthicsEngine
        except (ImportError, AttributeError):
             _loaded_modules[name] = _EthicsEngine_stub
             return _EthicsEngine_stub

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "EthicsEngine",
    "Guardian",
]
