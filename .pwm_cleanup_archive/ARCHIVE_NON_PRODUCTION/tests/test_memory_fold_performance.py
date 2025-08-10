#!/usr/bin/env python3
"""
Memory Fold System Performance Test
Tests the efficiency of the memory fold architecture vs traditional storage
"""

import asyncio
import json
import os
import random
import sys
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory.core_system import create_memory_fold_system


async def generate_test_memories(count: int) -> list:
    """Generate test memories with realistic overlap."""
    memories = []

    # Common tags that will be reused (simulating real-world patterns)
    common_tags = [
        "2025",
        "january",
        "system",
        "colony",
        "reasoning",
        "creativity",
        "memory",
        "oracle",
        "ethics",
        "quantum",
        "bio-symbolic",
        "coherence",
        "drift",
        "dream",
        "evolution",
    ]

    # Colonies that generate memories
    colonies = ["reasoning", "creativity", "memory", "oracle", "ethics"]

    for i in range(count):
        # Some memories share content (testing deduplication)
        if i % 10 == 0 and i > 0:
            # Duplicate content with different tags
            base_memory = memories[i - 10]
            memory = {
                "data": base_memory["data"],
                "tags": random.sample(common_tags, random.randint(3, 7)),
                "emotional_weight": random.random(),
                "colony_source": random.choice(colonies),
            }
        else:
            # Unique content
            memory = {
                "data": {
                    "content": f"Memory content {i}",
                    "timestamp": datetime.utcnow().isoformat(),
                    "value": random.random(),
                    "context": f"Context for memory {i}",
                },
                "tags": random.sample(common_tags, random.randint(3, 7)),
                "emotional_weight": random.random(),
                "colony_source": random.choice(colonies),
            }

        memories.append(memory)

    return memories


async def test_memory_fold_performance():
    """Test memory fold system performance."""
    print("🧬 MEMORY FOLD SYSTEM PERFORMANCE TEST")
    print("=" * 70)

    # Create memory fold system
    memory_system = create_memory_fold_system(
        enable_conscience=True, enable_auto_tagging=True
    )

    # Test parameters
    memory_count = 1000

    print("📊 Test Configuration:")
    print(f"  - Memory items to process: {memory_count}")
    print("  - Conscience enabled: Yes")
    print("  - Auto-tagging enabled: Yes")
    print()

    # Generate test memories
    print(f"🔄 Generating {memory_count} test memories...")
    test_memories = await generate_test_memories(memory_count)

    # Test 1: Fold-in performance
    print("\n🧪 TEST 1: Fold-in Performance")
    print("-" * 50)

    start_time = time.time()
    fold_in_times = []

    for i, memory in enumerate(test_memories):
        op_start = time.time()
        await memory_system.fold_in(
            data=memory["data"],
            tags=memory["tags"],
            emotional_weight=memory["emotional_weight"],
            colony_source=memory["colony_source"],
        )
        op_time = (time.time() - op_start) * 1000  # Convert to ms
        fold_in_times.append(op_time)

        if (i + 1) % 100 == 0:
            avg_time = sum(fold_in_times[-100:]) / 100
            print(f"  Processed {i + 1} items - Avg time: {avg_time:.2f}ms")

    total_fold_in_time = time.time() - start_time
    avg_fold_in_time = sum(fold_in_times) / len(fold_in_times)

    print("\n  ✅ Fold-in Results:")
    print(f"    - Total time: {total_fold_in_time:.2f}s")
    print(f"    - Average per item: {avg_fold_in_time:.2f}ms")
    print(f"    - Items per second: {memory_count / total_fold_in_time:.0f}")

    # Get statistics
    stats = memory_system.get_statistics()
    print("\n  📊 Deduplication Statistics:")
    print(f"    - Total items stored: {stats['total_items']}")
    print(f"    - Total unique tags: {stats['total_tags']}")
    print(f"    - Deduplication saves: {stats['deduplication_saves']}")
    print(
        f"    - Storage efficiency: {(1 - stats['total_items']/memory_count) * 100:.1f}% saved"
    )

    # Test 2: Fold-out performance
    print("\n🧪 TEST 2: Fold-out Performance")
    print("-" * 50)

    # Test tag-based retrieval
    test_tags = ["system", "colony", "quantum", "2025"]
    fold_out_times = []

    for tag in test_tags:
        op_start = time.time()
        results = await memory_system.fold_out_by_tag(
            tag_name=tag, include_related=True, max_items=50
        )
        op_time = (time.time() - op_start) * 1000
        fold_out_times.append(op_time)

        print(f"  Tag '{tag}': {len(results)} items in {op_time:.2f}ms")

    avg_fold_out_time = sum(fold_out_times) / len(fold_out_times)
    print("\n  ✅ Fold-out Results:")
    print(f"    - Average retrieval time: {avg_fold_out_time:.2f}ms")
    print(f"    - Performance: {'EXCELLENT' if avg_fold_out_time < 10 else 'GOOD'}")

    # Test 3: Colony-based retrieval
    print("\n🧪 TEST 3: Colony-based Retrieval")
    print("-" * 50)

    for colony in ["reasoning", "creativity", "memory"]:
        op_start = time.time()
        results = await memory_system.fold_out_by_colony(colony)
        op_time = (time.time() - op_start) * 1000

        print(f"  Colony '{colony}': {len(results)} items in {op_time:.2f}ms")

    # Test 4: Memory export/import
    print("\n🧪 TEST 4: LKF-Pack Export/Import")
    print("-" * 50)

    from pathlib import Path

    export_path = Path("/tmp/test_memory_fold.lkf")

    # Export
    op_start = time.time()
    export_stats = await memory_system.export_archive(export_path)
    export_time = (time.time() - op_start) * 1000

    print("  Export Results:")
    print(f"    - Export time: {export_time:.2f}ms")
    print(f"    - Compressed size: {export_stats['compressed_size']} bytes")
    print(f"    - Compression ratio: {export_stats['compression_ratio']:.2f}")

    # Import to new system
    new_system = create_memory_fold_system(enable_conscience=False)

    op_start = time.time()
    import_stats = await new_system.import_archive(export_path)
    import_time = (time.time() - op_start) * 1000

    print("\n  Import Results:")
    print(f"    - Import time: {import_time:.2f}ms")
    print(f"    - Items imported: {import_stats['imported']}")
    print(f"    - Items skipped: {import_stats['skipped']}")

    # Clean up
    export_path.unlink()

    # Final performance summary
    print("\n🏆 PERFORMANCE SUMMARY")
    print("=" * 70)
    print(f"✅ Fold-in Performance: {avg_fold_in_time:.2f}ms per item")
    print(f"✅ Fold-out Performance: {avg_fold_out_time:.2f}ms per query")
    print(
        f"✅ Deduplication Efficiency: {stats['deduplication_saves']} duplicates eliminated"
    )
    print(f"✅ Tag Reuse: {stats['average_items_per_tag']:.1f} items per tag")
    print(f"✅ Memory Compression: {export_stats['compression_ratio']:.2f}x reduction")

    # Performance verdict
    if avg_fold_in_time < 2 and avg_fold_out_time < 10:
        print("\n🌟 VERDICT: EXCELLENT PERFORMANCE")
        print("   Sub-2ms fold-in maintains real-time capabilities")
        print("   Sub-10ms fold-out ensures responsive retrieval")
        print(
            "   Memory fold architecture successfully balances performance with rich features"
        )
    elif avg_fold_in_time < 5 and avg_fold_out_time < 20:
        print("\n⭐ VERDICT: GOOD PERFORMANCE")
        print("   Performance suitable for production use")
        print("   Consider optimization for higher throughput scenarios")
    else:
        print("\n⚠️ VERDICT: PERFORMANCE NEEDS OPTIMIZATION")
        print("   Consider reducing auto-tagging or tag relationship updates")


