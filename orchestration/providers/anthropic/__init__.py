"""Bridge: orchestration.providers.anthropic"""
from __future__ import annotations
from lukhas._bridgeutils import bridge_from_candidates
_CANDIDATES = (
  "lukhas_website.lukhas.orchestration.providers.anthropic",
  "candidate.orchestration.providers.anthropic",
  "orchestration.providers.anthropic",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES); globals().update(_exports)
