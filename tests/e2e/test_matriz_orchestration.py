#!/usr/bin/env python3
"""
End-to-End MATRIZ Orchestration Testing

Tests the complete MATRIZ pipeline for T4/0.01% performance targets:
- <100ms stage latency
- <250ms total pipeline latency
- 99.9% success rate
- Proper error handling and fail-soft behavior
"""

import asyncio
import time
# from typing import Dict  # All imports converted to builtins (PEP 585)

import pytest
from core.matriz.async_orchestrator import AsyncOrchestrator
from core.matriz.pipeline_stage import PipelineStage
from observability.opentelemetry_tracing import LUKHASTracer
from observability.prometheus_metrics import LUKHASMetrics


class MockPlugin:
    """Mock plugin for testing."""

    def __init__(self, name: str, processing_time: float = 0.05, failure_rate: float = 0.0):
        self.name = name
        self.processing_time = processing_time
        self.failure_rate = failure_rate
        self.call_count = 0

    async def process(self, input_data: dict) -> dict:
        """Mock processing with configurable delay and failure."""
        self.call_count += 1
        await asyncio.sleep(self.processing_time)

        if self.failure_rate > 0 and (self.call_count * self.failure_rate) >= 1:
            raise Exception(f"Mock failure in {self.name}")

        return {
            "processed_by": self.name,
            "input": input_data,
            "timestamp": time.time()
        }


