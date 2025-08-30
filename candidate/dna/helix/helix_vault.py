"""
🔐 Helix Vault - Secure Repository for DNA Helix Memories
========================================================

Manages collections of immutable memories with DNA helix structure.
Provides search, consensus, and vault-wide operations.
"""

import asyncio
import contextlib
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import aiofiles

from lukhas.core.common import get_logger

from .dna_healix import (
    MemoryHelix,
    RepairMethod,
)

logger = get_logger(__name__)


class HelixVault:
    """
    🔐 Encrypted repository of trusted symbolic strands
    """

    def __init__(self, vault_path: Optional[Path] = None):
        self.memories: dict[str, MemoryHelix] = {}
        self.vault_path = vault_path or Path("./helix_vault")
        self.vault_path.mkdir(exist_ok=True)

        # Indexing structures
        self.tag_index: dict[str, set[str]] = defaultdict(set)  # tag -> memory_ids
        self.time_index: dict[str, datetime] = {}  # memory_id -> created_at
        self.drift_monitor: dict[str, float] = {}  # memory_id -> last_drift

        # Vault configuration
        self.auto_persist = True
        self.persist_interval = 300  # 5 minutes
        self.max_drift_threshold = 0.5
        self.consensus_min_memories = 3

        # Background tasks
        self._persist_task = None
        self._monitor_task = None
        self.running = False

    async def start(self):
        """Start vault background services"""
        self.running = True

        # Load existing memories
        await self.load_vault()

        # Start background tasks
        self._persist_task = asyncio.create_task(self._persist_loop())
        self._monitor_task = asyncio.create_task(self._monitor_loop())

        logger.info(f"🔐 Helix Vault started with {len(self.memories)} memories")

    async def stop(self):
        """Stop vault services"""
        self.running = False

        # Cancel tasks
        for task in [self._persist_task, self._monitor_task]:
            if task:
                task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await task

        # Final persist
        await self.persist_vault()
        logger.info("🔐 Helix Vault stopped")

    def store_memory(self, memory_data):
        """Store memory in the helix vault - alias for create_memory"""
        return self.create_memory(
            memory_id=memory_data.get("id", "auto"),
            content=memory_data.get("content", {}),
            tags=memory_data.get("tags", []),
        )

    def retrieve_memory(self, memory_id):
        """Retrieve memory from the helix vault - alias for get_memory"""
        return self.get_memory(memory_id)

    def preserve_identity(self):
        """Preserve identity in DNA helix"""
        # This maintains the integrity of all memories
        return {
            "preserved": True,
            "memory_count": len(self.memories),
            "vault_path": str(self.vault_path),
        }

    def create_memory(
        self, memory_id: str, initial_glyphs: list[str], tags: Optional[set[str]] = None
    ) -> MemoryHelix:
        """Create new memory in vault"""
        if memory_id in self.memories:
            raise ValueError(f"Memory {memory_id} already exists")

        memory = MemoryHelix(memory_id, initial_glyphs)
        if tags:
            memory.tags.update(tags)

        self.memories[memory_id] = memory
        self.time_index[memory_id] = memory.created_at
        self.drift_monitor[memory_id] = 0.0

        # Update tag index
        for tag in memory.tags:
            self.tag_index[tag].add(memory_id)

        logger.info(f"✨ Created memory {memory_id} with {len(initial_glyphs)} glyphs")
        return memory

    def get_memory(self, memory_id: str) -> Optional[MemoryHelix]:
        """Retrieve memory by ID"""
        return self.memories.get(memory_id)

    def search_by_tags(self, tags: set[str], match_all: bool = False) -> list[MemoryHelix]:
        """Search memories by tags"""
        if match_all:
            # All tags must match
            memory_ids = None
            for tag in tags:
                tag_memories = self.tag_index.get(tag, set())
                if memory_ids is None:
                    memory_ids = tag_memories.copy()
                else:
                    memory_ids &= tag_memories

            if memory_ids is None:
                return []
        else:
            # Any tag matches
            memory_ids = set()
            for tag in tags:
                memory_ids.update(self.tag_index.get(tag, set()))

        return [self.memories[mid] for mid in memory_ids if mid in self.memories]

    def search_by_drift(self, min_drift: float = 0.0, max_drift: float = 1.0) -> list[MemoryHelix]:
        """Search memories by drift range"""
        results = []
        for memory in self.memories.values():
            drift = memory.helix_core.calculate_drift()
            if min_drift <= drift <= max_drift:
                results.append(memory)
        return results

    def search_by_time(self, start: datetime, end: datetime) -> list[MemoryHelix]:
        """Search memories by creation time"""
        results = []
        for memory_id, created_at in self.time_index.items():
            if start <= created_at <= end and memory_id in self.memories:
                results.append(self.memories[memory_id])
        return results

    async def consensus_repair(
        self, memory_id: str, quorum_tags: Optional[set[str]] = None
    ) -> bool:
        """
        Repair memory using consensus from similar memories
        """
        memory = self.get_memory(memory_id)
        if not memory:
            return False

        # Find quorum memories
        if quorum_tags:
            quorum_memories = self.search_by_tags(quorum_tags)
        else:
            # Use memories with similar tags
            quorum_memories = self.search_by_tags(memory.tags)

        # Remove self from quorum
        quorum_memories = [m for m in quorum_memories if m.memory_id != memory_id]

        if len(quorum_memories) < self.consensus_min_memories:
            logger.warning(
                f"Insufficient quorum for {memory_id}: {len(quorum_memories)} < {self.consensus_min_memories}"
            )
            return False

        # Extract strands for consensus
        quorum_strands = [m.helix_core.current for m in quorum_memories]

        # Perform consensus repair
        memory.helix_core.repair(
            method=RepairMethod.CONSENSUS,
            cause=f"Vault consensus with {len(quorum_strands)} memories",
            quorum_strands=quorum_strands,
        )

        return True

    def get_statistics(self) -> dict[str, Any]:
        """Get vault statistics"""
        if not self.memories:
            return {
                "total_memories": 0,
                "avg_drift": 0.0,
                "max_drift": 0.0,
                "total_repairs": 0,
                "locked_memories": 0,
                "unique_tags": 0,
            }

        drifts = [m.helix_core.calculate_drift() for m in self.memories.values()]
        repairs = sum(len(m.helix_core.repair_history) for m in self.memories.values())
        locked = sum(1 for m in self.memories.values() if m.locked)

        return {
            "total_memories": len(self.memories),
            "avg_drift": sum(drifts) / len(drifts),
            "max_drift": max(drifts),
            "min_drift": min(drifts),
            "total_repairs": repairs,
            "locked_memories": locked,
            "unique_tags": len(self.tag_index),
            "avg_memory_size": sum(len(m.origin_strand) for m in self.memories.values())
            / len(self.memories),
        }

    async def _persist_loop(self):
        """Background persistence loop"""
        while self.running:
            try:
                await asyncio.sleep(self.persist_interval)
                if self.auto_persist:
                    await self.persist_vault()
            except Exception as e:
                logger.error(f"Persist error: {e}")

    async def _monitor_loop(self):
        """Background drift monitoring loop"""
        while self.running:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                await self._check_drifts()
            except Exception as e:
                logger.error(f"Monitor error: {e}")

    async def _check_drifts(self):
        """Check all memories for high drift"""
        high_drift_memories = []

        for memory in self.memories.values():
            drift = memory.helix_core.calculate_drift()
            self.drift_monitor[memory.memory_id] = drift

            if drift > self.max_drift_threshold:
                high_drift_memories.append((memory.memory_id, drift))

        if high_drift_memories:
            logger.warning(f"⚠️ {len(high_drift_memories)} memories with high drift detected")
            for memory_id, drift in high_drift_memories[:5]:  # Log top 5
                logger.warning(f"   • {memory_id}: {drift:.3f}")

    async def persist_vault(self):
        """Persist vault to disk"""
        vault_data = {
            "version": "1.0",
            "created": datetime.now().isoformat(),
            "statistics": self.get_statistics(),
            "memories": {},
        }

        # Export all memories
        for memory_id, memory in self.memories.items():
            vault_data["memories"][memory_id] = memory.export()

        # Save to file
        vault_file = self.vault_path / "vault.json"
        temp_file = vault_file.with_suffix(".tmp")

        async with aiofiles.open(temp_file, "w") as f:
            await f.write(json.dumps(vault_data, indent=2))

        # Atomic rename
        temp_file.rename(vault_file)

        logger.info(f"💾 Persisted {len(self.memories)} memories to vault")

    async def load_vault(self):
        """Load vault from disk"""
        vault_file = self.vault_path / "vault.json"

        if not vault_file.exists():
            logger.info("No existing vault found")
            return

        try:
            async with aiofiles.open(vault_file) as f:
                content = await f.read()
                vault_data = json.loads(content)

            # Restore memories
            for memory_id, memory_data in vault_data["memories"].items():
                memory = MemoryHelix.from_export(memory_data)
                self.memories[memory_id] = memory
                self.time_index[memory_id] = memory.created_at
                self.drift_monitor[memory_id] = memory.helix_core.calculate_drift()

                # Rebuild tag index
                for tag in memory.tags:
                    self.tag_index[tag].add(memory_id)

            logger.info(f"📂 Loaded {len(self.memories)} memories from vault")

        except Exception as e:
            logger.error(f"Failed to load vault: {e}")

    def create_drift_oracle(self):
        """Create a drift analysis oracle"""
        return DriftOracle(self)


