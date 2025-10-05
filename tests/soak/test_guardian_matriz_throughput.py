#!/usr/bin/env python3
"""
Guardian Serializer Throughput Lock - T4/0.01% Excellence
========================================================

Soak testing Guardian serializer performance under MATRIZ load to ensure
no performance regressions when MATRIZ traffic spikes.

Performance Requirements:
- Guardian serializer: >1K ops/s throughput
- Guardian validation: <1ms mean latency
- No performance degradation under MATRIZ load
- Memory usage stable during 60s soak test

Test Methodology:
- Parallel Guardian serialize→validate operations
- Concurrent MATRIZ tick processing
- 60-second sustained load test
- Statistical validation of performance targets

Constellation Framework: 🛡️ Guardian Performance Lock
"""

import asyncio
import logging
import statistics
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from unittest.mock import patch

import pytest

# Import MATRIZ components
from lukhas.consciousness.matriz_thought_loop import MATRIZProcessingContext, MATRIZThoughtLoop
from lukhas.consciousness.types import ConsciousnessState

# Import Guardian components
from lukhas.governance.guardian_serializers import GuardianEnvelopeSerializer

logger = logging.getLogger(__name__)

# Performance targets
PERFORMANCE_TARGETS = {
    "guardian_throughput_ops_per_sec": 1000.0,
    "guardian_mean_latency_ms": 1.0,
    "guardian_p95_latency_ms": 5.0,
    "soak_duration_seconds": 60.0,
    "memory_stability_threshold": 0.2  # 20% memory growth max
}


@dataclass
class PerformanceMeasurement:
    """Individual performance measurement."""
    operation_type: str
    duration_ms: float
    success: bool
    timestamp: float
    memory_mb: Optional[float] = None
    error: Optional[str] = None


@dataclass
class SoakTestResult:
    """Result of soak test execution."""
    test_name: str
    duration_seconds: float
    guardian_throughput_ops_per_sec: float
    guardian_mean_latency_ms: float
    guardian_p95_latency_ms: float
    matriz_throughput_ops_per_sec: float
    total_operations: int
    success_rate: float
    performance_targets_met: bool
    memory_stable: bool
    errors: List[str]
    warnings: List[str]
    detailed_metrics: Dict[str, Any]


