"""
tests/test_folds.py

Unit tests for FoldGuard circuit breaker - memory cascade prevention.
Validates fanout limits, depth overflow, budget overflow, and metrics.
"""
from lukhas.memory.folds import FoldGuard


def test_fanout_permit_then_deny():
    """Test that FoldGuard permits up to max_fanout, then denies"""
    guard = FoldGuard(max_fanout=3, max_depth=10, window_budget=100)
    guard.start_tick()

    # Should permit within limits
    assert guard.allow(fanout=1, depth=1) is True
    assert guard.allow(fanout=2, depth=1) is True  # Total fanout now 3
    assert guard.window == 3

    # Should deny when exceeding max_fanout
    assert guard.allow(fanout=1, depth=1) is False  # Would make total 4
    assert guard.tripped is True


def test_depth_overflow_triggers_trip():
    """Test that depth overflow triggers circuit trip"""
    guard = FoldGuard(max_fanout=10, max_depth=2, window_budget=100)
    guard.start_tick()

    # Should permit within depth limit
    assert guard.allow(fanout=1, depth=1) is True
    assert guard.allow(fanout=1, depth=2) is True
    assert guard.depth == 2

    # Should deny when exceeding max_depth
    assert guard.allow(fanout=1, depth=3) is False
    assert guard.tripped is True


def test_budget_overflow_triggers_trip():
    """Test that budget overflow triggers trip and increments metric"""
    guard = FoldGuard(max_fanout=10, max_depth=10, window_budget=5)
    guard.start_tick()

    # Should permit within budget
    assert guard.allow(fanout=1, depth=1, cost=2) is True
    assert guard.allow(fanout=1, depth=1, cost=3) is True  # Total cost now 5
    assert guard.ops == 5

    # Should deny when exceeding budget
    assert guard.allow(fanout=1, depth=1, cost=1) is False  # Would make total 6
    assert guard.tripped is True


def test_start_tick_resets_safely():
    """Test that start_tick() resets all counters safely"""
    guard = FoldGuard(max_fanout=3, max_depth=2, window_budget=10)
    guard.start_tick()

    # Fill up the guard
    guard.allow(fanout=3, depth=2, cost=10)
    assert guard.window == 3
    assert guard.depth == 2
    assert guard.ops == 10

    # Trip the guard
    guard.allow(fanout=1, depth=1, cost=1)
    assert guard.tripped is True

    # Reset should clear everything
    guard.start_tick()
    assert guard.window == 0
    assert guard.depth == 0
    assert guard.ops == 0
    assert guard.tripped is False

    # Should work again after reset
    assert guard.allow(fanout=1, depth=1, cost=1) is True


def test_tripped_state_blocks_all():
    """Test that once tripped, all subsequent operations are blocked"""
    guard = FoldGuard(max_fanout=2, max_depth=10, window_budget=100)
    guard.start_tick()

    # Trip the guard with fanout
    guard.allow(fanout=2, depth=1)
    assert guard.allow(fanout=1, depth=1) is False  # This trips it
    assert guard.tripped is True

    # All subsequent operations should be blocked
    assert guard.allow(fanout=0, depth=0, cost=0) is False
    assert guard.allow(fanout=1, depth=1, cost=1) is False


def test_cumulative_tracking():
    """Test that fanout and cost accumulate, depth takes max"""
    guard = FoldGuard(max_fanout=10, max_depth=5, window_budget=20)
    guard.start_tick()

    # Multiple operations should accumulate
    guard.allow(fanout=2, depth=3, cost=4)
    guard.allow(fanout=3, depth=1, cost=5)  # depth should stay at 3 (max)
    guard.allow(fanout=1, depth=4, cost=2)  # depth should become 4

    assert guard.window == 6  # 2 + 3 + 1
    assert guard.depth == 4   # max(3, 1, 4)
    assert guard.ops == 11    # 4 + 5 + 2


def test_default_cost():
    """Test that default cost is 1 when not specified"""
    guard = FoldGuard(max_fanout=10, max_depth=10, window_budget=3)
    guard.start_tick()

    # Default cost should be 1
    guard.allow(fanout=1, depth=1)  # cost=1 by default
    guard.allow(fanout=1, depth=1)  # cost=1 by default
    guard.allow(fanout=1, depth=1)  # cost=1 by default, total=3

    assert guard.ops == 3

    # Next operation should trip the budget
    assert guard.allow(fanout=1, depth=1) is False


def test_zero_limits():
    """Test edge case with zero limits"""
    guard = FoldGuard(max_fanout=0, max_depth=0, window_budget=0)
    guard.start_tick()

    # Zero operations should be allowed with zero limits
    assert guard.allow(fanout=0, depth=0, cost=0) is True
    assert guard.tripped is False

    # Any non-zero operation should trip
    guard.start_tick()  # Reset
    assert guard.allow(fanout=1, depth=0, cost=0) is False
    assert guard.tripped is True

    guard.start_tick()  # Reset
    assert guard.allow(fanout=0, depth=1, cost=0) is False
    assert guard.tripped is True

    guard.start_tick()  # Reset
    assert guard.allow(fanout=0, depth=0, cost=1) is False
    assert guard.tripped is True


def test_properties_reflect_state():
    """Test that properties correctly reflect internal state"""
    guard = FoldGuard(max_fanout=10, max_depth=10, window_budget=10)
    guard.start_tick()

    # Initially zero
    assert guard.window == 0
    assert guard.depth == 0
    assert guard.ops == 0

    # After operations
    guard.allow(fanout=3, depth=5, cost=7)
    assert guard.window == 3
    assert guard.depth == 5
    assert guard.ops == 7


def test_prometheus_metric_increment():
    """Test that metrics are incremented when circuit trips (if available)"""
    # Note: This test verifies the metric increment logic
    # The actual Prometheus client may or may not be available
    guard = FoldGuard(max_fanout=1, max_depth=10, window_budget=10)
    guard.start_tick()

    # Fill up fanout limit
    guard.allow(fanout=1, depth=1)

    # This should trip and increment the metric
    # We can't directly test the Prometheus metric without mocking,
    # but we can verify the trip behavior
    result = guard.allow(fanout=1, depth=1)
    assert result is False
    assert guard.tripped is True
