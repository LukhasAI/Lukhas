"""
Dream Memory Bridge for Cognitive AI Enhanced Memory

Integrates dream system with memory architecture for creative consolidation,
pattern discovery, and insight generation through dream-enhanced memory processing.
"""

import asyncio
import logging
import random
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

import numpy as np

from .vector_memory import MemoryImportance, MemoryType, MemoryVector, VectorMemoryStore

logger = logging.getLogger(__name__)


class DreamPhase(Enum):
    """Dream phases for memory processing."""

    EXPLORATION = "exploration"  # Explore memory connections
    SYNTHESIS = "synthesis"  # Synthesize patterns and insights
    CONSOLIDATION = "consolidation"  # Consolidate and strengthen memories
    CREATIVITY = "creativity"  # Generate creative associations
    INTEGRATION = "integration"  # Integrate new insights with existing knowledge


class DreamInsightType(Enum):
    """Types of dream-generated insights."""

    PATTERN_DISCOVERY = "pattern_discovery"  # Discovered hidden patterns
    CREATIVE_CONNECTION = "creative_connection"  # Novel associations
    EMOTIONAL_SYNTHESIS = "emotional_synthesis"  # Emotional meaning integration
    CAUSAL_INSIGHT = "causal_insight"  # Causal relationship discovery
    CONCEPTUAL_BRIDGE = "conceptual_bridge"  # Bridging different concepts
    TEMPORAL_PATTERN = "temporal_pattern"  # Time-based patterns


@dataclass
class DreamMemoryPattern:
    """Pattern discovered during dream processing."""

    pattern_id: str
    pattern_type: DreamInsightType
    memory_ids: list[str]  # Memories involved in this pattern
    confidence: float  # Confidence in pattern validity
    insight_content: str  # Human-readable description
    vector_signature: Optional[np.ndarray] = None  # Vector representation of pattern
    emotional_tone: Optional[float] = None  # Emotional valence of pattern
    constellation_alignment: dict[str, float] = field(default_factory=dict)
    discovery_time: datetime = field(default_factory=datetime.now)

    def get_pattern_strength(self) -> float:
        """Calculate overall pattern strength."""
        base_strength = self.confidence

        # Boost for multiple memories
        memory_boost = min(0.3, len(self.memory_ids) * 0.05)

        # Boost for strong constellation alignment
        constellation_boost = max(self.constellation_alignment.values()) * 0.2 if self.constellation_alignment else 0.0

        return min(1.0, base_strength + memory_boost + constellation_boost)


@dataclass
class DreamSession:
    """Dream processing session for memory consolidation."""

    session_id: str
    phase: DreamPhase
    target_memories: list[str]
    patterns_discovered: list[DreamMemoryPattern]
    insights_generated: list[dict[str, Any]]
    processing_time_ms: int
    success: bool
    error_message: Optional[str] = None


