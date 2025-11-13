#!/usr/bin/env python3
"""
MATRIZ Risk Assessment Node

Assesses and quantifies risks associated with decisions and actions.
Evaluates probability and impact of potential negative outcomes.

Example: "Action X has 30% risk of failure with high impact → Risk level: HIGH"
"""

import time
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List

from matriz.core.node_interface import CognitiveNode, NodeState, NodeTrigger


@dataclass
class RiskFactor:
    """A specific risk factor."""
    risk_id: str
    description: str
    probability: float  # 0.0 - 1.0
    impact: float  # 0.0 - 1.0
    severity: str  # low, medium, high, critical
    mitigation: str


class RiskAssessmentNode(CognitiveNode):
    """
    Assesses risks for decisions and actions.

    Capabilities:
    - Risk identification
    - Probability estimation
    - Impact assessment
    - Severity classification
    """

    def __init__(self, tenant: str = "default"):
        super().__init__(
            node_name="matriz_risk_assessment",
            capabilities=[
                "risk_identification",
                "probability_estimation",
                "impact_assessment",
                "governed_trace"
            ],
            tenant=tenant
        )

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess risks.

        Args:
            input_data: Dict containing:
                - decision: Decision or action to assess
                - context: Current context and constraints
                - historical_data: Past outcomes for similar decisions
                - risk_tolerance: Acceptable risk level

        Returns:
            Dict with risk factors, overall risk level, and MATRIZ node
        """
        start_time = time.time()

        decision = input_data.get("decision", {})
        context = input_data.get("context", {})
        historical_data = input_data.get("historical_data", [])
        risk_tolerance = input_data.get("risk_tolerance", 0.5)

        # Identify risk factors
        risk_factors = self._identify_risks(
            decision,
            context,
            historical_data
        )

        # Calculate overall risk
        overall_risk = self._calculate_overall_risk(risk_factors)

        # Determine risk level
        risk_level = self._classify_risk_level(overall_risk)

        # Check if acceptable
        acceptable = overall_risk <= risk_tolerance

        # Generate recommendations
        recommendations = self._generate_recommendations(risk_factors, risk_tolerance)

        # Compute confidence
        confidence = self._compute_confidence(risk_factors, historical_data)

        # Create NodeState
        state = NodeState(
            confidence=confidence,
            salience=min(1.0, 0.7 + overall_risk * 0.3),
            novelty=max(0.1, 0.4),
            utility=min(1.0, 0.5 + (1.0 - overall_risk) * 0.5),
            risk=overall_risk
        )

        # Create trigger
        trigger = NodeTrigger(
            event_type="risk_assessment_request",
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
                "risk_factor_count": len(risk_factors)
            },
            "risk_factors": [
                {
                    "risk_id": r.risk_id,
                    "description": r.description,
                    "probability": r.probability,
                    "impact": r.impact,
                    "severity": r.severity,
                    "mitigation": r.mitigation
                }
                for r in risk_factors
            ],
            "overall_risk": overall_risk,
            "risk_level": risk_level,
            "acceptable": acceptable,
            "recommendations": recommendations
        }

        return {
            "answer": {
                "risk_factors": matriz_node["risk_factors"],
                "overall_risk": overall_risk,
                "risk_level": risk_level,
                "acceptable": acceptable,
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

        return "risk_factors" in output["answer"]

    def _identify_risks(
        self,
        decision: dict,
        context: dict,
        historical_data: List[dict]
    ) -> List[RiskFactor]:
        """Identify risk factors for decision."""
        risk_factors = []

        # Extract explicit risks from decision
        explicit_risks = decision.get("risks", [])

        for i, risk in enumerate(explicit_risks):
            risk_id = risk.get("id", f"risk_{i}")
            description = risk.get("description", f"Risk {i}")
            probability = risk.get("probability", 0.3)
            impact = risk.get("impact", 0.5)

            severity = self._classify_severity(probability, impact)
            mitigation = risk.get("mitigation", "No mitigation specified")

            risk_factors.append(
                RiskFactor(
                    risk_id=risk_id,
                    description=description,
                    probability=probability,
                    impact=impact,
                    severity=severity,
                    mitigation=mitigation
                )
            )

        # Infer risks from context
        inferred_risks = self._infer_contextual_risks(decision, context)
        risk_factors.extend(inferred_risks)

        # Learn from historical data
        if historical_data:
            historical_risks = self._learn_from_history(decision, historical_data)
            risk_factors.extend(historical_risks)

        return risk_factors

    def _classify_severity(self, probability: float, impact: float) -> str:
        """Classify risk severity based on probability and impact."""
        risk_score = probability * impact

        if risk_score >= 0.7:
            return "critical"
        elif risk_score >= 0.5:
            return "high"
        elif risk_score >= 0.3:
            return "medium"
        else:
            return "low"

    def _infer_contextual_risks(
        self,
        decision: dict,
        context: dict
    ) -> List[RiskFactor]:
        """Infer risks from context."""
        risks = []

        # Resource constraints
        if context.get("resource_limited"):
            risks.append(
                RiskFactor(
                    risk_id="resource_constraint",
                    description="Resource constraints may cause failure",
                    probability=0.4,
                    impact=0.6,
                    severity="medium",
                    mitigation="Secure additional resources or reduce scope"
                )
            )

        # Time pressure
        if context.get("time_critical"):
            risks.append(
                RiskFactor(
                    risk_id="time_pressure",
                    description="Time pressure may compromise quality",
                    probability=0.5,
                    impact=0.5,
                    severity="medium",
                    mitigation="Extend deadline or prioritize essential features"
                )
            )

        # Complexity
        complexity = decision.get("complexity", 0.5)
        if complexity > 0.7:
            risks.append(
                RiskFactor(
                    risk_id="high_complexity",
                    description="High complexity increases failure risk",
                    probability=0.6,
                    impact=0.7,
                    severity="high",
                    mitigation="Break down into simpler sub-tasks"
                )
            )

        return risks

    def _learn_from_history(
        self,
        decision: dict,
        historical_data: List[dict]
    ) -> List[RiskFactor]:
        """Learn risk patterns from historical data."""
        risks = []

        # Count failures in similar decisions
        similar = [h for h in historical_data if self._is_similar(decision, h)]

        if similar:
            failures = sum(1 for h in similar if h.get("outcome") == "failure")
            failure_rate = failures / len(similar)

            if failure_rate > 0.3:
                risks.append(
                    RiskFactor(
                        risk_id="historical_failure",
                        description=f"Historical failure rate: {int(failure_rate * 100)}%",
                        probability=failure_rate,
                        impact=0.8,
                        severity=self._classify_severity(failure_rate, 0.8),
                        mitigation="Review past failures and apply lessons learned"
                    )
                )

        return risks

    def _is_similar(self, decision1: dict, decision2: dict) -> bool:
        """Check if two decisions are similar."""
        # Simplified similarity check
        type1 = decision1.get("type", "")
        type2 = decision2.get("type", "")

        return type1 == type2

    def _calculate_overall_risk(self, risk_factors: List[RiskFactor]) -> float:
        """Calculate overall risk from individual factors."""
        if not risk_factors:
            return 0.0

        # Combine risks using probability theory
        # Overall risk is NOT simply average - risks compound

        # Start with complement of no-risk
        no_risk_prob = 1.0

        for risk in risk_factors:
            # Probability this specific risk occurs
            risk_occurs = risk.probability * risk.impact

            # Update overall no-risk probability
            no_risk_prob *= (1.0 - risk_occurs)

        # Overall risk is complement of no-risk
        overall_risk = 1.0 - no_risk_prob

        return min(1.0, overall_risk)

    def _classify_risk_level(self, overall_risk: float) -> str:
        """Classify overall risk level."""
        if overall_risk >= 0.7:
            return "CRITICAL"
        elif overall_risk >= 0.5:
            return "HIGH"
        elif overall_risk >= 0.3:
            return "MEDIUM"
        else:
            return "LOW"

    def _generate_recommendations(
        self,
        risk_factors: List[RiskFactor],
        risk_tolerance: float
    ) -> List[str]:
        """Generate risk mitigation recommendations."""
        recommendations = []

        # Prioritize high-severity risks
        high_risks = [r for r in risk_factors if r.severity in ["high", "critical"]]

        for risk in high_risks:
            if risk.mitigation:
                recommendations.append(risk.mitigation)

        # General recommendations
        if not recommendations:
            recommendations.append("Monitor execution closely")
            recommendations.append("Prepare contingency plans")

        return recommendations

    def _compute_confidence(
        self,
        risk_factors: List[RiskFactor],
        historical_data: List[dict]
    ) -> float:
        """Compute confidence in risk assessment."""
        # More data = higher confidence

        # Base confidence from risk factor clarity
        base_confidence = min(1.0, 0.5 + len(risk_factors) * 0.1)

        # Boost from historical data
        history_boost = min(0.3, len(historical_data) * 0.05)

        return min(1.0, base_confidence + history_boost)
