"""
📄 MODULE      : lucas_ethics_guard.py
🛡️ PURPOSE     : Enforces symbolic consent, user data access boundaries, and ethical tiers
📚 COMPLIANCE  : GDPR, EU AI Act, ECHR, ISO/IEC 27001 (Annex A.5.19)
🧠 PART OF     : LUCAS AI Ethics Core
🛠️ VERSION     : v1.0.0 • 📅 CREATED: 2025-05-05 • ✍️ AUTHOR: LUCAS AGI TEAM

┌─────────────────────────────────────────────────────────────────────┐
│ This module acts as a real-time ethics firewall and contextual     │
│ resolution engine. It checks symbolic consent, prevents            │
│ unauthorized access to personal data, and logs attempted boundary  │
│ violations in symbolic terms for introspection and explainability.│
│ It also screens for cultural sensitivity issues using predefined  │
│ regional vocabulary filters.                                       │
└─────────────────────────────────────────────────────────────────────┘
"""
import json
import os
from datetime import datetime, timezone


class LegalComplianceAssistant:
    """Real-time EU legal compliance checker using ECHR guidelines and symbolic tiers.
    Also filters context using cultural vocabulary filters."""

    def __init__(self):
        self.legal_graph = self._build_legal_knowledge_graph()
        self.violation_log_path = "logs/ethics/violations.jsonl"

    def check_access(self, signal: str, tier_level: int, user_consent: dict) -> bool:
        """Determines if the signal is ethically accessible under the current tier and consent scope"""
        allowed = user_consent.get("allowed_signals", [])
        if signal not in allowed or user_consent.get("tier", 0) < tier_level:
            self.log_violation(signal, tier_level, user_consent)
            return False
        return True

    def log_violation(self, signal: str, tier: int, context: dict):
        violation = {
            "signal": signal,
            "required_tier": tier,
            "user_tier": context.get("tier"),
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            "explanation": f"Signal '{signal}' was accessed without sufficient tier or consent.",
        }
        os.makedirs(os.path.dirname(self.violation_log_path), exist_ok=True)
        with open(self.violation_log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(violation) + "\n")

    def _build_legal_knowledge_graph(self):
        return {
            "GDPR": ["consent", "right_to_be_forgotten", "data_minimization"],
            "ECHR": ["privacy", "expression", "non-discrimination"],
            "EU_AI_ACT": ["human oversight", "transparency", "safety"],
        }

    def check_cultural_context(self, content: str, region: str = "EU") -> list:
        """Checks content for cultural sensitivity based on regional norms"""
        sensitive_vocab = {
            "EU": ["illegal immigrant", "crazy", "man up"],
            "US": ["retarded", "ghetto", "terrorist"],
            "LATAM": ["indio", "maricón", "bruja"],
            "GLOBAL": ["slut", "fat", "dumb"],
        }

        blocked_terms = sensitive_vocab.get(region, []) + sensitive_vocab["GLOBAL"]
        violations = [word for word in blocked_terms if word in content.lower()]

        if violations:
            self.log_violation(
                signal="cultural_sensitivity",
                tier=3,
                context={
                    "tier": 2,
                    "violations": violations,
                    "region": region,
                    "content_excerpt": content[:100],
                },
            )
        return violations
