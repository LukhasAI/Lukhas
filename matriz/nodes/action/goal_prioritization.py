#!/usr/bin/env python3
"""
MATRIZ Goal Prioritization Node

Prioritizes multiple goals based on importance, urgency, and feasibility.
Uses multi-criteria decision making to rank goals.

Example: "Given [learn Python, finish project, exercise], prioritize finish project (urgent deadline)"
"""

import time
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List

from matriz.core.node_interface import CognitiveNode, NodeState, NodeTrigger


@dataclass
class PrioritizedGoal:
    """A goal with priority scoring."""
    goal_id: str
    description: str
    importance: float  # How important (0.0 - 1.0)
    urgency: float  # How urgent (0.0 - 1.0)
    feasibility: float  # How feasible (0.0 - 1.0)
    priority_score: float  # Overall priority


class GoalPrioritizationNode(CognitiveNode):
    """
    Prioritizes multiple competing goals.

    Capabilities:
    - Importance assessment
    - Urgency evaluation
    - Feasibility analysis
    - Priority ranking
    """

    def __init__(self, tenant: str = "default"):
        super().__init__(
            node_name="matriz_goal_prioritization",
            capabilities=[
                "goal_ranking",
                "importance_assessment",
                "urgency_evaluation",
                "governed_trace"
            ],
            tenant=tenant
        )

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prioritize goals.

        Args:
            input_data: Dict containing:
                - goals: List of goals to prioritize
                - current_state: Current state/context
                - constraints: Time/resource constraints
                - values: Value system for importance weighting

        Returns:
            Dict with prioritized goals and MATRIZ node
        """
        start_time = time.time()

        goals = input_data.get("goals", [])
        current_state = input_data.get("current_state", {})
        constraints = input_data.get("constraints", {})
        values = input_data.get("values", {})

        # Evaluate and prioritize all goals
        prioritized = self._prioritize_goals(
            goals,
            current_state,
            constraints,
            values
        )

        # Rank by priority score
        prioritized.sort(key=lambda g: g.priority_score, reverse=True)

        # Compute confidence
        confidence = self._compute_confidence(prioritized)

        # Create NodeState
        state = NodeState(
            confidence=confidence,
            salience=min(1.0, 0.7 + len(prioritized) * 0.05),
            novelty=max(0.1, 0.4),
            utility=min(1.0, 0.8 + len(prioritized) * 0.03),
            urgency=prioritized[0].urgency if prioritized else 0.5
        )

        # Create trigger
        trigger = NodeTrigger(
            event_type="goal_prioritization_request",
            timestamp=int(time.time() * 1000)
        )

        # Build MATRIZ node
        matriz_node = {
            "id": str(uuid.uuid4()),
            "type": "INTENT",
            "state": {
                "confidence": state.confidence,
                "salience": state.salience,
                "novelty": state.novelty,
                "utility": state.utility,
                "urgency": state.urgency
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
                "goal_count": len(goals)
            },
            "prioritized_goals": [
                {
                    "goal_id": g.goal_id,
                    "description": g.description,
                    "importance": g.importance,
                    "urgency": g.urgency,
                    "feasibility": g.feasibility,
                    "priority_score": g.priority_score,
                    "rank": i + 1
                }
                for i, g in enumerate(prioritized)
            ]
        }

        return {
            "answer": {
                "prioritized_goals": matriz_node["prioritized_goals"],
                "top_priority": matriz_node["prioritized_goals"][0] if prioritized else None
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

        return "prioritized_goals" in output["answer"]

    def _prioritize_goals(
        self,
        goals: List[dict],
        current_state: dict,
        constraints: dict,
        values: dict
    ) -> List[PrioritizedGoal]:
        """Evaluate and prioritize all goals."""
        prioritized = []

        for i, goal in enumerate(goals):
            goal_id = goal.get("id", f"goal_{i}")
            description = goal.get("description", f"Goal {i}")

            # Assess importance (aligned with values)
            importance = self._assess_importance(goal, values)

            # Assess urgency (time constraints)
            urgency = self._assess_urgency(goal, constraints)

            # Assess feasibility
            feasibility = self._assess_feasibility(goal, current_state, constraints)

            # Compute priority score
            priority_score = self._compute_priority(importance, urgency, feasibility)

            prioritized.append(
                PrioritizedGoal(
                    goal_id=goal_id,
                    description=description,
                    importance=importance,
                    urgency=urgency,
                    feasibility=feasibility,
                    priority_score=priority_score
                )
            )

        return prioritized

    def _assess_importance(self, goal: dict, values: dict) -> float:
        """Assess importance based on value alignment."""
        # Get explicit importance
        explicit_importance = goal.get("importance", 0.5)

        # Check alignment with values
        goal_tags = set(goal.get("tags", []))
        value_tags = set(values.get("priorities", []))

        if not value_tags:
            return explicit_importance

        # How many values does this goal align with?
        alignment = len(goal_tags & value_tags) / max(1, len(value_tags))

        # Combine explicit and alignment-based importance
        return min(1.0, (explicit_importance + alignment) / 2)

    def _assess_urgency(self, goal: dict, constraints: dict) -> float:
        """Assess urgency based on deadlines and time pressure."""
        # Get explicit urgency
        explicit_urgency = goal.get("urgency", 0.5)

        # Check deadline
        deadline = goal.get("deadline")
        current_time = constraints.get("current_time", 0)

        if deadline and current_time:
            time_remaining = deadline - current_time
            max_time = constraints.get("planning_horizon", 86400000)  # 24 hours default

            # Higher urgency as deadline approaches
            deadline_urgency = max(0.0, 1.0 - time_remaining / max_time)

            return min(1.0, max(explicit_urgency, deadline_urgency))

        return explicit_urgency

    def _assess_feasibility(
        self,
        goal: dict,
        current_state: dict,
        constraints: dict
    ) -> float:
        """Assess how feasible the goal is."""
        # Check required resources
        required_resources = goal.get("required_resources", {})
        available_resources = current_state.get("resources", {})

        if not required_resources:
            return 0.8  # High feasibility if no special resources needed

        resource_feasibility = 1.0
        for resource, amount in required_resources.items():
            available = available_resources.get(resource, 0)
            if available < amount:
                # Reduce feasibility proportionally
                resource_feasibility *= available / amount if amount > 0 else 0.0

        # Check preconditions
        preconditions = goal.get("preconditions", [])
        state_facts = set(current_state.get("facts", []))

        if preconditions:
            satisfied = sum(1 for p in preconditions if p in state_facts)
            precondition_feasibility = satisfied / len(preconditions)
        else:
            precondition_feasibility = 1.0

        return (resource_feasibility + precondition_feasibility) / 2

    def _compute_priority(
        self,
        importance: float,
        urgency: float,
        feasibility: float
    ) -> float:
        """Compute overall priority score."""
        # Eisenhower matrix inspired: importance x urgency
        # But also consider feasibility (don't prioritize impossible goals)

        # Base priority from importance and urgency
        base_priority = (
            0.5 * importance +
            0.3 * urgency
        )

        # Modulate by feasibility (reduce priority if not feasible)
        priority = base_priority * (0.5 + 0.5 * feasibility)

        return min(1.0, max(0.0, priority))

    def _compute_confidence(self, prioritized: List[PrioritizedGoal]) -> float:
        """Compute confidence in prioritization."""
        if not prioritized:
            return 0.0

        # High confidence if clear separation between priorities
        if len(prioritized) < 2:
            return 0.9  # Easy to prioritize one goal

        # Check score separation
        top_score = prioritized[0].priority_score
        second_score = prioritized[1].priority_score

        gap = top_score - second_score

        # Larger gap = higher confidence
        return min(1.0, 0.6 + gap)
