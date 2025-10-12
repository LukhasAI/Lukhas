"""Bridge: lukhas.observability.opentelemetry_tracing."""
from __future__ import annotations

from lukhas._bridgeutils import bridge_from_candidates

_CANDIDATES = (
    "lukhas_website.lukhas.observability.opentelemetry_tracing",
    "labs.observability.opentelemetry_tracing",
    "observability.opentelemetry_tracing",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES); globals().update(_exports)
