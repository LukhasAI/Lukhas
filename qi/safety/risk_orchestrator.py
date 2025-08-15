from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any
@dataclass
class RoutePlan:
    tier: str
    actions: list
    notes: str = ""

class RiskOrchestrator:
    def score(self, *, calibrated_conf: float, pii_hits: int, content_flags: int, jurisdiction: str="global") -> str:
        risk = 0
        risk += (0 if calibrated_conf >= 0.7 else (1 if calibrated_conf >= 0.4 else 2))
        risk += 1 if pii_hits>0 else 0
        risk += min(2, content_flags)
        return ["low","med","high","critical"][min(3, risk)]
    def route(self, *, task: str, ctx: Dict[str,Any]) -> RoutePlan:
        conf = float(ctx.get("calibrated_confidence", 0.5))
        pii_hits = len(ctx.get("pii",{}).get("_auto_hits",[]))
        flags = len(ctx.get("content_flags",[]))
        tier = self.score(calibrated_conf=conf, pii_hits=pii_hits, content_flags=flags, jurisdiction=ctx.get("jurisdiction","global"))
        actions = []
        if tier in ("med","high","critical"):
            actions.append("increase_retrieval")
        if tier in ("high","critical"):
            actions += ["longer_reasoning","reduce_temperature"]
        if pii_hits>0:
            actions.append("mask_pii")
        if tier=="critical":
            actions.append("human_review")
        return RoutePlan(tier=tier, actions=actions, notes=f"task={task}")
if __name__ == "__main__":
    import json, argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--context", required=True)
    ap.add_argument("--task", required=True)
    args = ap.parse_args()
    ctx = json.loads(open(args.context).read())
    plan = RiskOrchestrator().route(task=args.task, ctx=ctx)
    print(json.dumps({"tier":plan.tier,"actions":plan.actions,"notes":plan.notes}, indent=2))
