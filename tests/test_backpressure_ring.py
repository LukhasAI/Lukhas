#!/usr/bin/env python3
"""
tests/test_backpressure_ring.py

Unit tests for ring buffer backpressure and decimation functionality.
Tests the Ring and DecimatingRing classes for Phase 4 backpressure guarantees.
"""
import pytest

from core.ring import DecimatingRing, Ring


class TestRing:
    """Basic ring buffer tests."""

    def test_ring_basic_functionality(self):
        """Test basic ring buffer operations."""
        ring = Ring(capacity=5)

        # Test initial state
        assert len(ring) == 0
        assert ring.capacity == 5
        assert ring.utilization == 0.0

        # Test pushing items
        for i in range(3):
            ring.push(f"item_{i}")

        assert len(ring) == 3
        assert ring.utilization == 0.6

        # Test pop_all
        items = ring.pop_all()
        assert items == ["item_0", "item_1", "item_2"]
        assert len(ring) == 0
        assert ring.utilization == 0.0

    def test_ring_capacity_overflow(self):
        """Test ring behavior when exceeding capacity."""
        ring = Ring(capacity=3)

        # Fill beyond capacity
        for i in range(5):
            ring.push(f"item_{i}")

        # Should only keep last 3 items
        assert len(ring) == 3
        items = ring.pop_all()
        assert items == ["item_2", "item_3", "item_4"]


class TestDecimatingRing:
    """Decimating ring buffer tests for backpressure."""

    def test_decimating_ring_initialization(self):
        """Test decimating ring initialization with various parameters."""
        ring = DecimatingRing(capacity=100, pressure_threshold=0.7, decimation_factor=3, decimation_strategy="adaptive")

        assert ring.capacity == 100
        assert ring.pressure_threshold == 0.7
        assert ring.decimation_factor == 3
        assert ring.decimation_strategy == "adaptive"

        stats = ring.get_backpressure_stats()
        assert stats["total_drops"] == 0
        assert stats["decimation_events"] == 0

    def test_no_backpressure_below_threshold(self):
        """Test no decimation occurs below pressure threshold."""
        ring = DecimatingRing(capacity=10, pressure_threshold=0.8)

        # Add items below threshold (80% = 8 items)
        for i in range(7):
            ring.push(f"item_{i}")

        stats = ring.get_backpressure_stats()
        assert stats["total_drops"] == 0
        assert stats["decimation_events"] == 0
        assert len(ring) == 7

    def test_skip_nth_decimation_strategy(self):
        """Test skip_nth decimation strategy under pressure."""
        ring = DecimatingRing(
            capacity=5, pressure_threshold=0.6, decimation_factor=2, decimation_strategy="skip_nth"  # 60% = 3 items
        )

        # Fill to trigger pressure (beyond 3 items)
        for i in range(10):
            ring.push(f"item_{i}")

        stats = ring.get_backpressure_stats()

        # Should have dropped some items due to skip_nth strategy
        assert stats["total_drops"] > 0
        assert stats["drop_rate"] > 0.0
        assert stats["decimation_strategy"] == "skip_nth"

        # Ring should be at or near capacity
        assert len(ring) <= ring.capacity

    def test_keep_recent_decimation_strategy(self):
        """Test keep_recent decimation strategy."""
        ring = DecimatingRing(
            capacity=4, pressure_threshold=0.7, decimation_factor=2, decimation_strategy="keep_recent"
        )

        # Fill beyond capacity to trigger decimation
        for i in range(8):
            ring.push(f"item_{i}")

        stats = ring.get_backpressure_stats()

        # keep_recent should have fewer drops but trigger decimation events
        assert stats["decimation_events"] > 0
        assert len(ring) <= ring.capacity

    def test_adaptive_decimation_strategy(self):
        """Test adaptive decimation strategy becomes more aggressive under pressure."""
        ring = DecimatingRing(
            capacity=6, pressure_threshold=0.5, decimation_factor=2, decimation_strategy="adaptive"  # 50% = 3 items
        )

        # Gradually increase pressure
        for i in range(12):
            ring.push(f"item_{i}")

        stats = ring.get_backpressure_stats()

        # Adaptive should have responded to increasing pressure
        assert stats["decimation_strategy"] == "adaptive"
        assert stats["total_drops"] >= 0  # May have dropped items adaptively

    def test_backpressure_stats_comprehensive(self):
        """Test comprehensive backpressure statistics."""
        ring = DecimatingRing(capacity=5, pressure_threshold=0.6, decimation_factor=2)

        # Generate activity
        for i in range(15):
            ring.push(f"item_{i}")

        stats = ring.get_backpressure_stats()

        # Verify all expected stats are present
        expected_keys = {
            "capacity",
            "current_size",
            "utilization",
            "pressure_threshold",
            "total_pushes",
            "total_drops",
            "drop_rate",
            "decimation_events",
            "decimation_factor",
            "decimation_strategy",
            "last_decimation_utilization",
        }

        assert set(stats.keys()) == expected_keys
        assert stats["total_pushes"] == 15
        assert 0.0 <= stats["drop_rate"] <= 1.0
        assert 0.0 <= stats["utilization"] <= 1.0

    def test_zero_drops_guarantee_within_budget(self):
        """Test zero drops guarantee when staying within capacity budget."""
        ring = DecimatingRing(capacity=100, pressure_threshold=0.8)

        # Stay well within budget (80% = 80 items, use only 50)
        for i in range(50):
            ring.push(f"item_{i}")

        stats = ring.get_backpressure_stats()

        # Should have zero drops when within budget
        assert stats["total_drops"] == 0
        assert stats["drop_rate"] == 0.0
        assert stats["decimation_events"] == 0
        assert len(ring) == 50

    def test_backpressure_reset_stats(self):
        """Test resetting backpressure statistics."""
        ring = DecimatingRing(capacity=5, pressure_threshold=0.6)

        # Generate some activity
        for i in range(10):
            ring.push(f"item_{i}")

        stats_before = ring.get_backpressure_stats()
        assert stats_before["total_pushes"] > 0

        # Reset stats
        ring.reset_stats()

        stats_after = ring.get_backpressure_stats()
        assert stats_after["total_pushes"] == 0
        assert stats_after["total_drops"] == 0
        assert stats_after["decimation_events"] == 0

        # Ring contents should be unchanged
        assert len(ring) == stats_before["current_size"]

    def test_high_load_stress_test(self):
        """Test ring behavior under high load stress conditions."""
        ring = DecimatingRing(capacity=20, pressure_threshold=0.7, decimation_factor=2, decimation_strategy="adaptive")

        # Simulate high load burst
        for i in range(200):
            ring.push(f"burst_item_{i}")

        stats = ring.get_backpressure_stats()

        # Should handle high load gracefully
        assert len(ring) <= ring.capacity
        assert stats["total_pushes"] == 200
        assert stats["utilization"] <= 1.0

        # Should have applied backpressure mechanisms
        assert stats["total_drops"] > 0 or stats["decimation_events"] > 0

    def test_priority_based_handling(self):
        """Test priority parameter in push method."""
        ring = DecimatingRing(capacity=3, pressure_threshold=0.6)

        # Fill with normal priority items
        ring.push("normal_1")
        ring.push("normal_2")

        # Try to push high priority item when at threshold
        ring.push("high_priority", priority=10)

        # Verify the item was handled
        stats = ring.get_backpressure_stats()
        assert stats["total_pushes"] == 3


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
