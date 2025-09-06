"""
Memory Consolidation System for AGI

Integrates with LUKHAS fold-based memory system and dream processes
for intelligent memory consolidation, strengthening, and organization.
"""

import asyncio
import logging
import statistics
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np

from .vector_memory import MemoryImportance, MemoryType, MemoryVector, VectorMemoryStore

logger = logging.getLogger(__name__, timezone)


class ConsolidationStrategy(Enum):
    """Memory consolidation strategies."""

    TEMPORAL = "temporal"  # Time-based consolidation
    SEMANTIC = "semantic"  # Meaning-based clustering
    EMOTIONAL = "emotional"  # Emotion-guided consolidation
    IMPORTANCE = "importance"  # Priority-based strengthening
    DREAM_GUIDED = "dream_guided"  # Dream-enhanced consolidation
    CAUSAL = "causal"  # Causal chain reinforcement


class ConsolidationType(Enum):
    """Types of consolidation operations."""

    STRENGTHEN = "strengthen"  # Reinforce memory strength
    MERGE = "merge"  # Combine similar memories
    ASSOCIATE = "associate"  # Create associative links
    DECAY = "decay"  # Natural memory decay
    REORGANIZE = "reorganize"  # Restructure memory organization


@dataclass
class ConsolidationJob:
    """Memory consolidation job specification."""

    strategy: ConsolidationStrategy
    consolidation_type: ConsolidationType
    target_memories: list[str]  # Memory IDs to consolidate
    priority: float = 1.0
    scheduled_time: Optional[datetime] = None
    dream_context: Optional[dict[str, Any]] = None  # Dream insights for consolidation


@dataclass
class ConsolidationResult:
    """Result of memory consolidation operation."""

    job_id: str
    success: bool
    memories_processed: int
    memories_strengthened: int
    memories_merged: int
    new_associations: int
    consolidation_score: float
    processing_time_ms: int
    errors: list[str]


