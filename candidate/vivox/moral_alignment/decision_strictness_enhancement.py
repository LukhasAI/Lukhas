"""
VIVOX Decision Strictness Enhancement
Implements stricter ethical evaluation criteria
"""
import time
from dataclasses import dataclass
from typing import Any

import streamlit as st

from .vivox_mae_core import ActionProposal, MAEDecision


@dataclass
class RiskAssessment:
    """Detailed risk assessment for an action"""

    risk_level: float  # 0.0 (safe) to 1.0 (critical risk)
    risk_factors: list[str]
    potential_harms: list[dict[str, Any]]
    mitigation_required: bool


class StricterEthicalEvaluator:
    """Enhanced ethical evaluation with stricter criteria"""

    def __init__(self):
        # Harm keywords that trigger immediate concern
        self.harm_indicators = {
            "override": 0.8,
            "bypass": 0.7,
            "disable": 0.6,
            "force": 0.7,
            "delete": 0.5,
            "remove": 0.4,
            "hack": 0.9,
            "exploit": 0.9,
            "manipulate": 0.7,
            "deceive": 0.8,
            "steal": 0.9,
            "destroy": 0.9,
            "kill": 1.0,
            "harm": 0.8,
            "injure": 0.8,
            "damage": 0.6,
            "violate": 0.8,
            "breach": 0.7,
            "unauthorized": 0.7,
            "illegal": 0.9,
            "unethical": 0.8,
        }

        # Safety-critical systems that should never be overridden
        self.protected_systems = {
            "safety",
            "security",
            "emergency",
            "medical",
            "life_support",
            "authentication",
            "authorization",
            "encryption",
            "privacy",
            "backup",
            "critical_infrastructure",
            "financial",
            "voting",
        }

        # Context factors that increase scrutiny
        self.risk_amplifiers = {
            "no_consent": 2.0,
            "vulnerable_population": 1.8,
            "irreversible": 1.7,
            "large_scale": 1.6,
            "precedent_setting": 1.5,
            "experimental": 1.4,
            "untested": 1.5,
            "rushed": 1.3,
        }

    async def assess_action_risk(self, action: ActionProposal, context: dict[str, Any]) -> RiskAssessment:
        """
        Perform comprehensive risk assessment
        """
        risk_factors = []
        potential_harms = []
        base_risk = 0.0

        # 1. Check action type for harm indicators
        action_lower = action.action_type.lower()
        for indicator, risk_value in self.harm_indicators.items():
            if indicator in action_lower:
                risk_factors.append(f"Action contains harm indicator: {indicator}")
                base_risk = max(base_risk, risk_value)

        # 2. Check for protected system violations
        content_str = str(action.content).lower()
        for system in self.protected_systems:
            if system in content_str or system in action_lower:
                if "override" in action_lower or "bypass" in action_lower:
                    risk_factors.append(f"Attempting to override protected system: {system}")
                    base_risk = max(base_risk, 0.9)
                    potential_harms.append(
                        {
                            "type": "system_compromise",
                            "target": system,
                            "severity": "critical",
                        }
                    )

        # 3. Analyze context for risk amplifiers
        amplifier = 1.0
        for factor, multiplier in self.risk_amplifiers.items():
            if context.get(factor):
                risk_factors.append(f"Risk amplifier present: {factor}")
                amplifier = max(amplifier, multiplier)

        # Special case: Check user consent
        if not context.get("user_consent", True):
            risk_factors.append("Action lacks user consent")
            base_risk = max(base_risk, 0.7)
            amplifier = max(amplifier, 1.5)

        # 4. Check for data sensitivity
        if "data_sensitivity" in context:
            sensitivity = context["data_sensitivity"]
            if sensitivity > 0.7:
                risk_factors.append(f"High data sensitivity: {sensitivity}")
                base_risk = max(base_risk, sensitivity * 0.8)
                potential_harms.append(
                    {
                        "type": "privacy_violation",
                        "severity": "high" if sensitivity > 0.8 else "medium",
                    }
                )

        # 5. Check for irreversible actions
        irreversible_keywords = ["delete", "destroy", "remove", "erase", "wipe"]
        for keyword in irreversible_keywords:
            if keyword in action_lower or keyword in content_str:
                risk_factors.append(f"Potentially irreversible action: {keyword}")
                base_risk = max(base_risk, 0.6)
                potential_harms.append({"type": "data_loss", "reversible": False, "severity": "high"})

        # 6. Calculate final risk level
        final_risk = min(1.0, base_risk * amplifier)

        # 7. Determine if mitigation is required
        mitigation_required = final_risk > 0.5 or len(potential_harms) > 0

        return RiskAssessment(
            risk_level=final_risk,
            risk_factors=risk_factors,
            potential_harms=potential_harms,
            mitigation_required=mitigation_required,
        )

    def calculate_stricter_dissonance(
        self,
        action: ActionProposal,
        context: dict[str, Any],
        risk_assessment: RiskAssessment,
    ) -> float:
        """
        Calculate dissonance score with stricter criteria
        """
        base_dissonance = 0.0

        # Start with risk level as base
        base_dissonance = risk_assessment.risk_level * 0.5

        # Add dissonance for each risk factor
        factor_dissonance = len(risk_assessment.risk_factors) * 0.05
        base_dissonance += min(0.3, factor_dissonance)

        # Add dissonance for potential harms
        harm_dissonance = 0.0
        for harm in risk_assessment.potential_harms:
            if harm.get("severity") == "critical":
                harm_dissonance += 0.2
            elif harm.get("severity") == "high":
                harm_dissonance += 0.1
            else:
                harm_dissonance += 0.05
        base_dissonance += min(0.4, harm_dissonance)

        # Increase dissonance for certain action types
        if action.action_type in [
            "override_safety",
            "bypass_security",
            "disable_protection",
        ]:
            base_dissonance += 0.3

        # Cap at 1.0
        return min(1.0, base_dissonance)

    def recommend_safer_alternatives(self, action: ActionProposal, risk_assessment: RiskAssessment) -> list[str]:
        """
        Suggest safer alternatives to risky actions
        """
        alternatives = []

        # Check for override actions
        if "override" in action.action_type:
            alternatives.append("Request proper authorization instead of overriding")
            alternatives.append("Document the need and escalate through proper channels")
            alternatives.append("Use temporary access with audit trail")

        # Check for data access without consent
        if "data_access" in action.action_type and risk_assessment.risk_level > 0.5:
            alternatives.append("Request explicit user consent before accessing data")
            alternatives.append("Use anonymized or aggregated data instead")
            alternatives.append("Limit scope to only necessary data fields")

        # Check for destructive actions
        if any(keyword in action.action_type.lower() for keyword in ["delete", "remove", "destroy"]):
            alternatives.append("Archive data instead of deleting")
            alternatives.append("Implement soft delete with recovery option")
            alternatives.append("Create backup before proceeding")

        # Check for security bypasses
        if "bypass" in action.action_type or "disable" in action.action_type:
            alternatives.append("Work within existing security constraints")
            alternatives.append("Request security exception through proper process")
            alternatives.append("Find alternative approach that maintains security")

        # General alternatives for high-risk actions
        if risk_assessment.risk_level > 0.7:
            alternatives.append("Seek additional review before proceeding")
            alternatives.append("Implement in controlled test environment first")
            alternatives.append("Break down into smaller, safer steps")

        return alternatives


