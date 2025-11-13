#!/usr/bin/env python3
"""
MATRIZ Deductive Reasoning Node

A cognitive node for performing deductive reasoning based on a set of premises.
"""

import time
from typing import Any, Optional

from matriz.core.node_interface import CognitiveNode, NodeState, NodeTrigger


class DeductiveReasoningNode(CognitiveNode):
    """
    A cognitive node that performs deductive reasoning.
    """

    def __init__(self, tenant: str = "default"):
        """
        Initialize the deductive reasoning node.

        Args:
            tenant: Tenant identifier for multi-tenancy
        """
        super().__init__(
            node_name="matriz_deductive_reasoning_node",
            capabilities=[
                "deductive_reasoning",
                "logical_inference",
            ],
            tenant=tenant,
        )

    def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Process a deductive reasoning task.

        Args:
            input_data: Dict containing:
                - 'premises': A list of logical premises.
                - 'question': The question to answer based on the premises.
                - 'trace_id': Optional execution trace ID
                - 'context': Optional additional context

        Returns:
            Dict containing the result of the reasoning.
        """
        start_time = time.time()
        trace_id = input_data.get("trace_id", self.get_deterministic_hash(input_data))
        premises = input_data.get("premises", [])
        question = input_data.get("question", "")
        context = input_data.get("context", {})

        trigger = NodeTrigger(
            event_type="deductive_reasoning_request",
            timestamp=int(time.time() * 1000),
            effect="logical_conclusion",
        )

        if not premises or not question:
            return self._create_error_response(
                "Missing premises or question",
                input_data,
                trace_id,
                start_time,
                [trigger],
            )

        # A very simple deductive reasoning implementation
        try:
            conclusion = self._reason(premises, question)
            confidence = 0.9 if conclusion is not None else 0.5

            state = NodeState(
                confidence=confidence,
                salience=0.8,
                valence=0.7,
                utility=0.9,
            )

            reflection = self.create_reflection(
                reflection_type="affirmation",
                cause="Successfully performed deductive reasoning.",
                new_state={"conclusion": conclusion},
            )

            matriz_node = self.create_matriz_node(
                node_type="THOUGHT",
                state=state,
                trace_id=trace_id,
                triggers=[trigger],
                reflections=[reflection],
                additional_data={
                    "premises": premises,
                    "question": question,
                    "conclusion": conclusion,
                    "context": context,
                },
            )

            answer = f"Based on the premises, the conclusion is: {conclusion}"

        except Exception as e:
            return self._create_error_response(
                f"Reasoning error: {e!s}",
                input_data,
                trace_id,
                start_time,
                [trigger],
                premises=premises,
                question=question,
            )

        processing_time = time.time() - start_time

        return {
            "answer": answer,
            "confidence": confidence,
            "matriz_node": matriz_node,
            "processing_time": processing_time,
        }

    def _reason(self, premises: list[str], question: str) -> Any:
        # This is a placeholder for a real deductive reasoning engine.
        # For this example, we'll just do a very simple keyword match.
        for premise in premises:
            if all(word in premise for word in question.split()):
                 return premise
        return "I cannot answer the question based on the given premises."


    def validate_output(self, output: dict[str, Any]) -> bool:
        """
        Validate the output of the deductive reasoning node.
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
        premises: Optional[list[str]] = None,
        question: str = "",
    ) -> dict[str, Any]:
        """
        Create standardized error response with MATRIZ node.
        """
        if premises is None:
            premises = []
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
            cause=f"Deductive reasoning failed: {error_message}",
            old_state={"premises": premises, "question": question},
            new_state={"error": error_message},
        )

        matriz_node = self.create_matriz_node(
            node_type="THOUGHT",
            state=state,
            trace_id=trace_id,
            triggers=triggers,
            reflections=[reflection],
            additional_data={
                "premises": premises,
                "question": question,
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
