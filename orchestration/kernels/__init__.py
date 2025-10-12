"""Bridge: orchestration.kernels (kernel bus, adapters)."""
from __future__ import annotations

from lukhas._bridgeutils import bridge_from_candidates

_CANDIDATES = (
  "lukhas_website.lukhas.orchestration.kernels",
  "candidate.orchestration.kernels",
  "orchestration.kernels",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES); globals().update(_exports)
