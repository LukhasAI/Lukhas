"""Bridge: orchestration.providers.openai"""
from __future__ import annotations

from _bridgeutils import bridge_from_candidates

_CANDIDATES = (
  "lukhas_website.orchestration.providers.openai",
  "candidate.orchestration.providers.openai",
  "orchestration.providers.openai",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES); globals().update(_exports)
