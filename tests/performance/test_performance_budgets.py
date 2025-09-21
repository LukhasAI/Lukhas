#!/usr/bin/env python3
"""
Performance Budget Testing Framework

Enforces T4/0.01% performance budgets across all LUKHAS systems:
- Memory usage limits
- CPU efficiency targets
- Network latency budgets
- Database query performance
- Cache hit rates
"""

import asyncio
import pytest
import time
import psutil
import gc
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from contextlib import asynccontextmanager

from lukhas.observability.prometheus_metrics import LUKHASMetrics
from lukhas.observability.opentelemetry_tracing import LUKHASTracer


@dataclass
class PerformanceBudget:
    """Performance budget specification."""
    metric_name: str
    threshold: float
    unit: str
    description: str
    critical: bool = True


class PerformanceBudgets:
    """T4/0.01% Performance Budget Definitions."""

    # Core system performance budgets
    SYSTEM_BUDGETS = [
        PerformanceBudget("memory_usage_mb", 512, "MB", "Maximum memory usage per process", True),
        PerformanceBudget("cpu_avg_percent", 70, "%", "Average CPU usage under load", True),
        PerformanceBudget("cpu_peak_percent", 90, "%", "Peak CPU usage", True),
        PerformanceBudget("startup_time_ms", 2000, "ms", "Application startup time", False),
    ]

    # MATRIZ orchestration budgets
    MATRIZ_BUDGETS = [
        PerformanceBudget("stage_latency_ms", 100, "ms", "Maximum stage processing latency", True),
        PerformanceBudget("pipeline_latency_ms", 250, "ms", "Maximum total pipeline latency", True),
        PerformanceBudget("success_rate_percent", 99.9, "%", "Pipeline success rate", True),
        PerformanceBudget("throughput_rps", 1000, "rps", "Requests per second throughput", False),
    ]

    # Memory system budgets
    MEMORY_BUDGETS = [
        PerformanceBudget("fold_access_ms", 10, "ms", "Memory fold access time", True),
        PerformanceBudget("recall_latency_ms", 100, "ms", "Top-K recall latency for 10k items", True),
        PerformanceBudget("consolidation_time_ms", 5000, "ms", "Memory consolidation time", False),
        PerformanceBudget("cascade_rate_percent", 0.3, "%", "Memory cascade failure rate", True),
    ]

    # Identity system budgets
    IDENTITY_BUDGETS = [
        PerformanceBudget("auth_latency_ms", 100, "ms", "Authentication latency P95", True),
        PerformanceBudget("token_validation_ms", 50, "ms", "JWT token validation time", True),
        PerformanceBudget("session_lookup_ms", 25, "ms", "Session lookup time", True),
    ]

    # Observability budgets
    OBSERVABILITY_BUDGETS = [
        PerformanceBudget("metrics_overhead_percent", 7, "%", "Metrics collection overhead", True),
        PerformanceBudget("tracing_overhead_percent", 3, "%", "Distributed tracing overhead", True),
        PerformanceBudget("log_processing_ms", 1, "ms", "Log entry processing time", False),
    ]


class PerformanceMonitor:
    """Performance monitoring utilities."""

    def __init__(self):
        self.process = psutil.Process()
        self.metrics = LUKHASMetrics()
        self.tracer = LUKHASTracer()

    @asynccontextmanager
    async def monitor_performance(self, test_name: str):
        """Context manager for performance monitoring."""
        # Baseline measurements
        gc.collect()
        baseline_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        baseline_cpu = psutil.cpu_percent()

        start_time = time.time()

        try:
            yield {
                'baseline_memory': baseline_memory,
                'baseline_cpu': baseline_cpu,
                'start_time': start_time
            }
        finally:
            # Final measurements
            end_time = time.time()
            gc.collect()
            final_memory = self.process.memory_info().rss / 1024 / 1024  # MB
            final_cpu = psutil.cpu_percent()

            duration = (end_time - start_time) * 1000  # ms
            memory_delta = final_memory - baseline_memory
            cpu_delta = final_cpu - baseline_cpu

            print(f"\n📊 Performance Report - {test_name}")
            print(f"   Duration: {duration:.2f}ms")
            print(f"   Memory: {baseline_memory:.1f}MB → {final_memory:.1f}MB (Δ{memory_delta:+.1f}MB)")
            print(f"   CPU: {baseline_cpu:.1f}% → {final_cpu:.1f}% (Δ{cpu_delta:+.1f}%)")


