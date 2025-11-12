#!/usr/bin/env python3
"""
MATRIZ Awareness Nodes

Awareness nodes monitor and calibrate cognitive processes for metacognitive insight.
"""

from matriz.nodes.awareness.metacognitive_monitoring import MetacognitiveMonitoringNode
from matriz.nodes.awareness.confidence_calibration import ConfidenceCalibrationNode

__all__ = [
    "ConfidenceCalibrationNode",
    "MetacognitiveMonitoringNode",
]

# Additional awareness nodes
from matriz.nodes.awareness.performance_evaluation import PerformanceEvaluationNode
from matriz.nodes.awareness.self_monitoring import SelfMonitoringNode

__all__.extend([
    "PerformanceEvaluationNode",
    "SelfMonitoringNode",
])
