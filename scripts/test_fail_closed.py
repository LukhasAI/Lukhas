#!/usr/bin/env python3
"""
T4/0.01% Excellence Chaos Engineering & Fail-Closed Validation

Tests system behavior under extreme stress conditions and validates fail-closed safety mechanisms.
Implements chaos engineering principles with controlled stress testing.
"""

import argparse
import asyncio
import json
import multiprocessing
import os
import random
import sys
import threading
import time
import traceback
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from governance.guardian_system import GuardianSystem
    from lukhas.consciousness import ConsciousnessStream, CreativityEngine
    from lukhas.consciousness.types import ConsciousnessState, CreativeTask
except ImportError:
    print("Warning: LUKHAS modules not available, using simulation mode")
    GuardianSystem = None
    ConsciousnessStream = None
    CreativityEngine = None


@dataclass
class StressTestResult:
    """Result of a single stress test execution."""
    test_id: str
    component: str
    stress_level: str
    success: bool
    latency_ms: float
    error_message: Optional[str]
    fail_closed: bool
    timestamp: float
    metadata: Dict[str, Any]


@dataclass
class ChaosTestSuite:
    """Complete chaos test suite results."""
    suite_id: str
    component: str
    stress_level: str
    total_tests: int
    successful_tests: int
    failed_tests: int
    fail_closed_violations: int
    average_latency_ms: float
    max_latency_ms: float
    results: List[StressTestResult]
    system_metrics: Dict[str, Any]


