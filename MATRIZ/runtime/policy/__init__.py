"""Bridge for `matriz.runtime.policy`.

Auto-generated bridge following canonical pattern:
  1) lukhas_website.matriz.runtime.policy
  2) candidate.matriz.runtime.policy
  3) matriz.runtime.policy

Graceful fallback to stubs if no backend available.
"""
from __future__ import annotations

from importlib import import_module
from typing import List

__all__: List[str] = []

def _try(n: str):
    try:
        return import_module(n)
    except Exception:
        return None

# Try backends in order
_CANDIDATES = (
    "lukhas_website.matriz.runtime.policy",
    "candidate.matriz.runtime.policy",
    "matriz.runtime.policy",
)

_SRC = None
for _cand in _CANDIDATES:
    _m = _try(_cand)
    if _m:
        _SRC = _m
        for _k in dir(_m):
            if not _k.startswith("_"):
                globals()[_k] = getattr(_m, _k)
                __all__.append(_k)
        break

# Add expected symbols as stubs if not found
# No pre-defined stubs

# Add expected symbols as stubs if not found
if "PolicyEngine" not in globals():

    class PolicyEngine:
        def __init__(self, constitution_evaluator=None, constitution_rules=None):
            self.constitution_evaluator = constitution_evaluator
            self.constitution_rules = constitution_rules

        def evaluate_trigger(self, trigger):
            if not isinstance(trigger, dict):
                raise TypeError("trigger must be a mapping")

            if self.constitution_evaluator:
                if not self.constitution_evaluator(trigger):
                    return False

            if self.constitution_rules:
                for rule in self.constitution_rules:
                    if rule.startswith("require:"):
                        required_label = rule.split(":")[1]
                        if required_label not in trigger.get("constitution", []):
                            return False
                    elif rule in trigger.get("constitution", []):
                        return False

            return True
