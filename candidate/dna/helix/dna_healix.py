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

Author: LUKHAS AGI Framework
Version: 1.0
"""

import asyncio
import contextlib
import hashlib
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional

import numpy as np

from lukhas.core.common import get_logger

# from sklearn.metrics.pairwise import cosine_similarity  # Optional dependency


logger = get_logger(__name__)


def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    """Calculate cosine similarity between two vectors"""
    # Handle 2D arrays (as sklearn expects)
    if v1.ndim == 2:
        v1 = v1.flatten()
    if v2.ndim == 2:
        v2 = v2.flatten()

    # Calculate cosine similarity
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)

    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0

    return dot_product / (norm_v1 * norm_v2)


class RepairMethod(Enum):
    """Types of repair methods available"""

    FULL_RESET = "full_reset"  # Complete reset to origin
    PARTIAL_HEAL = "partial_heal"  # Heal only high-drift segments
    CONSENSUS = "consensus"  # Use quorum of strands
    GUIDED = "guided"  # AI-guided restoration
    SELECTIVE = "selective"  # Repair specific glyphs only


@dataclass
class RepairMetadata:
    """Metadata for repair operations"""

    repaired_by: str
    repair_method: RepairMethod
    cause: str
    confidence: float
    timestamp: datetime
    drift_before: float
    drift_after: float
    glyphs_repaired: list[int]


class SymbolicStrand:
    """
    🧬 Immutable symbolic strand representing a sequence of meaning units
    """

    def __init__(self, glyphs: list[str]):
        """Initialize with immutable glyph sequence"""
        self.sequence = tuple(glyphs)  # Immutable
        self._hash = None
        self._vector = None

    def __len__(self) -> int:
        return len(self.sequence)

    def __getitem__(self, index: int) -> str:
        return self.sequence[index]

    def __iter__(self):
        return iter(self.sequence)

    def entropy(self) -> float:
        """Calculate Shannon entropy of the strand"""
        if not self.sequence:
            return 0.0

        # Count occurrences
        counts = defaultdict(int)
        for glyph in self.sequence:
            counts[glyph] += 1

        # Calculate entropy
        total = len(self.sequence)
        entropy = 0.0
        for count in counts.values():
            if count > 0:
                p = count / total
                entropy -= p * np.log2(p)

        # Normalize by max possible entropy
        max_entropy = np.log2(len(self.sequence))
        return entropy / max_entropy if max_entropy > 0 else 0.0

    def hash(self) -> str:
        """Get cryptographic hash of the strand"""
        if self._hash is None:
            content = "".join(self.sequence)
            self._hash = hashlib.sha256(content.encode()).hexdigest()
        return self._hash

    def to_vector(
        self, glyph_embeddings: Optional[dict[str, np.ndarray]] = None
    ) -> np.ndarray:
        """Convert strand to vector representation"""
        if glyph_embeddings:
            # Use provided embeddings
            vectors = [glyph_embeddings.get(g, np.zeros(128)) for g in self.sequence]
            return np.mean(vectors, axis=0)
        else:
            # Create stable one-hot encoding using all possible glyphs seen
            # This ensures consistent vector dimensions
            all_glyphs = sorted(set(self.sequence))
            vector = np.zeros(len(all_glyphs) * len(self.sequence))

            for i, glyph in enumerate(self.sequence):
                idx = all_glyphs.index(glyph)
                vector[i * len(all_glyphs) + idx] = 1.0

            return vector

    def distance_to(self, other: "SymbolicStrand", method: str = "edit") -> float:
        """Calculate distance to another strand"""
        if method == "edit":
            # Levenshtein distance
            return self._edit_distance(other)
        elif method == "cosine":
            # Cosine similarity with unified vocabulary
            # Get all unique glyphs from both strands
            all_glyphs = sorted(set(self.sequence) | set(other.sequence))

            # Create vectors with same dimensions
            v1 = np.zeros(len(all_glyphs) * len(self.sequence))
            v2 = np.zeros(len(all_glyphs) * len(other.sequence))

            # Fill vectors
            for i, glyph in enumerate(self.sequence):
                if glyph in all_glyphs:
                    idx = all_glyphs.index(glyph)
                    if i * len(all_glyphs) + idx < len(v1):
                        v1[i * len(all_glyphs) + idx] = 1.0

            for i, glyph in enumerate(other.sequence):
                if glyph in all_glyphs:
                    idx = all_glyphs.index(glyph)
                    if i * len(all_glyphs) + idx < len(v2):
                        v2[i * len(all_glyphs) + idx] = 1.0

            # Ensure same dimensions
            if len(v1) != len(v2):
                max_len = max(len(v1), len(v2))
                v1 = np.pad(v1, (0, max_len - len(v1)))
                v2 = np.pad(v2, (0, max_len - len(v2)))

            similarity = cosine_similarity(v1, v2)
            return 1 - similarity
        else:
            raise ValueError(f"Unknown distance method: {method}")

    def _edit_distance(self, other: "SymbolicStrand") -> int:
        """Calculate Levenshtein distance"""
        m, n = len(self), len(other)
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if self[i - 1] == other[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])

        return dp[m][n]


class DNAHealixCore:
    """
    🧠 Core DNA helix manager with origin/current strand tracking
    """

    def __init__(
        self, origin: SymbolicStrand, current: Optional[SymbolicStrand] = None
    ):
        self.origin = origin
        self.current = current or SymbolicStrand(list(origin.sequence))
        self.repair_history: list[RepairMetadata] = []
        self.drift_threshold = 0.3  # 30% drift triggers repair
        self.entropy_threshold = 0.4  # Minimum entropy for safety

    def calculate_drift(self, method: str = "combined") -> float:
        """
        Calculate drift score between origin and current

        Methods:
        - 'edit': Edit distance normalized by length
        - 'cosine': Cosine distance
        - 'entropy': Entropy difference
        - 'combined': Weighted combination of all methods
        """
        if method == "edit":
            distance = self.origin.distance_to(self.current, "edit")
            return distance / max(len(self.origin), len(self.current))

        elif method == "cosine":
            return self.origin.distance_to(self.current, "cosine")

        elif method == "entropy":
            return abs(self.origin.entropy() - self.current.entropy())

        elif method == "combined":
            # Weighted combination
            edit_drift = self.calculate_drift("edit")
            cosine_drift = self.calculate_drift("cosine")
            entropy_drift = self.calculate_drift("entropy")

            # Weights: edit=0.5, cosine=0.3, entropy=0.2
            return 0.5 * edit_drift + 0.3 * cosine_drift + 0.2 * entropy_drift

        else:
            raise ValueError(f"Unknown drift method: {method}")

    def should_repair(self, threshold: Optional[float] = None) -> bool:
        """Check if repair is needed based on drift"""
        threshold = threshold or self.drift_threshold
        return self.calculate_drift() > threshold

    def repair(
        self,
        method: RepairMethod = RepairMethod.PARTIAL_HEAL,
        cause: str = "Automatic drift detection",
        **kwargs,
    ) -> SymbolicStrand:
        """
        Perform repair based on selected method
        """
        drift_before = self.calculate_drift()

        if method == RepairMethod.FULL_RESET:
            repaired = self._full_reset()

        elif method == RepairMethod.PARTIAL_HEAL:
            repaired = self._partial_heal(**kwargs)

        elif method == RepairMethod.CONSENSUS:
            repaired = self._consensus_repair(**kwargs)

        elif method == RepairMethod.GUIDED:
            repaired = self._guided_repair(**kwargs)

        elif method == RepairMethod.SELECTIVE:
            repaired = self._selective_repair(**kwargs)

        else:
            raise ValueError(f"Unknown repair method: {method}")

        # Validate repaired strand
        repaired = self._validate_repair(repaired)

        # Update current and log
        glyphs_repaired = [
            i
            for i, (a, b) in enumerate(zip(self.current.sequence, repaired.sequence))
            if a != b
        ]
        self.current = repaired
        drift_after = self.calculate_drift()

        metadata = RepairMetadata(
            repaired_by=f"{method.value}_repair",
            repair_method=method,
            cause=cause,
            confidence=1.0 - drift_after,
            timestamp=datetime.now(),
            drift_before=drift_before,
            drift_after=drift_after,
            glyphs_repaired=glyphs_repaired,
        )

        self.repair_history.append(metadata)
        logger.info(f"🛠 Repair complete: {drift_before:.3f} → {drift_after:.3f}")

        return repaired

    def _full_reset(self) -> SymbolicStrand:
        """Complete reset to origin strand"""
        return SymbolicStrand(list(self.origin.sequence))

    def _partial_heal(self, heal_threshold: float = 0.5) -> SymbolicStrand:
        """Heal only segments with high local drift"""
        glyphs = list(self.current.sequence)

        # Find segments with high drift
        window_size = max(3, len(glyphs) // 10)
        for i in range(0, len(glyphs) - window_size + 1):
            window_current = glyphs[i : i + window_size]
            window_origin = list(self.origin.sequence)[i : i + window_size]

            # Calculate local drift
            local_drift = (
                sum(1 for a, b in zip(window_current, window_origin) if a != b)
                / window_size
            )

            if local_drift > heal_threshold:
                # Heal this segment
                for j in range(window_size):
                    if i + j < len(glyphs) and i + j < len(self.origin):
                        glyphs[i + j] = self.origin[i + j]

        return SymbolicStrand(glyphs)

    def _consensus_repair(
        self, quorum_strands: list[SymbolicStrand], min_agreement: float = 0.6
    ) -> SymbolicStrand:
        """Repair using consensus from multiple strands"""
        if not quorum_strands:
            return self._partial_heal()

        glyphs = []
        max_len = max(len(s) for s in [self.origin, self.current, *quorum_strands])

        for i in range(max_len):
            # Collect votes for this position
            votes = defaultdict(int)

            # Origin gets extra weight
            if i < len(self.origin):
                votes[self.origin[i]] += 2

            # Current strand vote
            if i < len(self.current):
                votes[self.current[i]] += 1

            # Quorum votes
            for strand in quorum_strands:
                if i < len(strand):
                    votes[strand[i]] += 1

            # Select by consensus
            total_votes = sum(votes.values())
            best_glyph = max(votes.items(), key=lambda x: x[1])

            if best_glyph[1] / total_votes >= min_agreement:
                glyphs.append(best_glyph[0])
            else:
                # No consensus, use origin
                glyphs.append(self.origin[i] if i < len(self.origin) else best_glyph[0])

        return SymbolicStrand(glyphs)

    def _guided_repair(
        self, guidance_function: Optional[Callable] = None
    ) -> SymbolicStrand:
        """AI-guided repair using external guidance"""
        if guidance_function is None:
            # Default to partial heal
            return self._partial_heal()

        # Get AI guidance
        suggested_glyphs = guidance_function(
            origin=self.origin.sequence,
            current=self.current.sequence,
            drift=self.calculate_drift(),
        )

        return SymbolicStrand(suggested_glyphs)

    def _selective_repair(self, positions: list[int]) -> SymbolicStrand:
        """Repair only specific positions"""
        glyphs = list(self.current.sequence)

        for pos in positions:
            if 0 <= pos < len(glyphs) and pos < len(self.origin):
                glyphs[pos] = self.origin[pos]

        return SymbolicStrand(glyphs)

    def _validate_repair(self, repaired: SymbolicStrand) -> SymbolicStrand:
        """Validate repaired strand meets safety constraints"""
        # Check entropy
        if repaired.entropy() < self.entropy_threshold:
            logger.warning(f"⚠️ Low entropy {repaired.entropy():.3f}, using origin")
            return self.origin

        # Check not empty
        if len(repaired) == 0:
            logger.warning("⚠️ Empty strand, using origin")
            return self.origin

        return repaired


class SymbolicRepairLoop:
    """
    🔁 Recursive self-assembly and monitoring loop
    """

    def __init__(
        self, dna: DNAHealixCore, check_interval: float = 1.0, auto_repair: bool = True
    ):
        self.dna = dna
        self.check_interval = check_interval
        self.auto_repair = auto_repair
        self.iteration = 0
        self.running = False
        self._task = None

    async def start(self):
        """Start the monitoring loop"""
        self.running = True
        self._task = asyncio.create_task(self._monitor_loop())
        logger.info("🔄 Symbolic repair loop started")

    async def stop(self):
        """Stop the monitoring loop"""
        self.running = False
        if self._task:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task
        logger.info("⏹ Symbolic repair loop stopped")

    async def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
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

                self.dna.repair(
                    method=method, cause=f"Auto-repair at drift {drift:.3f}"
                )
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
        self.created_at = datetime.now()
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
        self.last_accessed = datetime.now()

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
                "last_access": (
                    self.last_accessed.isoformat() if self.last_accessed else None
                ),
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
                "last_access": (
                    self.last_accessed.isoformat() if self.last_accessed else None
                ),
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
        self.last_accessed = datetime.now()
        return self.strands.get(strand_id)

    async def verify_integrity(self) -> dict[str, Any]:
        """Verify the integrity of the memory helix"""
        drift_score = self.helix_core.calculate_drift()
        should_repair = self.helix_core.should_repair()

        return {
            "status": (
                "healthy"
                if drift_score < 0.1
                else "degraded" if drift_score < 0.3 else "critical"
            ),
            "drift_score": drift_score,
            "should_repair": should_repair,
            "last_accessed": (
                self.last_accessed.isoformat() if self.last_accessed else None
            ),
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
        memory.last_accessed = (
            datetime.fromisoformat(meta["last_access"]) if meta["last_access"] else None
        )
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
