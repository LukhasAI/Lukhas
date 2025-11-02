"""
LUKHAS AI - Dream State Memory Integration
==========================================

#TAG:consciousness
#TAG:memory
#TAG:dreams
#TAG:neuroplastic

Advanced dream state memory integration for LUKHAS AI.
Bridges dream processing with memory systems and consciousness.

Constellation Framework: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian
"""

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


class DreamState(Enum):
    """Different states of dream processing"""

    AWAKE = "awake"
    DROWSY = "drowsy"
    LIGHT_SLEEP = "light_sleep"
    DEEP_SLEEP = "deep_sleep"
    REM_SLEEP = "rem_sleep"
    LUCID_DREAMING = "lucid_dreaming"


class DreamType(Enum):
    """Types of dream experiences"""

    MEMORY_CONSOLIDATION = "memory_consolidation"
    CREATIVE_SYNTHESIS = "creative_synthesis"
    PROBLEM_SOLVING = "problem_solving"
    EMOTIONAL_PROCESSING = "emotional_processing"
    PATTERN_INTEGRATION = "pattern_integration"
    SYMBOLIC_TRANSFORMATION = "symbolic_transformation"


@dataclass
class DreamMemoryEntry:
    """Memory entry enhanced for dream processing"""

    memory_id: str
    content: Any
    dream_relevance: float
    symbolic_content: dict[str, Any]
    emotional_weight: float
    consolidation_priority: float
    dream_associations: list[str] = field(default_factory=list)
    transformation_history: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class DreamExperience:
    """Represents a dream experience"""

    dream_id: str
    dream_type: DreamType
    dream_state: DreamState
    start_time: datetime
    duration_seconds: float
    participating_memories: list[str]
    dream_narrative: str
    symbolic_elements: dict[str, Any]
    emotional_themes: dict[str, float]
    insights_generated: list[str]
    memory_transformations: list[dict[str, Any]]
    consciousness_integration: dict[str, Any]