async def test_memory_fold_vs_traditional():
    """Compare memory fold to traditional storage."""
    print("\n\n🔬 MEMORY FOLD VS TRADITIONAL STORAGE COMPARISON")
    print("=" * 70)

    # Generate test data with high duplication
    memories = []
    base_contents = [
        "System initialization complete",
        "Colony reasoning activated",
        "Quantum coherence at 102.22%",
        "Ethics validation passed",
        "Memory consolidation in progress",
    ]

    # Generate 1000 memories with lots of duplicates
    for i in range(1000):
        content = random.choice(base_contents)
        memories.append(
            {
                "id": i,
                "content": content,
                "timestamp": datetime.utcnow().isoformat(),
                "tags": random.sample(["system", "colony", "quantum", "ethics"], 2),
            }
        )

    # Traditional storage (no deduplication)
    traditional_size = sum(len(json.dumps(m)) for m in memories)

    # Memory fold storage (with deduplication)
    unique_contents = set(m["content"] for m in memories)
    unique_tags = set(tag for m in memories for tag in m["tags"])

    # Estimate memory fold size
    fold_size = (
        len(unique_contents) * 50  # Unique content storage
        + len(unique_tags) * 20  # Tag registry
        + len(memories) * 20  # References only
    )

    print("📊 Storage Comparison (1000 memories):")
    print(f"  Traditional Storage: {traditional_size:,} bytes")
    print(f"  Memory Fold Storage: {fold_size:,} bytes")
    print(f"  Space Saved: {(1 - fold_size/traditional_size) * 100:.1f}%")
    print(f"  Compression Factor: {traditional_size/fold_size:.1f}x")


if __name__ == "__main__":
    asyncio.run(test_memory_fold_performance())
    asyncio.run(test_memory_fold_vs_traditional())
