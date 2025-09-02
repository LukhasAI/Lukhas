#!/usr/bin/env python3
"""
Resonance-Based Memory Retrieval System
Context-aware memory access through frequency alignment and emotional resonance
"""

import hashlib
import json
import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

try:
    pass

    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False


@dataclass
class EmotionalState:
    """Emotional state representation for resonance matching"""

    valence: float  # -1.0 (negative) to 1.0 (positive)
    arousal: float  # 0.0 (calm) to 1.0 (excited)
    dominance: float  # 0.0 (submissive) to 1.0 (dominant)
    stress_level: float  # 0.0 (relaxed) to 1.0 (stressed)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class FrequencyFingerprint:
    """Frequency fingerprint for emotional state"""

    frequencies: list[float]
    amplitudes: list[float]
    phase_shifts: list[float]
    dominant_frequency: float
    bandwidth: float
    energy: float


@dataclass
class ResonantMemory:
    """Memory with frequency-based resonance properties"""

    memory_id: str
    data: Any
    frequency_signature: FrequencyFingerprint
    emotional_state: EmotionalState
    creation_time: datetime
    access_count: int = 0
    last_accessed: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    decay_factor: float = 1.0
    resonance_strength: float = 1.0


class FrequencyGenerator:
    """Generate frequency signatures from emotional states"""

    @staticmethod
    def emotional_state_to_frequency(emotional_state: EmotionalState) -> list[float]:
        """Convert emotional state to frequency spectrum"""
        # Base frequency mapping
        base_freq = 440.0  # A4 as reference

        # Map emotional dimensions to frequency components
        valence_freq = base_freq * (1 + emotional_state.valence * 0.5)  # 330-660 Hz
        arousal_freq = base_freq * (0.5 + emotional_state.arousal * 1.5)  # 220-880 Hz
        dominance_freq = base_freq * (0.25 + emotional_state.dominance * 0.75)  # 110-550 Hz
        stress_freq = base_freq * (2 + emotional_state.stress_level * 2)  # 880-1760 Hz

        # Create harmonic series
        frequencies = [
            valence_freq,
            arousal_freq,
            dominance_freq,
            stress_freq,
            valence_freq * 2,  # First harmonic
            arousal_freq * 1.5,  # Subharmonic
            base_freq / (1 + emotional_state.stress_level),  # Stress-modulated base
        ]

        return frequencies

    @staticmethod
    def generate_frequency_fingerprint(
        emotional_state: EmotionalState,
    ) -> FrequencyFingerprint:
        """Generate comprehensive frequency fingerprint"""
        frequencies = FrequencyGenerator.emotional_state_to_frequency(emotional_state)

        # Calculate amplitudes based on emotional intensity
        base_amplitude = 1.0
        amplitudes = []

        for i, _freq in enumerate(frequencies):
            # Amplitude varies with emotional dimensions
            if i == 0:  # Valence component
                amp = base_amplitude * (0.5 + abs(emotional_state.valence) * 0.5)
            elif i == 1:  # Arousal component
                amp = base_amplitude * (0.3 + emotional_state.arousal * 0.7)
            elif i == 2:  # Dominance component
                amp = base_amplitude * (0.4 + emotional_state.dominance * 0.6)
            elif i == 3:  # Stress component
                amp = base_amplitude * (0.2 + emotional_state.stress_level * 0.8)
            else:  # Harmonics
                amp = base_amplitude * (0.6 - i * 0.1)

            amplitudes.append(max(0.1, amp))

        # Calculate phase shifts based on emotional coherence
        phase_shifts = []
        for i, _freq in enumerate(frequencies):
            # Phase relates to emotional synchronization
            coherence = 1.0 - emotional_state.stress_level * 0.5
            phase = (i * math.pi / 4) * coherence
            phase_shifts.append(phase)

        # Find dominant frequency (highest amplitude)
        dominant_idx = amplitudes.index(max(amplitudes))
        dominant_frequency = frequencies[dominant_idx]

        # Calculate bandwidth (frequency spread)
        min_freq, max_freq = min(frequencies), max(frequencies)
        bandwidth = max_freq - min_freq

        # Calculate total energy
        energy = sum(amp**2 for amp in amplitudes)

        return FrequencyFingerprint(
            frequencies=frequencies,
            amplitudes=amplitudes,
            phase_shifts=phase_shifts,
            dominant_frequency=dominant_frequency,
            bandwidth=bandwidth,
            energy=energy,
        )


