"""Bridge: tools.performance_monitor (logger compat included)."""
from __future__ import annotations
from lukhas._bridgeutils import bridge_from_candidates, bridge_from_candidates as bcf

__all__, _exp = bridge_from_candidates(
    "lukhas_website.lukhas.tools.performance_monitor",
    "candidate.tools.performance_monitor",
    "tools.performance_monitor",
)
globals().update(_exp)

# if module expects core.common.logger.getLogger
try:
    a, e = bcf("core.common.logger")
    if "getLogger" in a and "getLogger" not in globals():
        globals()["getLogger"] = e["getLogger"]; __all__.append("getLogger")
except Exception:
    pass
