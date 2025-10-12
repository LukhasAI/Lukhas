"""
Facade for `lukhas.core.policy_guard`.
Search order: website → candidate → core (root). Minimal fallbacks if none bind.
"""
from __future__ import annotations

from importlib import import_module
from typing import List, Optional

__all__: List[str] = ["PolicyGuard", "PolicyResult", "ReplayDecision"]
_SRC: Optional[object] = None

def _try(modname: str):
    try:
        return import_module(modname)
    except Exception:
        return None

# Richest to leanest sources.
for _mod in (
    "lukhas_website.lukhas.core.policy_guard",
    "labs.core.policy_guard",
    "core.policy_guard",
):
    _m = _try(_mod)
    if _m:
        _SRC = _m
        break

if _SRC is not None:
    # Re-export public names from the bound module if they exist.
    for _name in ("PolicyGuard", "PolicyResult", "ReplayDecision"):
        if hasattr(_SRC, _name):
            globals()[_name] = getattr(_SRC, _name)
    # Keep __all__ accurate.
    __all__ = [n for n in __all__ if n in globals()]
else:
    # Minimal safe fallbacks – keep signatures simple and non-blocking.
    class PolicyResult:
        def __init__(self, allowed: bool, reason: str = ""):
            self.allowed = allowed
            self.reason = reason
        def __repr__(self) -> str:
            return f"PolicyResult(allowed={self.allowed}, reason={self.reason!r})"

    class ReplayDecision(PolicyResult):
        pass

    class PolicyGuard:
        def check(self, *_args, **_kw) -> PolicyResult:
            return PolicyResult(True, "fallback-allow")

def __getattr__(name: str):
    if _SRC is not None:
        return getattr(_SRC, name)
    raise AttributeError(name)
