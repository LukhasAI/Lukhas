from __future__ import annotations
from typing import Dict, Any

def score_scenario(s: Dict[str, Any]) -> Dict[str, float]:
    var = s.get("variant")
    if var == "optimistic":
        return {"utility": 0.85, "risk": 0.15, "novelty": 0.35}
    if var == "baseline":
        return {"utility": 0.70, "risk": 0.30, "novelty": 0.40}
    return {"utility": 0.55, "risk": 0.60, "novelty": 0.80}
