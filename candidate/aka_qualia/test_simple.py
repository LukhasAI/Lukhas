#!/usr/bin/env python3

"""
Simple Test for Wave C Memory System Validation
===============================================

Minimal test to validate the C4.4 test infrastructure is working.
"""
import pytest
import streamlit as st
from memory_noop import NoopMemory

from memory import create_memory_client


def test_noop_memory_basic():
    """Basic test that NoopMemory works"""
    memory = NoopMemory()

    assert memory.driver == "noop"
    assert memory.save_calls == 0

    # Test save operation
    scene_id = memory.save(
        user_id="test_user",
        scene={"subject": "test", "object": "test"},
        glyphs=[{"key": "test:glyph", "attrs": {}}],
        policy={"gain": 1.0},
        metrics={"drift_phi": 0.9},
        cfg_version="wave_c_v1.0.0",
    )

    assert scene_id is not None
    assert scene_id.startswith("noop_")
    assert memory.save_calls == 1


def test_memory_client_factory():
    """Test that the factory function works"""
    memory = create_memory_client("noop")
    assert isinstance(memory, NoopMemory)

    with pytest.raises(ValueError, match="Unknown memory driver"):
        create_memory_client("invalid_driver")


def test_noop_memory_get_stats():
    """Test that stats work correctly"""
    memory = NoopMemory()

    # Initial stats
    stats = memory.get_stats()
    assert stats["driver"] == "noop"
    assert stats["scenes_saved"] == 0

    # After save operation
    memory.save(
        user_id="stats_test",
        scene={},
        glyphs=[],
        policy={},
        metrics={},
        cfg_version="v1",
    )

    stats = memory.get_stats()
    assert stats["scenes_saved"] == 1
    assert stats["success_rate"] == 1.0


if __name__ == "__main__":
    test_noop_memory_basic()
    test_memory_client_factory()
    test_noop_memory_get_stats()
    print("✅ All simple tests passed!")
