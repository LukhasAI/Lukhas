"""Bridge: orchestration.providers.anthropic.adapters"""
from __future__ import annotations

from _bridgeutils import bridge_from_candidates, deprecate, safe_guard

_CANDIDATES = (
    "lukhas_website.orchestration.providers.anthropic.adapters",
    "candidate.orchestration.providers.anthropic.adapters",
    "orchestration.providers.anthropic.adapters",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES); globals().update(_exports)  # TODO[T4-ISSUE]: {"code":"E702","ticket":"GH-1031","owner":"consciousness-team","status":"planned","reason":"Multiple statements on one line - split for readability","estimate":"5m","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_orchestration_providers_anthropic_adapters___init___py_L11"}
safe_guard(__name__, __all__); deprecate(__name__, "use via orchestration.providers.anthropic.adapters")  # TODO[T4-ISSUE]: {"code":"E702","ticket":"GH-1031","owner":"consciousness-team","status":"planned","reason":"Multiple statements on one line - split for readability","estimate":"5m","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_orchestration_providers_anthropic_adapters___init___py_L12"}
