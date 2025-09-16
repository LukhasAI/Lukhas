"""Symbolic moral agent template with simple reasoning hooks."""

# LUKHAS_TAG: symbolic_template, moral_agent
from typing import Any
import logging

# TAG:governance
# TAG:ethics
# TAG:neuroplastic
# TAG:colony


logger = logging.getLogger(__name__)


class MoralAgentTemplate:
    """A template for a symbolic moral agent."""

    def __init__(self) -> None:
        self.name = "moral_agent"

    def process_signal(self, signal: dict[str, Any]) -> dict[str, Any]:
        """Processes a signal and returns a moral judgment."""
        action = signal.get("action", "")
        context = signal.get("context", {})

        # Expand moral reasoning beyond keyword heuristics
        judgment, affect_delta, reasoning_context = self._comprehensive_moral_analysis(action, context)

        # ΛTAG: driftScore
        drift_score = abs(affect_delta)

        logger.debug(
            "MoralAgentTemplate processed action=%s affect_delta=%s driftScore=%s reasoning=%s",
            action,
            affect_delta,
            drift_score,
            reasoning_context.get("primary_framework", "keyword")
        )

        return {
            "judgment": judgment,
            "confidence": drift_score,
            "metrics": {
                "affect_delta": affect_delta,
                "driftScore": drift_score,
                "reasoning_frameworks": reasoning_context.get("frameworks_applied", []),
                "ethical_principles": reasoning_context.get("principles_considered", []),
                "confidence_factors": reasoning_context.get("confidence_factors", {})
            },
        }

    def _comprehensive_moral_analysis(self, action: str, context: dict) -> tuple[str, float, dict]:
        """Expanded moral reasoning using multiple ethical frameworks."""
        reasoning_context = {
            "frameworks_applied": [],
            "principles_considered": [],
            "confidence_factors": {}
        }

        # 1. Deontological Analysis (Rule-based ethics)
        deont_result = self._deontological_analysis(action, context)

        # 2. Consequentialist Analysis (Outcome-based ethics)
        conseq_result = self._consequentialist_analysis(action, context)

        # 3. Virtue Ethics Analysis (Character-based ethics)
        virtue_result = self._virtue_ethics_analysis(action, context)

        # 4. Care Ethics Analysis (Relationship-based ethics)
        care_result = self._care_ethics_analysis(action, context)

        # Synthesize results from multiple frameworks
        frameworks = [deont_result, conseq_result, virtue_result, care_result]
        reasoning_context["frameworks_applied"] = [f["framework"] for f in frameworks]

        # Weight the judgments (can be made more sophisticated)
        weighted_affect = sum(f["affect_delta"] * f["weight"] for f in frameworks) / sum(f["weight"] for f in frameworks)

        # Determine overall judgment
        if weighted_affect > 0.3:
            judgment = "approve"
        elif weighted_affect < -0.3:
            judgment = "reject"
        else:
            judgment = "neutral"

        # Calculate confidence based on framework agreement
        agreements = [f["judgment"] for f in frameworks]
        confidence_boost = agreements.count(judgment) / len(agreements)
        reasoning_context["confidence_factors"]["framework_agreement"] = confidence_boost

        reasoning_context["primary_framework"] = max(frameworks, key=lambda f: abs(f["affect_delta"]))["framework"]
        reasoning_context["principles_considered"] = list(set(p for f in frameworks for p in f.get("principles", [])))

        return judgment, weighted_affect, reasoning_context

    def _deontological_analysis(self, action: str, context: dict) -> dict:
        """Rule-based ethical analysis."""
        principles = []
        affect_delta = 0.0

        # Universal rules
        if any(word in action.lower() for word in ["kill", "murder", "harm", "torture", "abuse"]):
            affect_delta = -1.0
            principles.append("do_no_harm")
        elif any(word in action.lower() for word in ["help", "assist", "heal", "protect", "save"]):
            affect_delta = 1.0
            principles.append("beneficence")
        elif any(word in action.lower() for word in ["lie", "deceive", "cheat", "steal"]):
            affect_delta = -0.7
            principles.append("honesty")
        elif any(word in action.lower() for word in ["consent", "autonomy", "choice", "voluntary"]):
            affect_delta = 0.8
            principles.append("autonomy")

        judgment = "approve" if affect_delta > 0 else "reject" if affect_delta < 0 else "neutral"

        return {
            "framework": "deontological",
            "affect_delta": affect_delta,
            "judgment": judgment,
            "weight": 0.3,
            "principles": principles
        }

    def _consequentialist_analysis(self, action: str, context: dict) -> dict:
        """Outcome-based ethical analysis."""
        principles = []
        affect_delta = 0.0

        # Analyze potential outcomes
        potential_harm = context.get("potential_harm", 0)
        potential_benefit = context.get("potential_benefit", 0)
        affected_people = context.get("affected_people", 1)

        # Utilitarian calculation
        if potential_harm > 0:
            affect_delta -= potential_harm * (affected_people / 10)  # Scale down
            principles.append("minimize_harm")
        if potential_benefit > 0:
            affect_delta += potential_benefit * (affected_people / 10)
            principles.append("maximize_benefit")

        # Look for outcome indicators in action
        if any(word in action.lower() for word in ["prevent", "stop", "avoid"]):
            affect_delta += 0.5
            principles.append("prevention")
        elif any(word in action.lower() for word in ["cause", "create", "generate"]):
            if any(bad in action.lower() for bad in ["damage", "pain", "suffering"]):
                affect_delta -= 0.8
                principles.append("harm_prevention")

        judgment = "approve" if affect_delta > 0 else "reject" if affect_delta < 0 else "neutral"

        return {
            "framework": "consequentialist",
            "affect_delta": affect_delta,
            "judgment": judgment,
            "weight": 0.4,
            "principles": principles
        }

    def _virtue_ethics_analysis(self, action: str, context: dict) -> dict:
        """Character-based ethical analysis."""
        principles = []
        affect_delta = 0.0

        # Analyze virtues
        virtues = {
            "courage": ["brave", "courageous", "stand up", "defend"],
            "compassion": ["care", "empathy", "kindness", "comfort"],
            "honesty": ["truth", "honest", "transparent", "genuine"],
            "justice": ["fair", "equal", "just", "right"],
            "temperance": ["moderate", "balanced", "restrained", "controlled"],
            "wisdom": ["wise", "thoughtful", "careful", "prudent"]
        }

        vices = {
            "cowardice": ["coward", "flee", "abandon", "desert"],
            "cruelty": ["cruel", "mean", "vicious", "brutal"],
            "dishonesty": ["lie", "deceive", "fake", "false"],
            "injustice": ["unfair", "biased", "discriminate", "prejudice"],
            "excess": ["extreme", "excessive", "overindulge", "addiction"],
            "ignorance": ["ignore", "dismiss", "careless", "reckless"]
        }

        for virtue, keywords in virtues.items():
            if any(word in action.lower() for word in keywords):
                affect_delta += 0.6
                principles.append(virtue)

        for vice, keywords in vices.items():
            if any(word in action.lower() for word in keywords):
                affect_delta -= 0.6
                principles.append(f"avoid_{vice}")

        judgment = "approve" if affect_delta > 0 else "reject" if affect_delta < 0 else "neutral"

        return {
            "framework": "virtue_ethics",
            "affect_delta": affect_delta,
            "judgment": judgment,
            "weight": 0.2,
            "principles": principles
        }

    def _care_ethics_analysis(self, action: str, context: dict) -> dict:
        """Relationship-based ethical analysis."""
        principles = []
        affect_delta = 0.0

        # Analyze care and relationship aspects
        relationship_context = context.get("relationships", {})
        care_level = context.get("care_required", 0)

        if any(word in action.lower() for word in ["nurture", "support", "listen", "understand"]):
            affect_delta += 0.7
            principles.append("care")
        elif any(word in action.lower() for word in ["abandon", "neglect", "ignore", "dismiss"]):
            affect_delta -= 0.7
            principles.append("neglect_prevention")

        # Consider vulnerable populations
        if context.get("involves_vulnerable", False):
            if affect_delta > 0:
                affect_delta += 0.3  # Boost positive actions toward vulnerable
                principles.append("protect_vulnerable")
            else:
                affect_delta -= 0.5  # Heavily penalize harm to vulnerable
                principles.append("vulnerable_protection")

        judgment = "approve" if affect_delta > 0 else "reject" if affect_delta < 0 else "neutral"

        return {
            "framework": "care_ethics",
            "affect_delta": affect_delta,
            "judgment": judgment,
            "weight": 0.1,
            "principles": principles
        }


plugin = MoralAgentTemplate
