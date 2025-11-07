"""
tests/test_consciousness_tick.py

Unit tests for ConsciousnessTicker - tick routing with ring buffer and backpressure.
Validates tick handling, decimation, buffer management, and Prometheus metrics.
"""
from unittest.mock import Mock, patch

import pytest

from core.consciousness_ticker import ConsciousnessTicker


def test_ticker_initialization():
    """Test that ConsciousnessTicker initializes correctly"""
    ct = ConsciousnessTicker(fps=30, cap=120)

    assert ct.ticker.fps == 30
    assert ct.buffer.capacity == 120
    assert len(ct.buffer) == 0


def test_tick_handling():
    """Test that ticks are properly handled and stored in buffer"""
    ct = ConsciousnessTicker(fps=30, cap=120)

    # Simulate tick
    ct._on_tick(42)

    assert len(ct.buffer) == 1
    frames = ct.buffer.pop_all()
    assert len(frames) == 1
    assert frames[0]["id"] == 42


def test_multiple_ticks():
    """Test handling multiple consecutive ticks"""
    ct = ConsciousnessTicker(fps=30, cap=120)

    # Simulate multiple ticks
    for i in range(10):
        ct._on_tick(i)

    assert len(ct.buffer) == 10
    frames = ct.buffer.pop_all()
    assert len(frames) == 10
    assert [f["id"] for f in frames] == list(range(10))


def test_decimation_trigger():
    """Test that decimation triggers at 80% capacity"""
    ct = ConsciousnessTicker(fps=30, cap=10)  # Small capacity for easy testing

    # Fill to 80% (8 frames)
    for i in range(8):
        ct._on_tick(i)

    assert len(ct.buffer) == 8

    # Next tick should trigger decimation
    ct._on_tick(8)

    # Buffer should be decimated to half capacity (5 frames)
    # Should keep the last 5 frames (4, 5, 6, 7, 8)
    assert len(ct.buffer) == 5
    frames = ct.buffer.pop_all()
    assert [f["id"] for f in frames] == [4, 5, 6, 7, 8]


def test_decimation_logic():
    """Test the internal decimation logic"""
    ct = ConsciousnessTicker(fps=30, cap=10)

    # Fill to 8 frames (80% of 10) - no decimation yet
    for i in range(8):
        ct._on_tick(i)
    assert len(ct.buffer) == 8

    # 9th tick triggers decimation (>80%)
    ct._on_tick(8)

    # After decimation, should keep last half (5 frames)
    frames = ct.buffer.pop_all()
    assert len(frames) == 5
    # Should be the most recent frames from the original 9
    assert all(f["id"] >= 4 for f in frames)


def test_start_stop():
    """Test start and stop functionality"""
    with patch.object(ConsciousnessTicker, '__init__', return_value=None):
        ct = ConsciousnessTicker.__new__(ConsciousnessTicker)
        ct.ticker = Mock()

        # Test start
        ct.start(seconds=5)
        ct.ticker.run.assert_called_once_with(seconds=5)

        # Test stop
        ct.stop()
        assert ct.ticker.running is False


def test_prometheus_metrics_available():
    """Test Prometheus metrics when available"""
    with patch('core.consciousness_ticker.PROM', True):
        with patch('core.consciousness_ticker.TICK') as mock_tick:
            with patch('core.consciousness_ticker.TICKS_DROPPED') as mock_dropped:
                ct = ConsciousnessTicker(fps=30, cap=4)

                # Trigger normal tick
                ct._on_tick(1)
                mock_tick.labels.assert_called()
                mock_tick.labels().observe.assert_called()

                # Trigger decimation
                for i in range(2, 6):  # Will trigger decimation at 80% (3.2 ≈ 3)
                    ct._on_tick(i)

                mock_dropped.labels.assert_called()
                mock_dropped.labels().inc.assert_called()


def test_prometheus_metrics_unavailable():
    """Test graceful handling when Prometheus is unavailable"""
    with patch('core.consciousness_ticker.PROM', False):
        ct = ConsciousnessTicker(fps=30, cap=10)

        # Should not raise exceptions even without Prometheus
        # Fill to 8, then trigger decimation with 9th
        for i in range(9):
            ct._on_tick(i)

        # Basic functionality should still work
        assert len(ct.buffer) == 5  # Decimated


def test_exception_handling():
    """Test that exceptions in tick handling are properly managed"""
    with patch('core.consciousness_ticker.SUB_EXC') as mock_exc:
        ct = ConsciousnessTicker(fps=30, cap=10)

        # Mock buffer.push to raise an exception
        with patch.object(ct.buffer, 'push', side_effect=Exception("Test error")):
            with pytest.raises(Exception, match="Test error"):
                ct._on_tick(1)

            # Exception counter should be incremented
            mock_exc.labels.assert_called()
            mock_exc.labels().inc.assert_called()


def test_lane_environment_variable():
    """Test that LUKHAS_LANE environment variable is used"""
    with patch('core.consciousness_ticker.LANE', 'test_lane'):
        with patch('core.consciousness_ticker.TICK') as mock_tick:
            ct = ConsciousnessTicker(fps=30, cap=10)
            ct._on_tick(1)

            mock_tick.labels.assert_called_with(lane='test_lane')


def test_deterministic_frame_structure():
    """Test that frames have deterministic structure for tests"""
    ct = ConsciousnessTicker(fps=30, cap=10)

    ct._on_tick(123)
    frames = ct.buffer.pop_all()

    # Frame should have deterministic structure
    assert len(frames) == 1
    assert isinstance(frames[0], dict)
    assert "id" in frames[0]
    assert frames[0]["id"] == 123


def test_buffer_capacity_property():
    """Test that buffer capacity is accessible"""
    ct = ConsciousnessTicker(fps=30, cap=42)
    assert ct.buffer.capacity == 42


def test_concurrent_tick_simulation():
    """Test behavior under rapid tick simulation"""
    ct = ConsciousnessTicker(fps=30, cap=8)

    # Simulate rapid ticks
    for i in range(50):
        ct._on_tick(i)

    # Should have maintained buffer size through decimation
    assert len(ct.buffer) <= ct.buffer.capacity

    # Should contain recent frames
    frames = ct.buffer.pop_all()
    if frames:  # Buffer might be empty after multiple decimations
        assert all(f["id"] >= 42 for f in frames)  # Recent frames