class ResonanceCalculator:
    """Calculate resonance similarity between frequency fingerprints"""

    @staticmethod
    def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if not vec1 or not vec2:
            return 0.0

        # Ensure equal length by padding or truncating
        max_len = max(len(vec1), len(vec2))
        vec1_padded = vec1 + [0.0] * (max_len - len(vec1))
        vec2_padded = vec2 + [0.0] * (max_len - len(vec2))

        # Calculate dot product
        dot_product = sum(a * b for a, b in zip(vec1_padded, vec2_padded))

        # Calculate magnitudes
        mag1 = math.sqrt(sum(a**2 for a in vec1_padded))
        mag2 = math.sqrt(sum(b**2 for b in vec2_padded))

        if mag1 == 0 or mag2 == 0:
            return 0.0

        return dot_product / (mag1 * mag2)

    @staticmethod
    def frequency_resonance(fp1: FrequencyFingerprint, fp2: FrequencyFingerprint) -> float:
        """Calculate frequency-based resonance between fingerprints"""
        # Frequency similarity
        freq_similarity = ResonanceCalculator.cosine_similarity(fp1.frequencies, fp2.frequencies)

        # Amplitude similarity
        amp_similarity = ResonanceCalculator.cosine_similarity(fp1.amplitudes, fp2.amplitudes)

        # Phase coherence
        phase_diff = sum(abs(p1 - p2) for p1, p2 in zip(fp1.phase_shifts, fp2.phase_shifts))
        phase_coherence = 1.0 / (1.0 + phase_diff / math.pi)

        # Dominant frequency alignment
        dominant_diff = abs(fp1.dominant_frequency - fp2.dominant_frequency)
        dominant_alignment = 1.0 / (1.0 + dominant_diff / 100.0)  # 100 Hz tolerance

        # Bandwidth compatibility
        bandwidth_ratio = min(fp1.bandwidth, fp2.bandwidth) / max(fp1.bandwidth, fp2.bandwidth)

        # Energy level similarity
        energy_ratio = min(fp1.energy, fp2.energy) / max(fp1.energy, fp2.energy)

        # Weighted combination
        weights = [0.25, 0.2, 0.15, 0.2, 0.1, 0.1]
        components = [
            freq_similarity,
            amp_similarity,
            phase_coherence,
            dominant_alignment,
            bandwidth_ratio,
            energy_ratio,
        ]

        resonance_score = sum(w * c for w, c in zip(weights, components))

        return min(1.0, max(0.0, resonance_score))

    @staticmethod
    def temporal_decay(creation_time: datetime, current_time: datetime, half_life_hours: float = 24.0) -> float:
        """Calculate temporal decay factor for memory resonance"""
        time_diff = (current_time - creation_time).total_seconds() / 3600  # hours
        decay_factor = math.exp(-math.log(2) * time_diff / half_life_hours)
        return decay_factor

    @staticmethod
    def access_boost(access_count: int, last_accessed: datetime, current_time: datetime) -> float:
        """Calculate access-based boost for frequently accessed memories"""
        # Base boost from access count
        access_boost = math.log(1 + access_count) / 10  # Logarithmic scaling

        # Recent access bonus
        hours_since_access = (current_time - last_accessed).total_seconds() / 3600
        recency_bonus = math.exp(-hours_since_access / 24) * 0.2  # 24-hour decay

        return min(0.5, access_boost + recency_bonus)  # Cap at 50% boost


