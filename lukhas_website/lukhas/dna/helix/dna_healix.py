"""
🧬 DNA Healix - Immutable Memory Architecture for LUKHAS
======================================================

A symbolic DNA-inspired memory system that maintains immutable origin strands
while tracking drift and enabling controlled repair mechanisms.

Architecture:
- SymbolicStrand: Immutable sequences of symbolic glyphs
- DNAHealixCore: Manages origin/current state with drift detection
- SymbolicRepairLoop: Monitors and stabilizes memory integrity
- MemoryHelix: Full immutable memory system with DNA-like structure

Author: LUKHAS Cognitive AI Framework
Version: 1.0
"""

import logging
from datetime import timezone
import asyncio
import contextlib
import hashlib
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional
import numpy as np
from core.common import get_logger
            try:

logger = logging.getLogger(__name__)

                await self.step()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in repair loop: {e}")
                await asyncio.sleep(self.check_interval)

    async def step(self):
        """Single monitoring step"""
        drift = self.dna.calculate_drift()

        if self.dna.should_repair():
            logger.info(f"🛠 Drift detected: {drift:.3f}")

            if self.auto_repair:
                # Determine repair method based on drift level
                if drift > 0.7:
                    method = RepairMethod.FULL_RESET
                elif drift > 0.5:
                    method = RepairMethod.CONSENSUS
                else:
                    method = RepairMethod.PARTIAL_HEAL

                self.dna.repair(method=method, cause=f"Auto-repair at drift {drift:.3f}")
            else:
                logger.warning(f"⚠️ High drift {drift:.3f} but auto-repair disabled")
        else:
            logger.debug(f"✅ System stable (drift: {drift:.3f})")

        self.iteration += 1


class MemoryHelix:
    """
    🧬 Complete immutable memory system with DNA helix structure
    """

    def __init__(self, memory_id: str, initial_glyphs: list[str]):
        self.memory_id = memory_id
        self.origin_strand = SymbolicStrand(initial_glyphs)
        self.helix_core = DNAHealixCore(self.origin_strand)
        self.repair_loop = SymbolicRepairLoop(self.helix_core)

        # Additional strands for multi-dimensional memory
        self.emotional_strand = SymbolicStrand(initial_glyphs)  # Emotional context
        self.temporal_strand = SymbolicStrand(initial_glyphs)  # Temporal markers
        self.causal_strand = SymbolicStrand(initial_glyphs)  # Causal relationships

        # Storage for additional strands
        self.strands = {}  # For storing named strands

        # Metadata
        self.created_at = datetime.now(timezone.utc)
        self.access_count = 0
        self.last_accessed = None
        self.tags: set[str] = set()
        self.locked = False  # For GDPR compliance

    def __repr__(self) -> str:
        return f"MemoryHelix({self.memory_id}, drift={self.helix_core.calculate_drift():.3f})"

    def access(self) -> dict[str, Any]:
        """Access memory with tracking"""
        if self.locked:
            raise PermissionError(f"Memory {self.memory_id} is locked")

        self.access_count += 1
        self.last_accessed = datetime.now(timezone.utc)

        return {
            "memory_id": self.memory_id,
            "origin": list(self.origin_strand.sequence),
            "current": list(self.helix_core.current.sequence),
            "drift": self.helix_core.calculate_drift(),
            "emotional_context": list(self.emotional_strand.sequence),
            "temporal_context": list(self.temporal_strand.sequence),
            "causal_context": list(self.causal_strand.sequence),
            "metadata": {
                "created": self.created_at.isoformat(),
                "accessed": self.access_count,
                "last_access": (self.last_accessed.isoformat() if self.last_accessed else None),
                "tags": list(self.tags),
                "repairs": len(self.helix_core.repair_history),
            },
        }

    def mutate(self, new_glyphs: list[str]) -> None:
        """Update current strand (origin remains immutable)"""
        if self.locked:
            raise PermissionError(f"Memory {self.memory_id} is locked")

        self.helix_core.current = SymbolicStrand(new_glyphs)

    def add_emotional_context(self, emotional_glyphs: list[str]) -> None:
        """Add emotional context strand"""
        self.emotional_strand = SymbolicStrand(emotional_glyphs)

    def add_temporal_context(self, temporal_glyphs: list[str]) -> None:
        """Add temporal context strand"""
        self.temporal_strand = SymbolicStrand(temporal_glyphs)

    def add_causal_context(self, causal_glyphs: list[str]) -> None:
        """Add causal context strand"""
        self.causal_strand = SymbolicStrand(causal_glyphs)

    def lock(self, reason: str = "GDPR request") -> None:
        """Lock memory (for GDPR right to erasure)"""
        self.locked = True
        self.tags.add(f"locked:{reason}")
        logger.info(f"🔒 Memory {self.memory_id} locked: {reason}")

    def unlock(self) -> None:
        """Unlock memory"""
        self.locked = False
        self.tags = {t for t in self.tags if not t.startswith("locked:")}
        logger.info(f"🔓 Memory {self.memory_id} unlocked")

    def export(self) -> dict[str, Any]:
        """Export memory for persistence"""
        return {
            "memory_id": self.memory_id,
            "origin": list(self.origin_strand.sequence),
            "current": list(self.helix_core.current.sequence),
            "emotional": list(self.emotional_strand.sequence),
            "temporal": list(self.temporal_strand.sequence),
            "causal": list(self.causal_strand.sequence),
            "metadata": {
                "created": self.created_at.isoformat(),
                "accessed": self.access_count,
                "last_access": (self.last_accessed.isoformat() if self.last_accessed else None),
                "tags": list(self.tags),
                "locked": self.locked,
                "repair_history": [
                    {
                        "timestamp": r.timestamp.isoformat(),
                        "method": r.repair_method.value,
                        "drift_before": r.drift_before,
                        "drift_after": r.drift_after,
                        "cause": r.cause,
                    }
                    for r in self.helix_core.repair_history
                ],
            },
        }

    async def store_strand(self, strand) -> None:
        """Store a symbolic strand in the helix"""
        if self.locked:
            raise PermissionError(f"Memory {self.memory_id} is locked")

        self.strands[strand.strand_id] = strand
        self.access_count += 1

    async def retrieve_strand(self, strand_id: str):
        """Retrieve a symbolic strand by ID"""
        if self.locked:
            raise PermissionError(f"Memory {self.memory_id} is locked")

        self.access_count += 1
        self.last_accessed = datetime.now(timezone.utc)
        return self.strands.get(strand_id)

    async def verify_integrity(self) -> dict[str, Any]:
        """Verify the integrity of the memory helix"""
        drift_score = self.helix_core.calculate_drift()
        should_repair = self.helix_core.should_repair()

        return {
            "status": ("healthy" if drift_score < 0.1 else "degraded" if drift_score < 0.3 else "critical"),
            "drift_score": drift_score,
            "should_repair": should_repair,
            "last_accessed": (self.last_accessed.isoformat() if self.last_accessed else None),
            "access_count": self.access_count,
            "repair_count": len(self.helix_core.repair_history),
            "locked": self.locked,
        }

    @classmethod
    def from_export(cls, data: dict[str, Any]) -> "MemoryHelix":
        """Restore memory from export"""
        memory = cls(data["memory_id"], data["origin"])
        memory.helix_core.current = SymbolicStrand(data["current"])
        memory.emotional_strand = SymbolicStrand(data["emotional"])
        memory.temporal_strand = SymbolicStrand(data["temporal"])
        memory.causal_strand = SymbolicStrand(data["causal"])

        # Restore metadata
        meta = data["metadata"]
        memory.created_at = datetime.fromisoformat(meta["created"])
        memory.access_count = meta["accessed"]
        memory.last_accessed = datetime.fromisoformat(meta["last_access"]) if meta["last_access"] else None
        memory.tags = set(meta["tags"])
        memory.locked = meta["locked"]

        return memory