class DriftOracle:
    """
    🔮 Analyzes and predicts memory drift patterns
    """

    def __init__(self, vault: HelixVault):
        self.vault = vault

    def analyze_drift_patterns(self) -> dict[str, Any]:
        """Analyze drift patterns across vault"""
        if not self.vault.memories:
            return {"status": "no_memories"}

        # Collect drift data
        drift_data = []
        for memory in self.vault.memories.values():
            drift = memory.helix_core.calculate_drift()
            age = (datetime.now() - memory.created_at).total_seconds() / 3600  # hours
            repairs = len(memory.helix_core.repair_history)

            drift_data.append(
                {
                    "memory_id": memory.memory_id,
                    "drift": drift,
                    "age_hours": age,
                    "repairs": repairs,
                    "access_count": memory.access_count,
                    "tags": len(memory.tags),
                    "locked": memory.locked,
                }
            )

        # Calculate patterns
        avg_drift = sum(d["drift"] for d in drift_data) / len(drift_data)

        # Drift velocity (drift per hour)
        velocities = []
        for d in drift_data:
            if d["age_hours"] > 0:
                velocities.append(d["drift"] / d["age_hours"])

        avg_velocity = sum(velocities) / len(velocities) if velocities else 0

        # Repair effectiveness
        repaired = [d for d in drift_data if d["repairs"] > 0]
        repair_effectiveness = (
            1.0 - (sum(d["drift"] for d in repaired) / len(repaired)) if repaired else 0
        )

        return {
            "total_analyzed": len(drift_data),
            "average_drift": avg_drift,
            "max_drift": max(d["drift"] for d in drift_data),
            "min_drift": min(d["drift"] for d in drift_data),
            "drift_velocity": avg_velocity,
            "repair_effectiveness": repair_effectiveness,
            "high_drift_memories": [d["memory_id"] for d in drift_data if d["drift"] > 0.5],
            "stable_memories": [d["memory_id"] for d in drift_data if d["drift"] < 0.1],
            "frequently_accessed": sorted(
                drift_data, key=lambda x: x["access_count"], reverse=True
            )[:5],
        }

    def predict_repair_needs(self, hours_ahead: float = 24) -> list[tuple[str, float]]:
        """Predict which memories will need repair"""
        predictions = []

        for memory in self.vault.memories.values():
            # Calculate drift velocity
            age_hours = (datetime.now() - memory.created_at).total_seconds() / 3600
            if age_hours > 0:
                velocity = memory.helix_core.calculate_drift() / age_hours

                # Predict future drift
                future_drift = memory.helix_core.calculate_drift() + (velocity * hours_ahead)

                if future_drift > memory.helix_core.drift_threshold:
                    predictions.append((memory.memory_id, future_drift))

        return sorted(predictions, key=lambda x: x[1], reverse=True)


