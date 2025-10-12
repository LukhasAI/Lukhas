"""Governance facade exporting canonical guardian and policy symbols."""
from __future__ import annotations

from importlib import import_module
from typing import Iterable

__all__ = ["Guardian", "SafetyGuard", "PolicyGuard", "PolicyResult", "LUKHASLane", "get_lane_enum"]

_CANDIDATE_SOURCES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("lukhas_website.lukhas.governance.guardian_system", ("Guardian", "SafetyGuard", "PolicyGuard", "PolicyResult")),
    ("labs.core.ethics.ab_safety_guard", ("Guardian", "SafetyGuard", "PolicyGuard", "PolicyResult")),
    ("lukhas.governance.guardian_impl", ("Guardian", "SafetyGuard", "PolicyGuard", "PolicyResult")),
    ("lukhas_website.lukhas.governance.schema_registry", ("LUKHASLane", "get_lane_enum")),
    ("lukhas.governance.schema_registry", ("LUKHASLane", "get_lane_enum")),
)


def _bind(module: str, names: Iterable[str]) -> None:
    try:
        mod = import_module(module)
    except Exception:
        return
    for name in names:
        if hasattr(mod, name):
            globals()[name] = getattr(mod, name)
            if name not in __all__:
                __all__.append(name)  # type: ignore[arg-type]


for mod, symbols in _CANDIDATE_SOURCES:
    _bind(mod, symbols)


if "PolicyResult" not in globals():
    class PolicyResult:  # type: ignore[misc]
        pass


if "PolicyGuard" not in globals():
    class PolicyGuard:  # type: ignore[misc]
        def __call__(self, *args, **kwargs):
            return PolicyResult()


if "Guardian" not in globals():
    class Guardian:  # type: ignore[misc]
        """Fallback guardian implementation."""

        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

        def evaluate(self, *args, **kwargs):
            return PolicyResult()


if "SafetyGuard" not in globals():
    class SafetyGuard:  # type: ignore[misc]
        def __call__(self, *args, **kwargs):
            return PolicyResult()
