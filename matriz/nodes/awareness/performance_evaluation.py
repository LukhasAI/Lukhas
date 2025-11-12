#!/usr/bin/env python3
"""
MATRIZ Performance Evaluation Cognitive Node

This node evaluates the quality of cognitive processing, compares actual
vs. expected outcomes, and identifies opportunities for improvement.
"""

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List

from matriz.core.node_interface import CognitiveNode, NodeState


@dataclass
class PerformanceReport:
    """Dataclass for performance evaluation reports."""
    task_id: str
    accuracy: float
    efficiency: float  # e.g., in tasks per second
    latency: float  # e.g., in seconds
    success_rate: float
    recommendations: List[str] = field(default_factory=list)


class PerformanceEvaluationNode(CognitiveNode):
    """
    A cognitive node that evaluates the performance of cognitive tasks.
    """

    def __init__(self, tenant: str = "default"):
        """
        Initializes the PerformanceEvaluationNode.
        """
        super().__init__(
            node_name="PerformanceEvaluationNode",
            capabilities=["performance_evaluation", "quality_assessment", "recommendation"],
            tenant=tenant,
        )

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Asynchronously evaluates performance based on input data.

        Args:
            input_data: A dictionary containing 'actual_outcome' and 'expected_outcome'.

        Returns:
            A dictionary containing the performance report and the MATRIZ node.
        """
        start_process_time = time.monotonic()

        actual_outcome = input_data.get("actual_outcome")
        expected_outcome = input_data.get("expected_outcome")
        task_id = input_data.get("task_id", "unknown")

        if actual_outcome is None or expected_outcome is None:
            raise ValueError("Input must contain 'actual_outcome' and 'expected_outcome'.")

        # Placeholder for complex evaluation logic
        accuracy = 1.0 if actual_outcome == expected_outcome else 0.0
        success_rate = 1.0 if accuracy > 0.9 else 0.0

        processing_time = time.monotonic() - start_process_time

        recommendations = []
        if accuracy < 0.8:
            recommendations.append("Consider retraining the model for this task.")
        if processing_time > 1.0:
            recommendations.append("Optimize the processing pipeline for lower latency.")

        performance_report = PerformanceReport(
            task_id=task_id,
            accuracy=accuracy,
            efficiency=1/processing_time if processing_time > 0 else 0,
            latency=processing_time,
            success_rate=success_rate,
            recommendations=recommendations,
        )

        # Create MATRIZ node
        state = NodeState(
            confidence=0.95,
            salience=0.8,
            utility=0.9,
        )

        matriz_node = self.create_matriz_node(
            node_type="AWARENESS",
            state=state,
            additional_data=performance_report.__dict__,
        )

        output = {
            "answer": performance_report,
            "confidence": 0.95,
            "matriz_node": matriz_node,
            "processing_time": processing_time,
        }

        self.validate_output(output)
        return output

    def validate_output(self, output: Dict[str, Any]) -> bool:
        """
        Validates the output of the process method.

        Args:
            output: The output dictionary from the process method.

        Returns:
            True if the output is valid, otherwise raises a ValueError.
        """
        if "answer" not in output or not isinstance(output["answer"], PerformanceReport):
            raise ValueError("Output 'answer' must be a PerformanceReport object.")
        if not self.validate_matriz_node(output["matriz_node"]):
            raise ValueError("Invalid MATRIZ node in output.")
        return True

async def main():
    """Example usage of the PerformanceEvaluationNode."""
    node = PerformanceEvaluationNode()
    print(f"Initialized {node.node_name} with capabilities: {node.capabilities}")

    # Simulate a successful task
    input_success = {"actual_outcome": "A", "expected_outcome": "A", "task_id": "task-001"}
    result_success = await node.process(input_success)

    print("\n--- Performance Report (Success) ---")
    report = result_success["answer"]
    print(f"Task ID: {report.task_id}")
    print(f"Accuracy: {report.accuracy:.2f}")
    print(f"Latency: {report.latency:.4f}s")
    print(f"Recommendations: {report.recommendations or 'None'}")
    print("------------------------------------\n")

    # Simulate a failed task
    input_fail = {"actual_outcome": "B", "expected_outcome": "A", "task_id": "task-002"}
    result_fail = await node.process(input_fail)

    print("--- Performance Report (Failure) ---")
    report = result_fail["answer"]
    print(f"Task ID: {report.task_id}")
    print(f"Accuracy: {report.accuracy:.2f}")
    print(f"Latency: {report.latency:.4f}s")
    print(f"Recommendations: {report.recommendations}")
    print("------------------------------------\n")

if __name__ == "__main__":
    asyncio.run(main())