class DreamMemoryIntegrator:
    """
    Integrates dream processing with memory systems.

    Handles:
    - Memory selection for dream processing
    - Dream state management
    - Memory consolidation during dreams
    - Dream-memory feedback loops
    - Consciousness-dream-memory integration
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)

        # Dream state tracking
        self.current_dream_state = DreamState.AWAKE
        self.dream_experiences: list[DreamExperience] = []
        self.active_dream_memories: dict[str, DreamMemoryEntry] = {}

        # Integration parameters
        self.integration_config = {
            "max_dream_memories": 50,
            "consolidation_threshold": 0.7,
            "symbolic_transformation_rate": 0.3,
            "consciousness_feedback_enabled": True,
            "dream_cycle_duration": 300,  # 5 minutes
            "memory_selection_strategy": "importance_emotional",
        }

        # Performance metrics
        self.integration_metrics = {
            "total_dream_sessions": 0,
            "memories_consolidated": 0,
            "insights_generated": 0,
            "successful_integrations": 0,
            "consciousness_feedback_events": 0,
        }

        # State management
        self.integration_active = False
        self.dream_session_active = False

    async def initialize(self) -> bool:
        """Initialize the dream-memory integration system"""
        try:
            self.logger.info("Initializing Dream-Memory Integration System")

            # Start background integration monitoring
            asyncio.create_task(self._integration_monitoring_loop())

            # Initialize dream memory selection
            await self._initialize_dream_memory_selection()

            self.integration_active = True
            self.logger.info("Dream-Memory Integration System initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize dream-memory integration: {e}")
            return False

    async def start_dream_session(
        self, memories: Optional[list[dict[str, Any]]] = None, dream_type: DreamType = DreamType.MEMORY_CONSOLIDATION
    ) -> DreamExperience:
        """Start a new dream session with memory integration"""

        if self.dream_session_active:
            self.logger.warning("Dream session already active")
            return None

        dream_id = f"dream_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        start_time = datetime.now(timezone.utc)

        self.logger.info(f"Starting dream session: {dream_id} (type: {dream_type.name})")

        # Select memories for dream processing
        if memories is None:
            memories = await self._select_memories_for_dream(dream_type)

        # Prepare dream memories
        dream_memories = await self._prepare_dream_memories(memories)

        # Set dream state
        self.current_dream_state = DreamState.REM_SLEEP  # Default to REM for processing
        self.dream_session_active = True

        # Process dream experience
        dream_experience = await self._process_dream_experience(dream_id, dream_type, start_time, dream_memories)

        # Store dream experience
        self.dream_experiences.append(dream_experience)
        self.integration_metrics["total_dream_sessions"] += 1

        # Integration with consciousness
        if self.integration_config["consciousness_feedback_enabled"]:
            await self._integrate_with_consciousness(dream_experience)

        self.dream_session_active = False
        self.logger.info(f"Completed dream session: {dream_id}")

        return dream_experience

    async def consolidate_dream_memories(self, dream_experience: DreamExperience) -> dict[str, Any]:
        """Consolidate memories processed during dream"""

        consolidation_results = {
            "memories_consolidated": 0,
            "memories_transformed": 0,
            "new_associations": 0,
            "insights_integrated": 0,
            "consolidation_quality": 0.0,
        }

        # Process each participating memory
        for memory_id in dream_experience.participating_memories:
            if memory_id in self.active_dream_memories:
                memory_entry = self.active_dream_memories[memory_id]

                # Perform consolidation if above threshold
                if memory_entry.consolidation_priority >= self.integration_config["consolidation_threshold"]:
                    consolidation_success = await self._consolidate_memory(memory_entry, dream_experience)

                    if consolidation_success:
                        consolidation_results["memories_consolidated"] += 1

                # Apply transformations
                transformations = await self._apply_dream_transformations(memory_entry, dream_experience)
                if transformations:
                    consolidation_results["memories_transformed"] += len(transformations)

                # Create new associations
                new_associations = await self._create_dream_associations(memory_entry, dream_experience)
                consolidation_results["new_associations"] += len(new_associations)

        # Integrate insights
        insight_integration = await self._integrate_dream_insights(dream_experience)
        consolidation_results["insights_integrated"] = len(insight_integration)

        # Calculate consolidation quality
        consolidation_results["consolidation_quality"] = await self._calculate_consolidation_quality(
            dream_experience, consolidation_results
        )

        # Update metrics
        self.integration_metrics["memories_consolidated"] += consolidation_results["memories_consolidated"]
        self.integration_metrics["insights_generated"] += consolidation_results["insights_integrated"]

        if consolidation_results["consolidation_quality"] > 0.7:
            self.integration_metrics["successful_integrations"] += 1

        self.logger.info(f"Dream memory consolidation completed: {consolidation_results}")

        return consolidation_results

    async def transition_dream_state(self, new_state: DreamState) -> bool:
        """Transition to a new dream state"""

        if new_state == self.current_dream_state:
            return True

        self.logger.info(f"Transitioning dream state: {self.current_dream_state.name} -> {new_state.name}")

        # Validate state transition
        if not self._is_valid_state_transition(self.current_dream_state, new_state):
            self.logger.warning(f"Invalid dream state transition: {self.current_dream_state.name} -> {new_state.name}")
            return False

        # Perform state-specific processing
        await self._process_state_transition(self.current_dream_state, new_state)

        # Update current state
        self.current_dream_state = new_state

        return True

    async def get_dream_memory_insights(self, memory_id: str) -> dict[str, Any]:
        """Get dream-based insights for a specific memory"""

        insights = {
            "memory_id": memory_id,
            "dream_appearances": 0,
            "symbolic_interpretations": [],
            "emotional_transformations": [],
            "association_networks": [],
            "consolidation_history": [],
        }

        # Search through dream experiences
        for dream in self.dream_experiences:
            if memory_id in dream.participating_memories:
                insights["dream_appearances"] += 1

                # Extract symbolic interpretations
                if memory_id in dream.symbolic_elements:
                    insights["symbolic_interpretations"].append(dream.symbolic_elements[memory_id])

                # Track emotional transformations
                for transformation in dream.memory_transformations:
                    if transformation.get("memory_id") == memory_id:
                        insights["emotional_transformations"].append(transformation)

        # Get current dream memory data if available
        if memory_id in self.active_dream_memories:
            dream_memory = self.active_dream_memories[memory_id]
            insights["association_networks"] = dream_memory.dream_associations
            insights["consolidation_history"] = dream_memory.transformation_history

        return insights

    async def optimize_memory_dream_coupling(self) -> dict[str, Any]:
        """Optimize the coupling between memory and dream systems"""

        optimization_results = {
            "coupling_strength": 0.0,
            "memory_dream_correlation": 0.0,
            "optimization_improvements": [],
            "performance_metrics": {},
        }

        # Analyze current coupling strength
        coupling_strength = await self._analyze_memory_dream_coupling()
        optimization_results["coupling_strength"] = coupling_strength

        # Calculate memory-dream correlation
        correlation = await self._calculate_memory_dream_correlation()
        optimization_results["memory_dream_correlation"] = correlation

        # Identify optimization opportunities
        optimizations = await self._identify_coupling_optimizations()
        optimization_results["optimization_improvements"] = optimizations

        # Apply optimizations
        for optimization in optimizations:
            await self._apply_coupling_optimization(optimization)

        # Update performance metrics
        optimization_results["performance_metrics"] = {
            "dream_sessions_per_hour": self._calculate_dream_session_rate(),
            "memory_consolidation_efficiency": self._calculate_consolidation_efficiency(),
            "consciousness_integration_rate": self._calculate_consciousness_integration_rate(),
        }

        self.logger.info(f"Memory-dream coupling optimization completed: {optimization_results}")

        return optimization_results

    # Private methods for internal processing

    async def _integration_monitoring_loop(self):
        """Background loop for integration monitoring"""
        while self.integration_active:
            try:
                await self._monitor_integration_health()
                await asyncio.sleep(30.0)  # Monitor every 30 seconds
            except Exception as e:
                self.logger.error(f"Error in integration monitoring loop: {e}")
                await asyncio.sleep(60.0)

    async def _select_memories_for_dream(self, dream_type: DreamType) -> list[dict[str, Any]]:
        """Select memories for dream processing based on type"""

        # This would integrate with actual memory systems
        # For now, return simulated memory selection
        memory_count = min(self.integration_config["max_dream_memories"], 20)

        memories = []
        for i in range(memory_count):
            memories.append(
                {
                    "id": f"mem_{i:03d}",
                    "content": f"Memory content for {dream_type.name} processing",
                    "importance": 0.5 + (i % 5) * 0.1,
                    "emotional_weight": 0.3 + (i % 7) * 0.1,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "associations": [f"assoc_{j}" for j in range(i % 3)],
                }
            )

        self.logger.info(f"Selected {len(memories)} memories for {dream_type.name} dream")
        return memories

    async def _prepare_dream_memories(self, memories: list[dict[str, Any]]) -> dict[str, DreamMemoryEntry]:
        """Prepare memories for dream processing"""

        dream_memories = {}

        for memory in memories:
            memory_id = memory["id"]

            # Calculate dream relevance
            dream_relevance = await self._calculate_dream_relevance(memory)

            # Extract symbolic content
            symbolic_content = await self._extract_symbolic_content(memory)

            # Calculate consolidation priority
            consolidation_priority = await self._calculate_consolidation_priority(memory)

            dream_memory = DreamMemoryEntry(
                memory_id=memory_id,
                content=memory["content"],
                dream_relevance=dream_relevance,
                symbolic_content=symbolic_content,
                emotional_weight=memory.get("emotional_weight", 0.5),
                consolidation_priority=consolidation_priority,
            )

            dream_memories[memory_id] = dream_memory
            self.active_dream_memories[memory_id] = dream_memory

        return dream_memories

    async def _process_dream_experience(
        self, dream_id: str, dream_type: DreamType, start_time: datetime, dream_memories: dict[str, DreamMemoryEntry]
    ) -> DreamExperience:
        """Process the core dream experience"""

        # Simulate dream processing duration
        duration = self.integration_config["dream_cycle_duration"]
        await asyncio.sleep(0.1)  # Simulated processing time

        # Generate dream narrative
        narrative = await self._generate_dream_narrative(dream_type, dream_memories)

        # Extract symbolic elements
        symbolic_elements = await self._extract_dream_symbols(dream_memories)

        # Identify emotional themes
        emotional_themes = await self._identify_emotional_themes(dream_memories)

        # Generate insights
        insights = await self._generate_dream_insights(dream_type, dream_memories)

        # Create memory transformations
        transformations = await self._create_memory_transformations(dream_memories)

        # Prepare consciousness integration data
        consciousness_integration = await self._prepare_consciousness_integration(dream_memories, insights)

        return DreamExperience(
            dream_id=dream_id,
            dream_type=dream_type,
            dream_state=self.current_dream_state,
            start_time=start_time,
            duration_seconds=duration,
            participating_memories=list(dream_memories.keys()),
            dream_narrative=narrative,
            symbolic_elements=symbolic_elements,
            emotional_themes=emotional_themes,
            insights_generated=insights,
            memory_transformations=transformations,
            consciousness_integration=consciousness_integration,
        )

    async def _calculate_dream_relevance(self, memory: dict[str, Any]) -> float:
        """Calculate how relevant a memory is for dream processing"""

        relevance_factors = []

        # Importance factor
        importance = memory.get("importance", 0.5)
        relevance_factors.append(importance * 0.4)

        # Emotional weight factor
        emotional_weight = memory.get("emotional_weight", 0.5)
        relevance_factors.append(emotional_weight * 0.3)

        # Recency factor (newer memories slightly more relevant)
        # Simplified - in real implementation would parse timestamp
        relevance_factors.append(0.6 * 0.2)

        # Association factor
        associations = memory.get("associations", [])
        association_factor = min(1.0, len(associations) / 5.0)
        relevance_factors.append(association_factor * 0.1)

        return sum(relevance_factors)

    async def _extract_symbolic_content(self, memory: dict[str, Any]) -> dict[str, Any]:
        """Extract symbolic content from memory for dream processing"""

        content = str(memory.get("content", ""))

        # Simplified symbolic extraction
        symbolic_content = {
            "abstract_concepts": [],
            "emotional_symbols": [],
            "relational_patterns": [],
            "metaphorical_content": [],
        }

        # Identify abstract concepts (simplified)
        abstract_keywords = ["decision", "learning", "insight", "understanding", "growth"]
        for keyword in abstract_keywords:
            if keyword in content.lower():
                symbolic_content["abstract_concepts"].append(keyword)

        # Identify emotional symbols
        emotional_keywords = ["joy", "fear", "excitement", "anxiety", "peace"]
        for keyword in emotional_keywords:
            if keyword in content.lower():
                symbolic_content["emotional_symbols"].append(keyword)

        return symbolic_content

    async def _calculate_consolidation_priority(self, memory: dict[str, Any]) -> float:
        """Calculate consolidation priority for memory"""

        priority_factors = []

        # Importance factor
        importance = memory.get("importance", 0.5)
        priority_factors.append(importance * 0.5)

        # Emotional significance
        emotional_weight = memory.get("emotional_weight", 0.5)
        priority_factors.append(emotional_weight * 0.3)

        # Association richness
        associations = memory.get("associations", [])
        association_factor = min(1.0, len(associations) / 3.0)
        priority_factors.append(association_factor * 0.2)

        return sum(priority_factors)

    async def _generate_dream_narrative(
        self, dream_type: DreamType, dream_memories: dict[str, DreamMemoryEntry]
    ) -> str:
        """Generate a narrative for the dream experience"""

        memory_count = len(dream_memories)
        narrative_templates = {
            DreamType.MEMORY_CONSOLIDATION: f"Consolidating {memory_count} memories through symbolic integration",
            DreamType.CREATIVE_SYNTHESIS: f"Creatively synthesizing patterns from {memory_count} memory fragments",
            DreamType.PROBLEM_SOLVING: f"Processing problem-solving insights through {memory_count} memory connections",
            DreamType.EMOTIONAL_PROCESSING: f"Emotionally processing and integrating {memory_count} memory experiences",
        }

        base_narrative = narrative_templates.get(dream_type, f"Processing {memory_count} memories in dream state")

        # Add symbolic details
        symbolic_elements = [mem.symbolic_content for mem in dream_memories.values()]
        total_symbols = sum(len(elem.get("abstract_concepts", [])) for elem in symbolic_elements)

        if total_symbols > 5:
            base_narrative += f" with rich symbolic content ({total_symbols} symbolic elements)"

        return base_narrative

    async def _extract_dream_symbols(self, dream_memories: dict[str, DreamMemoryEntry]) -> dict[str, Any]:
        """Extract symbolic elements from dream memories"""

        symbols = {
            "collective_symbols": [],
            "personal_symbols": [],
            "archetypal_patterns": [],
            "transformation_symbols": [],
        }

        # Aggregate symbols from all memories
        for memory in dream_memories.values():
            symbolic_content = memory.symbolic_content

            symbols["collective_symbols"].extend(symbolic_content.get("abstract_concepts", []))
            symbols["personal_symbols"].extend(symbolic_content.get("emotional_symbols", []))

        # Identify archetypal patterns (simplified)
        if len(symbols["collective_symbols"]) > 3:
            symbols["archetypal_patterns"].append("integration_archetype")

        if len(symbols["personal_symbols"]) > 2:
            symbols["archetypal_patterns"].append("emotional_transformation")

        return symbols

    async def _identify_emotional_themes(self, dream_memories: dict[str, DreamMemoryEntry]) -> dict[str, float]:
        """Identify emotional themes in dream memories"""

        themes = {
            "consolidation_theme": 0.0,
            "transformation_theme": 0.0,
            "integration_theme": 0.0,
            "resolution_theme": 0.0,
        }

        # Calculate theme strengths based on memory characteristics
        total_memories = len(dream_memories)
        high_priority_memories = sum(1 for mem in dream_memories.values() if mem.consolidation_priority > 0.7)

        themes["consolidation_theme"] = high_priority_memories / total_memories if total_memories > 0 else 0.0

        # Other themes based on symbolic content richness
        symbolic_richness = sum(
            len(mem.symbolic_content.get("abstract_concepts", [])) for mem in dream_memories.values()
        )

        themes["transformation_theme"] = min(1.0, symbolic_richness / (total_memories * 2))
        themes["integration_theme"] = themes["consolidation_theme"] * 0.8
        themes["resolution_theme"] = (themes["consolidation_theme"] + themes["transformation_theme"]) / 2

        return themes

    async def _generate_dream_insights(
        self, dream_type: DreamType, dream_memories: dict[str, DreamMemoryEntry]
    ) -> list[str]:
        """Generate insights from dream processing"""

        insights = []

        # Type-specific insights
        if dream_type == DreamType.MEMORY_CONSOLIDATION:
            high_priority_count = sum(1 for mem in dream_memories.values() if mem.consolidation_priority > 0.7)
            insights.append(f"Identified {high_priority_count} memories for high-priority consolidation")

        elif dream_type == DreamType.CREATIVE_SYNTHESIS:
            symbol_diversity = len(
                set(
                    symbol
                    for mem in dream_memories.values()
                    for symbol in mem.symbolic_content.get("abstract_concepts", [])
                )
            )
            insights.append(f"Discovered {symbol_diversity} unique symbolic patterns for creative synthesis")

        # General insights
        if len(dream_memories) > 10:
            insights.append("Large memory set suggests need for systematic consolidation approach")

        emotional_variance = self._calculate_emotional_variance(dream_memories)
        if emotional_variance > 0.5:
            insights.append("High emotional variance detected - opportunity for emotional integration")

        return insights

    def _calculate_emotional_variance(self, dream_memories: dict[str, DreamMemoryEntry]) -> float:
        """Calculate emotional variance across dream memories"""
        emotional_weights = [mem.emotional_weight for mem in dream_memories.values()]

        if len(emotional_weights) < 2:
            return 0.0

        mean_emotion = sum(emotional_weights) / len(emotional_weights)
        variance = sum((weight - mean_emotion) ** 2 for weight in emotional_weights) / len(emotional_weights)

        return variance

    async def _create_memory_transformations(self, dream_memories: dict[str, DreamMemoryEntry]) -> list[dict[str, Any]]:
        """Create memory transformations during dream processing"""

        transformations = []

        for memory_id, memory in dream_memories.items():
            if memory.consolidation_priority > 0.6:
                transformation = {
                    "memory_id": memory_id,
                    "transformation_type": "consolidation_enhancement",
                    "priority_boost": 0.1,
                    "symbolic_integration": len(memory.symbolic_content.get("abstract_concepts", [])) > 0,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                transformations.append(transformation)

        return transformations

    async def _prepare_consciousness_integration(
        self, dream_memories: dict[str, DreamMemoryEntry], insights: list[str]
    ) -> dict[str, Any]:
        """Prepare data for consciousness integration"""

        return {
            "memory_count": len(dream_memories),
            "high_priority_memories": sum(1 for mem in dream_memories.values() if mem.consolidation_priority > 0.7),
            "insights_generated": len(insights),
            "symbolic_richness": sum(
                len(mem.symbolic_content.get("abstract_concepts", [])) for mem in dream_memories.values()
            ),
            "consciousness_relevance": 0.8,  # High relevance for dream integration
            "integration_timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def _integrate_with_consciousness(self, dream_experience: DreamExperience):
        """Integrate dream experience with consciousness systems"""

        self.logger.info(f"Integrating dream experience {dream_experience.dream_id} with consciousness")

        # This would integrate with the awareness mechanism
        integration_data = {
            "content": f"Dream integration: {dream_experience.dream_type.name}",
            "triggers": ["dream_integration", "memory_consolidation"],
            "emotional_context": dream_experience.emotional_themes,
            "dream_reference": dream_experience.dream_id,
            "insights": dream_experience.insights_generated,
        }

        # Simulated consciousness integration
        await asyncio.sleep(0.05)

        self.integration_metrics["consciousness_feedback_events"] += 1

    async def _consolidate_memory(self, memory_entry: DreamMemoryEntry, dream_experience: DreamExperience) -> bool:
        """Consolidate a specific memory through dream processing"""

        try:
            # Apply consolidation transformations
            memory_entry.transformation_history.append(
                {
                    "transformation_type": "dream_consolidation",
                    "dream_id": dream_experience.dream_id,
                    "consolidation_strength": memory_entry.consolidation_priority,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )

            # Enhance memory with dream insights
            relevant_insights = [
                insight for insight in dream_experience.insights_generated if memory_entry.memory_id in insight
            ]

            if relevant_insights:
                memory_entry.dream_associations.extend(relevant_insights)

            self.logger.debug(f"Consolidated memory {memory_entry.memory_id} through dream processing")
            return True

        except Exception as e:
            self.logger.error(f"Failed to consolidate memory {memory_entry.memory_id}: {e}")
            return False

    async def _apply_dream_transformations(
        self, memory_entry: DreamMemoryEntry, dream_experience: DreamExperience
    ) -> list[dict[str, Any]]:
        """Apply dream-based transformations to memory"""

        transformations = []

        # Apply symbolic transformations
        symbolic_rate = self.integration_config["symbolic_transformation_rate"]
        if memory_entry.dream_relevance > symbolic_rate:
            transformation = {
                "type": "symbolic_enhancement",
                "symbols_added": len(memory_entry.symbolic_content.get("abstract_concepts", [])),
                "transformation_strength": memory_entry.dream_relevance,
            }
            transformations.append(transformation)

        # Apply emotional transformations
        for theme, strength in dream_experience.emotional_themes.items():
            if strength > 0.6:
                transformation = {"type": "emotional_integration", "theme": theme, "integration_strength": strength}
                transformations.append(transformation)

        return transformations

    async def _create_dream_associations(
        self, memory_entry: DreamMemoryEntry, dream_experience: DreamExperience
    ) -> list[str]:
        """Create new associations through dream processing"""

        new_associations = []

        # Associate with other memories in the same dream
        for other_memory_id in dream_experience.participating_memories:
            if other_memory_id != memory_entry.memory_id:
                association = f"dream_link_{other_memory_id}"
                if association not in memory_entry.dream_associations:
                    memory_entry.dream_associations.append(association)
                    new_associations.append(association)

        # Associate with dream insights
        for insight in dream_experience.insights_generated:
            insight_association = f"insight_{insight[:20]}"  # Truncated for brevity
            if insight_association not in memory_entry.dream_associations:
                memory_entry.dream_associations.append(insight_association)
                new_associations.append(insight_association)

        return new_associations

    async def _integrate_dream_insights(self, dream_experience: DreamExperience) -> list[dict[str, Any]]:
        """Integrate dream insights into memory system"""

        integrated_insights = []

        for insight in dream_experience.insights_generated:
            insight_data = {
                "insight_content": insight,
                "dream_id": dream_experience.dream_id,
                "insight_type": "dream_generated",
                "relevance_score": 0.8,
                "integration_timestamp": datetime.now(timezone.utc).isoformat(),
            }
            integrated_insights.append(insight_data)

        return integrated_insights

    async def _calculate_consolidation_quality(
        self, dream_experience: DreamExperience, consolidation_results: dict[str, Any]
    ) -> float:
        """Calculate the quality of dream consolidation"""

        quality_factors = []

        # Success rate factor
        total_memories = len(dream_experience.participating_memories)
        consolidated_memories = consolidation_results["memories_consolidated"]
        success_rate = consolidated_memories / total_memories if total_memories > 0 else 0.0
        quality_factors.append(success_rate * 0.4)

        # Transformation richness
        transformations = consolidation_results["memories_transformed"]
        transformation_rate = transformations / total_memories if total_memories > 0 else 0.0
        quality_factors.append(min(1.0, transformation_rate) * 0.3)

        # Insight generation
        insights = consolidation_results["insights_integrated"]
        insight_density = insights / total_memories if total_memories > 0 else 0.0
        quality_factors.append(min(1.0, insight_density * 2) * 0.2)

        # Association creation
        associations = consolidation_results["new_associations"]
        association_density = associations / total_memories if total_memories > 0 else 0.0
        quality_factors.append(min(1.0, association_density) * 0.1)

        return sum(quality_factors)

    def _is_valid_state_transition(self, from_state: DreamState, to_state: DreamState) -> bool:
        """Check if dream state transition is valid"""

        # Define valid transitions
        valid_transitions = {
            DreamState.AWAKE: [DreamState.DROWSY],
            DreamState.DROWSY: [DreamState.AWAKE, DreamState.LIGHT_SLEEP],
            DreamState.LIGHT_SLEEP: [DreamState.DROWSY, DreamState.DEEP_SLEEP, DreamState.REM_SLEEP],
            DreamState.DEEP_SLEEP: [DreamState.LIGHT_SLEEP, DreamState.REM_SLEEP],
            DreamState.REM_SLEEP: [DreamState.LIGHT_SLEEP, DreamState.LUCID_DREAMING, DreamState.DROWSY],
            DreamState.LUCID_DREAMING: [DreamState.REM_SLEEP, DreamState.AWAKE],
        }

        return to_state in valid_transitions.get(from_state, [])

    async def _process_state_transition(self, from_state: DreamState, to_state: DreamState):
        """Process dream state transition"""

        self.logger.debug(f"Processing dream state transition: {from_state.name} -> {to_state.name}")

        # State-specific transition processing
        if to_state == DreamState.REM_SLEEP:
            # Prepare for active dream processing
            await self._prepare_rem_processing()
        elif to_state == DreamState.AWAKE:
            # Finalize dream processing
            await self._finalize_dream_processing()

    async def _prepare_rem_processing(self):
        """Prepare for REM sleep dream processing"""
        self.logger.debug("Preparing for REM sleep processing")
        # Enhanced memory processing in REM state

    async def _finalize_dream_processing(self):
        """Finalize dream processing when returning to awake state"""
        self.logger.debug("Finalizing dream processing")
        # Consolidate dream results

    async def _monitor_integration_health(self):
        """Monitor health of dream-memory integration"""

        # Check for system overload
        if len(self.active_dream_memories) > self.integration_config["max_dream_memories"] * 1.2:
            self.logger.warning("Dream memory system approaching overload")

        # Check integration success rate
        if self.integration_metrics["total_dream_sessions"] > 10:
            success_rate = (
                self.integration_metrics["successful_integrations"] / self.integration_metrics["total_dream_sessions"]
            )
            if success_rate < 0.7:
                self.logger.warning(f"Dream integration success rate low: {success_rate:.2f}")

    async def _analyze_memory_dream_coupling(self) -> float:
        """Analyze the coupling strength between memory and dream systems"""

        # Calculate based on successful integrations and processing efficiency
        if self.integration_metrics["total_dream_sessions"] == 0:
            return 0.5  # Default coupling

        success_rate = (
            self.integration_metrics["successful_integrations"] / self.integration_metrics["total_dream_sessions"]
        )

        processing_efficiency = self.integration_metrics["memories_consolidated"] / max(
            1, self.integration_metrics["total_dream_sessions"] * 10
        )

        coupling_strength = (success_rate + processing_efficiency) / 2.0
        return min(1.0, coupling_strength)

    async def _calculate_memory_dream_correlation(self) -> float:
        """Calculate correlation between memory importance and dream processing"""

        # Simplified correlation calculation
        correlations = []

        for memory in self.active_dream_memories.values():
            # Correlation between importance and dream relevance
            importance = getattr(memory, "importance", 0.5)  # Would come from memory system
            correlation = abs(importance - memory.dream_relevance)
            correlations.append(1.0 - correlation)  # Higher correlation = lower difference

        return sum(correlations) / len(correlations) if correlations else 0.5

    async def _identify_coupling_optimizations(self) -> list[dict[str, Any]]:
        """Identify opportunities to optimize memory-dream coupling"""

        optimizations = []

        # Check memory selection strategy
        if self.integration_config["memory_selection_strategy"] == "importance_emotional":
            current_success = self.integration_metrics.get("successful_integrations", 0)
            total_sessions = self.integration_metrics.get("total_dream_sessions", 1)

            if current_success / total_sessions < 0.8:
                optimizations.append(
                    {
                        "type": "selection_strategy_adjustment",
                        "current_strategy": "importance_emotional",
                        "suggested_strategy": "relevance_priority",
                        "expected_improvement": 0.15,
                    }
                )

        # Check consolidation threshold
        if self.integration_config["consolidation_threshold"] > 0.8:
            optimizations.append(
                {
                    "type": "threshold_adjustment",
                    "parameter": "consolidation_threshold",
                    "current_value": self.integration_config["consolidation_threshold"],
                    "suggested_value": 0.7,
                    "expected_improvement": 0.1,
                }
            )

        return optimizations

    async def _apply_coupling_optimization(self, optimization: dict[str, Any]):
        """Apply a specific coupling optimization"""

        opt_type = optimization["type"]

        if opt_type == "selection_strategy_adjustment":
            self.integration_config["memory_selection_strategy"] = optimization["suggested_strategy"]
            self.logger.info(f"Updated memory selection strategy to {optimization['suggested_strategy']}")

        elif opt_type == "threshold_adjustment":
            parameter = optimization["parameter"]
            new_value = optimization["suggested_value"]
            self.integration_config[parameter] = new_value
            self.logger.info(f"Updated {parameter} to {new_value}")

    def _calculate_dream_session_rate(self) -> float:
        """Calculate dream sessions per hour"""
        # Simplified calculation - would use actual timing data
        return self.integration_metrics["total_dream_sessions"] / 24.0  # Assume 24 hour period

    def _calculate_consolidation_efficiency(self) -> float:
        """Calculate memory consolidation efficiency"""
        total_sessions = self.integration_metrics["total_dream_sessions"]
        if total_sessions == 0:
            return 0.0

        return self.integration_metrics["memories_consolidated"] / (total_sessions * 10.0)  # Expected 10 per session

    def _calculate_consciousness_integration_rate(self) -> float:
        """Calculate consciousness integration rate"""
        total_events = self.integration_metrics["consciousness_feedback_events"]
        total_sessions = self.integration_metrics["total_dream_sessions"]

        if total_sessions == 0:
            return 0.0

        return total_events / total_sessions  # Events per session

    async def _initialize_dream_memory_selection(self):
        """Initialize dream memory selection system"""
        self.logger.debug("Initializing dream memory selection system")
        # Setup selection algorithms and thresholds


# Global instance
_dream_memory_integrator = None


def get_dream_memory_integrator() -> DreamMemoryIntegrator:
    """Get or create dream memory integrator singleton"""
    global _dream_memory_integrator
    if _dream_memory_integrator is None:
        _dream_memory_integrator = DreamMemoryIntegrator()
    return _dream_memory_integrator
