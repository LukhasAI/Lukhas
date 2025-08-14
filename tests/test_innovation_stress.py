#!/usr/bin/env python3
"""
Innovation System Stress Testing Suite
=======================================
High-volume stress tests for the AI Self-Innovation system to validate
performance, safety, and stability under extreme conditions.

Tests include:
- Massive parallel reality exploration (10,000+ branches)
- Drift threshold boundary testing
- Concurrent innovation generation
- Memory and resource stress testing
- Rapid-fire safety validation
"""

import asyncio
import json
import sys
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Core imports
from consciousness.dream.autonomous_innovation_core import (
    InnovationDomain,
    InnovationHypothesis,
)
from consciousness.dream.innovation_drift_protection import (
    DriftProtectionConfig,
    InnovationDriftProtection,
)

# Logging
from core.common import get_logger

logger = get_logger(__name__)


@dataclass
class StressTestMetrics:
    """Metrics collected during stress testing"""
    test_name: str
    start_time: datetime
    end_time: Optional[datetime]

    # Performance metrics
    total_operations: int
    successful_operations: int
    failed_operations: int
    avg_operation_time: float
    max_operation_time: float
    min_operation_time: float
    operations_per_second: float

    # Resource metrics
    peak_memory_mb: float
    avg_memory_mb: float
    peak_cpu_percent: float
    avg_cpu_percent: float

    # Safety metrics
    drift_violations: int
    max_drift_score: float
    hallucinations_detected: int
    safety_interventions: int
    rollbacks_triggered: int

    # System stability
    errors_encountered: List[str]
    system_crashes: int
    recovery_success_rate: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'test_name': self.test_name,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'performance': {
                'total_operations': self.total_operations,
                'successful_operations': self.successful_operations,
                'failed_operations': self.failed_operations,
                'avg_operation_time': self.avg_operation_time,
                'max_operation_time': self.max_operation_time,
                'min_operation_time': self.min_operation_time,
                'operations_per_second': self.operations_per_second
            },
            'resources': {
                'peak_memory_mb': self.peak_memory_mb,
                'avg_memory_mb': self.avg_memory_mb,
                'peak_cpu_percent': self.peak_cpu_percent,
                'avg_cpu_percent': self.avg_cpu_percent
            },
            'safety': {
                'drift_violations': self.drift_violations,
                'max_drift_score': self.max_drift_score,
                'hallucinations_detected': self.hallucinations_detected,
                'safety_interventions': self.safety_interventions,
                'rollbacks_triggered': self.rollbacks_triggered
            },
            'stability': {
                'errors_encountered': len(self.errors_encountered),
                'error_samples': self.errors_encountered[:5],  # First 5 errors
                'system_crashes': self.system_crashes,
                'recovery_success_rate': self.recovery_success_rate
            }
        }


