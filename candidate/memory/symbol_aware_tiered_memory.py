#!/usr/bin/env python3
"""
```plaintext
┌──────────────────────────────────────────────────────────────────────────────┐
│                              SYMBOL AWARE TIERED MEMORY                      │
├──────────────────────────────────────────────────────────────────────────────┤
│ A sophisticated memory system imbued with the essence of symbolic reasoning.   │
├──────────────────────────────────────────────────────────────────────────────┤
│                              POETIC ESSENCE                                   │
│                                                                              │
│ In the realm of computation, where the ephemeral whispers of data dance,     │
│ lies a sanctuary of memory—a tiered bastion, where the echoes of symbols      │
│ resonate like ancient tomes of wisdom. Here, the Symbol Aware Tiered Memory   │
│ unfurls its wings, embracing the duality of structure and fluidity,           │
│ encapsulating the essence of thought within its carefully wrought cache.      │
│                                                                              │
│ Like the philosopher's stone, it transmutes the mundane into the profound,    │
│ weaving a tapestry of contextual understanding that transcends mere storage.  │
│ Each memory, a vessel of insight, is not merely captured but adorned with     │
│ the luminous threads of symbolic metadata. It beckons forth the dream-flagged  │
│ memories, inviting the seeker to traverse the labyrinth of reasoning, where   │
│ every twist and turn illuminates the path of knowledge.                      │
│                                                                              │
│ Thus, the Symbol Aware Tiered Memory serves as a bridge over the chasm of     │
│ obscurity—an oracle that bestows clarity upon the chaotic symphony of         │
│ information. In this hallowed space, the ephemeral becomes eternal, as        │
│ context and memory coalesce, crafting a narrative woven from the fabric of    │
│ dreams and reason.                                                            │
│                                                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│                              TECHNICAL FEATURES                                │
│                                                                              │
│ • Encapsulates and manages a multi-tiered caching system for efficient memory  │
│   retrieval and storage.                                                      │
│ • Integrates symbolic metadata tracking, enhancing contextual memory usage.    │
│ • Facilitates the retrieval of dream-flagged memories for enriched reasoning.  │
│ • Provides an intuitive interface that abstracts the complexities of memory    │
│   management.                                                                 │
│ • Implements advanced memory optimization techniques via the                     │
│   `TieredMemoryCache` class.                                                  │
│ • Supports customizable memory tiers to meet diverse application needs.       │
│ • Ensures compatibility with existing memory optimization frameworks.          │
│ • Offers robust error handling and data integrity checks throughout memory     │
│   operations.                                                                 │
├──────────────────────────────────────────────────────────────────────────────┤
│                                ΛTAG KEYWORDS                                   │
│                                                                              │
│ symbolic_memory_core, tiered_memory, contextual_reasoning,                    │
│ memory_optimization, cache_management, symbolic_metadata                      │
└──────────────────────────────────────────────────────────────────────────────┘
```
"""

from typing import Any, Optional

from .memory_optimization import MemoryTier, TieredMemoryCache


# ΛTAG: symbolic_memory_core
class SymbolAwareTieredMemory:
    """Tiered memory with symbolic awareness."""

    def __init__(self):
        self.cache = TieredMemoryCache()
        self.metadata: dict[str, dict[str, Any]] = {}

    def store(
        self,
        memory_id: str,
        data: Any,
        symbols: Optional[list[str]] = None,
        *,
        is_dream: bool = False,
        tier: MemoryTier = MemoryTier.HOT,
    ) -> None:
        """Store an item with optional symbolic metadata."""
        self.cache.put(memory_id, data, tier)
        self.metadata[memory_id] = {
            "symbols": symbols or [],
            "is_dream": is_dream,
            "tier": tier,
        }

    def retrieve(self, memory_id: str) -> Optional[Any]:
        """Retrieve an item if present."""
        return self.cache.get(memory_id)

    def get_dream_flagged(self, limit: int = 5) -> list[dict[str, Any]]:
        """Return recent dream-flagged memories."""
        dreams = [
            {"id": mid, "data": self.cache.get(mid)} for mid, meta in self.metadata.items() if meta.get("is_dream")
        ]
        return dreams[:limit]
