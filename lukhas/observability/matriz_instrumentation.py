"""Bridge for ``lukhas.observability.matriz_instrumentation``."""
from __future__ import annotations

from lukhas._bridgeutils import bridge_from_candidates

__all__, _exports = bridge_from_candidates(
    "lukhas_website.lukhas.observability.matriz_instrumentation",
    "observability.matriz_instrumentation",
    "labs.observability.matriz_instrumentation",
)
globals().update(_exports)

# ΛTAG: observability_bridge -- MATRIZ instrumentation shim

