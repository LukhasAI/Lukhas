#!/usr/bin/env python3
"""
Test for memory_cleaner cleanup implementation.
Tests the memory cleanup and optimization functionality.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from datetime import datetime


def test_memory_cleanup():
    """Test the memory cleanup implementation."""

    # Import the memory cleaner
    from orchestration.monitoring.sub_agents.memory_cleaner import (
        MemoryCleaner,
    )

    # Create test instance
    cleaner = MemoryCleaner(
        parent_id="test_parent_002",
        task_data={
            "memory_issue": "high_fragmentation",
            "severity": "high",
            "requested_action": "cleanup",
        },
    )

    # First run analysis to see the state before cleanup
    analysis_before = cleaner.analyze_memory_fragmentation()
    print("\n📊 Memory State Before Cleanup:")
    print(f"   - Fragmentation: {analysis_before['fragmentation_level']:.1%}")
    print(f"   - Corrupted segments: {len(analysis_before['corrupted_segments'])}")
    print(f"   - Redundant memories: {len(analysis_before['redundant_memories'])}")
    print(
        f"   - Optimization potential: {analysis_before['optimization_potential']:.1%}"
    )

    # Perform cleanup
    print("\n🧹 Performing cleanup...")
    success = cleaner.perform_cleanup()

    # Validate cleanup result
    assert isinstance(success, bool), "Cleanup should return boolean success status"

    # Check cleanup stats were recorded
    assert cleaner.last_cleanup_stats is not None, "Cleanup stats should be recorded"
    assert cleaner.last_cleanup_time is not None, "Cleanup time should be recorded"

    # Validate cleanup stats structure
    stats = cleaner.last_cleanup_stats
    required_fields = [
        "segments_cleaned",
        "memories_consolidated",
        "space_recovered_mb",
        "errors_fixed",
    ]

    for field in required_fields:
        assert field in stats, f"Missing required stat field: {field}"

    # Validate stats values
    assert stats["segments_cleaned"] >= 0, "Segments cleaned should be non-negative"
    assert (
        stats["memories_consolidated"] >= 0
    ), "Memories consolidated should be non-negative"
    assert stats["space_recovered_mb"] >= 0, "Space recovered should be non-negative"
    assert stats["errors_fixed"] >= 0, "Errors fixed should be non-negative"

    # Check that cleanup time is recent
    time_diff = (datetime.now() - cleaner.last_cleanup_time).total_seconds()
    assert time_diff < 60, "Cleanup time should be recent"

    print("\n✅ Memory cleanup test passed!")
    print(f"   - Success: {success}")
    print(f"   - Segments cleaned: {stats['segments_cleaned']}")
    print(f"   - Memories consolidated: {stats['memories_consolidated']}")
    print(f"   - Space recovered: {stats['space_recovered_mb']:.2f} MB")
    print(f"   - Errors fixed: {stats['errors_fixed']}")

    # Run analysis again to see improvement
    analysis_after = cleaner.analyze_memory_fragmentation()
    print("\n📊 Memory State After Cleanup:")
    print(f"   - Fragmentation: {analysis_after['fragmentation_level']:.1%}")
    print(f"   - Corrupted segments: {len(analysis_after['corrupted_segments'])}")
    print(f"   - Redundant memories: {len(analysis_after['redundant_memories'])}")

    return {
        "before": analysis_before,
        "after": analysis_after,
        "cleanup_stats": stats,
        "success": success,
    }


if __name__ == "__main__":
    try:
        result = test_memory_cleanup()
        print("\n📋 Full cleanup results:")
        print(json.dumps(result["cleanup_stats"], indent=2))
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