class InnovationStressTest:
    """
    Stress testing suite for Innovation System.
    Pushes the system to its limits to identify breaking points.
    """

    def __init__(self):
        self.innovation_system: Optional[InnovationDriftProtection] = None
        self.metrics: List[StressTestMetrics] = []
        self.resource_monitor = ResourceMonitor()

    async def setup(self, aggressive_config: bool = True) -> None:
        """Initialize stress test system"""
        logger.info("🔥 Initializing Stress Test System")

        # Use aggressive configuration for stress testing
        if aggressive_config:
            config = DriftProtectionConfig(
                drift_threshold=0.05,  # Very strict threshold
                hallucination_threshold=0.05,  # Very sensitive
                enable_auto_rollback=True,
                enable_emotional_regulation=True,
                checkpoint_interval=1,  # Checkpoint every operation
                max_rollback_depth=100,  # Deep rollback history
                recalibration_sensitivity=0.95  # Highly sensitive
            )
        else:
            config = DriftProtectionConfig()  # Default config

        # Initialize with mock core
        from unittest.mock import AsyncMock, Mock
        mock_core = Mock()
        mock_core.operational = True
        mock_core.initialize = AsyncMock(return_value=None)
        mock_core.shutdown = AsyncMock(return_value=None)

        # Mock the exploration methods for testing
        async def mock_explore(*args, **kwargs):
            await asyncio.sleep(0.001)  # Simulate work
            return [{'id': str(uuid.uuid4()), 'score': 0.8} for _ in range(10)]

        mock_core.explore_innovation_in_parallel_realities = mock_explore
        mock_core.validate_and_synthesize_innovation = AsyncMock(return_value={
            'innovation_id': str(uuid.uuid4()),
            'title': 'Test Innovation',
            'description': 'Stress test generated innovation'
        })

        self.innovation_system = InnovationDriftProtection(
            innovation_core=mock_core,
            config=config
        )
        await self.innovation_system.initialize()

        logger.info("✅ Stress test system initialized")

    async def teardown(self) -> None:
        """Cleanup stress test system"""
        if self.innovation_system:
            await self.innovation_system.shutdown()
        logger.info("Stress test system shutdown complete")

    async def stress_test_massive_parallel_exploration(self,
                                                       reality_count: int = 10000) -> StressTestMetrics:
        """Test system with massive parallel reality exploration"""
        test_name = f"massive_parallel_{reality_count}"
        logger.info(f"🚀 Starting stress test: {test_name}")

        metrics = StressTestMetrics(
            test_name=test_name,
            start_time=datetime.now(timezone.utc),
            end_time=None,
            total_operations=0,
            successful_operations=0,
            failed_operations=0,
            avg_operation_time=0,
            max_operation_time=0,
            min_operation_time=float('inf'),
            operations_per_second=0,
            peak_memory_mb=0,
            avg_memory_mb=0,
            peak_cpu_percent=0,
            avg_cpu_percent=0,
            drift_violations=0,
            max_drift_score=0,
            hallucinations_detected=0,
            safety_interventions=0,
            rollbacks_triggered=0,
            errors_encountered=[],
            system_crashes=0,
            recovery_success_rate=0
        )

        # Start resource monitoring
        monitor_task = asyncio.create_task(
            self.resource_monitor.monitor(metrics)
        )

        operation_times = []

        try:
            # Create massive hypothesis
            hypothesis = InnovationHypothesis(
                hypothesis_id=str(uuid.uuid4()),
                domain=InnovationDomain.QUANTUM_COMPUTING,
                description="Stress test hypothesis for massive parallel exploration",
                breakthrough_potential=0.9,
                feasibility_score=0.8,
                impact_magnitude=0.9
            )

            # Execute massive parallel exploration
            start_time = time.time()

            # Split into batches to avoid overwhelming the system
            batch_size = 1000
            batches = reality_count // batch_size

            for batch in range(batches):
                batch_start = time.time()

                try:
                    # Attempt innovation generation
                    innovation = await self.innovation_system.generate_innovation_with_protection(
                        hypothesis=hypothesis,
                        reality_count=batch_size,
                        exploration_depth=3  # Reduced depth for stress testing
                    )

                    if innovation:
                        metrics.successful_operations += 1
                    else:
                        metrics.failed_operations += 1
                        metrics.safety_interventions += 1

                    metrics.total_operations += 1

                except Exception as e:
                    metrics.failed_operations += 1
                    metrics.errors_encountered.append(str(e)[:100])  # First 100 chars
                    logger.warning(f"Batch {batch} error: {e}")

                batch_time = time.time() - batch_start
                operation_times.append(batch_time)
                metrics.max_operation_time = max(metrics.max_operation_time, batch_time)
                metrics.min_operation_time = min(metrics.min_operation_time, batch_time)

                # Check drift score
                if self.innovation_system.drift_events:
                    latest_drift = self.innovation_system.drift_events[-1]
                    metrics.max_drift_score = max(metrics.max_drift_score, latest_drift.drift_score)
                    if latest_drift.drift_score > self.innovation_system.config.drift_threshold:
                        metrics.drift_violations += 1

                # Small delay between batches
                await asyncio.sleep(0.01)

                # Progress log
                if (batch + 1) % 10 == 0:
                    logger.info(f"  Progress: {(batch + 1) * batch_size}/{reality_count} realities explored")

            total_time = time.time() - start_time
            metrics.avg_operation_time = sum(operation_times) / len(operation_times) if operation_times else 0
            metrics.operations_per_second = metrics.total_operations / total_time if total_time > 0 else 0

        except Exception as e:
            logger.error(f"Stress test failed: {e}")
            metrics.system_crashes += 1
            metrics.errors_encountered.append(f"System crash: {str(e)[:200]}")

        finally:
            # Stop resource monitoring
            monitor_task.cancel()
            try:
                await monitor_task
            except asyncio.CancelledError:
                pass

        metrics.end_time = datetime.now(timezone.utc)
        metrics.recovery_success_rate = (
            metrics.successful_operations / metrics.total_operations
            if metrics.total_operations > 0 else 0
        )

        self._log_metrics(metrics)
        return metrics

    async def stress_test_rapid_fire_generation(self,
                                               operations: int = 1000,
                                               concurrent: int = 10) -> StressTestMetrics:
        """Test rapid-fire concurrent innovation generation"""
        test_name = f"rapid_fire_{operations}x{concurrent}"
        logger.info(f"🔥 Starting stress test: {test_name}")

        metrics = StressTestMetrics(
            test_name=test_name,
            start_time=datetime.now(timezone.utc),
            end_time=None,
            total_operations=operations,
            successful_operations=0,
            failed_operations=0,
            avg_operation_time=0,
            max_operation_time=0,
            min_operation_time=float('inf'),
            operations_per_second=0,
            peak_memory_mb=0,
            avg_memory_mb=0,
            peak_cpu_percent=0,
            avg_cpu_percent=0,
            drift_violations=0,
            max_drift_score=0,
            hallucinations_detected=0,
            safety_interventions=0,
            rollbacks_triggered=0,
            errors_encountered=[],
            system_crashes=0,
            recovery_success_rate=0
        )

        # Start resource monitoring
        monitor_task = asyncio.create_task(
            self.resource_monitor.monitor(metrics)
        )

        async def generate_single():
            """Generate a single innovation"""
            try:
                hypothesis = InnovationHypothesis(
                    hypothesis_id=str(uuid.uuid4()),
                    domain=InnovationDomain.ARTIFICIAL_INTELLIGENCE,
                    description=f"Rapid test hypothesis {uuid.uuid4().hex[:8]}",
                    breakthrough_potential=0.7,
                    feasibility_score=0.8,
                    impact_magnitude=0.6
                )

                start = time.time()
                innovation = await self.innovation_system.generate_innovation_with_protection(
                    hypothesis=hypothesis,
                    reality_count=10,  # Small for rapid testing
                    exploration_depth=2
                )
                elapsed = time.time() - start

                return (True if innovation else False, elapsed, None)

            except Exception as e:
                return (False, 0, str(e)[:100])

        try:
            # Create batches of concurrent operations
            batches = operations // concurrent
            all_times = []

            for batch in range(batches):
                # Launch concurrent generations
                tasks = [generate_single() for _ in range(concurrent)]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                for result in results:
                    if isinstance(result, Exception):
                        metrics.failed_operations += 1
                        metrics.errors_encountered.append(str(result)[:100])
                    else:
                        success, elapsed, error = result
                        if success:
                            metrics.successful_operations += 1
                        else:
                            metrics.failed_operations += 1
                            if error:
                                metrics.errors_encountered.append(error)

                        if elapsed > 0:
                            all_times.append(elapsed)
                            metrics.max_operation_time = max(metrics.max_operation_time, elapsed)
                            metrics.min_operation_time = min(metrics.min_operation_time, elapsed)

                # Progress log
                if (batch + 1) % 10 == 0:
                    logger.info(f"  Progress: {(batch + 1) * concurrent}/{operations} operations")

            # Calculate averages
            if all_times:
                metrics.avg_operation_time = sum(all_times) / len(all_times)
                total_time = (metrics.end_time or datetime.now(timezone.utc) - metrics.start_time).total_seconds()
                metrics.operations_per_second = len(all_times) / total_time if total_time > 0 else 0

        except Exception as e:
            logger.error(f"Rapid fire test failed: {e}")
            metrics.system_crashes += 1
            metrics.errors_encountered.append(f"System crash: {str(e)[:200]}")

        finally:
            # Stop resource monitoring
            monitor_task.cancel()
            try:
                await monitor_task
            except asyncio.CancelledError:
                pass

        metrics.end_time = datetime.now(timezone.utc)
        metrics.recovery_success_rate = (
            metrics.successful_operations / metrics.total_operations
            if metrics.total_operations > 0 else 0
        )

        self._log_metrics(metrics)
        return metrics

    async def stress_test_drift_boundary(self, iterations: int = 100) -> StressTestMetrics:
        """Test system behavior at drift threshold boundaries"""
        test_name = f"drift_boundary_{iterations}"
        logger.info(f"⚡ Starting stress test: {test_name}")

        metrics = StressTestMetrics(
            test_name=test_name,
            start_time=datetime.now(timezone.utc),
            end_time=None,
            total_operations=iterations,
            successful_operations=0,
            failed_operations=0,
            avg_operation_time=0,
            max_operation_time=0,
            min_operation_time=float('inf'),
            operations_per_second=0,
            peak_memory_mb=0,
            avg_memory_mb=0,
            peak_cpu_percent=0,
            avg_cpu_percent=0,
            drift_violations=0,
            max_drift_score=0,
            hallucinations_detected=0,
            safety_interventions=0,
            rollbacks_triggered=0,
            errors_encountered=[],
            system_crashes=0,
            recovery_success_rate=0
        )

        # Start resource monitoring
        monitor_task = asyncio.create_task(
            self.resource_monitor.monitor(metrics)
        )

        try:
            # Gradually increase drift-inducing parameters
            for i in range(iterations):
                # Create increasingly risky hypothesis
                risk_level = i / iterations  # 0 to 1

                hypothesis = InnovationHypothesis(
                    hypothesis_id=str(uuid.uuid4()),
                    domain=InnovationDomain.CONSCIOUSNESS_TECH,
                    description=f"Drift test: reality manipulation level {risk_level:.2f}",
                    breakthrough_potential=0.9 + (risk_level * 0.1),  # Push limits
                    feasibility_score=1.0 - (risk_level * 0.5),  # Decrease feasibility
                    impact_magnitude=0.9 + (risk_level * 0.1),
                    metadata={'drift_inducing': True, 'risk_level': risk_level}
                )

                start = time.time()

                try:
                    innovation = await self.innovation_system.generate_innovation_with_protection(
                        hypothesis=hypothesis,
                        reality_count=50 + int(risk_level * 450),  # Increase with risk
                        exploration_depth=3 + int(risk_level * 7)  # Deeper with risk
                    )

                    if innovation:
                        metrics.successful_operations += 1
                    else:
                        metrics.failed_operations += 1
                        metrics.safety_interventions += 1

                except Exception as e:
                    metrics.failed_operations += 1
                    metrics.errors_encountered.append(f"Drift {risk_level:.2f}: {str(e)[:50]}")

                elapsed = time.time() - start
                metrics.max_operation_time = max(metrics.max_operation_time, elapsed)
                metrics.min_operation_time = min(metrics.min_operation_time, elapsed)

                # Check drift metrics
                if self.innovation_system.drift_events:
                    latest_drift = self.innovation_system.drift_events[-1]
                    metrics.max_drift_score = max(metrics.max_drift_score, latest_drift.drift_score)

                    if latest_drift.drift_score > self.innovation_system.config.drift_threshold:
                        metrics.drift_violations += 1

                    if latest_drift.intervention_required:
                        metrics.safety_interventions += 1

                # Check for rollbacks
                if len(self.innovation_system.checkpoints) > metrics.rollbacks_triggered + 1:
                    metrics.rollbacks_triggered = len(self.innovation_system.checkpoints) - 1

                # Progress log
                if (i + 1) % 10 == 0:
                    logger.info(f"  Drift test progress: {i + 1}/{iterations} (max drift: {metrics.max_drift_score:.3f})")

        except Exception as e:
            logger.error(f"Drift boundary test failed: {e}")
            metrics.system_crashes += 1
            metrics.errors_encountered.append(f"System crash: {str(e)[:200]}")

        finally:
            # Stop resource monitoring
            monitor_task.cancel()
            try:
                await monitor_task
            except asyncio.CancelledError:
                pass

        metrics.end_time = datetime.now(timezone.utc)
        total_time = (metrics.end_time - metrics.start_time).total_seconds()
        metrics.operations_per_second = metrics.total_operations / total_time if total_time > 0 else 0
        metrics.recovery_success_rate = (
            metrics.successful_operations / metrics.total_operations
            if metrics.total_operations > 0 else 0
        )

        self._log_metrics(metrics)
        return metrics

    def _log_metrics(self, metrics: StressTestMetrics) -> None:
        """Log stress test metrics"""
        logger.info(f"\n📊 Stress Test Results: {metrics.test_name}")
        logger.info(f"  Duration: {(metrics.end_time - metrics.start_time).total_seconds():.2f}s")
        logger.info(f"  Operations: {metrics.successful_operations}/{metrics.total_operations} successful")
        logger.info(f"  Throughput: {metrics.operations_per_second:.2f} ops/sec")
        logger.info(f"  Avg Time: {metrics.avg_operation_time:.3f}s")
        logger.info(f"  Peak Memory: {metrics.peak_memory_mb:.1f} MB")
        logger.info(f"  Max Drift: {metrics.max_drift_score:.3f}")
        logger.info(f"  Drift Violations: {metrics.drift_violations}")
        logger.info(f"  Safety Interventions: {metrics.safety_interventions}")
        logger.info(f"  Rollbacks: {metrics.rollbacks_triggered}")
        logger.info(f"  Errors: {len(metrics.errors_encountered)}")

    async def run_all_stress_tests(self) -> Dict[str, Any]:
        """Run complete stress test suite"""
        logger.info("="*60)
        logger.info("INNOVATION SYSTEM STRESS TEST SUITE")
        logger.info("="*60)

        # Setup with aggressive config
        await self.setup(aggressive_config=True)

        # Test 1: Massive parallel exploration
        metrics1 = await self.stress_test_massive_parallel_exploration(reality_count=5000)
        self.metrics.append(metrics1)
        await asyncio.sleep(1)  # Cool down

        # Test 2: Rapid fire generation
        metrics2 = await self.stress_test_rapid_fire_generation(operations=100, concurrent=5)
        self.metrics.append(metrics2)
        await asyncio.sleep(1)  # Cool down

        # Test 3: Drift boundary testing
        metrics3 = await self.stress_test_drift_boundary(iterations=50)
        self.metrics.append(metrics3)

        # Cleanup
        await self.teardown()

        # Generate report
        report = self.generate_report()
        self.save_results(report)

        return report

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive stress test report"""
        report = {
            'test_suite': 'Innovation System Stress Tests',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'tests_run': len(self.metrics),
            'summary': {
                'total_operations': sum(m.total_operations for m in self.metrics),
                'total_successful': sum(m.successful_operations for m in self.metrics),
                'total_failed': sum(m.failed_operations for m in self.metrics),
                'avg_success_rate': sum(m.recovery_success_rate for m in self.metrics) / len(self.metrics) if self.metrics else 0,
                'max_drift_observed': max(m.max_drift_score for m in self.metrics) if self.metrics else 0,
                'total_safety_interventions': sum(m.safety_interventions for m in self.metrics),
                'total_rollbacks': sum(m.rollbacks_triggered for m in self.metrics)
            },
            'performance': {
                'avg_throughput': sum(m.operations_per_second for m in self.metrics) / len(self.metrics) if self.metrics else 0,
                'peak_memory_mb': max(m.peak_memory_mb for m in self.metrics) if self.metrics else 0,
                'peak_cpu_percent': max(m.peak_cpu_percent for m in self.metrics) if self.metrics else 0
            },
            'stability': {
                'total_errors': sum(len(m.errors_encountered) for m in self.metrics),
                'system_crashes': sum(m.system_crashes for m in self.metrics)
            },
            'test_results': [m.to_dict() for m in self.metrics]
        }

        # Print summary
        logger.info("\n" + "="*60)
        logger.info("STRESS TEST SUMMARY")
        logger.info("="*60)
        logger.info(f"Tests Run: {report['tests_run']}")
        logger.info(f"Total Operations: {report['summary']['total_operations']}")
        logger.info(f"Success Rate: {report['summary']['avg_success_rate']*100:.1f}%")
        logger.info(f"Avg Throughput: {report['performance']['avg_throughput']:.2f} ops/sec")
        logger.info(f"Peak Memory: {report['performance']['peak_memory_mb']:.1f} MB")
        logger.info(f"Max Drift: {report['summary']['max_drift_observed']:.3f}")
        logger.info(f"System Crashes: {report['stability']['system_crashes']}")
        logger.info("="*60)

        return report

    def save_results(self, report: Dict[str, Any]) -> None:
        """Save stress test results"""
        results_dir = Path(__file__).parent.parent / "test_results"
        results_dir.mkdir(exist_ok=True)

        output_file = results_dir / "innovation_stress_results.json"
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"📊 Stress test results saved to: {output_file}")


class ResourceMonitor:
    """Monitor system resources during testing"""

    async def monitor(self, metrics: StressTestMetrics, interval: float = 0.1):
        """Monitor resources and update metrics"""
        memory_samples = []
        cpu_samples = []

        try:
            process = psutil.Process()

            while True:
                # Memory usage
                memory_mb = process.memory_info().rss / 1024 / 1024
                memory_samples.append(memory_mb)
                metrics.peak_memory_mb = max(metrics.peak_memory_mb, memory_mb)

                # CPU usage
                cpu_percent = process.cpu_percent()
                cpu_samples.append(cpu_percent)
                metrics.peak_cpu_percent = max(metrics.peak_cpu_percent, cpu_percent)

                await asyncio.sleep(interval)

        except asyncio.CancelledError:
            # Calculate averages before stopping
            if memory_samples:
                metrics.avg_memory_mb = sum(memory_samples) / len(memory_samples)
            if cpu_samples:
                metrics.avg_cpu_percent = sum(cpu_samples) / len(cpu_samples)
            raise


async def main():
    """Main stress test execution"""
    tester = InnovationStressTest()
    report = await tester.run_all_stress_tests()

    # Success if average success rate > 70% (stress tests are harder)
    success_rate = report['summary']['avg_success_rate']
    success = success_rate >= 0.7 and report['stability']['system_crashes'] == 0

    if success:
        logger.info(f"\n✅ Stress tests PASSED with {success_rate*100:.1f}% success rate")
    else:
        logger.error(f"\n❌ Stress tests FAILED with {success_rate*100:.1f}% success rate")

    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
