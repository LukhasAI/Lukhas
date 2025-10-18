"""Bridge: orchestration.providers.openai.types (request/response models)."""
from __future__ import annotations

from _bridgeutils import bridge_from_candidates, safe_guard

_CANDIDATES = (
    "lukhas_website.orchestration.providers.openai.types",
    "candidate.orchestration.providers.openai.types",
    "orchestration.providers.openai.types",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES); globals().update(_exports)
safe_guard(__name__, __all__)
