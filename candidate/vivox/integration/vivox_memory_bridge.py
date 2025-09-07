"""
VIVOX Memory Bridge
Bridge between existing LUKHAS memory systems and VIVOX.ME
"""

import asyncio
import builtins
import contextlib
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

# VIVOX imports
from ..memory_expansion.vivox_me_core import EmotionalDNA, MemoryHelixEntry, VIVOXMemoryExpansion


@dataclass
class MigrationResult:
    """Result of single memory migration"""

    original_id: str
    vivox_sequence_id: str
    migration_status: str
    error_message: Optional[str] = None


@dataclass
class MigrationReport:
    """Complete migration report"""

    results: list[MigrationResult]
    total_migrated: int = 0
    total_failed: int = 0

    def __post_init__(self):
        self.total_migrated = sum(1 for r in self.results if r.migration_status == "success")
        self.total_failed = sum(1 for r in self.results if r.migration_status == "failed")

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_memories": len(self.results),
            "total_migrated": self.total_migrated,
            "total_failed": self.total_failed,
            "success_rate": (self.total_migrated / len(self.results) if self.results else 0),
            "failed_memories": [
                {"id": r.original_id, "error": r.error_message} for r in self.results if r.migration_status == "failed"
            ],
        }


class HelixMemoryAdapter:
    """Adapter to convert LUKHAS memories to VIVOX helix format"""

    async def convert_to_helix_entry(self, lukhas_memory: dict[str, Any]) -> MemoryHelixEntry:
        """Convert LUKHAS memory format to VIVOX helix entry"""
        # Extract emotional context
        emotional_context = lukhas_memory.get("emotional_context", {})
        if not emotional_context:
            # Try to infer from memory content
            emotional_context = self._infer_emotional_context(lukhas_memory)

        # Create emotional DNA
        emotional_dna = EmotionalDNA(
            valence=emotional_context.get("valence", 0.0),
            arousal=emotional_context.get("arousal", 0.5),
            dominance=emotional_context.get("dominance", 0.5),
        )

        # Extract decision data
        decision_data = {
            "action": lukhas_memory.get("action", "unknown"),
            "content": lukhas_memory.get("content", {}),
            "context": lukhas_memory.get("context", {}),
            "original_type": lukhas_memory.get("memory_type", "imported"),
        }

        # Generate moral hash (simplified for imports)
        moral_hash = lukhas_memory.get("ethical_signature", "imported_memory")

        # Create helix entry
        entry = MemoryHelixEntry(
            sequence_id=f"imported_{lukhas_memory.get('id', 'unknown')}",
            decision_data=decision_data,
            emotional_dna=emotional_dna,
            moral_hash=moral_hash,
            timestamp_utc=self._parse_timestamp(lukhas_memory.get("timestamp")),
            cryptographic_hash="",  # Will be set by VIVOX.ME
            previous_hash="",  # Will be set by VIVOX.ME
        )

        return entry

    def _infer_emotional_context(self, memory: dict[str, Any]) -> dict[str, float]:
        """Infer emotional context from memory content"""
        # Simple heuristic-based inference
        content_str = json.dumps(memory).lower()

        valence = 0.0
        arousal = 0.5
        dominance = 0.5

        # Positive indicators
        positive_words = ["success", "happy", "good", "achieve", "complete", "help"]
        negative_words = ["error", "fail", "bad", "problem", "issue", "conflict"]

        positive_count = sum(1 for word in positive_words if word in content_str)
        negative_count = sum(1 for word in negative_words if word in content_str)

        # Calculate valence
        if positive_count + negative_count > 0:
            valence = (positive_count - negative_count) / (positive_count + negative_count)

        # High arousal indicators
        arousal_words = ["urgent", "critical", "important", "immediate", "emergency"]
        arousal_count = sum(1 for word in arousal_words if word in content_str)
        arousal = min(1.0, 0.5 + (arousal_count * 0.1))

        return {"valence": valence, "arousal": arousal, "dominance": dominance}

    def _parse_timestamp(self, timestamp: Any) -> datetime:
        """Parse various timestamp formats"""
        if isinstance(timestamp, datetime):
            return timestamp
        elif isinstance(timestamp, str):
            try:
                return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            except BaseException:
                return datetime.now(timezone.utc)
        elif isinstance(timestamp, (int, float)):
            return datetime.fromtimestamp(timestamp)
        else:
            return datetime.now(timezone.utc)


