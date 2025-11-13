#!/usr/bin/env python3
"""
MATRIZ Option Selection Node

A cognitive node for selecting the best option from a list.
"""

import time
from typing import Any, ClassVar

from matriz.core.node_interface import CognitiveNode, NodeState, NodeTrigger


class OptionSelectionNode(CognitiveNode):
    """
    A cognitive node that selects the best option from a list.
    """

    def __init__(self, tenant: str = "default"):
        """
        Initialize the option selection node.

        Args:
            tenant: Tenant identifier for multi-tenancy
        """
        super().__init__(
            node_name="matriz_option_selection_node",
            capabilities=[
                "option_selection",
                "decision_making",
            ],
            tenant=tenant,
        )

    def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Process an option selection task.

        Args:
            input_data: Dict containing:
                - 'options': A list of options to choose from.
                - 'criteria': The criteria for selecting the best option.
                - 'trace_id': Optional execution trace ID
                - 'context': Optional additional context

        Returns:
            Dict containing the selected option.
        """
        start_time = time.time()
        trace_id = input_data.get("trace_id", self.get_deterministic_hash(input_data))
        options = input_data.get("options", [])
        criteria = input_data.get("criteria", "")
        context = input_data.get("context", {})

        trigger = NodeTrigger(
            event_type="option_selection_request",
            timestamp=int(time.time() * 1000),
            effect="option_selected",
        )

        if not options or not criteria:
            return self._create_error_response(
                "Missing options or criteria",
                input_data,
                trace_id,
                start_time,
                [trigger],
            )

        try:
            best_option = self._select_option(options, criteria)
            confidence = 0.9

            state = NodeState(
                confidence=confidence,
                salience=0.85,
                valence=0.75,
                utility=0.9,
            )

            reflection = self.create_reflection(
                reflection_type="affirmation",
                cause="Successfully selected an option.",
                new_state={"best_option": best_option},
            )

            matriz_node = self.create_matriz_node(
                node_type="DECISION",
                state=state,
                trace_id=trace_id,
                triggers=[trigger],
                reflections=[reflection],
                additional_data={
                    "options": options,
                    "criteria": criteria,
                    "best_option": best_option,
                    "context": context,
                },
            )

            answer = f"The best option based on '{criteria}' is: {best_option}"

        except Exception as e:
            return self._create_error_response(
                f"Option selection error: {e!s}",
                input_data,
                trace_id,
                start_time,
                [trigger],
                options=options,
                criteria=criteria,
            )

        processing_time = time.time() - start_time

        return {
            "answer": answer,
            "confidence": confidence,
            "matriz_node": matriz_node,
            "processing_time": processing_time,
        }

    def _select_option(self, options: list[str], criteria: str) -> str:
        # This is a placeholder for a real option selection engine.
        # For this example, we'll just return the first option.
        return options[0]

    def validate_output(self, output: dict[str, Any]) -> bool:
        """
        Validate the output of the option selection node.
        """
        try:
            required_fields = ["answer", "confidence", "matriz_node", "processing_time"]
            for field in required_fields:
                if field not in output:
                    return False
            if not isinstance(output["answer"], str):
                return False
            if not (0 <= output["confidence"] <= 1):
                return False
            return self.validate_matriz_node(output["matriz_node"])
        except Exception:
            return False

    def _create_error_response(
        self,
        error_message: str,
        input_data: dict[str, Any],
        trace_id: str,
        start_time: float,
        triggers: list[NodeTrigger],
        options: list[str] = [],
        criteria: str = "",
    ) -> dict[str, Any]:
        """
        Create standardized error response with MATRIZ node.
        """
        confidence = 0.1
        state = NodeState(
            confidence=confidence,
            salience=0.3,
            valence=-0.6,
            risk=0.8,
            utility=0.1,
        )

        reflection = self.create_reflection(
            reflection_type="regret",
            cause=f"Option selection failed: {error_message}",
            old_state={"options": options, "criteria": criteria},
            new_state={"error": error_message},
        )

        matriz_node = self.create_matriz_node(
            node_type="DECISION",
            state=state,
            trace_id=trace_id,
            triggers=triggers,
            reflections=[reflection],
            additional_data={
                "options": options,
                "criteria": criteria,
                "error": error_message,
                "context": input_data.get("context", {}),
            },
        )
        processing_time = time.time() - start_time
        return {
            "answer": f"Error: {error_message}",
            "confidence": confidence,
            "matriz_node": matriz_node,
            "processing_time": processing_time,
        }
