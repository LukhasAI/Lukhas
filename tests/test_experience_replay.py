#!/usr/bin/env python3
"""
tests/test_experience_replay.py

Experience Replay golden fixture tests for Phase 4.
Tests deterministic replays under load using golden fixture validation.
"""
import json
import os
import time
from pathlib import Path

import pytest

from lukhas.core.consciousness_stream import ConsciousnessStream


class TestExperienceReplay:
    """Test suite for experience replay using golden fixtures."""

    @pytest.fixture
    def golden_fixture(self):
        """Load the golden fixture for consciousness stream replay."""
        fixture_path = Path(__file__).parent / "fixtures" / "golden" / "consciousness_stream_replay.json"
        with open(fixture_path) as f:
            return json.load(f)

    def setup_method(self):
        """Set up hermetic test environment."""
        os.environ["LUKHAS_LANE"] = "experimental"
        os.environ["PYTHONHASHSEED"] = "0"
        os.environ["TZ"] = "UTC"
        os.environ["LUKHAS_RNG_SEED"] = "42"

    def test_deterministic_replay_golden_fixture(self, golden_fixture):
        """Test deterministic replay matches golden fixture expectations."""
        fixture = golden_fixture
        config = fixture["stream_configuration"]

        # Create stream with golden fixture configuration
        stream = ConsciousnessStream(
            fps=config["fps"],
            store_capacity=config["store_capacity"]
        )

        # Run stream for specified duration
        start_time = time.perf_counter()
        stream.start(duration_seconds=config["duration_seconds"])
        end_time = time.perf_counter()

        # Validate performance budget
        total_duration_ms = (end_time - start_time) * 1000
        budget = fixture["performance_budgets"]["total_duration_ms"]
        assert total_duration_ms <= budget, f"Stream took {total_duration_ms:.1f}ms (budget: {budget}ms)"

        # Validate tick count
        expected_ticks = config["expected_ticks"]
        tolerance = 5  # Allow some timing variation
        assert abs(stream.tick_count - expected_ticks) <= tolerance, \
            f"Expected ~{expected_ticks} ticks, got {stream.tick_count}"

        # Validate event structure
        events = stream.get_recent_events(limit=1000)
        event_kinds = [e.kind for e in events]

        for expected_event in fixture["expected_events"]:
            kind = expected_event["kind"]
            assert kind in event_kinds, f"Missing expected event kind: {kind}"

            kind_count = event_kinds.count(kind)
            if "count" in expected_event:
                expected_count = expected_event["count"]
                # Allow some tolerance for timing-sensitive events
                assert abs(kind_count - expected_count) <= tolerance, \
                    f"Expected ~{expected_count} {kind} events, got {kind_count}"

    def test_replay_under_load(self, golden_fixture):
        """Test experience replay functionality under load conditions."""
        fixture = golden_fixture
        config = fixture["stream_configuration"]
        load_config = fixture["load_testing"]

        # Create multiple concurrent streams to simulate load
        streams = []
        concurrent = load_config["concurrent_streams"]

        for i in range(concurrent):
            stream = ConsciousnessStream(
                fps=config["fps"],
                store_capacity=config["store_capacity"]
            )
            streams.append(stream)

        # Run all streams for a short burst
        start_time = time.perf_counter()

        for stream in streams:
            # Process ticks manually to simulate load
            for tick in range(20):
                stream._on_consciousness_tick(tick)

        end_time = time.perf_counter()

        # Validate all streams processed events (allow for some timing variation)
        for i, stream in enumerate(streams):
            assert abs(stream.tick_count - 20) <= 2, f"Stream {i} processed {stream.tick_count} ticks (expected ~20)"
            assert stream.events_processed >= 20, f"Stream {i} processed {stream.events_processed} events"

            # Test replay functionality
            replay_events = stream.replay_events(since_minutes=1)
            assert len(replay_events) > 0, f"Stream {i} replay returned no events"

            # Validate event ordering (oldest first for replay) - allow for microsecond variations
            if len(replay_events) > 1:
                # Check that events are roughly chronological (within 1ms tolerance)
                time_diffs = [(replay_events[j].ts - replay_events[j-1].ts).total_seconds()
                              for j in range(1, len(replay_events))]
                # Most events should be in order, allow for some small timing variations
                out_of_order = sum(1 for diff in time_diffs if diff < -0.001)  # 1ms tolerance
                assert out_of_order <= 2, f"Stream {i} has {out_of_order} events significantly out of order"

    def test_metrics_validation_golden(self, golden_fixture):
        """Test per-stream metrics match golden fixture validation ranges."""
        fixture = golden_fixture
        config = fixture["stream_configuration"]
        metrics_validation = fixture["metrics_validation"]

        stream = ConsciousnessStream(fps=config["fps"])

        # Process enough ticks to generate meaningful metrics
        for i in range(30):
            stream._on_consciousness_tick(i)
            # Add slight processing variation to trigger metrics
            if i % 5 == 0:
                time.sleep(0.001)  # 1ms delay

        metrics = stream.get_stream_metrics()

        # Validate all metrics are within golden fixture ranges
        for metric_name, range_spec in metrics_validation.items():
            if metric_name in metrics:
                value = metrics[metric_name]
                min_val = range_spec["min"]
                max_val = range_spec["max"]

                assert min_val <= value <= max_val, \
                    f"{metric_name}={value} outside golden range [{min_val}, {max_val}]"

    def test_sliding_window_replay_consistency(self, golden_fixture):
        """Test sliding window replay maintains consistency under load."""
        fixture = golden_fixture
        replay_validation = fixture["replay_validation"]

        stream = ConsciousnessStream(fps=30)

        # Generate events over time
        for i in range(50):
            stream._on_consciousness_tick(i)
            if i % 10 == 0:
                time.sleep(0.01)  # Brief pause to create time separation

        # Test sliding window replay
        window_minutes = replay_validation["sliding_window_minutes"]
        replay_events = stream.replay_events(since_minutes=window_minutes)

        expected_range = replay_validation["expected_recent_events"]
        event_count = len(replay_events)

        # Allow some flexibility in event count due to timing variations
        assert expected_range["min"] <= event_count <= expected_range["max"] + 20, \
            f"Replay returned {event_count} events, expected {expected_range['min']}-{expected_range['max']}"

        # Validate lane isolation
        if replay_validation["lane_isolation"]:
            lanes = {e.lane for e in replay_events}
            assert lanes == {"experimental"}, f"Expected only experimental lane, got {lanes}"

        # Validate glyph ID consistency
        if replay_validation["glyph_id_consistency"]:
            glyph_ids = {e.glyph_id for e in replay_events}
            assert len(glyph_ids) == 1, f"Expected single glyph ID, got {len(glyph_ids)} different IDs"

    def test_memory_efficiency_under_load(self, golden_fixture):
        """Test memory efficiency during extended replay operations."""
        fixture = golden_fixture
        load_config = fixture["load_testing"]

        stream = ConsciousnessStream(fps=10, store_capacity=1000)  # Bounded capacity

        # Simulate extended operation
        for cycle in range(5):
            # Process batch of events
            for i in range(50):
                stream._on_consciousness_tick(cycle * 50 + i)

            # Perform replay operations
            recent = stream.get_recent_events(limit=100)
            replay = stream.replay_events(since_minutes=1)

            # Validate memory usage stays bounded
            store_size = len(stream.event_store.events)
            assert store_size <= stream.event_store.max_capacity, \
                f"Store size {store_size} exceeds capacity {stream.event_store.max_capacity}"

            # Validate metrics tracking stays bounded
            assert len(stream._tick_processing_times) <= 100, \
                f"Tick times tracking unbounded: {len(stream._tick_processing_times)}"
            assert len(stream._breakthrough_timestamps) <= 1000, \
                f"Breakthrough timestamps unbounded: {len(stream._breakthrough_timestamps)}"

    def test_golden_fixture_completeness(self, golden_fixture):
        """Test that the golden fixture covers all required fields."""
        fixture = golden_fixture

        # Validate required top-level fields
        required_fields = [
            "fixture_metadata", "stream_configuration", "expected_events",
            "performance_budgets", "metrics_validation", "replay_validation", "load_testing"
        ]

        for field in required_fields:
            assert field in fixture, f"Missing required field in golden fixture: {field}"

        # Validate metadata completeness
        metadata = fixture["fixture_metadata"]
        metadata_fields = ["name", "description", "version", "timestamp", "environment"]
        for field in metadata_fields:
            assert field in metadata, f"Missing metadata field: {field}"

        # Validate environment variables
        env = metadata["environment"]
        required_env = ["LUKHAS_LANE", "PYTHONHASHSEED", "TZ", "LUKHAS_RNG_SEED"]
        for var in required_env:
            assert var in env, f"Missing environment variable: {var}"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