class MemoryConsolidator:
    """
    Advanced Memory Consolidation System for AGI

    Provides intelligent memory consolidation that integrates with LUKHAS
    consciousness framework and dream system for optimal memory organization.
    """

    def __init__(self, memory_store: VectorMemoryStore):
        self.memory_store = memory_store
        self.consolidation_history: list[ConsolidationResult] = []
        self.consolidation_jobs: list[ConsolidationJob] = []

        # Consolidation Parameters
        self.similarity_threshold = 0.85  # Threshold for memory merging
        self.association_threshold = 0.7  # Threshold for creating associations
        self.decay_rate = 0.02  # Base memory decay rate
        self.dream_boost_factor = 0.3  # Dream consolidation enhancement

        # Statistics
        self.stats = {
            "total_consolidations": 0,
            "memories_consolidated": 0,
            "consolidation_types": {ct.value: 0 for ct in ConsolidationType},
            "avg_consolidation_time": 0.0,
        }

    async def schedule_consolidation(self, job: ConsolidationJob) -> str:
        """Schedule a memory consolidation job."""
        job_id = f"cons_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{len(self.consolidation_jobs)}"
        job.scheduled_time = job.scheduled_time or datetime.now(timezone.utc)

        self.consolidation_jobs.append(job)
        self.consolidation_jobs.sort(key=lambda j: (j.scheduled_time, -j.priority))

        logger.info(f"Scheduled consolidation job {job_id} (strategy: {job.strategy.value})")
        return job_id

    async def run_consolidation_cycle(self) -> list[ConsolidationResult]:
        """Run scheduled consolidation jobs."""
        results = []
        now = datetime.now(timezone.utc)

        # Process due jobs
        due_jobs = [job for job in self.consolidation_jobs if job.scheduled_time <= now]

        for job in due_jobs:
            try:
                result = await self._execute_consolidation_job(job)
                results.append(result)
                self.consolidation_history.append(result)

                # Remove completed job
                self.consolidation_jobs.remove(job)

            except Exception as e:
                logger.error(f"Error executing consolidation job: {e}")
                results.append(
                    ConsolidationResult(
                        job_id=f"failed_{now.isoformat()}",
                        success=False,
                        memories_processed=0,
                        memories_strengthened=0,
                        memories_merged=0,
                        new_associations=0,
                        consolidation_score=0.0,
                        processing_time_ms=0,
                        errors=[str(e)],
                    )
                )

        return results

    async def _execute_consolidation_job(self, job: ConsolidationJob) -> ConsolidationResult:
        """Execute a specific consolidation job."""
        start_time = asyncio.get_event_loop().time()
        job_id = f"exec_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"

        result = ConsolidationResult(
            job_id=job_id,
            success=True,
            memories_processed=0,
            memories_strengthened=0,
            memories_merged=0,
            new_associations=0,
            consolidation_score=0.0,
            processing_time_ms=0,
            errors=[],
        )

        try:
            # Get target memories
            target_memories = []
            for memory_id in job.target_memories:
                memory = await self.memory_store.get_memory(memory_id, reinforce=False)
                if memory:
                    target_memories.append(memory)

            if not target_memories:
                result.errors.append("No valid target memories found")
                return result

            result.memories_processed = len(target_memories)

            # Execute consolidation based on strategy
            if job.strategy == ConsolidationStrategy.TEMPORAL:
                await self._temporal_consolidation(target_memories, job, result)

            elif job.strategy == ConsolidationStrategy.SEMANTIC:
                await self._semantic_consolidation(target_memories, job, result)

            elif job.strategy == ConsolidationStrategy.EMOTIONAL:
                await self._emotional_consolidation(target_memories, job, result)

            elif job.strategy == ConsolidationStrategy.IMPORTANCE:
                await self._importance_consolidation(target_memories, job, result)

            elif job.strategy == ConsolidationStrategy.DREAM_GUIDED:
                await self._dream_guided_consolidation(target_memories, job, result)

            elif job.strategy == ConsolidationStrategy.CAUSAL:
                await self._causal_consolidation(target_memories, job, result)

            # Calculate consolidation score
            result.consolidation_score = self._calculate_consolidation_score(result)

            # Update statistics
            self.stats["total_consolidations"] += 1
            self.stats["memories_consolidated"] += result.memories_processed
            self.stats["consolidation_types"][job.consolidation_type.value] += 1

        except Exception as e:
            result.success = False
            result.errors.append(str(e))
            logger.error(f"Error in consolidation job execution: {e}")

        finally:
            processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
            result.processing_time_ms = int(processing_time)

            # Update average processing time
            total_jobs = self.stats["total_consolidations"]
            if total_jobs > 0:
                self.stats["avg_consolidation_time"] = (
                    self.stats["avg_consolidation_time"] * (total_jobs - 1) + processing_time
                ) / total_jobs

        return result

    async def _temporal_consolidation(
        self, memories: list[MemoryVector], job: ConsolidationJob, result: ConsolidationResult
    ):
        """Consolidate memories based on temporal proximity."""
        # Group memories by time windows
        time_groups = {}
        window_hours = 24  # 24-hour consolidation window

        for memory in memories:
            time_key = memory.timestamp.replace(minute=0, second=0, microsecond=0)
            time_key = time_key.replace(hour=(time_key.hour // window_hours) * window_hours)

            if time_key not in time_groups:
                time_groups[time_key] = []
            time_groups[time_key].append(memory)

        # Strengthen memories in each time group
        for time_group in time_groups.values():
            if len(time_group) > 1:
                # Strengthen memories that occurred together
                for memory in time_group:
                    memory.reinforce(0.1)
                    result.memories_strengthened += 1

                # Create temporal associations
                for i, memory1 in enumerate(time_group):
                    for memory2 in time_group[i + 1 :]:
                        if memory2.id not in memory1.related_memories:
                            memory1.related_memories.append(memory2.id)
                            memory2.related_memories.append(memory1.id)
                            result.new_associations += 1

    async def _semantic_consolidation(
        self, memories: list[MemoryVector], job: ConsolidationJob, result: ConsolidationResult
    ):
        """Consolidate memories based on semantic similarity."""
        # Calculate pairwise similarities
        for i, memory1 in enumerate(memories):
            for memory2 in memories[i + 1 :]:
                # Calculate cosine similarity
                similarity = np.dot(memory1.vector, memory2.vector) / (
                    np.linalg.norm(memory1.vector) * np.linalg.norm(memory2.vector)
                )

                if similarity > self.similarity_threshold:
                    # Very similar memories - consider merging
                    if job.consolidation_type == ConsolidationType.MERGE:
                        await self._merge_memories(memory1, memory2, result)
                    else:
                        # Create semantic associations
                        if memory2.id not in memory1.related_memories:
                            memory1.related_memories.append(memory2.id)
                            memory2.related_memories.append(memory1.id)
                            result.new_associations += 1

                elif similarity > self.association_threshold:
                    # Moderately similar - strengthen association
                    if memory2.id not in memory1.related_memories:
                        memory1.related_memories.append(memory2.id)
                        memory2.related_memories.append(memory1.id)
                        result.new_associations += 1

    async def _emotional_consolidation(
        self, memories: list[MemoryVector], job: ConsolidationJob, result: ConsolidationResult
    ):
        """Consolidate memories based on emotional content."""
        # Group memories by emotional valence
        emotional_groups = {"positive": [], "negative": [], "neutral": []}

        for memory in memories:
            if memory.emotional_valence is None:
                emotional_groups["neutral"].append(memory)
            elif memory.emotional_valence > 0.3:
                emotional_groups["positive"].append(memory)
            elif memory.emotional_valence < -0.3:
                emotional_groups["negative"].append(memory)
            else:
                emotional_groups["neutral"].append(memory)

        # Strengthen emotionally significant memories
        for group_name, group_memories in emotional_groups.items():
            if group_name != "neutral":
                for memory in group_memories:
                    # Emotional memories get stronger consolidation
                    boost = abs(memory.emotional_valence or 0) * 0.2
                    memory.reinforce(boost)
                    result.memories_strengthened += 1

    async def _importance_consolidation(
        self, memories: list[MemoryVector], job: ConsolidationJob, result: ConsolidationResult
    ):
        """Consolidate memories based on importance levels."""
        # Group by importance
        importance_groups = {}
        for memory in memories:
            importance = memory.importance
            if importance not in importance_groups:
                importance_groups[importance] = []
            importance_groups[importance].append(memory)

        # Strengthen high-importance memories more
        for importance, group_memories in importance_groups.items():
            boost_factor = importance.value / 5.0  # Scale to 0.0-1.0

            for memory in group_memories:
                memory.reinforce(boost_factor * 0.15)
                result.memories_strengthened += 1

    async def _dream_guided_consolidation(
        self, memories: list[MemoryVector], job: ConsolidationJob, result: ConsolidationResult
    ):
        """Use dream insights to guide memory consolidation."""
        if not job.dream_context:
            # Fallback to semantic consolidation
            await self._semantic_consolidation(memories, job, result)
            return

        dream_insights = job.dream_context.get("insights", [])
        job.dream_context.get("patterns", [])

        # Strengthen memories that align with dream insights
        for memory in memories:
            dream_relevance = 0.0

            # Check relevance to dream insights
            for insight in dream_insights:
                insight_content = insight.get("content", "")
                # Simple keyword matching (could be enhanced with semantic similarity)
                if any(keyword in memory.content.lower() for keyword in insight_content.lower().split()):
                    dream_relevance += insight.get("confidence", 0.5)

            # Apply dream-guided strengthening
            if dream_relevance > 0:
                boost = min(0.3, dream_relevance * self.dream_boost_factor)
                memory.reinforce(boost)
                result.memories_strengthened += 1

                # Tag with dream context
                memory.constellation_tags["DREAM"] = min(
                    1.0, memory.constellation_tags.get("DREAM", 0.0) + dream_relevance
                )

    async def _causal_consolidation(
        self, memories: list[MemoryVector], job: ConsolidationJob, result: ConsolidationResult
    ):
        """Consolidate memories based on causal relationships."""
        # Identify potential causal chains based on timestamps and content similarity
        sorted_memories = sorted(memories, key=lambda m: m.timestamp)

        for i, memory1 in enumerate(sorted_memories):
            for memory2 in sorted_memories[i + 1 : i + 6]:  # Look ahead up to 5 memories
                # Check if they could be causally related
                time_diff = (memory2.timestamp - memory1.timestamp).total_seconds()

                # Must be within reasonable causal timeframe (1 hour to 1 week)
                if 3600 <= time_diff <= 604800:  # 1 hour to 1 week
                    # Check semantic similarity for causal relevance
                    similarity = np.dot(memory1.vector, memory2.vector) / (
                        np.linalg.norm(memory1.vector) * np.linalg.norm(memory2.vector)
                    )

                    if similarity > 0.6:  # Moderate similarity suggests possible causation
                        # Create causal link
                        if memory2.id not in memory1.causal_links:
                            memory1.causal_links.append(memory2.id)
                            result.new_associations += 1

                        # Strengthen both memories in causal chain
                        memory1.reinforce(0.1)
                        memory2.reinforce(0.1)
                        result.memories_strengthened += 2

    async def _merge_memories(self, memory1: MemoryVector, memory2: MemoryVector, result: ConsolidationResult):
        """Merge two highly similar memories."""
        # Create merged content (simple concatenation - could be enhanced)
        merged_content = f"{memory1.content} [MERGED] {memory2.content}"

        # Average the vectors (simple approach)
        merged_vector = (memory1.vector + memory2.vector) / 2

        # Use higher importance and strength
        merged_importance = max(memory1.importance, memory2.importance, key=lambda x: x.value)
        merged_strength = max(memory1.strength, memory2.strength)

        # Combine constellation tags (take maximum alignment for each star)
        merged_constellation = {}
        all_stars = set(memory1.constellation_tags.keys()) | set(memory2.constellation_tags.keys())
        for star in all_stars:
            merged_constellation[star] = max(
                memory1.constellation_tags.get(star, 0.0), memory2.constellation_tags.get(star, 0.0)
            )

        # Update memory1 with merged data
        memory1.content = merged_content
        memory1.vector = merged_vector
        memory1.importance = merged_importance
        memory1.strength = merged_strength
        memory1.constellation_tags = merged_constellation
        memory1.access_count += memory2.access_count
        memory1.reinforce(0.2)  # Boost from merging

        # Combine associative links
        for related_id in memory2.related_memories:
            if related_id not in memory1.related_memories:
                memory1.related_memories.append(related_id)

        for causal_id in memory2.causal_links:
            if causal_id not in memory1.causal_links:
                memory1.causal_links.append(causal_id)

        # Remove memory2
        await self.memory_store.delete_memory(memory2.id)
        result.memories_merged += 1

        logger.info(f"Merged memories {memory1.id} and {memory2.id}")

    def _calculate_consolidation_score(self, result: ConsolidationResult) -> float:
        """Calculate overall consolidation effectiveness score."""
        if result.memories_processed == 0:
            return 0.0

        # Weighted scoring
        strengthening_score = result.memories_strengthened / result.memories_processed
        association_score = min(1.0, result.new_associations / (result.memories_processed * 0.5))
        merge_efficiency = result.memories_merged / result.memories_processed if result.memories_merged > 0 else 0.0

        # Time efficiency (bonus for fast processing)
        time_efficiency = max(0.0, 1.0 - (result.processing_time_ms / 10000))  # 10 second baseline

        overall_score = (
            strengthening_score * 0.4 + association_score * 0.3 + merge_efficiency * 0.2 + time_efficiency * 0.1
        )

        return min(1.0, overall_score)

    async def auto_consolidate_memory_type(
        self, memory_type: MemoryType, strategy: ConsolidationStrategy = ConsolidationStrategy.SEMANTIC
    ) -> str:
        """Automatically consolidate all memories of a specific type."""
        # Get all memories of this type
        target_memories = []
        for memory_id, memory in self.memory_store.memories.items():
            if memory.memory_type == memory_type:
                target_memories.append(memory_id)

        if not target_memories:
            logger.warning(f"No memories found for type {memory_type.value}")
            return ""

        # Create consolidation job
        job = ConsolidationJob(
            strategy=strategy,
            consolidation_type=ConsolidationType.STRENGTHEN,
            target_memories=target_memories,
            priority=0.8,
        )

        return await self.schedule_consolidation(job)

    async def dream_consolidation_cycle(self, dream_insights: dict[str, Any]) -> str:
        """Run dream-guided consolidation for recent memories."""
        # Get recent memories (last 24 hours)
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)
        recent_memories = []

        for memory_id, memory in self.memory_store.memories.items():
            if memory.timestamp >= cutoff_time:
                recent_memories.append(memory_id)

        if not recent_memories:
            return ""

        # Create dream-guided consolidation job
        job = ConsolidationJob(
            strategy=ConsolidationStrategy.DREAM_GUIDED,
            consolidation_type=ConsolidationType.STRENGTHEN,
            target_memories=recent_memories,
            priority=1.2,  # High priority for dream consolidation
            dream_context=dream_insights,
        )

        return await self.schedule_consolidation(job)

    def get_consolidation_stats(self) -> dict[str, Any]:
        """Get comprehensive consolidation statistics."""
        recent_results = [r for r in self.consolidation_history if r.success][-100:]  # Last 100 successful

        stats = {
            **self.stats,
            "pending_jobs": len(self.consolidation_jobs),
            "recent_performance": {
                "avg_consolidation_score": (
                    statistics.mean([r.consolidation_score for r in recent_results]) if recent_results else 0.0
                ),
                "success_rate": len(recent_results) / max(1, len(self.consolidation_history[-100:])),
                "avg_memories_per_job": (
                    statistics.mean([r.memories_processed for r in recent_results]) if recent_results else 0.0
                ),
            },
        }

        return stats
