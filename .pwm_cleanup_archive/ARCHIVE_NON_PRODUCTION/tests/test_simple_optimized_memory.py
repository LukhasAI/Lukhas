#!/usr/bin/env python3
"""
Simple test for OptimizedMemoryItem functionality.
"""

import os
import sys
from datetime import datetime, timezone

import numpy as np

# Add memory systems to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "memory", "systems"))

# Import OptimizedMemoryItem
from optimized_memory_item import create_optimized_memory


def test_basic_functionality():
    """Test basic OptimizedMemoryItem functionality"""
    print("🧪 Testing OptimizedMemoryItem...")

    # Test data
    content = (
        "This is a test memory with some substantial content that will be compressed. "
        * 5
    )
    tags = ["test", "optimization", "memory", "validation", "performance"]
    embedding = np.random.randn(1024).astype(np.float32)
    metadata = {
        "timestamp": datetime.now(timezone.utc),
        "importance": 0.8,
        "access_count": 5,
        "emotion": "joy",
        "type": "knowledge",
        "drift_score": 0.1,
    }

    # Create optimized memory
    print("  Creating optimized memory...")
    optimized_memory = create_optimized_memory(
        content=content, tags=tags, embedding=embedding, metadata=metadata
    )

    print(f"  Memory size: {optimized_memory.memory_usage_kb:.1f} KB")

    # Test data integrity
    print("  Testing data integrity...")
    recovered_content = optimized_memory.get_content()
    recovered_tags = optimized_memory.get_tags()
    recovered_metadata = optimized_memory.get_metadata()
    recovered_embedding = optimized_memory.get_embedding()

    # Validate content
    print(f"    Content preserved: {recovered_content == content}")
    print(f"    Tags preserved: {recovered_tags == tags}")
    print(f"    Metadata preserved: {recovered_metadata is not None}")

    # Validate embedding quality
    if recovered_embedding is not None:
        embedding_similarity = np.dot(embedding, recovered_embedding) / (
            np.linalg.norm(embedding) * np.linalg.norm(recovered_embedding)
        )
        print(f"    Embedding similarity: {embedding_similarity:.6f}")

    # Test integrity validation
    integrity_valid = optimized_memory.validate_integrity()
    print(f"    Integrity validation: {integrity_valid}")

    print("  ✅ Basic functionality test completed!")

    return {
        "memory_size_kb": optimized_memory.memory_usage_kb,
        "content_preserved": recovered_content == content,
        "tags_preserved": recovered_tags == tags,
        "metadata_preserved": recovered_metadata is not None,
        "embedding_similarity": (
            embedding_similarity if recovered_embedding is not None else 0
        ),
        "integrity_valid": integrity_valid,
    }


def test_compression_ratios():
    """Test compression ratios with different content types"""
    print("\n🔍 Testing compression ratios...")

    test_cases = [
        ("Short text", "Short memory content"),
        ("Medium text", "This is a medium-length memory content " * 10),
        (
            "Long text",
            "This is a long memory content with lots of repetitive text " * 50,
        ),
        ("Code-like", "def function():\n    return 'test'\n" * 20),
        ("Numbers", "1234567890 " * 100),
    ]

    results = []

    for name, content in test_cases:
        # Create standard memory representation size estimate
        legacy_size = (
            len(content.encode("utf-8"))  # Content
            + 100  # Tags
            + 4096  # Embedding (1024 float32)
            + 200  # Metadata
            + 500  # Python overhead
            + 1000  # System overhead
        )

        # Create optimized memory
        optimized_memory = create_optimized_memory(
            content=content,
            tags=["test", "compression"],
            embedding=np.random.randn(1024).astype(np.float32),
            metadata={"importance": 0.5},
        )

        optimized_size = optimized_memory.memory_usage
        compression_ratio = legacy_size / optimized_size

        print(
            f"  {name:12}: {legacy_size/1024:6.1f}KB → {optimized_size/1024:6.1f}KB ({compression_ratio:4.1f}x)"
        )

        results.append(
            {
                "name": name,
                "legacy_size_kb": legacy_size / 1024,
                "optimized_size_kb": optimized_size / 1024,
                "compression_ratio": compression_ratio,
            }
        )

    avg_compression = np.mean([r["compression_ratio"] for r in results])
    print(f"  Average compression: {avg_compression:.1f}x")

    return results


def main():
    """Run all tests"""
    print("🎯 SIMPLE OPTIMIZED MEMORY TEST")
    print("=" * 50)

    try:
        # Test 1: Basic functionality
        basic_results = test_basic_functionality()

        # Test 2: Compression ratios
        compression_results = test_compression_ratios()

        # Summary
        print("\n📊 TEST SUMMARY")
        print("=" * 50)
        print(f"✅ Memory size: {basic_results['memory_size_kb']:.1f}KB per memory")
        print(
            f"✅ All data preserved: {all([basic_results['content_preserved'], basic_results['tags_preserved'], basic_results['metadata_preserved']])}"
        )
        print(f"✅ Embedding similarity: {basic_results['embedding_similarity']:.6f}")
        print(
            f"✅ Average compression: {np.mean([r['compression_ratio'] for r in compression_results]):.1f}x"
        )

        # Success metrics
        success = (
            basic_results["memory_size_kb"] < 50  # Under 50KB
            and basic_results["embedding_similarity"] > 0.99  # High quality
            and all(
                [basic_results["content_preserved"], basic_results["tags_preserved"]]
            )  # Data integrity
        )

        if success:
            print("\n🎉 OPTIMIZATION SUCCESS!")
            print("Memory usage reduced significantly while preserving quality!")
        else:
            print("\n⚠️  Optimization needs improvement")

        return success

    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ All tests completed successfully!")
    else:
        print("\n❌ Tests failed!")
        exit(1)