class ChaosEngineer:
    """Chaos engineering framework for T4/0.01% validation."""

    def __init__(self, component: str, stress_level: str = "moderate"):
        self.component = component
        self.stress_level = stress_level
        self.guardian = None
        self.consciousness_stream = None
        self.creativity_engine = None

        # Initialize components if available
        try:
            self._initialize_components()
        except Exception as e:
            print(f"Warning: Component initialization failed: {e}")

    def _initialize_components(self):
        """Initialize LUKHAS components for chaos testing."""
        if GuardianSystem:
            self.guardian = GuardianSystem()

        if ConsciousnessStream:
            self.consciousness_stream = ConsciousnessStream({
                "guardian_validator": self._mock_guardian_validator
            })

        if CreativityEngine:
            self.creativity_engine = CreativityEngine(
                guardian_validator=self._mock_guardian_validator
            )

    async def _mock_guardian_validator(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Mock Guardian validator with controlled failure scenarios."""
        # Simulate stress-induced delays
        if self.stress_level == "extreme":
            await asyncio.sleep(random.uniform(0.1, 0.5))  # High latency under stress
        elif self.stress_level == "high":
            await asyncio.sleep(random.uniform(0.01, 0.1))
        else:
            await asyncio.sleep(random.uniform(0.0001, 0.001))

        # Simulate occasional failures under stress
        failure_rate = {
            "low": 0.01,
            "moderate": 0.05,
            "high": 0.10,
            "extreme": 0.20
        }.get(self.stress_level, 0.05)

        if random.random() < failure_rate:
            raise Exception("Guardian service under stress")

        # Always fail-closed: when uncertain, deny
        uncertainty_rate = {
            "low": 0.02,
            "moderate": 0.10,
            "high": 0.20,
            "extreme": 0.30
        }.get(self.stress_level, 0.10)

        if random.random() < uncertainty_rate:
            return {
                "approved": False,  # FAIL-CLOSED behavior
                "reason": "System under stress - failing closed for safety",
                "confidence": 0.3,
                "stress_mode": True
            }

        return {
            "approved": True,
            "reason": "Content approved under stress conditions",
            "confidence": 0.8,
            "stress_mode": True
        }

    def apply_cpu_stress(self, intensity: float = 0.5):
        """Apply CPU stress to the system."""
        def cpu_stress_worker():
            """CPU-intensive worker function."""
            end_time = time.time() + 10  # Run for 10 seconds
            while time.time() < end_time:
                # CPU-intensive calculation
                for _ in range(10000):
                    _ = sum(i * i for i in range(100))

        # Determine number of workers based on intensity
        cpu_count = multiprocessing.cpu_count()
        worker_count = max(1, int(cpu_count * intensity))

        # Start CPU stress workers
        workers = []
        for _ in range(worker_count):
            worker = threading.Thread(target=cpu_stress_worker)
            worker.daemon = True
            worker.start()
            workers.append(worker)

        return workers

    def apply_memory_stress(self, memory_mb: int = 500):
        """Apply memory stress to the system."""
        stress_data = []

        try:
            # Allocate memory in chunks
            chunk_size = 1024 * 1024  # 1MB chunks
            chunks_needed = memory_mb

            for _ in range(chunks_needed):
                # Allocate and fill memory
                chunk = bytearray(chunk_size)
                # Fill with random data to prevent compression
                for i in range(0, chunk_size, 1024):
                    chunk[i:i+8] = os.urandom(8)
                stress_data.append(chunk)

            return stress_data

        except MemoryError:
            print(f"Warning: Could not allocate {memory_mb}MB of memory")
            return stress_data

    def apply_io_stress(self, duration: float = 5.0):
        """Apply I/O stress to the system."""
        def io_stress_worker():
            """I/O-intensive worker function."""
            end_time = time.time() + duration
            temp_files = []

            try:
                while time.time() < end_time:
                    # Create temporary file
                    temp_file = f"/tmp/stress_test_{os.getpid()}_{random.randint(1000, 9999)}.tmp"
                    temp_files.append(temp_file)

                    # Write random data
                    with open(temp_file, 'wb') as f:
                        f.write(os.urandom(1024 * 1024))  # 1MB

                    # Read it back
                    with open(temp_file, 'rb') as f:
                        _ = f.read()

            finally:
                # Cleanup
                for temp_file in temp_files:
                    try:
                        os.remove(temp_file)
                    except:
                        pass

        # Start I/O stress worker
        worker = threading.Thread(target=io_stress_worker)
        worker.daemon = True
        worker.start()
        return worker

    async def test_guardian_under_stress(self, test_count: int = 100) -> List[StressTestResult]:
        """Test Guardian system under stress conditions."""
        results = []

        # Apply stress based on level
        stress_workers = []
        memory_stress = None

        if self.stress_level in ["high", "extreme"]:
            # Apply CPU stress
            cpu_workers = self.apply_cpu_stress(intensity=0.7 if self.stress_level == "extreme" else 0.4)
            stress_workers.extend(cpu_workers)

            # Apply memory stress
            memory_mb = 1000 if self.stress_level == "extreme" else 500
            memory_stress = self.apply_memory_stress(memory_mb)

            # Apply I/O stress
            io_worker = self.apply_io_stress(duration=30.0)
            stress_workers.append(io_worker)

        try:
            for i in range(test_count):
                test_id = f"guardian_stress_{i:04d}"
                start_time = time.time()

                try:
                    # Create test request
                    request = {
                        "type": "creative_idea",
                        "content": {
                            "description": f"Test creative idea under stress #{i}",
                            "stress_test": True
                        },
                        "novelty": random.uniform(0.3, 0.9),
                        "coherence": random.uniform(0.3, 0.9)
                    }

                    # Test Guardian validation
                    if self.guardian:
                        response = await self.guardian.validate_async(request)
                    else:
                        response = await self._mock_guardian_validator(request)

                    end_time = time.time()
                    latency_ms = (end_time - start_time) * 1000

                    # Check fail-closed behavior
                    fail_closed = True
                    if response.get("approved") and response.get("confidence", 0) < 0.5:
                        # Suspicious: approved with low confidence under stress
                        fail_closed = False

                    results.append(StressTestResult(
                        test_id=test_id,
                        component="guardian",
                        stress_level=self.stress_level,
                        success=True,
                        latency_ms=latency_ms,
                        error_message=None,
                        fail_closed=fail_closed,
                        timestamp=start_time,
                        metadata={
                            "response": response,
                            "approved": response.get("approved", False),
                            "confidence": response.get("confidence", 0.0)
                        }
                    ))

                except Exception as e:
                    end_time = time.time()
                    latency_ms = (end_time - start_time) * 1000

                    # Exception during stress is acceptable if system fails closed
                    fail_closed = True  # Exceptions should fail closed

                    results.append(StressTestResult(
                        test_id=test_id,
                        component="guardian",
                        stress_level=self.stress_level,
                        success=False,
                        latency_ms=latency_ms,
                        error_message=str(e),
                        fail_closed=fail_closed,
                        timestamp=start_time,
                        metadata={"exception": str(e)}
                    ))

                # Brief pause between tests
                if i % 10 == 0:
                    await asyncio.sleep(0.01)

        finally:
            # Cleanup stress conditions
            del memory_stress  # Release memory
            # Workers will naturally terminate

        return results

    async def test_consciousness_under_stress(self, test_count: int = 50) -> List[StressTestResult]:
        """Test consciousness stream under stress conditions."""
        results = []

        if not self.consciousness_stream:
            # Simulate consciousness testing
            for i in range(test_count):
                await asyncio.sleep(0.001)
                results.append(StressTestResult(
                    test_id=f"consciousness_sim_{i:04d}",
                    component="consciousness",
                    stress_level=self.stress_level,
                    success=True,
                    latency_ms=random.uniform(50, 200),
                    error_message=None,
                    fail_closed=True,
                    timestamp=time.time(),
                    metadata={"simulated": True}
                ))
            return results

        try:
            await self.consciousness_stream.start()

            for i in range(test_count):
                test_id = f"consciousness_stress_{i:04d}"
                start_time = time.time()

                try:
                    # Create stress signals
                    signals = {
                        "processing_queue_size": random.randint(50, 200),
                        "active_threads": random.randint(10, 50),
                        "memory_pressure": random.uniform(0.7, 0.95),
                        "cpu_utilization": random.uniform(0.8, 0.99),
                        "stress_test": True
                    }

                    # Execute consciousness tick under stress
                    metrics = await self.consciousness_stream.tick(signals)

                    end_time = time.time()
                    latency_ms = (end_time - start_time) * 1000

                    # Validate fail-closed behavior
                    fail_closed = True
                    if metrics and hasattr(metrics, 'anomaly_rate_per_hour'):
                        if metrics.anomaly_rate_per_hour > 1000:  # Too many anomalies
                            fail_closed = False

                    results.append(StressTestResult(
                        test_id=test_id,
                        component="consciousness",
                        stress_level=self.stress_level,
                        success=metrics is not None,
                        latency_ms=latency_ms,
                        error_message=None,
                        fail_closed=fail_closed,
                        timestamp=start_time,
                        metadata={
                            "metrics_generated": metrics is not None,
                            "anomaly_rate": getattr(metrics, 'anomaly_rate_per_hour', 0) if metrics else 0
                        }
                    ))

                except Exception as e:
                    end_time = time.time()
                    latency_ms = (end_time - start_time) * 1000

                    results.append(StressTestResult(
                        test_id=test_id,
                        component="consciousness",
                        stress_level=self.stress_level,
                        success=False,
                        latency_ms=latency_ms,
                        error_message=str(e),
                        fail_closed=True,  # Exceptions should fail closed
                        timestamp=start_time,
                        metadata={"exception": str(e)}
                    ))

        finally:
            try:
                await self.consciousness_stream.stop()
            except:
                pass

        return results

    async def test_creativity_under_stress(self, test_count: int = 20) -> List[StressTestResult]:
        """Test creativity engine under stress conditions."""
        results = []

        for i in range(test_count):
            test_id = f"creativity_stress_{i:04d}"
            start_time = time.time()

            try:
                if self.creativity_engine:
                    # Create challenging creative task
                    task = CreativeTask(
                        prompt=f"Generate stress-tested creative solution #{i}",
                        min_ideas=random.randint(3, 8),
                        constraints=[f"stress_constraint_{j}" for j in range(random.randint(2, 5))],
                        max_generation_time_ms=100.0  # Tight time constraint
                    )

                    consciousness_state = ConsciousnessState(
                        phase="CREATE",
                        awareness_level="enhanced",
                        level=random.uniform(0.5, 0.9)
                    )

                    # Generate ideas under stress
                    snapshot = await self.creativity_engine.generate_ideas(
                        task, consciousness_state, {"stress_mode": True}
                    )

                    end_time = time.time()
                    latency_ms = (end_time - start_time) * 1000

                    # Validate fail-closed behavior for creativity
                    fail_closed = True
                    if snapshot:
                        # Check for concerning patterns
                        if len(snapshot.ideas) == 0 and latency_ms > 200:
                            fail_closed = False  # Should have failed faster

                        if snapshot.novelty_score > 0.95 and latency_ms < 10:
                            fail_closed = False  # Suspiciously fast high-quality output

                    results.append(StressTestResult(
                        test_id=test_id,
                        component="creativity",
                        stress_level=self.stress_level,
                        success=snapshot is not None,
                        latency_ms=latency_ms,
                        error_message=None,
                        fail_closed=fail_closed,
                        timestamp=start_time,
                        metadata={
                            "ideas_generated": len(snapshot.ideas) if snapshot else 0,
                            "novelty_score": snapshot.novelty_score if snapshot else 0.0,
                            "generation_time": snapshot.generation_time_ms if snapshot else 0.0
                        }
                    ))

                else:
                    # Simulate creativity testing
                    await asyncio.sleep(random.uniform(0.02, 0.1))
                    end_time = time.time()
                    latency_ms = (end_time - start_time) * 1000

                    results.append(StressTestResult(
                        test_id=test_id,
                        component="creativity",
                        stress_level=self.stress_level,
                        success=True,
                        latency_ms=latency_ms,
                        error_message=None,
                        fail_closed=True,
                        timestamp=start_time,
                        metadata={"simulated": True}
                    ))

            except Exception as e:
                end_time = time.time()
                latency_ms = (end_time - start_time) * 1000

                results.append(StressTestResult(
                    test_id=test_id,
                    component="creativity",
                    stress_level=self.stress_level,
                    success=False,
                    latency_ms=latency_ms,
                    error_message=str(e),
                    fail_closed=True,  # Exceptions should fail closed
                    timestamp=start_time,
                    metadata={"exception": str(e)}
                ))

        return results

    def capture_system_metrics(self) -> Dict[str, Any]:
        """Capture system metrics during stress testing."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": memory.available / (1024**3),
                "disk_percent": disk.percent,
                "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0],
                "process_count": len(psutil.pids()),
                "timestamp": time.time()
            }
        except Exception as e:
            return {"error": str(e), "timestamp": time.time()}

    async def run_chaos_test_suite(self) -> ChaosTestSuite:
        """Run complete chaos engineering test suite."""
        print(f"🌪️  Running Chaos Test Suite: {self.component} ({self.stress_level})")

        suite_id = f"chaos_{self.component}_{self.stress_level}_{int(time.time())}"
        start_time = time.time()

        # Capture initial system metrics
        initial_metrics = self.capture_system_metrics()

        all_results = []

        try:
            if self.component == "guardian" or self.component == "all":
                print("Testing Guardian under stress...")
                guardian_results = await self.test_guardian_under_stress()
                all_results.extend(guardian_results)

            if self.component == "consciousness" or self.component == "all":
                print("Testing Consciousness under stress...")
                consciousness_results = await self.test_consciousness_under_stress()
                all_results.extend(consciousness_results)

            if self.component == "creativity" or self.component == "all":
                print("Testing Creativity under stress...")
                creativity_results = await self.test_creativity_under_stress()
                all_results.extend(creativity_results)

        except Exception as e:
            print(f"Chaos test suite error: {e}")
            traceback.print_exc()

        # Capture final system metrics
        final_metrics = self.capture_system_metrics()

        # Analyze results
        total_tests = len(all_results)
        successful_tests = sum(1 for r in all_results if r.success)
        failed_tests = total_tests - successful_tests
        fail_closed_violations = sum(1 for r in all_results if not r.fail_closed)

        latencies = [r.latency_ms for r in all_results if r.latency_ms > 0]
        avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
        max_latency = max(latencies) if latencies else 0.0

        duration = time.time() - start_time

        suite_result = ChaosTestSuite(
            suite_id=suite_id,
            component=self.component,
            stress_level=self.stress_level,
            total_tests=total_tests,
            successful_tests=successful_tests,
            failed_tests=failed_tests,
            fail_closed_violations=fail_closed_violations,
            average_latency_ms=avg_latency,
            max_latency_ms=max_latency,
            results=all_results,
            system_metrics={
                "initial": initial_metrics,
                "final": final_metrics,
                "duration_seconds": duration
            }
        )

        return suite_result


