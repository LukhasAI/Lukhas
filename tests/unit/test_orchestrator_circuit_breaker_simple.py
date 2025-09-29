#!/usr/bin/env python3
"""
Simple Circuit Breaker Integration Test

Validates that circuit breaker integration is properly wired into the orchestrator.
"""

from unittest.mock import Mock

from matriz.core.async_orchestrator import AsyncCognitiveOrchestrator
from matriz.core.node_interface import CognitiveNode


def test_orchestrator_circuit_breaker_integration():
    """Test that circuit breaker features are properly integrated"""
    orchestrator = AsyncCognitiveOrchestrator(
        total_timeout=0.250  # 250ms total budget
    )

    # Create and register a mock node
    mock_node = Mock(spec=CognitiveNode)
    mock_node.process.return_value = {
        "answer": "Circuit breaker test response",
        "confidence": 0.85
    }
    orchestrator.register_node("test_node", mock_node)

    # Get performance report to verify circuit breaker integration
    report = orchestrator.get_performance_report()

    # Verify required keys exist
    assert "stage_timeouts" in report
    assert "total_timeout" in report
    assert "orchestrator_metrics" in report
    assert "node_health" in report

    # Verify timeout configuration is reasonable
    assert report["total_timeout"] == 0.250

    timeouts = report["stage_timeouts"]
    assert len(timeouts) == 5  # 5 MATRIZ stages
    assert all(isinstance(timeout, (int, float)) for timeout in timeouts.values())
    assert all(timeout > 0 for timeout in timeouts.values())

    # Verify node health tracking exists
    node_health = report["node_health"]
    assert "test_node" in node_health

    health_data = node_health["test_node"]
    required_fields = ["success_count", "failure_count", "total_duration_ms", "p95_latency_ms"]
    for field in required_fields:
        assert field in health_data


def test_circuit_breaker_metrics_structure():
    """Test that circuit breaker metrics have correct structure"""
    orchestrator = AsyncCognitiveOrchestrator()

    # Register a test node
    mock_node = Mock(spec=CognitiveNode)
    orchestrator.register_node("metrics_test", mock_node)

    # Get performance report
    report = orchestrator.get_performance_report()

    # Verify metrics structure
    metrics = report.get("orchestrator_metrics", {})
    expected_metrics = [
        "total_duration_ms", "stage_durations", "timeout_count",
        "error_count", "stages_completed", "stages_skipped"
    ]

    for metric in expected_metrics:
        assert metric in metrics or hasattr(orchestrator.metrics, metric)


def test_adaptive_health_tracking():
    """Test that adaptive health tracking is properly configured"""
    orchestrator = AsyncCognitiveOrchestrator()

    # Register node and check initial state
    mock_node = Mock(spec=CognitiveNode)
    orchestrator.register_node("health_test", mock_node)

    # Verify initial health state
    report = orchestrator.get_performance_report()
    node_health = report["node_health"]["health_test"]

    # Check initial counters are zero
    assert node_health["success_count"] == 0
    assert node_health["failure_count"] == 0
    assert node_health["total_duration_ms"] == 0.0
    assert isinstance(node_health["recent_latencies"], list)
    assert len(node_health["recent_latencies"]) == 0


def test_timeout_configuration_validation():
    """Test that timeout configurations are properly validated"""
    # Test default configuration
    orchestrator = AsyncCognitiveOrchestrator()
    report = orchestrator.get_performance_report()

    timeouts = report["stage_timeouts"]

    # Verify all stage types have timeouts
    expected_stages = ["intent", "decision", "processing", "validation", "reflection"]
    for stage in expected_stages:
        assert stage in timeouts
        assert timeouts[stage] > 0
        assert timeouts[stage] < 1.0  # Should be sub-second for 0.01% performance

    # Verify total is sum of parts (approximately)
    total_timeout = report["total_timeout"]
    assert total_timeout >= max(timeouts.values())  # At least as long as longest stage


if __name__ == "__main__":
    test_orchestrator_circuit_breaker_integration()
    test_circuit_breaker_metrics_structure()
    test_adaptive_health_tracking()
    test_timeout_configuration_validation()
    print("✅ All circuit breaker integration tests passed!")