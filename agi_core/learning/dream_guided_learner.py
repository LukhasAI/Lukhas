"""
Dream-Guided Learning System for AGI

Integrates dream processing with learning mechanisms for creative
and intuitive learning beyond traditional supervised approaches.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

import numpy as np

from ..memory.dream_memory import DreamInsightType, DreamMemoryBridge, DreamPhase
from ..memory.vector_memory import MemoryImportance, MemoryType, MemoryVector, VectorMemoryStore
from ..orchestration.model_router import ModelRouter, RoutingRequest, TaskType

logger = logging.getLogger(__name__)


class LearningMode(Enum):
    """Different modes of dream-guided learning."""

    EXPLORATORY = "exploratory"  # Free-form exploration and discovery
    TARGETED = "targeted"  # Goal-directed learning
    CREATIVE = "creative"  # Creative synthesis and innovation
    CONSOLIDATION = "consolidation"  # Memory consolidation and strengthening
    REFLECTION = "reflection"  # Self-reflective learning
    INTUITIVE = "intuitive"  # Intuition-based pattern recognition


class LearningPhase(Enum):
    """Phases of the learning process."""

    PREPARATION = "preparation"  # Prepare for learning
    EXPLORATION = "exploration"  # Explore new information
    ASSIMILATION = "assimilation"  # Integrate new knowledge
    PRACTICE = "practice"  # Practice and reinforce
    REFLECTION = "reflection"  # Reflect on learning
    INTEGRATION = "integration"  # Integrate with existing knowledge


@dataclass
class LearningObjective:
    """Learning objective with success criteria."""

    objective_id: str
    description: str
    target_concepts: list[str]
    success_criteria: dict[str, float]  # Criteria and thresholds
    priority: float = 1.0
    deadline: Optional[datetime] = None
    constellation_alignment: dict[str, float] = field(default_factory=dict)


@dataclass
class LearningOutcome:
    """Result of a learning session."""

    outcome_id: str
    session_id: str
    concepts_learned: list[str]
    skills_acquired: list[str]
    insights_generated: list[str]
    confidence_score: float
    learning_effectiveness: float  # How effective was the learning (0-1)
    retention_prediction: float  # Predicted retention (0-1)
    transfer_potential: float  # Potential for transfer to other domains (0-1)
    dream_contributions: list[str]  # Contributions from dream processing


@dataclass
class LearningSession:
    """Dream-guided learning session."""

    session_id: str
    mode: LearningMode
    phase: LearningPhase
    objectives: list[LearningObjective]

    # Session state
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None

    # Learning content
    source_materials: list[str] = field(default_factory=list)  # Memory IDs or external sources
    generated_insights: list[dict[str, Any]] = field(default_factory=list)
    dream_sessions: list[str] = field(default_factory=list)  # Dream session IDs

    # Outcomes and metrics
    learning_outcomes: list[LearningOutcome] = field(default_factory=list)
    success_score: Optional[float] = None
    engagement_score: Optional[float] = None
    creativity_score: Optional[float] = None

    # Error tracking
    errors_encountered: list[str] = field(default_factory=list)
    recovery_strategies: list[str] = field(default_factory=list)


class DreamGuidedLearner:
    """
    Advanced Dream-Guided Learning System for AGI

    Combines traditional learning approaches with dream-enhanced creativity
    and intuition for more human-like learning experiences.
    """

    def __init__(self, memory_store: VectorMemoryStore, dream_bridge: DreamMemoryBridge, model_router: ModelRouter):
        self.memory_store = memory_store
        self.dream_bridge = dream_bridge
        self.model_router = model_router

        # Learning state
        self.active_sessions: dict[str, LearningSession] = {}
        self.completed_sessions: list[LearningSession] = []
        self.learning_history: list[dict[str, Any]] = []

        # Learning parameters
        self.dream_integration_weight = 0.3  # How much to weight dream insights
        self.creativity_threshold = 0.7  # Threshold for creative learning
        self.consolidation_interval_hours = 24  # How often to consolidate learning
        self.retention_decay_rate = 0.1  # Learning retention decay rate

        # Learning strategies
        self.learning_strategies = {
            LearningMode.EXPLORATORY: self._exploratory_learning,
            LearningMode.TARGETED: self._targeted_learning,
            LearningMode.CREATIVE: self._creative_learning,
            LearningMode.CONSOLIDATION: self._consolidation_learning,
            LearningMode.REFLECTION: self._reflection_learning,
            LearningMode.INTUITIVE: self._intuitive_learning,
        }

        # Statistics
        self.stats = {
            "total_sessions": 0,
            "successful_sessions": 0,
            "concepts_learned": 0,
            "skills_acquired": 0,
            "dream_enhanced_sessions": 0,
            "avg_learning_effectiveness": 0.0,
            "learning_modes": {mode.value: 0 for mode in LearningMode},
        }

    async def start_learning_session(
        self,
        objectives: list[LearningObjective],
        mode: LearningMode = LearningMode.TARGETED,
        source_materials: Optional[list[str]] = None,
    ) -> str:
        """Start a new dream-guided learning session."""

        session_id = f"learn_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{len(self.active_sessions)}"

        session = LearningSession(
            session_id=session_id,
            mode=mode,
            phase=LearningPhase.PREPARATION,
            objectives=objectives,
            start_time=datetime.now(timezone.utc),
            source_materials=source_materials or [],
        )

        self.active_sessions[session_id] = session

        # Update statistics
        self.stats["total_sessions"] += 1
        self.stats["learning_modes"][mode.value] += 1

        logger.info(f"Started learning session {session_id} in {mode.value} mode")

        # Begin learning process
        await self._execute_learning_session(session)

        return session_id

    async def _execute_learning_session(self, session: LearningSession):
        """Execute the learning session through all phases."""

        try:
            # Phase 1: Preparation
            session.phase = LearningPhase.PREPARATION
            await self._prepare_learning(session)

            # Phase 2: Exploration
            session.phase = LearningPhase.EXPLORATION
            await self._explore_content(session)

            # Phase 3: Dream-enhanced processing
            if session.mode in [LearningMode.CREATIVE, LearningMode.INTUITIVE, LearningMode.EXPLORATORY]:
                await self._integrate_dream_processing(session)

            # Phase 4: Assimilation
            session.phase = LearningPhase.ASSIMILATION
            await self._assimilate_learning(session)

            # Phase 5: Practice (if applicable)
            if session.mode != LearningMode.REFLECTION:
                session.phase = LearningPhase.PRACTICE
                await self._practice_skills(session)

            # Phase 6: Reflection
            session.phase = LearningPhase.REFLECTION
            await self._reflect_on_learning(session)

            # Phase 7: Integration
            session.phase = LearningPhase.INTEGRATION
            await self._integrate_knowledge(session)

            # Evaluate session success
            await self._evaluate_session(session)

        except Exception as e:
            session.errors_encountered.append(str(e))
            logger.error(f"Error in learning session {session.session_id}: {e}")

            # Attempt recovery
            await self._recover_from_error(session, e)

        finally:
            # Complete session
            await self._complete_session(session)

    async def _prepare_learning(self, session: LearningSession):
        """Prepare for learning by gathering context and setting expectations."""

        # Gather relevant existing knowledge
        relevant_memories = []
        for objective in session.objectives:
            for concept in objective.target_concepts:
                # Search for related memories
                results = await self.memory_store.search_similar(
                    query_vector=await self._get_concept_vector(concept),
                    k=10,
                    memory_types=[MemoryType.SEMANTIC, MemoryType.EPISODIC, MemoryType.PROCEDURAL],
                )
                relevant_memories.extend([r.memory.id for r in results])

        session.source_materials.extend(relevant_memories)

        # Set learning context based on constellation alignment
        for objective in session.objectives:
            if objective.constellation_alignment:
                session.generated_insights.append(
                    {
                        "type": "context_setting",
                        "content": f"Learning objective aligned with constellation: {objective.constellation_alignment}",
                        "phase": "preparation",
                    }
                )

    async def _explore_content(self, session: LearningSession):
        """Explore learning content and generate initial insights."""

        learning_strategy = self.learning_strategies.get(session.mode)
        if learning_strategy:
            await learning_strategy(session)

        # Generate exploration insights
        for material_id in session.source_materials:
            memory = await self.memory_store.get_memory(material_id)
            if memory:
                # Analyze content for learning opportunities
                insight = await self._analyze_for_learning(memory, session.objectives)
                if insight:
                    session.generated_insights.append(insight)

    async def _integrate_dream_processing(self, session: LearningSession):
        """Integrate dream processing for enhanced learning."""

        # Select relevant memories for dream processing
        dream_targets = session.source_materials[:10]  # Limit to top 10 for efficiency

        # Initiate dream session for creative insights
        dream_phase = DreamPhase.CREATIVITY if session.mode == LearningMode.CREATIVE else DreamPhase.SYNTHESIS

        dream_session_id = await self.dream_bridge.initiate_dream_session(
            target_memories=dream_targets, phase=dream_phase, session_params={"learning_context": True}
        )

        session.dream_sessions.append(dream_session_id)
        self.stats["dream_enhanced_sessions"] += 1

        # Wait for dream processing to complete
        await asyncio.sleep(2)  # Simplified wait - in practice, would check dream session status

        # Retrieve dream insights
        dream_session = self.dream_bridge.get_dream_session(dream_session_id)
        if dream_session and dream_session.success:
            for insight in dream_session.insights_generated:
                session.generated_insights.append(
                    {
                        "type": "dream_insight",
                        "content": insight.get("content", ""),
                        "confidence": insight.get("confidence", 0.5),
                        "phase": "dream_processing",
                        "dream_type": insight.get("type", "general"),
                    }
                )

            # Apply dream patterns to learning
            for pattern in dream_session.patterns_discovered:
                await self._apply_dream_pattern_to_learning(pattern, session)

    async def _assimilate_learning(self, session: LearningSession):
        """Assimilate and integrate new learning."""

        concepts_learned = set()
        skills_acquired = set()

        # Process generated insights
        for insight in session.generated_insights:
            # Extract learning from insights
            if insight.get("type") == "concept_discovery":
                concepts_learned.add(insight.get("concept", ""))
            elif insight.get("type") == "skill_identification":
                skills_acquired.add(insight.get("skill", ""))

        # Create memories for new learning
        for concept in concepts_learned:
            await self._create_learning_memory(concept, "concept", session)

        for skill in skills_acquired:
            await self._create_learning_memory(skill, "skill", session)

        # Update session with learning outcomes
        outcome = LearningOutcome(
            outcome_id=f"outcome_{session.session_id}_{len(session.learning_outcomes)}",
            session_id=session.session_id,
            concepts_learned=list(concepts_learned),
            skills_acquired=list(skills_acquired),
            insights_generated=[i.get("content", "") for i in session.generated_insights],
            confidence_score=self._calculate_confidence_score(session),
            learning_effectiveness=0.0,  # Will be calculated later
            retention_prediction=0.0,  # Will be calculated later
            transfer_potential=0.0,  # Will be calculated later
            dream_contributions=[
                i.get("content", "") for i in session.generated_insights if i.get("type") == "dream_insight"
            ],
        )

        session.learning_outcomes.append(outcome)

    async def _practice_skills(self, session: LearningSession):
        """Practice and reinforce learned skills."""

        # Generate practice scenarios
        for outcome in session.learning_outcomes:
            for skill in outcome.skills_acquired:
                practice_insight = {
                    "type": "practice_opportunity",
                    "content": f"Practice opportunity identified for skill: {skill}",
                    "skill": skill,
                    "phase": "practice",
                    "confidence": 0.8,
                }
                session.generated_insights.append(practice_insight)

    async def _reflect_on_learning(self, session: LearningSession):
        """Reflect on the learning process and outcomes."""

        # Generate reflection insights
        reflection_content = f"Learning session reflection: {session.mode.value} mode"
        if session.learning_outcomes:
            total_concepts = sum(len(o.concepts_learned) for o in session.learning_outcomes)
            total_skills = sum(len(o.skills_acquired) for o in session.learning_outcomes)
            reflection_content += f". Learned {total_concepts} concepts and {total_skills} skills."

        reflection_insight = {
            "type": "reflection",
            "content": reflection_content,
            "phase": "reflection",
            "confidence": 0.9,
        }
        session.generated_insights.append(reflection_insight)

        # Update statistics
        if session.learning_outcomes:
            self.stats["concepts_learned"] += sum(len(o.concepts_learned) for o in session.learning_outcomes)
            self.stats["skills_acquired"] += sum(len(o.skills_acquired) for o in session.learning_outcomes)

    async def _integrate_knowledge(self, session: LearningSession):
        """Integrate new knowledge with existing knowledge base."""

        # Connect new learning with existing memories
        for outcome in session.learning_outcomes:
            for concept in outcome.concepts_learned:
                # Find related existing concepts
                concept_vector = await self._get_concept_vector(concept)
                if concept_vector is not None:
                    similar_memories = await self.memory_store.search_similar(
                        query_vector=concept_vector, k=5, memory_types=[MemoryType.SEMANTIC, MemoryType.CONCEPTUAL]
                    )

                    # Create associative links
                    for result in similar_memories:
                        if concept not in result.memory.related_memories:
                            result.memory.related_memories.append(f"learned_concept_{concept}")

        # Update constellation alignments based on learning
        for objective in session.objectives:
            for star, alignment in objective.constellation_alignment.items():
                # Strengthen relevant memories
                for material_id in session.source_materials:
                    memory = await self.memory_store.get_memory(material_id)
                    if memory:
                        current_alignment = memory.constellation_tags.get(star, 0.0)
                        memory.constellation_tags[star] = min(1.0, current_alignment + alignment * 0.1)

    async def _evaluate_session(self, session: LearningSession):
        """Evaluate the success of the learning session."""

        total_effectiveness = 0.0

        for outcome in session.learning_outcomes:
            # Calculate learning effectiveness
            concepts_score = len(outcome.concepts_learned) / max(
                1, sum(len(obj.target_concepts) for obj in session.objectives)
            )
            skills_score = len(outcome.skills_acquired) / max(1, len(session.objectives))
            dream_boost = len(outcome.dream_contributions) * self.dream_integration_weight

            effectiveness = min(1.0, concepts_score + skills_score + dream_boost)
            outcome.learning_effectiveness = effectiveness

            # Predict retention based on multiple factors
            outcome.retention_prediction = self._predict_retention(outcome, session)

            # Assess transfer potential
            outcome.transfer_potential = self._assess_transfer_potential(outcome, session)

            total_effectiveness += effectiveness

        # Calculate overall session success
        if session.learning_outcomes:
            session.success_score = total_effectiveness / len(session.learning_outcomes)

            # Determine if session was successful
            if session.success_score > 0.6:
                self.stats["successful_sessions"] += 1

            # Update average learning effectiveness
            current_avg = self.stats["avg_learning_effectiveness"]
            total_sessions = self.stats["total_sessions"]
            self.stats["avg_learning_effectiveness"] = (
                current_avg * (total_sessions - 1) + session.success_score
            ) / total_sessions

    async def _complete_session(self, session: LearningSession):
        """Complete the learning session."""

        session.end_time = datetime.now(timezone.utc)
        if session.end_time:
            duration = session.end_time - session.start_time
            session.duration_minutes = int(duration.total_seconds() / 60)

        # Move from active to completed
        if session.session_id in self.active_sessions:
            del self.active_sessions[session.session_id]

        self.completed_sessions.append(session)

        # Create session summary memory
        await self._create_session_summary_memory(session)

        logger.info(
            f"Completed learning session {session.session_id} with success score: {session.success_score or 0.0:.2f}"
        )

    # Learning strategy implementations
    async def _exploratory_learning(self, session: LearningSession):
        """Free-form exploratory learning."""

        # Randomly explore related concepts
        for material_id in session.source_materials[:5]:  # Limit exploration
            memory = await self.memory_store.get_memory(material_id)
            if memory:
                # Get associative memories for exploration
                associated = await self.memory_store.get_associative_memories(material_id, depth=2)

                for assoc_memory in associated[:3]:  # Explore top 3 associations
                    session.generated_insights.append(
                        {
                            "type": "exploration_discovery",
                            "content": f"Explored connection: {memory.content[:50]}... -> {assoc_memory.content[:50]}...",
                            "phase": "exploration",
                            "confidence": 0.7,
                        }
                    )

    async def _targeted_learning(self, session: LearningSession):
        """Goal-directed targeted learning."""

        for objective in session.objectives:
            for concept in objective.target_concepts:
                # Use model router to get detailed information about concept
                request = RoutingRequest(
                    content=f"Explain the concept: {concept}",
                    task_type=TaskType.ANALYTICAL,
                    constellation_context=objective.constellation_alignment,
                )

                try:
                    decision, response = await self.model_router.route_request(request)

                    session.generated_insights.append(
                        {
                            "type": "concept_discovery",
                            "content": response.content,
                            "concept": concept,
                            "phase": "targeted_learning",
                            "confidence": response.quality_score,
                            "model_used": response.model_used,
                        }
                    )

                except Exception as e:
                    session.errors_encountered.append(f"Failed to learn concept {concept}: {e}")

    async def _creative_learning(self, session: LearningSession):
        """Creative synthesis and innovative learning."""

        # Combine disparate concepts for creative insights
        materials = [await self.memory_store.get_memory(mid) for mid in session.source_materials[:5]]
        materials = [m for m in materials if m is not None]

        for i, memory1 in enumerate(materials):
            for memory2 in materials[i + 1 :]:
                # Look for creative connections
                if memory1.memory_type != memory2.memory_type:  # Cross-domain creativity
                    session.generated_insights.append(
                        {
                            "type": "creative_connection",
                            "content": f"Creative synthesis: {memory1.content[:30]}... + {memory2.content[:30]}...",
                            "phase": "creative_learning",
                            "confidence": 0.6,
                            "memory1_id": memory1.id,
                            "memory2_id": memory2.id,
                        }
                    )

    async def _consolidation_learning(self, session: LearningSession):
        """Memory consolidation and strengthening."""

        # Strengthen related memories
        for material_id in session.source_materials:
            memory = await self.memory_store.get_memory(material_id, reinforce=True)
            if memory:
                memory.reinforce(0.2)  # Strong consolidation boost

                session.generated_insights.append(
                    {
                        "type": "consolidation",
                        "content": f"Consolidated memory: {memory.content[:50]}...",
                        "phase": "consolidation",
                        "confidence": 0.9,
                        "memory_id": memory.id,
                    }
                )

    async def _reflection_learning(self, session: LearningSession):
        """Self-reflective learning and meta-cognition."""

        # Analyze learning patterns and strategies
        recent_sessions = self.completed_sessions[-5:]  # Last 5 sessions

        if recent_sessions:
            avg_success = np.mean([s.success_score for s in recent_sessions if s.success_score])
            most_effective_mode = max(
                set(s.mode for s in recent_sessions),
                key=lambda mode: np.mean(
                    [s.success_score for s in recent_sessions if s.mode == mode and s.success_score]
                ),
            )

            session.generated_insights.append(
                {
                    "type": "meta_learning",
                    "content": f"Reflection: Recent learning success rate: {avg_success:.2f}, Most effective mode: {most_effective_mode.value}",
                    "phase": "reflection",
                    "confidence": 0.8,
                }
            )

    async def _intuitive_learning(self, session: LearningSession):
        """Intuition-based pattern recognition learning."""

        # Use dream insights and pattern matching for intuitive learning
        for material_id in session.source_materials:
            memory = await self.memory_store.get_memory(material_id)
            if memory:
                # Look for intuitive patterns in constellation alignments
                strong_alignments = [star for star, alignment in memory.constellation_tags.items() if alignment > 0.7]

                if strong_alignments:
                    session.generated_insights.append(
                        {
                            "type": "intuitive_pattern",
                            "content": f"Intuitive pattern recognized: Strong {', '.join(strong_alignments)} alignment",
                            "phase": "intuitive_learning",
                            "confidence": max(memory.constellation_tags[star] for star in strong_alignments),
                            "pattern_stars": strong_alignments,
                        }
                    )

    # Helper methods
    async def _get_concept_vector(self, concept: str) -> Optional[np.ndarray]:
        """Get vector representation of a concept."""
        # This would normally use proper text embedding
        # For now, return a normalized random vector
        vector = np.random.normal(0, 1, self.memory_store.embedding_dimension)
        return vector / np.linalg.norm(vector)

    async def _analyze_for_learning(
        self, memory: MemoryVector, objectives: list[LearningObjective]
    ) -> Optional[dict[str, Any]]:
        """Analyze memory content for learning opportunities."""

        # Simple analysis based on memory type and constellation alignment
        learning_score = 0.0

        for objective in objectives:
            for concept in objective.target_concepts:
                if concept.lower() in memory.content.lower():
                    learning_score += 0.3

            # Check constellation alignment
            for star, target_alignment in objective.constellation_alignment.items():
                memory_alignment = memory.constellation_tags.get(star, 0.0)
                if memory_alignment >= target_alignment * 0.8:  # 80% threshold
                    learning_score += 0.2

        if learning_score > 0.5:
            return {
                "type": "learning_opportunity",
                "content": f"Learning opportunity in: {memory.content[:100]}...",
                "score": learning_score,
                "memory_id": memory.id,
                "phase": "exploration",
            }

        return None

    async def _apply_dream_pattern_to_learning(self, pattern, session: LearningSession):
        """Apply dream pattern insights to learning process."""

        if pattern.pattern_type == DreamInsightType.CREATIVE_CONNECTION:
            session.generated_insights.append(
                {
                    "type": "dream_creative_insight",
                    "content": f"Dream revealed creative connection: {pattern.insight_content}",
                    "phase": "dream_integration",
                    "confidence": pattern.confidence,
                    "pattern_id": pattern.pattern_id,
                }
            )

        elif pattern.pattern_type == DreamInsightType.PATTERN_DISCOVERY:
            session.generated_insights.append(
                {
                    "type": "dream_pattern_insight",
                    "content": f"Dream discovered pattern: {pattern.insight_content}",
                    "phase": "dream_integration",
                    "confidence": pattern.confidence,
                    "pattern_id": pattern.pattern_id,
                }
            )

    async def _create_learning_memory(self, content: str, content_type: str, session: LearningSession):
        """Create a memory for new learning."""

        memory_type = MemoryType.SEMANTIC if content_type == "concept" else MemoryType.PROCEDURAL

        # Create vector representation
        vector = await self._get_concept_vector(content)
        if vector is None:
            return

        # Determine constellation alignment based on session objectives
        constellation_tags = {}
        for objective in session.objectives:
            for star, alignment in objective.constellation_alignment.items():
                constellation_tags[star] = constellation_tags.get(star, 0.0) + alignment * 0.1

        learning_memory = MemoryVector(
            id=f"learned_{content_type}_{session.session_id}_{len(session.learning_outcomes)}",
            content=f"Learned {content_type}: {content}",
            vector=vector,
            memory_type=memory_type,
            importance=MemoryImportance.HIGH,  # New learning is important
            timestamp=datetime.now(timezone.utc),
            constellation_tags=constellation_tags,
            source_context=f"Learning session: {session.session_id}",
            confidence=0.8,
        )

        await self.memory_store.add_memory(learning_memory)

    def _calculate_confidence_score(self, session: LearningSession) -> float:
        """Calculate confidence in learning outcomes."""

        if not session.generated_insights:
            return 0.5

        confidences = [insight.get("confidence", 0.5) for insight in session.generated_insights]
        base_confidence = np.mean(confidences)

        # Boost for dream integration
        dream_insights = [i for i in session.generated_insights if i.get("type", "").startswith("dream")]
        dream_boost = len(dream_insights) * 0.05

        # Boost for multiple learning modes
        unique_phases = set(i.get("phase", "") for i in session.generated_insights)
        diversity_boost = len(unique_phases) * 0.02

        return min(1.0, base_confidence + dream_boost + diversity_boost)

    def _predict_retention(self, outcome: LearningOutcome, session: LearningSession) -> float:
        """Predict how well learning will be retained."""

        base_retention = 0.7

        # Higher retention for concepts with multiple reinforcements
        concept_reinforcement = len(outcome.concepts_learned) * 0.05
        skill_reinforcement = len(outcome.skills_acquired) * 0.1  # Skills generally better retained

        # Dream contribution boost
        dream_boost = len(outcome.dream_contributions) * 0.05

        # Session engagement boost
        insight_diversity = len(set(i.get("type", "") for i in session.generated_insights))
        engagement_boost = insight_diversity * 0.02

        retention = base_retention + concept_reinforcement + skill_reinforcement + dream_boost + engagement_boost

        return min(1.0, retention)

    def _assess_transfer_potential(self, outcome: LearningOutcome, session: LearningSession) -> float:
        """Assess potential for transferring learning to other domains."""

        base_transfer = 0.5

        # Higher transfer potential for abstract concepts
        abstract_concepts = len(
            [
                c
                for c in outcome.concepts_learned
                if any(keyword in c.lower() for keyword in ["pattern", "principle", "strategy"])
            ]
        )
        abstract_boost = abstract_concepts * 0.1

        # Creative learning has higher transfer potential
        creative_boost = 0.15 if session.mode == LearningMode.CREATIVE else 0.0

        # Dream insights often have good transfer potential
        dream_boost = len(outcome.dream_contributions) * 0.05

        transfer = base_transfer + abstract_boost + creative_boost + dream_boost

        return min(1.0, transfer)

    async def _create_session_summary_memory(self, session: LearningSession):
        """Create a summary memory for the learning session."""

        summary_content = f"Learning session: {session.mode.value} mode\n"
        summary_content += f"Duration: {session.duration_minutes or 0} minutes\n"
        summary_content += f"Success score: {session.success_score or 0.0:.2f}\n"

        if session.learning_outcomes:
            total_concepts = sum(len(o.concepts_learned) for o in session.learning_outcomes)
            total_skills = sum(len(o.skills_acquired) for o in session.learning_outcomes)
            summary_content += f"Learned {total_concepts} concepts and {total_skills} skills\n"

        if session.dream_sessions:
            summary_content += f"Dream-enhanced with {len(session.dream_sessions)} dream sessions\n"

        # Create vector representation
        vector = np.random.normal(0, 1, self.memory_store.embedding_dimension)
        vector = vector / np.linalg.norm(vector)

        # Aggregate constellation alignment from objectives
        constellation_tags = {}
        for objective in session.objectives:
            for star, alignment in objective.constellation_alignment.items():
                constellation_tags[star] = max(constellation_tags.get(star, 0.0), alignment)

        summary_memory = MemoryVector(
            id=f"learning_summary_{session.session_id}",
            content=summary_content,
            vector=vector,
            memory_type=MemoryType.EPISODIC,
            importance=(
                MemoryImportance.HIGH
                if session.success_score and session.success_score > 0.8
                else MemoryImportance.MEDIUM
            ),
            timestamp=session.end_time or datetime.now(timezone.utc),
            constellation_tags=constellation_tags,
            source_context="Learning session summary",
            confidence=session.success_score or 0.5,
        )

        await self.memory_store.add_memory(summary_memory)

    async def _recover_from_error(self, session: LearningSession, error: Exception):
        """Attempt to recover from learning session errors."""

        recovery_strategy = f"Error recovery: Simplified learning approach due to {type(error).__name__}"
        session.recovery_strategies.append(recovery_strategy)

        # Try simplified learning approach
        if session.source_materials:
            simple_insight = {
                "type": "recovery_insight",
                "content": f"Recovered with simplified analysis of {len(session.source_materials)} materials",
                "phase": "error_recovery",
                "confidence": 0.3,
            }
            session.generated_insights.append(simple_insight)

    def get_learning_stats(self) -> dict[str, Any]:
        """Get comprehensive learning statistics."""

        recent_sessions = self.completed_sessions[-20:] if self.completed_sessions else []

        stats = {
            **self.stats,
            "active_sessions": len(self.active_sessions),
            "completed_sessions": len(self.completed_sessions),
            "recent_performance": {
                "avg_success_score": (
                    np.mean([s.success_score for s in recent_sessions if s.success_score]) if recent_sessions else 0.0
                ),
                "avg_duration_minutes": (
                    np.mean([s.duration_minutes for s in recent_sessions if s.duration_minutes])
                    if recent_sessions
                    else 0.0
                ),
                "dream_integration_rate": len([s for s in recent_sessions if s.dream_sessions])
                / max(1, len(recent_sessions)),
            },
        }

        return stats