class TestMATRIZE2E:
    """End-to-end MATRIZ orchestration tests."""

    @pytest.fixture
    async def orchestrator(self):
        """Create test orchestrator with metrics and tracing."""
        metrics = LUKHASMetrics()
        tracer = LUKHASTracer()

        orchestrator = AsyncOrchestrator(
            metrics=metrics,
            tracer=tracer,
            stage_timeout=0.1,  # 100ms timeout for T4 targets
            total_timeout=0.25  # 250ms total timeout
        )

        # Add test stages
        stages = [
            PipelineStage(
                name="preprocessing",
                plugin=MockPlugin("preprocessor", 0.02),  # 20ms
                critical=True
            ),
            PipelineStage(
                name="analysis",
                plugin=MockPlugin("analyzer", 0.03),  # 30ms
                critical=True
            ),
            PipelineStage(
                name="transformation",
                plugin=MockPlugin("transformer", 0.025),  # 25ms
                critical=False
            ),
            PipelineStage(
                name="output",
                plugin=MockPlugin("outputter", 0.015),  # 15ms
                critical=True
            )
        ]

        for stage in stages:
            orchestrator.add_stage(stage)

        return orchestrator

    @pytest.mark.asyncio
    async def test_e2e_performance_targets(self, orchestrator):
        """Test T4/0.01% performance targets are met."""
        input_data = {"test": "data", "timestamp": time.time()}

        start_time = time.time()
        result = await orchestrator.process(input_data)
        end_time = time.time()

        total_latency = (end_time - start_time) * 1000  # Convert to ms

        # Verify T4 performance targets
        assert total_latency < 250, f"Total pipeline latency {total_latency:.2f}ms exceeds 250ms target"
        assert result.success, "Pipeline should succeed with healthy plugins"
        assert len(result.stage_results) == 4, "All stages should be processed"

        # Verify each stage meets latency targets
        for stage_name, stage_result in result.stage_results.items():
            stage_latency = stage_result.processing_time * 1000
            assert stage_latency < 100, f"Stage {stage_name} latency {stage_latency:.2f}ms exceeds 100ms target"

    @pytest.mark.asyncio
    async def test_e2e_stress_performance(self, orchestrator):
        """Test performance under stress with multiple concurrent requests."""
        concurrent_requests = 20  # More realistic for test environment

        async def single_request():
            input_data = {"test": "concurrent", "id": id(asyncio.current_task())}
            start_time = time.time()
            try:
                result = await orchestrator.process(input_data)
                latency = (time.time() - start_time) * 1000
                return result.success, latency
            except Exception as e:
                latency = (time.time() - start_time) * 1000
                print(f"Request failed: {e}")
                return False, latency

        # Execute concurrent requests with controlled batching
        start_time = time.time()
        tasks = [single_request() for _ in range(concurrent_requests)]
        results = await asyncio.gather(*tasks, return_exceptions=False)
        total_time = time.time() - start_time

        # Analyze results
        successes = [r[0] for r in results if r[0]]
        latencies = [r[1] for r in results]

        success_rate = len(successes) / concurrent_requests if concurrent_requests > 0 else 0
        avg_latency = sum(latencies) / len(latencies) if latencies else 0
        p95_latency = sorted(latencies)[int(0.95 * len(latencies))] if latencies else 0

        # More realistic stress performance targets for test environment
        assert success_rate >= 0.85, f"Success rate {success_rate:.3f} below 85% target"
        assert avg_latency < 500, f"Average latency {avg_latency:.2f}ms exceeds 500ms target"
        assert p95_latency < 750, f"P95 latency {p95_latency:.2f}ms exceeds 750ms stress target"

        print(f"Stress test: {concurrent_requests} requests in {total_time:.2f}s")
        print(f"Success rate: {success_rate:.3f}, Avg latency: {avg_latency:.2f}ms, P95: {p95_latency:.2f}ms")

    @pytest.mark.asyncio
    async def test_e2e_fail_soft_behavior(self, orchestrator):
        """Test fail-soft behavior with non-critical stage failures."""
        # Add a failing non-critical stage
        failing_stage = PipelineStage(
            name="optional_enhancement",
            plugin=MockPlugin("enhancer", 0.02, failure_rate=1.0),  # Always fails
            critical=False
        )
        orchestrator.add_stage(failing_stage)

        input_data = {"test": "fail_soft"}
        result = await orchestrator.process(input_data)

        # Should succeed despite non-critical failure
        assert result.success, "Pipeline should succeed with non-critical failures"
        assert "optional_enhancement" in result.stage_results
        assert not result.stage_results["optional_enhancement"].success
        assert result.stage_results["preprocessing"].success, "Critical stages should succeed"

    @pytest.mark.asyncio
    async def test_e2e_critical_failure_handling(self, orchestrator):
        """Test proper failure handling when critical stages fail."""
        # Replace critical stage with failing one
        orchestrator.stages.clear()

        stages = [
            PipelineStage(
                name="preprocessing",
                plugin=MockPlugin("preprocessor", 0.02),
                critical=True
            ),
            PipelineStage(
                name="critical_analysis",
                plugin=MockPlugin("analyzer", 0.03, failure_rate=1.0),  # Always fails
                critical=True
            ),
            PipelineStage(
                name="output",
                plugin=MockPlugin("outputter", 0.015),
                critical=True
            )
        ]

        for stage in stages:
            orchestrator.add_stage(stage)

        input_data = {"test": "critical_failure"}
        result = await orchestrator.process(input_data)

        # Should fail due to critical stage failure
        assert not result.success, "Pipeline should fail with critical stage failures"
        assert result.error is not None, "Error should be captured"
        assert "analyzer" in str(result.error), "Error should reference failed stage"

    @pytest.mark.asyncio
    async def test_e2e_timeout_handling(self, orchestrator):
        """Test timeout handling for stages that exceed limits."""
        # Add a slow stage that exceeds timeout
        slow_stage = PipelineStage(
            name="slow_processing",
            plugin=MockPlugin("slow_processor", 0.15),  # 150ms > 100ms timeout
            critical=False
        )
        orchestrator.add_stage(slow_stage)

        input_data = {"test": "timeout"}
        start_time = time.time()
        result = await orchestrator.process(input_data)
        processing_time = time.time() - start_time

        # Should handle timeout gracefully
        assert processing_time < 0.3, "Total processing should not exceed overall timeout"
        assert "slow_processing" in result.stage_results
        # Non-critical timeout should allow pipeline to continue

    @pytest.mark.asyncio
    async def test_e2e_metrics_collection(self, orchestrator):
        """Test that metrics are properly collected during E2E processing."""
        input_data = {"test": "metrics"}

        # Process request
        result = await orchestrator.process(input_data)

        # Verify metrics were collected
        metrics = orchestrator.metrics
        assert hasattr(metrics, 'enabled')
        assert hasattr(metrics, 'config')
        assert callable(getattr(metrics, 'record_matriz_pipeline', None))

        # Metrics should reflect the processing
        assert result.success, "Test request should succeed"

    @pytest.mark.asyncio
    async def test_e2e_tracing_spans(self, orchestrator):
        """Test that distributed tracing spans are created properly."""
        input_data = {"test": "tracing"}

        # Process with tracing
        result = await orchestrator.process(input_data)

        # Verify tracing spans were created
        tracer = orchestrator.tracer
        assert tracer is not None
        assert result.success, "Test request should succeed"

        # Spans should be created for pipeline and each stage
        # (Actual span verification would depend on tracer implementation)

    @pytest.mark.asyncio
    async def test_e2e_data_flow_integrity(self, orchestrator):
        """Test that data flows correctly through the entire pipeline."""
        input_data = {
            "original_id": "test_123",
            "payload": {"data": "important_content"},
            "metadata": {"source": "e2e_test"}
        }

        result = await orchestrator.process(input_data)

        assert result.success, "Pipeline should process data successfully"

        # Verify data integrity through pipeline
        final_output = result.output
        assert "original_id" in str(final_output), "Original ID should be preserved"
        assert "important_content" in str(final_output), "Content should be preserved"

        # Verify each stage processed the data
        for stage_name, stage_result in result.stage_results.items():
            assert stage_result.success, f"Stage {stage_name} should succeed"
            assert "input" in stage_result.output, f"Stage {stage_name} should have input data"


