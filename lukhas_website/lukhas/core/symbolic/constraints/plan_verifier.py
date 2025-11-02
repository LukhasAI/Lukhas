# lukhas/core/symbolic/constraints/plan_verifier.py
"""
Hard constraints pre-exec (minimal, extend later).

Rule examples:
- Block external POST when plan indicates PII presence.
"""

from __future__ import annotations

from typing import List, Tuple
from collections.abc import Mapping


def verify(plan: Mapping) -> Tuple[bool, List[str]]:
    violations: List[str] = []
    contains_pii = bool(plan.get("contains_pii"))
    verb = str(plan.get("verb", "")).upper()
    target = str(plan.get("target", ""))

    if contains_pii and verb == "POST" and ("http://" in target or "https://" in target):
        violations.append("PII+external_POST")

    return (len(violations) == 0, violations)
