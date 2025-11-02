"""
T4/0.01% Excellence Tests: Memory Event Optimization
====================================================

Comprehensive test suite for Memory Event bounded optimization,
including unit tests, property tests, load tests, and memory leak detection.
"""

import gc
import os
import sys
import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor

import psutil
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

from memory.memory_event import MemoryEvent, MemoryEventFactory


class TestMemoryEventOptimization:
    """Test Memory Event bounded optimization and performance"""

    def setup_method(self):
        """Setup test environment"""
        self.factory = MemoryEventFactory()

    def test_drift_history_is_bounded_deque(self):
        """Verify drift_history uses bounded deque instead of unbounded list"""
        assert isinstance(self.factory._drift_history, deque)
        assert self.factory._drift_history.maxlen == 100

    def test_drift_history_respects_bounds(self):
        """Test drift_history automatically maintains bounds"""
        # Add more than maxlen items
        for i in range(150):
            self.factory._drift_history.append(float(i))

        # Should maintain exactly maxlen items
        assert len(self.factory._drift_history) == 100

        # Should contain the last 100 items (50-149)
        expected_values = list(range(50, 150))
        actual_values = list(self.factory._drift_history)
        assert actual_values == expected_values

    def test_drift_trend_calculation_with_empty_deque(self):
        """Test drift trend calculation handles empty deque gracefully"""
        # Empty drift history
        assert len(self.factory._drift_history) == 0

        # Create event with empty history
        event = self.factory.create(data={"test": "data"}, metadata={"affect_delta": 0.5})

        # Should not crash and should handle empty deque
        assert "driftTrend" in event.metadata["metrics"]
        drift_trend = event.metadata["metrics"]["driftTrend"]
        assert isinstance(drift_trend, float)

    def test_drift_trend_calculation_accuracy(self):
        """Test drift trend calculation with known values"""
        # Add known drift values
        test_values = [0.1, 0.2, 0.3, 0.4, 0.5]
        for value in test_values:
            self.factory._drift_history.append(value)

        # Create event which will add one more value
        event = self.factory.create(data={"test": "data"}, metadata={"affect_delta": 0.6, "driftScore": 0.6})

        # Should calculate trend from last 3 values: [0.4, 0.5, 0.6]
        expected_trend = (0.4 + 0.5 + 0.6) / 3
        actual_trend = event.metadata["metrics"]["driftTrend"]
        assert abs(actual_trend - expected_trend) < 0.001

    @pytest.mark.performance
    def test_memory_usage_bounded_under_load(self):
        """Test memory usage remains bounded under high event load"""
        process = psutil.Process()
        initial_memory = process.memory_info().rss

        # Create many events to test memory bounds
        for i in range(10000):
            self.factory.create(data={"event": i}, metadata={"affect_delta": float(i % 100) / 100.0})

        # Force garbage collection
        gc.collect()

        final_memory = process.memory_info().rss
        memory_growth = final_memory - initial_memory

        # Memory growth should be reasonable (less than 50MB for 10K events)
        assert memory_growth < 50 * 1024 * 1024, f"Excessive memory growth: {memory_growth / 1024 / 1024:.1f}MB"

        # Drift history should still be bounded
        assert len(self.factory._drift_history) <= 100

    @pytest.mark.performance
    def test_event_creation_performance(self):
        """Test event creation performance meets requirements"""
        # Warm up
        for _ in range(100):
            self.factory.create(data={"test": "data"}, metadata={"affect_delta": 0.5})

        # Measure performance
        start_time = time.time()
        event_count = 1000

        for i in range(event_count):
            self.factory.create(data={"event": i}, metadata={"affect_delta": float(i % 100) / 100.0})

        end_time = time.time()
        total_time = end_time - start_time
        events_per_second = event_count / total_time

        # Should handle at least 10,000 events/second
        assert events_per_second > 10000, f"Performance too slow: {events_per_second:.0f} events/sec"

    @pytest.mark.load
    def test_concurrent_event_creation(self):
        """Test thread-safe event creation under concurrent load"""

        def create_events(thread_id, event_count):
            for i in range(event_count):
                self.factory.create(
                    data={"thread": thread_id, "event": i}, metadata={"affect_delta": float(i % 100) / 100.0}
                )

        # Run concurrent threads
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for thread_id in range(10):
                future = executor.submit(create_events, thread_id, 1000)
                futures.append(future)

            # Wait for completion
            for future in futures:
                future.result()

        # Verify bounds maintained under concurrency
        assert len(self.factory._drift_history) <= 100

    @pytest.mark.property
    def test_deque_invariants(self):
        """Property-based tests for deque behavior invariants"""
        from hypothesis import given, strategies as st

        @given(st.lists(st.floats(min_value=-1.0, max_value=1.0, allow_nan=False), min_size=0, max_size=200))
        def check_deque_invariants(drift_values):
            factory = MemoryEventFactory()

            # Add all values
            for value in drift_values:
                factory._drift_history.append(value)

            # Invariants that must always hold
            assert len(factory._drift_history) <= 100
            assert isinstance(factory._drift_history, deque)
            assert factory._drift_history.maxlen == 100

            # If we have values, they should be the most recent ones
            if len(drift_values) > 100:
                expected_values = drift_values[-100:]
                actual_values = list(factory._drift_history)
                assert actual_values == expected_values

        check_deque_invariants()

    def test_memory_leak_prevention(self):
        """Test that repeated operations don't cause memory leaks"""
        # Get baseline memory
        gc.collect()
        initial_objects = len(gc.get_objects())

        # Perform many operations
        for cycle in range(100):
            factory = MemoryEventFactory()
            for i in range(1000):
                factory.create(data={"cycle": cycle, "event": i}, metadata={"affect_delta": float(i % 100) / 100.0})
            del factory

        # Force garbage collection
        gc.collect()
        final_objects = len(gc.get_objects())

        # Object count should not grow significantly
        object_growth = final_objects - initial_objects
        assert object_growth < 1000, f"Potential memory leak: {object_growth} new objects"

    @pytest.mark.stress
    def test_extreme_load_stability(self):
        """Test system stability under extreme load"""
        factory = MemoryEventFactory()

        # Create extreme number of events
        for i in range(100000):
            event = factory.create(data={"stress_test": i}, metadata={"affect_delta": float(i % 1000) / 1000.0})

            # Verify structure maintained
            assert "driftTrend" in event.metadata["metrics"]
            assert len(factory._drift_history) <= 100

        # System should still be responsive
        start_time = time.time()
        factory.create(data={"final_test": True}, metadata={"affect_delta": 0.5})
        response_time = time.time() - start_time

        assert response_time < 0.01, f"System became unresponsive: {response_time:.3f}s"

    def test_backward_compatibility(self):
        """Ensure optimization maintains API compatibility"""
        # Original API should still work
        event = self.factory.create(data={"test": "data"}, metadata={"affect_delta": 0.5})

        # Check return type and structure
        assert isinstance(event, MemoryEvent)
        assert hasattr(event, "data")
        assert hasattr(event, "metadata")
        assert "metrics" in event.metadata
        assert "driftTrend" in event.metadata["metrics"]

    def test_drift_history_operations_performance(self):
        """Test deque operations are more efficient than list operations"""
        # Test append performance (should be O(1))
        start_time = time.time()
        for i in range(10000):
            self.factory._drift_history.append(float(i))
        append_time = time.time() - start_time

        # Should be very fast for O(1) operations
        assert append_time < 0.1, f"Deque append too slow: {append_time:.3f}s"

        # Test recent access performance
        start_time = time.time()
        for _ in range(1000):
            list(self.factory._drift_history)[-3:]
        access_time = time.time() - start_time

        assert access_time < 0.1, f"Recent access too slow: {access_time:.3f}s"


@pytest.mark.integration
class TestMemoryEventIntegration:
    """Integration tests for optimized memory events"""

    def test_memory_event_metrics_integration(self):
        """Test optimized events integrate properly with metrics system"""

        factory = MemoryEventFactory()

        # Create events that should trigger metrics calculations
        event1 = factory.create(data={"test": "data1"}, metadata={"affect_delta": 0.3})

        event2 = factory.create(data={"test": "data2"}, metadata={"affect_delta": 0.7})

        # Both events should have proper metrics
        for event in [event1, event2]:
            assert "metrics" in event.metadata
            assert "driftTrend" in event.metadata["metrics"]
            assert isinstance(event.metadata["metrics"]["driftTrend"], float)

    def test_memory_guardian_integration(self):
        """Test optimized memory events work with Guardian system"""
        factory = MemoryEventFactory()

        # Create events with various drift patterns
        events = []
        for i in range(50):
            event = factory.create(data={"event": i}, metadata={"affect_delta": float(i % 10) / 10.0})
            events.append(event)

        # All events should be processable by Guardian
        for event in events:
            drift_score = event.metadata["metrics"]["driftScore"]
            assert isinstance(drift_score, (int, float))
            assert 0.0 <= drift_score <= 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-m", "not stress"])
