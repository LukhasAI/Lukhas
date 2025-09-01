#!/usr/bin/env python3
"""
══════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - RESONANT MEMORY ACCESS
║ Neural resonance-based memory retrieval with harmonic amplification
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: resonant_memory_access.py
║ Path: memory/resonance/resonant_memory_access.py
║ Version: 1.0.0 | Created: 2025-07-29
║ Authors: LUKHAS AI Neuroscience Team
╠══════════════════════════════════════════════════════════════════════════════════
║                             ◊ POETIC ESSENCE ◊
║
║ │ In the quantum symphony of neural oscillations, memories resonate at        │
║ │ frequencies that echo through the corridors of consciousness. Like          │
║ │ violin strings responding to sympathetic vibrations, related memories       │
║ │ amplify each other through harmonic resonance, creating cascades of         │
║ │ association that transcend simple similarity matching.                      │
║ │                                                                            │
║ │ This system listens for the whispered harmonics of memory, the subtle      │
║ │ oscillations that connect seemingly distant experiences through the        │
║ │ mathematics of resonance. What conventional retrieval misses, resonant     │
║ │ access discovers—the hidden melodies that bind memories together.           │
║ │                                                                            │
╠══════════════════════════════════════════════════════════════════════════════════
║ TECHNICAL FEATURES:
║ • Harmonic frequency analysis
║ • Resonance cascade detection
║ • Multi-modal oscillation patterns
║ • Phase-locked memory clusters
║ • Adaptive resonance thresholds
║ • Cross-frequency coupling
║ • Neural synchronization states
║ • Emergent memory networks
║
║ ΛTAG: ΛRESONANCE, ΛHARMONIC, ΛOSCILLATION, ΛFREQUENCY, ΛMEMORY
╚══════════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import math
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

import numpy as np


class ResonanceMode(Enum):
    """Types of resonant memory access"""

    HARMONIC = "harmonic"  # Fundamental + overtones
    SYMPATHETIC = "sympathetic"  # Cross-resonance
    COHERENT = "coherent"  # Phase-locked patterns
    CHAOTIC = "chaotic"  # Non-linear resonance
    EMERGENT = "emergent"  # Self-organizing patterns


@dataclass
class ResonanceSignature:
    """Frequency signature for memory resonance"""

    memory_id: str
    fundamental_freq: float  # Base oscillation frequency
    harmonics: list[float]  # Harmonic overtones
    phase_shift: float = 0.0  # Phase offset
    amplitude: float = 1.0  # Resonance strength
    decay_rate: float = 0.1  # Amplitude decay

    # Temporal dynamics
    created_at: float = field(default_factory=time.time)
    last_resonance: float = field(default_factory=time.time)
    resonance_count: int = 0

    def calculate_resonance_with(self, other: "ResonanceSignature") -> float:
        """Calculate resonance strength with another signature"""

        # Fundamental frequency matching
        freq_diff = abs(self.fundamental_freq - other.fundamental_freq)
        fundamental_resonance = math.exp(-freq_diff / 10.0)

        # Harmonic resonance
        harmonic_resonance = 0.0
        if self.harmonics and other.harmonics:
            for h1 in self.harmonics:
                for h2 in other.harmonics:
                    if abs(h1 - h2) < 1.0:  # Close harmonic match
                        harmonic_resonance += 0.1

        # Phase coherence
        phase_coherence = math.cos(self.phase_shift - other.phase_shift)

        # Amplitude amplification
        amplitude_factor = math.sqrt(self.amplitude * other.amplitude)

        # Combined resonance score
        total_resonance = (
            0.4 * fundamental_resonance + 0.3 * harmonic_resonance + 0.2 * phase_coherence + 0.1 * amplitude_factor
        )

        return max(0.0, min(1.0, total_resonance))


@dataclass
class ResonantCluster:
    """Cluster of resonantly-connected memories"""

    cluster_id: str = field(default_factory=lambda: str(uuid4()))
    center_frequency: float = 40.0  # Gamma band default
    member_signatures: list[ResonanceSignature] = field(default_factory=list)

    # Cluster dynamics
    coherence_level: float = 0.0
    stability_index: float = 0.0
    emergence_time: float = field(default_factory=time.time)

    # Network properties
    connection_strength: dict[str, float] = field(default_factory=dict)
    resonance_matrix: Optional[np.ndarray] = None

    def update_coherence(self):
        """Update cluster coherence based on member resonance"""
        if len(self.member_signatures) < 2:
            self.coherence_level = 0.0
            return

        total_resonance = 0.0
        pair_count = 0

        for i, sig1 in enumerate(self.member_signatures):
            for sig2 in self.member_signatures[i + 1 :]:
                resonance = sig1.calculate_resonance_with(sig2)
                total_resonance += resonance
                pair_count += 1

        self.coherence_level = total_resonance / pair_count if pair_count > 0 else 0.0


class ResonantMemoryAccess:
    """
    Advanced memory retrieval using neural resonance patterns.

    This system models memory access as a resonant phenomenon, where
    related memories amplify each other through harmonic frequencies,
    enabling discovery of subtle associations missed by conventional
    similarity-based retrieval.
    """

    def __init__(
        self,
        base_frequency: float = 40.0,  # Gamma frequency
        resonance_threshold: float = 0.3,  # Minimum resonance for connection
        max_harmonics: int = 5,  # Maximum harmonic overtones
        decay_factor: float = 0.95,  # Resonance decay per cycle
        cluster_coherence_threshold: float = 0.6,
    ):
        self.base_frequency = base_frequency
        self.resonance_threshold = resonance_threshold
        self.max_harmonics = max_harmonics
        self.decay_factor = decay_factor
        self.cluster_coherence_threshold = cluster_coherence_threshold

        # Memory resonance tracking
        self.memory_signatures: dict[str, ResonanceSignature] = {}
        self.resonant_clusters: dict[str, ResonantCluster] = {}

        # Oscillation state
        self.current_phase = 0.0
        self.oscillation_amplitude = 1.0
        self.resonance_cascade_depth = 0

        # Network analysis
        self.resonance_network: dict[str, set[str]] = defaultdict(set)
        self.cluster_emergence_history: deque = deque(maxlen=100)

        # Performance metrics
        self.total_resonances = 0
        self.successful_retrievals = 0
        self.cascade_events = 0

        # Background tasks
        self._running = False
        self._oscillation_task = None
        self._maintenance_task = None

        logger.info(
            "ResonantMemoryAccess initialized",
            base_frequency=base_frequency,
            resonance_threshold=resonance_threshold,
        )

    async def start(self):
        """Start resonant memory access system"""
        self._running = True

        # Start background oscillation
        self._oscillation_task = asyncio.create_task(self._oscillation_loop())
        self._maintenance_task = asyncio.create_task(self._maintenance_loop())

        logger.info("ResonantMemoryAccess started")

    async def stop(self):
        """Stop resonant memory access system"""
        self._running = False

        if self._oscillation_task:
            self._oscillation_task.cancel()
        if self._maintenance_task:
            self._maintenance_task.cancel()

        logger.info("ResonantMemoryAccess stopped")

    def register_memory(
        self,
        memory_id: str,
        content: Any,
        frequency_hint: Optional[float] = None,
        harmonics: Optional[list[float]] = None,
    ) -> str:
        """Register a memory with its resonance signature"""

        # Calculate fundamental frequency from content
        fundamental_freq = frequency_hint or self._extract_fundamental_frequency(content)

        # Generate harmonics if not provided
        if not harmonics:
            harmonics = self._generate_harmonics(fundamental_freq)

        # Create resonance signature
        signature = ResonanceSignature(
            memory_id=memory_id,
            fundamental_freq=fundamental_freq,
            harmonics=harmonics,
            phase_shift=np.random.uniform(0, 2 * math.pi),
            amplitude=1.0,
        )

        self.memory_signatures[memory_id] = signature

        # Update resonance network
        self._update_resonance_network(memory_id)

        # Check for cluster formation
        self._check_cluster_formation(memory_id)

        logger.debug(
            "Memory registered for resonant access",
            memory_id=memory_id,
            fundamental_freq=fundamental_freq,
            harmonics=len(harmonics),
        )

        return memory_id

    def _extract_fundamental_frequency(self, content: Any) -> float:
        """Extract fundamental resonance frequency from content"""

        # Simple heuristic based on content characteristics
        content_str = str(content).lower()

        # Map content types to frequency bands
        if any(word in content_str for word in ["emotion", "feel", "love", "fear"]):
            return np.random.uniform(4, 8)  # Theta band (emotional)
        elif any(word in content_str for word in ["remember", "memory", "recall"]):
            return np.random.uniform(8, 12)  # Alpha band (memory)
        elif any(word in content_str for word in ["think", "analyze", "logic"]):
            return np.random.uniform(12, 30)  # Beta band (cognitive)
        elif any(word in content_str for word in ["insight", "creative", "dream"]):
            return np.random.uniform(30, 100)  # Gamma band (insight)
        else:
            # Default to gamma band with content-based variation
            content_hash = hash(content_str) % 1000
            return 40.0 + (content_hash / 1000.0) * 20  # 40-60 Hz

    def _generate_harmonics(self, fundamental_freq: float) -> list[float]:
        """Generate harmonic overtones for fundamental frequency"""
        harmonics = []

        for i in range(2, self.max_harmonics + 2):
            harmonic = fundamental_freq * i
            # Add some natural variation
            harmonic += np.random.normal(0, 0.5)
            harmonics.append(harmonic)

        return harmonics

    async def resonant_retrieve(
        self,
        query_content: Any,
        mode: ResonanceMode = ResonanceMode.HARMONIC,
        max_cascade_depth: int = 3,
        return_limit: int = 10,
    ) -> list[tuple[str, float, dict[str, Any]]]:
        """
        Retrieve memories using resonant patterns.

        Returns list of (memory_id, resonance_score, metadata)
        """

        # Create query signature
        query_freq = self._extract_fundamental_frequency(query_content)
        query_harmonics = self._generate_harmonics(query_freq)

        query_signature = ResonanceSignature(
            memory_id="query",
            fundamental_freq=query_freq,
            harmonics=query_harmonics,
            amplitude=self.oscillation_amplitude,
            phase_shift=self.current_phase,
        )

        # Find direct resonances
        direct_resonances = []
        for memory_id, signature in self.memory_signatures.items():
            resonance_score = query_signature.calculate_resonance_with(signature)

            if resonance_score >= self.resonance_threshold:
                direct_resonances.append(
                    (
                        memory_id,
                        resonance_score,
                        {
                            "resonance_type": "direct",
                            "fundamental_match": abs(query_freq - signature.fundamental_freq) < 2.0,
                            "harmonic_matches": self._count_harmonic_matches(query_harmonics, signature.harmonics),
                        },
                    )
                )

        # Cascade resonance if requested
        cascaded_resonances = []
        if max_cascade_depth > 0 and mode in [
            ResonanceMode.SYMPATHETIC,
            ResonanceMode.EMERGENT,
        ]:
            cascaded_resonances = await self._cascade_resonance(
                direct_resonances, query_signature, depth=max_cascade_depth
            )

        # Combine and rank results
        all_resonances = direct_resonances + cascaded_resonances
        all_resonances.sort(key=lambda x: x[1], reverse=True)  # Sort by resonance score

        # Apply resonance mode filters
        filtered_resonances = self._apply_mode_filter(all_resonances, mode)

        # Update metrics
        self.total_resonances += len(all_resonances)
        if all_resonances:
            self.successful_retrievals += 1

        logger.debug(
            "Resonant retrieval completed",
            query_freq=query_freq,
            direct_matches=len(direct_resonances),
            cascaded_matches=len(cascaded_resonances),
            mode=mode.value,
        )

        return filtered_resonances[:return_limit]

    def _count_harmonic_matches(self, harmonics1: list[float], harmonics2: list[float]) -> int:
        """Count close harmonic frequency matches"""
        matches = 0
        for h1 in harmonics1:
            for h2 in harmonics2:
                if abs(h1 - h2) < 1.0:  # Within 1 Hz
                    matches += 1
        return matches

    async def _cascade_resonance(
        self,
        initial_resonances: list[tuple[str, float, dict[str, Any]]],
        query_signature: ResonanceSignature,
        depth: int,
        visited: Optional[set[str]] = None,
    ) -> list[tuple[str, float, dict[str, Any]]]:
        """Recursively find cascaded resonances"""

        if depth <= 0 or not initial_resonances:
            return []

        if visited is None:
            visited = set()

        cascaded = []

        for memory_id, _score, _metadata in initial_resonances:
            if memory_id in visited:
                continue

            visited.add(memory_id)

            # Find memories that resonate with this memory
            memory_signature = self.memory_signatures.get(memory_id)
            if not memory_signature:
                continue

            for other_id, other_signature in self.memory_signatures.items():
                if other_id in visited:
                    continue

                # Calculate cascaded resonance
                cascade_score = memory_signature.calculate_resonance_with(other_signature)

                if cascade_score >= self.resonance_threshold:
                    # Dampen cascaded score
                    dampened_score = cascade_score * (0.8 ** (4 - depth))

                    cascaded.append(
                        (
                            other_id,
                            dampened_score,
                            {
                                "resonance_type": "cascaded",
                                "cascade_depth": 4 - depth,
                                "cascade_source": memory_id,
                                "original_score": cascade_score,
                            },
                        )
                    )

        # Continue cascade
        if depth > 1:
            next_level = await self._cascade_resonance(cascaded, query_signature, depth - 1, visited)
            cascaded.extend(next_level)

        self.cascade_events += 1
        return cascaded

    def _apply_mode_filter(
        self, resonances: list[tuple[str, float, dict[str, Any]]], mode: ResonanceMode
    ) -> list[tuple[str, float, dict[str, Any]]]:
        """Apply resonance mode specific filtering"""

        if mode == ResonanceMode.HARMONIC:
            # Prefer harmonic matches
            return sorted(
                resonances,
                key=lambda x: (x[2].get("harmonic_matches", 0), x[1]),
                reverse=True,
            )

        elif mode == ResonanceMode.SYMPATHETIC:
            # Prefer cascaded resonances
            return [r for r in resonances if r[2].get("resonance_type") == "cascaded"]

        elif mode == ResonanceMode.COHERENT:
            # Prefer cluster-based matches
            coherent = []
            for memory_id, score, metadata in resonances:
                if self._is_in_coherent_cluster(memory_id):
                    coherent.append((memory_id, score * 1.2, metadata))  # Boost coherent memories
            return coherent

        elif mode == ResonanceMode.EMERGENT:
            # Prefer novel resonance patterns
            return [r for r in resonances if r[1] > 0.7]  # High resonance only

        else:  # CHAOTIC
            # Random selection with bias toward high resonance
            np.random.shuffle(resonances)
            return resonances

    def _is_in_coherent_cluster(self, memory_id: str) -> bool:
        """Check if memory is part of a coherent cluster"""
        for cluster in self.resonant_clusters.values():
            if any(sig.memory_id == memory_id for sig in cluster.member_signatures):
                return cluster.coherence_level >= self.cluster_coherence_threshold
        return False

    def _update_resonance_network(self, memory_id: str):
        """Update the resonance network connections"""
        signature = self.memory_signatures[memory_id]

        # Find all resonant connections
        for other_id, other_signature in self.memory_signatures.items():
            if other_id == memory_id:
                continue

            resonance = signature.calculate_resonance_with(other_signature)

            if resonance >= self.resonance_threshold:
                self.resonance_network[memory_id].add(other_id)
                self.resonance_network[other_id].add(memory_id)

    def _check_cluster_formation(self, memory_id: str):
        """Check if new memory should form or join a cluster"""
        signature = self.memory_signatures[memory_id]

        # Find potential cluster members
        potential_members = []
        for connected_id in self.resonance_network[memory_id]:
            connected_sig = self.memory_signatures[connected_id]
            resonance = signature.calculate_resonance_with(connected_sig)

            if resonance >= 0.7:  # High resonance threshold for clustering
                potential_members.append(connected_sig)

        if len(potential_members) >= 2:  # Need at least 3 total (including new memory)
            # Create new cluster
            cluster = ResonantCluster(
                center_frequency=signature.fundamental_freq,
                member_signatures=[signature, *potential_members],
            )
            cluster.update_coherence()

            if cluster.coherence_level >= self.cluster_coherence_threshold:
                self.resonant_clusters[cluster.cluster_id] = cluster

                self.cluster_emergence_history.append(
                    {
                        "cluster_id": cluster.cluster_id,
                        "emergence_time": time.time(),
                        "member_count": len(cluster.member_signatures),
                        "coherence": cluster.coherence_level,
                    }
                )

                logger.info(
                    "Resonant cluster formed",
                    cluster_id=cluster.cluster_id,
                    members=len(cluster.member_signatures),
                    coherence=cluster.coherence_level,
                )

    async def _oscillation_loop(self):
        """Background oscillation to drive resonance dynamics"""
        while self._running:
            # Update global phase
            self.current_phase = (self.current_phase + 0.1) % (2 * math.pi)

            # Update oscillation amplitude with natural variation
            self.oscillation_amplitude = 0.8 + 0.4 * math.sin(self.current_phase * 0.1)

            # Decay all signature amplitudes
            for signature in self.memory_signatures.values():
                signature.amplitude *= self.decay_factor
                signature.amplitude = max(0.1, signature.amplitude)  # Minimum amplitude

            await asyncio.sleep(0.1)  # 10 Hz update rate

    async def _maintenance_loop(self):
        """Background maintenance for cluster management"""
        while self._running:
            # Update cluster coherence
            for cluster in self.resonant_clusters.values():
                cluster.update_coherence()

            # Remove low-coherence clusters
            to_remove = [cid for cid, cluster in self.resonant_clusters.items() if cluster.coherence_level < 0.2]

            for cid in to_remove:
                del self.resonant_clusters[cid]
                logger.debug("Removed low-coherence cluster", cluster_id=cid)

            await asyncio.sleep(10)  # Every 10 seconds

    def get_resonance_stats(self) -> dict[str, Any]:
        """Get comprehensive resonance statistics"""

        avg_cluster_coherence = (
            np.mean([c.coherence_level for c in self.resonant_clusters.values()]) if self.resonant_clusters else 0.0
        )

        network_density = sum(len(connections) for connections in self.resonance_network.values()) / 2
        network_density /= max(1, len(self.memory_signatures))

        return {
            "registered_memories": len(self.memory_signatures),
            "total_resonances": self.total_resonances,
            "successful_retrievals": self.successful_retrievals,
            "cascade_events": self.cascade_events,
            "active_clusters": len(self.resonant_clusters),
            "average_cluster_coherence": avg_cluster_coherence,
            "network_density": network_density,
            "current_phase": self.current_phase,
            "oscillation_amplitude": self.oscillation_amplitude,
        }


# Example usage
async def demonstrate_resonant_memory():
    """Demonstrate resonant memory access"""

    # Create resonant memory system
    resonant_memory = ResonantMemoryAccess(base_frequency=40.0, resonance_threshold=0.3, max_harmonics=4)

    await resonant_memory.start()

    print("🎵 RESONANT MEMORY ACCESS DEMONSTRATION")
    print("=" * 60)

    # Register some test memories
    test_memories = [
        ("mem_1", {"content": "I feel happy when I see sunlight", "emotion": "joy"}),
        (
            "mem_2",
            {"content": "The sunset was beautiful yesterday", "visual": "colors"},
        ),
        ("mem_3", {"content": "Remembering my childhood home", "memory": "nostalgia"}),
        (
            "mem_4",
            {
                "content": "Creative insight about colors and light",
                "insight": "connection",
            },
        ),
        ("mem_5", {"content": "Fear of the dark stormy night", "emotion": "fear"}),
    ]

    print("\n1. Registering memories...")
    for mem_id, content in test_memories:
        resonant_memory.register_memory(mem_id, content)
        print(f"   ✓ {mem_id}: {content['content'][:30]}...")

    # Wait for resonance network to stabilize
    await asyncio.sleep(1.0)

    # Test resonant retrieval
    print("\n2. Resonant retrieval tests...")

    test_queries = [
        ("Light and happiness", ResonanceMode.HARMONIC),
        ("Emotional memories", ResonanceMode.SYMPATHETIC),
        ("Visual experiences", ResonanceMode.COHERENT),
    ]

    for query, mode in test_queries:
        print(f"\n   Query: '{query}' (mode: {mode.value})")

        results = await resonant_memory.resonant_retrieve(
            query_content={"content": query},
            mode=mode,
            max_cascade_depth=2,
            return_limit=3,
        )

        for i, (mem_id, score, metadata) in enumerate(results, 1):
            print(f"   {i}. {mem_id} (resonance: {score:.3f}) - {metadata.get('resonance_type', 'unknown')}")

    # Show statistics
    print("\n3. Resonance Statistics:")
    stats = resonant_memory.get_resonance_stats()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.3f}")
        else:
            print(f"   {key}: {value}")

    await resonant_memory.stop()


if __name__ == "__main__":
    asyncio.run(demonstrate_resonant_memory())
