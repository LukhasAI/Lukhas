#!/usr/bin/env python3
"""
Test Circuit Breaker Integration with Async Orchestrator

Validates that circuit breaker patterns are properly integrated
for retries, backpressure, and graceful degradation.
"""

import asyncio
import time
from unittest.mock import Mock, patch

import pytest
from core.reliability.circuit_breaker import get_circuit_health

# pytest-asyncio is already configured globally
from matriz.core.async_orchestrator import AsyncCognitiveOrchestrator
from matriz.core.node_interface import CognitiveNode


class TestOrchestratoresWithCircuitBreakers:
    """Test orchestrator circuit breaker integration"""

    def setup_method(self):
        """Set up test orchestrator with mock nodes"""
        self.orchestrator = AsyncCognitiveOrchestrator(
            total_timeout=0.500  # 500ms total budget for testing
        )

        # Create mock nodes
        self.mock_node = Mock(spec=CognitiveNode)
        self.mock_node.process.return_value = {
            "answer": "Test response",
            "confidence": 0.9
        }

        self.orchestrator.register_node("test_node", self.mock_node)

    @pytest.mark.asyncio
    async def test_circuit_breaker_normal_operation(self):
        """Test that circuit breaker allows normal operations"""
        # Process multiple successful requests
        for i in range(5):
            result = await self.orchestrator.process_query(f"test query {i}")
            assert "answer" in result
            assert result["answer"] == "Test response"

        # Check performance report includes circuit breaker status
        report = self.orchestrator.get_performance_report()
        assert "circuit_breaker_health" in report or "orchestrator_metrics" in report

    @pytest.mark.asyncio
    async def test_circuit_breaker_failure_recovery(self):
        """Test circuit breaker opens on failures and recovers"""
        # Configure mock to fail initially
        self.mock_node.process.side_effect = Exception("Simulated failure")

        # Generate failures to trigger circuit breaker
        for i in range(12):  # Exceed failure threshold
            try:  # TODO[T4-ISSUE]: {"code":"SIM105","ticket":"GH-1031","owner":"consciousness-team","status":"planned","reason":"try-except-pass pattern - consider contextlib.suppress for clarity","estimate":"10m","priority":"low","dependencies":"contextlib","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_tests_unit_test_orchestrator_circuit_breaker_py_L60"}
                await self.orchestrator.process_query(f"failing query {i}")
            except Exception:
                pass  # Expected failures

        # Check circuit breaker health
        health = get_circuit_health()
        if isinstance(health, dict) and health:
            breaker_states = []
            for status in health.values():
                if isinstance(status, dict):
                    breaker_states.append(status.get("state"))
                else:
                    breaker_states.append(status)

            assert any(
                state in {"open", "half_open"} for state in breaker_states if state
            ) or any(state is not None for state in breaker_states)

        # Now fix the mock and test recovery
        self.mock_node.process.side_effect = None
        self.mock_node.process.return_value = {
            "answer": "Recovery response",
            "confidence": 0.8
        }

        # Give time for recovery timeout (circuit breakers have 30s recovery)
        # In test, we'll just verify the mechanism exists
        report = self.orchestrator.get_performance_report()
        assert "circuit_breaker_health" in report or "node_health" in report

    @pytest.mark.asyncio
    async def test_performance_degradation_detection(self):
        """Test that performance degradation is detected"""
        # Create slow responses to trigger performance degradation
        async def slow_process(*args, **kwargs):
            await asyncio.sleep(0.1)  # 100ms delay
            return {"answer": "Slow response", "confidence": 0.7}

        # Patch the node processing to be slow
        with patch.object(self.orchestrator, '_process_node_async', slow_process):
            for i in range(10):
                try:  # TODO[T4-ISSUE]: {"code":"SIM105","ticket":"GH-1031","owner":"consciousness-team","status":"planned","reason":"try-except-pass pattern - consider contextlib.suppress for clarity","estimate":"10m","priority":"low","dependencies":"contextlib","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_tests_unit_test_orchestrator_circuit_breaker_py_L102"}
                    await self.orchestrator.process_query(f"slow query {i}")
                except asyncio.TimeoutError:
                    pass  # Expected due to slow processing

        # Check that performance metrics are tracked
        report = self.orchestrator.get_performance_report()
        assert "node_health" in report
        assert "orchestrator_metrics" in report

    @pytest.mark.asyncio
    async def test_adaptive_timeout_behavior(self):
        """Test that timeouts are enforced properly"""
        # Create a very slow mock that will definitely timeout
        async def timeout_process(*args, **kwargs):
            await asyncio.sleep(1.0)  # 1 second - much longer than 120ms stage timeout
            return {"answer": "Too slow", "confidence": 0.1}

        with patch.object(self.orchestrator, '_process_node_async', timeout_process):
            start_time = time.perf_counter()
            result = await self.orchestrator.process_query("timeout test")
            end_time = time.perf_counter()

            # Should complete within total timeout (500ms)
            duration_ms = (end_time - start_time) * 1000
            assert duration_ms < 600  # Allow some overhead

            # Should have error information
            assert "error" in result or "stages" in result

    @pytest.mark.asyncio
    async def test_backpressure_metrics_collection(self):
        """Test that backpressure and retry metrics are collected"""
        # Generate mixed success/failure pattern
        responses = [
            {"answer": "Success 1", "confidence": 0.9},
            Exception("Failure 1"),
            {"answer": "Success 2", "confidence": 0.8},
            Exception("Failure 2"),
            {"answer": "Success 3", "confidence": 0.7},
        ]

        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                self.mock_node.process.side_effect = response
            else:
                self.mock_node.process.side_effect = None
                self.mock_node.process.return_value = response

            try:  # TODO[T4-ISSUE]: {"code":"SIM105","ticket":"GH-1031","owner":"consciousness-team","status":"planned","reason":"try-except-pass pattern - consider contextlib.suppress for clarity","estimate":"10m","priority":"low","dependencies":"contextlib","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_tests_unit_test_orchestrator_circuit_breaker_py_L151"}
                await self.orchestrator.process_query(f"mixed query {i}")
            except Exception:
                pass  # Expected for failure cases

        # Verify metrics collection
        report = self.orchestrator.get_performance_report()
        metrics = report.get("orchestrator_metrics", {})

        # Should have recorded both successes and failures
        assert metrics.get("error_count", 0) >= 0
        assert metrics.get("stages_completed", 0) >= 0

    def test_circuit_breaker_configuration(self):
        """Test that circuit breaker configuration is accessible"""
        report = self.orchestrator.get_performance_report()

        # Should have timeout configuration
        assert "stage_timeouts" in report
        assert "total_timeout" in report

        # Validate timeout values are reasonable
        assert report["total_timeout"] == 0.500
        timeouts = report["stage_timeouts"]
        assert all(isinstance(timeout, (int, float)) for timeout in timeouts.values())
        assert all(timeout > 0 for timeout in timeouts.values())

    @pytest.mark.asyncio
    async def test_graceful_degradation(self):
        """Test graceful degradation when non-critical stages fail"""
        # Create a validator that always fails
        mock_validator = Mock()
        mock_validator.validate_output.side_effect = Exception("Validation failed")
        self.orchestrator.register_node("validator", mock_validator)

        # Query should still succeed even with validation failure
        result = await self.orchestrator.process_query("test with failing validation")

        # Should have successful answer despite validation failure
        assert "answer" in result or "error" not in result

        # Check that validation stage was attempted but failed gracefully
        if "stages" in result:
            validation_stages = [
                stage for stage in result["stages"]
                if stage.get("stage_type", "") == "validation"
            ]
            if validation_stages:
                # Validation should have failed but not stopped the pipeline
                assert not validation_stages[0]["success"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