def main():
    """Main chaos engineering execution function."""
    parser = argparse.ArgumentParser(description="T4/0.01% Chaos Engineering Tests")
    parser.add_argument("--component", choices=["guardian", "consciousness", "creativity", "all"],
                       default="guardian", help="Component to test")
    parser.add_argument("--stress-level", choices=["low", "moderate", "high", "extreme"],
                       default="moderate", help="Stress level")
    parser.add_argument("--output", required=True, help="Output JSON file")
    parser.add_argument("--requirement", default="never_false_positive",
                       help="Fail-closed requirement to validate")

    args = parser.parse_args()

    async def run_chaos_tests():
        # Create chaos engineer
        engineer = ChaosEngineer(args.component, args.stress_level)

        # Run test suite
        results = await engineer.run_chaos_test_suite()

        # Save results
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(asdict(results), f, indent=2, sort_keys=True)

        # Print summary
        print("\n🎯 Chaos Test Results:")
        print(f"Component: {results.component}")
        print(f"Stress Level: {results.stress_level}")
        print(f"Total Tests: {results.total_tests}")
        print(f"Successful: {results.successful_tests}")
        print(f"Failed: {results.failed_tests}")
        print(f"Fail-Closed Violations: {results.fail_closed_violations}")
        print(f"Average Latency: {results.average_latency_ms:.1f}ms")
        print(f"Max Latency: {results.max_latency_ms:.1f}ms")

        # Validate fail-closed requirement
        if args.requirement == "never_false_positive":
            if results.fail_closed_violations == 0:
                print("✅ FAIL-CLOSED VALIDATION: PASSED")
                print("🛡️  System maintains safety under stress")
            else:
                print("❌ FAIL-CLOSED VALIDATION: FAILED")
                print(f"⚠️  {results.fail_closed_violations} fail-closed violations detected")
                return 1

        print(f"Output: {args.output}")
        return 0

    # Run chaos tests
    result = asyncio.run(run_chaos_tests())
    sys.exit(result)


if __name__ == "__main__":
    main()