class ResonanceGate:
    """Main resonance-based memory retrieval system"""

    def __init__(self, resonance_threshold: float = 0.85, max_memories: int = 1000):
        self.frequency_memory_map: dict[str, ResonantMemory] = {}
        self.resonance_threshold = resonance_threshold
        self.max_memories = max_memories
        self.access_log: list[dict[str, Any]] = []

    def store_memory_with_frequency(
        self,
        memory_data: Any,
        emotional_state: EmotionalState,
        metadata: Optional[dict[str, Any]] = None,
    ) -> str:
        """Store memory linked to emotional frequency signature"""

        # Generate frequency fingerprint
        freq_fingerprint = FrequencyGenerator.generate_frequency_fingerprint(emotional_state)

        # Create memory ID
        memory_content = json.dumps(memory_data) if not isinstance(memory_data, str) else memory_data
        memory_id = hashlib.sha3_256((memory_content + str(datetime.now())).encode()).hexdigest()[:16]

        # Create resonant memory
        resonant_memory = ResonantMemory(
            memory_id=memory_id,
            data=memory_data,
            frequency_signature=freq_fingerprint,
            emotional_state=emotional_state,
            creation_time=datetime.now(timezone.utc),
        )

        # Store memory
        self.frequency_memory_map[memory_id] = resonant_memory

        # Enforce memory limit
        if len(self.frequency_memory_map) > self.max_memories:
            self._evict_oldest_memory()

        # Log storage event
        self.access_log.append(
            {
                "event": "memory_stored",
                "memory_id": memory_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "emotional_state": {
                    "valence": emotional_state.valence,
                    "arousal": emotional_state.arousal,
                    "dominance": emotional_state.dominance,
                    "stress_level": emotional_state.stress_level,
                },
                "metadata": metadata or {},
            }
        )

        return memory_id

    def _evict_oldest_memory(self) -> None:
        """Evict the oldest, least accessed memory"""
        if not self.frequency_memory_map:
            return

        # Find memory with lowest combined score (age + access)
        current_time = datetime.now(timezone.utc)
        lowest_score = float("inf")
        memory_to_evict = None

        for memory_id, memory in self.frequency_memory_map.items():
            # Score based on age and access
            age_hours = (current_time - memory.creation_time).total_seconds() / 3600
            access_score = math.log(1 + memory.access_count)
            combined_score = access_score - (age_hours / 24)  # Favor recent and accessed

            if combined_score < lowest_score:
                lowest_score = combined_score
                memory_to_evict = memory_id

        if memory_to_evict:
            del self.frequency_memory_map[memory_to_evict]

            self.access_log.append(
                {
                    "event": "memory_evicted",
                    "memory_id": memory_to_evict,
                    "timestamp": current_time.isoformat(),
                    "reason": "memory_limit_exceeded",
                }
            )

    def retrieve_by_resonance(
        self,
        current_emotional_state: EmotionalState,
        limit: int = 10,
        include_scores: bool = False,
    ) -> list[dict[str, Any]]:
        """Retrieve memories that resonate with current emotional state"""

        current_time = datetime.now(timezone.utc)
        current_fingerprint = FrequencyGenerator.generate_frequency_fingerprint(current_emotional_state)

        resonant_memories = []

        for memory_id, memory in self.frequency_memory_map.items():
            # Calculate base resonance
            base_resonance = ResonanceCalculator.frequency_resonance(current_fingerprint, memory.frequency_signature)

            # Apply temporal decay
            temporal_factor = ResonanceCalculator.temporal_decay(memory.creation_time, current_time)

            # Apply access boost
            access_factor = ResonanceCalculator.access_boost(memory.access_count, memory.last_accessed, current_time)

            # Calculate final resonance score
            final_resonance = base_resonance * temporal_factor + access_factor
            final_resonance = min(1.0, final_resonance)  # Cap at 1.0

            if final_resonance >= self.resonance_threshold:
                memory_info = {
                    "memory_id": memory_id,
                    "data": memory.data,
                    "resonance_score": final_resonance,
                    "creation_time": memory.creation_time.isoformat(),
                    "access_count": memory.access_count,
                    "emotional_context": {
                        "valence": memory.emotional_state.valence,
                        "arousal": memory.emotional_state.arousal,
                        "dominance": memory.emotional_state.dominance,
                        "stress_level": memory.emotional_state.stress_level,
                    },
                }

                if include_scores:
                    memory_info["detailed_scores"] = {
                        "base_resonance": base_resonance,
                        "temporal_factor": temporal_factor,
                        "access_factor": access_factor,
                    }

                resonant_memories.append(memory_info)

                # Update access statistics
                memory.access_count += 1
                memory.last_accessed = current_time

        # Sort by resonance score and limit results
        resonant_memories.sort(key=lambda x: x["resonance_score"], reverse=True)
        limited_results = resonant_memories[:limit]

        # Log retrieval event
        self.access_log.append(
            {
                "event": "memory_retrieval",
                "query_emotional_state": {
                    "valence": current_emotional_state.valence,
                    "arousal": current_emotional_state.arousal,
                    "dominance": current_emotional_state.dominance,
                    "stress_level": current_emotional_state.stress_level,
                },
                "results_count": len(limited_results),
                "threshold": self.resonance_threshold,
                "timestamp": current_time.isoformat(),
            }
        )

        return limited_results

    def update_memory_resonance(self, memory_id: str, new_emotional_state: EmotionalState) -> bool:
        """Update the emotional resonance of an existing memory"""
        if memory_id not in self.frequency_memory_map:
            return False

        memory = self.frequency_memory_map[memory_id]

        # Generate new frequency fingerprint
        new_fingerprint = FrequencyGenerator.generate_frequency_fingerprint(new_emotional_state)

        # Update memory
        memory.frequency_signature = new_fingerprint
        memory.emotional_state = new_emotional_state
        memory.last_accessed = datetime.now(timezone.utc)

        # Log update
        self.access_log.append(
            {
                "event": "memory_updated",
                "memory_id": memory_id,
                "new_emotional_state": {
                    "valence": new_emotional_state.valence,
                    "arousal": new_emotional_state.arousal,
                    "dominance": new_emotional_state.dominance,
                    "stress_level": new_emotional_state.stress_level,
                },
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

        return True

    def get_memory_by_id(self, memory_id: str) -> Optional[dict[str, Any]]:
        """Retrieve specific memory by ID"""
        if memory_id not in self.frequency_memory_map:
            return None

        memory = self.frequency_memory_map[memory_id]
        memory.access_count += 1
        memory.last_accessed = datetime.now(timezone.utc)

        return {
            "memory_id": memory_id,
            "data": memory.data,
            "creation_time": memory.creation_time.isoformat(),
            "access_count": memory.access_count,
            "last_accessed": memory.last_accessed.isoformat(),
            "emotional_context": {
                "valence": memory.emotional_state.valence,
                "arousal": memory.emotional_state.arousal,
                "dominance": memory.emotional_state.dominance,
                "stress_level": memory.emotional_state.stress_level,
            },
            "frequency_info": {
                "dominant_frequency": memory.frequency_signature.dominant_frequency,
                "bandwidth": memory.frequency_signature.bandwidth,
                "energy": memory.frequency_signature.energy,
            },
        }

    def analyze_resonance_patterns(self) -> dict[str, Any]:
        """Analyze patterns in memory resonance and access"""
        if not self.frequency_memory_map:
            return {"error": "No memories available for analysis"}

        memories = list(self.frequency_memory_map.values())

        # Emotional distribution analysis
        valences = [m.emotional_state.valence for m in memories]
        arousals = [m.emotional_state.arousal for m in memories]
        dominances = [m.emotional_state.dominance for m in memories]
        stress_levels = [m.emotional_state.stress_level for m in memories]

        # Frequency analysis
        dominant_freqs = [m.frequency_signature.dominant_frequency for m in memories]
        bandwidths = [m.frequency_signature.bandwidth for m in memories]
        energies = [m.frequency_signature.energy for m in memories]

        # Access pattern analysis
        access_counts = [m.access_count for m in memories]

        # Recent activity (last 24 hours)
        recent_threshold = datetime.now(timezone.utc) - timedelta(hours=24)
        recent_activity = sum(1 for m in memories if m.last_accessed > recent_threshold)

        analysis = {
            "memory_count": len(memories),
            "emotional_distributions": {
                "valence": {
                    "min": min(valences),
                    "max": max(valences),
                    "avg": sum(valences) / len(valences),
                },
                "arousal": {
                    "min": min(arousals),
                    "max": max(arousals),
                    "avg": sum(arousals) / len(arousals),
                },
                "dominance": {
                    "min": min(dominances),
                    "max": max(dominances),
                    "avg": sum(dominances) / len(dominances),
                },
                "stress": {
                    "min": min(stress_levels),
                    "max": max(stress_levels),
                    "avg": sum(stress_levels) / len(stress_levels),
                },
            },
            "frequency_distributions": {
                "dominant_frequency": {
                    "min": min(dominant_freqs),
                    "max": max(dominant_freqs),
                    "avg": sum(dominant_freqs) / len(dominant_freqs),
                },
                "bandwidth": {
                    "min": min(bandwidths),
                    "max": max(bandwidths),
                    "avg": sum(bandwidths) / len(bandwidths),
                },
                "energy": {
                    "min": min(energies),
                    "max": max(energies),
                    "avg": sum(energies) / len(energies),
                },
            },
            "access_patterns": {
                "total_accesses": sum(access_counts),
                "avg_access_count": sum(access_counts) / len(access_counts),
                "most_accessed": max(access_counts),
                "recent_activity": recent_activity,
            },
            "system_stats": {
                "resonance_threshold": self.resonance_threshold,
                "max_memories": self.max_memories,
                "memory_utilization": len(memories) / self.max_memories,
                "total_events": len(self.access_log),
            },
            "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
        }

        return analysis

    def get_system_health(self) -> dict[str, Any]:
        """Get overall system health metrics"""
        current_time = datetime.now(timezone.utc)

        # Memory metrics
        total_memories = len(self.frequency_memory_map)
        utilization = total_memories / self.max_memories

        # Activity metrics (last hour)
        recent_events = [
            log
            for log in self.access_log
            if datetime.fromisoformat(log["timestamp"].replace("Z", "+00:00")) > current_time - timedelta(hours=1)
        ]

        # Performance metrics
        avg_resonance = 0.0
        if self.frequency_memory_map:
            # Estimate average resonance by sampling
            sample_state = EmotionalState(valence=0, arousal=0.5, dominance=0.5, stress_level=0.3)
            sample_results = self.retrieve_by_resonance(sample_state, limit=5, include_scores=True)
            if sample_results:
                avg_resonance = sum(r["resonance_score"] for r in sample_results) / len(sample_results)

        health = {
            "status": ("healthy" if utilization < 0.9 else "near_capacity" if utilization < 1.0 else "at_capacity"),
            "memory_utilization": utilization,
            "total_memories": total_memories,
            "recent_activity": len(recent_events),
            "avg_resonance_quality": avg_resonance,
            "system_uptime": "active",  # Simplified for demo
            "resonance_threshold": self.resonance_threshold,
            "health_check_timestamp": current_time.isoformat(),
        }

        return health


# Example usage and testing
if __name__ == "__main__":

    def demo_resonance_system():
        """Demonstrate the resonance-based memory retrieval system"""
        print("🧠 Initializing Resonance-Based Memory Retrieval System...")
        resonance_gate = ResonanceGate(resonance_threshold=0.6, max_memories=50)

        # Create test emotional states and memories
        test_memories = [
            {
                "data": "Successfully completed important project deadline",
                "emotional_state": EmotionalState(valence=0.8, arousal=0.6, dominance=0.7, stress_level=0.3),
            },
            {
                "data": "Had a stressful meeting with difficult client",
                "emotional_state": EmotionalState(valence=-0.4, arousal=0.8, dominance=0.3, stress_level=0.9),
            },
            {
                "data": "Enjoyed relaxing weekend with family",
                "emotional_state": EmotionalState(valence=0.7, arousal=0.2, dominance=0.6, stress_level=0.1),
            },
            {
                "data": "Learned new programming technique",
                "emotional_state": EmotionalState(valence=0.5, arousal=0.7, dominance=0.8, stress_level=0.2),
            },
            {
                "data": "Received positive feedback from supervisor",
                "emotional_state": EmotionalState(valence=0.9, arousal=0.5, dominance=0.6, stress_level=0.1),
            },
        ]

        print(f"\n📝 Storing {len(test_memories)} test memories...")
        memory_ids = []

        for i, memory_data in enumerate(test_memories):
            memory_id = resonance_gate.store_memory_with_frequency(
                memory_data["data"],
                memory_data["emotional_state"],
                {"category": f"test_memory_{i + 1}"},
            )
            memory_ids.append(memory_id)

            print(f"  📦 Stored: {memory_id} - {memory_data['data'][:30]}...")

        # Test resonance-based retrieval with different emotional states
        print("\n🔍 Testing resonance-based retrieval...")

        test_queries = [
            {
                "name": "Happy/Positive State",
                "state": EmotionalState(valence=0.8, arousal=0.5, dominance=0.7, stress_level=0.2),
            },
            {
                "name": "Stressed/Negative State",
                "state": EmotionalState(valence=-0.3, arousal=0.9, dominance=0.4, stress_level=0.8),
            },
            {
                "name": "Calm/Relaxed State",
                "state": EmotionalState(valence=0.6, arousal=0.2, dominance=0.5, stress_level=0.1),
            },
        ]

        for query in test_queries:
            print(f"\n🎯 Query: {query['name']}")
            print(
                f"   State: v={query['state'].valence:.1f}, a={query['state'].arousal:.1f}, d={query['state'].dominance:.1f}, s={query['state'].stress_level:.1f}"
            )

            results = resonance_gate.retrieve_by_resonance(query["state"], limit=3, include_scores=True)

            if results:
                print(f"   📊 Found {len(results)} resonant memories:")
                for result in results:
                    data_preview = (
                        str(result["data"])[:40] + "..." if len(str(result["data"])) > 40 else str(result["data"])
                    )
                    print(f"     • {result['resonance_score']:.3f}: {data_preview}")
                    if "detailed_scores" in result:
                        scores = result["detailed_scores"]
                        print(
                            f"       (base: {scores['base_resonance']:.3f}, temporal: {scores['temporal_factor']:.3f}, access: {scores['access_factor']:.3f})"
                        )
            else:
                print(f"   ❌ No memories found above threshold ({resonance_gate.resonance_threshold})")

        # Test memory access by ID
        print("\n🔍 Testing direct memory access...")
        if memory_ids:
            test_memory = resonance_gate.get_memory_by_id(memory_ids[0])
            if test_memory:
                print(f"   📖 Memory: {test_memory['data']}")
                print(f"   📊 Access count: {test_memory['access_count']}")
                print(f"   🎵 Dominant frequency: {test_memory['frequency_info']['dominant_frequency']:.1f} Hz")

        # Analyze patterns
        print("\n📈 Analyzing resonance patterns...")
        analysis = resonance_gate.analyze_resonance_patterns()

        if "error" not in analysis:
            print(f"   📊 Total memories: {analysis['memory_count']}")
            print(f"   😊 Avg valence: {analysis['emotional_distributions']['valence']['avg']:.2f}")
            print(f"   ⚡ Avg arousal: {analysis['emotional_distributions']['arousal']['avg']:.2f}")
            print(f"   🎵 Avg frequency: {analysis['frequency_distributions']['dominant_frequency']['avg']:.1f} Hz")
            print(f"   👁️ Total accesses: {analysis['access_patterns']['total_accesses']}")

        # System health check
        print("\n🏥 System health check...")
        health = resonance_gate.get_system_health()
        print(f"   Status: {health['status']}")
        print(f"   Memory utilization: {health['memory_utilization']:.1%}")
        print(f"   Recent activity: {health['recent_activity']} events")
        print(f"   Avg resonance quality: {health['avg_resonance_quality']:.3f}")

        return resonance_gate, memory_ids, analysis

    # Run the demo
    gate_system, demo_memory_ids, pattern_analysis = demo_resonance_system()
    print("\n✅ Resonance-based memory retrieval demonstration complete!")
