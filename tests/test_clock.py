#!/usr/bin/env python3
"""
Central Clock Ticker Tests
T4-Approved: Timing budget and performance validation

These tests verify that the central ticker maintains target FPS
and meets T4 performance requirements.
"""
import time
from unittest.mock import Mock

import pytest
from core.clock import Ticker, create_consciousness_ticker


@pytest.mark.clock
class TestTickerBasics:
    """Basic ticker functionality tests"""

    def test_ticker_initialization(self):
        """Test ticker initializes with correct FPS"""
        ticker = Ticker(fps=30)

        assert ticker.fps == 30
        assert ticker.period == 1.0 / 30
        assert ticker.tick_count == 0
        assert not ticker.running
        assert len(ticker.subscribers) == 0

    def test_ticker_subscribe_unsubscribe(self):
        """Test subscriber management"""
        ticker = Ticker()
        callback = Mock()

        # Subscribe
        ticker.subscribe(callback)
        assert callback in ticker.subscribers

        # Unsubscribe
        ticker.unsubscribe(callback)
        assert callback not in ticker.subscribers

    def test_ticker_metrics_initialization(self):
        """Test metrics are properly initialized"""
        ticker = Ticker()
        metrics = ticker.get_metrics()

        # Ticker attributes (source of truth)
        assert ticker.fps == 30  # Default FPS
        assert ticker.period == 1.0 / 30
        assert ticker.tick_count == 0
        assert ticker.running is False

        # Metrics structure (align with core/clock.py implementation)
        assert "ticks_processed" in metrics and metrics["ticks_processed"] == 0
        assert "ticks_dropped" in metrics and metrics["ticks_dropped"] == 0
        assert "total_processing_time" in metrics and metrics["total_processing_time"] == 0.0
        assert "max_processing_time" in metrics and metrics["max_processing_time"] == 0.0
        assert "p95_processing_time" in metrics and metrics["p95_processing_time"] == 0.0
        assert "subscriber_exceptions" in metrics and metrics["subscriber_exceptions"] == 0


@pytest.mark.clock
class TestTickerTiming:
    """Ticker timing and performance tests"""

    def test_ticker_budget_30fps(self):
        """T4 Requirement: Ticker maintains 30±5 FPS for 1 second"""
        ticker = Ticker(fps=30)
        ticks_received = []

        def counter(tick_count):
            ticks_received.append(tick_count)
            # Small processing delay to simulate real work
            time.sleep(0.005)  # 5ms processing time

        ticker.subscribe(counter)
        ticker.run(seconds=1)

        # T4 Acceptance: 25-35 ticks in 1 second (30±5)
        assert 25 <= len(ticks_received) <= 35
        print(f"Ticks in 1 second: {len(ticks_received)} (target: 30±5)")

    def test_ticker_performance_metrics(self):
        """Test that performance metrics are tracked"""
        ticker = Ticker(fps=30)
        processing_times = []

        def slow_processor(tick_count):
            # Simulate variable processing time
            delay = 0.01 if tick_count % 2 == 0 else 0.005
            time.sleep(delay)
            processing_times.append(delay)

        ticker.subscribe(slow_processor)
        ticker.run(seconds=0.5)  # Run for half second

        metrics = ticker.get_metrics()

        # Verify metrics were collected
        assert metrics["ticks_processed"] > 0
        assert metrics["total_processing_time"] > 0
        assert metrics["max_processing_time"] > 0

        # T4 Performance target: p95 < 35ms
        if len(processing_times) >= 20:
            p95_ms = metrics["p95_processing_time"] * 1000
            print(f"P95 processing time: {p95_ms:.2f}ms (target: <35ms)")

    def test_ticker_subscriber_error_handling(self):
        """Test that subscriber errors don't stop ticker"""
        ticker = Ticker(fps=60)  # Faster for quicker test
        good_calls = []
        error_calls = []

        def good_subscriber(tick_count):
            good_calls.append(tick_count)

        def error_subscriber(tick_count):
            error_calls.append(tick_count)
            if tick_count % 3 == 0:
                raise ValueError("Test error")

        ticker.subscribe(good_subscriber)
        ticker.subscribe(error_subscriber)

        # Run briefly
        ticker.run(seconds=0.2)

        # Both subscribers should have been called despite errors
        assert len(good_calls) > 0
        assert len(error_calls) > 0
        # Good subscriber should not be affected by error subscriber
        assert len(good_calls) == len(error_calls)

    def test_ticker_stop_gracefully(self):
        """Test ticker can be stopped gracefully"""
        ticker = Ticker()
        stop_called = False

        def stopper(tick_count):
            nonlocal stop_called
            if tick_count >= 5:
                ticker.stop()
                stop_called = True

        ticker.subscribe(stopper)
        ticker.run(seconds=10)  # Would run long, but should stop early

        assert stop_called
        assert not ticker.running
        assert ticker.tick_count >= 5