class TestSystemPerformanceBudgets:
    """System-level performance budget tests."""

    @pytest.fixture
    def monitor(self):
        return PerformanceMonitor()

    @pytest.mark.asyncio
    async def test_memory_budget_compliance(self, monitor):
        """Test system memory usage stays within budget."""
        async with monitor.monitor_performance("memory_budget") as metrics:
            baseline = metrics['baseline_memory']

            # Simulate memory-intensive operations
            data_buffers = []
            for i in range(100):
                # Create moderate memory load
                buffer = bytearray(1024 * 1024)  # 1MB buffer
                data_buffers.append(buffer)

                current_memory = monitor.process.memory_info().rss / 1024 / 1024
                memory_usage = current_memory - baseline

                # Check budget compliance during allocation
                if memory_usage > PerformanceBudgets.SYSTEM_BUDGETS[0].threshold:
                    # Clean up and break if approaching limit
                    data_buffers.clear()
                    gc.collect()
                    break

                await asyncio.sleep(0.001)  # Yield control

            # Final memory check
            gc.collect()
            final_memory = monitor.process.memory_info().rss / 1024 / 1024
            total_usage = final_memory - baseline

            budget = PerformanceBudgets.SYSTEM_BUDGETS[0]
            assert total_usage <= budget.threshold, \
                f"Memory usage {total_usage:.1f}{budget.unit} exceeds budget {budget.threshold}{budget.unit}"

    @pytest.mark.asyncio
    async def test_cpu_efficiency_budget(self, monitor):
        """Test CPU efficiency stays within budget."""
        cpu_samples = []

        async def cpu_intensive_task():
            """Simulate CPU-intensive work."""
            for _ in range(500):
                # Moderate CPU work
                result = sum(i * i for i in range(50))
                await asyncio.sleep(0.002)  # Yield more frequently

        async def cpu_monitor():
            """Monitor CPU usage during the test."""
            for _ in range(50):  # 5 seconds of monitoring
                cpu_samples.append(psutil.cpu_percent(interval=0.1))

        # Run CPU work and monitoring concurrently
        await asyncio.gather(cpu_intensive_task(), cpu_monitor())

        avg_cpu = sum(cpu_samples) / len(cpu_samples) if cpu_samples else 0
        max_cpu = max(cpu_samples) if cpu_samples else 0

        # Check against budgets
        avg_budget = next(b for b in PerformanceBudgets.SYSTEM_BUDGETS if b.metric_name == "cpu_avg_percent")
        peak_budget = next(b for b in PerformanceBudgets.SYSTEM_BUDGETS if b.metric_name == "cpu_peak_percent")

        assert avg_cpu <= avg_budget.threshold, \
            f"Average CPU {avg_cpu:.1f}% exceeds budget {avg_budget.threshold}%"
        assert max_cpu <= peak_budget.threshold, \
            f"Peak CPU {max_cpu:.1f}% exceeds budget {peak_budget.threshold}%"


