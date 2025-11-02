"""
Ethical Engine for LUKHAS AI System

This module provides comprehensive ethical decision-making capabilities
for the LUKHAS AI consciousness system, integrating with the Constellation Framework
to ensure responsible AI behavior across all system operations.

#TAG:governance
#TAG:ethics
#TAG:neuroplastic
#TAG:colony

Features:
- Real-time ethical decision evaluation
- Constellation Framework integration (⚛️🧠🛡️)
- Constitutional AI principles enforcement
- Multi-layer ethical reasoning
- Context-aware moral judgment
- Guardian system integration

Rehabilitated: 2025-09-10 from quarantine status
Original location: ./orchestration/brain/compliance/ethical_engine.py
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

try:
    from core.common import get_logger
except ImportError:

    def get_logger(name):
        return logging.getLogger(name)


logger = get_logger(__name__)


class EthicalDecision(Enum):
    """Possible ethical decisions"""

    APPROVE = "approve"
    DENY = "deny"
    REVIEW = "review"
    ESCALATE = "escalate"
    MODIFY = "modify"
    MONITOR = "monitor"


class EthicalPrinciple(Enum):
    """Core ethical principles"""

    BENEFICENCE = "beneficence"  # Do good
    NON_MALEFICENCE = "non_maleficence"  # Do no harm
    AUTONOMY = "autonomy"  # Respect autonomy
    JUSTICE = "justice"  # Fairness and equity
    TRANSPARENCY = "transparency"  # Openness and honesty
    ACCOUNTABILITY = "accountability"  # Responsibility for actions
    PRIVACY = "privacy"  # Respect for privacy
    CONSENT = "consent"  # Informed consent


@dataclass
class EthicalContext:
    """Context for ethical evaluation"""

    action: str
    user_id: Optional[str] = None
    content: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    # Constellation Framework context
    identity_context: dict[str, Any] = field(default_factory=dict)  # ⚛️
    consciousness_context: dict[str, Any] = field(default_factory=dict)  # 🧠
    guardian_context: dict[str, Any] = field(default_factory=dict)  # 🛡️


@dataclass
class EthicalEvaluation:
    """Result of ethical evaluation"""

    decision: EthicalDecision
    confidence: float  # 0.0 to 1.0
    reasoning: str
    violated_principles: list[EthicalPrinciple] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    # Constellation Framework assessment
    identity_impact: str = "none"  # ⚛️
    consciousness_impact: str = "none"  # 🧠
    guardian_status: str = "monitoring"  # 🛡️

    # Metadata
    evaluation_time: float = 0.0
    evaluator_version: str = "1.0.0"
    timestamp: datetime = field(default_factory=datetime.now)


class EthicalEngine:
    """
    Core ethical decision-making engine for LUKHAS AI

    Provides comprehensive ethical evaluation capabilities with Constellation Framework
    integration for identity-consciousness-guardian alignment.
    """

    def __init__(self):
        self.logger = logger
        self.version = "1.0.0"

        # Constellation Framework weights
        self.identity_weight = 0.3  # ⚛️
        self.consciousness_weight = 0.4  # 🧠
        self.guardian_weight = 0.3  # 🛡️

        # Ethical thresholds
        self.approval_threshold = 0.8
        self.review_threshold = 0.6
        self.denial_threshold = 0.4

        # Principle weights
        self.principle_weights = {
            EthicalPrinciple.NON_MALEFICENCE: 0.25,  # Highest weight
            EthicalPrinciple.BENEFICENCE: 0.2,
            EthicalPrinciple.AUTONOMY: 0.15,
            EthicalPrinciple.JUSTICE: 0.15,
            EthicalPrinciple.TRANSPARENCY: 0.1,
            EthicalPrinciple.ACCOUNTABILITY: 0.1,
            EthicalPrinciple.PRIVACY: 0.05,
        }

        logger.info("🛡️ Ethical Engine initialized with Constellation Framework")

    def evaluate_action(self, context: EthicalContext) -> EthicalEvaluation:
        """
        Evaluate an action for ethical compliance

        Args:
            context: Ethical context containing action and metadata

        Returns:
            Ethical evaluation with decision and reasoning
        """
        start_time = datetime.now()

        try:
            # Multi-layer ethical analysis
            principle_scores = self._evaluate_principles(context)
            constellation_assessment = self._assess_trinity_impact(context)
            risk_analysis = self._analyze_risks(context)

            # Calculate overall ethical score
            overall_score = self._calculate_overall_score(principle_scores, constellation_assessment, risk_analysis)

            # Determine decision
            decision = self._determine_decision(overall_score, principle_scores)

            # Generate reasoning
            reasoning = self._generate_reasoning(decision, overall_score, principle_scores, constellation_assessment)

            # Identify violated principles
            violated_principles = [principle for principle, score in principle_scores.items() if score < 0.5]

            # Generate recommendations
            recommendations = self._generate_recommendations(decision, violated_principles, constellation_assessment)

            # Calculate evaluation time
            evaluation_time = (datetime.now() - start_time).total_seconds()

            evaluation = EthicalEvaluation(
                decision=decision,
                confidence=overall_score,
                reasoning=reasoning,
                violated_principles=violated_principles,
                recommendations=recommendations,
                identity_impact=constellation_assessment.get("identity_impact", "none"),
                consciousness_impact=constellation_assessment.get("consciousness_impact", "none"),
                guardian_status=constellation_assessment.get("guardian_status", "monitoring"),
                evaluation_time=evaluation_time,
                evaluator_version=self.version,
            )

            logger.debug(f"Ethical evaluation completed: {decision.value} (score: {overall_score:.2f})")
            return evaluation

        except Exception as e:
            logger.error(f"Ethical evaluation failed: {e}")

            # Conservative fallback
            return EthicalEvaluation(
                decision=EthicalDecision.REVIEW,
                confidence=0.5,
                reasoning=f"Evaluation error: {str(e)}",
                recommendations=["Manual review required due to evaluation error"],
                guardian_status="escalated",
                evaluation_time=(datetime.now() - start_time).total_seconds(),
            )

    def _evaluate_principles(self, context: EthicalContext) -> dict[EthicalPrinciple, float]:
        """Evaluate adherence to core ethical principles"""

        scores = {}

        # Non-maleficence: Do no harm
        harm_score = self._assess_harm_potential(context)
        scores[EthicalPrinciple.NON_MALEFICENCE] = 1.0 - harm_score

        # Beneficence: Do good
        benefit_score = self._assess_benefit_potential(context)
        scores[EthicalPrinciple.BENEFICENCE] = benefit_score

        # Autonomy: Respect user autonomy
        autonomy_score = self._assess_autonomy_respect(context)
        scores[EthicalPrinciple.AUTONOMY] = autonomy_score

        # Justice: Fairness and equity
        justice_score = self._assess_fairness(context)
        scores[EthicalPrinciple.JUSTICE] = justice_score

        # Transparency: Openness
        transparency_score = self._assess_transparency(context)
        scores[EthicalPrinciple.TRANSPARENCY] = transparency_score

        # Accountability: Responsibility
        accountability_score = self._assess_accountability(context)
        scores[EthicalPrinciple.ACCOUNTABILITY] = accountability_score

        # Privacy: Respect for privacy
        privacy_score = self._assess_privacy_protection(context)
        scores[EthicalPrinciple.PRIVACY] = privacy_score

        return scores

    def _assess_harm_potential(self, context: EthicalContext) -> float:
        """Assess potential for harm (0.0 = no harm, 1.0 = high harm)"""

        harm_indicators = 0.0

        if context.content:
            content_lower = context.content.lower()

            # Check for harmful content patterns
            harmful_patterns = [
                "violence",
                "harm",
                "dangerous",
                "illegal",
                "threat",
                "manipulation",
                "deception",
                "exploit",
                "abuse",
            ]

            for pattern in harmful_patterns:
                if pattern in content_lower:
                    harm_indicators += 0.2

        # Check action type
        risky_actions = ["delete", "remove", "destroy", "modify_critical"]
        if context.action in risky_actions:
            harm_indicators += 0.3

        # Check guardian context
        if context.guardian_context.get("risk_level") == "high":
            harm_indicators += 0.4

        return min(1.0, harm_indicators)

    def _assess_benefit_potential(self, context: EthicalContext) -> float:
        """Assess potential for benefit (0.0 = no benefit, 1.0 = high benefit)"""

        benefit_score = 0.5  # Neutral baseline

        # Check for beneficial actions
        beneficial_actions = ["help", "assist", "create", "improve", "learn", "educate", "heal", "support", "protect"]

        if any(action in context.action.lower() for action in beneficial_actions):
            benefit_score += 0.3

        # Check consciousness context for learning/growth
        if context.consciousness_context.get("learning_opportunity"):
            benefit_score += 0.2

        return min(1.0, benefit_score)

    def _assess_autonomy_respect(self, context: EthicalContext) -> float:
        """Assess respect for user autonomy"""

        autonomy_score = 0.8  # Default high respect

        # Check for autonomy violations
        if context.metadata.get("user_consent") is False:
            autonomy_score -= 0.4

        if context.action in ["force", "override", "bypass"]:
            autonomy_score -= 0.3

        # Check for user choice preservation
        if context.metadata.get("preserves_user_choice", True):
            autonomy_score += 0.1

        return max(0.0, min(1.0, autonomy_score))

    def _assess_fairness(self, context: EthicalContext) -> float:
        """Assess fairness and justice"""

        fairness_score = 0.8  # Default fair

        # Check for bias indicators
        bias_indicators = ["discriminate", "bias", "unfair", "prejudice"]
        if context.content and any(indicator in context.content.lower() for indicator in bias_indicators):
            fairness_score -= 0.4

        # Check for equal treatment
        if context.metadata.get("equal_treatment", True):
            fairness_score += 0.1

        return max(0.0, min(1.0, fairness_score))

    def _assess_transparency(self, context: EthicalContext) -> float:
        """Assess transparency and openness"""

        transparency_score = 0.7  # Default moderately transparent

        # Check for transparency indicators
        if context.metadata.get("transparent_process", False):
            transparency_score += 0.2

        if context.metadata.get("hidden_agenda", False):
            transparency_score -= 0.4

        return max(0.0, min(1.0, transparency_score))

    def _assess_accountability(self, context: EthicalContext) -> float:
        """Assess accountability and responsibility"""

        accountability_score = 0.8  # Default accountable

        # Check for accountability mechanisms
        if context.metadata.get("audit_trail", True):
            accountability_score += 0.1

        if context.guardian_context.get("monitoring_enabled", True):
            accountability_score += 0.1

        return min(1.0, accountability_score)

    def _assess_privacy_protection(self, context: EthicalContext) -> float:
        """Assess privacy protection"""

        privacy_score = 0.8  # Default good privacy

        # Check for privacy violations
        if context.metadata.get("accesses_personal_data", False):
            if not context.metadata.get("user_consent", False):
                privacy_score -= 0.5

        if context.action in ["expose", "leak", "share_private"]:
            privacy_score -= 0.6

        return max(0.0, privacy_score)

    def _assess_trinity_impact(self, context: EthicalContext) -> dict[str, str]:
        """Assess impact on Constellation Framework components"""

        # ⚛️ Identity impact assessment
        identity_impact = "none"
        if context.identity_context.get("affects_identity", False):
            identity_impact = "moderate"
            if not context.metadata.get("identity_consent", True):
                identity_impact = "high"

        # 🧠 Consciousness impact assessment
        consciousness_impact = "none"
        if context.consciousness_context.get("affects_consciousness", False):
            consciousness_impact = "moderate"
            if context.consciousness_context.get("drift_risk", False):
                consciousness_impact = "high"

        # 🛡️ Guardian status assessment
        guardian_status = "monitoring"
        if context.guardian_context.get("escalation_required", False):
            guardian_status = "escalated"
        elif context.guardian_context.get("active_protection", False):
            guardian_status = "protecting"

        return {
            "identity_impact": identity_impact,
            "consciousness_impact": consciousness_impact,
            "guardian_status": guardian_status,
        }

    def _analyze_risks(self, context: EthicalContext) -> dict[str, float]:
        """Analyze various risk factors"""

        return {
            "security_risk": self._assess_security_risk(context),
            "privacy_risk": self._assess_privacy_risk(context),
            "safety_risk": self._assess_safety_risk(context),
            "bias_risk": self._assess_bias_risk(context),
        }

    def _assess_security_risk(self, context: EthicalContext) -> float:
        """Assess security risk"""
        security_indicators = ["hack", "breach", "exploit", "vulnerability"]
        if context.content and any(indicator in context.content.lower() for indicator in security_indicators):
            return 0.8
        return 0.2

    def _assess_privacy_risk(self, context: EthicalContext) -> float:
        """Assess privacy risk"""
        if context.metadata.get("accesses_personal_data", False):
            return 0.6
        return 0.1

    def _assess_safety_risk(self, context: EthicalContext) -> float:
        """Assess safety risk"""
        safety_indicators = ["dangerous", "unsafe", "risk", "hazard"]
        if context.content and any(indicator in context.content.lower() for indicator in safety_indicators):
            return 0.7
        return 0.1

    def _assess_bias_risk(self, context: EthicalContext) -> float:
        """Assess bias risk"""
        bias_indicators = ["discriminate", "bias", "prejudice", "stereotype"]
        if context.content and any(indicator in context.content.lower() for indicator in bias_indicators):
            return 0.8
        return 0.2

    def _calculate_overall_score(
        self,
        principle_scores: dict[EthicalPrinciple, float],
        constellation_assessment: dict[str, str],
        risk_analysis: dict[str, float],
    ) -> float:
        """Calculate overall ethical score"""

        # Weighted principle score
        principle_score = sum(
            score * self.principle_weights.get(principle, 0.1) for principle, score in principle_scores.items()
        )

        # Constellation impact modifier
        constellation_modifier = 1.0
        if constellation_assessment["identity_impact"] == "high":
            constellation_modifier -= 0.2
        if constellation_assessment["consciousness_impact"] == "high":
            constellation_modifier -= 0.2
        if constellation_assessment["guardian_status"] == "escalated":
            constellation_modifier -= 0.3

        # Risk modifier
        avg_risk = sum(risk_analysis.values()) / len(risk_analysis)
        risk_modifier = 1.0 - (avg_risk * 0.3)

        overall_score = principle_score * constellation_modifier * risk_modifier
        return max(0.0, min(1.0, overall_score))

    def _determine_decision(
        self, overall_score: float, principle_scores: dict[EthicalPrinciple, float]
    ) -> EthicalDecision:
        """Determine ethical decision based on scores"""

        # Check for critical principle violations
        if principle_scores.get(EthicalPrinciple.NON_MALEFICENCE, 1.0) < 0.3:
            return EthicalDecision.DENY

        # Use overall score thresholds
        if overall_score >= self.approval_threshold:
            return EthicalDecision.APPROVE
        elif overall_score >= self.review_threshold:
            return EthicalDecision.REVIEW
        elif overall_score >= self.denial_threshold:
            return EthicalDecision.ESCALATE
        else:
            return EthicalDecision.DENY

    def _generate_reasoning(
        self,
        decision: EthicalDecision,
        overall_score: float,
        principle_scores: dict[EthicalPrinciple, float],
        constellation_assessment: dict[str, str],
    ) -> str:
        """Generate human-readable reasoning for the decision"""

        reasoning_parts = [f"Ethical decision: {decision.value} (confidence: {overall_score:.2f})"]

        # Principle analysis
        low_scores = [principle.value for principle, score in principle_scores.items() if score < 0.5]
        if low_scores:
            reasoning_parts.append(f"Concerns with: {', '.join(low_scores)}")

        # Constellation Framework impact
        constellation_impacts = [
            f"Identity: {constellation_assessment['identity_impact']}",
            f"Consciousness: {constellation_assessment['consciousness_impact']}",
            f"Guardian: {constellation_assessment['guardian_status']}",
        ]
        reasoning_parts.append(f"Constellation impact - {', '.join(constellation_impacts)}")

        return " | ".join(reasoning_parts)

    def _generate_recommendations(
        self,
        decision: EthicalDecision,
        violated_principles: list[EthicalPrinciple],
        constellation_assessment: dict[str, str],
    ) -> list[str]:
        """Generate actionable recommendations"""

        recommendations = []

        # Decision-specific recommendations
        if decision == EthicalDecision.DENY:
            recommendations.append("Action denied due to ethical concerns")
        elif decision == EthicalDecision.REVIEW:
            recommendations.append("Manual review recommended before proceeding")
        elif decision == EthicalDecision.ESCALATE:
            recommendations.append("Escalate to human oversight for decision")

        # Principle-specific recommendations
        for principle in violated_principles:
            if principle == EthicalPrinciple.NON_MALEFICENCE:
                recommendations.append("Review for potential harm and implement safeguards")
            elif principle == EthicalPrinciple.AUTONOMY:
                recommendations.append("Ensure user consent and preserve user choice")
            elif principle == EthicalPrinciple.PRIVACY:
                recommendations.append("Implement privacy protection measures")

        # Constellation Framework recommendations
        if constellation_assessment["guardian_status"] == "escalated":
            recommendations.append("Guardian system intervention required")

        return recommendations


# Export main classes
__all__ = ["EthicalDecision", "EthicalPrinciple", "EthicalContext", "EthicalEvaluation", "EthicalEngine"]
