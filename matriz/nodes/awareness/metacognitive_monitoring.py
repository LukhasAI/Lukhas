#!/usr/bin/env python3
"""
MATRIZ Metacognitive Monitoring Node

Monitors cognitive processes in real-time for quality and performance.
Provides ongoing assessment of reasoning, decision-making, and learning.

Example: "Current reasoning shows confirmation bias, confidence calibration needed"
"""

import time
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List

from matriz.core.node_interface import CognitiveNode, NodeState, NodeTrigger


@dataclass
class CognitiveMetrics:
    """Metrics for cognitive process monitoring."""
    process_name: str
    efficiency: float  # How efficiently processing
    accuracy: float  # Estimated accuracy
    confidence_calibration: float  # How well-calibrated confidence is
    bias_score: float  # Detected bias level
    learning_rate: float  # Rate of improvement


class MetacognitiveMonitoringNode(CognitiveNode):
    """
    Monitors cognitive processes in real-time.

    Capabilities:
    - Process efficiency tracking
    - Accuracy estimation
    - Bias detection
    - Learning rate assessment
    """

    def __init__(self, tenant: str = "default"):
        super().__init__(
            node_name="matriz_metacognitive_monitoring",
            capabilities=[
                "cognitive_monitoring",
                "process_tracking",
                "bias_detection",
                "governed_trace"
            ],
            tenant=tenant
        )

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Monitor cognitive processes.

        Args:
            input_data: Dict containing:
                - active_processes: List of currently active cognitive processes
                - performance_history: Historical performance data
                - target_metrics: Target performance metrics
                - monitoring_window: Time window for monitoring

        Returns:
            Dict with monitoring results, alerts, and MATRIZ node
        """
        start_time = time.time()

        active_processes = input_data.get("active_processes", [])
        performance_history = input_data.get("performance_history", [])
        target_metrics = input_data.get("target_metrics", {})
        monitoring_window = input_data.get("monitoring_window", 3600000)  # 1 hour

        # Monitor each process
        metrics = self._monitor_processes(
            active_processes,
            performance_history,
            monitoring_window
        )

        # Detect anomalies
        anomalies = self._detect_anomalies(metrics, target_metrics)

        # Generate alerts
        alerts = self._generate_alerts(metrics, anomalies)

        # Calculate overall health
        overall_health = self._calculate_health(metrics)

        # Compute confidence
        confidence = self._compute_confidence(metrics, performance_history)

        # Create NodeState
        state = NodeState(
            confidence=confidence,
            salience=min(1.0, 0.8 + len(anomalies) * 0.05),
            novelty=max(0.1, len(anomalies) * 0.15),
            utility=overall_health
        )

        # Create trigger
        trigger = NodeTrigger(
            event_type="metacognitive_monitoring_update",
            timestamp=int(time.time() * 1000)
        )

        # Build MATRIZ node
        matriz_node = {
            "id": str(uuid.uuid4()),
            "type": "AWARENESS",
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
                "process_count": len(active_processes)
            },
            "cognitive_metrics": [
                {
                    "process_name": m.process_name,
                    "efficiency": m.efficiency,
                    "accuracy": m.accuracy,
                    "confidence_calibration": m.confidence_calibration,
                    "bias_score": m.bias_score,
                    "learning_rate": m.learning_rate
                }
                for m in metrics
            ],
            "anomalies": anomalies,
            "alerts": alerts,
            "overall_health": overall_health
        }

        return {
            "answer": {
                "cognitive_metrics": matriz_node["cognitive_metrics"],
                "anomalies": anomalies,
                "alerts": alerts,
                "overall_health": overall_health
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

        if "cognitive_metrics" not in output["answer"]:
            return False

        return True

    def _monitor_processes(
        self,
        active_processes: List[dict],
        performance_history: List[dict],
        monitoring_window: int
    ) -> List[CognitiveMetrics]:
        """Monitor each active cognitive process."""
        metrics = []

        for process in active_processes:
            process_name = process.get("name", "unknown")

            # Calculate efficiency
            efficiency = self._calculate_efficiency(process, performance_history)

            # Estimate accuracy
            accuracy = self._estimate_accuracy(process, performance_history)

            # Check confidence calibration
            calibration = self._check_calibration(process, performance_history)

            # Detect biases
            bias_score = self._detect_bias(process)

            # Calculate learning rate
            learning_rate = self._calculate_learning_rate(process, performance_history)

            metrics.append(
                CognitiveMetrics(
                    process_name=process_name,
                    efficiency=efficiency,
                    accuracy=accuracy,
                    confidence_calibration=calibration,
                    bias_score=bias_score,
                    learning_rate=learning_rate
                )
            )

        return metrics

    def _calculate_efficiency(
        self,
        process: dict,
        performance_history: List[dict]
    ) -> float:
        """Calculate process efficiency."""
        # Efficiency = output / resources used
        processing_time = process.get("processing_time", 1.0)
        outputs_produced = process.get("outputs_produced", 1)

        base_efficiency = outputs_produced / max(1.0, processing_time / 1000.0)

        # Normalize to 0-1
        return min(1.0, base_efficiency / 10.0)

    def _estimate_accuracy(
        self,
        process: dict,
        performance_history: List[dict]
    ) -> float:
        """Estimate current accuracy."""
        # Check recent performance
        recent = [
            h for h in performance_history[-10:]
            if h.get("process") == process.get("name")
        ]

        if not recent:
            return 0.7  # Default moderate accuracy

        # Calculate success rate
        successes = sum(1 for h in recent if h.get("success", False))
        return successes / len(recent)

    def _check_calibration(
        self,
        process: dict,
        performance_history: List[dict]
    ) -> float:
        """Check confidence calibration."""
        # Compare stated confidence with actual accuracy
        stated_confidence = process.get("confidence", 0.7)

        # Get historical accuracy
        accuracy = self._estimate_accuracy(process, performance_history)

        # Calibration error
        calibration_error = abs(stated_confidence - accuracy)

        # Convert to calibration score (lower error = better)
        return max(0.0, 1.0 - calibration_error)

    def _detect_bias(self, process: dict) -> float:
        """Detect cognitive biases in process."""
        bias_score = 0.0

        # Check for common biases
        biases = process.get("detected_biases", [])

        # Each detected bias increases score
        bias_score = min(1.0, len(biases) * 0.2)

        return bias_score

    def _calculate_learning_rate(
        self,
        process: dict,
        performance_history: List[dict]
    ) -> float:
        """Calculate learning/improvement rate."""
        # Check performance trend
        recent = [
            h for h in performance_history[-20:]
            if h.get("process") == process.get("name")
        ]

        if len(recent) < 2:
            return 0.0  # Not enough data

        # Compare first half to second half
        midpoint = len(recent) // 2
        first_half = recent[:midpoint]
        second_half = recent[midpoint:]

        first_avg = sum(h.get("accuracy", 0.5) for h in first_half) / len(first_half)
        second_avg = sum(h.get("accuracy", 0.5) for h in second_half) / len(second_half)

        # Learning rate is improvement
        improvement = second_avg - first_avg

        return max(-1.0, min(1.0, improvement))

    def _detect_anomalies(
        self,
        metrics: List[CognitiveMetrics],
        target_metrics: dict
    ) -> List[str]:
        """Detect anomalies in cognitive processes."""
        anomalies = []

        for metric in metrics:
            # Check efficiency
            target_efficiency = target_metrics.get("efficiency", 0.7)
            if metric.efficiency < target_efficiency - 0.2:
                anomalies.append(
                    f"{metric.process_name}: Low efficiency ({metric.efficiency:.2f})"
                )

            # Check accuracy
            target_accuracy = target_metrics.get("accuracy", 0.8)
            if metric.accuracy < target_accuracy - 0.2:
                anomalies.append(
                    f"{metric.process_name}: Low accuracy ({metric.accuracy:.2f})"
                )

            # Check calibration
            if metric.confidence_calibration < 0.6:
                anomalies.append(
                    f"{metric.process_name}: Poor confidence calibration"
                )

            # Check bias
            if metric.bias_score > 0.5:
                anomalies.append(
                    f"{metric.process_name}: High bias detected ({metric.bias_score:.2f})"
                )

            # Check learning
            if metric.learning_rate < -0.1:
                anomalies.append(
                    f"{metric.process_name}: Negative learning (performance degrading)"
                )

        return anomalies

    def _generate_alerts(
        self,
        metrics: List[CognitiveMetrics],
        anomalies: List[str]
    ) -> List[str]:
        """Generate alerts for attention."""
        alerts = []

        # Critical alerts
        for metric in metrics:
            if metric.efficiency < 0.3:
                alerts.append(f"CRITICAL: {metric.process_name} efficiency very low")

            if metric.accuracy < 0.5:
                alerts.append(f"CRITICAL: {metric.process_name} accuracy below 50%")

            if metric.bias_score > 0.7:
                alerts.append(f"WARNING: High bias in {metric.process_name}")

        # General alerts from anomalies
        if len(anomalies) >= 5:
            alerts.append("WARNING: Multiple cognitive anomalies detected")

        return alerts

    def _calculate_health(self, metrics: List[CognitiveMetrics]) -> float:
        """Calculate overall cognitive health."""
        if not metrics:
            return 0.5

        # Average key metrics
        avg_efficiency = sum(m.efficiency for m in metrics) / len(metrics)
        avg_accuracy = sum(m.accuracy for m in metrics) / len(metrics)
        avg_calibration = sum(m.confidence_calibration for m in metrics) / len(metrics)

        # Penalty for bias
        avg_bias = sum(m.bias_score for m in metrics) / len(metrics)

        health = (avg_efficiency + avg_accuracy + avg_calibration) / 3 - avg_bias * 0.2

        return max(0.0, min(1.0, health))

    def _compute_confidence(
        self,
        metrics: List[CognitiveMetrics],
        performance_history: List[dict]
    ) -> float:
        """Compute confidence in monitoring."""
        # More history = higher confidence

        base_confidence = min(1.0, 0.5 + len(performance_history) * 0.01)

        # Boost if processes are well-calibrated
        if metrics:
            avg_calibration = sum(m.confidence_calibration for m in metrics) / len(metrics)
            calibration_boost = avg_calibration * 0.3

            return min(1.0, base_confidence + calibration_boost)

        return base_confidence
