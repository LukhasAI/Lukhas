#!/usr/bin/env python3
"""
MATRIZ Self-Monitoring Cognitive Node

This node monitors the internal state of the cognitive system,
tracks resource usage, and detects anomalies.
"""

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List

from matriz.core.node_interface import CognitiveNode, NodeState

# Try to import psutil for system metrics, but handle its absence
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


@dataclass
class HealthMetrics:
    """Dataclass for system health metrics."""
    cpu_usage: float
    memory_usage: float
    processing_time: float
    tasks_processed: int
    anomalies_detected: List[str] = field(default_factory=list)


class SelfMonitoringNode(CognitiveNode):
    """
    A cognitive node that monitors its own operational state and system health.
    """

    def __init__(self, tenant: str = "default"):
        """
        Initializes the SelfMonitoringNode.
        """
        super().__init__(
            node_name="SelfMonitoringNode",
            capabilities=["system_monitoring", "anomaly_detection", "health_reporting"],
            tenant=tenant,
        )
        self.start_time = time.time()
        self.tasks_processed = 0

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Asynchronously processes monitoring data and generates a health report.

        Args:
            input_data: A dictionary, can be empty or contain specific monitoring requests.

        Returns:
            A dictionary containing the health metrics and the MATRIZ node.
        """
        start_process_time = time.monotonic()

        # Gather metrics
        cpu_usage = psutil.cpu_percent() if PSUTIL_AVAILABLE else 0.0
        memory_info = psutil.virtual_memory() if PSUTIL_AVAILABLE else None
        memory_usage = memory_info.percent if memory_info else 0.0

        self.tasks_processed += 1

        # Anomaly detection
        anomalies = []
        if cpu_usage > 95.0:
            anomalies.append(f"High CPU usage detected: {cpu_usage}%")
        if memory_usage > 90.0:
            anomalies.append(f"High memory usage detected: {memory_usage}%")

        processing_time = time.monotonic() - start_process_time

        health_metrics = HealthMetrics(
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            processing_time=processing_time,
            tasks_processed=self.tasks_processed,
            anomalies_detected=anomalies,
        )

        # Create MATRIZ node
        state = NodeState(
            confidence=1.0,
            salience=0.9 if anomalies else 0.5,
            urgency=0.8 if anomalies else 0.2,
        )

        matriz_node = self.create_matriz_node(
            node_type="AWARENESS",
            state=state,
            additional_data=health_metrics.__dict__,
        )

        output = {
            "answer": health_metrics,
            "confidence": 1.0,
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
        if "answer" not in output or not isinstance(output["answer"], HealthMetrics):
            raise ValueError("Output 'answer' must be a HealthMetrics object.")
        if "matriz_node" not in output or not self.validate_matriz_node(output["matriz_node"]):
            raise ValueError("Invalid MATRIZ node in output.")
        return True

async def main():
    """Example usage of the SelfMonitoringNode."""
    node = SelfMonitoringNode()
    print(f"Initialized {node.node_name} with capabilities: {node.capabilities}")

    # Simulate processing
    result = await node.process({})

    print("\n--- Self-Monitoring Report ---")
    health_metrics = result["answer"]
    print(f"CPU Usage: {health_metrics.cpu_usage}%")
    print(f"Memory Usage: {health_metrics.memory_usage}%")
    print(f"Processing Time: {health_metrics.processing_time:.4f}s")
    print(f"Anomalies: {health_metrics.anomalies_detected or 'None'}")
    print("----------------------------\n")

    print("Generated MATRIZ Node:")
    import json
    print(json.dumps(result["matriz_node"], indent=2))

if __name__ == "__main__":
    asyncio.run(main())
