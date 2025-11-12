#!/usr/bin/env python3
"""
MATRIZ Ethical Constraint Node

Enforces ethical constraints on decisions and actions.
Evaluates decisions against ethical principles and values.

Example: "Action violates privacy principle → BLOCKED by ethical constraint"
"""

import time
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List

from matriz.core.node_interface import CognitiveNode, NodeState, NodeTrigger


@dataclass
class EthicalViolation:
    """An ethical constraint violation."""
    violation_id: str
    principle: str
    description: str
    severity: str  # minor, moderate, major, critical
    recommendation: str


class EthicalConstraintNode(CognitiveNode):
    """
    Enforces ethical constraints on decisions.

    Capabilities:
    - Ethical principle checking
    - Violation detection
    - Severity assessment
    - Recommendation generation
    """

    def __init__(self, tenant: str = "default"):
        super().__init__(
            node_name="matriz_ethical_constraint",
            capabilities=[
                "ethical_validation",
                "principle_checking",
                "violation_detection",
                "governed_trace"
            ],
            tenant=tenant
        )

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check ethical constraints.

        Args:
            input_data: Dict containing:
                - decision: Decision or action to evaluate
                - ethical_principles: List of ethical principles to check
                - context: Contextual information
                - stakeholders: Affected stakeholders

        Returns:
            Dict with violations, approval status, and MATRIZ node
        """
        start_time = time.time()

        decision = input_data.get("decision", {})
        ethical_principles = input_data.get("ethical_principles", self._default_principles())
        context = input_data.get("context", {})
        stakeholders = input_data.get("stakeholders", [])

        # Check each ethical principle
        violations = self._check_ethical_principles(
            decision,
            ethical_principles,
            context,
            stakeholders
        )

        # Determine approval status
        approved = self._determine_approval(violations)

        # Calculate ethical score
        ethical_score = self._calculate_ethical_score(violations)

        # Generate recommendations
        recommendations = self._generate_recommendations(violations)

        # Compute confidence
        confidence = self._compute_confidence(ethical_principles)

        # Create NodeState
        state = NodeState(
            confidence=confidence,
            salience=min(1.0, 0.9 + len(violations) * 0.02),
            novelty=max(0.1, len(violations) * 0.15),
            utility=ethical_score,
            risk=min(1.0, len(violations) * 0.25)
        )

        # Create trigger
        trigger = NodeTrigger(
            event_type="ethical_constraint_check",
            timestamp=int(time.time() * 1000)
        )

        # Build MATRIZ node
        matriz_node = {
            "id": str(uuid.uuid4()),
            "type": "DECISION",
            "state": {
                "confidence": state.confidence,
                "salience": state.salience,
                "novelty": state.novelty,
                "utility": state.utility,
                "risk": state.risk
            },
            "triggers": [{
                "event_type": trigger.event_type,
                "timestamp": trigger.timestamp
            }],
            "metadata": {
                "node_name": self.node_name,
                "tenant": self.tenant,
                "capabilities": self.capabilities,
                "processing_time": time.time() - start_time,
                "violation_count": len(violations)
            },
            "violations": [
                {
                    "violation_id": v.violation_id,
                    "principle": v.principle,
                    "description": v.description,
                    "severity": v.severity,
                    "recommendation": v.recommendation
                }
                for v in violations
            ],
            "approved": approved,
            "ethical_score": ethical_score,
            "recommendations": recommendations
        }

        return {
            "answer": {
                "violations": matriz_node["violations"],
                "approved": approved,
                "ethical_score": ethical_score,
                "recommendations": recommendations
            },
            "confidence": confidence,
            "matriz_node": matriz_node,
            "processing_time": time.time() - start_time
        }

    def validate_output(self, output: Dict[str, Any]) -> bool:
        """Validate output structure."""
        required = ["answer", "confidence", "matriz_node", "processing_time"]
        if not all(k in output for k in required):
            return False

        if not 0.0 <= output["confidence"] <= 1.0:
            return False

        if "approved" not in output["answer"]:
            return False

        return True

    def _default_principles(self) -> List[dict]:
        """Default ethical principles to check."""
        return [
            {
                "name": "autonomy",
                "description": "Respect individual autonomy and consent",
                "priority": "high"
            },
            {
                "name": "beneficence",
                "description": "Act in the best interest of stakeholders",
                "priority": "high"
            },
            {
                "name": "non_maleficence",
                "description": "Do no harm",
                "priority": "critical"
            },
            {
                "name": "justice",
                "description": "Ensure fairness and equity",
                "priority": "high"
            },
            {
                "name": "privacy",
                "description": "Protect personal information and privacy",
                "priority": "high"
            },
            {
                "name": "transparency",
                "description": "Maintain transparency and explainability",
                "priority": "medium"
            }
        ]

    def _check_ethical_principles(
        self,
        decision: dict,
        ethical_principles: List[dict],
        context: dict,
        stakeholders: List[dict]
    ) -> List[EthicalViolation]:
        """Check decision against ethical principles."""
        violations = []

        for principle in ethical_principles:
            principle_name = principle.get("name", "")
            violation = self._check_principle(
                decision,
                principle,
                context,
                stakeholders
            )

            if violation:
                violations.append(violation)

        return violations

    def _check_principle(
        self,
        decision: dict,
        principle: dict,
        context: dict,
        stakeholders: List[dict]
    ) -> EthicalViolation:
        """Check a specific ethical principle."""
        principle_name = principle.get("name", "")

        # Check autonomy
        if principle_name == "autonomy":
            if not decision.get("consent_obtained", True):
                return EthicalViolation(
                    violation_id=f"violation_{principle_name}",
                    principle="Autonomy",
                    description="Decision made without stakeholder consent",
                    severity="major",
                    recommendation="Obtain explicit consent from affected parties"
                )

        # Check non-maleficence (do no harm)
        elif principle_name == "non_maleficence":
            harmful_effects = decision.get("harmful_effects", [])
            if harmful_effects:
                return EthicalViolation(
                    violation_id=f"violation_{principle_name}",
                    principle="Non-maleficence",
                    description=f"Decision may cause harm: {', '.join(harmful_effects)}",
                    severity="critical",
                    recommendation="Eliminate or mitigate harmful effects"
                )

        # Check justice/fairness
        elif principle_name == "justice":
            if decision.get("discriminatory", False):
                return EthicalViolation(
                    violation_id=f"violation_{principle_name}",
                    principle="Justice",
                    description="Decision may discriminate against certain groups",
                    severity="major",
                    recommendation="Ensure fair treatment of all stakeholders"
                )

        # Check privacy
        elif principle_name == "privacy":
            if decision.get("privacy_risk", False):
                return EthicalViolation(
                    violation_id=f"violation_{principle_name}",
                    principle="Privacy",
                    description="Decision poses privacy risks",
                    severity="major",
                    recommendation="Implement privacy protections and safeguards"
                )

        # Check beneficence (benefit stakeholders)
        elif principle_name == "beneficence":
            stakeholder_benefit = decision.get("stakeholder_benefit", 0.5)
            if stakeholder_benefit < 0.3:
                return EthicalViolation(
                    violation_id=f"violation_{principle_name}",
                    principle="Beneficence",
                    description="Decision provides insufficient benefit to stakeholders",
                    severity="moderate",
                    recommendation="Increase stakeholder benefits or reconsider decision"
                )

        # Check transparency
        elif principle_name == "transparency":
            if not decision.get("explainable", True):
                return EthicalViolation(
                    violation_id=f"violation_{principle_name}",
                    principle="Transparency",
                    description="Decision lacks transparency and explainability",
                    severity="moderate",
                    recommendation="Provide clear explanation and reasoning"
                )

        return None

    def _determine_approval(self, violations: List[EthicalViolation]) -> bool:
        """Determine if decision is ethically approved."""
        # Block if any critical violations
        critical = [v for v in violations if v.severity == "critical"]
        if critical:
            return False

        # Block if multiple major violations
        major = [v for v in violations if v.severity == "major"]
        if len(major) >= 2:
            return False

        # Approve otherwise
        return True

    def _calculate_ethical_score(self, violations: List[EthicalViolation]) -> float:
        """Calculate overall ethical score."""
        if not violations:
            return 1.0

        # Severity weights
        severity_weights = {
            "minor": 0.1,
            "moderate": 0.2,
            "major": 0.4,
            "critical": 0.6
        }

        # Calculate penalty
        total_penalty = sum(
            severity_weights.get(v.severity, 0.3)
            for v in violations
        )

        # Ethical score is 1.0 minus penalties
        return max(0.0, 1.0 - total_penalty)

    def _generate_recommendations(
        self,
        violations: List[EthicalViolation]
    ) -> List[str]:
        """Generate ethical recommendations."""
        if not violations:
            return ["Decision is ethically sound"]

        recommendations = []

        # Add specific recommendations from violations
        for violation in violations:
            recommendations.append(violation.recommendation)

        # Add general guidance
        if len(violations) >= 3:
            recommendations.append("Consider alternative decisions with fewer ethical concerns")

        return recommendations

    def _compute_confidence(self, ethical_principles: List[dict]) -> float:
        """Compute confidence in ethical assessment."""
        # More principles checked = higher confidence
        base_confidence = min(1.0, 0.6 + len(ethical_principles) * 0.08)

        return base_confidence
