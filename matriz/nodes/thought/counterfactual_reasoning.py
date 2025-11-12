import time
from typing import Any, Dict, List, Tuple

from matriz.core.node_interface import CognitiveNode, NodeState


class CounterfactualReasoningNode(CognitiveNode):
    """
    Performs counterfactual reasoning to explore alternative scenarios and outcomes.
    This node conforms to the modern MATRIZ CognitiveNode interface.
    """

    def __init__(self, tenant: str = "default"):
        super().__init__(
            node_name="counterfactual_reasoning",
            capabilities=["counterfactual_analysis", "scenario_simulation", "what_if_reasoning"],
            tenant=tenant,
        )

    def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Reasons about alternative scenarios by applying an intervention to an actual scenario.

        Args:
            input_data: A dictionary containing:
                - 'actual_scenario': What actually happened.
                - 'intervention': What to change in the counterfactual.
                - 'causal_model': A model of causal relationships.

        Returns:
            A dictionary containing the answer, confidence, a MATRIZ node, and processing time.
        """
        start_time = time.time()

        actual = input_data.get("actual_scenario", {})
        intervention = input_data.get("intervention", {})
        causal_model = input_data.get("causal_model", {})
        trace_id = input_data.get("trace_id", self.get_deterministic_hash(input_data))

        if not actual or not intervention:
            confidence = 0.1
            answer = "Counterfactual reasoning requires an actual scenario and an intervention."
            state = NodeState(confidence=confidence, salience=0.3)
            matriz_node = self.create_matriz_node(
                node_type="DECISION",
                state=state,
                trace_id=trace_id,
                additional_data={"error": "Missing actual_scenario or intervention."}
            )
        else:
            scenarios = self._generate_scenarios(actual, intervention, causal_model)
            most_likely = max(scenarios, key=lambda s: s["likelihood"]) if scenarios else None
            insights = self._extract_insights(actual, scenarios, causal_model)

            confidence = most_likely["likelihood"] if most_likely else 0.2
            answer = f"Generated {len(scenarios)} counterfactual scenarios. The most likely outcome is '{most_likely['counterfactual_outcome']}'." if most_likely else "Could not generate any counterfactual scenarios."

            state = NodeState(confidence=confidence, salience=0.8, utility=0.7)
            matriz_node = self.create_matriz_node(
                node_type="HYPOTHESIS",
                state=state,
                trace_id=trace_id,
                additional_data={
                    "counterfactual_scenarios": scenarios,
                    "most_likely": most_likely,
                    "insights": insights,
                }
            )

        processing_time = time.time() - start_time

        return {
            "answer": answer,
            "confidence": confidence,
            "matriz_node": matriz_node,
            "processing_time": processing_time,
        }

    def validate_output(self, output: dict[str, Any]) -> bool:
        """Validates the output of the counterfactual reasoning node."""
        if not all(k in output for k in ["answer", "confidence", "matriz_node", "processing_time"]):
            return False
        if not (0 <= output["confidence"] <= 1):
            return False
        if not self.validate_matriz_node(output["matriz_node"]):
            return False
        return True

    def _generate_scenarios(self, actual: dict, intervention: dict, causal_model: dict) -> List[dict]:
        """Generates possible counterfactual scenarios."""
        original_outcome = actual.get("outcome", "unknown")
        modified_model = self._apply_intervention(causal_model, intervention)
        outcomes = self._simulate_outcomes(modified_model, actual, intervention)

        return [{
            "intervention": intervention.get("description", "unknown"),
            "original_outcome": original_outcome,
            "counterfactual_outcome": outcome,
            "likelihood": likelihood,
            "explanation": self._explain_difference(original_outcome, outcome, intervention)
        } for outcome, likelihood in outcomes]

    def _apply_intervention(self, causal_model: dict, intervention: dict) -> dict:
        """Applies an intervention to the causal model."""
        modified = causal_model.copy()
        var_name = intervention.get("variable")
        var_value = intervention.get("value")
        if var_name and "variables" in modified:
            modified["variables"][var_name] = var_value
        return modified

    def _simulate_outcomes(self, modified_model: dict, actual: dict, intervention: dict) -> List[Tuple[str, float]]:
        """Simulates possible outcomes given the modified model."""
        # Simplified placeholder logic
        outcomes = [
            (actual.get("outcome", "unknown"), 0.3),
            (f"{actual.get('outcome', 'unknown')}_modified", 0.6),
            ("unexpected_outcome", 0.1),
        ]
        return outcomes

    def _explain_difference(self, original: str, counterfactual: str, intervention: dict) -> str:
        """Explains why the outcomes differ."""
        if original == counterfactual:
            return "Intervention had no effect on the outcome."
        var_name = intervention.get("variable", "unknown")
        return f"Changing {var_name} altered the causal chain, leading to {counterfactual}."

    def _extract_insights(self, actual: dict, scenarios: List[dict], causal_model: dict) -> List[str]:
        """Extracts actionable insights from the counterfactual analysis."""
        insights = []
        original_outcome = actual.get("outcome", "unknown")
        better_scenarios = [s for s in scenarios if s["counterfactual_outcome"] != original_outcome and s["likelihood"] > 0.4]

        if better_scenarios:
            insights.append(f"Could have achieved a different outcome by: {better_scenarios[0]['intervention']}")

        insights.append("Critical factors: [would be extracted from causal model]")
        return insights
