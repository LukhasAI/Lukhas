from __future__ import annotations

from lukhas.memory.adaptive_memory import AdaptiveMemorySystem, MemoryType

# ΛTAG: memory_embedding_index_integration_test


def test_recall_uses_embedding_candidates() -> None:
    system = AdaptiveMemorySystem(enable_embeddings=True)
    system.store("alpha", memory_type=MemoryType.SEMANTIC, embedding=[1.0, 0.0])
    system.store("beta", memory_type=MemoryType.SEMANTIC, embedding=[0.0, 1.0])

    items, _ = system.recall_top_k(k=1, query_embedding=[1.0, 0.0])
    assert items
    assert items[0].content == "alpha"
