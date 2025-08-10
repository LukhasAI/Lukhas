#!/usr/bin/env python3
"""
Test script for attention-based memory mechanisms
"""

import os
import sys
from datetime import datetime, timedelta, timezone

import numpy as np

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from memory.systems.attention_memory_layer import create_attention_orchestrator


def test_multi_head_attention():
    """Test multi-head attention on memory embeddings"""
    print("🧠 Testing Multi-Head Attention")
    print("-" * 50)

    # Create orchestrator
    orchestrator = create_attention_orchestrator(
        hidden_dim=256, num_heads=4  # Smaller for demo
    )

    # Create sample memories
    memories = []
    for i in range(10):
        memory = {
            "content": f"Memory {i}: "
            + ["Important task", "Random thought", "Key insight"][i % 3],
            "embedding": np.random.randn(256),
            "tags": ["work", "personal", "insight"][i % 3],
        }
        memories.append(memory)

    # Query
    query = "Find important work-related memories"

    # Compute relevance
    relevance_scores = orchestrator.compute_memory_relevance(
        query=query, memories=memories, mode="multi_head"
    )

    print(f"Query: '{query}'")
    print("\nTop 5 relevant memories:")
    for idx, score in relevance_scores[:5]:
        print(
            f"  Memory {idx}: {memories[idx]['content'][:50]}... (score: {score:.4f})"
        )

    # Explain attention
    attention_weights = np.array([score for _, score in relevance_scores])
    explanation = orchestrator.explain_attention(attention_weights, memories)

    print("\nAttention Analysis:")
    print(f"  Focus Score: {explanation['focus_score']:.2f}")
    print(f"  Entropy: {explanation['attention_entropy']:.2f}")
    print(
        f"  Distribution - Max: {explanation['attention_distribution']['max']:.4f}, "
        f"Min: {explanation['attention_distribution']['min']:.4f}"
    )


def test_temporal_attention():
    """Test temporal attention with time-aware retrieval"""
    print("\n\n⏰ Testing Temporal Attention")
    print("-" * 50)

    orchestrator = create_attention_orchestrator(hidden_dim=256)

    # Create memories with different timestamps
    now = datetime.now(timezone.utc)
    memories = []

    time_descriptions = [
        ("1 hour ago", timedelta(hours=1)),
        ("Yesterday", timedelta(days=1)),
        ("Last week", timedelta(weeks=1)),
        ("Last month", timedelta(days=30)),
        ("6 months ago", timedelta(days=180)),
    ]

    for i, (desc, delta) in enumerate(time_descriptions):
        memory = {
            "content": f"Event from {desc}: Meeting about project X",
            "embedding": np.random.randn(256),
            "timestamp": now - delta,
            "tags": ["meeting", "project"],
        }
        memories.append(memory)

    # Recent query
    query = "Recent project meetings"
    context = {"query_time": now}

    relevance_scores = orchestrator.compute_memory_relevance(
        query=query, memories=memories, mode="temporal", context=context
    )

    print(f"Query: '{query}' (current time)")
    print("\nTemporal relevance ranking:")
    for idx, score in relevance_scores:
        time_ago = (now - memories[idx]["timestamp"]).total_seconds() / 3600
        print(
            f"  {memories[idx]['content'][:40]}... "
            f"({time_ago:.1f} hours ago, score: {score:.4f})"
        )


def test_hierarchical_attention():
    """Test hierarchical attention for multi-scale processing"""
    print("\n\n🏗️ Testing Hierarchical Attention")
    print("-" * 50)

    orchestrator = create_attention_orchestrator(hidden_dim=256)

    # Create many memories to demonstrate hierarchical processing
    memories = []
    categories = ["Planning", "Execution", "Review", "Learning"]

    for i in range(20):
        category = categories[i % len(categories)]
        memory = {
            "content": f"{category} Phase {i//4 + 1}: Task detail {i}",
            "embedding": np.random.randn(256),
            "tags": [category.lower()],
            "level": "detail" if i % 2 == 0 else "summary",
        }
        memories.append(memory)

    query = "Overall project progress"

    relevance_scores = orchestrator.compute_memory_relevance(
        query=query, memories=memories, mode="hierarchical"
    )

    print(f"Query: '{query}'")
    print("\nHierarchical attention results:")
    print("Top memories across different scales:")
    for idx, score in relevance_scores[:8]:
        level = memories[idx]["level"]
        print(f"  [{level:7s}] {memories[idx]['content'][:40]}... (score: {score:.4f})")


def test_cross_modal_attention():
    """Test cross-modal attention between different modalities"""
    print("\n\n🎭 Testing Cross-Modal Attention")
    print("-" * 50)

    orchestrator = create_attention_orchestrator(hidden_dim=256)

    # Create multi-modal memories
    memories = []
    modalities = ["text", "image", "audio", "text+image", "text+audio"]

    for i in range(10):
        modality = modalities[i % len(modalities)]
        memory = {
            "content": f"Memory {i}: {modality} content",
            "embedding": np.random.randn(256),
            "modality": modality,
            "tags": [modality],
        }
        memories.append(memory)

    # Simulate modality embeddings
    context = {
        "modalities": {
            "text": np.random.randn(256),
            "image": np.random.randn(256),
            "audio": np.random.randn(256),
        }
    }

    query = "Find visual information"

    relevance_scores = orchestrator.compute_memory_relevance(
        query=query, memories=memories, mode="cross_modal", context=context
    )

    print(f"Query: '{query}'")
    print("\nCross-modal attention results:")
    for idx, score in relevance_scores[:5]:
        print(
            f"  {memories[idx]['content']} [modality: {memories[idx]['modality']}] "
            f"(score: {score:.4f})"
        )


def run_performance_test():
    """Test attention performance with larger memory sets"""
    print("\n\n⚡ Performance Test")
    print("-" * 50)

    orchestrator = create_attention_orchestrator(hidden_dim=512, num_heads=8)

    # Create large memory set
    num_memories = 1000
    memories = []

    print(f"Creating {num_memories} memories...")
    for i in range(num_memories):
        memory = {
            "content": f"Memory {i}",
            "embedding": np.random.randn(512),
            "tags": [f"tag_{i % 20}"],
            "timestamp": datetime.now(timezone.utc) - timedelta(hours=i),
        }
        memories.append(memory)

    query_embedding = np.random.randn(512)

    # Test different attention modes
    import time

    modes = ["multi_head", "temporal", "hierarchical"]

    for mode in modes:
        start = time.time()

        relevance_scores = orchestrator.compute_memory_relevance(
            query=query_embedding,
            memories=memories,
            mode=mode,
            context={"query_time": datetime.now(timezone.utc)},
        )

        elapsed = (time.time() - start) * 1000

        print(f"\n{mode.title()} attention:")
        print(f"  Time: {elapsed:.2f}ms")
        print(f"  Top score: {relevance_scores[0][1]:.4f}")
        print(f"  Memories/sec: {num_memories / (elapsed/1000):.0f}")


def main():
    """Run all attention tests"""
    print("=" * 70)
    print("🧬 LUKHAS AI - ATTENTION MEMORY LAYER TEST SUITE")
    print("=" * 70)

    test_multi_head_attention()
    test_temporal_attention()
    test_hierarchical_attention()
    test_cross_modal_attention()
    run_performance_test()

    print("\n✅ All attention tests completed!")


if __name__ == "__main__":
    main()
