"""Bridge: orchestration.providers.anthropic.adapters"""
from __future__ import annotations

from _bridgeutils import bridge_from_candidates, deprecate, safe_guard

_CANDIDATES = (
    "lukhas_website.orchestration.providers.anthropic.adapters",
    "candidate.orchestration.providers.anthropic.adapters",
    "orchestration.providers.anthropic.adapters",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES); globals().update(_exports)
safe_guard(__name__, __all__); deprecate(__name__, "use via orchestration.providers.anthropic.adapters")
