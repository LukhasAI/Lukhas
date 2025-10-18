"""Bridge: orchestration.providers (OpenAI/Anthropic/etc.)."""
from __future__ import annotations

from _bridgeutils import bridge_from_candidates

_CANDIDATES = (
  "lukhas_website.orchestration.providers",
  "candidate.orchestration.providers",
  "orchestration.providers",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES); globals().update(_exports)
