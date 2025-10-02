from __future__ import annotations
from typing import Dict, Any, List

def generate_scenarios(seed: Dict[str, Any], trace_id: str) -> List[Dict[str, Any]]:
    goal = seed.get("goal", "unspecified")
    ctx_keys = sorted((seed.get("context") or {}).keys())
    base = {"goal": goal, "ctx": ctx_keys, "trace_id": trace_id}
    return [
        {**base, "variant": "optimistic", "assumptions": ["ideal conditions", "low risk"]},
        {**base, "variant": "baseline", "assumptions": ["expected variability", "moderate risk"]},
        {**base, "variant": "adversarial", "assumptions": ["edge cases", "high risk paths"]},
    ]
