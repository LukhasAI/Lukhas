#!/usr/bin/env python3
"""
Simplified Memory Fold Performance Test (No External Dependencies)
"""

import hashlib
import json
import random
import time
from collections import defaultdict


class SimplifiedMemoryFold:
    """Simplified memory fold implementation for testing."""

    def __init__(self):
        self.items = {}
        self.item_tags = defaultdict(set)
        self.tag_items = defaultdict(set)
        self.tag_registry = {}
        self.content_hashes = {}
        self.stats = {"total_items": 0, "total_tags": 0, "deduplication_saves": 0}
        self.next_id = 0

    def _hash_content(self, data):
        """Generate content hash."""
        content = (
            json.dumps(data, sort_keys=True) if isinstance(data, dict) else str(data)
        )
        return hashlib.sha256(content.encode()).hexdigest()

    def fold_in(self, data, tags):
        """Add memory with deduplication."""
        # Check for duplicate content
        content_hash = self._hash_content(data)

        if content_hash in self.content_hashes:
            # Duplicate found - just add tags
            existing_id = self.content_hashes[content_hash]
            self.stats["deduplication_saves"] += 1

            # Add new tags to existing item
            for tag in tags:
                self.item_tags[existing_id].add(tag)
                self.tag_items[tag].add(existing_id)
                if tag not in self.tag_registry:
                    self.tag_registry[tag] = {"count": 0}
                    self.stats["total_tags"] += 1
                self.tag_registry[tag]["count"] += 1

            return existing_id

        # New item
        item_id = self.next_id
        self.next_id += 1

        self.items[item_id] = data
        self.content_hashes[content_hash] = item_id
        self.stats["total_items"] += 1

        # Process tags
        for tag in tags:
            self.item_tags[item_id].add(tag)
            self.tag_items[tag].add(item_id)
            if tag not in self.tag_registry:
                self.tag_registry[tag] = {"count": 0}
                self.stats["total_tags"] += 1
            self.tag_registry[tag]["count"] += 1

        return item_id

    def fold_out(self, tag):
        """Retrieve items by tag."""
        return [self.items[item_id] for item_id in self.tag_items.get(tag, [])]


def test_performance():
    """Test memory fold performance."""
    print("🧬 SIMPLIFIED MEMORY FOLD PERFORMANCE TEST")
    print("=" * 70)

    # Test configuration
    memory_count = 10000
    duplicate_rate = 0.3  # 30% duplicates

    print("📊 Test Configuration:")
    print(f"  - Memory items: {memory_count}")
    print(f"  - Duplicate rate: {duplicate_rate * 100}%")
    print()

    # Common tags
    common_tags = [
        "system",
        "colony",
        "reasoning",
        "creativity",
        "memory",
        "oracle",
        "ethics",
        "quantum",
        "2025",
        "january",
    ]

    # Generate test data
    test_memories = []
    base_contents = []

    for i in range(memory_count):
        if random.random() < duplicate_rate and base_contents:
            # Create duplicate
            content = random.choice(base_contents)
        else:
            # Create unique content
            content = {
                "id": i,
                "data": f"Memory content {i}",
                "value": i,  # Fixed value for consistent hashing
            }
            base_contents.append(content)

        memory = {
            "data": content,
            "tags": random.sample(common_tags, random.randint(2, 5)),
        }
        test_memories.append(memory)

    # Test fold-in performance
    print("🧪 TEST 1: Fold-in Performance")
    print("-" * 50)

    fold_system = SimplifiedMemoryFold()

    start_time = time.time()
    fold_times = []

    for i, memory in enumerate(test_memories):
        op_start = time.time()
        fold_system.fold_in(memory["data"], memory["tags"])
        fold_times.append((time.time() - op_start) * 1000)

        if (i + 1) % 1000 == 0:
            avg_time = sum(fold_times[-1000:]) / 1000
            print(f"  Processed {i + 1} items - Avg: {avg_time:.3f}ms")

    total_time = time.time() - start_time
    avg_time = sum(fold_times) / len(fold_times)

    print("\n✅ Results:")
    print(f"  - Total time: {total_time:.2f}s")
    print(f"  - Average per item: {avg_time:.3f}ms")
    print(f"  - Throughput: {memory_count / total_time:.0f} items/sec")

    stats = fold_system.stats
    print("\n📊 Deduplication Stats:")
    print(f"  - Unique items stored: {stats['total_items']}")
    print(f"  - Duplicates eliminated: {stats['deduplication_saves']}")
    print(
        f"  - Storage efficiency: {(stats['deduplication_saves'] / memory_count) * 100:.1f}% saved"
    )
    print(f"  - Unique tags: {stats['total_tags']}")

    # Test fold-out performance
    print("\n🧪 TEST 2: Fold-out Performance")
    print("-" * 50)

    retrieval_times = []

    for tag in ["system", "colony", "quantum"]:
        op_start = time.time()
        results = fold_system.fold_out(tag)
        op_time = (time.time() - op_start) * 1000
        retrieval_times.append(op_time)
        print(f"  Tag '{tag}': {len(results)} items in {op_time:.3f}ms")

    avg_retrieval = sum(retrieval_times) / len(retrieval_times)
    print(f"\n✅ Average retrieval: {avg_retrieval:.3f}ms")

    # Storage comparison
    print("\n🧪 TEST 3: Storage Efficiency")
    print("-" * 50)

    # Traditional storage (all items)
    traditional_size = sum(len(json.dumps(m["data"])) for m in test_memories)

    # Memory fold storage (deduplicated)
    fold_size = sum(len(json.dumps(item)) for item in fold_system.items.values())

    print(f"  Traditional storage: {traditional_size:,} bytes")
    print(f"  Memory fold storage: {fold_size:,} bytes")
    print(f"  Compression ratio: {traditional_size / fold_size:.2f}x")
    print(f"  Space saved: {(1 - fold_size/traditional_size) * 100:.1f}%")

    # Performance verdict
    print("\n🏆 PERFORMANCE SUMMARY")
    print("=" * 70)

    if avg_time < 0.1:  # Sub-0.1ms
        print("🌟 EXCELLENT: Sub-0.1ms fold-in maintains extreme performance")
    elif avg_time < 1.0:  # Sub-1ms
        print("⭐ VERY GOOD: Sub-1ms fold-in suitable for real-time systems")
    elif avg_time < 5.0:  # Sub-5ms
        print("✅ GOOD: Performance suitable for production use")
    else:
        print("⚠️  NEEDS OPTIMIZATION: Consider performance improvements")

    print("\nKey Metrics:")
    print(f"  • Fold-in: {avg_time:.3f}ms per item")
    print(f"  • Fold-out: {avg_retrieval:.3f}ms per query")
    print(f"  • Deduplication: {stats['deduplication_saves']} items saved")
    print(f"  • Compression: {traditional_size / fold_size:.2f}x reduction")

    return avg_time < 1.0  # Success if sub-1ms


if __name__ == "__main__":
    success = test_performance()
    exit(0 if success else 1)
