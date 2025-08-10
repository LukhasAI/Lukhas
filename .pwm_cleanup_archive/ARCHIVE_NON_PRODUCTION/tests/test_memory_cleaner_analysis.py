#!/usr/bin/env python3
"""
Test for memory_cleaner analysis implementation.
Tests the memory fragmentation analysis functionality.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json


def test_memory_analysis():
    """Test the memory analysis implementation."""

    # Import the memory cleaner
    from orchestration.monitoring.sub_agents.memory_cleaner import (
        MemoryCleaner,
    )

    # Create test instance
    cleaner = MemoryCleaner(
        parent_id="test_parent_001",
        task_data={"memory_issue": "high_fragmentation", "severity": "medium"},
    )

    # Run analysis
    result = cleaner.analyze_memory_fragmentation()

    # Validate result structure
    assert isinstance(result, dict), "Result should be a dictionary"

    # Check required fields
    required_fields = [
        "fragmentation_level",
        "corrupted_segments",
        "redundant_memories",
        "optimization_potential",
        "memory_stats",
        "segment_stats",
    ]

    for field in required_fields:
        assert field in result, f"Missing required field: {field}"

    # Validate data types
    assert isinstance(
        result["fragmentation_level"], float
    ), "fragmentation_level should be float"
    assert isinstance(
        result["corrupted_segments"], list
    ), "corrupted_segments should be list"
    assert isinstance(
        result["redundant_memories"], list
    ), "redundant_memories should be list"
    assert isinstance(
        result["optimization_potential"], float
    ), "optimization_potential should be float"
    assert isinstance(result["memory_stats"], dict), "memory_stats should be dict"
    assert isinstance(result["segment_stats"], dict), "segment_stats should be dict"

    # Validate ranges
    assert (
        0 <= result["fragmentation_level"] <= 1
    ), "fragmentation_level should be between 0 and 1"
    assert (
        0 <= result["optimization_potential"] <= 1
    ), "optimization_potential should be between 0 and 1"

    # Validate memory stats
    mem_stats = result["memory_stats"]
    assert mem_stats["total_mb"] > 0, "Total memory should be positive"
    assert mem_stats["used_mb"] >= 0, "Used memory should be non-negative"
    assert mem_stats["available_mb"] >= 0, "Available memory should be non-negative"
    assert (
        0 <= mem_stats["percent_used"] <= 100
    ), "Percent used should be between 0 and 100"

    # Validate segment stats
    seg_stats = result["segment_stats"]
    assert seg_stats["total_segments"] > 0, "Total segments should be positive"
    assert seg_stats["corrupted_count"] >= 0, "Corrupted count should be non-negative"
    assert seg_stats["redundant_count"] >= 0, "Redundant count should be non-negative"
    assert seg_stats["healthy_count"] >= 0, "Healthy count should be non-negative"

    # Validate segment count consistency
    total = (
        seg_stats["corrupted_count"]
        + seg_stats["redundant_count"]
        + seg_stats["healthy_count"]
    )
    assert total == seg_stats["total_segments"], "Segment counts should sum to total"

    print("✅ Memory analysis test passed!")
    print(f"   - Fragmentation level: {result['fragmentation_level']:.1%}")
    print(f"   - Optimization potential: {result['optimization_potential']:.1%}")
    print(f"   - Corrupted segments: {seg_stats['corrupted_count']}")
    print(f"   - Redundant memories: {seg_stats['redundant_count']}")
    print(f"   - Memory usage: {mem_stats['percent_used']:.1f}%")

    return result


if __name__ == "__main__":
    try:
        result = test_memory_analysis()
        print("\nFull analysis result:")
        print(json.dumps(result, indent=2, default=str))
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
