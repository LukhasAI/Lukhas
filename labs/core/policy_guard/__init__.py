"""Governance policy guard facade for candidate core import paths."""
from __future__ import annotations

from importlib import import_module

__all__ = ["PolicyGuard", "PolicyResult", "ReplayDecision"]

_CANDIDATES = (
    "lukhas_website.lukhas.core.policy_guard",
    "lukhas.governance.policy_guard",
    "labs.core.ethics.ab_safety_guard",
)


def _resolve(module: str, name: str):
    try:
        mod = import_module(module)
    except Exception:
        return None
    return getattr(mod, name, None)


for _symbol in list(__all__):
    value = next((result for result in (_resolve(mod, _symbol) for mod in _CANDIDATES) if result), None)
    if value is not None:
        globals()[_symbol] = value


if "PolicyResult" not in globals():
    class PolicyResult:  # type: ignore[misc]
        ok: bool = True
        reason: str = "noop"


if "ReplayDecision" not in globals():
    class ReplayDecision:  # type: ignore[misc]
        allow: bool = True


if "PolicyGuard" not in globals():
    class PolicyGuard:  # type: ignore[misc]
        def evaluate(self, *args, **kwargs) -> PolicyResult:
            return PolicyResult()