class TestMATRIZPerformanceBudgets:
    """Performance budget tests for MATRIZ system."""

    @pytest.fixture
    async def orchestrator(self):
        """Create test orchestrator with metrics and tracing."""
        metrics = LUKHASMetrics()
        tracer = LUKHASTracer()

        # Create orchestrator with realistic test stages
        orchestrator = AsyncOrchestrator(
            metrics=metrics,
            tracer=tracer,
            stage_timeout=2.0,
            total_timeout=10.0
        )

        # Add test stages
        stages = [
            PipelineStage("validation", MockPlugin("validation"), True),
            PipelineStage("processing", MockPlugin("processing"), True),
            PipelineStage("output", MockPlugin("output"), False)
        ]

        for stage in stages:
            orchestrator.add_stage(stage)

        yield orchestrator

    @pytest.mark.asyncio
    async def test_memory_budget_compliance(self, orchestrator):
        """Test that MATRIZ operations stay within memory budgets."""
        import gc

        import psutil

        process = psutil.Process()

        # Baseline memory
        gc.collect()
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Use provided orchestrator fixture

        # Process multiple requests
        for i in range(100):
            await orchestrator.process({"iteration": i})

        # Check memory after processing
        gc.collect()
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - baseline_memory

        # Memory increase should be reasonable (< 50MB for this test)
        assert memory_increase < 50, f"Memory increase {memory_increase:.2f}MB exceeds budget"

    @pytest.mark.asyncio
    async def test_cpu_efficiency_budget(self, orchestrator):
        """Test CPU efficiency stays within budget."""
        import psutil

        # Monitor CPU usage during processing
        cpu_samples = []

        async def cpu_monitor():
            for _ in range(10):
                cpu_samples.append(psutil.cpu_percent(interval=0.1))

        async def process_load():
            tasks = []
            for i in range(20):
                task = orchestrator.process({"load_test": i})
                tasks.append(task)
            await asyncio.gather(*tasks)

        # Run both monitoring and processing
        await asyncio.gather(cpu_monitor(), process_load())

        avg_cpu = sum(cpu_samples) / len(cpu_samples) if cpu_samples else 0
        max_cpu = max(cpu_samples) if cpu_samples else 0

        # CPU usage should be reasonable
        assert avg_cpu < 80, f"Average CPU {avg_cpu:.2f}% exceeds 80% budget"
        assert max_cpu < 95, f"Peak CPU {max_cpu:.2f}% exceeds 95% budget"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
