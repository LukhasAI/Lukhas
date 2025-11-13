#!/usr/bin/env python3
"""
MATRIZ Tool Usage Node

A cognitive node for selecting and using tools.
"""

import time
from typing import Any, Optional

from matriz.core.node_interface import CognitiveNode, NodeState, NodeTrigger


class ToolUsageNode(CognitiveNode):
    """
    A cognitive node that selects and uses a tool.
    """

    def __init__(self, tenant: str = "default"):
        """
        Initialize the tool usage node.

        Args:
            tenant: Tenant identifier for multi-tenancy
        """
        super().__init__(
            node_name="matriz_tool_usage_node",
            capabilities=[
                "tool_usage",
                "action_execution",
            ],
            tenant=tenant,
        )

    def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Process a tool usage task.

        Args:
            input_data: Dict containing:
                - 'tool_name': The name of the tool to use.
                - 'tool_params': The parameters for the tool.
                - 'trace_id': Optional execution trace ID
                - 'context': Optional additional context

        Returns:
            Dict containing the result of the tool usage.
        """
        start_time = time.time()
        trace_id = input_data.get("trace_id", self.get_deterministic_hash(input_data))
        tool_name = input_data.get("tool_name", "")
        tool_params = input_data.get("tool_params", {})
        context = input_data.get("context", {})

        trigger = NodeTrigger(
            event_type="tool_usage_request",
            timestamp=int(time.time() * 1000),
            effect="tool_execution",
        )

        if not tool_name:
            return self._create_error_response(
                "Missing tool name",
                input_data,
                trace_id,
                start_time,
                [trigger],
            )

        try:
            tool_result = self._execute_tool(tool_name, tool_params)
            confidence = 0.95

            state = NodeState(
                confidence=confidence,
                salience=0.9,
                valence=0.8,
                utility=0.95,
            )

            reflection = self.create_reflection(
                reflection_type="affirmation",
                cause="Successfully used a tool.",
                new_state={"tool_result": tool_result},
            )

            matriz_node = self.create_matriz_node(
                node_type="ACTION",
                state=state,
                trace_id=trace_id,
                triggers=[trigger],
                reflections=[reflection],
                additional_data={
                    "tool_name": tool_name,
                    "tool_params": tool_params,
                    "tool_result": tool_result,
                    "context": context,
                },
            )

            answer = f"Executed tool '{tool_name}' with result: {tool_result}"

        except Exception as e:
            return self._create_error_response(
                f"Tool execution error: {e!s}",
                input_data,
                trace_id,
                start_time,
                [trigger],
                tool_name=tool_name,
                tool_params=tool_params,
            )

        processing_time = time.time() - start_time

        return {
            "answer": answer,
            "confidence": confidence,
            "matriz_node": matriz_node,
            "processing_time": processing_time,
        }

    def _execute_tool(self, tool_name: str, tool_params: dict[str, Any]) -> Any:
        # This is a placeholder for a real tool execution engine.
        if tool_name == "calculator":
            return eval(tool_params.get("expression", "0"))
        elif tool_name == "search":
            return f"Search results for: {tool_params.get('query', '')}"
        else:
            raise ValueError(f"Unknown tool: {tool_name}")

    def validate_output(self, output: dict[str, Any]) -> bool:
        """
        Validate the output of the tool usage node.
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
        tool_name: str = "",
        tool_params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Create standardized error response with MATRIZ node.
        """
        if tool_params is None:
            tool_params = {}
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
            cause=f"Tool usage failed: {error_message}",
            old_state={"tool_name": tool_name, "tool_params": tool_params},
            new_state={"error": error_message},
        )

        matriz_node = self.create_matriz_node(
            node_type="ACTION",
            state=state,
            trace_id=trace_id,
            triggers=triggers,
            reflections=[reflection],
            additional_data={
                "tool_name": tool_name,
                "tool_params": tool_params,
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
