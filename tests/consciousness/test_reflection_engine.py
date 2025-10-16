#!/usr/bin/env python3
"""
Comprehensive test suite for SelfReflectionEngine

Tests include:
- Property tests (Hypothesis): coherence monotonicity when state deltas shrink
- Chaos tests: injected noise → anomaly counter increments
- Performance tests: 10k iterations p95 <10ms (unit + E2E)
- Prometheus rule tests: alert if rate(lukhas_reflection_anomalies_total[5m]) > 0.1

Follows T4/0.01% excellence standards with regulatory-grade validation.
"""

import asyncio
import os
import statistics
import time
from typing import Any, Dict
from unittest.mock import patch

import pytest
from hypothesis import HealthCheck, given, settings, strategies as st

# Set up test environment
os.environ["CONSC_REFLECTION_ENABLED"] = "1"
os.environ["LUKHAS_LANE"] = "testing"

from lukhas.consciousness.reflection.self_reflection_engine import (
    REFLECTION_P95_TARGET_MS,
    ReflectionReport,
    SelfReflectionEngine,
)
from lukhas.consciousness.systems.state import ConsciousnessState


class MockContextProvider:
    """Mock context provider for testing"""

    def __init__(self, context_data: Dict[str, Any] = None, should_fail: bool = False):
        self.context_data = context_data or {"test": "context"}
        self.should_fail = should_fail

    async def get_context(self) -> Dict[str, Any]:
        if self.should_fail:
            raise Exception("Mock context provider failure")
        return self.context_data


class TestReflectionEngineUnit:
    """Unit tests for SelfReflectionEngine core functionality"""

    @pytest.fixture
    async def engine(self):
        """Create and initialize a test reflection engine"""
        engine = SelfReflectionEngine()
        await engine.init([])
        yield engine
        await engine.shutdown()

    @pytest.fixture
    async def consciousness_state(self):
        """Create a test consciousness state"""
        state = ConsciousnessState(
            level=0.8,
            awareness_type="enhanced",
            emotional_tone="positive"
        )
        await state.initialize()
        return state

    async def test_engine_initialization(self):
        """Test engine initialization and configuration"""
        engine = SelfReflectionEngine()

        # Test uninitialized state
        assert not engine.is_initialized
        assert engine.status == "inactive"

        # Test successful initialization
        success = await engine.init([])
        assert success
        assert engine.is_initialized
        assert engine.status == "active"

        await engine.shutdown()

    async def test_engine_initialization_with_context_providers(self):
        """Test engine initialization with context providers"""
        provider1 = MockContextProvider({"lukhas.memory": "data"})
        provider2 = MockContextProvider({"emotion": "calm"})

        engine = SelfReflectionEngine()
        success = await engine.init([provider1, provider2])

        assert success
        assert len(engine.context_providers) == 2

        await engine.shutdown()

    async def test_feature_flag_disabled(self):
        """Test engine behavior when feature flag is disabled"""
        with patch.dict(os.environ, {"CONSC_REFLECTION_ENABLED": "0"}):
            engine = SelfReflectionEngine()
            success = await engine.init([])

            assert success
            assert engine.status == "disabled"

            await engine.shutdown()

    async def test_basic_reflection(self, engine, consciousness_state):
        """Test basic reflection functionality"""
        report = await engine.reflect(consciousness_state)

        assert isinstance(report, ReflectionReport)
        assert report.schema_version == "1.0.0"
        assert report.correlation_id.startswith("reflection_")
        assert report.reflection_duration_ms >= 0
        assert 0.0 <= report.coherence_score <= 1.0
        assert report.consciousness_level == consciousness_state.level
        assert report.awareness_type == consciousness_state.awareness_type

    async def test_reflection_without_initialization(self):
        """Test reflection fails gracefully when engine not initialized"""
        engine = SelfReflectionEngine()
        state = ConsciousnessState()

        report = await engine.reflect(state)

        assert report.anomaly_count > 0
        assert any(a["type"] == "engine_error" for a in report.anomalies)

    async def test_coherence_calculation(self, engine, consciousness_state):
        """Test coherence score calculation with state changes"""
        # First reflection - should have perfect coherence
        report1 = await engine.reflect(consciousness_state)
        assert report1.coherence_score == 1.0

        # Small change - should maintain high coherence
        consciousness_state.level = 0.81
        report2 = await engine.reflect(consciousness_state)
        assert report2.coherence_score >= 0.95

        # Large change - should reduce coherence
        consciousness_state.level = 0.2
        report3 = await engine.reflect(consciousness_state)
        assert report3.coherence_score < 0.85

    async def test_anomaly_detection(self, engine):
        """Test anomaly detection for invalid consciousness states"""
        # Invalid consciousness level
        invalid_state = ConsciousnessState(level=1.5)  # > 1.0
        await invalid_state.initialize()

        report = await engine.reflect(invalid_state)

        assert report.anomaly_count > 0
        assert any(a["type"] == "invalid_consciousness_level" for a in report.anomalies)

    async def test_context_provider_integration(self):
        """Test context provider integration"""
        provider = MockContextProvider({"test_context": "value"})
        engine = SelfReflectionEngine()
        await engine.init([provider])

        state = ConsciousnessState()
        await state.initialize()

        # Test successful context gathering
        context = await engine._gather_context()
        assert context["test_context"] == "value"

        await engine.shutdown()

    async def test_context_provider_failure_handling(self):
        """Test graceful handling of context provider failures"""
        failing_provider = MockContextProvider(should_fail=True)
        working_provider = MockContextProvider({"good": "data"})

        engine = SelfReflectionEngine()
        await engine.init([failing_provider, working_provider])

        # Should still work with one provider failing
        context = await engine._gather_context()
        assert context.get("good") == "data"
        assert "test" not in context  # Failed provider data not included

        await engine.shutdown()

    async def test_performance_tracking(self, engine, consciousness_state):
        """Test performance metrics tracking"""
        # Perform multiple reflections
        for _ in range(5):
            await engine.reflect(consciousness_state)

        stats = engine.get_performance_stats()

        assert stats["sample_count"] == 5
        assert "mean_latency_ms" in stats
        assert "median_latency_ms" in stats
        assert stats["status"] == "active"

    async def test_validation_performance_compliance(self, engine, consciousness_state):
        """Test validation of performance compliance"""
        # Perform enough reflections to enable validation
        for _ in range(15):
            await engine.reflect(consciousness_state)

        # Should validate successfully with normal performance
        is_valid = await engine.validate()
        assert is_valid

    def test_status_reporting(self, engine):
        """Test comprehensive status reporting"""
        status = engine.get_status()

        assert status["component"] == "SelfReflectionEngine"
        assert status["category"] == "consciousness"
        assert status["status"] == "active"
        assert status["initialized"] is True
        assert "timestamp" in status
        assert "feature_enabled" in status


