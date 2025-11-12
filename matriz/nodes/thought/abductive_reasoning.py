import time
from typing import Any, Dict, List

from matriz.core.node_interface import CognitiveNode, NodeState


class AbductiveReasoningNode(CognitiveNode):
    """
    Performs abductive reasoning to find the best explanation for a set of observations.
    This node conforms to the modern MATRIZ CognitiveNode interface.
    """

    def __init__(self, tenant: str = "default"):
        super().__init__(
            node_name="abductive_reasoning",
            capabilities=["abductive_inference", "explanation_generation", "hypothesis_evaluation"],
            tenant=tenant,
        )

    def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Infers the best explanation for a given set of observations.

        Args:
            input_data: A dictionary containing:
                - 'observations': A list of observed facts.
                - 'background_knowledge': Domain knowledge.
                - 'explanation_constraints': Constraints on the explanations.

        Returns:
            A dictionary containing the answer, confidence, a MATRIZ node, and processing time.
        """
        start_time = time.time()

        observations = input_data.get("observations", [])
        background = input_data.get("background_knowledge", {})
        constraints = input_data.get("explanation_constraints", {})
        trace_id = input_data.get("trace_id", self.get_deterministic_hash(input_data))

        if not observations:
            confidence = 0.1
            answer = "Abductive reasoning requires a list of observations to explain."
            state = NodeState(confidence=confidence, salience=0.3)
            matriz_node = self.create_matriz_node(
                node_type="DECISION",
                state=state,
                trace_id=trace_id,
                additional_data={"error": "Missing observations list."}
            )
        else:
            candidates = self._generate_candidates(observations, background)
            explanations = self._evaluate_explanations(candidates, observations, background, constraints)
            explanations.sort(key=lambda e: e["score"], reverse=True)
            best = explanations[0] if explanations else None

            confidence = self._compute_confidence(explanations)
            answer = f"The best explanation is: {best['hypothesis']}" if best else "No plausible explanation found."

            state = NodeState(confidence=confidence, salience=0.9, utility=0.8)
            matriz_node = self.create_matriz_node(
                node_type="HYPOTHESIS",
                state=state,
                trace_id=trace_id,
                additional_data={
                    "best_explanation": best,
                    "alternative_explanations": explanations[1:6],
                    "observation_count": len(observations),
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
        """Validates the output of the abductive reasoning node."""
        if not all(k in output for k in ["answer", "confidence", "matriz_node", "processing_time"]):
            return False
        if not (0 <= output["confidence"] <= 1):
            return False
        if not self.validate_matriz_node(output["matriz_node"]):
            return False
        return True

    def _generate_candidates(self, observations: List[str], background: dict) -> List[tuple[str, list[str]]]:
        """Generates candidate explanations and the observations they explain."""
        candidates = []
        for pattern in background.get("patterns", []):
            if self._matches_observations(pattern, observations):
                # The pattern explains the observations it requires
                candidates.append((pattern["explanation"], pattern.get("requires", [])))
        if len(observations) >= 2:
            # The generic "common cause" explains the first two observations
            explained_by_common_cause = observations[:2]
            candidates.append((f"Common cause of: {', '.join(explained_by_common_cause)}", explained_by_common_cause))
        return candidates

    def _matches_observations(self, pattern: dict, observations: List[str]) -> bool:
        """Checks if a pattern matches the observations."""
        return all(obs in observations for obs in pattern.get("requires", []))

    def _evaluate_explanations(self, candidates: List[tuple[str, list[str]]], observations: List[str], background: dict, constraints: dict) -> List[dict]:
        """Evaluates the candidate explanations."""
        explanations = []
        for hypothesis, explains in candidates:
            plausibility = self._assess_plausibility(hypothesis, background)
            simplicity = self._assess_simplicity(hypothesis)
            # Use the pre-determined explained observations for score calculation
            score = (0.5 * (len(explains) / max(1, len(observations))) + 0.3 * plausibility + 0.2 * simplicity)

            explanations.append({
                "hypothesis": hypothesis,
                "explains": explains,
                "plausibility": plausibility,
                "simplicity": simplicity,
                "score": score,
            })
        return explanations

    def _assess_plausibility(self, hypothesis: str, background: dict) -> float:
        """Assesses the plausibility of a hypothesis."""
        for pattern in background.get("patterns", []):
            if hypothesis in pattern.get("explanation", ""):
                return 0.9
        return 0.5

    def _assess_simplicity(self, hypothesis: str) -> float:
        """Assesses the simplicity of a hypothesis."""
        return max(0.0, 1.0 - len(hypothesis) / 200)

    def _compute_confidence(self, explanations: List[dict]) -> float:
        """Computes the confidence in the best explanation."""
        if not explanations:
            return 0.0
        best_score = explanations[0]["score"]
        second_best_score = explanations[1]["score"] if len(explanations) > 1 else 0.0
        gap = best_score - second_best_score
        return min(1.0, best_score + gap * 0.5)
