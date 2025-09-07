"""

#TAG:memory
#TAG:consolidation
#TAG:neuroplastic
#TAG:colony


Consolidated Memory System - Memory Colonies

Consolidated from 4 files:
- core/colonies/memory_colony_enhanced.py
- memory/adapters/colony_memory_adapter.py
- memory/colonies/base_memory_colony.py
- memory/colonies/episodic_memory_colony.py
"""
import streamlit as st

import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

# Import core systems with fallbacks
try:
    from candidate.core.colonies.memory_colony_enhanced import EnhancedMemoryColony
    from candidate.memory.adapters.colony_memory_adapter import ColonyMemoryAdapter
except ImportError:
    EnhancedMemoryColony = None
    ColonyMemoryAdapter = None

logger = logging.getLogger(__name__)


class ColonyType(Enum):
    """Types of memory colonies"""

    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    EMOTIONAL = "emotional"
    WORKING = "working"


class ColonyState(Enum):
    """Colony operational states"""

    DORMANT = "dormant"
    ACTIVE = "active"
    CONSOLIDATING = "consolidating"
    REPLICATING = "replicating"
    DEGRADING = "degrading"


@dataclass
class MemoryColony:
    """Represents a memory colony with specialized processing capabilities"""

    colony_id: str
    colony_type: ColonyType
    state: ColonyState = ColonyState.DORMANT
    memory_capacity: int = 1000
    current_load: int = 0
    specialization_score: float = 0.8
    health_score: float = 1.0
    last_activity: Optional[datetime] = None
    processing_queue: deque = field(default_factory=lambda: deque(maxlen=100))
    processed_memories: set[str] = field(default_factory=set)


