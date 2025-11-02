# candidate/core/orchestration/consensus_arbitrator.py
"""
Consensus arbitration: choose among proposals with ethics gating.

Fail-closed: ethics_risk >= 0.8 is excluded.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass
from typing import Iterable, List, Tuple


@dataclass
class Proposal:
    id: str
    confidence: float
    ts: float
    ethics_risk: float  # 0 allow ... 1 block
    role_weight: float  # e.g. ΛiD weight
    rationale: str = ""


def score(p: Proposal, now: float | None = None) -> float:
    now = now or time.time()
    if p.ethics_risk >= 0.8:
        return -math.inf
    recency = math.exp(-max(0.0, (now - p.ts)) / 30.0)
    return (0.6 * p.confidence) + (0.3 * recency) + (0.1 * p.role_weight) - (0.5 * p.ethics_risk)


def choose(proposals: Iterable[Proposal]) -> Tuple[Proposal | None, dict]:
    ranked: List[Tuple[Proposal, float]] = []
    for p in proposals:
        ranked.append((p, score(p)))
    ranked.sort(key=lambda t: t[1], reverse=True)
    winner = ranked[0][0] if ranked else None
    rationale = {"ranking": [(p.id, s) for p, s in ranked[:5]]}
    return winner, rationale
