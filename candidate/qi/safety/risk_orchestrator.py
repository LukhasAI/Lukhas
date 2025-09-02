from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from typing import Any

import yaml

DEFAULT_CFG = {
    "weights": {
        "conf_low": 2.0,  # below conf_lo
        "conf_mid": 1.0,  # between conf_lo and conf_hi
        "pii": 1.5,
        "content_flag": 1.0,
    },
    "thresholds": {"conf_lo": 0.4, "conf_hi": 0.7},
    "tiers": [
        {"name": "low", "min": 0.0, "actions": []},
        {"name": "medium", "min": 1.5, "actions": ["increase_retrieval"]},
        {
            "name": "high",
            "min": 3.0,
            "actions": ["increase_retrieval", "reduce_temperature", "longer_reasoning"],
        },
        {
            "name": "critical",
            "min": 4.5,
            "actions": ["mask_pii", "human_review", "quarantine_output"],
        },
    ],
}


@dataclass
class RoutePlan:
    tier: str
    score: float
    actions: list[str]
    notes: str = ""


class RiskOrchestrator:
    def __init__(self, cfg_path: str | None = None):
        self.cfg = self._load_cfg(cfg_path)

    def _load_cfg(self, path: str | None) -> dict[str, Any]:
        if path and os.path.exists(path):
            return yaml.safe_load(open(path, encoding="utf-8"))
        # allow jurisdictional override under policy packs
        policy_root = os.path.join("qi", "safety", "policy_packs", "global")
        override = os.path.join(policy_root, "risk_orchestrator.yaml")
        if os.path.exists(override):
            return yaml.safe_load(open(override, encoding="utf-8"))
        return DEFAULT_CFG

    def score(
        self, *, calibrated_conf: float, pii_hits: int, content_flags: int
    ) -> float:
        w = self.cfg["weights"]
        t = self.cfg["thresholds"]
        s = 0.0
        if calibrated_conf < t["conf_lo"]:
            s += w["conf_low"]
        elif calibrated_conf < t["conf_hi"]:
            s += w["conf_mid"]
        s += w["pii"] * (1 if pii_hits > 0 else 0)
        s += w["content_flag"] * float(content_flags)
        return round(s, 3)

    def _tier(self, score: float) -> dict[str, Any]:
        best = sorted(self.cfg["tiers"], key=lambda x: x["min"])
        chosen = best[0]
        for tier in best:
            if score >= tier["min"]:
                chosen = tier
        return chosen

    def route(self, *, task: str, ctx: dict[str, Any]) -> RoutePlan:
        conf = float(ctx.get("calibrated_confidence", 0.5))
        pii_hits = len(ctx.get("pii", {}).get("_auto_hits", []))
        flags = len(ctx.get("content_flags", []))
        score = self.score(calibrated_conf=conf, pii_hits=pii_hits, content_flags=flags)
        tier = self._tier(score)
        actions = list(dict.fromkeys(tier.get("actions", [])))  # dedupe, preserve order
        # always remediate PII if present
        if pii_hits > 0 and "mask_pii" not in actions:
            actions.insert(0, "mask_pii")
        return RoutePlan(
            tier=tier["name"], score=score, actions=actions, notes=f"task={task}"
        )


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Risk Orchestrator")
    ap.add_argument("--cfg")
    ap.add_argument("--context", required=True)
    ap.add_argument("--task", required=True)
    args = ap.parse_args()
    ctx = json.load(open(args.context, encoding="utf-8"))
    ro = RiskOrchestrator(args.cfg)
    plan = ro.route(task=args.task, ctx=ctx)
    print(
        json.dumps(
            {
                "tier": plan.tier,
                "score": plan.score,
                "actions": plan.actions,
                "notes": plan.notes,
            },
            indent=2,
        )
    )
