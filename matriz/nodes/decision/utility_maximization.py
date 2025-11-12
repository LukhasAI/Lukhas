#!/usr/bin/env python3
"""
MATRIZ Utility Maximization Node

Selects options that maximize expected utility.
Uses decision theory and utility functions for rational choice.

Example: "Option A: 70% chance of $100 (utility 70), Option B: $50 guaranteed (utility 50) → Choose A"
"""

import time
import uuid
from typing import Any, Dict, List
from dataclasses import dataclass

from matriz.core.node_interface import CognitiveNode, NodeState, NodeTrigger


@dataclass
class UtilityOption:
    """An option with utility calculation."""
    option_id: str
    description: str
    expected_utility: float
    probability: float
    base_value: float
    utility_score: float


class UtilityMaximizationNode(CognitiveNode):
    """
    Maximizes expected utility across options.

    Capabilities:
    - Utility calculation
    - Expected value computation
    - Risk-adjusted utility
    - Rational choice selection
    """

    def __init__(self, tenant: str = "default"):
        super().__init__(
            node_name="matriz_utility_maximization",
            capabilities=[
                "utility_calculation",
                "expected_value",
                "rational_choice",
                "governed_trace"
            ],
            tenant=tenant
        )

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Maximize expected utility.

        Args:
            input_data: Dict containing:
                - options: List of decision options
                - utility_function: Utility function parameters
                - risk_preference: Risk aversion/seeking coefficient
                - constraints: Decision constraints

        Returns:
            Dict with optimal choice, utility analysis, and MATRIZ node
        """
        start_time = time.time()

        options = input_data.get("options", [])
        utility_function = input_data.get("utility_function", {"type": "linear"})
        risk_preference = input_data.get("risk_preference", 0.0)  # 0 = neutral
        constraints = input_data.get("constraints", {})

        # Calculate utilities for all options
        utility_options = self._calculate_utilities(
            options,
            utility_function,
            risk_preference
        )

        # Rank by utility
        utility_options.sort(key=lambda o: o.utility_score, reverse=True)

        # Select maximum utility option
        optimal = utility_options[0] if utility_options else None

        # Compute confidence
        confidence = self._compute_confidence(utility_options)

        # Create NodeState
        state = NodeState(
            confidence=confidence,
            salience=min(1.0, 0.8 + (optimal.utility_score if optimal else 0) * 0.2),
            novelty=max(0.1, 0.3),
            utility=optimal.utility_score if optimal else 0.5
        )

        # Create trigger
        trigger = NodeTrigger(
            event_type="utility_maximization_request",
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
                "option_count": len(options)
            },
            "optimal_choice": {
                "option_id": optimal.option_id,
                "description": optimal.description,
                "expected_utility": optimal.expected_utility,
                "probability": optimal.probability,
                "base_value": optimal.base_value,
                "utility_score": optimal.utility_score
            } if optimal else None,
            "alternative_options": [
                {
                    "option_id": o.option_id,
                    "description": o.description,
                    "utility_score": o.utility_score
                }
                for o in utility_options[1:4]  # Top 3 alternatives
            ]
        }

        return {
            "answer": {
                "optimal_choice": matriz_node["optimal_choice"],
                "alternative_options": matriz_node["alternative_options"]
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

        if "optimal_choice" not in output["answer"]:
            return False

        return True

    def _calculate_utilities(
        self,
        options: List[dict],
        utility_function: dict,
        risk_preference: float
    ) -> List[UtilityOption]:
        """Calculate utility for each option."""
        utility_options = []

        for i, option in enumerate(options):
            option_id = option.get("id", f"option_{i}")
            description = option.get("description", f"Option {i}")
            probability = option.get("probability", 1.0)
            base_value = option.get("value", 0.0)

            # Calculate utility
            utility = self._apply_utility_function(
                base_value,
                utility_function
            )

            # Calculate expected utility
            expected_utility = probability * utility

            # Adjust for risk preference
            utility_score = self._adjust_for_risk(
                expected_utility,
                probability,
                risk_preference
            )

            utility_options.append(
                UtilityOption(
                    option_id=option_id,
                    description=description,
                    expected_utility=expected_utility,
                    probability=probability,
                    base_value=base_value,
                    utility_score=utility_score
                )
            )

        return utility_options

    def _apply_utility_function(
        self,
        value: float,
        utility_function: dict
    ) -> float:
        """Apply utility function to value."""
        func_type = utility_function.get("type", "linear")

        if func_type == "linear":
            return value

        elif func_type == "logarithmic":
            # Logarithmic utility (risk-averse)
            import math
            return math.log(1 + max(0, value))

        elif func_type == "exponential":
            # Exponential utility (risk-seeking)
            import math
            alpha = utility_function.get("alpha", 0.5)
            return (math.exp(alpha * value) - 1) / alpha

        elif func_type == "power":
            # Power utility
            alpha = utility_function.get("alpha", 0.5)
            return value ** alpha if value >= 0 else -((-value) ** alpha)

        else:
            # Default to linear
            return value

    def _adjust_for_risk(
        self,
        expected_utility: float,
        probability: float,
        risk_preference: float
    ) -> float:
        """Adjust utility for risk preference."""
        # risk_preference: < 0 = risk-averse, 0 = neutral, > 0 = risk-seeking

        if risk_preference == 0.0:
            return expected_utility

        # Risk adjustment based on uncertainty
        uncertainty = 1.0 - probability

        if risk_preference < 0:
            # Risk-averse: penalize uncertain outcomes
            penalty = abs(risk_preference) * uncertainty * expected_utility
            return expected_utility - penalty
        else:
            # Risk-seeking: bonus for uncertain outcomes
            bonus = risk_preference * uncertainty * expected_utility * 0.5
            return expected_utility + bonus

    def _compute_confidence(self, utility_options: List[UtilityOption]) -> float:
        """Compute confidence in utility maximization."""
        if not utility_options:
            return 0.0

        # High confidence if:
        # 1. Clear winner (large gap)
        # 2. High probabilities

        # Check utility gap
        best_utility = utility_options[0].utility_score
        second_best = utility_options[1].utility_score if len(utility_options) > 1 else 0.0

        gap = best_utility - second_best

        # Check probability of best option
        best_prob = utility_options[0].probability

        # Combine factors
        confidence = min(1.0, (gap + best_prob) / 2)

        return max(0.1, confidence)
