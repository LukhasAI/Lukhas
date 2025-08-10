"""Bridge between Meta-Ethics Governor (MEG) and Ethics Policy System


#TAG:governance
#TAG:ethics
#TAG:neuroplastic
#TAG:colony


This module provides integration between the existing ethics policy system
and the Meta-Ethics Governor for comprehensive ethical governance.

ΛTAG: ethics_meg_bridge
"""

from typing import Any, Optional

from core.common import get_logger

from .meta_ethics_governor import (
    CulturalContext,
    EthicalDecision,
    EthicalVerdict,
    MetaEthicsGovernor,
    Severity,
)
from .meta_ethics_governor import EthicalEvaluation as MEGEvaluation
from .policy_engines.base import Decision as EthicsDecision
from .policy_engines.base import EthicsEvaluation, RiskLevel

logger = get_logger(__name__)


class MEGPolicyBridge:
    """Bridge between MEG and existing ethics policy system"""

    def __init__(self, meg: Optional[MetaEthicsGovernor] = None):
        """Initialize the bridge

        Args:
            meg: MEG instance (creates new if None)
        """
        self.meg = meg or MetaEthicsGovernor()
        self.metrics = {
            "meg_evaluations": 0,
            "meg_approvals": 0,
            "meg_rejections": 0,
            "meg_reviews_required": 0,
            "cultural_conflicts": 0,
        }

    def ethics_decision_to_meg_decision(
        self, decision: EthicsDecision
    ) -> EthicalDecision:
        """Convert ethics system decision to MEG decision format"""

        # Map urgency levels
        urgency_map = {
            RiskLevel.LOW: Severity.LOW,
            RiskLevel.MEDIUM: Severity.MEDIUM,
            RiskLevel.HIGH: Severity.HIGH,
            RiskLevel.CRITICAL: Severity.CRITICAL,
        }

        # Infer cultural context from decision context
        cultural_context = CulturalContext.UNIVERSAL
        if decision.context:
            context_str = str(decision.context).lower()
            if (
                "western" in context_str
                or "american" in context_str
                or "european" in context_str
            ):
                cultural_context = CulturalContext.WESTERN
            elif "eastern" in context_str or "asian" in context_str:
                cultural_context = CulturalContext.EASTERN
            elif "nordic" in context_str or "scandinavian" in context_str:
                cultural_context = CulturalContext.NORDIC
            elif "medical" in context_str or "healthcare" in context_str:
                cultural_context = CulturalContext.MEDICAL
            elif "legal" in context_str or "law" in context_str:
                cultural_context = CulturalContext.LEGAL
            elif "corporate" in context_str or "business" in context_str:
                cultural_context = CulturalContext.CORPORATE

        # Analyze action for ethical implications
        action_lower = decision.action.lower()
        potential_outcomes = []

        # Infer potential outcomes from action and context
        if (
            "help" in action_lower
            or "assist" in action_lower
            or "benefit" in action_lower
        ):
            potential_outcomes.append("positive: assistance provided")
        if "harm" in action_lower or "damage" in action_lower or "hurt" in action_lower:
            potential_outcomes.append("negative: potential harm")
        if "privacy" in action_lower or "data" in action_lower:
            potential_outcomes.append("privacy implications")
        if "learn" in action_lower or "improve" in action_lower:
            potential_outcomes.append("positive: learning/improvement")
        if "manipulate" in action_lower or "deceive" in action_lower:
            potential_outcomes.append("negative: manipulation/deception")

        return EthicalDecision(
            action_type=decision.action,
            description=f"Ethics evaluation: {decision.action}",
            context=decision.context or {},
            stakeholders=[decision.requester_id] if decision.requester_id else [],
            potential_outcomes=potential_outcomes,
            cultural_context=cultural_context,
            urgency=urgency_map.get(decision.urgency, Severity.MEDIUM),
            metadata={
                "original_glyphs": decision.glyphs or [],
                "symbolic_state": decision.symbolic_state or {},
                "timestamp": (
                    decision.timestamp.isoformat() if decision.timestamp else None
                ),
            },
        )

    def meg_evaluation_to_ethics_evaluation(
        self, meg_eval: MEGEvaluation, original_decision: EthicsDecision
    ) -> EthicsEvaluation:
        """Convert MEG evaluation to ethics system evaluation format"""

        # Map verdicts to allowed/denied
        allowed_verdicts = {
            EthicalVerdict.APPROVED,
            EthicalVerdict.CONDITIONALLY_APPROVED,
        }

        denied_verdicts = {EthicalVerdict.REJECTED, EthicalVerdict.LEGAL_VIOLATION}

        if meg_eval.verdict in allowed_verdicts:
            allowed = True
        elif meg_eval.verdict in denied_verdicts:
            allowed = False
        else:  # review_verdicts or unknown
            allowed = False  # Conservative approach

        # Create risk flags from MEG evaluation
        risk_flags = []
        if meg_eval.verdict == EthicalVerdict.CULTURAL_CONFLICT:
            risk_flags.append("CULTURAL_CONFLICT")
        if meg_eval.verdict == EthicalVerdict.LEGAL_VIOLATION:
            risk_flags.append("LEGAL_VIOLATION")
        if meg_eval.human_review_required:
            risk_flags.append("MEG_REVIEW_REQUIRED")
        if meg_eval.conflicting_principles:
            risk_flags.append("PRINCIPLE_CONFLICT")
        if meg_eval.severity.value >= Severity.HIGH.value:
            risk_flags.append("HIGH_SEVERITY")

        # Calculate risk metrics based on MEG evaluation
        drift_impact = 0.0
        if meg_eval.verdict == EthicalVerdict.CULTURAL_CONFLICT:
            drift_impact = 0.7
        elif meg_eval.severity.value >= Severity.HIGH.value:
            drift_impact = 0.5
        elif meg_eval.conflicting_principles:
            drift_impact = 0.4

        collapse_risk = 0.0
        if meg_eval.verdict == EthicalVerdict.REJECTED:
            collapse_risk = 0.6
        elif meg_eval.severity == Severity.CRITICAL:
            collapse_risk = 0.8
        elif meg_eval.confidence < 0.3:
            collapse_risk = 0.4

        symbolic_alignment = (
            meg_eval.confidence
        )  # Use MEG confidence as alignment score

        # Combine reasoning from MEG
        combined_reasoning = (
            f"MEG Evaluation ({meg_eval.evaluator_framework.value}): " + " + "
            "; ".join(meg_eval.reasoning)
        )

        # Create recommendations based on MEG findings
        recommendations = []
        if meg_eval.verdict == EthicalVerdict.CONDITIONALLY_APPROVED:
            recommendations.append("Monitor for compliance with conditions")
        if meg_eval.human_review_required:
            recommendations.append("Escalate to human review")
        if meg_eval.cultural_considerations:
            recommendations.append("Consider cultural context in implementation")
        if meg_eval.conflicting_principles:
            recommendations.append("Resolve principle conflicts before proceeding")

        return EthicsEvaluation(
            allowed=allowed,
            reasoning=combined_reasoning,
            confidence=meg_eval.confidence,
            risk_flags=risk_flags,
            drift_impact=drift_impact,
            symbolic_alignment=symbolic_alignment,
            collapse_risk=collapse_risk,
            policy_name="MEG_HYBRID",
            evaluation_time_ms=0.0,  # MEG doesn't track this
            recommendations=recommendations,
        )

    async def evaluate_with_meg(self, decision: EthicsDecision) -> EthicsEvaluation:
        """Evaluate decision using MEG and return in ethics system format"""

        self.metrics["meg_evaluations"] += 1

        try:
            # Convert to MEG format
            meg_decision = self.ethics_decision_to_meg_decision(decision)

            # Evaluate with MEG
            meg_evaluation = await self.meg.evaluate_decision(meg_decision)

            # Update metrics
            if meg_evaluation.verdict == EthicalVerdict.APPROVED:
                self.metrics["meg_approvals"] += 1
            elif meg_evaluation.verdict == EthicalVerdict.REJECTED:
                self.metrics["meg_rejections"] += 1

            if meg_evaluation.human_review_required:
                self.metrics["meg_reviews_required"] += 1

            if meg_evaluation.verdict == EthicalVerdict.CULTURAL_CONFLICT:
                self.metrics["cultural_conflicts"] += 1

            # Convert back to ethics system format
            ethics_evaluation = self.meg_evaluation_to_ethics_evaluation(
                meg_evaluation, decision
            )

            logger.info(
                f"MEG evaluation completed: {meg_evaluation.verdict.value} "
                f"(confidence: {meg_evaluation.confidence:.2f})"
            )

            return ethics_evaluation

        except Exception as e:
            logger.error(f"MEG evaluation failed: {e}")
            # Return conservative denial
            return EthicsEvaluation(
                allowed=False,
                reasoning=f"MEG evaluation failed: {str(e)}",
                confidence=0.0,
                risk_flags=["MEG_ERROR"],
                drift_impact=0.5,
                symbolic_alignment=0.0,
                collapse_risk=0.3,
                policy_name="MEG_ERROR",
                recommendations=["Fix MEG integration before proceeding"],
            )

    def get_cultural_context_info(self, context: CulturalContext) -> dict[str, Any]:
        """Get information about a cultural context from MEG"""
        if context in self.meg.cultural_adapters:
            return self.meg.cultural_adapters[context].copy()
        return {}

    def get_meg_status(self) -> dict[str, Any]:
        """Get MEG status and metrics"""
        meg_status = self.meg.get_status()
        meg_status["bridge_metrics"] = self.metrics.copy()
        return meg_status

    async def quick_meg_check(
        self, action: str, context: dict[str, Any] = None
    ) -> bool:
        """Quick ethical check using MEG"""
        return await self.meg.quick_ethical_check(action, context)

    def add_meg_callback(self, event_type: str, callback):
        """Add callback to MEG events"""
        self.meg.add_event_callback(event_type, callback)

    def get_human_review_queue(self) -> list[dict[str, Any]]:
        """Get MEG human review queue in simplified format"""
        queue = self.meg.get_human_review_queue()
        return [
            {
                "id": eval.evaluation_id,
                "decision_id": eval.decision_id,
                "verdict": eval.verdict.value,
                "confidence": eval.confidence,
                "reasoning": eval.reasoning,
                "timestamp": eval.timestamp.isoformat(),
                "severity": eval.severity.value,
            }
            for eval in queue
        ]


# Convenience function
def create_meg_bridge(meg: Optional[MetaEthicsGovernor] = None) -> MEGPolicyBridge:
    """Create and configure MEG bridge

    Args:
        meg: Existing MEG instance (creates new if None)

    Returns:
        Configured MEGPolicyBridge
    """
    bridge = MEGPolicyBridge(meg)
    logger.info("MEG-Policy bridge created and configured")
    return bridge


# CLAUDE CHANGELOG
# [CLAUDE_MEG_INTEGRATION] Created MEG-Policy bridge for integration between Meta-Ethics Governor and existing ethics policy system. Provides bidirectional conversion between decision formats, cultural context mapping, comprehensive risk assessment, and unified evaluation interface. Enables multi-framework ethical reasoning with cultural adaptation and human review escalation. # CLAUDE_EDIT_v0.20
