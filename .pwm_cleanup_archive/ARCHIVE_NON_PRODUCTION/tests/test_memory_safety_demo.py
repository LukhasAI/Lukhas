#!/usr/bin/env python3
"""
Test Memory Safety Features - Demonstration Script
"""

import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta, timezone

from memory.core import create_hybrid_memory_fold
from memory.systems.memory_safety_features import (
    MemorySafetySystem,
    SafeMemoryFold,
)


async def demonstrate_safety_features():
    """Demonstrate memory safety features"""

    # Create base memory system
    base_memory = create_hybrid_memory_fold()

    # Create safety system
    safety = MemorySafetySystem()

    # Add reality anchors
    safety.add_reality_anchor("LUKHAS", "LUKHAS is an AGI system")
    safety.add_reality_anchor("2025", "Current year is 2025")

    # Create safe memory wrapper
    safe_memory = SafeMemoryFold(base_memory, safety)

    print("🛡️ MEMORY SAFETY DEMONSTRATION")
    print("=" * 60)

    # Test 1: Valid memory
    print("\n1. Storing valid memory...")
    valid_memory = {
        "content": "LUKHAS is learning about memory safety",
        "type": "knowledge",
        "timestamp": datetime.now(timezone.utc),
    }

    mem_id = await safe_memory.safe_fold_in(valid_memory, ["safety", "valid"])
    print(f"✅ Valid memory stored: {mem_id}")

    # Test 2: Hallucination attempt
    print("\n2. Attempting to store hallucinated memory...")
    hallucination = {
        "content": "LUKHAS is not an AGI system",  # Contradicts reality anchor
        "type": "false_claim",
        "timestamp": datetime.now(timezone.utc),
    }

    mem_id = await safe_memory.safe_fold_in(hallucination, ["false"])
    if mem_id is None:
        print("❌ Hallucination prevented!")

    # Test 3: Future memory attempt
    print("\n3. Attempting to store future memory...")
    future_memory = {
        "content": "Event from tomorrow",
        "timestamp": datetime.now(timezone.utc) + timedelta(days=1),
    }

    mem_id = await safe_memory.safe_fold_in(future_memory, ["future"])
    if mem_id is None:
        print("❌ Future memory prevented!")

    # Test 4: Drift tracking
    print("\n4. Tracking drift over multiple uses...")
    import numpy as np

    for i in range(5):
        test_memory = {
            "content": f"Test memory {i}",
            "type": "test",
            "timestamp": datetime.now(timezone.utc),
        }

        # Create slightly different embeddings to simulate drift
        embedding = np.random.randn(1024).astype(np.float32)
        embedding += i * 0.1  # Add drift

        mem_id = await base_memory.fold_in_with_embedding(
            data=test_memory, tags=["drifting"], embedding=embedding
        )

        # Track drift
        drift_score = safety.track_drift(
            tag="drifting", embedding=embedding, usage_context={"iteration": i}
        )
        print(f"  Memory {i}: drift score = {drift_score:.3f}")

    # Test 5: Consensus validation
    print("\n5. Testing consensus validation...")

    # Store multiple similar memories
    consensus_memories = []
    for i in range(5):
        mem = {
            "content": f"The sky is blue - observation {i}",
            "type": "observation",
            "emotion": "neutral",
            "timestamp": datetime.now(timezone.utc),
        }
        mem_id = await safe_memory.safe_fold_in(mem, ["observation", "sky"])
        consensus_memories.append(mem_id)

    # Try to add contradicting memory
    contradiction = {
        "content": "The sky is green",
        "type": "observation",
        "emotion": "joy",  # Wrong emotion for this observation
        "timestamp": datetime.now(timezone.utc),
    }

    # This should be caught by consensus validation when retrieved
    bad_id = await base_memory.fold_in_with_embedding(
        data={
            **contradiction,
            "_collapse_hash": safety.compute_collapse_hash(contradiction),
        },
        tags=["observation", "sky"],
        text_content=contradiction["content"],
    )

    # Retrieve with consensus validation
    results = await safe_memory.safe_fold_out(
        query="sky color", verify=True, check_consensus=True
    )

    print(f"  Retrieved {len(results)} validated memories")
    for mem, score in results[:3]:
        print(f"    • {mem.data['content'][:40]}... (confidence: {score:.3f})")

    # Get safety report
    print("\n6. Safety Report:")
    report = safety.get_safety_report()
    print(f"  Monitored tags: {report['drift_analysis']['monitored_tags']}")
    print(f"  Average drift: {report['drift_analysis']['average_drift']:.3f}")
    print(f"  Verified memories: {report['verifold_status']['total_verified']}")
    print(
        f"  Contradictions caught: {report['hallucination_prevention']['contradictions_caught']}"
    )
    print(f"  Reality anchors: {report['hallucination_prevention']['reality_anchors']}")

    print("\n✅ Safety demonstration complete!")

    # Show how modules benefit
    print("\n🎯 MODULE INTEGRATION BENEFITS:")
    print("=" * 60)

    print("\n📚 LEARNING MODULE:")
    print("  • Safe memories provide reliable training data")
    print("  • Drift detection prevents catastrophic forgetting")
    print("  • Verified memories improve model accuracy")

    print("\n🎨 CREATIVITY MODULE:")
    print("  • Hallucination prevention ensures creative outputs are grounded")
    print("  • Reality anchors provide constraints for safe exploration")
    print("  • Consensus validation filters out inconsistent creative attempts")

    print("\n🗣️ VOICE MODULE:")
    print("  • Voice memories are tagged and verified like all others")
    print("  • Speaker-specific drift tracking adapts to voice changes")
    print("  • Emotional consistency validation improves voice synthesis")

    print("\n🧠 META MODULE:")
    print("  • Collapse hashes enable efficient meta-pattern detection")
    print("  • Drift scores reveal concept evolution over time")
    print("  • Causal chains support meta-reasoning about knowledge")


if __name__ == "__main__":
    asyncio.run(demonstrate_safety_features())