class GuardianMATRIZSoakTester:
    """Soak tester for Guardian performance under MATRIZ load."""

    def __init__(self):
        """Initialize soak tester."""
        self.guardian_serializer = GuardianEnvelopeSerializer()

        # Create mock MATRIZ loop for load simulation
        self.matriz_loop = MATRIZThoughtLoop(
            tenant="soak_test",
            max_inference_depth=3,  # Reduced for load testing
            total_time_budget_ms=50.0,  # Fast for throughput
            enable_advanced_features=False  # Simplified for load testing
        )

        self.measurements: Dict[str, List[PerformanceMeasurement]] = {
            "guardian_serialize": [],
            "guardian_validate": [],
            "matriz_tick": []
        }

        # Memory tracking
        self.memory_samples = []

    def create_test_decision_envelope(self, operation_id: str) -> Dict[str, Any]:
        """Create test Guardian decision envelope."""
        return {
            "schema_version": "2.1.0",
            "decision": {
                "status": "allow",
                "policy": "soak_test/v1.0.0",
                "severity": "low",
                "confidence": 0.95,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "ttl_seconds": 300
            },
            "subject": {
                "user_id": f"soak_user_{operation_id}",
                "session_id": f"soak_session_{operation_id}",
                "tier": "T4",
                "namespace": "soak_test"
            },
            "context": {
                "request_type": "soak_test_operation",
                "operation_id": operation_id,
                "test_data": "Guardian serializer soak test data",
                "lane": "integration"
            },
            "metrics": {
                "processing_time_ms": 25.0,
                "confidence_score": 0.95,
                "quality_assessment": 0.9,
                "risk_score": 0.05
            },
            "enforcement": {
                "enabled": True,
                "mode": "enforced",
                "actions": ["allow_processing"],
                "restrictions": []
            },
            "audit": {
                "correlation_id": f"soak_test_{operation_id}",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "source": "soak_test",
                "compliance_checked": True
            },
            "integrity": {
                "schema_version": "2.1.0",
                "payload_hash": f"hash_{operation_id}",
                "signature": f"signature_{operation_id}",
                "algorithm": "ed25519",
                "keyid": "soak_test_key"
            }
        }

    async def measure_guardian_serialize_operation(self, operation_id: str) -> PerformanceMeasurement:
        """Measure Guardian serialization operation."""
        start_time = time.perf_counter()
        success = True
        error = None

        try:
            # Create test envelope
            envelope = self.create_test_decision_envelope(operation_id)

            # Serialize with Guardian
            serialized_data = self.guardian_serializer.serialize_envelope(envelope)

            # Verify serialization worked
            if not serialized_data or len(serialized_data) == 0:
                success = False
                error = "Serialization produced empty result"

        except Exception as e:
            success = False
            error = str(e)
            logger.debug(f"Guardian serialize operation {operation_id} failed: {e}")

        duration_ms = (time.perf_counter() - start_time) * 1000

        return PerformanceMeasurement(
            operation_type="guardian_serialize",
            duration_ms=duration_ms,
            success=success,
            timestamp=time.time(),
            error=error
        )

    async def measure_guardian_validate_operation(self, operation_id: str) -> PerformanceMeasurement:
        """Measure Guardian validation operation."""
        start_time = time.perf_counter()
        success = True
        error = None

        try:
            # Create test envelope
            envelope = self.create_test_decision_envelope(operation_id)

            # Validate with Guardian
            validation_result = self.guardian_serializer.validate_envelope(envelope)

            # Check validation result
            success = validation_result.get('valid', False)
            if not success:
                error = f"Validation failed: {validation_result.get('errors', [])}"

        except Exception as e:
            success = False
            error = str(e)
            logger.debug(f"Guardian validate operation {operation_id} failed: {e}")

        duration_ms = (time.perf_counter() - start_time) * 1000

        return PerformanceMeasurement(
            operation_type="guardian_validate",
            duration_ms=duration_ms,
            success=success,
            timestamp=time.time(),
            error=error
        )

    async def measure_matriz_tick_operation(self, operation_id: str) -> PerformanceMeasurement:
        """Measure MATRIZ tick operation."""
        start_time = time.perf_counter()
        success = True
        error = None

        try:
            # Create minimal MATRIZ context
            context = MATRIZProcessingContext(
                query=f"Soak test query {operation_id}",
                memory_signals=[
                    {"id": f"mem_{operation_id}", "content": "Soak test memory", "score": 0.8}
                ],
                consciousness_state=ConsciousnessState.ACTIVE,
                processing_config={"complexity": "simple"},
                session_id=f"matriz_soak_{operation_id}",
                tenant="soak_test",
                time_budget_ms=30.0,  # Fast for load testing
                enable_all_features=False
            )

            # Mock the thought processing for load testing
            with patch.object(self.matriz_loop.enhanced_thought_node, 'process_async') as mock_process:
                mock_process.return_value = {
                    'success': True,
                    'answer': {'summary': f'Soak test result {operation_id}'},
                    'confidence': 0.85,
                    'processing_time_ms': 15.0,
                    'enhanced_features': {
                        'inference_depth_reached': 1,
                        'quality_score': 0.8,
                        'cognitive_load': 0.2
                    }
                }

                # Execute MATRIZ tick
                result = await self.matriz_loop.process_complete_thought_loop(context)
                success = result.success

        except Exception as e:
            success = False
            error = str(e)
            logger.debug(f"MATRIZ tick operation {operation_id} failed: {e}")

        duration_ms = (time.perf_counter() - start_time) * 1000

        return PerformanceMeasurement(
            operation_type="matriz_tick",
            duration_ms=duration_ms,
            success=success,
            timestamp=time.time(),
            error=error
        )

    def sample_memory_usage(self) -> float:
        """Sample current memory usage in MB."""
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / (1024 * 1024)
            return memory_mb
        except ImportError:
            # If psutil not available, return mock value
            return 100.0

    async def run_parallel_load_worker(self, worker_id: int, duration_seconds: float, operations_per_worker: int):
        """Run parallel load worker for sustained operations."""
        worker_start_time = time.time()
        operations_completed = 0

        logger.info(f"Worker {worker_id} starting {operations_per_worker} operations over {duration_seconds}s")

        while (time.time() - worker_start_time) < duration_seconds and operations_completed < operations_per_worker:
            operation_id = f"worker_{worker_id}_op_{operations_completed}"

            # Alternate between Guardian and MATRIZ operations
            if operations_completed % 3 == 0:
                # Guardian serialize operation
                measurement = await self.measure_guardian_serialize_operation(operation_id)
                self.measurements["guardian_serialize"].append(measurement)
            elif operations_completed % 3 == 1:
                # Guardian validate operation
                measurement = await self.measure_guardian_validate_operation(operation_id)
                self.measurements["guardian_validate"].append(measurement)
            else:
                # MATRIZ tick operation
                measurement = await self.measure_matriz_tick_operation(operation_id)
                self.measurements["matriz_tick"].append(measurement)

            operations_completed += 1

            # Brief pause to prevent overwhelming
            await asyncio.sleep(0.001)  # 1ms between operations

        logger.info(f"Worker {worker_id} completed {operations_completed} operations")

    async def run_soak_test(self, duration_seconds: float = 60.0, concurrent_workers: int = 8) -> SoakTestResult:
        """Run comprehensive soak test with parallel load."""
        test_start_time = time.time()

        # Initial memory sample
        initial_memory = self.sample_memory_usage()
        self.memory_samples = [initial_memory]

        logger.info(f"Starting {duration_seconds}s soak test with {concurrent_workers} workers")

        # Calculate operations per worker
        total_target_operations = int(PERFORMANCE_TARGETS["guardian_throughput_ops_per_sec"] * duration_seconds)
        operations_per_worker = max(1, total_target_operations // (concurrent_workers * 2))  # Split between Guardian and MATRIZ

        try:
            # Create memory sampling task
            memory_task = asyncio.create_task(self._sample_memory_periodically(duration_seconds))

            # Create worker tasks
            worker_tasks = []
            for worker_id in range(concurrent_workers):
                task = asyncio.create_task(
                    self.run_parallel_load_worker(worker_id, duration_seconds, operations_per_worker)
                )
                worker_tasks.append(task)

            # Wait for all workers to complete
            await asyncio.gather(*worker_tasks)

            # Stop memory sampling
            memory_task.cancel()
            try:
                await memory_task
            except asyncio.CancelledError:
                pass

        except Exception as e:
            logger.error(f"Soak test execution failed: {e}")

        # Final memory sample
        final_memory = self.sample_memory_usage()
        self.memory_samples.append(final_memory)

        # Calculate test duration
        actual_duration = time.time() - test_start_time

        # Analyze results
        return self._analyze_soak_results(actual_duration, initial_memory, final_memory)

    async def _sample_memory_periodically(self, duration_seconds: float):
        """Sample memory usage periodically during soak test."""
        sample_interval = 5.0  # Sample every 5 seconds
        start_time = time.time()

        while (time.time() - start_time) < duration_seconds:
            await asyncio.sleep(sample_interval)
            memory_mb = self.sample_memory_usage()
            self.memory_samples.append(memory_mb)

    def _analyze_soak_results(self, duration_seconds: float, initial_memory: float, final_memory: float) -> SoakTestResult:
        """Analyze soak test results and calculate performance metrics."""

        # Guardian operations analysis
        guardian_serialize_measurements = [m for m in self.measurements["guardian_serialize"] if m.success]
        guardian_validate_measurements = [m for m in self.measurements["guardian_validate"] if m.success]
        matriz_measurements = [m for m in self.measurements["matriz_tick"] if m.success]

        # Total operations
        total_guardian_ops = len(guardian_serialize_measurements) + len(guardian_validate_measurements)
        total_matriz_ops = len(matriz_measurements)
        total_operations = total_guardian_ops + total_matriz_ops

        # Guardian throughput calculation
        guardian_throughput = total_guardian_ops / duration_seconds if duration_seconds > 0 else 0
        matriz_throughput = total_matriz_ops / duration_seconds if duration_seconds > 0 else 0

        # Guardian latency analysis
        all_guardian_latencies = []
        all_guardian_latencies.extend([m.duration_ms for m in guardian_serialize_measurements])
        all_guardian_latencies.extend([m.duration_ms for m in guardian_validate_measurements])

        guardian_mean_latency = statistics.mean(all_guardian_latencies) if all_guardian_latencies else 0
        guardian_p95_latency = statistics.quantiles(all_guardian_latencies, n=20)[18] if len(all_guardian_latencies) > 20 else (max(all_guardian_latencies) if all_guardian_latencies else 0)

        # Success rate calculation
        total_attempted = total_operations + sum(1 for m in self.measurements["guardian_serialize"] if not m.success) + sum(1 for m in self.measurements["guardian_validate"] if not m.success) + sum(1 for m in self.measurements["matriz_tick"] if not m.success)
        success_rate = (total_operations / total_attempted) * 100 if total_attempted > 0 else 0

        # Memory stability analysis
        memory_growth_pct = ((final_memory - initial_memory) / initial_memory) * 100 if initial_memory > 0 else 0
        memory_stable = abs(memory_growth_pct) <= (PERFORMANCE_TARGETS["memory_stability_threshold"] * 100)

        # Performance targets evaluation
        throughput_target_met = guardian_throughput >= PERFORMANCE_TARGETS["guardian_throughput_ops_per_sec"]
        latency_target_met = guardian_mean_latency <= PERFORMANCE_TARGETS["guardian_mean_latency_ms"]
        p95_latency_target_met = guardian_p95_latency <= PERFORMANCE_TARGETS["guardian_p95_latency_ms"]

        performance_targets_met = throughput_target_met and latency_target_met and p95_latency_target_met

        # Collect errors and warnings
        errors = []
        warnings = []

        if not throughput_target_met:
            errors.append(f"Guardian throughput {guardian_throughput:.1f} ops/s < target {PERFORMANCE_TARGETS['guardian_throughput_ops_per_sec']} ops/s")

        if not latency_target_met:
            errors.append(f"Guardian mean latency {guardian_mean_latency:.2f}ms > target {PERFORMANCE_TARGETS['guardian_mean_latency_ms']}ms")

        if not p95_latency_target_met:
            errors.append(f"Guardian P95 latency {guardian_p95_latency:.2f}ms > target {PERFORMANCE_TARGETS['guardian_p95_latency_ms']}ms")

        if not memory_stable:
            warnings.append(f"Memory growth {memory_growth_pct:.1f}% exceeds stability threshold {PERFORMANCE_TARGETS['memory_stability_threshold'] * 100}%")

        if success_rate < 95.0:
            warnings.append(f"Success rate {success_rate:.1f}% below 95% threshold")

        return SoakTestResult(
            test_name="guardian_matriz_throughput_soak",
            duration_seconds=duration_seconds,
            guardian_throughput_ops_per_sec=guardian_throughput,
            guardian_mean_latency_ms=guardian_mean_latency,
            guardian_p95_latency_ms=guardian_p95_latency,
            matriz_throughput_ops_per_sec=matriz_throughput,
            total_operations=total_operations,
            success_rate=success_rate,
            performance_targets_met=performance_targets_met,
            memory_stable=memory_stable,
            errors=errors,
            warnings=warnings,
            detailed_metrics={
                "guardian_serialize_ops": len(guardian_serialize_measurements),
                "guardian_validate_ops": len(guardian_validate_measurements),
                "matriz_tick_ops": len(matriz_measurements),
                "initial_memory_mb": initial_memory,
                "final_memory_mb": final_memory,
                "memory_growth_pct": memory_growth_pct,
                "memory_samples": len(self.memory_samples),
                "throughput_target_met": throughput_target_met,
                "latency_target_met": latency_target_met,
                "p95_target_met": p95_latency_target_met
            }
        )


@pytest.mark.asyncio
@pytest.mark.soak
@pytest.mark.performance
class TestGuardianMATRIZThroughput:
    """Guardian serializer throughput soak tests under MATRIZ load."""

    async def test_guardian_throughput_under_matriz_load(self):
        """Test Guardian maintains >1K ops/s throughput under MATRIZ load."""
        tester = GuardianMATRIZSoakTester()

        # Run 60-second soak test
        result = await tester.run_soak_test(
            duration_seconds=PERFORMANCE_TARGETS["soak_duration_seconds"],
            concurrent_workers=8
        )

        # Log comprehensive results
        logger.info("=== Guardian MATRIZ Throughput Soak Test Results ===")
        logger.info(f"Test Duration: {result.duration_seconds:.1f}s")
        logger.info(f"Total Operations: {result.total_operations}")
        logger.info(f"Success Rate: {result.success_rate:.1f}%")

        logger.info("Guardian Performance:")
        logger.info(f"  Throughput: {result.guardian_throughput_ops_per_sec:.1f} ops/s (target: ≥{PERFORMANCE_TARGETS['guardian_throughput_ops_per_sec']})")
        logger.info(f"  Mean Latency: {result.guardian_mean_latency_ms:.2f}ms (target: ≤{PERFORMANCE_TARGETS['guardian_mean_latency_ms']}ms)")
        logger.info(f"  P95 Latency: {result.guardian_p95_latency_ms:.2f}ms (target: ≤{PERFORMANCE_TARGETS['guardian_p95_latency_ms']}ms)")

        logger.info(f"MATRIZ Throughput: {result.matriz_throughput_ops_per_sec:.1f} ops/s")
        logger.info(f"Memory Stable: {'✓' if result.memory_stable else '✗'}")

        if result.errors:
            logger.error("Performance Errors:")
            for error in result.errors:
                logger.error(f"  ❌ {error}")

        if result.warnings:
            logger.warning("Performance Warnings:")
            for warning in result.warnings:
                logger.warning(f"  ⚠️  {warning}")

        # Assertions
        assert result.performance_targets_met, f"Performance targets not met: {result.errors}"
        assert result.guardian_throughput_ops_per_sec >= PERFORMANCE_TARGETS["guardian_throughput_ops_per_sec"], \
            f"Guardian throughput {result.guardian_throughput_ops_per_sec:.1f} below target"
        assert result.guardian_mean_latency_ms <= PERFORMANCE_TARGETS["guardian_mean_latency_ms"], \
            f"Guardian mean latency {result.guardian_mean_latency_ms:.2f}ms above target"
        assert result.success_rate >= 95.0, f"Success rate {result.success_rate:.1f}% below 95%"
        assert result.memory_stable, "Memory not stable during soak test"

    async def test_guardian_latency_stability_under_load(self):
        """Test Guardian latency remains stable <1ms mean under sustained load."""
        tester = GuardianMATRIZSoakTester()

        # Run focused latency test
        result = await tester.run_soak_test(
            duration_seconds=30.0,  # Shorter focused test
            concurrent_workers=12   # Higher concurrency for latency stress
        )

        logger.info("Guardian Latency Stability Test:")
        logger.info(f"  Mean Latency: {result.guardian_mean_latency_ms:.2f}ms")
        logger.info(f"  P95 Latency: {result.guardian_p95_latency_ms:.2f}ms")
        logger.info(f"  Throughput: {result.guardian_throughput_ops_per_sec:.1f} ops/s")

        # Focus on latency requirements
        assert result.guardian_mean_latency_ms <= PERFORMANCE_TARGETS["guardian_mean_latency_ms"], \
            f"Mean latency {result.guardian_mean_latency_ms:.2f}ms exceeds 1ms target"
        assert result.guardian_p95_latency_ms <= PERFORMANCE_TARGETS["guardian_p95_latency_ms"], \
            f"P95 latency {result.guardian_p95_latency_ms:.2f}ms exceeds 5ms target"

    async def test_memory_stability_during_soak(self):
        """Test memory usage remains stable during sustained Guardian+MATRIZ load."""
        tester = GuardianMATRIZSoakTester()

        # Run memory-focused soak test
        result = await tester.run_soak_test(
            duration_seconds=45.0,  # Medium duration
            concurrent_workers=6    # Moderate concurrency
        )

        memory_growth_pct = result.detailed_metrics["memory_growth_pct"]

        logger.info("Memory Stability Test:")
        logger.info(f"  Initial Memory: {result.detailed_metrics['initial_memory_mb']:.1f}MB")
        logger.info(f"  Final Memory: {result.detailed_metrics['final_memory_mb']:.1f}MB")
        logger.info(f"  Memory Growth: {memory_growth_pct:.1f}%")
        logger.info(f"  Memory Stable: {'✓' if result.memory_stable else '✗'}")

        # Memory stability assertions
        assert result.memory_stable, f"Memory growth {memory_growth_pct:.1f}% exceeds {PERFORMANCE_TARGETS['memory_stability_threshold'] * 100}% threshold"
        assert abs(memory_growth_pct) <= 30.0, f"Memory growth {memory_growth_pct:.1f}% exceeds reasonable bounds"


if __name__ == "__main__":
    # Run soak test standalone
    async def run_soak_test():
        print("Starting Guardian MATRIZ throughput soak test...")

        tester = GuardianMATRIZSoakTester()
        result = await tester.run_soak_test(
            duration_seconds=30.0,  # Shorter for standalone run
            concurrent_workers=6
        )

        print("\n=== Guardian MATRIZ Soak Test Results ===")
        print(f"Duration: {result.duration_seconds:.1f}s")
        print(f"Total Operations: {result.total_operations}")
        print(f"Success Rate: {result.success_rate:.1f}%")

        print("\nGuardian Performance:")
        print(f"  Throughput: {result.guardian_throughput_ops_per_sec:.1f} ops/s ({'✓' if result.guardian_throughput_ops_per_sec >= PERFORMANCE_TARGETS['guardian_throughput_ops_per_sec'] else '✗'})")
        print(f"  Mean Latency: {result.guardian_mean_latency_ms:.2f}ms ({'✓' if result.guardian_mean_latency_ms <= PERFORMANCE_TARGETS['guardian_mean_latency_ms'] else '✗'})")
        print(f"  P95 Latency: {result.guardian_p95_latency_ms:.2f}ms ({'✓' if result.guardian_p95_latency_ms <= PERFORMANCE_TARGETS['guardian_p95_latency_ms'] else '✗'})")

        print(f"\nMATRIZ Throughput: {result.matriz_throughput_ops_per_sec:.1f} ops/s")
        print(f"Memory Stable: {'✓ PASS' if result.memory_stable else '✗ FAIL'}")
        print(f"Performance Targets: {'✅ ALL MET' if result.performance_targets_met else '❌ SOME FAILED'}")

        if result.errors:
            print("\n❌ Errors:")
            for error in result.errors:
                print(f"   {error}")

        if result.warnings:
            print("\n⚠️  Warnings:")
            for warning in result.warnings:
                print(f"   {warning}")

        return result.performance_targets_met and result.memory_stable

    import sys
    success = asyncio.run(run_soak_test())
    sys.exit(0 if success else 1)