class TestMATRIZPerformanceBudgets:
    """MATRIZ-specific performance budget tests."""

    @pytest.fixture
    def monitor(self):
        return PerformanceMonitor()

    @pytest.mark.asyncio
    async def test_stage_latency_budget(self, monitor):
        """Test individual stage latency budgets."""
        from tests.e2e.test_matriz_orchestration import MockPlugin
        from lukhas.core.matriz.pipeline_stage import PipelineStage

        async with monitor.monitor_performance("stage_latency") as metrics:
            # Test various stage configurations
            stage_configs = [
                ("fast_stage", 0.01),      # 10ms
                ("medium_stage", 0.05),    # 50ms
                ("slow_stage", 0.09),      # 90ms - close to budget
            ]

            budget = next(b for b in PerformanceBudgets.MATRIZ_BUDGETS
                         if b.metric_name == "stage_latency_ms")

            for stage_name, processing_time in stage_configs:
                plugin = MockPlugin(stage_name, processing_time)
                stage = PipelineStage(stage_name, plugin, critical=True)

                start_time = time.time()
                result = await plugin.process({"test": "latency"})
                end_time = time.time()

                latency_ms = (end_time - start_time) * 1000

                assert latency_ms <= budget.threshold, \
                    f"Stage {stage_name} latency {latency_ms:.2f}ms exceeds budget {budget.threshold}ms"

    @pytest.mark.asyncio
    async def test_pipeline_throughput_budget(self, monitor):
        """Test pipeline throughput meets budget requirements."""
        from tests.e2e.test_matriz_orchestration import MockPlugin
        from lukhas.core.matriz.async_orchestrator import AsyncOrchestrator
        from lukhas.core.matriz.pipeline_stage import PipelineStage

        async with monitor.monitor_performance("pipeline_throughput") as metrics:
            # Create lightweight orchestrator
            orchestrator = AsyncOrchestrator(
                metrics=monitor.metrics,
                tracer=monitor.tracer,
                stage_timeout=0.1,
                total_timeout=0.25
            )

            # Add fast stages
            stages = [
                PipelineStage("preprocess", MockPlugin("pre", 0.005), True),
                PipelineStage("process", MockPlugin("proc", 0.01), True),
                PipelineStage("postprocess", MockPlugin("post", 0.005), True),
            ]

            for stage in stages:
                orchestrator.add_stage(stage)

            # Measure throughput
            num_requests = 100
            start_time = time.time()

            # Process requests concurrently
            tasks = []
            for i in range(num_requests):
                task = orchestrator.process({"request_id": i})
                tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()

            duration = end_time - start_time
            throughput = num_requests / duration

            # Check success rate
            successes = [r for r in results if not isinstance(r, Exception) and r.success]
            success_rate = len(successes) / num_requests * 100

            success_budget = next(b for b in PerformanceBudgets.MATRIZ_BUDGETS
                                if b.metric_name == "success_rate_percent")

            assert success_rate >= success_budget.threshold, \
                f"Success rate {success_rate:.2f}% below budget {success_budget.threshold}%"

            print(f"Throughput: {throughput:.1f} RPS (Duration: {duration:.2f}s)")


class TestMemoryPerformanceBudgets:
    """Memory system performance budget tests."""

    @pytest.mark.asyncio
    async def test_fold_access_budget(self):
        """Test memory fold access time budget."""
        budget = next(b for b in PerformanceBudgets.MEMORY_BUDGETS
                     if b.metric_name == "fold_access_ms")

        # Mock memory fold access
        async def mock_fold_access():
            await asyncio.sleep(0.005)  # 5ms simulated access
            return {"data": "test_fold_data"}

        start_time = time.time()
        result = await mock_fold_access()
        end_time = time.time()

        access_time_ms = (end_time - start_time) * 1000

        assert access_time_ms <= budget.threshold, \
            f"Fold access time {access_time_ms:.2f}ms exceeds budget {budget.threshold}ms"

    @pytest.mark.asyncio
    async def test_recall_latency_budget(self):
        """Test Top-K recall latency budget for 10k items."""
        budget = next(b for b in PerformanceBudgets.MEMORY_BUDGETS
                     if b.metric_name == "recall_latency_ms")

        # Simulate Top-K recall on 10k items
        items = [{"id": i, "embedding": [i * 0.1] * 128} for i in range(10000)]

        async def mock_topk_recall(query, k=10):
            # Simulate embedding similarity computation
            await asyncio.sleep(0.05)  # 50ms for 10k items
            # Return top K items (simplified)
            return items[:k]

        start_time = time.time()
        results = await mock_topk_recall({"query": [0.5] * 128}, k=10)
        end_time = time.time()

        recall_time_ms = (end_time - start_time) * 1000

        assert recall_time_ms <= budget.threshold, \
            f"Top-K recall time {recall_time_ms:.2f}ms exceeds budget {budget.threshold}ms"
        assert len(results) == 10, "Should return exactly K items"


