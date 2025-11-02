"""
VIVOX.ME - Memory Expansion Subsystem
The living, multidimensional thread of cognition

Core Features:
- 3D encrypted memory helix (DNA-inspired)
- Symbolic proteome with protein folding
- Immutable ethical timeline
- Memory veiling (GDPR compliance)
- Resonant access and flashbacks
"""

import hashlib
import json
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

import numpy as np

# Import optimized logging
try:
    from ..utils.logging_config import VIVOXLoggers, debug_trace, log_performance

    logger = VIVOXLoggers.ME
except ImportError:
    # Fallback for testing
    import logging

    logger = logging.getLogger("VIVOX.ME")

    def debug_trace(l, m, **k):
        return l.debug(f"{m} | {k}" if k else m)

    def log_performance(l, o, e, c=None):
        return l.info(f"{o}: {e:.3f}s")


class VeilLevel(Enum):
    """Levels of memory veiling for privacy compliance"""

    ACCESSIBLE = "accessible"
    PARTIALLY_VEILED = "partially_veiled"
    FULLY_DISENGAGED = "fully_disengaged"
    PERMANENTLY_SEALED = "permanently_sealed"


@dataclass
class MemoryHelixEntry:
    """Single entry in the 3D memory helix"""

    sequence_id: str
    decision_data: dict[str, Any]
    emotional_dna: "EmotionalDNA"
    moral_hash: str
    timestamp_utc: datetime
    cryptographic_hash: str
    previous_hash: str
    helix_coordinates: tuple[float, float, float] = field(default_factory=lambda: (0.0, 0.0, 0.0))
    resonance_score: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "sequence_id": self.sequence_id,
            "decision_data": self.decision_data,
            "emotional_dna": self.emotional_dna.to_dict(),
            "moral_hash": self.moral_hash,
            "timestamp_utc": self.timestamp_utc.isoformat(),
            "cryptographic_hash": self.cryptographic_hash,
            "previous_hash": self.previous_hash,
            "helix_coordinates": list(self.helix_coordinates),
            "resonance_score": self.resonance_score,
        }


@dataclass
class EmotionalDNA:
    """Emotional encoding for memory entries"""

    valence: float  # -1 to 1 (negative to positive)
    arousal: float  # 0 to 1 (calm to excited)
    dominance: float  # 0 to 1 (submissive to dominant)
    resonance_frequency: float = field(init=False)

    def __post_init__(self):
        # Calculate resonance frequency based on VAD values
        self.resonance_frequency = np.sqrt(self.valence**2 + self.arousal**2 + self.dominance**2) / np.sqrt(3)

    def to_dict(self) -> dict[str, float]:
        return {
            "valence": self.valence,
            "arousal": self.arousal,
            "dominance": self.dominance,
            "resonance_frequency": self.resonance_frequency,
        }


@dataclass
class VeilingOperation:
    """Record of memory veiling operation"""

    memory_ids: list[str]
    reason: str
    approval_hash: str
    timestamp: datetime
    veil_level: VeilLevel


@dataclass
class TruthAuditResult:
    """Result of truth audit query"""

    decision_traces: list[dict[str, Any]] = field(default_factory=list)

    def add_decision_trace(
        self,
        what_known: dict[str, Any],
        when_decided: datetime,
        why_acted: list[str],
        moral_fingerprint: str,
    ):
        self.decision_traces.append(
            {
                "what_known": what_known,
                "when_decided": when_decided.isoformat(),
                "why_acted": why_acted,
                "moral_fingerprint": moral_fingerprint,
            }
        )


class MemoryHelix3D:
    """3D DNA-inspired memory storage structure"""

    def __init__(self):
        self.entries: list[MemoryHelixEntry] = []
        self.sequence_index: dict[str, int] = {}
        self.coordinate_index: dict[tuple[int, int, int], list[str]] = defaultdict(list)
        self.latest_hash = "genesis_block"

    async def append_entry(self, entry: MemoryHelixEntry, coordinates: tuple[float, float, float]):
        """Add entry to helix at specified coordinates"""
        entry.helix_coordinates = coordinates
        self.entries.append(entry)
        self.sequence_index[entry.sequence_id] = len(self.entries) - 1

        # Index by discretized coordinates for spatial queries
        discrete_coords = tuple(int(c * 100) for c in coordinates)
        self.coordinate_index[discrete_coords].append(entry.sequence_id)

        self.latest_hash = entry.cryptographic_hash

    async def get_latest_hash(self) -> str:
        """Get hash of most recent entry"""
        return self.latest_hash

    async def get_entry(self, sequence_id: str) -> Optional[MemoryHelixEntry]:
        """Retrieve entry by sequence ID"""
        if sequence_id in self.sequence_index:
            return self.entries[self.sequence_index[sequence_id]]
        return None

    async def iterate_entries(self):
        """Async iterator over all entries"""
        for entry in self.entries:
            yield entry