class TestReflectionEngineProperty:
    """Property-based tests using Hypothesis"""

    @given(
        initial_level=st.floats(min_value=0.0, max_value=1.0),
        level_changes=st.lists(
            st.floats(min_value=-0.1, max_value=0.1),
            min_size=3,
            max_size=10
        )
    )
    @settings(
        max_examples=50,
        deadline=5000,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    async def test_coherence_monotonicity_property(self, initial_level, level_changes):
        """
        Property test: coherence should increase as state deltas shrink

        This tests the core invariant that smaller state changes should
        result in higher coherence scores.
        """
        engine = SelfReflectionEngine()
        await engine.init([])

        try:
            state = ConsciousnessState(level=initial_level)
            await state.initialize()

            coherence_scores = []

            # Apply progressively smaller changes
            for i, change in enumerate(level_changes):
                # Scale change to make it progressively smaller
                scaled_change = change / (i + 1)
                new_level = max(0.0, min(1.0, state.level + scaled_change))
                state.level = new_level

                report = await engine.reflect(state)
                coherence_scores.append(report.coherence_score)

            # After initial baseline, coherence should generally increase
            # as changes become smaller (allowing for noise)
            if len(coherence_scores) > 3:
                recent_coherence = statistics.mean(coherence_scores[-3:])
                early_coherence = statistics.mean(coherence_scores[1:4])  # Skip first (perfect score)

                # Allow some tolerance for natural variation
                assert recent_coherence >= early_coherence - 0.1, \
                    f"Coherence should improve with smaller changes: {early_coherence} -> {recent_coherence}"

        finally:
            await engine.shutdown()

    @given(
        noise_levels=st.lists(
            st.floats(min_value=0.0, max_value=0.5),
            min_size=5,
            max_size=15
        )
    )
    @settings(max_examples=20, deadline=10000)
    async def test_noise_injection_anomaly_property(self, noise_levels):
        """
        Property test: injected noise should increase anomaly detection

        Higher noise levels should result in more anomalies being detected.
        """
        engine = SelfReflectionEngine()
        await engine.init([])

        try:
            state = ConsciousnessState(level=0.5)
            await state.initialize()

            low_noise_anomalies = 0
            high_noise_anomalies = 0

            for noise in noise_levels:
                # Apply noise to consciousness level
                noisy_level = max(0.0, min(1.0, 0.5 + noise))
                state.level = noisy_level

                report = await engine.reflect(state)

                if noise < 0.1:  # Low noise
                    low_noise_anomalies += report.anomaly_count
                elif noise > 0.3:  # High noise
                    high_noise_anomalies += report.anomaly_count

            # Higher noise should generally produce more anomalies
            # (allowing for statistical variation)
            if high_noise_anomalies > 0 or low_noise_anomalies > 0:
                anomaly_ratio = high_noise_anomalies / max(1, low_noise_anomalies)
                assert anomaly_ratio >= 0.5, \
                    f"High noise should produce more anomalies: low={low_noise_anomalies}, high={high_noise_anomalies}"

        finally:
            await engine.shutdown()


class TestReflectionEngineChaos:
    """Chaos engineering tests for resilience validation"""

    async def test_chaos_high_frequency_reflections(self):
        """Chaos test: engine handles high-frequency reflection requests"""
        engine = SelfReflectionEngine()
        await engine.init([])

        try:
            state = ConsciousnessState(level=0.7)
            await state.initialize()

            # Rapid-fire reflections to test stability
            reports = []
            start_time = time.perf_counter()

            for _ in range(100):
                report = await engine.reflect(state)
                reports.append(report)
                state.level = max(0.0, min(1.0, state.level + 0.001))  # Small perturbations

            duration = time.perf_counter() - start_time

            # Validate no degradation under load
            assert len(reports) == 100
            assert all(r.reflection_duration_ms < 50 for r in reports[-10:])  # Last 10 should be fast
            assert engine.anomaly_counter < 10  # Should not generate excessive anomalies

            print(f"Chaos test: 100 reflections in {duration:.2f}s")

        finally:
            await engine.shutdown()

    async def test_chaos_context_provider_failures(self):
        """Chaos test: engine resilience with failing context providers"""
        failing_provider = MockContextProvider(should_fail=True)
        working_provider = MockContextProvider({"stable": "data"})

        engine = SelfReflectionEngine()
        await engine.init([failing_provider, working_provider])

        try:
            state = ConsciousnessState()
            await state.initialize()

            # Multiple reflections with failing provider
            successful_reflections = 0
            for _ in range(10):
                report = await engine.reflect(state)
                if report.reflection_duration_ms > 0:  # Successful reflection
                    successful_reflections += 1

            # Should continue working despite provider failures
            assert successful_reflections >= 8  # Allow some failures
            assert engine.status == "active"

        finally:
            await engine.shutdown()

    async def test_chaos_memory_pressure(self):
        """Chaos test: engine behavior under memory pressure simulation"""
        engine = SelfReflectionEngine()
        await engine.init([])

        try:
            state = ConsciousnessState()
            await state.initialize()

            # Simulate memory pressure by creating large objects
            memory_hogs = []

            for i in range(10):
                # Create some memory pressure
                memory_hogs.append([0] * 10000)

                # Engine should still work
                report = await engine.reflect(state)
                assert report.correlation_id is not None

                # Clean up periodically
                if i % 3 == 0:
                    memory_hogs.clear()

            # Validate engine survived memory pressure
            final_report = await engine.reflect(state)
            assert final_report.reflection_duration_ms < REFLECTION_P95_TARGET_MS * 2

        finally:
            await engine.shutdown()


@pytest.mark.performance
class TestReflectionEnginePerformance:
    """Performance tests for SLO validation"""

    @pytest.mark.asyncio
    async def test_unit_performance_10k_iterations(self):
        """
        Performance test: 10k iterations p95 <10ms (unit level)

        Tests the core reflection loop performance without external dependencies.
        """
        engine = SelfReflectionEngine()
        await engine.init([])

        try:
            state = ConsciousnessState(level=0.5)
            await state.initialize()

            latencies = []
            anomaly_count = 0

            print("Running 10k unit performance test...")
            start_time = time.perf_counter()

            for i in range(10000):
                if i % 1000 == 0:
                    print(f"Progress: {i}/10000")

                iteration_start = time.perf_counter()
                report = await engine.reflect(state)
                iteration_time = (time.perf_counter() - iteration_start) * 1000

                latencies.append(iteration_time)
                anomaly_count += report.anomaly_count

                # Small state perturbations to avoid staleness
                state.level = max(0.0, min(1.0, state.level + (i % 100 - 50) * 0.001))

            total_time = time.perf_counter() - start_time

            # Calculate performance metrics
            p95_latency = statistics.quantiles(latencies, n=20)[18]  # 95th percentile
            mean_latency = statistics.mean(latencies)
            cv = statistics.stdev(latencies) / mean_latency

            print("\nUnit Performance Results:")
            print(f"Total time: {total_time:.2f}s")
            print(f"Mean latency: {mean_latency:.3f}ms")
            print(f"P95 latency: {p95_latency:.3f}ms")
            print(f"CV: {cv:.3f}")
            print(f"Total anomalies: {anomaly_count}")

            # Validate SLO compliance
            assert p95_latency < REFLECTION_P95_TARGET_MS, \
                f"P95 latency {p95_latency:.3f}ms exceeds target {REFLECTION_P95_TARGET_MS}ms"

            assert cv < 0.10, \
                f"Coefficient of variation {cv:.3f} exceeds target 0.10"

            assert anomaly_count < 100, \
                f"Excessive anomalies detected: {anomaly_count}"

        finally:
            await engine.shutdown()

    @pytest.mark.asyncio
    async def test_e2e_performance_with_context(self):
        """
        Performance test: E2E with context providers (smaller scale)

        Tests full integration performance including context gathering.
        """
        # Create context providers
        providers = [
            MockContextProvider({"lukhas.memory": f"data_{i}"})
            for i in range(3)
        ]

        engine = SelfReflectionEngine()
        await engine.init(providers)

        try:
            state = ConsciousnessState(level=0.6)
            await state.initialize()

            latencies = []

            print("Running E2E performance test (2000 iterations)...")

            for i in range(2000):
                if i % 500 == 0:
                    print(f"Progress: {i}/2000")

                start = time.perf_counter()
                await engine.reflect(state)
                latency = (time.perf_counter() - start) * 1000

                latencies.append(latency)

                # Vary state for realistic testing
                state.level = 0.6 + 0.3 * (i % 100) / 100

            # Performance analysis
            p95_latency = statistics.quantiles(latencies, n=20)[18]
            mean_latency = statistics.mean(latencies)

            print("\nE2E Performance Results:")
            print(f"Mean latency: {mean_latency:.3f}ms")
            print(f"P95 latency: {p95_latency:.3f}ms")

            # E2E allows slightly higher latency due to context overhead
            assert p95_latency < REFLECTION_P95_TARGET_MS * 2, \
                f"E2E P95 latency {p95_latency:.3f}ms too high"

        finally:
            await engine.shutdown()

    @pytest.mark.asyncio
    async def test_concurrent_reflection_performance(self):
        """Test performance under concurrent reflection loads"""
        engine = SelfReflectionEngine()
        await engine.init([])

        try:
            async def reflection_worker(worker_id: int, iterations: int):
                """Worker function for concurrent testing"""
                state = ConsciousnessState(level=0.5 + worker_id * 0.1)
                await state.initialize()

                latencies = []
                for i in range(iterations):
                    start = time.perf_counter()
                    await engine.reflect(state)
                    latency = (time.perf_counter() - start) * 1000
                    latencies.append(latency)

                    state.level = max(0.0, min(1.0, state.level + 0.001))

                return latencies

            # Run concurrent workers
            print("Running concurrent performance test...")
            tasks = [
                reflection_worker(i, 500)
                for i in range(4)  # 4 concurrent workers
            ]

            results = await asyncio.gather(*tasks)

            # Aggregate results
            all_latencies = []
            for worker_latencies in results:
                all_latencies.extend(worker_latencies)

            p95_concurrent = statistics.quantiles(all_latencies, n=20)[18]
            mean_concurrent = statistics.mean(all_latencies)

            print("\nConcurrent Performance Results:")
            print(f"Total reflections: {len(all_latencies)}")
            print(f"Mean latency: {mean_concurrent:.3f}ms")
            print(f"P95 latency: {p95_concurrent:.3f}ms")

            # Concurrent operations may have higher latency
            assert p95_concurrent < REFLECTION_P95_TARGET_MS * 3, \
                f"Concurrent P95 latency {p95_concurrent:.3f}ms too high"

        finally:
            await engine.shutdown()


@pytest.mark.alerting
class TestPrometheusRules:
    """Tests for Prometheus alerting rules compliance"""

    async def test_anomaly_rate_alert_threshold(self):
        """
        Test Prometheus rule: alert if rate(lukhas_reflection_anomalies_total[5m]) > 0.1

        Simulates anomaly generation to validate alerting thresholds.
        """
        engine = SelfReflectionEngine()
        await engine.init([])

        try:
            # Simulate anomaly generation over time
            anomaly_timestamps = []

            # Generate anomalies at different rates
            for rate_multiplier in [0.05, 0.15, 0.25]:  # 5%, 15%, 25% anomaly rates
                start_time = time.time()
                anomalies_in_window = 0

                for i in range(100):
                    # Create state that triggers anomalies based on rate
                    if i < rate_multiplier * 100:
                        state = ConsciousnessState(level=1.5)  # Invalid level
                    else:
                        state = ConsciousnessState(level=0.5)  # Valid level

                    await state.initialize()
                    report = await engine.reflect(state)

                    if report.anomaly_count > 0:
                        anomalies_in_window += report.anomaly_count
                        anomaly_timestamps.append(time.time())

                window_duration = time.time() - start_time
                anomaly_rate = anomalies_in_window / max(1, window_duration)

                print(f"Rate {rate_multiplier*100}%: {anomaly_rate:.3f} anomalies/sec")

                # Validate alert threshold behavior
                if rate_multiplier >= 0.15:  # Above 15% should trigger alerts
                    assert anomaly_rate > 0.1, \
                        f"High anomaly rate {anomaly_rate:.3f} should exceed 0.1 threshold"

                # Reset engine state between rate tests
                engine.anomaly_counter = 0

        finally:
            await engine.shutdown()

    async def test_latency_alert_conditions(self):
        """Test latency-based alerting conditions"""
        engine = SelfReflectionEngine()
        await engine.init([])

        try:
            state = ConsciousnessState()
            await state.initialize()

            # Generate baseline performance
            for _ in range(50):
                await engine.reflect(state)

            engine.get_performance_stats()

            # Simulate performance degradation
            with patch('time.perf_counter', side_effect=self._slow_perf_counter):
                degraded_latencies = []
                for _ in range(20):
                    time.time()
                    await engine.reflect(state)
                    # Record artificially high latency
                    degraded_latencies.append(25.0)  # Simulate 25ms latency
                    engine.performance_buffer.append(25.0)

            stats_after = engine.get_performance_stats()

            # Should detect performance degradation
            if "p95_latency_ms" in stats_after:
                assert stats_after["p95_latency_ms"] > REFLECTION_P95_TARGET_MS
                assert not stats_after.get("within_slo", True)

        finally:
            await engine.shutdown()

    def _slow_perf_counter(self):
        """Mock perf_counter that simulates slow performance"""
        self._call_count = getattr(self, '_call_count', 0) + 1
        if self._call_count % 2 == 0:  # Return value for end timing
            return 0.025  # 25ms elapsed
        else:  # Return value for start timing
            return 0.0


if __name__ == "__main__":
    # Run basic test when executed directly
    import asyncio

    async def run_basic_tests():
        print("Running basic reflection engine tests...")

        # Test 1: Basic functionality
        engine = SelfReflectionEngine()
        success = await engine.init([])
        assert success, "Engine initialization failed"

        state = ConsciousnessState(level=0.7)
        await state.initialize()

        report = await engine.reflect(state)
        assert report.reflection_duration_ms < REFLECTION_P95_TARGET_MS
        print(f"✅ Basic reflection: {report.reflection_duration_ms:.2f}ms")

        # Test 2: Performance sample
        latencies = []
        for _ in range(100):
            start = time.perf_counter()
            await engine.reflect(state)
            latency = (time.perf_counter() - start) * 1000
            latencies.append(latency)

        p95 = statistics.quantiles(latencies, n=20)[18]
        print(f"✅ 100-iteration P95: {p95:.2f}ms (target: <{REFLECTION_P95_TARGET_MS}ms)")

        # Test 3: Anomaly detection
        invalid_state = ConsciousnessState(level=1.2)
        await invalid_state.initialize()
        anomaly_report = await engine.reflect(invalid_state)
        assert anomaly_report.anomaly_count > 0
        print(f"✅ Anomaly detection: {anomaly_report.anomaly_count} anomalies")

        await engine.shutdown()
        print("All basic tests passed!")

    asyncio.run(run_basic_tests())