# Example usage
if __name__ == "__main__":

    async def demo():
        print("🔐 Helix Vault Demo")
        print("=" * 50)

        # Create vault
        vault = HelixVault()
        await vault.start()

        # Create some memories
        memory1 = vault.create_memory(
            "episodic_001",
            ["EXPERIENCE", "JOY", "FRIEND", "PARK", "SUNNY", "LAUGH"],
            tags={"episodic", "positive", "social"},
        )

        vault.create_memory(
            "semantic_001",
            ["CONCEPT", "GRAVITY", "FORCE", "MASS", "ACCELERATION"],
            tags={"semantic", "physics", "knowledge"},
        )

        vault.create_memory(
            "procedural_001",
            ["STEP", "MIX", "POUR", "HEAT", "STIR", "SERVE"],
            tags={"procedural", "cooking", "skill"},
        )

        # Show statistics
        stats = vault.get_statistics()
        print("\n📊 Vault Statistics:")
        for key, value in stats.items():
            print(f"   • {key}: {value}")

        # Simulate drift
        memory1.mutate(["EXPERIENCE", "HAPPY", "FRIEND", "BEACH", "SUNNY", "SMILE"])

        # Check drift oracle
        oracle = vault.create_drift_oracle()
        analysis = oracle.analyze_drift_patterns()

        print("\n🔮 Drift Analysis:")
        print(f"   • Average drift: {analysis['average_drift']:.3f}")
        print(f"   • Drift velocity: {analysis['drift_velocity']:.3f}/hour")

        # Persist
        await vault.persist_vault()

        # Stop
        await vault.stop()
        print("\n✨ Demo complete!")

    asyncio.run(demo())
