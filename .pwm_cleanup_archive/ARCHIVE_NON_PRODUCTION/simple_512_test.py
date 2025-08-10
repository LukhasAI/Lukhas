#!/usr/bin/env python3
"""Simple test for 512-dim optimization"""

from datetime import datetime

import numpy as np

# Import the optimized memory functions directly
exec(open("optimized_memory_item.py").read())


def test_512_dim():
    print("🧪 Testing 512-Dimensional Embedding Optimization")
    print("=" * 60)

    # Test content
    content = "This is a test memory for 512-dimensional embedding optimization."
    tags = ["test", "512-dim", "optimization"]
    metadata = {"importance": 0.8, "timestamp": datetime.now()}

    # Generate test embeddings
    embedding_1024 = np.random.randn(1024).astype(np.float32)
    embedding_512 = np.random.randn(512).astype(np.float32)

    # Create memories
    memory_1024 = create_optimized_memory(
        content=content, tags=tags, embedding=embedding_1024, metadata=metadata
    )

    memory_512 = create_optimized_memory_512(
        content=content,
        tags=tags,
        embedding=embedding_1024,  # Will be resized to 512
        metadata=metadata,
    )

    print(f"1024-dim memory: {memory_1024.memory_usage_kb:.2f} KB")
    print(f"512-dim memory:  {memory_512.memory_usage_kb:.2f} KB")

    # Calculate savings
    savings = (
        (memory_1024.memory_usage - memory_512.memory_usage)
        / memory_1024.memory_usage
        * 100
    )
    print(f"Memory savings:  {savings:.1f}%")

    # Verify data integrity
    assert memory_512.get_content() == content
    assert memory_512.get_tags() == tags
    recovered_embedding = memory_512.get_embedding()
    assert len(recovered_embedding) == 512

    print("✅ All tests passed!")
    print(f"✅ 512-dim embedding optimization provides {savings:.1f}% memory savings")

    return savings


if __name__ == "__main__":
    test_512_dim()
