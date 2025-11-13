#!/usr/bin/env python3
"""
MATRIZ State Assessment Node

A cognitive node for assessing the current state and providing a summary.
"""

import time
from typing import Any

from matriz.core.node_interface import CognitiveNode, NodeState, NodeTrigger


class StateAssessmentNode(CognitiveNode):
    """
    A cognitive node that assesses the current state.
    """

    def __init__(self, tenant: str = "default"):
        """
        Initialize the state assessment node.

        Args:
            tenant: Tenant identifier for multi-tenancy
        """
        super().__init__(
            node_name="matriz_state_assessment_node",
            capabilities=[
                "state_assessment",
                "self_awareness",
            ],
            tenant=tenant,
        )

    def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Process a state assessment task.

        Args:
            input_data: Dict containing:
                - 'state_to_assess': The state to be assessed.
                - 'trace_id': Optional execution trace ID
                - 'context': Optional additional context

        Returns:
            Dict containing the assessment summary.
        """
        start_time = time.time()
        trace_id = input_data.get("trace_id", self.get_deterministic_hash(input_data))
        state_to_assess = input_data.get("state_to_assess", {})
        context = input_data.get("context", {})

        trigger = NodeTrigger(
            event_type="state_assessment_request",
            timestamp=int(time.time() * 1000),
            effect="state_summarized",
        )

        if not state_to_assess:
            return self._create_error_response(
                "Missing state to assess",
                input_data,
                trace_id,
                start_time,
                [trigger],
            )

        try:
            summary = self._assess_state(state_to_assess)
            confidence = 0.85

            state = NodeState(
                confidence=confidence,
                salience=0.7,
                valence=0.5,
                utility=0.8,
            )

            reflection = self.create_reflection(
                reflection_type="affirmation",
                cause="Successfully assessed the state.",
                new_state={"summary": summary},
            )

            matriz_node = self.create_matriz_node(
                node_type="AWARENESS",
                state=state,
                trace_id=trace_id,
                triggers=[trigger],
                reflections=[reflection],
                additional_data={
                    "state_to_assess": state_to_assess,
                    "summary": summary,
                    "context": context,
                },
            )

            answer = f"State assessment summary: {summary}"

        except Exception as e:
            return self._create_error_response(
                f"State assessment error: {e!s}",
                input_data,
                trace_id,
                start_time,
                [trigger],
                state_to_assess=state_to_assess,
            )

        processing_time = time.time() - start_time

        return {
            "answer": answer,
            "confidence": confidence,
            "matriz_node": matriz_node,
            "processing_time": processing_time,
        }

    def _assess_state(self, state_to_assess: dict[str, Any]) -> str:
        # This is a placeholder for a real state assessment engine.
        return f"The state contains {len(state_to_assess)} items."

    def validate_output(self, output: dict[str, Any]) -> bool:
        """
        Validate the output of the state assessment node.
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
        state_to_assess: dict[str, Any] = {},
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
            cause=f"State assessment failed: {error_message}",
            old_state={"state_to_assess": state_to_assess},
            new_state={"error": error_message},
        )

        matriz_node = self.create_matriz_node(
            node_type="AWARENESS",
            state=state,
            trace_id=trace_id,
            triggers=triggers,
            reflections=[reflection],
            additional_data={
                "state_to_assess": state_to_assess,
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
