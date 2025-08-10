#!/usr/bin/env python3
"""
Performance Benchmarking Tests
Comprehensive performance testing for the integrated LUKHAS AGI system
"""

import asyncio
import json
import statistics
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@dataclass
class PerformanceMetrics:
    """Performance metrics collection"""

    operation: str
    samples: List[float] = field(default_factory=list)
    errors: int = 0

    @property
    def count(self) -> int:
        return len(self.samples)

    @property
    def mean(self) -> float:
        return statistics.mean(self.samples) if self.samples else 0

    @property
    def median(self) -> float:
        return statistics.median(self.samples) if self.samples else 0

    @property
    def stdev(self) -> float:
        return statistics.stdev(self.samples) if len(self.samples) > 1 else 0

    @property
    def p95(self) -> float:
        """95th percentile"""
        if not self.samples:
            return 0
        sorted_samples = sorted(self.samples)
        index = int(len(sorted_samples) * 0.95)
        return (
            sorted_samples[index] if index < len(sorted_samples) else sorted_samples[-1]
        )

    @property
    def p99(self) -> float:
        """99th percentile"""
        if not self.samples:
            return 0
        sorted_samples = sorted(self.samples)
        index = int(len(sorted_samples) * 0.99)
        return (
            sorted_samples[index] if index < len(sorted_samples) else sorted_samples[-1]
        )

    def add_sample(self, latency_ms: float):
        """Add a latency sample"""
        self.samples.append(latency_ms)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for reporting"""
        return {
            "operation": self.operation,
            "samples": self.count,
            "mean_ms": round(self.mean, 2),
            "median_ms": round(self.median, 2),
            "stdev_ms": round(self.stdev, 2),
            "p95_ms": round(self.p95, 2),
            "p99_ms": round(self.p99, 2),
            "min_ms": round(min(self.samples), 2) if self.samples else 0,
            "max_ms": round(max(self.samples), 2) if self.samples else 0,
            "errors": self.errors,
            "success_rate": (
                round((self.count / (self.count + self.errors) * 100), 2)
                if self.count + self.errors > 0
                else 0
            ),
        }


class TestPerformanceBenchmarks:
    """Performance benchmarking test suite"""

    @pytest.fixture
    def benchmark_config(self):
        """Benchmark configuration"""
        return {
            "warmup_iterations": 10,
            "test_iterations": 100,
            "concurrent_users": [1, 5, 10, 20, 50],
            "target_latency_ms": {
                "hub_creation": 50,
                "service_discovery": 10,
                "event_processing": 20,
                "bridge_communication": 30,
                "workflow_execution": 100,
                "health_check": 5,
            },
            "target_throughput": {
                "events_per_second": 1000,
                "requests_per_second": 500,
            },
        }

    @pytest.fixture
    async def mock_system(self):
        """Mock system with realistic timing"""

        class MockSystem:
            def __init__(self):
                self.hub_creation_time = 0.02  # 20ms
                self.service_discovery_time = 0.005  # 5ms
                self.event_processing_time = 0.01  # 10ms
                self.bridge_communication_time = 0.015  # 15ms

            async def create_hub(self, name: str):
                await asyncio.sleep(self.hub_creation_time)
                return {"hub": name, "created": True}

            async def discover_service(self, name: str):
                await asyncio.sleep(self.service_discovery_time)
                return {"service": name, "found": True}

            async def process_event(self, event: Dict[str, Any]):
                await asyncio.sleep(self.event_processing_time)
                return {"processed": True, "event_id": event.get("id")}

            async def bridge_communicate(self, source: str, target: str, data: Any):
                await asyncio.sleep(self.bridge_communication_time)
                return {"forwarded": True, "source": source, "target": target}

            async def execute_workflow(self, steps: int):
                total_time = steps * self.event_processing_time
                await asyncio.sleep(total_time)
                return {"completed": True, "steps": steps}

            async def health_check(self):
                await asyncio.sleep(0.002)  # 2ms
                return {"status": "healthy"}

        return MockSystem()

    async def measure_operation(self, operation, *args, **kwargs) -> Tuple[Any, float]:
        """Measure single operation latency"""
        start = time.perf_counter()
        try:
            result = await operation(*args, **kwargs)
            end = time.perf_counter()
            latency_ms = (end - start) * 1000
            return result, latency_ms
        except Exception:
            end = time.perf_counter()
            latency_ms = (end - start) * 1000
            raise

    @pytest.mark.asyncio
    async def test_hub_creation_performance(self, mock_system, benchmark_config):
        """Benchmark hub creation performance"""
        metrics = PerformanceMetrics("hub_creation")

        # Warmup
        for i in range(benchmark_config["warmup_iterations"]):
            await mock_system.create_hub(f"warmup_{i}")

        # Benchmark
        for i in range(benchmark_config["test_iterations"]):
            try:
                _, latency = await self.measure_operation(
                    mock_system.create_hub, f"hub_{i}"
                )
                metrics.add_sample(latency)
            except Exception:
                metrics.errors += 1

        # Assertions
        assert metrics.mean < benchmark_config["target_latency_ms"]["hub_creation"]
        assert metrics.p95 < benchmark_config["target_latency_ms"]["hub_creation"] * 1.5
        assert metrics.errors == 0

        return metrics

    @pytest.mark.asyncio
    async def test_service_discovery_performance(self, mock_system, benchmark_config):
        """Benchmark service discovery performance"""
        metrics = PerformanceMetrics("service_discovery")

        # Warmup
        for i in range(benchmark_config["warmup_iterations"]):
            await mock_system.discover_service(f"service_{i}")

        # Benchmark
        services = ["ai_interface", "memory_manager", "quantum_hub", "safety_checker"]

        for i in range(benchmark_config["test_iterations"]):
            service = services[i % len(services)]
            try:
                _, latency = await self.measure_operation(
                    mock_system.discover_service, service
                )
                metrics.add_sample(latency)
            except Exception:
                metrics.errors += 1

        # Assertions
        assert metrics.mean < benchmark_config["target_latency_ms"]["service_discovery"]
        assert (
            metrics.p99 < benchmark_config["target_latency_ms"]["service_discovery"] * 2
        )

        return metrics

    @pytest.mark.asyncio
    async def test_event_processing_throughput(self, mock_system, benchmark_config):
        """Benchmark event processing throughput"""
        metrics = PerformanceMetrics("event_processing_throughput")

        # Test different concurrency levels
        for concurrent_users in benchmark_config["concurrent_users"]:
            batch_start = time.perf_counter()

            # Create concurrent tasks
            tasks = []
            for i in range(concurrent_users):
                event = {"id": f"event_{i}", "type": "test", "data": "payload"}
                task = self.measure_operation(mock_system.process_event, event)
                tasks.append(task)

            # Execute concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)

            batch_end = time.perf_counter()
            batch_duration = batch_end - batch_start

            # Calculate throughput
            successful = sum(1 for r in results if not isinstance(r, Exception))
            throughput = successful / batch_duration

            # Record latencies
            for result in results:
                if not isinstance(result, Exception):
                    _, latency = result
                    metrics.add_sample(latency)

            print(f"Concurrency {concurrent_users}: {throughput:.2f} events/sec")

        # Assertions
        assert metrics.mean < benchmark_config["target_latency_ms"]["event_processing"]
        assert metrics.errors == 0

        return metrics

    @pytest.mark.asyncio
    async def test_bridge_communication_latency(self, mock_system, benchmark_config):
        """Benchmark bridge communication latency"""
        metrics = PerformanceMetrics("bridge_communication")

        bridges = [
            ("core", "consciousness"),
            ("consciousness", "quantum"),
            ("memory", "learning"),
            ("safety", "core"),
        ]

        # Benchmark
        for i in range(benchmark_config["test_iterations"]):
            source, target = bridges[i % len(bridges)]
            try:
                _, latency = await self.measure_operation(
                    mock_system.bridge_communicate, source, target, {"test": "data"}
                )
                metrics.add_sample(latency)
            except Exception:
                metrics.errors += 1

        # Assertions
        assert (
            metrics.mean < benchmark_config["target_latency_ms"]["bridge_communication"]
        )
        assert (
            metrics.p95
            < benchmark_config["target_latency_ms"]["bridge_communication"] * 1.5
        )

        return metrics

    @pytest.mark.asyncio
    async def test_workflow_execution_scaling(self, mock_system, benchmark_config):
        """Benchmark workflow execution with different step counts"""
        results = {}

        step_counts = [1, 3, 5, 10, 20]

        for steps in step_counts:
            metrics = PerformanceMetrics(f"workflow_{steps}_steps")

            for i in range(benchmark_config["test_iterations"] // len(step_counts)):
                try:
                    _, latency = await self.measure_operation(
                        mock_system.execute_workflow, steps
                    )
                    metrics.add_sample(latency)
                except Exception:
                    metrics.errors += 1

            results[steps] = metrics

            # Assert linear scaling
            expected_latency = (
                steps * benchmark_config["target_latency_ms"]["event_processing"]
            )
            assert metrics.mean < expected_latency * 1.2  # Allow 20% overhead

        return results

    @pytest.mark.asyncio
    async def test_system_under_stress(self, mock_system, benchmark_config):
        """Stress test the system with high load"""
        metrics = PerformanceMetrics("stress_test")

        # Generate high load
        stress_duration = 5  # seconds
        operations_per_batch = 100

        start_time = time.time()
        total_operations = 0

        while time.time() - start_time < stress_duration:
            tasks = []

            # Mix of operations
            for i in range(operations_per_batch):
                if i % 4 == 0:
                    task = mock_system.create_hub(f"stress_hub_{i}")
                elif i % 4 == 1:
                    task = mock_system.discover_service("test_service")
                elif i % 4 == 2:
                    task = mock_system.process_event({"id": f"stress_{i}"})
                else:
                    task = mock_system.health_check()

                tasks.append(task)

            # Execute batch
            batch_start = time.perf_counter()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            batch_end = time.perf_counter()

            batch_latency = (batch_end - batch_start) * 1000
            metrics.add_sample(
                batch_latency / operations_per_batch
            )  # Per-operation latency

            successful = sum(1 for r in results if not isinstance(r, Exception))
            total_operations += successful

        end_time = time.time()
        total_duration = end_time - start_time

        # Calculate overall metrics
        throughput = total_operations / total_duration

        print(f"Stress test: {throughput:.2f} ops/sec over {total_duration:.2f}s")
        print(f"Average latency: {metrics.mean:.2f}ms, P99: {metrics.p99:.2f}ms")

        # Assertions
        assert throughput > 500  # At least 500 ops/sec under stress
        assert metrics.p99 < 100  # P99 latency under 100ms

        return {
            "metrics": metrics,
            "throughput": throughput,
            "total_operations": total_operations,
        }

    @pytest.mark.asyncio
    async def test_memory_usage_profile(self, mock_system, benchmark_config):
        """Profile memory usage during operations"""
        import os

        import psutil

        process = psutil.Process(os.getpid())
        memory_samples = []

        # Baseline memory
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_samples.append(("baseline", baseline_memory))

        # Create many objects
        hubs = []
        for i in range(1000):
            hub = await mock_system.create_hub(f"memory_test_{i}")
            hubs.append(hub)

            if i % 100 == 0:
                current_memory = process.memory_info().rss / 1024 / 1024
                memory_samples.append((f"hubs_{i}", current_memory))

        # Peak memory
        peak_memory = max(m[1] for m in memory_samples)
        memory_increase = peak_memory - baseline_memory

        print(
            f"Memory usage - Baseline: {baseline_memory:.2f}MB, Peak: {peak_memory:.2f}MB"
        )
        print(f"Memory increase: {memory_increase:.2f}MB for 1000 hubs")

        # Cleanup
        hubs.clear()
        await asyncio.sleep(0.1)  # Allow GC

        final_memory = process.memory_info().rss / 1024 / 1024
        memory_samples.append(("after_cleanup", final_memory))

        # Assertions
        assert memory_increase < 100  # Less than 100MB increase for 1000 objects
        assert final_memory < baseline_memory * 1.5  # Memory properly released

        return memory_samples

    def generate_performance_report(
        self, all_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_operations": sum(
                    m.count if isinstance(m, PerformanceMetrics) else 0
                    for m in all_metrics.values()
                ),
                "total_errors": sum(
                    m.errors if isinstance(m, PerformanceMetrics) else 0
                    for m in all_metrics.values()
                ),
            },
            "operations": {},
            "recommendations": [],
        }

        # Process each metric
        for name, metric in all_metrics.items():
            if isinstance(metric, PerformanceMetrics):
                report["operations"][name] = metric.to_dict()

                # Generate recommendations
                if metric.mean > 50:
                    report["recommendations"].append(
                        f"Optimize {name} - average latency {metric.mean:.2f}ms exceeds 50ms"
                    )
                if metric.p99 > metric.mean * 3:
                    report["recommendations"].append(
                        f"Investigate {name} tail latency - P99 is {metric.p99/metric.mean:.1f}x mean"
                    )

        return report

    def plot_performance_results(
        self,
        metrics: Dict[str, PerformanceMetrics],
        output_path: str = "performance_results.png",
    ):
        """Plot performance visualization"""
        operations = []
        means = []
        p95s = []
        p99s = []

        for name, metric in metrics.items():
            if isinstance(metric, PerformanceMetrics):
                operations.append(metric.operation)
                means.append(metric.mean)
                p95s.append(metric.p95)
                p99s.append(metric.p99)

        # Create plot
        fig, ax = plt.subplots(figsize=(12, 8))

        x = np.arange(len(operations))
        width = 0.25

        bars1 = ax.bar(x - width, means, width, label="Mean", alpha=0.8)
        bars2 = ax.bar(x, p95s, width, label="P95", alpha=0.8)
        bars3 = ax.bar(x + width, p99s, width, label="P99", alpha=0.8)

        ax.set_ylabel("Latency (ms)")
        ax.set_title("Operation Performance Metrics")
        ax.set_xticks(x)
        ax.set_xticklabels(operations, rotation=45, ha="right")
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Add value labels
        for bars in [bars1, bars2, bars3]:
            for bar in bars:
                height = bar.get_height()
                ax.annotate(
                    f"{height:.1f}",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha="center",
                    va="bottom",
                    fontsize=8,
                )

        plt.tight_layout()
        plt.savefig(output_path, dpi=150)
        plt.close()

        print(f"Performance plot saved to {output_path}")


@pytest.mark.asyncio
async def test_full_performance_suite():
    """Run complete performance benchmark suite"""
    benchmarks = TestPerformanceBenchmarks()
    config = benchmarks.benchmark_config()
    system = await benchmarks.mock_system()

    # Run all benchmarks
    results = {}

    print("Running performance benchmarks...")

    # Individual operation benchmarks
    results["hub_creation"] = await benchmarks.test_hub_creation_performance(
        system, config
    )
    results["service_discovery"] = await benchmarks.test_service_discovery_performance(
        system, config
    )
    results["event_throughput"] = await benchmarks.test_event_processing_throughput(
        system, config
    )
    results["bridge_latency"] = await benchmarks.test_bridge_communication_latency(
        system, config
    )

    # Scaling tests
    workflow_results = await benchmarks.test_workflow_execution_scaling(system, config)
    results.update(workflow_results)

    # Stress test
    stress_results = await benchmarks.test_system_under_stress(system, config)
    results["stress_test"] = stress_results["metrics"]

    # Generate report
    report = benchmarks.generate_performance_report(results)

    # Save report
    report_path = Path("performance_benchmark_report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\nPerformance report saved to {report_path}")

    # Generate visualization
    benchmarks.plot_performance_results(results)

    return report


if __name__ == "__main__":
    # Run the benchmark suite
    asyncio.run(test_full_performance_suite())
