#!/usr/bin/env python3
"""
MATRIZ Abductive Reasoning Node

Performs abductive reasoning: inference to the best explanation.
Given observations, generates and evaluates candidate explanations.

Example: "The grass is wet. Best explanation: it rained last night"
"""

import time
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List

from matriz.core.node_interface import CognitiveNode, NodeState, NodeTrigger


@dataclass
class Explanation:
    """A candidate explanation for observations."""
    hypothesis: str
    explains: List[str]  # Observations explained
    plausibility: float  # 0.0 - 1.0
    simplicity: float  # 0.0 - 1.0 (prefer simpler)
    score: float  # Overall score


class AbductiveReasoningNode(CognitiveNode):
    """
    Performs abductive reasoning: inference to the best explanation.

    Capabilities:
    - Candidate explanation generation
    - Explanation evaluation
    - Plausibility assessment
    - Simplicity scoring (Occam's razor)
    """

    def __init__(self, tenant: str = "default"):
        super().__init__(
            node_name="matriz_abductive_reasoning",
            capabilities=[
                "explanation_generation",
                "hypothesis_evaluation",
                "best_explanation_selection",
                "governed_trace"
            ],
            tenant=tenant
        )

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform abductive reasoning.

        Args:
            input_data: Dict containing:
                - observations: List of observed facts
                - background_knowledge: Domain knowledge
                - explanation_constraints: Constraints on explanations

        Returns:
            Dict with best explanation, alternatives, and MATRIZ node
        """
        start_time = time.time()

        observations = input_data.get("observations", [])
        background = input_data.get("background_knowledge", {})
        constraints = input_data.get("explanation_constraints", {})

        # Generate candidate explanations
        candidates = self._generate_candidates(observations, background)

        # Evaluate explanations
        explanations = self._evaluate_explanations(
            candidates,
            observations,
            background,
            constraints
        )

        # Rank by score
        explanations.sort(key=lambda e: e.score, reverse=True)

        # Select best
        best = explanations[0] if explanations else None

        # Compute confidence
        confidence = self._compute_confidence(explanations)

        # Create NodeState
        state = NodeState(
            confidence=confidence,
            salience=min(1.0, 0.6 + (best.score if best else 0) * 0.4),
            novelty=max(0.1, 1.0 - confidence),
            utility=min(1.0, 0.7 + confidence / 2)
        )

        # Create trigger
        trigger = NodeTrigger(
            event_type="abductive_reasoning_request",
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
                "observation_count": len(observations),
                "candidate_count": len(explanations)
            },
            "best_explanation": {
                "hypothesis": best.hypothesis,
                "explains": best.explains,
                "plausibility": best.plausibility,
                "simplicity": best.simplicity,
                "score": best.score
            } if best else None,
            "alternative_explanations": [
                {
                    "hypothesis": e.hypothesis,
                    "score": e.score
                }
                for e in explanations[1:6]  # Top 5 alternatives
            ]
        }

        return {
            "answer": {
                "best_explanation": matriz_node["best_explanation"],
                "alternative_explanations": matriz_node["alternative_explanations"]
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

        return "best_explanation" in output["answer"]

    def _generate_candidates(
        self,
        observations: List[str],
        background: dict
    ) -> List[str]:
        """Generate candidate explanations."""
        candidates = []

        # Generate from background knowledge patterns
        for pattern in background.get("patterns", []):
            if self._matches_observations(pattern, observations):
                candidates.append(pattern.get("explanation", ""))

        # Generate from observation combinations
        if len(observations) >= 2:
            candidates.append(f"Common cause of: {', '.join(observations[:2])}")

        # Generate simple direct explanations
        for obs in observations:
            candidates.append(f"Direct cause: {obs}")

        # Remove empty candidates
        return [c for c in candidates if c]

    def _matches_observations(self, pattern: dict, observations: List[str]) -> bool:
        """Check if pattern matches observations."""
        required = pattern.get("requires", [])
        if not required:
            return False
        return any(obs in observations for obs in required)

    def _evaluate_explanations(
        self,
        candidates: List[str],
        observations: List[str],
        background: dict,
        constraints: dict
    ) -> List[Explanation]:
        """Evaluate candidate explanations."""
        explanations = []

        for hypothesis in candidates:
            # How many observations does it explain?
            explains = self._observations_explained(hypothesis, observations, background)

            # How plausible is it?
            plausibility = self._assess_plausibility(hypothesis, background)

            # How simple is it?
            simplicity = self._assess_simplicity(hypothesis)

            # Overall score (weighted combination)
            score = (
                0.5 * (len(explains) / max(1, len(observations)))  # Coverage
                + 0.3 * plausibility
                + 0.2 * simplicity
            )

            explanations.append(
                Explanation(
                    hypothesis=hypothesis,
                    explains=explains,
                    plausibility=plausibility,
                    simplicity=simplicity,
                    score=score
                )
            )

        return explanations

    def _observations_explained(
        self,
        hypothesis: str,
        observations: List[str],
        background: dict
    ) -> List[str]:
        """Determine which observations are explained by hypothesis."""
        explained = []
        for obs in observations:
            # Check if observation keywords in hypothesis
            if any(word in hypothesis.lower() for word in obs.lower().split()):
                explained.append(obs)
        return explained

    def _assess_plausibility(self, hypothesis: str, background: dict) -> float:
        """Assess how plausible explanation is given background knowledge."""
        # Check if hypothesis aligns with known patterns
        for pattern in background.get("patterns", []):
            if hypothesis in pattern.get("explanation", ""):
                return 0.9  # High plausibility

        # Check for implausible keywords
        implausible_keywords = ["magic", "miracle", "impossible"]
        if any(kw in hypothesis.lower() for kw in implausible_keywords):
            return 0.1

        # Default moderate plausibility
        return 0.5

    def _assess_simplicity(self, hypothesis: str) -> float:
        """Assess simplicity (prefer Occam's razor)."""
        # Simpler = fewer assumptions = shorter description
        max_len = 200
        base_score = max(0.0, 1.0 - len(hypothesis) / max_len)

        # Penalty for complex conjunctions
        and_count = hypothesis.lower().count(" and ")
        or_count = hypothesis.lower().count(" or ")
        complexity_penalty = min(0.3, (and_count + or_count) * 0.1)

        return max(0.0, base_score - complexity_penalty)

    def _compute_confidence(self, explanations: List[Explanation]) -> float:
        """Compute confidence in best explanation."""
        if not explanations:
            return 0.0

        # High confidence if best explanation much better than alternatives
        best_score = explanations[0].score
        second_best_score = explanations[1].score if len(explanations) > 1 else 0.0

        gap = best_score - second_best_score

        return min(1.0, best_score + gap * 0.5)
