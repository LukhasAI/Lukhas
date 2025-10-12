"""
tests/test_drift.py

Unit tests for DriftScore v2 - windowed cosine similarity with EMA.
Covers thresholds, EMA smoothing, and zero-vector safety.
"""
import os

import pytest

from lukhas.core.drift import LANE_CFG, DriftMonitor, _cosine


def test_cosine_similarity():
    """Test cosine similarity function edge cases"""
    # Identical vectors
    assert _cosine([1.0, 0.0], [1.0, 0.0]) == 1.0

    # Orthogonal vectors
    cos = _cosine([1.0, 0.0], [0.0, 1.0])
    assert abs(cos - 0.0) < 1e-10

    # Zero vectors
    assert _cosine([0.0, 0.0], [1.0, 0.0]) == 0.0
    assert _cosine([1.0, 0.0], [0.0, 0.0]) == 0.0
    assert _cosine([], []) == 0.0

    # Different lengths
    assert _cosine([1.0], [1.0, 0.0]) == 0.0

    # Anti-parallel vectors
    assert _cosine([1.0, 0.0], [-1.0, 0.0]) == -1.0


def test_drift_zero_vectors():
    """Zero vectors should produce drift = 1"""
    monitor = DriftMonitor(lane="experimental")
    result = monitor.update([0.0, 0.0], [0.0, 0.0])

    assert result["drift"] == 1.0  # 1 - 0 (zero similarity)
    assert result["guardian"] == "allow"


def test_drift_identical_vectors():
    """Identical vectors should produce drift = 0"""
    monitor = DriftMonitor(lane="experimental")
    result = monitor.update([1.0, 0.0], [1.0, 0.0])

    assert result["drift"] == 0.0  # 1 - 1 (perfect similarity)
    assert result["ema"] == 0.0  # First update: alpha * 0 + (1-alpha) * 0
    assert result["guardian"] == "allow"


def test_drift_orthogonal_vectors():
    """Orthogonal vectors should produce drift ≈ 1"""
    monitor = DriftMonitor(lane="experimental")
    result = monitor.update([1.0, 0.0], [0.0, 1.0])

    assert abs(result["drift"] - 1.0) < 1e-10
    assert result["guardian"] == "allow"  # First update, EMA not high enough yet


def test_ema_smoothing():
    """Test EMA smoothing behavior"""
    monitor = DriftMonitor(lane="experimental")

    # First update with high drift
    result1 = monitor.update([1.0, 0.0], [0.0, 1.0])  # orthogonal = drift ~1
    ema1 = result1["ema"]

    # Second update with same high drift
    result2 = monitor.update([1.0, 0.0], [0.0, 1.0])
    ema2 = result2["ema"]

    # EMA should be increasing
    assert ema2 > ema1
    assert ema1 == monitor.cfg.alpha * 1.0  # first update

    # Third update with zero drift
    result3 = monitor.update([1.0, 0.0], [1.0, 0.0])  # identical = drift 0
    ema3 = result3["ema"]

    # EMA should decrease but not to zero
    assert ema3 < ema2
    assert ema3 > 0


@pytest.mark.parametrize("lane,warn_thresh,block_thresh", [
    ("experimental", 0.30, 0.50),
    ("labs", 0.20, 0.35),
    ("prod", 0.15, 0.25),
])
def test_per_lane_thresholds(lane, warn_thresh, block_thresh):
    """Test per-lane threshold behavior"""
    monitor = DriftMonitor(lane=lane)

    assert monitor.lane == lane
    assert monitor.cfg.warn_threshold == warn_thresh
    assert monitor.cfg.block_threshold == block_thresh

    # Start with low drift
    result = monitor.update([1.0, 0.0], [1.0, 0.0])
    assert result["guardian"] == "allow"

    # Force EMA to warning level
    for _ in range(50):  # Many high-drift updates
        monitor.update([1.0, 0.0], [0.0, 1.0])

    result = monitor.update([1.0, 0.0], [0.0, 1.0])

    # Should eventually hit warn or block threshold
    if result["ema"] >= block_thresh:
        assert result["guardian"] == "block"
    elif result["ema"] >= warn_thresh:
        assert result["guardian"] == "warn"
    else:
        assert result["guardian"] == "allow"


def test_windowed_raw_drift():
    """Test windowed storage of raw drift values"""
    monitor = DriftMonitor(lane="experimental")

    # Fill up window
    for i in range(monitor.cfg.window + 10):
        monitor.update([1.0], [0.0])  # Always orthogonal

    # Window should be capped
    assert len(monitor._raw) == monitor.cfg.window
    assert monitor._raw[-1] == 1.0  # Last value should be drift=1


def test_default_lane_from_env():
    """Test that DriftMonitor uses LUKHAS_LANE env var"""
    old_lane = os.environ.get("LUKHAS_LANE")

    try:
        os.environ["LUKHAS_LANE"] = "labs"
        monitor = DriftMonitor()
        assert monitor.lane == "labs"

        os.environ["LUKHAS_LANE"] = "PROD"  # Test case conversion
        monitor = DriftMonitor()
        assert monitor.lane == "prod"

    finally:
        if old_lane:
            os.environ["LUKHAS_LANE"] = old_lane
        else:
            os.environ.pop("LUKHAS_LANE", None)


