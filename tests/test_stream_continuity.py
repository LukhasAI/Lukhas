#!/usr/bin/env python3
"""
tests/test_stream_continuity.py

Stream-continuity capability suite for Phase 4.
Tests zero unrouted signals, network coherence ≥0.8, and stream reliability.
"""
import os
import time

import pytest

from lukhas.core.consciousness_stream import ConsciousnessStream


class TestStreamContinuity:
    """Capability suite for stream-continuity validation."""

    def setup_method(self):
        """Set up hermetic test environment for capability tests."""
        os.environ["LUKHAS_LANE"] = "experimental"
        os.environ["PYTHONHASHSEED"] = "0"
        os.environ["TZ"] = "UTC"
        os.environ["LUKHAS_RNG_SEED"] = "42"

    def test_zero_unrouted_signals_guarantee(self):
        """Test zero unrouted signals guarantee - all events must be processed."""
        stream = ConsciousnessStream(fps=30, store_capacity=1000)

        # Start router to ensure it's active
        stream.router.start()

        # Process ticks and verify all are routed
        tick_count = 50
        for i in range(tick_count):
            stream._on_consciousness_tick(i)

        # Verify all events were processed through router
        router_logs = stream._router_logs
        publish_events = [log for log in router_logs if log["type"] == "router.publish"]

        # Should have router publish events for consciousness ticks
        assert len(publish_events) >= tick_count, f"Expected ≥{tick_count} router events, got {len(publish_events)}"

        # All router events should be successfully published (no routing failures)
        for event in publish_events:
            assert event["data"]["lane"] == "experimental"
            assert event["data"]["topic"] in ["breakthrough"], f"Unexpected topic: {event['data']['topic']}"

        # Zero unrouted guarantee: all consciousness events should have corresponding router activity
        assert len(publish_events) == tick_count, "Zero unrouted guarantee violated"

    def test_network_coherence_threshold(self):
        """Test network coherence ≥0.8 threshold validation."""
        stream = ConsciousnessStream(fps=30, store_capacity=500)

        # Process substantial load to build network coherence metrics
        for i in range(100):
            stream._on_consciousness_tick(i)
            if i % 10 == 0:
                time.sleep(0.001)  # Brief pause for timing variation

        # Calculate network coherence based on processing consistency
        metrics = stream.get_stream_metrics()

        # Use processing success rate as primary coherence measure (more reliable)
        # Timing-based coherence can be sensitive to system load

        # Primary coherence measure: event processing success rate
        total_events = stream.events_processed * 2  # tick + completion events
        events_in_store = metrics["store_size"]
        if stream.enable_backpressure and metrics["backpressure_stats"]:
            events_in_ring = metrics["backpressure_stats"]["current_size"]
            total_stored = events_in_store + events_in_ring
        else:
            total_stored = events_in_store

        processing_coherence = total_stored / max(1, total_events) if total_events > 0 else 1.0
        assert processing_coherence >= 0.8, f"Processing coherence {processing_coherence:.3f} below threshold"

    def test_stream_reliability_under_load(self):
        """Test stream reliability and continuity under sustained load."""
        stream = ConsciousnessStream(
            fps=20,  # Moderate rate for sustained testing
            store_capacity=200,
            enable_backpressure=True,
            backpressure_threshold=0.7
        )

        stream.router.start()

        # Sustained load test
        load_duration = 2.0  # 2 seconds
        expected_ticks = int(20 * load_duration)  # 20 FPS * 2 seconds

        start_time = time.perf_counter()
        tick_count = 0

        while (time.perf_counter() - start_time) < load_duration:
            stream._on_consciousness_tick(tick_count)
            tick_count += 1
            time.sleep(1.0 / 20)  # Maintain 20 FPS rhythm

        end_time = time.perf_counter()
        actual_duration = end_time - start_time

        # Verify stream continuity metrics
        metrics = stream.get_stream_metrics()

        # Stream should have processed events continuously
        assert stream.events_processed > 0, "No events processed during load test"

        # Processing rate should be consistent with target FPS
        actual_rate = stream.events_processed / actual_duration
        expected_rate = 20  # Target FPS
        rate_efficiency = actual_rate / expected_rate

        # Stream continuity: should maintain ≥80% of target processing rate
        assert rate_efficiency >= 0.8, f"Stream rate efficiency {rate_efficiency:.3f} below 0.8"

        # Router should have handled all events
        router_events = len([log for log in stream._router_logs if log["type"] == "router.publish"])
        assert router_events >= stream.events_processed * 0.8, "Router continuity below threshold"

    def test_fault_tolerance_and_recovery(self):
        """Test stream fault tolerance and recovery capabilities."""
        stream = ConsciousnessStream(fps=30, store_capacity=100)

        # Normal operation baseline
        for i in range(20):
            stream._on_consciousness_tick(i)

        baseline_processed = stream.events_processed

        # Simulate fault condition (router failure)
        original_router_publish = stream.router.publish
        failure_count = 0

        def faulty_router_publish(msg):
            nonlocal failure_count
            failure_count += 1
            if failure_count <= 5:  # Fail first 5 calls
                raise Exception("Simulated router failure")
            return original_router_publish(msg)

        stream.router.publish = faulty_router_publish

        # Continue processing during fault
        for i in range(20, 40):
            stream._on_consciousness_tick(i)

        # Verify fault tolerance
        post_fault_processed = stream.events_processed - baseline_processed

        # Stream should continue processing despite router failures
        assert post_fault_processed >= 15, f"Stream should process ≥15 events during fault, got {post_fault_processed}"

        # Check error events were created for failed router calls
        events = stream.get_recent_events(limit=100)
        error_events = [e for e in events if e.kind == "processing_error"]
        assert len(error_events) >= 5, f"Expected ≥5 error events for router failures, got {len(error_events)}"

    def test_multi_lane_coherence(self):
        """Test coherence across multiple lanes."""
        # Test experimental lane
        exp_stream = ConsciousnessStream(fps=20, store_capacity=100)

        for i in range(30):
            exp_stream._on_consciousness_tick(i)

        exp_metrics = exp_stream.get_stream_metrics()

        # Switch to candidate lane
        os.environ["LUKHAS_LANE"] = "candidate"
        cand_stream = ConsciousnessStream(fps=20, store_capacity=100)

        for i in range(30):
            cand_stream._on_consciousness_tick(i)

        cand_metrics = cand_stream.get_stream_metrics()

        # Verify lane isolation
        assert exp_metrics["lane"] == "experimental"
        assert cand_metrics["lane"] == "candidate"

        # Both lanes should achieve similar coherence levels
        exp_events = exp_stream.get_recent_events()
        cand_events = cand_stream.get_recent_events()

        exp_coherence = len(exp_events) / max(1, exp_metrics["events_processed"] * 2)
        cand_coherence = len(cand_events) / max(1, cand_metrics["events_processed"] * 2)

        assert exp_coherence >= 0.8, f"Experimental lane coherence {exp_coherence:.3f} below 0.8"
        assert cand_coherence >= 0.8, f"Candidate lane coherence {cand_coherence:.3f} below 0.8"

        # Reset lane
        os.environ["LUKHAS_LANE"] = "experimental"

    def test_memory_coherence_under_pressure(self):
        """Test memory coherence and leak prevention under pressure."""
        stream = ConsciousnessStream(
            fps=50,  # High rate
            store_capacity=50,  # Small capacity to create pressure
            enable_backpressure=True,
            backpressure_threshold=0.6
        )

        initial_metrics = stream.get_stream_metrics()

        # Generate sustained pressure
        for cycle in range(10):
            for i in range(20):  # 200 total events
                stream._on_consciousness_tick(cycle * 20 + i)

        final_metrics = stream.get_stream_metrics()

        # Memory coherence: bounded memory usage
        assert final_metrics["store_size"] <= final_metrics["store_capacity"], "Memory incoherence: store overflow"

        # Backpressure coherence: system should handle pressure gracefully
        if final_metrics["backpressure_stats"]:
            bp_stats = final_metrics["backpressure_stats"]
            # Should have applied backpressure mechanisms
            assert bp_stats["total_drops"] > 0 or bp_stats["decimation_events"] > 0, "No backpressure applied under pressure"
            # Drop rate should be reasonable (not losing everything)
            assert bp_stats["drop_rate"] < 0.5, f"Excessive drop rate: {bp_stats['drop_rate']:.3f}"

    def test_timing_coherence_and_drift_bounds(self):
        """Test timing coherence and drift boundary compliance."""
        stream = ConsciousnessStream(fps=30, store_capacity=200)

        # Process events with timing variations
        for i in range(60):
            stream._on_consciousness_tick(i)
            if i % 5 == 0:
                time.sleep(0.002)  # 2ms timing variation

        metrics = stream.get_stream_metrics()

        # Timing coherence: drift should be bounded
        drift_ema = metrics["drift_ema"]
        assert drift_ema < 0.1, f"Excessive timing drift: {drift_ema:.6f} (threshold: 0.1)"

        # Processing time coherence
        if metrics["tick_p95_ms"] > 0:
            assert metrics["tick_p95_ms"] < 50, f"P95 processing time {metrics['tick_p95_ms']:.1f}ms exceeds 50ms"

        # Average processing time should be reasonable
        if metrics["avg_tick_processing_ms"] > 0:
            assert metrics["avg_tick_processing_ms"] < 10, f"Average processing time {metrics['avg_tick_processing_ms']:.1f}ms exceeds 10ms"

    def test_comprehensive_stream_continuity_validation(self):
        """Comprehensive validation of all stream-continuity requirements."""
        # Create stream with production-like configuration
        stream = ConsciousnessStream(
            fps=30,
            store_capacity=500,
            enable_backpressure=True,
            backpressure_threshold=0.8,
            decimation_factor=2
        )

        stream.router.start()

        # Extended operation test
        start_time = time.perf_counter()
        total_ticks = 150  # 5 seconds at 30 FPS

        for i in range(total_ticks):
            stream._on_consciousness_tick(i)
            if i % 20 == 0:
                time.sleep(0.001)  # Periodic timing variation

        end_time = time.perf_counter()
        duration = end_time - start_time

        # Comprehensive validation
        metrics = stream.get_stream_metrics()

        # 1. Zero unrouted guarantee
        router_publishes = len([log for log in stream._router_logs if log["type"] == "router.publish"])
        assert router_publishes >= total_ticks, f"Unrouted events detected: {total_ticks - router_publishes}"

        # 2. Network coherence ≥0.8
        processing_rate = stream.events_processed / duration
        expected_rate = 30  # Target FPS
        rate_coherence = min(1.0, processing_rate / expected_rate)
        assert rate_coherence >= 0.8, f"Network coherence {rate_coherence:.3f} below 0.8"

        # 3. Stream continuity metrics
        assert metrics["events_processed"] >= total_ticks, "Stream continuity failure"
        assert metrics["drift_ema"] < 0.1, f"Excessive drift: {metrics['drift_ema']:.6f}"

        # 4. Memory coherence
        assert metrics["store_size"] <= metrics["store_capacity"], "Memory coherence violation"

        # 5. Fault tolerance validation
        error_rate = len([e for e in stream.get_recent_events() if e.kind == "processing_error"]) / max(1, total_ticks)
        assert error_rate < 0.05, f"Excessive error rate: {error_rate:.3f}"

        # 6. Performance coherence
        if metrics["tick_p95_ms"] > 0:
            assert metrics["tick_p95_ms"] < 35, f"P95 latency {metrics['tick_p95_ms']:.1f}ms exceeds target"


if __name__ == "__main__":
    # Run capability suite
    pytest.main([__file__, "-v"])
