"""Guardian integration facade with safe stubs."""
from __future__ import annotations

from importlib import import_module

__all__ = ["GuardianAdapter", "GuardianDecision", "guard_stream"]

_CANDIDATES = (
    "candidate.consciousness.guardian_integration",
    "lukhas_website.lukhas.consciousness.guardian_integration",
    "consciousness.guardian_integration",
    "candidate.core.ethics.ab_safety_guard",
)


def _find(name: str):
    for module in _CANDIDATES:
        try:
            mod = import_module(module)
        except Exception:
            continue
        if hasattr(mod, name):
            return getattr(mod, name)
    return None


for _name in list(__all__):
    value = _find(_name)
    if value is not None:
        globals()[_name] = value


if "GuardianDecision" not in globals():
    class GuardianDecision:  # type: ignore[misc]
        def __init__(self, allow: bool = True, reason: str = "noop") -> None:
            self.allow = allow
            self.reason = reason


if "GuardianAdapter" not in globals():
    class GuardianAdapter:  # type: ignore[misc]
        def evaluate(self, *args, **kwargs) -> GuardianDecision:
            return GuardianDecision()


if "guard_stream" not in globals():
    def guard_stream(iterable):  # type: ignore[misc]
        for item in iterable:
            yield item
