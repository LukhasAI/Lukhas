"""Bridge: orchestration.openai_modulated_service (syntax errors upstream guarded)."""
from __future__ import annotations

from _bridgeutils import bridge_from_candidates

_CANDIDATES = (
  "lukhas_website.orchestration.openai_modulated_service",
  "candidate.orchestration.openai_modulated_service",
  "orchestration.openai_modulated_service",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES); globals().update(_exports)
