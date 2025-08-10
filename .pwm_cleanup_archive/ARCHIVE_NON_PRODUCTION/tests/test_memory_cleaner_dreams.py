#!/usr/bin/env python3
"""
Test for memory_cleaner dream sequence optimization.
Tests the dream replay sequence consolidation functionality.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from datetime import datetime


def test_dream_consolidation():
    """Test the dream sequence consolidation implementation."""

    # Import the memory cleaner
    from orchestration.monitoring.sub_agents.memory_cleaner import (
        MemoryCleaner,
    )

    # Create test instance
    cleaner = MemoryCleaner(
        parent_id="test_parent_003",
        task_data={
            "memory_issue": "fragmented_dreams",
            "severity": "medium",
            "dream_coherence_threshold": 0.7,
        },
    )

    print("\n🌙 Testing Dream Sequence Consolidation...")

    # Perform consolidation
    success = cleaner.consolidate_dream_sequences()

    # Validate result
    assert isinstance(
        success, bool
    ), "Consolidation should return boolean success status"

    # Check consolidation stats were recorded
    assert (
        cleaner.last_consolidation_stats is not None
    ), "Consolidation stats should be recorded"
    assert (
        cleaner.last_consolidation_time is not None
    ), "Consolidation time should be recorded"

    # Validate consolidation stats structure
    stats = cleaner.last_consolidation_stats
    required_fields = [
        "sequences_analyzed",
        "sequences_optimized",
        "redundant_dreams_removed",
        "coherence_improvements",
        "replay_time_saved_ms",
    ]

    for field in required_fields:
        assert field in stats, f"Missing required stat field: {field}"

    # Validate stats values
    assert stats["sequences_analyzed"] > 0, "Should analyze at least one sequence"
    assert (
        stats["sequences_optimized"] >= 0
    ), "Optimized sequences should be non-negative"
    assert (
        stats["redundant_dreams_removed"] >= 0
    ), "Redundant dreams removed should be non-negative"
    assert (
        stats["coherence_improvements"] >= 0
    ), "Coherence improvements should be non-negative"
    assert stats["replay_time_saved_ms"] >= 0, "Time saved should be non-negative"

    # Check logical consistency
    assert (
        stats["sequences_optimized"] <= stats["sequences_analyzed"]
    ), "Cannot optimize more sequences than analyzed"

    # Check that consolidation time is recent
    time_diff = (datetime.now() - cleaner.last_consolidation_time).total_seconds()
    assert time_diff < 60, "Consolidation time should be recent"

    # Calculate optimization rate
    optimization_rate = (
        (stats["sequences_optimized"] / stats["sequences_analyzed"])
        if stats["sequences_analyzed"] > 0
        else 0
    )

    print("\n✅ Dream consolidation test passed!")
    print(f"   - Success: {success}")
    print(f"   - Sequences analyzed: {stats['sequences_analyzed']}")
    print(
        f"   - Sequences optimized: {stats['sequences_optimized']} ({optimization_rate:.0%})"
    )
    print(f"   - Redundant dreams removed: {stats['redundant_dreams_removed']}")
    print(f"   - Coherence improvements: {stats['coherence_improvements']}")
    print(f"   - Replay time saved: {stats['replay_time_saved_ms']} ms")

    return {"success": success, "stats": stats, "optimization_rate": optimization_rate}


def test_full_memory_cleaning_pipeline():
    """Test the complete memory cleaning pipeline."""

    from orchestration.monitoring.sub_agents.memory_cleaner import (
        MemoryCleaner,
    )

    print("\n🔄 Testing Full Memory Cleaning Pipeline...")

    # Create cleaner instance
    cleaner = MemoryCleaner(
        parent_id="test_parent_pipeline",
        task_data={"memory_issue": "comprehensive_maintenance", "severity": "high"},
    )

    # Step 1: Analysis
    print("\n1️⃣ Running memory analysis...")
    analysis = cleaner.analyze_memory_fragmentation()
    print(f"   - Fragmentation: {analysis['fragmentation_level']:.1%}")
    print(f"   - Optimization potential: {analysis['optimization_potential']:.1%}")

    # Step 2: Cleanup
    print("\n2️⃣ Performing memory cleanup...")
    cleanup_success = cleaner.perform_cleanup()
    print(f"   - Cleanup success: {cleanup_success}")
    if cleaner.last_cleanup_stats:
        print(
            f"   - Space recovered: {cleaner.last_cleanup_stats['space_recovered_mb']:.2f} MB"
        )

    # Step 3: Dream consolidation
    print("\n3️⃣ Consolidating dream sequences...")
    dream_success = cleaner.consolidate_dream_sequences()
    print(f"   - Dream consolidation success: {dream_success}")
    if cleaner.last_consolidation_stats:
        print(
            f"   - Time saved: {cleaner.last_consolidation_stats['replay_time_saved_ms']} ms"
        )

    # Overall success
    overall_success = cleanup_success and dream_success
    print(f"\n✅ Pipeline completed! Overall success: {overall_success}")

    return {
        "analysis": analysis,
        "cleanup_success": cleanup_success,
        "dream_success": dream_success,
        "overall_success": overall_success,
    }


if __name__ == "__main__":
    try:
        # Test dream consolidation
        dream_result = test_dream_consolidation()

        # Test full pipeline
        print("\n" + "=" * 60)
        pipeline_result = test_full_memory_cleaning_pipeline()

        print("\n📋 Full test results:")
        print(
            json.dumps(
                {
                    "dream_consolidation": dream_result,
                    "pipeline": {
                        "overall_success": pipeline_result["overall_success"],
                        "fragmentation_level": pipeline_result["analysis"][
                            "fragmentation_level"
                        ],
                    },
                },
                indent=2,
            )
        )

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
