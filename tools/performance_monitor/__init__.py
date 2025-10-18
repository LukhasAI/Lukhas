"""Bridge: tools.performance_monitor (with getLogger compat fix)."""
from __future__ import annotations

from _bridgeutils import bridge_from_candidates, deprecate, safe_guard

_CANDIDATES = (
    "lukhas_website.tools.performance_monitor",
    "labs.tools.performance_monitor",
    "tools.performance_monitor",
)

__all__, _exports = bridge_from_candidates(*_CANDIDATES)
globals().update(_exports)

# Phase 8: getLogger compat (some tests call getLogger(name, level))
try:
    logger_all, logger_exp = bridge_from_candidates("core.common.logger")
    if "getLogger" in logger_all and "getLogger" not in __all__:
        _orig = logger_exp["getLogger"]
        def _compat_getLogger(*args, **kwargs):
            # accept (name, level) but only pass name
            return _orig(*args[:1]) if args else _orig()
        globals()["getLogger"] = _compat_getLogger
        __all__ = list(__all__) + ["getLogger"]
except Exception:
    pass

safe_guard(__name__, __all__)
deprecate(__name__, "prefer candidate.tools.performance_monitor")
