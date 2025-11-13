#!/usr/bin/env python3
"""
MATRIZ Action Selection Node

Selects the best action from a set of candidate actions.
Uses utility maximization and constraint satisfaction.

Example: "Given options [walk, drive, bike], select drive (fastest)"
"""

import time
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List

from matriz.core.node_interface import CognitiveNode, NodeState, NodeTrigger


@dataclass
class ActionCandidate:
    """A candidate action with evaluation scores."""
    action_id: str
    description: str
    utility: float  # Expected utility (0.0 - 1.0)
    feasibility: float  # How feasible (0.0 - 1.0)
    risk: float  # Risk level (0.0 - 1.0)
    score: float  # Overall score


class ActionSelectionNode(CognitiveNode):
    """
    Selects best action from candidate actions.

    Capabilities:
    - Utility assessment
    - Feasibility evaluation
    - Risk analysis
    - Multi-criteria scoring
    """

    def __init__(self, tenant: str = "default"):
        super().__init__(
            node_name="matriz_action_selection",
            capabilities=[
                "action_evaluation",
                "utility_assessment",
                "risk_analysis",
                "governed_trace"
            ],
            tenant=tenant
        )

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Select best action.

        Args:
            input_data: Dict containing:
                - candidate_actions: List of possible actions
                - current_state: Current state of environment
                - goals: Active goals
                - constraints: Constraints on action selection

        Returns:
            Dict with selected action, alternatives, and MATRIZ node
        """
        start_time = time.time()

        candidates = input_data.get("candidate_actions", [])
        current_state = input_data.get("current_state", {})
        goals = input_data.get("goals", [])
        constraints = input_data.get("constraints", {})

        # Evaluate all candidates
        evaluated = self._evaluate_candidates(
            candidates,
            current_state,
            goals,
            constraints
        )

        # Rank by score
        evaluated.sort(key=lambda a: a.score, reverse=True)

        # Select best
        selected = evaluated[0] if evaluated else None

        # Compute confidence
        confidence = self._compute_confidence(evaluated)

        # Create NodeState
        state = NodeState(
            confidence=confidence,
            salience=min(1.0, 0.7 + (selected.score if selected else 0) * 0.3),
            novelty=max(0.1, 0.5),
            utility=selected.utility if selected else 0.5,
            risk=selected.risk if selected else 0.5
        )

        # Create trigger
        trigger = NodeTrigger(
            event_type="action_selection_request",
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
                "candidate_count": len(candidates)
            },
            "selected_action": {
                "action_id": selected.action_id,
                "description": selected.description,
                "utility": selected.utility,
                "feasibility": selected.feasibility,
                "risk": selected.risk,
                "score": selected.score
            } if selected else None,
            "alternative_actions": [
                {
                    "action_id": a.action_id,
                    "description": a.description,
                    "score": a.score
                }
                for a in evaluated[1:4]  # Top 3 alternatives
            ]
        }

        return {
            "answer": {
                "selected_action": matriz_node["selected_action"],
                "alternative_actions": matriz_node["alternative_actions"]
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

        return "selected_action" in output["answer"]

    def _evaluate_candidates(
        self,
        candidates: List[dict],
        current_state: dict,
        goals: List[str],
        constraints: dict
    ) -> List[ActionCandidate]:
        """Evaluate all candidate actions."""
        evaluated = []

        for i, candidate in enumerate(candidates):
            action_id = candidate.get("id", f"action_{i}")
            description = candidate.get("description", f"Action {i}")

            # Assess utility (how well does it achieve goals?)
            utility = self._assess_utility(candidate, goals)

            # Assess feasibility (can we actually do it?)
            feasibility = self._assess_feasibility(candidate, current_state, constraints)

            # Assess risk
            risk = self._assess_risk(candidate, current_state)

            # Compute overall score
            score = self._compute_score(utility, feasibility, risk)

            evaluated.append(
                ActionCandidate(
                    action_id=action_id,
                    description=description,
                    utility=utility,
                    feasibility=feasibility,
                    risk=risk,
                    score=score
                )
            )

        return evaluated

    def _assess_utility(self, candidate: dict, goals: List[str]) -> float:
        """Assess utility of action relative to goals."""
        effects = candidate.get("effects", [])

        if not goals:
            return 0.5  # Neutral if no goals

        # Count how many goals this action achieves
        achieved = sum(
            1 for goal in goals
            if any(goal.lower() in str(effect).lower() for effect in effects)
        )

        return min(1.0, achieved / len(goals))

    def _assess_feasibility(
        self,
        candidate: dict,
        current_state: dict,
        constraints: dict
    ) -> float:
        """Assess feasibility of action."""
        preconditions = candidate.get("preconditions", [])
        state_facts = set(current_state.get("facts", []))

        if not preconditions:
            return 0.9  # High feasibility if no preconditions

        # Check precondition satisfaction
        satisfied = sum(1 for precond in preconditions if precond in state_facts)

        base_feasibility = satisfied / len(preconditions)

        # Check resource constraints
        required_resources = candidate.get("required_resources", {})
        available_resources = current_state.get("resources", {})

        resource_feasibility = 1.0
        for resource, amount in required_resources.items():
            available = available_resources.get(resource, 0)
            if available < amount:
                resource_feasibility *= 0.5

        return base_feasibility * resource_feasibility

    def _assess_risk(self, candidate: dict, current_state: dict) -> float:
        """Assess risk level of action."""
        # Risk from explicit risk score
        explicit_risk = candidate.get("risk", 0.3)

        # Risk from negative effects
        effects = candidate.get("effects", [])
        negative_effects = [e for e in effects if "fail" in str(e).lower() or "damage" in str(e).lower()]

        effect_risk = min(0.4, len(negative_effects) * 0.2)

        return min(1.0, explicit_risk + effect_risk)

    def _compute_score(self, utility: float, feasibility: float, risk: float) -> float:
        """Compute overall action score."""
        # Weighted combination
        # Higher utility = better
        # Higher feasibility = better
        # Higher risk = worse

        score = (
            0.5 * utility +
            0.3 * feasibility +
            0.2 * (1.0 - risk)  # Invert risk (lower risk = higher score)
        )

        return min(1.0, max(0.0, score))

    def _compute_confidence(self, evaluated: List[ActionCandidate]) -> float:
        """Compute confidence in action selection."""
        if not evaluated:
            return 0.0

        # High confidence if best action clearly better than alternatives
        best_score = evaluated[0].score
        second_best_score = evaluated[1].score if len(evaluated) > 1 else 0.0

        gap = best_score - second_best_score

        # Also factor in absolute quality of best action
        return min(1.0, best_score + gap * 0.5)