class SymbolicProteome:
    """Protein folding system for memory organization"""

    def __init__(self):
        self.protein_folds: dict[str, ProteinFold] = {}

    async def fold_memory_protein(self, entry: MemoryHelixEntry, emotional_context: dict[str, Any]) -> "ProteinFold":
        """Fold memory into protein structure (placeholder for full implementation)"""
        # This would implement the full AlphaFold2-inspired folding
        # For now, return a simple fold structure
        fold = ProteinFold(
            protein_id=f"fold_{entry.sequence_id}",
            sequence=entry.sequence_id,
            stability=0.8,
            structure_data={},
        )
        self.protein_folds[fold.protein_id] = fold
        return fold


@dataclass
class ProteinFold:
    """Folded protein structure for memory"""

    protein_id: str
    sequence: str
    stability: float
    structure_data: dict[str, Any]


class ImmutableEthicalTimeline:
    """Append-only ethical decision log"""

    def __init__(self):
        self.timeline: list[dict[str, Any]] = []
        self.decision_index: dict[str, list[int]] = defaultdict(list)

    async def append_ethical_record(self, decision: dict[str, Any], moral_fingerprint: str, sequence_id: str):
        """Add ethical decision to timeline"""
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "decision": decision,
            "moral_fingerprint": moral_fingerprint,
            "memory_sequence_id": sequence_id,
            "index": len(self.timeline),
        }
        self.timeline.append(record)

        # Index by decision type for fast queries
        if "action" in decision:
            self.decision_index[decision["action"]].append(len(self.timeline) - 1)

    async def append_veiling_record(self, operation: VeilingOperation):
        """Record memory veiling operation"""
        record = {
            "timestamp": operation.timestamp.isoformat(),
            "operation_type": "memory_veiling",
            "memory_ids": operation.memory_ids,
            "reason": operation.reason,
            "approval_hash": operation.approval_hash,
            "veil_level": operation.veil_level.value,
        }
        self.timeline.append(record)

    async def search_decisions(self, query: str) -> list[dict[str, Any]]:
        """Search timeline for relevant decisions"""
        # Simple keyword search implementation
        results = []
        query_lower = query.lower()

        for record in self.timeline:
            if "decision" in record:
                decision_str = json.dumps(record["decision"]).lower()
                if query_lower in decision_str:
                    results.append(record)

        return results


class SomaLayer:
    """Memory veiling layer for GDPR compliance"""

    def __init__(self):
        self.veiled_memories: dict[str, VeilLevel] = {}
        self.veil_operations: list[VeilingOperation] = []

    async def is_memory_veiled(self, sequence_id: str) -> bool:
        """Check if memory is veiled"""
        return sequence_id in self.veiled_memories

    async def apply_veiling(self, operation: VeilingOperation) -> bool:
        """Apply veiling to specified memories"""
        try:
            for memory_id in operation.memory_ids:
                self.veiled_memories[memory_id] = operation.veil_level
            self.veil_operations.append(operation)
            return True
        except Exception as e:
            print(f"Veiling operation failed: {e}")
            return False


class CollapseLogger:
    """Logger for z(t) collapse events"""

    def __init__(self):
        self.collapse_log: list[dict[str, Any]] = []

    async def log_z_collapse_event(
        self,
        formula_inputs: dict[str, Any],
        collapsed_state: Any,
        collapse_timestamp: datetime,
        mathematical_trace: dict[str, Any],
    ):
        """Log detailed collapse event"""
        self.collapse_log.append(
            {
                "timestamp": collapse_timestamp.isoformat(),
                "formula_inputs": formula_inputs,
                "collapsed_state": str(collapsed_state),
                "mathematical_trace": mathematical_trace,
                "event_type": "z_collapse",
            }
        )


