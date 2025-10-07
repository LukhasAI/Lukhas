"""
Schema Registry bridge - canonical namespace for governance schemas.

Production-facing bridge re-exporting canonical registry.
"""
from __future__ import annotations

from importlib import import_module

__all__ = []

for path in [
    "lukhas_website.lukhas.governance.schema_registry",
    "governance.schema_registry",
    "candidate.core.ethics.schema_registry",
    "candidate.governance.schema_registry",
]:
    try:
        _m = import_module(path)
        names = getattr(_m, "__all__", [n for n in dir(_m) if not n.startswith("_")])
        globals().update({n: getattr(_m, n) for n in names})
        __all__ = names
        break
    except Exception:
        continue

if not __all__:
    # Minimal façade to satisfy imports; flesh out later
    from enum import Enum

    class LUKHASLane(Enum):
        """Lane enumeration stub."""
        EXPERIMENTAL = "experimental"
        CANDIDATE = "candidate"
        PRODUCTION = "production"

    class SchemaRegistry:
        """Schema registry placeholder."""
        pass

    def get_lane_enum():
        """Return lane enumeration."""
        return LUKHASLane

    __all__ = ["SchemaRegistry", "LUKHASLane", "get_lane_enum"]
