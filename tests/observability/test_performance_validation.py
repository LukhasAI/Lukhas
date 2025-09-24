#!/usr/bin/env python3
"""
Performance Validation for LUKHAS Observability System
Validates that observability operations meet <10ms overhead requirements.
"""

import asyncio
import statistics
import time
import pytest
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch, MagicMock

# Test imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lukhas.observability.evidence_collection import (
    EvidenceCollectionEngine, EvidenceType, ComplianceRegime
)
from lukhas.observability.advanced_metrics import AdvancedMetricsSystem
from lukhas.observability.performance_regression import PerformanceRegressionDetector
from lukhas.observability.intelligent_alerting import IntelligentAlertingSystem
from lukhas.observability.security_hardening import ObservabilitySecurityHardening


class TestPerformanceValidation:
    """Validate performance requirements for observability operations"""

    @pytest.fixture
    async def temp_evidence_dir(self):
        """Create temporary directory for evidence storage"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def mock_dependencies(self):
        """Mock external dependencies for performance testing"""
        mock_prometheus = MagicMock()
        mock_prometheus.lane = "test"
        mock_prometheus.errors_total = MagicMock()
        mock_prometheus.errors_total.labels.return_value.inc = MagicMock()
        return {'prometheus_metrics': mock_prometheus}

    @pytest.fixture
    async def evidence_engine(self, temp_evidence_dir):
        """Create evidence collection engine for performance testing"""
        engine = EvidenceCollectionEngine(
            storage_path=str(temp_evidence_dir),
            retention_days=30,
            compression_enabled=True,
            encryption_enabled=True,
            chain_block_size=100,  # Larger for performance
        )
        yield engine
        await engine.shutdown()

    @pytest.fixture
    def advanced_metrics_system(self, mock_dependencies):
        """Create advanced metrics system for performance testing"""
        with patch('lukhas.observability.advanced_metrics.get_lukhas_metrics', return_value=mock_dependencies['prometheus_metrics']):
            system = AdvancedMetricsSystem(
                enable_anomaly_detection=False,  # Disable for pure performance testing
                enable_ml_features=False,
                metric_retention_hours=1,  # Short retention for testing
            )
            yield system
            asyncio.create_task(system.shutdown())

    @pytest.fixture
    async def performance_detector(self, mock_dependencies):
        """Create performance regression detector for testing"""
        with patch('lukhas.observability.performance_regression.get_advanced_metrics', return_value=mock_dependencies['prometheus_metrics']):
            with patch('lukhas.observability.performance_regression.get_alerting_system', return_value=MagicMock()):
                detector = PerformanceRegressionDetector(
                    baseline_window_days=1,
                    enable_ml_detection=False,  # Disable for performance testing
                    enable_seasonal_analysis=False,
                )
                yield detector
                await detector.shutdown()

    @pytest.fixture
    async def security_hardening(self, temp_evidence_dir):
        """Create security hardening for performance testing"""
        hardening = ObservabilitySecurityHardening(
            key_storage_path=str(temp_evidence_dir / "keys"),
            enable_encryption=True,
            enable_signing=True,
        )
        yield hardening
        await hardening.shutdown()

    @pytest.mark.asyncio
    async def test_evidence_collection_performance_requirement(self, evidence_engine):
        """Test that evidence collection meets <10ms overhead requirement"""
        print("\n=== Evidence Collection Performance Test ===")

        # Warmup
        for i in range(10):
            await evidence_engine.collect_evidence(
                evidence_type=EvidenceType.SYSTEM_EVENT,
                source_component="warmup",
                operation="warmup_operation",
                payload={"warmup": i},
            )

        # Performance test
        durations = []
        test_iterations = 1000

        for i in range(test_iterations):
            start_time = time.perf_counter()

            await evidence_engine.collect_evidence(
                evidence_type=EvidenceType.PERFORMANCE_METRIC,
                source_component="performance_test",
                operation="performance_validation",
                payload={
                    "metric_name": "test_latency",
                    "value": 0.1,
                    "iteration": i,
                },
            )

            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            durations.append(duration_ms)

        # Calculate statistics
        mean_duration = statistics.mean(durations)
        median_duration = statistics.median(durations)
        p95_duration = sorted(durations)[int(len(durations) * 0.95)]
        p99_duration = sorted(durations)[int(len(durations) * 0.99)]
        max_duration = max(durations)

        print(f"Evidence Collection Performance Results:")
        print(f"  Iterations: {test_iterations}")
        print(f"  Mean: {mean_duration:.3f}ms")
        print(f"  Median: {median_duration:.3f}ms")
        print(f"  P95: {p95_duration:.3f}ms")
        print(f"  P99: {p99_duration:.3f}ms")
        print(f"  Max: {max_duration:.3f}ms")

        # Performance requirements
        assert mean_duration < 10.0, f"Mean duration {mean_duration:.3f}ms exceeds 10ms requirement"
        assert p95_duration < 15.0, f"P95 duration {p95_duration:.3f}ms should be <15ms"
        assert p99_duration < 25.0, f"P99 duration {p99_duration:.3f}ms should be <25ms"

        print(f"✓ Evidence collection meets <10ms requirement (mean: {mean_duration:.3f}ms)")

    @pytest.mark.asyncio
    async def test_advanced_metrics_performance_requirement(self, advanced_metrics_system):
        """Test that advanced metrics recording meets performance requirements"""
        print("\n=== Advanced Metrics Performance Test ===")

        # Warmup
        for i in range(10):
            await advanced_metrics_system.record_advanced_metric(
                metric_name="warmup_metric",
                value=i * 0.1,
            )

        # Performance test
        durations = []
        test_iterations = 1000

        for i in range(test_iterations):
            start_time = time.perf_counter()

            await advanced_metrics_system.record_advanced_metric(
                metric_name="performance_test_metric",
                value=0.1 + (i * 0.001),
                labels={"iteration": str(i)},
            )

            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            durations.append(duration_ms)

        # Calculate statistics
        mean_duration = statistics.mean(durations)
        p95_duration = sorted(durations)[int(len(durations) * 0.95)]
        max_duration = max(durations)

        print(f"Advanced Metrics Performance Results:")
        print(f"  Iterations: {test_iterations}")
        print(f"  Mean: {mean_duration:.3f}ms")
        print(f"  P95: {p95_duration:.3f}ms")
        print(f"  Max: {max_duration:.3f}ms")

        # Performance requirements
        assert mean_duration < 5.0, f"Mean duration {mean_duration:.3f}ms exceeds 5ms requirement"
        assert p95_duration < 10.0, f"P95 duration {p95_duration:.3f}ms should be <10ms"

        print(f"✓ Advanced metrics meets <5ms requirement (mean: {mean_duration:.3f}ms)")

    @pytest.mark.asyncio
    async def test_performance_regression_recording_performance(self, performance_detector):
        """Test performance regression detection recording performance"""
        print("\n=== Performance Regression Recording Test ===")

        # Warmup
        for i in range(10):
            await performance_detector.record_performance_metric(
                metric_name="warmup_metric",
                component="warmup_service",
                value=0.1,
            )

        # Performance test
        durations = []
        test_iterations = 500  # Fewer iterations as this is more complex

        for i in range(test_iterations):
            start_time = time.perf_counter()

            await performance_detector.record_performance_metric(
                metric_name="test_latency",
                component="test_service",
                value=0.1 + (i * 0.0001),
                operation=f"test_operation_{i}",
            )

            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            durations.append(duration_ms)

        # Calculate statistics
        mean_duration = statistics.mean(durations)
        p95_duration = sorted(durations)[int(len(durations) * 0.95)]
        max_duration = max(durations)

        print(f"Performance Regression Recording Results:")
        print(f"  Iterations: {test_iterations}")
        print(f"  Mean: {mean_duration:.3f}ms")
        print(f"  P95: {p95_duration:.3f}ms")
        print(f"  Max: {max_duration:.3f}ms")

        # Performance requirements (more lenient for regression detection)
        assert mean_duration < 15.0, f"Mean duration {mean_duration:.3f}ms exceeds 15ms requirement"
        assert p95_duration < 25.0, f"P95 duration {p95_duration:.3f}ms should be <25ms"

        print(f"✓ Performance regression recording meets requirement (mean: {mean_duration:.3f}ms)")

    @pytest.mark.asyncio
    async def test_security_hardening_performance(self, security_hardening):
        """Test security hardening operations performance"""
        print("\n=== Security Hardening Performance Test ===")

        # Performance test for secure evidence collection
        durations = []
        test_iterations = 200  # Fewer iterations due to cryptographic overhead

        for i in range(test_iterations):
            evidence_data = {
                "evidence_type": "performance_metric",
                "source_component": "security_test",
                "operation": "security_performance_test",
                "payload": {"iteration": i, "value": 0.1},
            }

            start_time = time.perf_counter()

            evidence_id, metadata = await security_hardening.secure_evidence_collection(
                evidence_data=evidence_data,
                source_ip="127.0.0.1",
                user_id="test_user",
            )

            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            durations.append(duration_ms)

        # Calculate statistics
        mean_duration = statistics.mean(durations)
        p95_duration = sorted(durations)[int(len(durations) * 0.95)]
        max_duration = max(durations)

        print(f"Security Hardening Performance Results:")
        print(f"  Iterations: {test_iterations}")
        print(f"  Mean: {mean_duration:.3f}ms")
        print(f"  P95: {p95_duration:.3f}ms")
        print(f"  Max: {max_duration:.3f}ms")

        # Performance requirements (more lenient for cryptographic operations)
        assert mean_duration < 50.0, f"Mean duration {mean_duration:.3f}ms exceeds 50ms requirement"
        assert p95_duration < 100.0, f"P95 duration {p95_duration:.3f}ms should be <100ms"

        print(f"✓ Security hardening meets requirement (mean: {mean_duration:.3f}ms)")

    @pytest.mark.asyncio
    async def test_concurrent_evidence_collection_performance(self, evidence_engine):
        """Test evidence collection performance under concurrent load"""
        print("\n=== Concurrent Evidence Collection Performance Test ===")

        async def collect_evidence_batch(batch_id, batch_size):
            """Collect a batch of evidence records"""
            batch_durations = []

            for i in range(batch_size):
                start_time = time.perf_counter()

                await evidence_engine.collect_evidence(
                    evidence_type=EvidenceType.SYSTEM_EVENT,
                    source_component=f"concurrent_test_{batch_id}",
                    operation="concurrent_collection",
                    payload={
                        "batch_id": batch_id,
                        "item_id": i,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    },
                )

                end_time = time.perf_counter()
                duration_ms = (end_time - start_time) * 1000
                batch_durations.append(duration_ms)

            return batch_durations

        # Run concurrent batches
        concurrent_batches = 10
        batch_size = 50

        start_total = time.perf_counter()

        tasks = [
            collect_evidence_batch(batch_id, batch_size)
            for batch_id in range(concurrent_batches)
        ]

        batch_results = await asyncio.gather(*tasks)

        end_total = time.perf_counter()
        total_duration = end_total - start_total

        # Aggregate all durations
        all_durations = []
        for batch_durations in batch_results:
            all_durations.extend(batch_durations)

        # Calculate statistics
        mean_duration = statistics.mean(all_durations)
        p95_duration = sorted(all_durations)[int(len(all_durations) * 0.95)]
        throughput = len(all_durations) / total_duration

        print(f"Concurrent Evidence Collection Results:")
        print(f"  Total records: {len(all_durations)}")
        print(f"  Concurrent batches: {concurrent_batches}")
        print(f"  Total time: {total_duration:.3f}s")
        print(f"  Throughput: {throughput:.1f} records/second")
        print(f"  Mean latency: {mean_duration:.3f}ms")
        print(f"  P95 latency: {p95_duration:.3f}ms")

        # Performance requirements
        assert mean_duration < 15.0, f"Mean concurrent duration {mean_duration:.3f}ms exceeds 15ms"
        assert throughput > 100, f"Throughput {throughput:.1f} records/second should be >100"

        print(f"✓ Concurrent evidence collection meets requirements")

    @pytest.mark.asyncio
    async def test_mixed_operations_performance(self, evidence_engine, advanced_metrics_system):
        """Test performance with mixed observability operations"""
        print("\n=== Mixed Operations Performance Test ===")

        async def mixed_operations_batch(batch_id, iterations):
            """Run mixed operations batch"""
            durations = []

            for i in range(iterations):
                # Mix of evidence collection and metrics recording
                operations = []

                # Evidence collection
                start_time = time.perf_counter()
                evidence_task = evidence_engine.collect_evidence(
                    evidence_type=EvidenceType.PERFORMANCE_METRIC,
                    source_component=f"mixed_test_{batch_id}",
                    operation="mixed_operation",
                    payload={"batch": batch_id, "iteration": i},
                )
                operations.append(evidence_task)

                # Metrics recording
                metrics_task = advanced_metrics_system.record_advanced_metric(
                    metric_name=f"mixed_metric_{batch_id}",
                    value=0.1 + (i * 0.001),
                )
                operations.append(metrics_task)

                # Wait for all operations
                await asyncio.gather(*operations)

                end_time = time.perf_counter()
                duration_ms = (end_time - start_time) * 1000
                durations.append(duration_ms)

            return durations

        # Run mixed operations test
        concurrent_batches = 5
        iterations_per_batch = 100

        start_total = time.perf_counter()

        batch_tasks = [
            mixed_operations_batch(batch_id, iterations_per_batch)
            for batch_id in range(concurrent_batches)
        ]

        batch_results = await asyncio.gather(*batch_tasks)

        end_total = time.perf_counter()
        total_duration = end_total - start_total

        # Aggregate results
        all_durations = []
        for batch_durations in batch_results:
            all_durations.extend(batch_durations)

        # Calculate statistics
        mean_duration = statistics.mean(all_durations)
        p95_duration = sorted(all_durations)[int(len(all_durations) * 0.95)]
        throughput = len(all_durations) / total_duration

        print(f"Mixed Operations Performance Results:")
        print(f"  Total operations: {len(all_durations)}")
        print(f"  Total time: {total_duration:.3f}s")
        print(f"  Throughput: {throughput:.1f} operations/second")
        print(f"  Mean latency: {mean_duration:.3f}ms")
        print(f"  P95 latency: {p95_duration:.3f}ms")

        # Performance requirements
        assert mean_duration < 20.0, f"Mean mixed operations duration {mean_duration:.3f}ms exceeds 20ms"
        assert throughput > 50, f"Mixed operations throughput {throughput:.1f} ops/second should be >50"

        print(f"✓ Mixed operations meet performance requirements")

    def test_memory_usage_bounds(self, evidence_engine, advanced_metrics_system):
        """Test that memory usage stays within reasonable bounds"""
        print("\n=== Memory Usage Validation ===")

        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Generate significant load to test memory bounds
        for i in range(5000):
            # Evidence collection
            evidence_engine.metric_history[f"memory_test_{i % 100}"].append(i * 0.001)
            evidence_engine.metric_timestamps[f"memory_test_{i % 100}"].append(datetime.now(timezone.utc))

            # Advanced metrics
            advanced_metrics_system.metric_history[f"memory_metric_{i % 50}"].append(i * 0.01)
            advanced_metrics_system.metric_timestamps[f"memory_metric_{i % 50}"].append(datetime.now(timezone.utc))

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        print(f"Memory Usage Results:")
        print(f"  Initial memory: {initial_memory:.1f} MB")
        print(f"  Final memory: {final_memory:.1f} MB")
        print(f"  Memory increase: {memory_increase:.1f} MB")

        # Memory usage should be reasonable (less than 100MB increase for 5000 operations)
        assert memory_increase < 100, f"Memory increase {memory_increase:.1f}MB exceeds 100MB limit"

        print(f"✓ Memory usage within bounds (+{memory_increase:.1f}MB)")

    @pytest.mark.asyncio
    async def test_high_frequency_operations(self, evidence_engine):
        """Test performance under very high frequency operations"""
        print("\n=== High Frequency Operations Test ===")

        # Test rapid-fire evidence collection
        iterations = 2000
        start_time = time.perf_counter()

        # Use gather for maximum concurrency
        tasks = []
        for i in range(iterations):
            task = evidence_engine.collect_evidence(
                evidence_type=EvidenceType.SYSTEM_EVENT,
                source_component="high_frequency_test",
                operation="rapid_fire",
                payload={"id": i, "rapid": True},
            )
            tasks.append(task)

        await asyncio.gather(*tasks)

        end_time = time.perf_counter()
        total_duration = end_time - start_time
        throughput = iterations / total_duration

        print(f"High Frequency Operations Results:")
        print(f"  Total operations: {iterations}")
        print(f"  Total time: {total_duration:.3f}s")
        print(f"  Throughput: {throughput:.1f} operations/second")
        print(f"  Average time per operation: {(total_duration / iterations) * 1000:.3f}ms")

        # High frequency requirements
        assert throughput > 500, f"High frequency throughput {throughput:.1f} ops/sec should be >500"
        assert total_duration < 10.0, f"High frequency test took {total_duration:.3f}s, should be <10s"

        print(f"✓ High frequency operations meet requirements ({throughput:.1f} ops/sec)")


class TestScalabilityValidation:
    """Test scalability characteristics of observability system"""

    @pytest.mark.asyncio
    async def test_load_scaling_characteristics(self):
        """Test how performance scales with increasing load"""
        print("\n=== Load Scaling Characteristics Test ===")

        # Test different load levels
        load_levels = [10, 50, 100, 500, 1000]
        results = {}

        with tempfile.TemporaryDirectory() as temp_dir:
            engine = EvidenceCollectionEngine(
                storage_path=temp_dir,
                retention_days=1,
                compression_enabled=True,
                encryption_enabled=False,  # Disable for pure scaling test
                chain_block_size=1000,
            )

            try:
                for load_level in load_levels:
                    print(f"  Testing load level: {load_level}")

                    start_time = time.perf_counter()

                    tasks = []
                    for i in range(load_level):
                        task = engine.collect_evidence(
                            evidence_type=EvidenceType.SYSTEM_EVENT,
                            source_component="scaling_test",
                            operation="scaling_operation",
                            payload={"load_level": load_level, "item": i},
                        )
                        tasks.append(task)

                    await asyncio.gather(*tasks)

                    end_time = time.perf_counter()
                    duration = end_time - start_time
                    throughput = load_level / duration
                    avg_latency = (duration / load_level) * 1000

                    results[load_level] = {
                        "duration": duration,
                        "throughput": throughput,
                        "avg_latency_ms": avg_latency,
                    }

            finally:
                await engine.shutdown()

        print(f"Load Scaling Results:")
        for load_level, result in results.items():
            print(f"  Load {load_level}: {result['throughput']:.1f} ops/sec, {result['avg_latency_ms']:.3f}ms avg")

        # Validate scaling characteristics
        # Throughput should generally increase with load (up to a point)
        # Latency should remain reasonable even at high load
        max_load_result = results[max(load_levels)]
        assert max_load_result['avg_latency_ms'] < 50.0, f"High load latency {max_load_result['avg_latency_ms']:.3f}ms too high"
        assert max_load_result['throughput'] > 100.0, f"High load throughput {max_load_result['throughput']:.1f} too low"

        print(f"✓ Load scaling characteristics acceptable")


class TestRealWorldScenarios:
    """Test performance under realistic usage scenarios"""

    @pytest.mark.asyncio
    async def test_typical_production_workload(self):
        """Simulate typical production workload patterns"""
        print("\n=== Typical Production Workload Test ===")

        with tempfile.TemporaryDirectory() as temp_dir:
            # Setup observability stack
            evidence_engine = EvidenceCollectionEngine(
                storage_path=temp_dir,
                compression_enabled=True,
                encryption_enabled=True,
            )

            mock_prometheus = MagicMock()
            mock_prometheus.lane = "production"
            mock_prometheus.errors_total = MagicMock()
            mock_prometheus.errors_total.labels.return_value.inc = MagicMock()

            with patch('lukhas.observability.advanced_metrics.get_lukhas_metrics', return_value=mock_prometheus):
                advanced_metrics = AdvancedMetricsSystem(
                    enable_anomaly_detection=True,
                    enable_ml_features=False,  # Realistic setting
                )

                try:
                    # Simulate production workload
                    total_operations = 0
                    start_time = time.perf_counter()

                    # User interactions (frequent)
                    for i in range(200):
                        await evidence_engine.collect_evidence(
                            evidence_type=EvidenceType.USER_INTERACTION,
                            source_component="web_frontend",
                            operation="page_view",
                            payload={"page": f"/page_{i % 10}", "user_id": f"user_{i % 50}"},
                        )
                        total_operations += 1

                    # API calls with metrics (very frequent)
                    for i in range(300):
                        await evidence_engine.collect_evidence(
                            evidence_type=EvidenceType.SYSTEM_EVENT,
                            source_component="api_server",
                            operation="api_call",
                            payload={"endpoint": f"/api/endpoint_{i % 20}", "duration_ms": 50 + (i % 100)},
                        )

                        await advanced_metrics.record_advanced_metric(
                            metric_name="api_response_time",
                            value=0.05 + (i % 100) * 0.001,
                            labels={"endpoint": f"endpoint_{i % 20}"},
                        )
                        total_operations += 2

                    # Performance metrics (regular)
                    for i in range(100):
                        await evidence_engine.collect_evidence(
                            evidence_type=EvidenceType.PERFORMANCE_METRIC,
                            source_component="monitoring",
                            operation="metric_collection",
                            payload={"metric": f"cpu_usage", "value": 50 + (i % 50)},
                        )
                        total_operations += 1

                    # Security events (occasional)
                    for i in range(10):
                        await evidence_engine.collect_evidence(
                            evidence_type=EvidenceType.SECURITY_EVENT,
                            source_component="security_monitor",
                            operation="failed_login",
                            payload={"ip": f"192.168.1.{100 + i}", "attempts": 3 + (i % 3)},
                        )
                        total_operations += 1

                    # Compliance events (rare but important)
                    for i in range(5):
                        await evidence_engine.collect_evidence(
                            evidence_type=EvidenceType.REGULATORY_EVENT,
                            source_component="gdpr_processor",
                            operation="data_deletion",
                            payload={"user_id": f"deleted_user_{i}", "data_categories": ["profile", "activity"]},
                            compliance_regimes=[ComplianceRegime.GDPR],
                        )
                        total_operations += 1

                    end_time = time.perf_counter()
                    total_duration = end_time - start_time
                    overall_throughput = total_operations / total_duration

                    print(f"Production Workload Results:")
                    print(f"  Total operations: {total_operations}")
                    print(f"  Total duration: {total_duration:.3f}s")
                    print(f"  Overall throughput: {overall_throughput:.1f} ops/sec")
                    print(f"  Average latency: {(total_duration / total_operations) * 1000:.3f}ms")

                    # Production performance requirements
                    assert overall_throughput > 200, f"Production throughput {overall_throughput:.1f} should be >200 ops/sec"
                    assert total_duration < 10.0, f"Production workload took {total_duration:.3f}s, should be <10s"

                    print(f"✓ Production workload performance acceptable")

                finally:
                    await evidence_engine.shutdown()
                    await advanced_metrics.shutdown()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])  # -s to show print statements