#!/usr/bin/env python3
"""
MATRIZ Counterfactual Reasoning Node

Performs counterfactual reasoning: "What if X had been different?"
Useful for understanding causality, planning, and learning from mistakes.

Example: "If I had taken the earlier train, I would have arrived on time"
"""

import time
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from matriz.core.node_interface import CognitiveNode, NodeState, NodeTrigger


@dataclass
class CounterfactualScenario:
    """A counterfactual 'what if' scenario."""
    intervention: str  # What we change
    original_outcome: str
    counterfactual_outcome: str
    likelihood: float  # How likely this outcome is
    explanation: str


class CounterfactualReasoningNode(CognitiveNode):
    """
    Performs counterfactual reasoning: exploring alternative scenarios.

    Capabilities:
    - Scenario generation
    - Outcome simulation
    - Causal model intervention
    - Insight extraction
    """

    def __init__(self, tenant: str = "default"):
        super().__init__(
            node_name="matriz_counterfactual_reasoning",
            capabilities=[
                "counterfactual_simulation",
                "alternative_outcomes",
                "causal_intervention",
                "governed_trace"
            ],
            tenant=tenant
        )

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform counterfactual reasoning.

        Args:
            input_data: Dict containing:
                - actual_scenario: What actually happened
                - intervention: What to change in counterfactual
                - causal_model: Model of causal relationships

        Returns:
            Dict with counterfactual scenarios, insights, and MATRIZ node
        """
        start_time = time.time()

        actual = input_data.get("actual_scenario", {})
        intervention = input_data.get("intervention", {})
        causal_model = input_data.get("causal_model", {})

        # Generate counterfactual scenarios
        scenarios = self._generate_scenarios(actual, intervention, causal_model)

        # Find most likely alternative
        most_likely = max(scenarios, key=lambda s: s.likelihood) if scenarios else None

        # Extract insights
        insights = self._extract_insights(actual, scenarios, causal_model)

        # Compute confidence
        confidence = self._compute_confidence(scenarios)

        # Create NodeState
        state = NodeState(
            confidence=confidence,
            salience=min(1.0, 0.6 + 0.1 * len(scenarios)),
            novelty=min(1.0, 0.7 + len(scenarios) * 0.1),
            utility=min(1.0, 0.7 + len(insights) * 0.1)
        )

        # Create trigger
        trigger = NodeTrigger(
            event_type="counterfactual_reasoning_request",
            timestamp=int(time.time() * 1000)
        )

        # Build MATRIZ node
        matriz_node = {
            "id": str(uuid.uuid4()),
            "type": "HYPOTHESIS",
            "state": {
                "confidence": state.confidence,
                "salience": state.salience,
                "novelty": state.novelty,
                "utility": state.utility
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
                "scenario_count": len(scenarios)
            },
            "counterfactual_scenarios": [
                {
                    "intervention": s.intervention,
                    "original_outcome": s.original_outcome,
                    "counterfactual_outcome": s.counterfactual_outcome,
                    "likelihood": s.likelihood,
                    "explanation": s.explanation
                }
                for s in scenarios
            ],
            "most_likely": {
                "outcome": most_likely.counterfactual_outcome,
                "likelihood": most_likely.likelihood,
                "explanation": most_likely.explanation
            } if most_likely else None,
            "insights": insights
        }

        return {
            "answer": {
                "counterfactual_scenarios": matriz_node["counterfactual_scenarios"],
                "most_likely": matriz_node["most_likely"],
                "insights": insights
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

        if "counterfactual_scenarios" not in output["answer"]:
            return False

        return True

    def _generate_scenarios(
        self,
        actual: dict,
        intervention: dict,
        causal_model: dict
    ) -> List[CounterfactualScenario]:
        """Generate possible counterfactual scenarios."""
        scenarios = []

        # Get actual outcome
        original_outcome = actual.get("outcome", "unknown")

        # Apply intervention to causal model
        modified_model = self._apply_intervention(causal_model, intervention)

        # Simulate alternative outcomes
        outcomes = self._simulate_outcomes(modified_model, actual, intervention)

        for outcome, likelihood in outcomes:
            scenarios.append(
                CounterfactualScenario(
                    intervention=intervention.get("description", "unknown"),
                    original_outcome=original_outcome,
                    counterfactual_outcome=outcome,
                    likelihood=likelihood,
                    explanation=self._explain_difference(
                        original_outcome,
                        outcome,
                        intervention
                    )
                )
            )

        return scenarios

    def _apply_intervention(self, causal_model: dict, intervention: dict) -> dict:
        """Apply intervention to causal model."""
        # Create modified copy
        modified = causal_model.copy()

        # Update specified variables
        var_name = intervention.get("variable")
        var_value = intervention.get("value")

        if var_name and "variables" in modified:
            modified["variables"][var_name] = var_value

        return modified

    def _simulate_outcomes(
        self,
        modified_model: dict,
        actual: dict,
        intervention: dict
    ) -> List[Tuple[str, float]]:
        """Simulate possible outcomes given modified model."""
        outcomes = []

        original_outcome = actual.get("outcome", "unknown")

        # Original outcome (lower likelihood due to intervention)
        outcomes.append((original_outcome, 0.3))

        # Alternative outcome based on intervention
        var_name = intervention.get("variable", "X")
        var_value = intervention.get("value", "changed")
        alt_outcome = f"{original_outcome}_with_{var_name}={var_value}"
        outcomes.append((alt_outcome, 0.6))

        # Unexpected outcome (lower likelihood)
        outcomes.append(("unexpected_outcome", 0.1))

        return outcomes

    def _explain_difference(
        self,
        original: str,
        counterfactual: str,
        intervention: dict
    ) -> str:
        """Explain why outcomes differ."""
        if original == counterfactual:
            return "Intervention had no effect on outcome"

        var_name = intervention.get("variable", "unknown")
        return f"Changing {var_name} altered the causal chain, leading to {counterfactual}"

    def _extract_insights(
        self,
        actual: dict,
        scenarios: List[CounterfactualScenario],
        causal_model: dict
    ) -> List[str]:
        """Extract actionable insights from counterfactual analysis."""
        insights = []

        # Find scenarios with different outcomes
        original_outcome = actual.get("outcome", "unknown")
        different_scenarios = [
            s for s in scenarios
            if s.counterfactual_outcome != original_outcome
            and s.likelihood > 0.4
        ]

        if different_scenarios:
            insights.append(
                f"Could have achieved different outcome by: {different_scenarios[0].intervention}"
            )

        # Identify critical decision points
        if causal_model.get("variables"):
            critical_vars = list(causal_model["variables"].keys())[:2]
            insights.append(f"Critical factors: {', '.join(critical_vars)}")

        # General learning
        insights.append("Counterfactual analysis reveals alternative possibilities")

        return insights

    def _compute_confidence(self, scenarios: List[CounterfactualScenario]) -> float:
        """Compute overall confidence in counterfactual analysis."""
        if not scenarios:
            return 0.0

        # Average likelihood across scenarios
        avg_likelihood = sum(s.likelihood for s in scenarios) / len(scenarios)

        # Boost if we have diverse scenarios
        diversity_boost = min(0.2, len(scenarios) * 0.05)

        return min(1.0, avg_likelihood + diversity_boost)