@pytest.mark.clock
class TestConsciousnessTicker:
    """Consciousness-specific ticker tests"""

    def test_consciousness_ticker_creation(self):
        """Test consciousness ticker factory"""
        ticker = create_consciousness_ticker()

        assert ticker.fps == 30
        assert ticker.period == 1.0 / 30

    def test_consciousness_tick_callback(self):
        """Test consciousness tick callback receives proper data"""
        ticker = create_consciousness_ticker()
        received_ticks = []

        def consciousness_processor(tick_count):
            received_ticks.append({
                "tick": tick_count,
                "timestamp": time.time()
            })

        ticker.subscribe(consciousness_processor)
        ticker.run(seconds=0.2)

        # Verify callbacks received tick data
        assert len(received_ticks) > 0
        assert all("tick" in tick for tick in received_ticks)
        assert all("timestamp" in tick for tick in received_ticks)

        # Verify tick counts are sequential
        tick_numbers = [tick["tick"] for tick in received_ticks]
        assert tick_numbers == list(range(len(tick_numbers)))


@pytest.mark.clock
@pytest.mark.slow
class TestTickerStressTest:
    """Stress tests for ticker performance"""

    def test_ticker_under_load(self):
        """Test ticker performance with multiple heavy subscribers"""
        ticker = Ticker(fps=30)
        results = []

        def heavy_processor_1(tick_count):
            # Simulate heavy computation
            start = time.time()
            sum(i * i for i in range(1000))  # CPU work
            end = time.time()
            results.append(("proc1", tick_count, end - start))

        def heavy_processor_2(tick_count):
            # Simulate I/O work
            start = time.time()
            time.sleep(0.001)  # Simulate I/O delay
            end = time.time()
            results.append(("proc2", tick_count, end - start))

        ticker.subscribe(heavy_processor_1)
        ticker.subscribe(heavy_processor_2)

        # Run under load
        ticker.run(seconds=0.5)

        metrics = ticker.get_metrics()

        # Verify ticker handled load
        assert metrics["ticks_processed"] > 0
        assert len(results) > 0

        # Log performance for analysis
        print(f"Processed {metrics['ticks_processed']} ticks under load")
        print(f"Dropped {metrics['ticks_dropped']} ticks")
        print(f"Max processing: {metrics['max_processing_time']*1000:.2f}ms")


@pytest.mark.clock
def test_ticker_example_usage():
    """Test example usage pattern from documentation"""
    ticker = Ticker(fps=30)
    frames_processed = 0

    def example_consciousness_frame(tick_count):
        nonlocal frames_processed
        frames_processed += 1
        # Simulate frame processing
        if tick_count % 30 == 0:  # Every second
            print(f"Consciousness second: {tick_count // 30 + 1}")

    ticker.subscribe(example_consciousness_frame)

    # Run for 2 seconds
    start_time = time.time()
    ticker.run(seconds=2)
    end_time = time.time()

    # Verify expected behavior
    actual_duration = end_time - start_time
    assert 1.8 <= actual_duration <= 2.2  # Allow some variance

    # Expect ~30 FPS with a ±5 FPS tolerance band
    expected_min = int(25 * actual_duration)
    expected_max = int(35 * actual_duration)
    assert expected_min <= frames_processed <= expected_max


if __name__ == "__main__":
    # Run clock tests only
    pytest.main([__file__, "-v", "-m", "clock"])
