"""Bridge: orchestration.providers.openai_modulated_service (syntax error stub)."""
from __future__ import annotations

from lukhas._bridgeutils import bridge_from_candidates, deprecate, safe_guard

_CANDIDATES = (
    "lukhas_website.lukhas.orchestration.providers.openai_modulated_service",
    "candidate.orchestration.providers.openai_modulated_service",
)

try:
    __all__, _exports = bridge_from_candidates(*_CANDIDATES)
    globals().update(_exports)
except SyntaxError:
    # candidate file has syntax error; provide no-op stub
    __all__ = []
    import warnings
    warnings.warn(
        f"{__name__}: backend has syntax error; using no-op stub",
        UserWarning,
        stacklevel=2,
    )

safe_guard(__name__, __all__)
deprecate(__name__, "backend has syntax errors, fix candidate.orchestration.providers.openai_modulated_service")
