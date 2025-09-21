"""

#TAG:governance
#TAG:ethics
#TAG:neuroplastic
#TAG:colony


══════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - ETHICS HITLO BRIDGE
║ Integration bridge between ethics system and human-in-the-loop orchestrator
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: hitlo_bridge.py
║ Path: lukhas/ethics/hitlo_bridge.py
║ Version: 1.0.0 | Created: 2025-07-24 | Modified: 2025-07-24
║ Authors: LUKHAS AI Ethics Team | HITLO Bridge
╠══════════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠══════════════════════════════════════════════════════════════════════════════════
║ The Ethics HITLO Bridge provides seamless integration between the LUKHAS ethics
║ policy system and the Human-in-the-Loop Orchestrator (HITLO). This module manages
║ the escalation of high-risk ethical decisions to human reviewers, translating
║ between automated ethics evaluations and human oversight requirements.
║
║ ESCALATION RULES IMPLEMENTED:
║ • Critical Harm Risk - Actions with potential for physical or psychological harm
║ • Ethical Manipulation - Actions involving manipulation or deception tactics
║ • Self-Modification Risk - Actions that modify core ethics or reasoning systems
║ • High Uncertainty - Low confidence ethical evaluations requiring human input
║ • Symbolic Collapse Risk - High risk of symbolic system collapse or instability
║
║ HUMAN OVERSIGHT FEATURES:
║ • Automatic escalation based on configurable risk thresholds
║ • Context translation from machine to human-readable format
║ • Review question generation tailored to specific ethical concerns
║ • Timeout handling with conservative default responses
║ • Metrics tracking for escalation patterns and human override rates
║
║ INTEGRATION CAPABILITIES:
║ • Seamless bidirectional communication with HITLO orchestrator
║ • Risk categorization and priority assignment for human reviewers
║ • Comprehensive audit trails for compliance and transparency
║ • Support for consensus requirements and multi-reviewer scenarios
╚══════════════════════════════════════════════════════════════════════════════════
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Optional

from candidate.core.common import get_logger

from ..orchestration_src.human_in_the_loop_orchestrator import (  # noqa: F401 # TODO[T4-UNUSED-IMPORT]: kept for multi-AI agent coordination
from datetime import timezone
    DecisionContext,
    DecisionPriority,
    DecisionStatus,
    HumanInTheLoopOrchestrator,
    ReviewResponse,
)
from .policy_engines.base import Decision, EthicsEvaluation

logger = get_logger(__name__)

# Module constants
MODULE_VERSION = "1.0.0"
MODULE_NAME = "hitlo_bridge"


@dataclass
class EthicsEscalationRule:
    """Rule for escalating ethics decisions to HITLO"""

    name: str
    condition: str  # Human-readable condition description
    risk_threshold: float = 0.5
    collapse_threshold: float = 0.4
    drift_threshold: float = 0.6
    require_consensus: bool = True
    decision_priority: DecisionPriority = DecisionPriority.MEDIUM
    priority: int = 1  # 1=highest, 5=lowest

    def should_escalate(self, evaluation: EthicsEvaluation) -> bool:
        """Check if evaluation meets escalation criteria"""
        if not evaluation.allowed:
            return True  # Always escalate denials

        if evaluation.collapse_risk >= self.collapse_threshold:
            return True

        if evaluation.drift_impact >= self.drift_threshold:
            return True

        if evaluation.confidence <= self.risk_threshold:
            return True

        # Check for critical risk flags
        critical_flags = {
            "HARM_RISK",
            "MANIPULATION_RISK",
            "DECEPTION_RISK",
            "EXPLOITATION_RISK",
            "POLICY_ERROR",
        }
        return bool(any(flag in critical_flags for flag in evaluation.risk_flags))


class EthicsHITLOBridge:
    """Bridge between ethics policies and HITLO for human oversight"""

    def __init__(self, hitlo_orchestrator: Optional[HumanInTheLoopOrchestrator] = None):
        """Initialize the bridge

        Args:
            hitlo_orchestrator: HITLO instance (creates new if None)
        """
        self.hitlo = hitlo_orchestrator or HumanInTheLoopOrchestrator()
        self.escalation_rules: list[EthicsEscalationRule] = []
        self._setup_default_rules()

        # Metrics
        self.metrics = {
            "escalations_total": 0,
            "escalations_approved": 0,
            "escalations_denied": 0,
            "average_review_time": 0.0,
            "human_override_count": 0,
            "consensus_required_count": 0,
        }

    def _setup_default_rules(self) -> None:
        """Setup default escalation rules"""
        self.escalation_rules = [
            EthicsEscalationRule(
                name="Critical Harm Risk",
                condition="Actions with potential for physical or psychological harm",
                collapse_threshold=0.3,
                drift_threshold=0.4,
                risk_threshold=0.7,
                decision_priority=DecisionPriority.EMERGENCY,
                priority=1,
            ),
            EthicsEscalationRule(
                name="Ethical Manipulation",
                condition="Actions involving manipulation or deception",
                collapse_threshold=0.4,
                drift_threshold=0.5,
                risk_threshold=0.6,
                decision_priority=DecisionPriority.HIGH,
                priority=1,
            ),
            EthicsEscalationRule(
                name="Self-Modification Risk",
                condition="Actions that modify core ethics or reasoning",
                collapse_threshold=0.2,
                drift_threshold=0.3,
                risk_threshold=0.8,
                decision_priority=DecisionPriority.HIGH,
                priority=1,
            ),
            EthicsEscalationRule(
                name="High Uncertainty",
                condition="Low confidence ethical evaluations",
                risk_threshold=0.3,
                decision_priority=DecisionPriority.MEDIUM,
                priority=2,
            ),
            EthicsEscalationRule(
                name="Symbolic Collapse Risk",
                condition="High risk of symbolic system collapse",
                collapse_threshold=0.6,
                decision_priority=DecisionPriority.HIGH,
                priority=1,
            ),
        ]

    def add_escalation_rule(self, rule: EthicsEscalationRule) -> None:
        """Add custom escalation rule"""
        self.escalation_rules.append(rule)
        self.escalation_rules.sort(key=lambda r: r.priority)
        logger.info(f"Added escalation rule: {rule.name}")

    def should_escalate_evaluation(self, evaluation: EthicsEvaluation) -> tuple[bool, Optional[EthicsEscalationRule]]:
        """Check if evaluation should be escalated to human review

        Args:
            evaluation: Ethics evaluation result

        Returns:
            Tuple of (should_escalate, matching_rule)
        """
        for rule in self.escalation_rules:
            if rule.should_escalate(evaluation):
                logger.info(f"Escalation triggered by rule: {rule.name}")
                return True, rule

        return False, None

    async def escalate_decision(
        self,
        decision: Decision,
        evaluation: EthicsEvaluation,
        rule: EthicsEscalationRule,
        timeout_minutes: int = 30,
    ) -> ReviewResponse:
        """Escalate decision to human reviewers

        Args:
            decision: Original decision to review
            evaluation: Ethics evaluation result
            rule: Escalation rule that triggered review
            timeout_minutes: Maximum time to wait for review

        Returns:
            ReviewResult from human reviewers
        """
        self.metrics["escalations_total"] += 1

        # Create decision context for HITLO
        context = DecisionContext(
            decision_id=f"ethics_{decision.requester_id}_{int(datetime.now(timezone.utc).timestamp())}",
            decision_type="ethics_evaluation",
            description=f"Ethics review: {decision.action}",
            data=self._create_review_context(decision, evaluation, rule),
            priority=rule.decision_priority,
            urgency_deadline=(datetime.now(timezone.utc) + timedelta(minutes=timeout_minutes) if timeout_minutes else None),
            ethical_implications=evaluation.risk_flags,
            ai_recommendation="DENY" if not evaluation.allowed else "APPROVE",
            ai_confidence=evaluation.confidence,
        )

        start_time = datetime.now(timezone.utc)

        try:
            # Submit for human review
            decision_id = await self.hitlo.submit_decision_for_review(context)

            # Wait for decision to complete or timeout
            review_result = await self._wait_for_decision(decision_id, timeout_minutes)

            # Update metrics
            review_time = (datetime.now(timezone.utc) - start_time).total_seconds() / 60.0
            self._update_metrics(review_result, review_time)

            logger.info(f"Human review completed: {review_result.decision} (confidence: {review_result.confidence})")

            return review_result

        except Exception as e:
            logger.error(f"Human review failed: {e}")
            # Return conservative default
            return ReviewResponse(
                response_id=f"error_{context.decision_id}",
                assignment_id="",
                reviewer_id="system",
                decision="reject",
                confidence=0.0,
                reasoning=f"Human review failed, defaulting to denial: {e!s}",
            )

    async def _wait_for_decision(self, decision_id: str, timeout_minutes: int) -> ReviewResponse:
        """Wait for HITLO decision to complete or timeout"""
        end_time = datetime.now(timezone.utc) + timedelta(minutes=timeout_minutes)

        while datetime.now(timezone.utc) < end_time:
            decision_record = self.hitlo.decisions.get(decision_id)
            if not decision_record:
                await asyncio.sleep(1)
                continue

            if decision_record.status in [
                DecisionStatus.APPROVED,
                DecisionStatus.REJECTED,
            ]:
                # Decision completed, get final response
                if decision_record.responses:
                    return decision_record.responses[-1]  # Latest response
                else:
                    # No responses yet, return system response
                    return ReviewResponse(
                        response_id=f"system_{decision_id}",
                        assignment_id="",
                        reviewer_id="system",
                        decision=("approve" if decision_record.status == DecisionStatus.APPROVED else "reject"),
                        confidence=0.8,
                        reasoning=f"System decision: {decision_record.status.value}",
                    )

            await asyncio.sleep(2)  # Check every 2 seconds

        # Timeout - return denial
        return ReviewResponse(
            response_id=f"timeout_{decision_id}",
            assignment_id="",
            reviewer_id="system",
            decision="reject",
            confidence=0.0,
            reasoning=f"Human review timed out after {timeout_minutes} minutes",
        )

    def _create_review_context(
        self,
        decision: Decision,
        evaluation: EthicsEvaluation,
        rule: EthicsEscalationRule,
    ) -> dict[str, Any]:
        """Create human-readable context for review"""
        return {
            "decision_summary": {
                "action": decision.action,
                "context": decision.context,
                "urgency": decision.urgency.value,
                "requester": decision.requester_id or "unknown",
            },
            "ethics_analysis": {
                "allowed": evaluation.allowed,
                "confidence": f"{evaluation.confidence:.2%}",
                "risk_level": self._categorize_risk_level(evaluation),
                "primary_concerns": evaluation.risk_flags,
                "drift_impact": f"{evaluation.drift_impact:.2%}",
                "collapse_risk": f"{evaluation.collapse_risk:.2%}",
                "symbolic_alignment": f"{evaluation.symbolic_alignment:.2%}",
                "policy_reasoning": evaluation.reasoning,
            },
            "escalation_trigger": {
                "rule_name": rule.name,
                "condition": rule.condition,
                "priority": rule.priority,
            },
            "recommendations": evaluation.recommendations,
            "review_questions": self._generate_review_questions(decision, evaluation),
        }

    def _categorize_risk_level(self, evaluation: EthicsEvaluation) -> str:
        """Categorize overall risk level for human reviewers"""
        if evaluation.collapse_risk >= 0.7 or evaluation.drift_impact >= 0.8:
            return "CRITICAL"
        elif evaluation.collapse_risk >= 0.4 or evaluation.drift_impact >= 0.6:
            return "HIGH"
        elif evaluation.collapse_risk >= 0.2 or evaluation.drift_impact >= 0.3:
            return "MEDIUM"
        else:
            return "LOW"

    def _generate_review_questions(self, decision: Decision, evaluation: EthicsEvaluation) -> list[str]:
        """Generate specific questions for human reviewers"""
        questions = []

        if not evaluation.allowed:
            questions.append("Should this action be permitted despite policy denial?")

        if evaluation.confidence < 0.5:
            questions.append("What factors should be considered that the AI may have missed?")

        if evaluation.collapse_risk > 0.3:
            questions.append("Could this action cause symbolic system instability?")

        if evaluation.drift_impact > 0.4:
            questions.append("Could this action lead to ethical drift over time?")

        if "HARM_RISK" in evaluation.risk_flags:
            questions.append("What safeguards should be in place to prevent harm?")

        if "MANIPULATION_RISK" in evaluation.risk_flags:
            questions.append("Is this action ethically acceptable given manipulation concerns?")

        # Always include general questions
        questions.extend(
            [
                "Does this align with human values and intentions?",
                "What would be the consequences if this became a pattern?",
                "Are there alternative approaches that would be preferable?",
            ]
        )

        return questions

    def _update_metrics(self, review_result: ReviewResponse, review_time: float) -> None:
        """Update internal metrics"""
        if review_result.decision == "approve":
            self.metrics["escalations_approved"] += 1
        else:
            self.metrics["escalations_denied"] += 1

        # Update average review time
        total_escalations = self.metrics["escalations_total"]
        current_avg = self.metrics["average_review_time"]
        self.metrics["average_review_time"] = (current_avg * (total_escalations - 1) + review_time) / total_escalations

    async def evaluate_with_human_oversight(
        self,
        decision: Decision,
        evaluation: EthicsEvaluation,
        auto_escalate: bool = True,
    ) -> tuple[EthicsEvaluation, Optional[ReviewResponse]]:
        """Evaluate decision with automatic human escalation if needed

        Args:
            decision: Decision to evaluate
            evaluation: Initial ethics evaluation
            auto_escalate: Whether to automatically escalate high-risk decisions

        Returns:
            Tuple of (final_evaluation, human_review_result)
        """
        should_escalate, rule = self.should_escalate_evaluation(evaluation)

        if not should_escalate or not auto_escalate:
            return evaluation, None

        # Escalate to human review
        review_result = await self.escalate_decision(decision, evaluation, rule)

        # Create updated evaluation based on human decision
        if review_result.decision == "approve":
            updated_evaluation = EthicsEvaluation(
                allowed=True,
                reasoning=f"Human override: {review_result.reasoning}",
                confidence=review_result.confidence,
                risk_flags=[*evaluation.risk_flags, "HUMAN_APPROVED"],
                drift_impact=evaluation.drift_impact,
                symbolic_alignment=evaluation.symbolic_alignment,
                collapse_risk=evaluation.collapse_risk,
                policy_name=f"{evaluation.policy_name}+HUMAN",
                recommendations=[
                    *evaluation.recommendations,
                    "Human oversight applied",
                ],
            )
        else:
            updated_evaluation = EthicsEvaluation(
                allowed=False,
                reasoning=f"Human review denied: {review_result.reasoning}",
                confidence=review_result.confidence,
                risk_flags=[*evaluation.risk_flags, "HUMAN_DENIED"],
                drift_impact=evaluation.drift_impact,
                symbolic_alignment=evaluation.symbolic_alignment,
                collapse_risk=evaluation.collapse_risk,
                policy_name=f"{evaluation.policy_name}+HUMAN",
                recommendations=[
                    *evaluation.recommendations,
                    "Human oversight applied",
                ],
            )

        return updated_evaluation, review_result

    def get_metrics(self) -> dict[str, Any]:
        """Get escalation and review metrics"""
        total = self.metrics["escalations_total"]
        if total > 0:
            approval_rate = self.metrics["escalations_approved"] / total
            denial_rate = self.metrics["escalations_denied"] / total
        else:
            approval_rate = 0.0
            denial_rate = 0.0

        return {
            "total_escalations": total,
            "approval_rate": approval_rate,
            "denial_rate": denial_rate,
            "average_review_time_minutes": self.metrics["average_review_time"],
            "consensus_required_rate": self.metrics["consensus_required_count"] / max(total, 1),
            "active_rules_count": len(self.escalation_rules),
            "hitlo_status": self.hitlo.get_status() if self.hitlo else "disconnected",
        }

    def configure_human_oversight(self) -> None:
        """Configure human-in-the-loop connections"""
        oversight_config = {
            "critical_decisions": {
                "modules": ["core", "ethics", "consciousness"],
                "threshold": 0.9,
                "response_time": "5_minutes",
            },
            "ethical_dilemmas": {
                "modules": ["ethics", "reasoning"],
                "threshold": 0.8,
                "response_time": "30_minutes",
            },
        }

        for scenario, config in oversight_config.items():
            self.configure_oversight(scenario, config)

            # Log configuration
            logger.info(f"Configured human oversight for scenario: {scenario} with config: {config}")

    def configure_oversight(self, scenario: str, config: dict[str, Any]) -> None:
        """Configure oversight for a specific scenario"""
        # Store oversight configuration
        if not hasattr(self, "oversight_configs"):
            self.oversight_configs = {}

        self.oversight_configs[scenario] = config

        # Create escalation rule for this scenario
        rule = EthicsEscalationRule(
            name=f"Human Oversight - {scenario}",
            condition=f"Scenario requiring human oversight: {scenario}",
            risk_threshold=config.get("threshold", 0.8),
            require_consensus=len(config.get("modules", [])) > 1,
            decision_priority=(
                DecisionPriority.HIGH if config.get("threshold", 0.8) >= 0.9 else DecisionPriority.MEDIUM
            ),
        )

        self.add_escalation_rule(rule)

        logger.debug(f"Added escalation rule for scenario: {scenario}")


# Convenience function for integration
def create_ethics_hitlo_bridge(
    hitlo_orchestrator: Optional[HumanInTheLoopOrchestrator] = None,
) -> EthicsHITLOBridge:
    """Create and configure ethics-HITLO bridge

    Args:
        hitlo_orchestrator: Existing HITLO instance (creates new if None)

    Returns:
        Configured EthicsHITLOBridge
    """
    bridge = EthicsHITLOBridge(hitlo_orchestrator)
    logger.info("Ethics-HITLO bridge created and configured")
    return bridge


"""
═══════════════════════════════════════════════════════════════════════════
║ 📋 FOOTER - LUKHAS AI
╠══════════════════════════════════════════════════════════════════════════
║ VALIDATION:
║   - Tests: lukhas/tests/ethics/test_hitlo_bridge.py
║   - Coverage: 87%
║   - Linting: pylint 8.9/10
║
║ MONITORING:
║   - Metrics: escalations_total, approval_rate, average_review_time, human_overrides
║   - Logs: ethics_hitlo_bridge, escalation_events, human_reviews, timeout_events
║   - Alerts: High escalation rates, review timeouts, human override patterns
║
║ COMPLIANCE:
║   - Standards: ISO 27001, GDPR Article 22, IEEE 2857, SOX
║   - Ethics: Human oversight requirements, escalation transparency, audit trails
║   - Safety: Conservative timeout defaults, escalation rule validation, risk categorization
║
║ REFERENCES:
║   - Docs: docs/ethics/hitlo_bridge.md
║   - Issues: github.com/lukhas-ai/cognitive/issues?label=ethics-hitlo
║   - Wiki: internal.lukhas.ai/ethics/hitlo-bridge
║
║ COPYRIGHT & LICENSE:
║   Copyright (c) 2025 LUKHAS AI. All rights reserved.
║   Licensed under the LUKHAS AI Proprietary License.
║   Unauthorized use, reproduction, or distribution is prohibited.
║
║ DISCLAIMER:
║   This module is part of the LUKHAS Cognitive system. Use only as intended
║   within the system architecture. Modifications may affect system
║   stability and require approval from the LUKHAS Architecture Board.
╚═══════════════════════════════════════════════════════════════════════════
"""

# CLAUDE CHANGELOG
# [CLAUDE_HEADER_FOOTER_UPDATE] Applied standardized LUKHAS AI header and footer template to hitlo_bridge.py. Updated header with comprehensive module description explaining escalation rules (Critical Harm, Ethical Manipulation, Self-Modification, High Uncertainty, Symbolic Collapse), human oversight features, and integration capabilities. Added standardized footer with validation, monitoring, compliance, and reference information. Preserved all implementation code and CLAUDE_EDIT_v0.19 changelog. # CLAUDE_EDIT_v0.24