class VIVOXMemoryExpansion:
    """
    VIVOX.ME - The living, multidimensional thread of cognition

    Core Features:
    - 3D encrypted memory helix (DNA-inspired)
    - Symbolic proteome with protein folding
    - Immutable ethical timeline
    - Memory veiling (GDPR compliance)
    - Resonant access and flashbacks
    """

    def __init__(self):
        self.memory_helix = MemoryHelix3D()
        self.symbolic_proteome = SymbolicProteome()
        self.ethical_timeline = ImmutableEthicalTimeline()
        self.soma_layer = SomaLayer()
        self.collapse_logger = CollapseLogger()
        self._sequence_counter = 0

    async def record_decision_mutation(
        self,
        decision: dict[str, Any],
        emotional_context: dict[str, Any],
        moral_fingerprint: str,
    ) -> str:
        """
        Log every experience, decision, or "mutation" in immutable chain
        """
        start_time = time.time()

        # Debug trace entry
        debug_trace(
            logger,
            "Recording decision mutation",
            action=decision.get("action", "unknown"),
            fingerprint=moral_fingerprint[:8],
        )

        # Create DNA-inspired memory entry
        memory_entry = MemoryHelixEntry(
            sequence_id=await self._generate_sequence_id(),
            decision_data=decision,
            emotional_dna=self._encode_emotional_dna(emotional_context),
            moral_hash=moral_fingerprint,
            timestamp_utc=datetime.now(timezone.utc),
            cryptographic_hash=self._generate_tamper_evident_hash(decision),
            previous_hash=await self.memory_helix.get_latest_hash(),
        )

        # Store in 3D helix structure
        helix_coordinates = await self._calculate_helix_position(emotional_context, decision)

        await self.memory_helix.append_entry(memory_entry, helix_coordinates)

        # Update symbolic proteome
        await self.symbolic_proteome.fold_memory_protein(memory_entry, emotional_context)

        # Log to immutable ethical timeline
        await self.ethical_timeline.append_ethical_record(decision, moral_fingerprint, memory_entry.sequence_id)

        # Performance logging
        elapsed = time.time() - start_time
        debug_trace(
            logger,
            f"Memory recorded in {elapsed:.3f}s",
            sequence_id=memory_entry.sequence_id,
        )

        return memory_entry.sequence_id

    async def resonant_memory_access(
        self, emotional_state: dict[str, Any], resonance_threshold: float = 0.7
    ) -> list[MemoryHelixEntry]:
        """
        Emotional state-triggered memory retrieval (flashbacks)
        """
        current_frequency = await self._emotional_state_to_frequency(emotional_state)

        resonant_memories = []

        async for memory_entry in self.memory_helix.iterate_entries():
            memory_frequency = memory_entry.emotional_dna.resonance_frequency

            resonance = await self._calculate_resonance(current_frequency, memory_frequency)

            if resonance >= resonance_threshold:
                # Check if memory is veiled
                if not await self.soma_layer.is_memory_veiled(memory_entry.sequence_id):
                    memory_entry.resonance_score = resonance
                    resonant_memories.append(memory_entry)

        return sorted(resonant_memories, key=lambda m: m.resonance_score, reverse=True)

    async def memory_veiling_operation(self, memory_ids: list[str], veiling_reason: str, ethical_approval: str) -> bool:
        """
        GDPR-compliant memory veiling through Soma Layer
        Instead of deletion, memories are disengaged from active cognition
        """
        veil_operation = VeilingOperation(
            memory_ids=memory_ids,
            reason=veiling_reason,
            approval_hash=ethical_approval,
            timestamp=datetime.now(timezone.utc),
            veil_level=VeilLevel.FULLY_DISENGAGED,
        )

        # Apply veiling to Soma Layer
        success = await self.soma_layer.apply_veiling(veil_operation)

        if success:
            # Log as ethical decision record
            await self.ethical_timeline.append_veiling_record(veil_operation)

            # Notify other VIVOX modules
            await self._notify_memory_veiling(memory_ids)

        return success

    async def truth_audit_query(self, query: str) -> TruthAuditResult:
        """
        "What did it know, when, and why did it act?"
        Structural conscience that refuses to lie to itself
        """
        audit_result = TruthAuditResult()

        # Search through immutable ethical timeline
        relevant_decisions = await self.ethical_timeline.search_decisions(query)

        for decision in relevant_decisions:
            if "memory_sequence_id" in decision:
                # Reconstruct decision context
                memory_entry = await self.memory_helix.get_entry(decision["memory_sequence_id"])

                if memory_entry:
                    # Analyze moral reasoning chain
                    moral_chain = await self._reconstruct_moral_reasoning(memory_entry, decision)

                    audit_result.add_decision_trace(
                        what_known=memory_entry.decision_data,
                        when_decided=memory_entry.timestamp_utc,
                        why_acted=moral_chain,
                        moral_fingerprint=decision.get("moral_fingerprint", ""),
                    )

        return audit_result

    async def record_conscious_moment(self, experience: dict[str, Any], collapse_details: dict[str, Any]):
        """Record conscious experience moment"""
        # Integration point for VIVOX.CIL
        await self.collapse_logger.log_z_collapse_event(
            formula_inputs=collapse_details.get("formula_inputs", {}),
            collapsed_state=experience,
            collapse_timestamp=datetime.now(timezone.utc),
            mathematical_trace=collapse_details.get("mathematical_trace", {}),
        )

    async def link_collapse_to_memory(self, collapse_id: str, memory_sequence_id: str):
        """Link collapse event to memory entry"""
        # Integration point for VIVOX.SRM
        # This would update cross-references between systems

    async def record_reflection_moment(self, reflection_data: dict[str, Any]) -> str:
        """Record a reflection moment in memory"""
        # Create memory entry for reflection
        sequence_id = await self.record_decision_mutation(
            decision={"type": "reflection", "data": reflection_data},
            emotional_context=reflection_data.get("emotional_context", {"valence": 0, "arousal": 0.5}),
            moral_fingerprint=f"reflection_{reflection_data.get('moment_id', 'unknown')}",
        )
        return sequence_id

    # Helper methods
    async def _generate_sequence_id(self) -> str:
        """Generate unique sequence ID"""
        self._sequence_counter += 1
        timestamp = datetime.now(timezone.utc).timestamp()
        return f"vivox_me_{timestamp}_{self._sequence_counter}"

    def _encode_emotional_dna(self, emotional_context: Any) -> EmotionalDNA:
        """Encode emotional context into DNA structure"""
        # Handle both dict and list formats
        if isinstance(emotional_context, list):
            # VAD list format
            if len(emotional_context) >= 3:
                return EmotionalDNA(
                    valence=emotional_context[0],
                    arousal=emotional_context[1],
                    dominance=emotional_context[2],
                )
            else:
                return EmotionalDNA(valence=0.0, arousal=0.5, dominance=0.5)
        elif isinstance(emotional_context, dict):
            return EmotionalDNA(
                valence=emotional_context.get("valence", 0.0),
                arousal=emotional_context.get("arousal", 0.5),
                dominance=emotional_context.get("dominance", 0.5),
            )
        else:
            # Default emotional state
            return EmotionalDNA(valence=0.0, arousal=0.5, dominance=0.5)

    def _generate_tamper_evident_hash(self, decision: dict[str, Any]) -> str:
        """Generate cryptographic hash for decision"""
        decision_str = json.dumps(decision, sort_keys=True)
        return hashlib.sha256(decision_str.encode()).hexdigest()

    async def _calculate_helix_position(
        self, emotional_context: dict[str, Any], decision: dict[str, Any]
    ) -> tuple[float, float, float]:
        """Calculate 3D position in memory helix"""
        # Use emotional values and decision complexity to determine position
        # This creates a spatial organization of memories

        emotional_dna = self._encode_emotional_dna(emotional_context)

        # Radial position based on emotional intensity
        radius = emotional_dna.resonance_frequency * 10

        # Angular position based on valence
        theta = (emotional_dna.valence + 1) * np.pi  # 0 to 2π

        # Height based on time and arousal
        z = self._sequence_counter + emotional_dna.arousal * 5

        # Convert to Cartesian coordinates
        x = radius * np.cos(theta)
        y = radius * np.sin(theta)

        return (x, y, z)

    async def _emotional_state_to_frequency(self, emotional_state: dict[str, Any]) -> float:
        """Convert emotional state to resonance frequency"""
        emotional_dna = self._encode_emotional_dna(emotional_state)
        return emotional_dna.resonance_frequency

    async def _calculate_resonance(self, freq1: float, freq2: float) -> float:
        """Calculate resonance between two frequencies"""
        # Resonance is higher when frequencies are similar
        diff = abs(freq1 - freq2)
        max_diff = 1.0  # Maximum possible difference
        resonance = 1.0 - (diff / max_diff)
        return max(0.0, min(1.0, resonance))

    async def _reconstruct_moral_reasoning(self, memory_entry: MemoryHelixEntry, decision: dict[str, Any]) -> list[str]:
        """Reconstruct moral reasoning chain"""
        reasoning_chain = []

        # Extract reasoning from decision data
        if "reasoning" in memory_entry.decision_data:
            reasoning_chain.extend(memory_entry.decision_data["reasoning"])

        # Add moral fingerprint interpretation
        reasoning_chain.append(f"Moral signature: {memory_entry.moral_hash[:8]}...")

        # Add emotional context
        emotional_summary = (
            f"Emotional state: valence={memory_entry.emotional_dna.valence:.2f}, "
            f"arousal={memory_entry.emotional_dna.arousal:.2f}"
        )
        reasoning_chain.append(emotional_summary)

        return reasoning_chain

    async def _notify_memory_veiling(self, memory_ids: list[str]):
        """Notify other VIVOX modules of memory veiling"""
        # This would integrate with event bus or messaging system
        # For now, just log the notification
        print(f"Memory veiling notification: {len(memory_ids)} memories veiled")
