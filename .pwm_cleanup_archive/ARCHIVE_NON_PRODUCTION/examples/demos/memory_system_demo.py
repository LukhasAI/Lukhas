#!/usr/bin/env python3
"""
LUKHAS Memory System Demo - Showcasing All Capabilities
"""

import asyncio

from memory.core import create_hybrid_memory_fold
from memory.structural_conscience import create_structural_conscience
from memory.systems.attention_memory_layer import create_attention_orchestrator


async def memory_demo():
    print("🧬 LUKHAS MEMORY SYSTEM CAPABILITIES DEMO")
    print("=" * 60)

    # Initialize systems
    memory = create_hybrid_memory_fold()
    attention = create_attention_orchestrator()
    conscience = create_structural_conscience()

    print("\n1️⃣ MEMORY STORAGE WITH DEDUPLICATION")
    print("-" * 40)

    # Store memories
    memories = [
        {
            "content": "Learning Python async/await",
            "type": "knowledge",
            "importance": 0.8,
        },
        {
            "content": "Learning Python async/await",
            "type": "knowledge",
            "duplicate": True,
        },  # Duplicate
        {
            "content": "User thanked me for help",
            "emotion": "gratitude",
            "type": "social",
        },
        {
            "content": "System error during processing",
            "type": "error",
            "severity": "high",
        },
    ]

    for i, mem in enumerate(memories):
        tags = [f"type:{mem.get('type', 'general')}"]
        if "emotion" in mem:
            tags.append(f"emotion:{mem['emotion']}")

        mem_id = await memory.fold_in_with_embedding(
            data=mem, tags=tags, text_content=mem["content"]
        )
        print(f"  Memory {i+1}: {mem['content'][:30]}... -> ID: {mem_id[:8]}")

    stats = memory.get_enhanced_statistics()
    print(f"\n  📊 Stats: {stats['total_items']} unique memories stored")
    print(f"  💾 Deduplication saved: {stats.get('deduplication_saves', 0)} duplicates")

    print("\n2️⃣ TAG-BASED CATEGORIZATION")
    print("-" * 40)

    # Retrieve by tags
    knowledge_mems = await memory.fold_out_by_tag("type:knowledge")
    print(f"  Knowledge memories: {len(knowledge_mems)}")

    social_mems = await memory.fold_out_by_tag("type:social")
    print(f"  Social memories: {len(social_mems)}")

    print("\n3️⃣ SEMANTIC SEARCH WITH ATTENTION")
    print("-" * 40)

    query = "help and gratitude"
    results = await memory.fold_out_semantic(query, top_k=3)
    print(f"  Query: '{query}'")
    for mem, score in results:
        print(f"    • {mem.data['content'][:40]}... (relevance: {score:.3f})")

    print("\n4️⃣ MEMORY PROTECTION & TIERS")
    print("-" * 40)

    # Store protected memory
    protected_mem = {
        "content": "API_KEY=secret123",
        "tier": "security",
        "encrypted": True,
        "access": "restricted",
    }

    # Simulate encryption
    encrypted_content = f"ENCRYPTED:{protected_mem['content'][:10]}..."

    mem_id = await memory.fold_in_with_embedding(
        data={**protected_mem, "content": encrypted_content},
        tags=["tier:security", "protected", "encrypted"],
        text_content="[REDACTED]",
    )
    print(f"  🔒 Protected memory stored: {mem_id[:8]}")
    print(f"  Original: {protected_mem['content']}")
    print(f"  Stored as: {encrypted_content}")

    print("\n5️⃣ MEMORY-DREAM INTEGRATION")
    print("-" * 40)

    # Simulate dream consolidation
    daily_memories = [
        {"content": "Struggled with complex algorithm", "emotion": "frustration"},
        {"content": "Finally solved the algorithm", "emotion": "satisfaction"},
        {"content": "Learned about recursion patterns", "type": "learning"},
    ]

    # Store daily memories
    daily_ids = []
    for mem in daily_memories:
        mem_id = await memory.fold_in_with_embedding(
            data=mem, tags=["daily", "pre-dream"], text_content=mem["content"]
        )
        daily_ids.append(mem_id)

    # Create dream synthesis
    dream = {
        "type": "dream_synthesis",
        "content": "In the dream, recursion unfolded like fractal patterns, revealing the solution",
        "insight": "Recursive thinking applies to problem decomposition",
        "source_memories": daily_ids,
    }

    dream_id = await memory.fold_in_with_embedding(
        data=dream,
        tags=["dream", "insight", "consolidated"],
        text_content=dream["content"],
    )

    # Create causal link
    if daily_ids:
        await memory.add_causal_link(
            cause_id=daily_ids[0],  # Struggle
            effect_id=dream_id,  # Dream insight
            strength=0.8,
            evidence=["Dream synthesis from daily experience"],
        )

    print("  💭 Dream consolidation complete")
    print(f"  Daily memories: {len(daily_ids)}")
    print(f"  Dream insight: {dream['insight']}")

    print("\n6️⃣ CONTINUOUS LEARNING")
    print("-" * 40)

    # Update memory importance based on usage
    for mem_id in daily_ids[:2]:
        await memory.update_memory_importance(
            memory_id=mem_id,
            feedback=0.8,  # Positive feedback
            context={"reason": "Helpful for problem solving"},
        )

    # Check tag weights
    if memory.enable_continuous_learning:
        important_tags = memory.learning_engine.tag_weights
        print("  📈 Learned tag importance:")
        for tag, weight in list(important_tags.items())[:5]:
            print(f"    • {tag}: {weight:.3f}")

    print("\n7️⃣ CAUSAL REASONING CHAINS")
    print("-" * 40)

    # Trace causal chain
    chains = await memory.trace_causal_chain(
        memory_id=dream_id, direction="backward", max_depth=3
    )

    print(f"  Causal chains from dream: {len(chains)}")
    if chains:
        print("  Chain: Struggle → Dream → Insight")

    print("\n8️⃣ MEMORY BASELINE & PERFORMANCE")
    print("-" * 40)

    final_stats = memory.get_enhanced_statistics()
    print(f"  Total memories: {final_stats['total_items']}")
    print(f"  Vector embeddings: {final_stats['vector_stats']['total_vectors']}")
    print(f"  Causal links: {final_stats['causal_stats']['total_causal_links']}")

    # Performance test
    import time

    start = time.time()
    test_id = await memory.fold_in_with_embedding(
        data={"content": "Performance test"},
        tags=["test"],
        text_content="Performance test",
    )
    fold_in_time = (time.time() - start) * 1000

    start = time.time()
    results = await memory.fold_out_by_tag("test")
    fold_out_time = (time.time() - start) * 1000

    print("\n  ⚡ Performance:")
    print(f"    • Fold-in: {fold_in_time:.2f}ms")
    print(f"    • Fold-out: {fold_out_time:.2f}ms")
    print(f"    • Throughput: {1000/fold_in_time:.0f} memories/second")

    print("\n✅ DEMO COMPLETE - All Systems Operational")


if __name__ == "__main__":
    asyncio.run(memory_demo())
