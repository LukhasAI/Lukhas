from __future__ import annotations

from typing import Any

from .evaluator import score_scenario
from .world_model import generate_scenarios


async def run_rollouts(seed: dict[str, Any], trace_id: str) -> list[dict[str, Any]]:
    scenarios = generate_scenarios(seed, trace_id)
    results = []
    for sc in scenarios:
        sc["scores"] = score_scenario(sc)
        results.append(sc)
    results.sort(key=lambda s: s["scores"]["utility"], reverse=True)
    return results
