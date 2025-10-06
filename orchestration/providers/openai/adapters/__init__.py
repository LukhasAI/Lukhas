"""Bridge: orchestration.providers.openai.adapters"""
from __future__ import annotations
from lukhas._bridgeutils import bridge_from_candidates, safe_guard, deprecate
_CANDIDATES = (
    "lukhas_website.lukhas.orchestration.providers.openai.adapters",
    "candidate.orchestration.providers.openai.adapters",
    "orchestration.providers.openai.adapters",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES); globals().update(_exports)
safe_guard(__name__, __all__); deprecate(__name__, "use via lukhas.orchestration.providers.openai.adapters")