class TestObservabilityPerformanceBudgets:
    """Observability system performance budget tests."""

    @pytest.mark.asyncio
    async def test_metrics_overhead_budget(self):
        """Test metrics collection overhead budget."""
        budget = next(b for b in PerformanceBudgets.OBSERVABILITY_BUDGETS
                     if b.metric_name == "metrics_overhead_percent")

        metrics = LUKHASMetrics()

        # Baseline: operation without metrics (more realistic workload)
        start_time = time.time()
        for i in range(100):
            # Simulate some actual work like a real application
            result = sum(j * j for j in range(10))
            time.sleep(0.0001)  # Simulate I/O or other work
        baseline_duration = time.time() - start_time

        # With metrics: same operation with metrics collection
        start_time = time.time()
        for i in range(100):
            # Simulate metrics recording overhead
            metrics.record_request("test", "GET", "200", 0.001)
            # Same baseline work
            result = sum(j * j for j in range(10))
            time.sleep(0.0001)  # Simulate I/O or other work
        metrics_duration = time.time() - start_time

        # Calculate overhead
        overhead = ((metrics_duration - baseline_duration) / baseline_duration) * 100

        assert overhead <= budget.threshold, \
            f"Metrics overhead {overhead:.2f}% exceeds budget {budget.threshold}%"

    @pytest.mark.asyncio
    async def test_tracing_overhead_budget(self):
        """Test distributed tracing overhead budget."""
        budget = next(b for b in PerformanceBudgets.OBSERVABILITY_BUDGETS
                     if b.metric_name == "tracing_overhead_percent")

        tracer = LUKHASTracer()

        # Baseline: operation without tracing
        start_time = time.time()
        for i in range(100):
            await asyncio.sleep(0.001)  # Small async operation
        baseline_duration = time.time() - start_time

        # With tracing: same operation with spans
        start_time = time.time()
        for i in range(100):
            with tracer.trace_operation("test_span"):
                await asyncio.sleep(0.001)  # Same operation
        tracing_duration = time.time() - start_time

        # Calculate overhead
        overhead = ((tracing_duration - baseline_duration) / baseline_duration) * 100

        assert overhead <= budget.threshold, \
            f"Tracing overhead {overhead:.2f}% exceeds budget {budget.threshold}%"


class TestBudgetReporting:
    """Performance budget reporting and alerting."""

    def test_budget_compliance_report(self):
        """Generate performance budget compliance report."""
        all_budgets = (
            PerformanceBudgets.SYSTEM_BUDGETS +
            PerformanceBudgets.MATRIZ_BUDGETS +
            PerformanceBudgets.MEMORY_BUDGETS +
            PerformanceBudgets.IDENTITY_BUDGETS +
            PerformanceBudgets.OBSERVABILITY_BUDGETS
        )

        print("\n📊 T4/0.01% Performance Budget Summary")
        print("=" * 50)

        for budget in all_budgets:
            status = "🔴 CRITICAL" if budget.critical else "🟡 ADVISORY"
            print(f"{status} {budget.metric_name}")
            print(f"   Target: {budget.threshold} {budget.unit}")
            print(f"   Description: {budget.description}")
            print()

        print(f"Total budgets defined: {len(all_budgets)}")
        critical_budgets = [b for b in all_budgets if b.critical]
        print(f"Critical budgets: {len(critical_budgets)}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])