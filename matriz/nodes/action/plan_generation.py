#!/usr/bin/env python3
"""
MATRIZ Plan Generation Node

Generates multi-step action plans to achieve goals.
Uses hierarchical task decomposition and constraint satisfaction.

Example: "To make coffee: 1) Fill water 2) Add grounds 3) Brew"
"""

import time
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List

from matriz.core.node_interface import CognitiveNode, NodeState, NodeTrigger


@dataclass
class ActionStep:
    """A single step in an action plan."""
    step_id: str
    description: str
    preconditions: List[str]
    effects: List[str]
    estimated_duration: float  # seconds


class PlanGenerationNode(CognitiveNode):
    """
    Generates multi-step action plans to achieve goals.

    Capabilities:
    - Goal decomposition
    - Step sequencing
    - Precondition checking
    - Success probability estimation
    """

    def __init__(self, tenant: str = "default"):
        super().__init__(
            node_name="matriz_plan_generation",
            capabilities=[
                "plan_generation",
                "task_decomposition",
                "constraint_satisfaction",
                "governed_trace"
            ],
            tenant=tenant
        )

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate action plan.

        Args:
            input_data: Dict containing:
                - goal: Target goal to achieve
                - current_state: Current state of the world
                - available_actions: Actions available to agent
                - constraints: Constraints on plan (time, resources, etc.)

        Returns:
            Dict with plan steps, estimated time, success probability, and MATRIZ node
        """
        start_time = time.time()

        goal = input_data.get("goal", "")
        current_state = input_data.get("current_state", {})
        available_actions = input_data.get("available_actions", [])
        constraints = input_data.get("constraints", {})

        # Decompose goal into subgoals
        subgoals = self._decompose_goal(goal, current_state)

        # Generate plan steps
        plan_steps = []
        for subgoal in subgoals:
            steps = self._plan_for_subgoal(
                subgoal,
                current_state,
                available_actions,
                constraints
            )
            plan_steps.extend(steps)

        # Estimate total time
        estimated_time = sum(step.estimated_duration for step in plan_steps)

        # Estimate success probability
        success_prob = self._estimate_success_probability(plan_steps, current_state)

        # Create NodeState
        state = NodeState(
            confidence=success_prob,
            salience=min(1.0, 0.7 + len(plan_steps) * 0.05),
            novelty=max(0.1, 1.0 - success_prob),
            utility=min(1.0, 0.8 + len(subgoals) * 0.05)
        )

        # Create trigger
        trigger = NodeTrigger(
            event_type="plan_generation_request",
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
                "step_count": len(plan_steps),
                "subgoal_count": len(subgoals)
            },
            "plan": [
                {
                    "step_id": step.step_id,
                    "description": step.description,
                    "preconditions": step.preconditions,
                    "effects": step.effects,
                    "estimated_duration": step.estimated_duration
                }
                for step in plan_steps
            ],
            "estimated_time": estimated_time,
            "success_probability": success_prob
        }

        return {
            "answer": {
                "plan": matriz_node["plan"],
                "estimated_time": estimated_time,
                "success_probability": success_prob
            },
            "confidence": success_prob,
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

        return "plan" in output["answer"]

    def _decompose_goal(self, goal: str, current_state: dict) -> List[str]:
        """Decompose high-level goal into subgoals."""
        subgoals = []

        if " and " in goal:
            subgoals = goal.split(" and ")
        else:
            # Single goal
            subgoals = [goal]

        return [sg.strip() for sg in subgoals if sg.strip()]

    def _plan_for_subgoal(
        self,
        subgoal: str,
        current_state: dict,
        available_actions: List[dict],
        constraints: dict
    ) -> List[ActionStep]:
        """Plan steps to achieve a single subgoal."""
        steps = []

        # Find actions that achieve subgoal
        relevant_actions = [
            action for action in available_actions
            if subgoal.lower() in str(action.get("effects", "")).lower()
        ]

        # If no relevant actions found, create generic step
        if not relevant_actions:
            steps.append(
                ActionStep(
                    step_id=f"step_{len(steps) + 1}",
                    description=f"Achieve: {subgoal}",
                    preconditions=[],
                    effects=[subgoal],
                    estimated_duration=10.0
                )
            )
        else:
            # Add relevant actions (max 3 per subgoal)
            for i, action in enumerate(relevant_actions[:3]):
                steps.append(
                    ActionStep(
                        step_id=f"step_{len(steps) + 1}",
                        description=action.get("description", f"Action {i+1}"),
                        preconditions=action.get("preconditions", []),
                        effects=action.get("effects", []),
                        estimated_duration=action.get("duration", 10.0)
                    )
                )

        return steps

    def _estimate_success_probability(
        self,
        plan_steps: List[ActionStep],
        current_state: dict
    ) -> float:
        """Estimate probability that plan will succeed."""
        if not plan_steps:
            return 0.0

        # Check precondition satisfaction
        satisfied_preconditions = 0
        total_preconditions = 0

        state_facts = set(current_state.get("facts", []))

        for step in plan_steps:
            for precond in step.preconditions:
                total_preconditions += 1
                if precond in state_facts:
                    satisfied_preconditions += 1

        if total_preconditions == 0:
            return 0.8  # Default high probability

        base_prob = satisfied_preconditions / total_preconditions

        # Penalty for long plans (more uncertainty)
        length_penalty = min(0.2, len(plan_steps) * 0.02)

        return max(0.0, base_prob - length_penalty)
