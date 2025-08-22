"""Quantum Glyph Registry
=======================
Synchronizes symbolic glyph states across multiple LUKHAS nodes and enables
distributed dream recombination.

# ΛTAG: quantum_glyph_registry, distributed_dream
"""

from __future__ import annotations

import logging
from threading import RLock
from typing import Any

from lukhas.memory.distributed_state_manager import MultiNodeStateManager

logger = logging.getLogger(__name__)


class QIGlyphRegistry:
    """Distributed registry for glyph states."""

    def __init__(self, node_configs: list[dict[str, Any]]):
        self.cluster = MultiNodeStateManager(node_configs)
        self._lock = RLock()

    def register_glyph_state(self, glyph_id: str, state: dict[str, Any]) -> None:
        """Register or update a glyph state across the cluster."""
        key = f"glyph:{glyph_id}"
        with self._lock:
            self.cluster.set(key, state)
            logger.debug("Registered glyph", glyph=glyph_id)

    def get_glyph_state(self, glyph_id: str) -> dict[str, Any] | None:
        """Retrieve a glyph state from the cluster."""
        key = f"glyph:{glyph_id}"
        with self._lock:
            return self.cluster.get(key)

    def list_glyphs(self) -> list[str]:
        """List all glyph identifiers known to the cluster."""
        glyphs: set[str] = set()
        with self._lock:
            for node in self.cluster.nodes.values():
                for shard_id in range(node.num_shards):
                    for key in node.get_shard_keys(shard_id):
                        if key.startswith("glyph:"):
                            glyphs.add(key.split(":", 1)[1])
        return sorted(glyphs)

    def sync_cluster_states(self) -> None:
        """Replicate all glyph states across nodes."""
        with self._lock:
            for glyph_id in self.list_glyphs():
                state = self.get_glyph_state(glyph_id)
                if state is None:
                    continue
                for node in self.cluster.nodes.values():
                    node.set(f"glyph:{glyph_id}", state)

    def recombine_dreams(self, glyph_ids: list[str]) -> dict[str, Any]:
        """Combine dream fragments from multiple glyphs."""
        fragments: list[str] = []
        drift_total = 0.0
        affect_total = 0.0
        for gid in glyph_ids:
            state = self.get_glyph_state(gid)
            if not state:
                continue
            fragments.append(state.get("dream_fragment", ""))
            drift_total += float(state.get("driftScore", 0.0))
            affect_total += float(state.get("affect_delta", 0.0))

        combined = " ".join(fragments)
        count = max(len(fragments), 1)
        return {
            "dream": combined,
            "driftScore": drift_total / count,
            "affect_delta": affect_total / count,
        }
