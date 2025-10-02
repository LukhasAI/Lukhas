from __future__ import annotations
from typing import Dict, Any, List
from .world_model import generate_scenarios
from .evaluator import score_scenario

async def run_rollouts(seed: Dict[str, Any], trace_id: str) -> List[Dict[str, Any]]:
    scenarios = generate_scenarios(seed, trace_id)
    results = []
    for sc in scenarios:
        sc["scores"] = score_scenario(sc)
        results.append(sc)
    results.sort(key=lambda s: s["scores"]["utility"], reverse=True)
    return results
