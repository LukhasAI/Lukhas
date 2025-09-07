import logging
from datetime import timezone
import streamlit as st
logger = logging.getLogger(__name__)
"""

#TAG:governance
#TAG:ethics
#TAG:neuroplastic
#TAG:colony


Shared Ethics Engine

Centralized ethical reasoning system for DAST, ABAS, and NIAS.
Ensures consistent ethical decisions across all systems.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any

from candidate.core.common import get_logger
from ethics.seedra import get_seedra
from symbolic.core import Symbol, SymbolicDomain, SymbolicType, get_symbolic_vocabulary

logger = get_logger(__name__, timezone)


class EthicalPrinciple(Enum):
    """Core ethical principles"""

    DO_NO_HARM = auto()
    RESPECT_AUTONOMY = auto()
    ENSURE_BENEFICENCE = auto()
    MAINTAIN_JUSTICE = auto()
    PRESERVE_PRIVACY = auto()
    ENSURE_TRANSPARENCY = auto()
    PROMOTE_DIGNITY = auto()
    PREVENT_DECEPTION = auto()


class EthicalSeverity(Enum):
    """Severity levels for ethical violations"""

    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class DecisionType(Enum):
    """Types of ethical decisions"""

    ALLOW = "allow"
    BLOCK = "block"
    REQUIRE_CONSENT = "require_consent"
    DEFER = "defer"
    ESCALATE = "escalate"


@dataclass
class EthicalConstraint:
    """Ethical constraint definition"""

    id: str
    principle: EthicalPrinciple
    description: str
    severity: EthicalSeverity
    applies_to: list[str] = field(default_factory=list)  # Systems or domains
    conditions: dict[str, Any] = field(default_factory=dict)
    active: bool = True


@dataclass
class EthicalDecision:
    """Result of ethical evaluation"""

    decision_type: DecisionType
    confidence: float
    principles_considered: list[EthicalPrinciple]
    violations: list[tuple[EthicalPrinciple, EthicalSeverity]]
    reasoning: str
    recommendations: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


class SharedEthicsEngine:
    """
    Centralized ethics engine for all Golden Trio systems.

    Provides consistent ethical reasoning and decision-making
    across DAST, ABAS, and NIAS operations.
    """

    def __init__(self):
        self.constraints: dict[str, EthicalConstraint] = {}
        self.decision_history: list[dict[str, Any]] = []
        self.principle_weights: dict[EthicalPrinciple, float] = {}
        self.seedra = get_seedra()
        self.vocabulary = get_symbolic_vocabulary()
        self._lock = asyncio.Lock()

        self._initialize_constraints()
        self._initialize_principle_weights()

        logger.info("Shared Ethics Engine initialized")

    def _initialize_constraints(self):
        """Initialize default ethical constraints"""
        # Privacy constraints
        self.add_constraint(
            EthicalConstraint(
                id="privacy_biometric",
                principle=EthicalPrinciple.PRESERVE_PRIVACY,
                description="Biometric data requires explicit consent and on-device processing",
                severity=EthicalSeverity.HIGH,
                applies_to=["NIAS", "DAST"],
                conditions={"data_type": "biometric", "require_consent": True},
            )
        )

        # Harm prevention constraints
        self.add_constraint(
            EthicalConstraint(
                id="prevent_emotional_harm",
                principle=EthicalPrinciple.DO_NO_HARM,
                description="Prevent content that could cause emotional distress",
                severity=EthicalSeverity.HIGH,
                applies_to=["NIAS", "ABAS"],
                conditions={"emotional_state": "vulnerable", "block_triggers": True},
            )
        )

        # Autonomy constraints
        self.add_constraint(
            EthicalConstraint(
                id="respect_user_choice",
                principle=EthicalPrinciple.RESPECT_AUTONOMY,
                description="Respect user's explicit preferences and choices",
                severity=EthicalSeverity.MEDIUM,
                applies_to=["DAST", "ABAS", "NIAS"],
                conditions={"override_user_preference": False},
            )
        )

        # Transparency constraints
        self.add_constraint(
            EthicalConstraint(
                id="decision_transparency",
                principle=EthicalPrinciple.ENSURE_TRANSPARENCY,
                description="Provide clear explanations for decisions",
                severity=EthicalSeverity.MEDIUM,
                applies_to=["ABAS"],
                conditions={"explainable": True, "log_decisions": True},
            )
        )

        # Deception prevention
        self.add_constraint(
            EthicalConstraint(
                id="prevent_deception",
                principle=EthicalPrinciple.PREVENT_DECEPTION,
                description="Prevent misleading or deceptive content",
                severity=EthicalSeverity.HIGH,
                applies_to=["NIAS"],
                conditions={"verify_claims": True, "flag_suspicious": True},
            )
        )

    def _initialize_principle_weights(self):
        """Initialize weights for ethical principles"""
        self.principle_weights = {
            EthicalPrinciple.DO_NO_HARM: 1.0,
            EthicalPrinciple.RESPECT_AUTONOMY: 0.9,
            EthicalPrinciple.ENSURE_BENEFICENCE: 0.8,
            EthicalPrinciple.MAINTAIN_JUSTICE: 0.8,
            EthicalPrinciple.PRESERVE_PRIVACY: 0.95,
            EthicalPrinciple.ENSURE_TRANSPARENCY: 0.7,
            EthicalPrinciple.PROMOTE_DIGNITY: 0.85,
            EthicalPrinciple.PREVENT_DECEPTION: 0.9,
        }

    def add_constraint(self, constraint: EthicalConstraint) -> None:
        """Add an ethical constraint"""
        self.constraints[constraint.id] = constraint
        logger.debug(f"Added ethical constraint: {constraint.id}")

    async def evaluate_action(
        self, action: dict[str, Any], context: dict[str, Any], requesting_system: str
    ) -> EthicalDecision:
        """
        Evaluate an action for ethical compliance.

        Args:
            action: The action to evaluate
            context: Context including user state, environment, etc.
            requesting_system: System requesting evaluation (DAST, ABAS, or NIAS)

        Returns:
            EthicalDecision with verdict and reasoning
        """
        async with self._lock:
            violations = []
            principles_considered = set()
            reasoning_parts = []

            # Check consent first if applicable
            user_id = context.get("user_id")
            if user_id and self._requires_consent(action):
                consent_check = await self._check_consent_requirements(user_id, action, context)
                if not consent_check["allowed"]:
                    return EthicalDecision(
                        decision_type=DecisionType.REQUIRE_CONSENT,
                        confidence=1.0,
                        principles_considered=[EthicalPrinciple.RESPECT_AUTONOMY],
                        violations=[(EthicalPrinciple.RESPECT_AUTONOMY, EthicalSeverity.HIGH)],
                        reasoning=f"Consent required: {consent_check['reason']}",
                        recommendations=["Obtain explicit user consent before proceeding"],
                    )

            # Evaluate against each applicable constraint
            for constraint in self.constraints.values():
                if not constraint.active:
                    continue

                if requesting_system not in constraint.applies_to and "ALL" not in constraint.applies_to:
                    continue

                principles_considered.add(constraint.principle)

                violation = self._check_constraint_violation(constraint, action, context)

                if violation:
                    violations.append((constraint.principle, constraint.severity))
                    reasoning_parts.append(f"Violates {constraint.principle.name}: {constraint.description}")

            # Calculate decision based on violations
            decision = self._calculate_decision(violations, action, context)

            # Build recommendations
            recommendations = self._generate_recommendations(violations, action, context, requesting_system)

            # Create ethical decision
            ethical_decision = EthicalDecision(
                decision_type=decision["type"],
                confidence=decision["confidence"],
                principles_considered=list(principles_considered),
                violations=violations,
                reasoning=("; ".join(reasoning_parts) if reasoning_parts else "No ethical concerns identified"),
                recommendations=recommendations,
                metadata={
                    "requesting_system": requesting_system,
                    "action_type": action.get("type", "unknown"),
                    "context_summary": self._summarize_context(context),
                },
            )

            # Log decision
            await self._log_decision(ethical_decision, action, context, requesting_system)

            return ethical_decision

    def _requires_consent(self, action: dict[str, Any]) -> bool:
        """Check if action requires consent"""
        consent_required_actions = [
            "process_biometric_data",
            "store_personal_data",
            "share_user_data",
            "track_location",
            "analyze_emotions",
        ]

        action_type = action.get("type", "")
        return any(req in action_type for req in consent_required_actions)

    async def _check_consent_requirements(
        self, user_id: str, action: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        """Check if user has provided necessary consent"""
        data_type = action.get("data_type", "general")
        operation = action.get("operation", "process")

        consent_result = await self.seedra.check_consent(user_id, data_type, operation)

        return consent_result

    def _check_constraint_violation(
        self,
        constraint: EthicalConstraint,
        action: dict[str, Any],
        context: dict[str, Any],
    ) -> bool:
        """Check if a specific constraint is violated"""
        # Check each condition in the constraint
        for condition_key, expected_value in constraint.conditions.items():
            actual_value = action.get(condition_key) or context.get(condition_key)

            # Special handling for different condition types
            if condition_key == "emotional_state" and expected_value == "vulnerable":
                if context.get("emotional_state", {}).get("vulnerability", 0) > 0.7:
                    return True

            elif condition_key == "override_user_preference":
                if action.get("overrides_preference", False) != expected_value:
                    return True

            elif isinstance(expected_value, bool) and bool(actual_value) != expected_value:
                return True

        return False

    def _calculate_decision(
        self,
        violations: list[tuple[EthicalPrinciple, EthicalSeverity]],
        action: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Calculate final decision based on violations"""
        if not violations:
            return {"type": DecisionType.ALLOW, "confidence": 0.95}

        # Check for critical violations
        max_severity = max(v[1].value for v in violations) if violations else 0

        if max_severity >= EthicalSeverity.CRITICAL.value:
            return {"type": DecisionType.BLOCK, "confidence": 1.0}
        elif max_severity >= EthicalSeverity.HIGH.value:
            # Check if user is in emergency context
            if context.get("emergency", False):
                return {"type": DecisionType.ESCALATE, "confidence": 0.9}
            else:
                return {"type": DecisionType.BLOCK, "confidence": 0.9}
        elif max_severity >= EthicalSeverity.MEDIUM.value:
            # Defer for human review or additional context
            return {"type": DecisionType.DEFER, "confidence": 0.7}
        else:
            # Low severity - allow with monitoring
            return {"type": DecisionType.ALLOW, "confidence": 0.6}

    def _generate_recommendations(
        self,
        violations: list[tuple[EthicalPrinciple, EthicalSeverity]],
        action: dict[str, Any],
        context: dict[str, Any],
        requesting_system: str,
    ) -> list[str]:
        """Generate recommendations based on ethical evaluation"""
        recommendations = []

        for principle, _severity in violations:
            if principle == EthicalPrinciple.PRESERVE_PRIVACY:
                recommendations.append("Consider anonymizing or aggregating data before processing")
                recommendations.append("Ensure data is processed on-device when possible")

            elif principle == EthicalPrinciple.DO_NO_HARM:
                recommendations.append("Add content warnings or safety filters")
                recommendations.append("Provide alternative options that minimize potential harm")

            elif principle == EthicalPrinciple.RESPECT_AUTONOMY:
                recommendations.append("Request explicit user consent before proceeding")
                recommendations.append("Provide clear opt-out mechanisms")

            elif principle == EthicalPrinciple.ENSURE_TRANSPARENCY:
                recommendations.append("Provide clear explanation of the action and its effects")
                recommendations.append("Make decision reasoning available to user")

        # System-specific recommendations
        if requesting_system == "NIAS":
            recommendations.append("Consider positive gating to ensure content aligns with user state")
        elif requesting_system == "DAST":
            recommendations.append("Verify task compatibility before execution")
        elif requesting_system == "ABAS":
            recommendations.append("Document conflict resolution reasoning for audit trail")

        return list(set(recommendations))  # Remove duplicates

    def _summarize_context(self, context: dict[str, Any]) -> dict[str, Any]:
        """Create a summary of relevant context"""
        return {
            "user_state": context.get("emotional_state", {}).get("summary", "unknown"),
            "environment": context.get("environment", "unknown"),
            "urgency": context.get("urgency", "normal"),
            "has_consent": bool(context.get("user_id")),
        }

    async def _log_decision(
        self,
        decision: EthicalDecision,
        action: dict[str, Any],
        context: dict[str, Any],
        requesting_system: str,
    ) -> None:
        """Log ethical decision for audit trail"""
        log_entry = {
            "timestamp": decision.timestamp.isoformat(),
            "requesting_system": requesting_system,
            "decision_type": decision.decision_type.value,
            "confidence": decision.confidence,
            "violations": [{"principle": p.name, "severity": s.name} for p, s in decision.violations],
            "action_summary": {
                "type": action.get("type", "unknown"),
                "data_involved": action.get("data_type", "none"),
            },
            "context_summary": self._summarize_context(context),
        }

        self.decision_history.append(log_entry)

        # Keep history size manageable
        if len(self.decision_history) > 10000:
            self.decision_history = self.decision_history[-5000:]

    async def create_ethical_symbol(self, decision: EthicalDecision) -> Symbol:
        """Create a symbolic representation of the ethical decision"""
        symbol = Symbol(
            id=f"ethics_{decision.timestamp.timestamp()}",
            domain=SymbolicDomain.ETHICS,
            type=SymbolicType.COMPOSITE,
            name=f"ethical_{decision.decision_type.value}",
            value=decision.decision_type == DecisionType.ALLOW,
        )

        # Add attributes
        symbol.add_attribute("confidence", decision.confidence)
        symbol.add_attribute(
            "severity",
            max(v[1].value for v in decision.violations) if decision.violations else 0,
        )
        symbol.add_attribute("principles", [p.name for p in decision.principles_considered])

        return symbol

    async def learn_from_outcome(self, decision_id: str, outcome: dict[str, Any]) -> None:
        """Learn from the outcome of an ethical decision"""
        # Find the decision in history
        for entry in reversed(self.decision_history):
            if entry.get("timestamp") == decision_id:
                entry["outcome"] = outcome

                # Adjust principle weights based on outcome
                if outcome.get("success", False):
                    # Successful outcome - slightly increase weights
                    for violation in entry.get("violations", []):
                        principle = EthicalPrinciple[violation["principle"]]
                        self.principle_weights[principle] *= 0.99  # Reduce strictness
                else:
                    # Negative outcome - increase weights
                    for violation in entry.get("violations", []):
                        principle = EthicalPrinciple[violation["principle"]]
                        self.principle_weights[principle] *= 1.01  # Increase strictness

                break

    def get_ethics_report(self) -> dict[str, Any]:
        """Generate a report of ethical decisions and patterns"""
        if not self.decision_history:
            return {"message": "No decisions recorded yet"}

        # Calculate statistics
        total_decisions = len(self.decision_history)
        decision_types = {}
        violation_counts = {}
        system_requests = {}

        for entry in self.decision_history:
            # Count decision types
            dt = entry["decision_type"]
            decision_types[dt] = decision_types.get(dt, 0) + 1

            # Count violations by principle
            for violation in entry.get("violations", []):
                principle = violation["principle"]
                violation_counts[principle] = violation_counts.get(principle, 0) + 1

            # Count by requesting system
            system = entry["requesting_system"]
            system_requests[system] = system_requests.get(system, 0) + 1

        return {
            "total_decisions": total_decisions,
            "decision_types": decision_types,
            "violation_counts": violation_counts,
            "system_requests": system_requests,
            "average_confidence": sum(e["confidence"] for e in self.decision_history) / total_decisions,
            "report_generated": datetime.now(timezone.utc).isoformat(),
        }

    async def health_check(self) -> dict[str, Any]:
        """Check health of the ethics engine"""
        return {
            "status": "healthy",
            "active_constraints": len([c for c in self.constraints.values() if c.active]),
            "total_constraints": len(self.constraints),
            "decision_history_size": len(self.decision_history),
            "seedra_connected": self.seedra is not None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# Singleton instance
_ethics_engine_instance = None


def get_shared_ethics_engine() -> SharedEthicsEngine:
    """Get or create shared ethics engine instance"""
    global _ethics_engine_instance
    if _ethics_engine_instance is None:
        _ethics_engine_instance = SharedEthicsEngine()
    return _ethics_engine_instance


__all__ = [
    "DecisionType",
    "EthicalConstraint",
    "EthicalDecision",
    "EthicalPrinciple",
    "EthicalSeverity",
    "SharedEthicsEngine",
    "get_shared_ethics_engine",
]