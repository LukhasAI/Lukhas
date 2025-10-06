"""Bridge: core.ethics.logic (policy rules, evaluators)."""
from __future__ import annotations
from lukhas._bridgeutils import bridge_from_candidates
_CANDIDATES = (
  "lukhas_website.lukhas.core.ethics.logic",
  "candidate.core.ethics.logic",
  "core.ethics.logic",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES); globals().update(_exports)