# CLI Test Interface
if __name__ == "__main__":
    print("🧬 DNA Healix Test Interface")
    print("=" * 50)

    # Create test memory
    test_glyphs = [
        "TRUST",
        "PROTECT",
        "LEARN",
        "GROW",
        "HELP",
        "UNDERSTAND",
        "CREATE",
        "CONNECT",
    ]
    memory = MemoryHelix("test_memory_001", test_glyphs)

    print(f"\n✨ Created memory: {memory}")
    print(f"📝 Origin: {' → '.join(test_glyphs)}")

    # Simulate drift
    drifted_glyphs = [
        "TRUST",
        "DEFEND",
        "LEARN",
        "GROW",
        "ASSIST",
        "ANALYZE",
        "BUILD",
        "NETWORK",
    ]
    memory.mutate(drifted_glyphs)

    print(f"\n🌊 After drift: {' → '.join(drifted_glyphs)}")
    print(f"📊 Drift score: {memory.helix_core.calculate_drift():.3f}")

    # Repair
    if memory.helix_core.should_repair():
        print("\n🛠 Initiating repair...")
        memory.helix_core.repair(RepairMethod.PARTIAL_HEAL)
        print(f"✅ Repaired: {' → '.join(memory.helix_core.current.sequence)}")
        print(f"📊 New drift: {memory.helix_core.calculate_drift():.3f}")

    # Show repair history
    if memory.helix_core.repair_history:
        print("\n📜 Repair History:")
        for r in memory.helix_core.repair_history:
            print(f"   • {r.timestamp.strftime('%H:%M:%S')} - {r.repair_method.value}")
            print(f"     Drift: {r.drift_before:.3f} → {r.drift_after:.3f}")
            print(f"     Glyphs repaired: {len(r.glyphs_repaired)}")

    print("\n✨ DNA Healix test complete!")