class VIVOXMemoryBridge:
    """
    Bridge between existing LUKHAS memory and VIVOX.ME
    """

    def __init__(self):
        self.vivox_me = VIVOXMemoryExpansion()
        self.helix_adapter = HelixMemoryAdapter()
        self._migration_log: list[MigrationResult] = []

    async def initialize_with_lukhas(self, lukhas_memory_manager: Any):
        """Initialize bridge with existing LUKHAS memory manager"""
        self.lukhas_memory = lukhas_memory_manager

    async def migrate_existing_memories(self, batch_size: int = 100) -> MigrationReport:
        """
        Migrate existing LUKHAS memories to VIVOX.ME format
        """
        if not hasattr(self, "lukhas_memory"):
            return MigrationReport(results=[])

        existing_memories = await self._get_all_lukhas_memories()

        migration_results = []

        # Process in batches
        for i in range(0, len(existing_memories), batch_size):
            batch = existing_memories[i : i + batch_size]
            batch_results = await self._migrate_batch(batch)
            migration_results.extend(batch_results)

            # Allow other tasks to run
            await asyncio.sleep(0.1)

        self._migration_log.extend(migration_results)

        return MigrationReport(results=migration_results)

    async def _get_all_lukhas_memories(self) -> list[dict[str, Any]]:
        """Get all memories from candidate.core.common system"""
        # This would interface with actual LUKHAS memory system
        # For now, return empty list as placeholder
        return []

    async def _migrate_batch(self, memories: list[dict[str, Any]]) -> list[MigrationResult]:
        """Migrate a batch of memories"""
        results = []

        for memory in memories:
            try:
                # Convert to VIVOX.ME format
                vivox_entry = await self.helix_adapter.convert_to_helix_entry(memory)

                # Store in VIVOX.ME (without triggering full decision flow)
                sequence_id = await self.vivox_me.store_migrated_memory(vivox_entry)

                results.append(
                    MigrationResult(
                        original_id=memory.get("id", "unknown"),
                        vivox_sequence_id=sequence_id,
                        migration_status="success",
                    )
                )

            except Exception as e:
                results.append(
                    MigrationResult(
                        original_id=memory.get("id", "unknown"),
                        vivox_sequence_id="",
                        migration_status="failed",
                        error_message=str(e),
                    )
                )

        return results

    async def sync_memory_operation(self, operation: str, memory_data: dict[str, Any]) -> bool:
        """
        Sync memory operations between LUKHAS and VIVOX
        """
        if operation == "create":
            # New memory created in LUKHAS, mirror to VIVOX
            return await self._sync_create(memory_data)

        elif operation == "update":
            # Memory updated in LUKHAS, update in VIVOX if exists
            return await self._sync_update(memory_data)

        elif operation == "veil":
            # Memory veiled/deleted in LUKHAS, veil in VIVOX
            return await self._sync_veil(memory_data)

        return False

    async def _sync_create(self, memory_data: dict[str, Any]) -> bool:
        """Sync memory creation"""
        try:
            # Convert and store in VIVOX
            await self.helix_adapter.convert_to_helix_entry(memory_data)

            # Use the main record method to maintain full tracking
            await self.vivox_me.record_decision_mutation(
                decision=memory_data.get("decision", {}),
                emotional_context=memory_data.get("emotional_context", {}),
                moral_fingerprint=memory_data.get("ethical_signature", "sync_create"),
            )

            return True
        except Exception as e:
            print(f"Failed to sync create: {e}")
            return False

    async def _sync_update(self, memory_data: dict[str, Any]) -> bool:
        """Sync memory update"""
        # VIVOX memories are immutable, so create new entry with reference
        updated_data = memory_data.copy()
        updated_data["update_reference"] = memory_data.get("id")

        return await self._sync_create(updated_data)

    async def _sync_veil(self, memory_data: dict[str, Any]) -> bool:
        """Sync memory veiling"""
        try:
            memory_ids = [memory_data.get("id", "")]

            return await self.vivox_me.memory_veiling_operation(
                memory_ids=memory_ids,
                veiling_reason="lukhas_sync_veil",
                ethical_approval="lukhas_system_veil",
            )
        except Exception as e:
            print(f"Failed to sync veil: {e}")
            return False

    async def query_unified_memory(
        self, query: str, include_lukhas: bool = True, include_vivox: bool = True
    ) -> dict[str, Any]:
        """
        Query across both LUKHAS and VIVOX memory systems
        """
        results = {"lukhas_results": [], "vivox_results": [], "unified_results": []}

        # Query VIVOX
        if include_vivox:
            vivox_audit = await self.vivox_me.truth_audit_query(query)
            results["vivox_results"] = vivox_audit.decision_traces

        # Query LUKHAS (placeholder)
        if include_lukhas and hasattr(self, "lukhas_memory"):
            # This would query actual LUKHAS system
            pass

        # Unify results
        results["unified_results"] = self._unify_results(results["lukhas_results"], results["vivox_results"])

        return results

    def _unify_results(
        self, lukhas_results: list[dict[str, Any]], vivox_results: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Unify results from both systems"""
        unified = []

        # Add VIVOX results with source tag
        for result in vivox_results:
            result_copy = result.copy()
            result_copy["source"] = "vivox"
            unified.append(result_copy)

        # Add LUKHAS results with source tag
        for result in lukhas_results:
            result_copy = result.copy()
            result_copy["source"] = "lukhas"
            unified.append(result_copy)

        # Sort by timestamp if available
        with contextlib.suppress(builtins.BaseException):
            unified.sort(key=lambda x: x.get("when_decided", ""), reverse=True)

        return unified


# Add method to VIVOXMemoryExpansion for migration support
async def store_migrated_memory(self, vivox_entry: MemoryHelixEntry) -> str:
    """Store migrated memory without full decision flow"""
    # Calculate helix position
    helix_coordinates = (0.0, 0.0, float(len(self.memory_helix.entries)))

    # Set hashes
    vivox_entry.cryptographic_hash = self._generate_tamper_evident_hash(vivox_entry.decision_data)
    vivox_entry.previous_hash = await self.memory_helix.get_latest_hash()

    # Store in helix
    await self.memory_helix.append_entry(vivox_entry, helix_coordinates)

    return vivox_entry.sequence_id


# Monkey patch the method onto VIVOXMemoryExpansion
VIVOXMemoryExpansion.store_migrated_memory = store_migrated_memory