def test_unknown_lane_fallback():
    """Test fallback to experimental for unknown lanes"""
    monitor = DriftMonitor(lane="unknown")
    assert monitor.lane == "unknown"
    assert monitor.cfg == LANE_CFG["experimental"]  # Falls back to experimental config


def test_result_structure():
    """Test that update returns proper result structure"""
    monitor = DriftMonitor(lane="experimental")
    result = monitor.update([1.0, 0.0], [0.9, 0.1])

    assert isinstance(result, dict)
    assert "lane" in result
    assert "drift" in result
    assert "ema" in result
    assert "guardian" in result
    assert "n" in result

    assert isinstance(result["drift"], float)
    assert isinstance(result["ema"], float)
    assert result["guardian"] in ["allow", "warn", "block"]
    assert isinstance(result["n"], int)


# Per-lane drift thresholds testing matrix
@pytest.mark.parametrize("lane,expected_warn,expected_block,drift_value,expected_guardian", [
    # Experimental lane (most permissive)
    ("experimental", 0.30, 0.50, 0.25, "allow"),
    ("experimental", 0.30, 0.50, 0.35, "warn"),
    ("experimental", 0.30, 0.50, 0.55, "block"),

    # Candidate lane (moderate)
    ("labs", 0.20, 0.35, 0.15, "allow"),
    ("labs", 0.20, 0.35, 0.25, "warn"),
    ("labs", 0.20, 0.35, 0.40, "block"),

    # Production lane (most restrictive)
    ("prod", 0.15, 0.25, 0.10, "allow"),
    ("prod", 0.15, 0.25, 0.20, "warn"),
    ("prod", 0.15, 0.25, 0.30, "block"),
])
def test_drift_thresholds_matrix(lane, expected_warn, expected_block, drift_value, expected_guardian):
    """Test per-lane drift threshold matrix with exact EMA values"""
    monitor = DriftMonitor(lane=lane)

    # Verify configuration
    assert monitor.cfg.warn_threshold == expected_warn
    assert monitor.cfg.block_threshold == expected_block

    # Force EMA to specific value by calculating required similarity
    target_ema = drift_value
    required_drift = target_ema / monitor.cfg.alpha  # Reverse EMA calculation for first update
    required_similarity = 1.0 - required_drift

    # Create vectors with specific cosine similarity
    if required_similarity >= 1.0:
        v1, v2 = [1.0, 0.0], [1.0, 0.0]  # Perfect similarity
    elif required_similarity <= -1.0:
        v1, v2 = [1.0, 0.0], [-1.0, 0.0]  # Anti-parallel
    elif abs(required_similarity) < 1e-10:
        v1, v2 = [1.0, 0.0], [0.0, 1.0]  # Orthogonal
    else:
        # Create vectors with specific angle
        import math
        angle = math.acos(max(-1.0, min(1.0, required_similarity)))
        v1 = [1.0, 0.0]
        v2 = [math.cos(angle), math.sin(angle)]

    result = monitor.update(v1, v2)

    # For first update, EMA should be alpha * drift
    expected_ema = monitor.cfg.alpha * result["drift"]

    # Test guardian decision based on EMA thresholds
    if expected_ema >= expected_block:
        assert result["guardian"] == "block"
    elif expected_ema >= expected_warn:
        assert result["guardian"] == "warn"
    else:
        assert result["guardian"] == "allow"


@pytest.mark.parametrize("lane", ["experimental", "labs", "prod"])
def test_lane_threshold_ordering(lane):
    """Test that lane thresholds maintain proper ordering: warn < block"""
    monitor = DriftMonitor(lane=lane)
    assert monitor.cfg.warn_threshold < monitor.cfg.block_threshold


@pytest.mark.parametrize("lane1,lane2", [
    ("prod", "labs"),
    ("labs", "experimental"),
    ("prod", "experimental"),
])
def test_cross_lane_threshold_ordering(lane1, lane2):
    """Test that prod < candidate < experimental for both warn and block thresholds"""
    monitor1 = DriftMonitor(lane=lane1)
    monitor2 = DriftMonitor(lane=lane2)

    # More restrictive lanes should have lower thresholds
    assert monitor1.cfg.warn_threshold <= monitor2.cfg.warn_threshold
    assert monitor1.cfg.block_threshold <= monitor2.cfg.block_threshold


def test_ema_progression_across_thresholds():
    """Test EMA progression from allow → warn → block states"""
    monitor = DriftMonitor(lane="experimental")  # Use permissive thresholds

    # Start with low drift
    result = monitor.update([1.0, 0.0], [1.0, 0.0])
    assert result["guardian"] == "allow"

    # Gradually increase drift to reach warn threshold
    for _ in range(20):
        result = monitor.update([1.0, 0.0], [0.0, 1.0])  # High drift
        if result["guardian"] == "warn":
            break

    warn_ema = result["ema"]
    assert result["guardian"] == "warn"
    assert warn_ema >= monitor.cfg.warn_threshold
    assert warn_ema < monitor.cfg.block_threshold

    # Continue to reach block threshold
    for _ in range(20):
        result = monitor.update([1.0, 0.0], [0.0, 1.0])  # High drift
        if result["guardian"] == "block":
            break

    block_ema = result["ema"]
    assert result["guardian"] == "block"
    assert block_ema >= monitor.cfg.block_threshold
    assert block_ema > warn_ema
