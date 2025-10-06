"""Bridge: tools.categorize_todos (used by tests)."""
from __future__ import annotations
from lukhas._bridgeutils import bridge_from_candidates
_CANDIDATES = (
  "lukhas_website.lukhas.tools.categorize_todos",
  "candidate.tools.categorize_todos",
  "tools.categorize_todos",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES); globals().update(_exports)