class ConsolidatedMemorycolonies:
    """Consolidated memory colonies with neuroplastic adaptation and Trinity Framework integration"""

    def __init__(self):
        self.active_memories = {}
        self.processing_queue = deque(maxlen=5000)
        self.colonies: dict[str, MemoryColony] = {}
        self.colony_network = defaultdict(list)  # Colony interconnections
        self.performance_metrics = {
            "total_colonies": 0,
            "active_colonies": 0,
            "total_processed": 0,
            "average_processing_time": 0.0,
            "consolidation_events": 0,
            "replication_events": 0,
        }

        # Initialize specialized colonies
        self._initialize_core_colonies()

        # Colony management parameters
        self.max_colonies = 50
        self.colony_replication_threshold = 0.8
        self.colony_degradation_threshold = 0.3

        logger.info(f"ConsolidatedMemoryColonies initialized with {len(self.colonies)} core colonies")

    def _initialize_core_colonies(self):
        """Initialize core memory colonies for different memory types"""
        core_colonies = [
            ("episodic_primary", ColonyType.EPISODIC, 2000),
            ("semantic_primary", ColonyType.SEMANTIC, 1500),
            ("procedural_primary", ColonyType.PROCEDURAL, 1000),
            ("emotional_primary", ColonyType.EMOTIONAL, 1200),
            ("working_primary", ColonyType.WORKING, 500),
        ]

        for colony_id, colony_type, capacity in core_colonies:
            colony = MemoryColony(
                colony_id=colony_id,
                colony_type=colony_type,
                memory_capacity=capacity,
                state=ColonyState.ACTIVE,
                last_activity=datetime.now(timezone.utc),
            )
            self.colonies[colony_id] = colony
            self.performance_metrics["total_colonies"] += 1
            self.performance_metrics["active_colonies"] += 1

    async def process_memory(self, memory_data: dict[str, Any]) -> Optional[dict]:
        """Process memory through consolidated colony pipeline with neuroplastic adaptation"""
        start_time = time.time()
        memory_id = memory_data.get("memory_id", f"mem_{int(time.time() * 1000}")

        try:
            # 🛡️ Guardian: Validate memory data and check system health
            if not self._validate_memory_data(memory_data):
                return {"status": "rejected", "reason": "invalid_data"}

            # ⚛️ Identity: Classify memory and determine target colonies
            memory_classification = await self._classify_memory(memory_data)
            target_colonies = await self._select_target_colonies(memory_classification, memory_data)

            if not target_colonies:
                # Create new specialized colony if needed
                new_colony = await self._create_specialized_colony(memory_classification)
                if new_colony:
                    target_colonies = [new_colony.colony_id]

            # 🧠 Consciousness: Apply consciousness-aware colony processing
            consciousness_context = self._extract_consciousness_context(memory_data)

            # Process memory through selected colonies
            processing_results = []
            for colony_id in target_colonies:
                if colony_id in self.colonies:
                    result = await self._process_through_colony(
                        self.colonies[colony_id], memory_data, consciousness_context
                    )
                    processing_results.append(result)

            # Consolidate results from multiple colonies
            consolidated_result = await self._consolidate_colony_results(processing_results, memory_classification)

            # Update performance metrics
            processing_time = time.time() - start_time
            self._update_performance_metrics(processing_time)

            # Check for colony replication or degradation
            await self._manage_colony_lifecycle(target_colonies, memory_data)

            consolidated_result.update(
                {
                    "processing_time": processing_time,
                    "colonies_used": target_colonies,
                    "memory_classification": memory_classification,
                }
            )

            return consolidated_result

        except Exception as e:
            logger.error(f"Colony memory processing failed for {memory_id}: {e!s}")
            return {
                "status": "error",
                "error": str(e),
                "processing_time": time.time() - start_time,
            }

    def _validate_memory_data(self, memory_data: dict) -> bool:
        """Validate memory data before processing"""
        required_fields = ["memory_id"]
        return all(field in memory_data for field in required_fields)

    async def _classify_memory(self, memory_data: dict) -> dict:
        """Classify memory type and characteristics for colony selection"""
        content = memory_data.get("content", "")
        emotional_context = memory_data.get("emotional_context", {})
        temporal_context = memory_data.get("temporal_context", {})

        # Analyze memory characteristics
        classification = {
            "primary_type": self._determine_primary_type(memory_data),
            "complexity_score": self._calculate_complexity(content),
            "emotional_intensity": emotional_context.get("intensity", 0.0),
            "temporal_significance": temporal_context.get("significance", 0.5),
            "associative_strength": memory_data.get("associative_strength", 0.5),
        }

        # Determine secondary characteristics
        classification["secondary_types"] = self._identify_secondary_types(memory_data, classification)

        return classification

    def _determine_primary_type(self, memory_data: dict) -> ColonyType:
        """Determine primary memory type"""
        content = str(memory_data.get("content", "")).lower()

        # Heuristic classification
        if any(word in content for word in ["remember", "happened", "experience", "event"]):
            return ColonyType.EPISODIC
        elif any(word in content for word in ["know", "fact", "concept", "definition"]):
            return ColonyType.SEMANTIC
        elif any(word in content for word in ["how", "procedure", "step", "process"]):
            return ColonyType.PROCEDURAL
        elif memory_data.get("emotional_context", {}).get("intensity", 0) > 0.6:
            return ColonyType.EMOTIONAL
        else:
            return ColonyType.WORKING

    def _calculate_complexity(self, content: str) -> float:
        """Calculate memory complexity score"""
        if not content:
            return 0.0

        word_count = len(content.split())
        unique_words = len(set(content.lower().split()))

        # Simple complexity measure
        complexity = (unique_words / max(word_count, 1)) * (word_count / 100)
        return min(complexity, 1.0)

    def _identify_secondary_types(self, memory_data: dict, classification: dict) -> list[ColonyType]:
        """Identify secondary memory types for cross-colony processing"""
        secondary_types = []

        # Add emotional if high emotional intensity
        if classification["emotional_intensity"] > 0.5 and classification["primary_type"] != ColonyType.EMOTIONAL:
            secondary_types.append(ColonyType.EMOTIONAL)

        # Add working memory if temporary significance
        if classification["temporal_significance"] < 0.3 and classification["primary_type"] != ColonyType.WORKING:
            secondary_types.append(ColonyType.WORKING)

        return secondary_types

    async def _select_target_colonies(self, classification: dict, memory_data: dict) -> list[str]:
        """Select target colonies for memory processing"""
        target_colonies = []
        primary_type = classification["primary_type"]

        # Find colonies of the primary type
        primary_colonies = [
            colony_id
            for colony_id, colony in self.colonies.items()
            if colony.colony_type == primary_type and colony.state == ColonyState.ACTIVE
        ]

        if primary_colonies:
            # Select colony with lowest current load
            best_colony = min(
                primary_colonies,
                key=lambda cid: self.colonies[cid].current_load / self.colonies[cid].memory_capacity,
            )
            target_colonies.append(best_colony)

        # Add secondary colonies if needed
        for secondary_type in classification.get("secondary_types", []):
            secondary_colonies = [
                colony_id
                for colony_id, colony in self.colonies.items()
                if colony.colony_type == secondary_type and colony.state == ColonyState.ACTIVE
            ]
            if secondary_colonies and len(target_colonies) < 3:  # Limit cross-processing
                best_secondary = min(
                    secondary_colonies,
                    key=lambda cid: self.colonies[cid].current_load / self.colonies[cid].memory_capacity,
                )
                target_colonies.append(best_secondary)

        return target_colonies

    async def _create_specialized_colony(self, classification: dict) -> Optional[MemoryColony]:
        """Create a new specialized colony if needed and capacity allows"""
        if len(self.colonies) >= self.max_colonies:
            logger.warning("Colony limit reached, cannot create new specialized colony")
            return None

        primary_type = classification["primary_type"]
        colony_id = f"{primary_type.value}_specialized_{int(time.time()}"

        # Determine capacity based on complexity
        base_capacity = 800
        complexity_bonus = int(classification.get("complexity_score", 0.5) * 500)
        capacity = base_capacity + complexity_bonus

        new_colony = MemoryColony(
            colony_id=colony_id,
            colony_type=primary_type,
            memory_capacity=capacity,
            state=ColonyState.ACTIVE,
            specialization_score=0.9,  # High specialization for new colony
            last_activity=datetime.now(timezone.utc),
        )

        self.colonies[colony_id] = new_colony
        self.performance_metrics["total_colonies"] += 1
        self.performance_metrics["active_colonies"] += 1

        logger.info(f"Created specialized colony {colony_id} of type {primary_type.value}")
        return new_colony

    def _extract_consciousness_context(self, memory_data: dict) -> dict:
        """Extract consciousness context for enhanced processing"""
        return {
            "attention_level": memory_data.get("attention_level", 0.7),
            "awareness_state": memory_data.get("awareness_state", "focused"),
            "dream_influence": memory_data.get("dream_influence", 0.0),
            "metacognitive_markers": memory_data.get("metacognitive_markers", []),
        }

    async def _process_through_colony(
        self, colony: MemoryColony, memory_data: dict, consciousness_context: dict
    ) -> dict:
        """Process memory through a specific colony"""
        colony.current_load += 1
        colony.last_activity = datetime.now(timezone.utc)
        memory_id = memory_data.get("memory_id")

        try:
            # Simulate specialized processing based on colony type
            processing_result = {
                "colony_id": colony.colony_id,
                "colony_type": colony.colony_type.value,
                "status": "processed",
                "specialization_applied": True,
                "consciousness_integration": consciousness_context,
                "processing_quality": colony.specialization_score * colony.health_score,
            }

            # Add specialized processing based on colony type
            if colony.colony_type == ColonyType.EPISODIC:
                processing_result.update(await self._process_episodic_memory(memory_data, colony))
            elif colony.colony_type == ColonyType.SEMANTIC:
                processing_result.update(await self._process_semantic_memory(memory_data, colony))
            elif colony.colony_type == ColonyType.PROCEDURAL:
                processing_result.update(await self._process_procedural_memory(memory_data, colony))
            elif colony.colony_type == ColonyType.EMOTIONAL:
                processing_result.update(await self._process_emotional_memory(memory_data, colony))
            elif colony.colony_type == ColonyType.WORKING:
                processing_result.update(await self._process_working_memory(memory_data, colony))

            # Add memory to colony's processed set
            colony.processed_memories.add(memory_id)

            return processing_result

        except Exception as e:
            logger.error(f"Colony {colony.colony_id} processing failed: {e!s}")
            return {"colony_id": colony.colony_id, "status": "error", "error": str(e)}
        finally:
            colony.current_load = max(0, colony.current_load - 1)

    async def _process_episodic_memory(self, memory_data: dict, colony: MemoryColony) -> dict:
        """Specialized episodic memory processing"""
        return {
            "episodic_features": {
                "temporal_context": memory_data.get("temporal_context", {}),
                "spatial_context": memory_data.get("spatial_context", {}),
                "personal_significance": memory_data.get("personal_significance", 0.5),
                "narrative_structure": self._extract_narrative_structure(memory_data),
            },
            "autobiographical_relevance": 0.8,
        }

    async def _process_semantic_memory(self, memory_data: dict, colony: MemoryColony) -> dict:
        """Specialized semantic memory processing"""
        return {
            "semantic_features": {
                "conceptual_links": memory_data.get("conceptual_links", []),
                "knowledge_category": memory_data.get("knowledge_category", "general"),
                "abstraction_level": memory_data.get("abstraction_level", 0.5),
                "factual_confidence": memory_data.get("factual_confidence", 0.7),
            },
            "knowledge_integration": 0.9,
        }

    async def _process_procedural_memory(self, memory_data: dict, colony: MemoryColony) -> dict:
        """Specialized procedural memory processing"""
        return {
            "procedural_features": {
                "skill_type": memory_data.get("skill_type", "cognitive"),
                "execution_steps": memory_data.get("execution_steps", []),
                "motor_components": memory_data.get("motor_components", []),
                "automaticity_level": memory_data.get("automaticity_level", 0.3),
            },
            "skill_integration": 0.7,
        }

    async def _process_emotional_memory(self, memory_data: dict, colony: MemoryColony) -> dict:
        """Specialized emotional memory processing"""
        emotional_context = memory_data.get("emotional_context", {})
        return {
            "emotional_features": {
                "valence": emotional_context.get("valence", 0.0),
                "arousal": emotional_context.get("arousal", 0.0),
                "dominance": emotional_context.get("dominance", 0.0),
                "emotional_tags": emotional_context.get("emotional_tags", []),
                "mood_influence": emotional_context.get("mood_influence", 0.0),
            },
            "emotional_salience": emotional_context.get("intensity", 0.5),
        }

    async def _process_working_memory(self, memory_data: dict, colony: MemoryColony) -> dict:
        """Specialized working memory processing"""
        return {
            "working_memory_features": {
                "retention_duration": memory_data.get("retention_duration", 30),  # seconds
                "manipulation_required": memory_data.get("manipulation_required", False),
                "attention_demands": memory_data.get("attention_demands", 0.5),
                "interference_resistance": memory_data.get("interference_resistance", 0.3),
            },
            "working_capacity_usage": colony.current_load / colony.memory_capacity,
        }

    def _extract_narrative_structure(self, memory_data: dict) -> dict:
        """Extract narrative structure from episodic memory"""
        content = memory_data.get("content", "")
        return {
            "has_beginning": "start" in content.lower() or "began" in content.lower(),
            "has_middle": "then" in content.lower() or "during" in content.lower(),
            "has_end": "end" in content.lower() or "finished" in content.lower(),
            "narrative_coherence": 0.6,
        }

    async def _consolidate_colony_results(self, processing_results: list[dict], classification: dict) -> dict:
        """Consolidate results from multiple colony processing"""
        if not processing_results:
            return {"status": "no_processing", "reason": "no_active_colonies"}

        successful_results = [r for r in processing_results if r.get("status") == "processed"]

        if not successful_results:
            return {
                "status": "processing_failed",
                "errors": [r.get("error") for r in processing_results],
            }

        # Consolidate processing results
        consolidated = {
            "status": "success",
            "primary_colony": successful_results[0]["colony_id"],
            "colonies_involved": [r["colony_id"] for r in successful_results],
            "processing_quality": sum(r.get("processing_quality", 0.5) for r in successful_results)
            / len(successful_results),
            "specialized_features": {},
            "cross_colony_benefits": len(successful_results) > 1,
        }

        # Merge specialized features
        for result in successful_results:
            for key, value in result.items():
                if key.endswith("_features"):
                    consolidated["specialized_features"][key] = value

        self.performance_metrics["consolidation_events"] += 1
        return consolidated

    async def _manage_colony_lifecycle(self, target_colonies: list[str], memory_data: dict):
        """Manage colony lifecycle including replication and degradation"""
        for colony_id in target_colonies:
            if colony_id not in self.colonies:
                continue

            colony = self.colonies[colony_id]
            utilization = colony.current_load / colony.memory_capacity

            # Check for replication need
            if (
                utilization > self.colony_replication_threshold
                and colony.health_score > 0.7
                and len(self.colonies) < self.max_colonies
            ):
                await self._replicate_colony(colony)

            # Update health score based on performance
            colony.health_score = min(1.0, colony.health_score + 0.01 - utilization * 0.02)

            # Check for degradation
            if colony.health_score < self.colony_degradation_threshold:
                await self._degrade_colony(colony_id)

    async def _replicate_colony(self, parent_colony: MemoryColony):
        """Replicate a high-performing colony"""
        replica_id = f"{parent_colony.colony_id}_replica_{int(time.time()}"

        replica = MemoryColony(
            colony_id=replica_id,
            colony_type=parent_colony.colony_type,
            memory_capacity=parent_colony.memory_capacity,
            state=ColonyState.ACTIVE,
            specialization_score=parent_colony.specialization_score * 0.9,  # Slightly lower
            health_score=0.8,  # Fresh colony health
            last_activity=datetime.now(timezone.utc),
        )

        self.colonies[replica_id] = replica
        self.performance_metrics["total_colonies"] += 1
        self.performance_metrics["active_colonies"] += 1
        self.performance_metrics["replication_events"] += 1

        logger.info(f"Replicated colony {parent_colony.colony_id} as {replica_id}")

    async def _degrade_colony(self, colony_id: str):
        """Degrade or remove an underperforming colony"""
        if colony_id not in self.colonies:
            return

        colony = self.colonies[colony_id]

        # Don't degrade primary colonies
        if "primary" in colony_id:
            colony.health_score = max(0.3, colony.health_score)  # Minimum health for primary
            return

        # Remove specialized colonies that are underperforming
        del self.colonies[colony_id]
        self.performance_metrics["active_colonies"] -= 1

        logger.info(f"Degraded and removed colony {colony_id}")

    def _update_performance_metrics(self, processing_time: float):
        """Update performance metrics"""
        self.performance_metrics["total_processed"] += 1

        # Exponential moving average for processing time
        alpha = 0.1
        self.performance_metrics["average_processing_time"] = (
            alpha * processing_time + (1 - alpha) * self.performance_metrics["average_processing_time"]
        )

    def get_colony_status(self) -> dict:
        """Get current colony system status"""
        colony_stats = {}
        for colony_id, colony in self.colonies.items():
            colony_stats[colony_id] = {
                "type": colony.colony_type.value,
                "state": colony.state.value,
                "utilization": colony.current_load / colony.memory_capacity,
                "health_score": colony.health_score,
                "specialization_score": colony.specialization_score,
                "memories_processed": len(colony.processed_memories),
            }

        return {
            "colony_statistics": colony_stats,
            "performance_metrics": self.performance_metrics,
            "system_health": sum(c.health_score for c in self.colonies.values()) / len(self.colonies),
        }

    def get_performance_metrics(self) -> dict:
        """Get current performance metrics"""
        return self.performance_metrics.copy()


# Global instance
memory_colonies_instance = ConsolidatedMemorycolonies()