class StrictDecisionMaker:
    """
    Wrapper for making stricter ethical decisions
    """

    def __init__(self, dissonance_threshold: float = 0.5):
        self.evaluator = StricterEthicalEvaluator()
        self.dissonance_threshold = dissonance_threshold

    async def evaluate_with_strict_criteria(
        self,
        action: ActionProposal,
        context: dict[str, Any],
        existing_decision: MAEDecision,
    ) -> MAEDecision:
        """
        Re-evaluate decision with stricter criteria
        """
        # Perform risk assessment
        risk_assessment = await self.evaluator.assess_action_risk(action, context)

        # Calculate stricter dissonance
        strict_dissonance = self.evaluator.calculate_stricter_dissonance(action, context, risk_assessment)

        # Get safer alternatives
        alternatives = self.evaluator.recommend_safer_alternatives(action, risk_assessment)

        # Override decision if risk is too high
        should_suppress = (
            strict_dissonance > self.dissonance_threshold
            or risk_assessment.risk_level > 0.7
            or risk_assessment.mitigation_required
        )

        if should_suppress and existing_decision.approved:
            # Override the approval
            return MAEDecision(
                approved=False,
                dissonance_score=strict_dissonance,
                moral_fingerprint=existing_decision.moral_fingerprint,
                ethical_confidence=1.0 - risk_assessment.risk_level,
                suppression_reason=f"High risk detected: {risk_assessment.risk_factors[0] if risk_assessment.risk_factors else 'Multiple risk factors'}",
                recommended_alternatives=alternatives,
                decision_timestamp=existing_decision.decision_timestamp,
                risk_assessment=risk_assessment,  # Attach for reference
            )

        # Enhance existing decision with risk info
        existing_decision.risk_assessment = risk_assessment
        if not existing_decision.recommended_alternatives:
            existing_decision.recommended_alternatives = alternatives

        return existing_decision


def create_strict_decision_maker(threshold: float = 0.5):
    """Factory function to create strict decision maker"""
    return StrictDecisionMaker(threshold)
