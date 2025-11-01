"""Bridge: tools.performance_monitor.metrics"""
from __future__ import annotations

from _bridgeutils import bridge_from_candidates

_CANDIDATES = (
  "lukhas_website.tools.performance_monitor.metrics",
  "labs.tools.performance_monitor.metrics",
  "tools.performance_monitor.metrics",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES)
globals().update(_exports)
