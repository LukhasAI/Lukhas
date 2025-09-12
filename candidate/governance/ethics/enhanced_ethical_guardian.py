# lukhas/governance/ethics/enhanced_ethical_guardian.py
from dataclasses import dataclass
from typing import Dict, List, Any

@dataclass
class EthicsDecision:
    allow: bool
    risk_final: float
    reasons: List[str]
    matched: List[str]
    context_hits: List[str]
    policy_version: str

class EnhancedEthicalGuardian:
    def __init__(self, policy: Dict[str, Any], policy_version: str = "v1"):
        self.p = policy
        self.version = policy_version

    def evaluate(self, text: str, context: Dict[str, str]) -> EthicsDecision:
        kws = self.p["keywords_block"]
        matched = [k for k in kws if k in text.lower()]

        risk = 0.0
        reasons = []
        if matched:
            risk += self.p["risk"]["keyword_base"]
            reasons.append(f"keyword:{'+'.join(matched)}")

        ctx_hits = []
        domain = (context.get("domain") or "").lower()
        justification = (context.get("justification") or "").lower()

        # Context discount only if both domain and justification are whitelisted
        discount = 0.0
        if domain in self.p["risk"]["context_discount"]:
            allow_just = set(map(str.lower, self.p["justify_allow"].get(domain, [])))
            if any(tok in justification for tok in allow_just):
                discount = self.p["risk"]["context_discount"][domain]
                ctx_hits = [domain, "justified"]
                reasons.append(f"context:{domain}+justified")

        # clamp and decide
        floor = self.p["thresholds"]["floor"]
        ceil  = self.p["thresholds"]["ceiling"]
        risk_final = max(floor, min(ceil, risk - discount))
        allow = (risk_final < self.p["thresholds"]["decision"])

        return EthicsDecision(
            allow=allow, risk_final=risk_final, reasons=reasons,
            matched=matched, context_hits=ctx_hits, policy_version=self.version
        )
