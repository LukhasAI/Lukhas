"""Bridge: orchestration.providers.anthropic.adapters"""
from __future__ import annotations

from lukhas._bridgeutils import bridge_from_candidates, deprecate, safe_guard

_CANDIDATES = (
    "lukhas_website.lukhas.orchestration.providers.anthropic.adapters",
    "candidate.orchestration.providers.anthropic.adapters",
    "orchestration.providers.anthropic.adapters",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES); globals().update(_exports)
safe_guard(__name__, __all__); deprecate(__name__, "use via lukhas.orchestration.providers.anthropic.adapters")
