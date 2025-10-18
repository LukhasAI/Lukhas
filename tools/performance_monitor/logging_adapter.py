"""Bridge: tools.performance_monitor.logging_adapter (getLogger fix)."""
from __future__ import annotations

from _bridgeutils import bridge_from_candidates

# Many failures originate from missing adapter that wraps logging.getLogger
_CANDIDATES = (
  "lukhas_website.tools.performance_monitor.logging_adapter",
  "labs.tools.performance_monitor.logging_adapter",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES); globals().update(_exports)