class DreamMemoryBridge:
    """
    Dream Memory Bridge for Cognitive AI Memory Enhancement

    Provides dream-enhanced memory processing that integrates with LUKHAS
    dream system for creative memory consolidation and insight generation.
    """

    def __init__(self, memory_store: VectorMemoryStore):
        self.memory_store = memory_store
        self.dream_sessions: list[DreamSession] = []
        self.discovered_patterns: dict[str, DreamMemoryPattern] = {}

        # Dream Processing Parameters
        self.exploration_depth = 3  # How deep to explore memory connections
        self.pattern_threshold = 0.7  # Threshold for pattern recognition
        self.creativity_factor = 0.3  # How much to encourage creative connections
        self.dream_vocabulary = self._load_dream_vocabulary()

        # Statistics
        self.stats = {
            "total_dream_sessions": 0,
            "patterns_discovered": 0,
            "insights_generated": 0,
            "avg_session_time": 0.0,
            "pattern_types": {dt.value: 0 for dt in DreamInsightType},
        }

    def _load_dream_vocabulary(self) -> dict[str, Any]:
        """Load dream vocabulary for pattern interpretation."""
        # This would normally load from the LUKHAS dream vocabulary
        # For now, we'll create a simplified version
        return {
            "phases": ["emergence", "drift", "synthesis", "integration", "reflection"],
            "patterns": ["spiral", "cascade", "resonance", "bridge", "vortex"],
            "emotions": ["wonder", "curiosity", "insight", "connection", "transcendence"],
            "symbols": ["light", "flow", "network", "constellation", "transformation"],
        }

    async def initiate_dream_session(
        self,
        target_memories: Optional[list[str]] = None,
        phase: DreamPhase = DreamPhase.EXPLORATION,
        session_params: Optional[dict[str, Any]] = None,
    ) -> str:
        """
        Initiate a dream processing session for memory enhancement.

        Args:
            target_memories: Specific memories to process (None for auto-selection)
            phase: Dream phase to execute
            session_params: Additional parameters for dream processing

        Returns:
            Session ID for tracking
        """
        session_id = f"dream_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{len(self.dream_sessions)}"
        start_time = asyncio.get_event_loop().time()

        # Auto-select memories if not provided
        if target_memories is None:
            target_memories = await self._select_dream_targets()

        # Filter to valid memory IDs
        valid_memories = [mid for mid in target_memories if mid in self.memory_store.memories]

        session = DreamSession(
            session_id=session_id,
            phase=phase,
            target_memories=valid_memories,
            patterns_discovered=[],
            insights_generated=[],
            processing_time_ms=0,
            success=False,
        )

        try:
            # Execute dream phase
            if phase == DreamPhase.EXPLORATION:
                await self._dream_exploration(session, session_params or {})
            elif phase == DreamPhase.SYNTHESIS:
                await self._dream_synthesis(session, session_params or {})
            elif phase == DreamPhase.CONSOLIDATION:
                await self._dream_consolidation(session, session_params or {})
            elif phase == DreamPhase.CREATIVITY:
                await self._dream_creativity(session, session_params or {})
            elif phase == DreamPhase.INTEGRATION:
                await self._dream_integration(session, session_params or {})

            session.success = True

            # Store discovered patterns
            for pattern in session.patterns_discovered:
                self.discovered_patterns[pattern.pattern_id] = pattern

            # Update statistics
            self.stats["total_dream_sessions"] += 1
            self.stats["patterns_discovered"] += len(session.patterns_discovered)
            self.stats["insights_generated"] += len(session.insights_generated)

            for pattern in session.patterns_discovered:
                self.stats["pattern_types"][pattern.pattern_type.value] += 1

        except Exception as e:
            session.success = False
            session.error_message = str(e)
            logger.error(f"Dream session {session_id} failed: {e}")

        finally:
            processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
            session.processing_time_ms = int(processing_time)

            # Update average session time
            total_sessions = self.stats["total_dream_sessions"]
            if total_sessions > 0:
                self.stats["avg_session_time"] = (
                    self.stats["avg_session_time"] * (total_sessions - 1) + processing_time
                ) / total_sessions

        self.dream_sessions.append(session)
        logger.info(f"Dream session {session_id} completed: {session.success}")

        return session_id

    async def _select_dream_targets(self) -> list[str]:
        """Automatically select memories for dream processing."""
        candidates = []
        now = datetime.now(timezone.utc)

        # Select recent memories with interesting characteristics
        for memory_id, memory in self.memory_store.memories.items():
            # Recent memories (last 7 days)
            if (now - memory.timestamp).days <= 7:
                candidates.append((memory_id, self._calculate_dream_interest(memory)))

        # Sort by dream interest and take top candidates
        candidates.sort(key=lambda x: x[1], reverse=True)
        return [memory_id for memory_id, _ in candidates[:20]]  # Top 20 candidates

    def _calculate_dream_interest(self, memory: MemoryVector) -> float:
        """Calculate how interesting a memory is for dream processing."""
        interest = 0.0

        # High importance memories are more interesting
        interest += memory.importance.value / 5.0 * 0.3

        # Memories with emotional content are more interesting
        if memory.emotional_valence is not None:
            interest += abs(memory.emotional_valence) * 0.2

        # Memories with strong constellation alignment are interesting
        if memory.constellation_tags:
            max_alignment = max(memory.constellation_tags.values())
            interest += max_alignment * 0.2

        # Creative and contextual memories are very interesting for dreams
        if memory.memory_type in [MemoryType.CREATIVE, MemoryType.CONTEXTUAL, MemoryType.DREAM]:
            interest += 0.2

        # Add some randomness for exploration
        interest += random.random() * 0.1

        return min(1.0, interest)

    async def _dream_exploration(self, session: DreamSession, params: dict[str, Any]):
        """Explore memory connections and associations."""
        memories_to_explore = []
        for memory_id in session.target_memories:
            memory = await self.memory_store.get_memory(memory_id, reinforce=False)
            if memory:
                memories_to_explore.append(memory)

        # Explore associative networks
        for memory in memories_to_explore:
            # Get associative memories
            associated = await self.memory_store.get_associative_memories(memory.id, depth=self.exploration_depth)

            # Look for hidden patterns in associations
            if len(associated) >= 2:
                pattern = await self._discover_association_pattern(memory, associated)
                if pattern:
                    session.patterns_discovered.append(pattern)

        # Cross-memory exploration
        await self._explore_cross_memory_patterns(memories_to_explore, session)

    async def _dream_synthesis(self, session: DreamSession, params: dict[str, Any]):
        """Synthesize patterns and generate insights from memories."""
        target_memories = []
        for memory_id in session.target_memories:
            memory = await self.memory_store.get_memory(memory_id, reinforce=False)
            if memory:
                target_memories.append(memory)

        # Synthesize temporal patterns
        temporal_pattern = await self._synthesize_temporal_pattern(target_memories)
        if temporal_pattern:
            session.patterns_discovered.append(temporal_pattern)

        # Synthesize semantic clusters
        semantic_clusters = await self._synthesize_semantic_clusters(target_memories)
        for cluster_pattern in semantic_clusters:
            session.patterns_discovered.append(cluster_pattern)

        # Generate synthetic insights
        insights = await self._generate_synthetic_insights(target_memories, session.patterns_discovered)
        session.insights_generated.extend(insights)

    async def _dream_consolidation(self, session: DreamSession, params: dict[str, Any]):
        """Consolidate memories through dream processing."""
        # Strengthen memories that appear in multiple patterns
        memory_pattern_count = {}
        for pattern in session.patterns_discovered:
            for memory_id in pattern.memory_ids:
                memory_pattern_count[memory_id] = memory_pattern_count.get(memory_id, 0) + 1

        # Reinforce memories that are part of multiple patterns
        for memory_id, count in memory_pattern_count.items():
            if count > 1:
                memory = await self.memory_store.get_memory(memory_id, reinforce=False)
                if memory:
                    # Dream consolidation boost
                    boost = min(0.3, count * 0.1)
                    memory.reinforce(boost)
                    memory.constellation_tags["DREAM"] = min(1.0, memory.constellation_tags.get("DREAM", 0.0) + boost)

    async def _dream_creativity(self, session: DreamSession, params: dict[str, Any]):
        """Generate creative connections and novel associations."""
        target_memories = []
        for memory_id in session.target_memories:
            memory = await self.memory_store.get_memory(memory_id, reinforce=False)
            if memory:
                target_memories.append(memory)

        # Create unexpected associations
        for i, memory1 in enumerate(target_memories):
            for memory2 in target_memories[i + 1 :]:
                # Calculate semantic distance
                similarity = np.dot(memory1.vector, memory2.vector) / (
                    np.linalg.norm(memory1.vector) * np.linalg.norm(memory2.vector)
                )

                # Look for creative connections in moderately similar memories
                if 0.3 <= similarity <= 0.7:
                    creative_pattern = await self._create_creative_connection(memory1, memory2, similarity)
                    if creative_pattern:
                        session.patterns_discovered.append(creative_pattern)

        # Generate creative insights
        creative_insights = await self._generate_creative_insights(target_memories)
        session.insights_generated.extend(creative_insights)

    async def _dream_integration(self, session: DreamSession, params: dict[str, Any]):
        """Integrate dream insights with existing knowledge."""
        # Apply discovered patterns to enhance memory organization
        for pattern in session.patterns_discovered:
            await self._integrate_pattern_insights(pattern)

        # Create meta-memories about the dream session itself
        dream_meta_memory = await self._create_dream_meta_memory(session)
        if dream_meta_memory:
            await self.memory_store.add_memory(dream_meta_memory)

    async def _discover_association_pattern(
        self, central_memory: MemoryVector, associated_memories: list[MemoryVector]
    ) -> Optional[DreamMemoryPattern]:
        """Discover patterns in memory associations."""
        if len(associated_memories) < 2:
            return None

        # Analyze the constellation alignment patterns
        constellation_patterns = {}
        for memory in associated_memories:
            for star, alignment in memory.constellation_tags.items():
                if star not in constellation_patterns:
                    constellation_patterns[star] = []
                constellation_patterns[star].append(alignment)

        # Find strong constellation convergence
        strong_alignments = {}
        for star, alignments in constellation_patterns.items():
            if len(alignments) >= 2:
                avg_alignment = np.mean(alignments)
                if avg_alignment > 0.6:
                    strong_alignments[star] = avg_alignment

        if strong_alignments:
            pattern_id = f"assoc_{central_memory.id}_{datetime.now(timezone.utc).strftime('%H%M%S')}"

            return DreamMemoryPattern(
                pattern_id=pattern_id,
                pattern_type=DreamInsightType.PATTERN_DISCOVERY,
                memory_ids=[central_memory.id] + [m.id for m in associated_memories],
                confidence=max(strong_alignments.values()),
                insight_content=f"Constellation convergence pattern around {central_memory.content[:100]}...",
                constellation_alignment=strong_alignments,
            )

        return None

    async def _explore_cross_memory_patterns(self, memories: list[MemoryVector], session: DreamSession):
        """Explore patterns across multiple memories."""
        # Look for temporal cascades
        temporal_memories = sorted(memories, key=lambda m: m.timestamp)

        if len(temporal_memories) >= 3:
            # Check for temporal progression patterns
            time_diffs = []
            for i in range(len(temporal_memories) - 1):
                diff = (temporal_memories[i + 1].timestamp - temporal_memories[i].timestamp).total_seconds()
                time_diffs.append(diff)

            # Look for regular intervals or accelerating/decelerating patterns
            if len({int(diff / 3600) for diff in time_diffs}) <= 2:  # Similar intervals (within hours)
                pattern_id = f"temporal_{datetime.now(timezone.utc).strftime('%H%M%S')}"

                pattern = DreamMemoryPattern(
                    pattern_id=pattern_id,
                    pattern_type=DreamInsightType.TEMPORAL_PATTERN,
                    memory_ids=[m.id for m in temporal_memories],
                    confidence=0.8,
                    insight_content="Temporal cascade pattern with regular intervals",
                    constellation_alignment={"MEMORY": 0.8, "DREAM": 0.6},
                )

                session.patterns_discovered.append(pattern)

    async def _synthesize_temporal_pattern(self, memories: list[MemoryVector]) -> Optional[DreamMemoryPattern]:
        """Synthesize temporal patterns from memory sequence."""
        if len(memories) < 3:
            return None

        sorted_memories = sorted(memories, key=lambda m: m.timestamp)

        # Analyze emotional progression
        emotional_sequence = []
        for memory in sorted_memories:
            if memory.emotional_valence is not None:
                emotional_sequence.append(memory.emotional_valence)

        if len(emotional_sequence) >= 3:
            # Look for emotional narrative arc
            if emotional_sequence[0] < 0 and emotional_sequence[-1] > 0:
                # Negative to positive arc
                pattern_id = f"emotional_arc_{datetime.now(timezone.utc).strftime('%H%M%S')}"

                return DreamMemoryPattern(
                    pattern_id=pattern_id,
                    pattern_type=DreamInsightType.EMOTIONAL_SYNTHESIS,
                    memory_ids=[m.id for m in sorted_memories if m.emotional_valence is not None],
                    confidence=0.7,
                    insight_content="Emotional transformation arc: negative to positive",
                    emotional_tone=emotional_sequence[-1] - emotional_sequence[0],
                    constellation_alignment={"ETHICS": 0.7, "DREAM": 0.8},
                )

        return None

    async def _synthesize_semantic_clusters(self, memories: list[MemoryVector]) -> list[DreamMemoryPattern]:
        """Find semantic clusters in memories."""
        clusters = []

        # Simple clustering based on vector similarity
        for i, memory1 in enumerate(memories):
            cluster_members = [memory1]

            for memory2 in memories[i + 1 :]:
                similarity = np.dot(memory1.vector, memory2.vector) / (
                    np.linalg.norm(memory1.vector) * np.linalg.norm(memory2.vector)
                )

                if similarity > 0.8:  # High similarity threshold
                    cluster_members.append(memory2)

            if len(cluster_members) >= 2:
                pattern_id = f"cluster_{i}_{datetime.now(timezone.utc).strftime('%H%M%S')}"

                pattern = DreamMemoryPattern(
                    pattern_id=pattern_id,
                    pattern_type=DreamInsightType.PATTERN_DISCOVERY,
                    memory_ids=[m.id for m in cluster_members],
                    confidence=0.75,
                    insight_content=f"Semantic cluster around theme: {memory1.content[:50]}...",
                    constellation_alignment={"VISION": 0.7, "DREAM": 0.6},
                )

                clusters.append(pattern)

        return clusters

    async def _generate_synthetic_insights(
        self, memories: list[MemoryVector], patterns: list[DreamMemoryPattern]
    ) -> list[dict[str, Any]]:
        """Generate synthetic insights from memories and patterns."""
        insights = []

        # Generate insights from patterns
        for pattern in patterns:
            if pattern.pattern_type == DreamInsightType.EMOTIONAL_SYNTHESIS:
                insights.append(
                    {
                        "type": "emotional_insight",
                        "content": f"Dream reveals emotional journey: {pattern.insight_content}",
                        "confidence": pattern.confidence,
                        "pattern_id": pattern.pattern_id,
                    }
                )

            elif pattern.pattern_type == DreamInsightType.PATTERN_DISCOVERY:
                insights.append(
                    {
                        "type": "pattern_insight",
                        "content": f"Hidden pattern discovered: {pattern.insight_content}",
                        "confidence": pattern.confidence,
                        "pattern_id": pattern.pattern_id,
                    }
                )

        # Generate constellation insights
        constellation_summary = {}
        for memory in memories:
            for star, alignment in memory.constellation_tags.items():
                if star not in constellation_summary:
                    constellation_summary[star] = []
                constellation_summary[star].append(alignment)

        for star, alignments in constellation_summary.items():
            if len(alignments) >= 2:
                avg_alignment = np.mean(alignments)
                if avg_alignment > 0.7:
                    insights.append(
                        {
                            "type": "constellation_insight",
                            "content": f"Strong {star} constellation alignment in dream memories",
                            "confidence": avg_alignment,
                            "constellation": star,
                        }
                    )

        return insights

    async def _create_creative_connection(
        self, memory1: MemoryVector, memory2: MemoryVector, similarity: float
    ) -> Optional[DreamMemoryPattern]:
        """Create creative connections between moderately similar memories."""
        # Find bridging concepts using dream vocabulary
        bridge_concepts = []

        # Use dream vocabulary to find creative bridges
        for symbol in self.dream_vocabulary.get("symbols", []):
            if symbol in memory1.content.lower() or symbol in memory2.content.lower():
                bridge_concepts.append(symbol)

        if bridge_concepts or random.random() < self.creativity_factor:
            pattern_id = f"creative_{memory1.id[:8]}_{memory2.id[:8]}"

            bridge_description = ", ".join(bridge_concepts) if bridge_concepts else "intuitive connection"

            return DreamMemoryPattern(
                pattern_id=pattern_id,
                pattern_type=DreamInsightType.CREATIVE_CONNECTION,
                memory_ids=[memory1.id, memory2.id],
                confidence=similarity + 0.2,  # Boost for creativity
                insight_content=f"Creative bridge through {bridge_description}",
                constellation_alignment={"DREAM": 0.9, "QUANTUM": 0.7},
            )

        return None

    async def _generate_creative_insights(self, memories: list[MemoryVector]) -> list[dict[str, Any]]:
        """Generate creative insights from memories."""
        insights = []

        # Generate metaphorical connections
        for memory in memories:
            if memory.memory_type == MemoryType.CREATIVE:
                # Use dream vocabulary to generate metaphorical insights
                dream_symbols = random.sample(
                    self.dream_vocabulary.get("symbols", []), min(2, len(self.dream_vocabulary.get("symbols", [])))
                )

                insights.append(
                    {
                        "type": "metaphorical_insight",
                        "content": f"Memory resonates with dream symbols: {', '.join(dream_symbols)}",
                        "confidence": 0.6,
                        "memory_id": memory.id,
                        "symbols": dream_symbols,
                    }
                )

        return insights

    async def _integrate_pattern_insights(self, pattern: DreamMemoryPattern):
        """Integrate pattern insights into memory organization."""
        # Apply pattern insights to involved memories
        for memory_id in pattern.memory_ids:
            memory = await self.memory_store.get_memory(memory_id, reinforce=False)
            if memory:
                # Strengthen constellation alignments based on pattern
                for star, alignment in pattern.constellation_alignment.items():
                    current = memory.constellation_tags.get(star, 0.0)
                    memory.constellation_tags[star] = min(1.0, current + alignment * 0.1)

                # Add pattern reference
                if "dream_patterns" not in memory.__dict__:
                    memory.__dict__["dream_patterns"] = []
                memory.__dict__["dream_patterns"].append(pattern.pattern_id)

    async def _create_dream_meta_memory(self, session: DreamSession) -> Optional[MemoryVector]:
        """Create a meta-memory about the dream session."""
        if not session.success:
            return None

        # Create summary of dream session
        content = f"Dream session {session.session_id}: Phase {session.phase.value}. "
        content += f"Discovered {len(session.patterns_discovered)} patterns, "
        content += f"generated {len(session.insights_generated)} insights. "

        pattern_types = [p.pattern_type.value for p in session.patterns_discovered]
        if pattern_types:
            content += f"Pattern types: {', '.join(set(pattern_types))}."

        # Create vector representation (simplified - would normally use proper embedding)
        vector = np.random.normal(0, 1, self.memory_store.embedding_dimension)
        vector = vector / np.linalg.norm(vector)  # Normalize

        # Create constellation alignment based on discovered patterns
        constellation_tags = {"DREAM": 1.0, "MEMORY": 0.8}
        for pattern in session.patterns_discovered:
            for star, alignment in pattern.constellation_alignment.items():
                current = constellation_tags.get(star, 0.0)
                constellation_tags[star] = min(1.0, current + alignment * 0.1)

        dream_meta_memory = MemoryVector(
            id=f"dream_meta_{session.session_id}",
            content=content,
            vector=vector,
            memory_type=MemoryType.DREAM,
            importance=MemoryImportance.HIGH,
            timestamp=datetime.now(timezone.utc),
            constellation_tags=constellation_tags,
            source_context="Dream session meta-memory",
            confidence=0.9,
        )

        return dream_meta_memory

    def get_dream_session(self, session_id: str) -> Optional[DreamSession]:
        """Get dream session by ID."""
        for session in self.dream_sessions:
            if session.session_id == session_id:
                return session
        return None

    def get_discovered_patterns(self, pattern_type: Optional[DreamInsightType] = None) -> list[DreamMemoryPattern]:
        """Get discovered patterns, optionally filtered by type."""
        if pattern_type is None:
            return list(self.discovered_patterns.values())

        return [pattern for pattern in self.discovered_patterns.values() if pattern.pattern_type == pattern_type]

    def get_dream_stats(self) -> dict[str, Any]:
        """Get comprehensive dream processing statistics."""
        recent_sessions = [s for s in self.dream_sessions if s.success][-50:]  # Last 50 successful

        stats = {
            **self.stats,
            "active_patterns": len(self.discovered_patterns),
            "recent_performance": {
                "success_rate": len(recent_sessions) / max(1, len(self.dream_sessions[-50:])),
                "avg_patterns_per_session": (
                    np.mean([len(s.patterns_discovered) for s in recent_sessions]) if recent_sessions else 0.0
                ),
                "avg_insights_per_session": (
                    np.mean([len(s.insights_generated) for s in recent_sessions]) if recent_sessions else 0.0
                ),
            },
            "pattern_distribution": {pt.value: count for pt, count in self.stats["pattern_types"].items() if count > 0},
        }

        return stats
