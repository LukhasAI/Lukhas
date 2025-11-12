#!/usr/bin/env python3
"""
Tests for MATRIZ Awareness Cognitive Nodes.
"""

import asyncio
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

import pytest

# Add repository root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../")))

# Mock psutil before importing the nodes
mock_psutil = MagicMock()
mock_psutil.cpu_percent.return_value = 10.0
mock_psutil.virtual_memory.return_value.percent = 20.0
sys.modules['psutil'] = mock_psutil

from matriz.nodes.awareness.performance_evaluation import (
    PerformanceEvaluationNode,
    PerformanceReport,
)
from matriz.nodes.awareness.self_monitoring import HealthMetrics, SelfMonitoringNode


@pytest.fixture
def self_monitoring_node():
    """Fixture for a SelfMonitoringNode instance."""
    return SelfMonitoringNode()

@pytest.fixture
def performance_evaluation_node():
    """Fixture for a PerformanceEvaluationNode instance."""
    return PerformanceEvaluationNode()

@pytest.mark.asyncio
async def test_self_monitoring_node_process(self_monitoring_node):
    """Test the basic processing of the SelfMonitoringNode."""
    result = await self_monitoring_node.process({})
    assert isinstance(result["answer"], HealthMetrics)
    assert result["confidence"] == 1.0
    assert "matriz_node" in result
    assert result["answer"].cpu_usage == 10.0
    assert result["answer"].memory_usage == 20.0

@pytest.mark.asyncio
async def test_performance_evaluation_node_process_success(performance_evaluation_node):
    """Test the basic processing of the PerformanceEvaluationNode for a successful task."""
    input_data = {"actual_outcome": "A", "expected_outcome": "A"}
    result = await performance_evaluation_node.process(input_data)
    report = result["answer"]
    assert isinstance(report, PerformanceReport)
    assert report.accuracy == 1.0
    assert result["confidence"] > 0.9

@pytest.mark.asyncio
async def test_performance_evaluation_node_process_failure(performance_evaluation_node):
    """Test the PerformanceEvaluationNode for a failed task."""
    input_data = {"actual_outcome": "B", "expected_outcome": "A"}
    result = await performance_evaluation_node.process(input_data)
    report = result["answer"]
    assert isinstance(report, PerformanceReport)
    assert report.accuracy == 0.0
    assert len(report.recommendations) > 0

if __name__ == "__main__":
    unittest.main()
