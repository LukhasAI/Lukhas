"""
Bridge for `lukhas.core.ethics.logic`.
Search order: candidate → core → website; minimal stubs otherwise.
"""
from __future__ import annotations
from importlib import import_module
from enum import Enum
from typing import Any, Dict, List

__all__: List[str] = []
_SRC = None

def _bind(modname: str) -> bool:
    global _SRC, __all__
    try:
        m = import_module(modname)
    except Exception:
        return False
    _SRC = m
    __all__ = [n for n in dir(m) if not n.startswith("_")]
    return True

for _mod in (
    "candidate.core.ethics.logic",
    "core.ethics.logic",
    "lukhas_website.lukhas.core.ethics.logic",
):
    if _bind(_mod):
        break
else:
    class SafetyTag(str, Enum):
        SAFE = "safe"
        REVIEW = "review"
        BLOCK = "block"

    def evaluate_policy(rule: Any, context: Dict[str, Any]) -> SafetyTag:
        # Minimal fallback: treat all as SAFE
        return SafetyTag.SAFE

    def apply_policies(rules: List[Any], context: Dict[str, Any]) -> SafetyTag:
        for r in rules or []:
            tag = evaluate_policy(r, context)
            if tag is SafetyTag.BLOCK:
                return SafetyTag.BLOCK
            if tag is SafetyTag.REVIEW:
                return SafetyTag.REVIEW
        return SafetyTag.SAFE

    __all__ = ["SafetyTag", "evaluate_policy", "apply_policies"]

if _SRC is not None:
    def __getattr__(name: str):
        return getattr(_SRC, name)
