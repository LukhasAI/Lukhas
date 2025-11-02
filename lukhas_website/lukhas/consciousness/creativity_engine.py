#!/usr/bin/env python3
"""
LUKHAS Consciousness CreativityEngine - Production Schema v1.0.0

Implements creative processes engine with divergent/convergent thinking, associative
reasoning, and imaginative synthesis. Part of the Constellation Framework.

T4/0.01% Excellence Standards:
- <50ms p95 creative processing latency
- Guardian-validated creative outputs
- Comprehensive observability and metrics
- Production-grade error handling

Constellation Framework: Spark Star (⚡), Oracle Star (🔮)
"""

from __future__ import annotations

import logging
import random
import time
from typing import Any, Callable, Dict, List, Optional

from opentelemetry import trace
from prometheus_client import Counter, Gauge, Histogram

from .types import (
    DEFAULT_CREATIVITY_CONFIG,
    ConsciousnessState,
    CreativeFlowState,
    CreativeProcessType,
    CreativeTask,
    CreativitySnapshot,
    ImaginationMode,
)

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)

# Prometheus metrics for T4/0.01% observability
creativity_cycles_total = Counter(
    'lukhas_creativity_cycles_total',
    'Total creativity processing cycles',
    ['component', 'process_type']
)

creativity_latency_seconds = Histogram(
    'lukhas_creativity_latency_seconds',
    'Creativity processing latency',
    ['component', 'process_type'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
)

creativity_ideas_generated = Counter(
    'lukhas_creativity_ideas_generated_total',
    'Total creative ideas generated',
    ['component', 'idea_type']
)

creativity_novelty_score = Gauge(
    'lukhas_creativity_novelty_score',
    'Current novelty score',
    ['component']
)

creativity_coherence_score = Gauge(
    'lukhas_creativity_coherence_score',
    'Current coherence score',
    ['component']
)

creativity_guardian_approvals = Counter(
    'lukhas_creativity_guardian_approvals_total',
    'Guardian approval decisions',
    ['component', 'approved']
)

creativity_flow_state = Gauge(
    'lukhas_creativity_flow_state',
    'Current creative flow state (0=blocked, 1=warming, 2=flowing, 3=peak, 4=cooling)',
    ['component']
)


class CreativityEngine:
    """
    Advanced creativity and imagination engine for consciousness system.

    Implements multiple creative processes including divergent thinking, convergent
    reasoning, associative synthesis, and transformative imagination. Provides
    T4/0.01% performance with Guardian validation and comprehensive observability.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None, guardian_validator: Optional[Callable] = None):
        """Initialize creativity engine with configuration and Guardian integration."""
        self.config = {**DEFAULT_CREATIVITY_CONFIG, **(config or {})}
        self.guardian_validator = guardian_validator

        # T4/0.01% performance targets
        self.p95_target_ms = self.config["p95_target_ms"]
        self.min_novelty_threshold = self.config["min_novelty_threshold"]
        self.min_coherence_threshold = self.config["min_coherence_threshold"]
        self.max_ideas_per_cycle = self.config["max_ideas_per_cycle"]
        self.guardian_approval_required = self.config["guardian_approval_required"]

        # Creative state
        self._flow_state: CreativeFlowState = "blocked"
        self._creative_energy = 0.0
        self._imagination_mode: ImaginationMode = "conceptual"
        self._component_id = "CreativityEngine"

        # Creativity knowledge base
        self._concept_network: Dict[str, List[str]] = {}
        self._creative_patterns: List[Dict[str, Any]] = []
        self._inspiration_sources: List[str] = []

        # Performance tracking
        self._cycle_count = 0
        self._processing_times: List[float] = []
        self._quality_scores: List[float] = []
        self._guardian_decisions: List[bool] = []

        # Memory and context
        self._recent_ideas: List[Dict[str, Any]] = []
        self._active_constraints: List[str] = []
        self._synthesis_cache: Dict[str, Any] = {}

    async def generate_ideas(
        self,
        task: CreativeTask,
        consciousness_state: ConsciousnessState,
        context: Optional[Dict[str, Any]] = None
    ) -> CreativitySnapshot:
        """
        Generate creative ideas for a given task using multiple creative processes.

        Args:
            task: Creative task specification
            consciousness_state: Current consciousness state
            context: Additional processing context

        Returns:
            CreativitySnapshot with generated ideas and creative metrics
        """
        start_time = time.time()

        with tracer.start_as_current_span("creativity_generation") as span:
            span.set_attribute("component", self._component_id)
            span.set_attribute("task.id", task.task_id)
            span.set_attribute("task.prompt", task.prompt[:100])  # Truncate for logging
            span.set_attribute("imagination_mode", task.imagination_mode)

            try:
                # Initialize creative session
                snapshot = await self._initialize_creative_session(task, consciousness_state, context)

                # Update flow state based on task and consciousness
                await self._update_flow_state(task, consciousness_state)

                # Execute creative processes based on task preferences
                if task.preferred_process:
                    await self._execute_single_process(task.preferred_process, task, snapshot)
                else:
                    await self._execute_multi_process_cycle(task, snapshot)

                # Perform synthesis and validation
                await self._synthesize_and_validate(snapshot, task)

                # Guardian approval if required
                if self.guardian_approval_required and self.guardian_validator:
                    await self._request_guardian_approvals(snapshot)

                # Finalize metrics and performance
                processing_time = (time.time() - start_time) * 1000
                await self._finalize_snapshot(snapshot, processing_time)

                # Update observability metrics
                self._update_metrics(snapshot, processing_time, task.preferred_process or "multi")

                span.set_attribute("ideas_generated", len(snapshot.ideas))
                span.set_attribute("novelty_score", snapshot.novelty_score)
                span.set_attribute("coherence_score", snapshot.coherence_score)
                span.set_attribute("processing_time_ms", processing_time)
                span.set_attribute("flow_state", snapshot.flow_state)

                return snapshot

            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                logger.error(f"Creativity generation failed: {e}")
                raise

    async def _initialize_creative_session(
        self,
        task: CreativeTask,
        consciousness_state: ConsciousnessState,
        context: Optional[Dict[str, Any]]
    ) -> CreativitySnapshot:
        """Initialize creativity snapshot for processing session."""

        snapshot = CreativitySnapshot(
            flow_state=self._flow_state,
            imagination_mode=task.imagination_mode,
            creative_energy=self._creative_energy,
            inspiration_sources=task.seed_concepts.copy(),
            creative_constraints=task.constraints.copy()
        )

        # Set creative energy based on consciousness level
        base_energy = consciousness_state.level
        awareness_bonus = {"minimal": 0.0, "basic": 0.1, "enhanced": 0.2,
                          "transcendent": 0.3, "unified": 0.4}[consciousness_state.awareness_level]

        self._creative_energy = min(1.0, base_energy + awareness_bonus)
        snapshot.creative_energy = self._creative_energy

        # Initialize concept network for associative processes
        await self._populate_concept_network(task, context)

        return snapshot

    async def _update_flow_state(self, task: CreativeTask, consciousness_state: ConsciousnessState):
        """Update creative flow state based on current conditions."""

        # Base flow calculation
        energy_factor = self._creative_energy
        consciousness_factor = consciousness_state.level
        constraint_factor = max(0.2, 1.0 - (len(task.constraints) / 10.0))

        flow_score = (energy_factor + consciousness_factor + constraint_factor) / 3.0

        # Map flow score to state
        if flow_score < 0.2:
            self._flow_state = "blocked"
        elif flow_score < 0.4:
            self._flow_state = "warming"
        elif flow_score < 0.7:
            self._flow_state = "flowing"
        elif flow_score < 0.9:
            self._flow_state = "peak"
        else:
            self._flow_state = "cooling"

        # Update metrics
        flow_state_values = {"blocked": 0, "warming": 1, "flowing": 2, "peak": 3, "cooling": 4}
        creativity_flow_state.labels(component=self._component_id).set(
            flow_state_values[self._flow_state]
        )

    async def _execute_single_process(
        self,
        process_type: CreativeProcessType,
        task: CreativeTask,
        snapshot: CreativitySnapshot
    ):
        """Execute a single creative process."""

        if process_type == "divergent":
            await self._divergent_thinking(task, snapshot)
        elif process_type == "convergent":
            await self._convergent_thinking(task, snapshot)
        elif process_type == "associative":
            await self._associative_reasoning(task, snapshot)
        elif process_type == "transformative":
            await self._transformative_imagination(task, snapshot)
        elif process_type == "synthesis":
            await self._creative_synthesis(task, snapshot)

    async def _execute_multi_process_cycle(self, task: CreativeTask, snapshot: CreativitySnapshot):
        """Execute multiple creative processes in optimal sequence."""

        # Adaptive process selection based on flow state
        if self._flow_state in ["blocked", "warming"]:
            # Start with divergent to generate raw material
            await self._divergent_thinking(task, snapshot)
            await self._associative_reasoning(task, snapshot)
        elif self._flow_state in ["flowing", "peak"]:
            # Full creative cycle
            await self._divergent_thinking(task, snapshot)
            await self._associative_reasoning(task, snapshot)
            await self._transformative_imagination(task, snapshot)
            await self._convergent_thinking(task, snapshot)
        else:  # cooling
            # Focus on synthesis and refinement
            await self._convergent_thinking(task, snapshot)
            await self._creative_synthesis(task, snapshot)

    async def _divergent_thinking(self, task: CreativeTask, snapshot: CreativitySnapshot):
        """Generate diverse ideas through divergent thinking."""

        with tracer.start_as_current_span("divergent_thinking") as span:
            idea_count = 0
            max_ideas = min(task.min_ideas * 2, self.max_ideas_per_cycle)

            # Generate ideas from multiple perspectives
            perspectives = ["functional", "aesthetic", "theoretical", "practical", "unconventional"]

            for perspective in perspectives:
                if idea_count >= max_ideas:
                    break

                # Generate ideas from this perspective
                ideas = await self._generate_perspective_ideas(task.prompt, perspective, task.context)

                for idea_content in ideas:
                    if idea_count >= max_ideas:
                        break

                    novelty = self._calculate_novelty(idea_content, snapshot.ideas)
                    coherence = self._calculate_coherence(idea_content, task)

                    snapshot.add_idea(
                        idea_type=f"divergent_{perspective}",
                        content=idea_content,
                        novelty=novelty,
                        coherence=coherence
                    )

                    idea_count += 1
                    creativity_ideas_generated.labels(
                        component=self._component_id,
                        idea_type=f"divergent_{perspective}"
                    ).inc()

            # Update divergence metrics
            unique_types = {idea.get("type", "") for idea in snapshot.ideas}
            snapshot.divergence_breadth = min(len(unique_types) / 10.0, 1.0)

            span.set_attribute("ideas_generated", idea_count)
            span.set_attribute("divergence_breadth", snapshot.divergence_breadth)

    async def _convergent_thinking(self, task: CreativeTask, snapshot: CreativitySnapshot):
        """Focus and refine ideas through convergent thinking."""

        with tracer.start_as_current_span("convergent_thinking") as span:
            if not snapshot.ideas:
                return

            # Filter ideas by quality thresholds
            quality_ideas = [
                idea for idea in snapshot.ideas
                if idea.get("novelty", 0.0) >= self.min_novelty_threshold
                and idea.get("coherence", 0.0) >= self.min_coherence_threshold
            ]

            # Rank and select top ideas
            ranked_ideas = sorted(
                quality_ideas,
                key=lambda x: x.get("validation_score", 0.0),
                reverse=True
            )

            # Refine top ideas
            refined_count = 0
            for idea in ranked_ideas[:5]:  # Focus on top 5
                refined_idea = await self._refine_idea(idea, task, snapshot)
                if refined_idea:
                    snapshot.add_idea(
                        idea_type="convergent_refined",
                        content=refined_idea,
                        novelty=idea.get("novelty", 0.0) * 1.1,  # Slight boost for refinement
                        coherence=idea.get("coherence", 0.0) * 1.2
                    )
                    refined_count += 1

            # Calculate convergence efficiency
            if len(snapshot.ideas) > 0:
                high_quality_ratio = len(quality_ideas) / len(snapshot.ideas)
                snapshot.convergence_efficiency = high_quality_ratio

            span.set_attribute("quality_ideas", len(quality_ideas))
            span.set_attribute("refined_ideas", refined_count)
            span.set_attribute("convergence_efficiency", snapshot.convergence_efficiency)

    async def _associative_reasoning(self, task: CreativeTask, snapshot: CreativitySnapshot):
        """Generate ideas through associative connections."""

        with tracer.start_as_current_span("associative_reasoning") as span:
            association_count = 0

            # Create associations from seed concepts
            for seed in task.seed_concepts:
                if association_count >= 10:  # Limit associations
                    break

                related_concepts = self._find_related_concepts(seed)

                for related in related_concepts[:3]:  # Top 3 per seed
                    strength = self._calculate_association_strength(seed, related)

                    if strength > 0.3:  # Minimum threshold
                        snapshot.add_association(seed, related, strength, "semantic")

                        # Generate idea from association
                        association_idea = await self._generate_association_idea(
                            seed, related, task.prompt, task.context
                        )

                        if association_idea:
                            novelty = self._calculate_novelty(association_idea, snapshot.ideas)
                            coherence = self._calculate_coherence(association_idea, task)

                            snapshot.add_idea(
                                idea_type="associative",
                                content=association_idea,
                                novelty=novelty,
                                coherence=coherence
                            )

                            association_count += 1
                            creativity_ideas_generated.labels(
                                component=self._component_id,
                                idea_type="associative"
                            ).inc()

            span.set_attribute("associations_created", len(snapshot.associations))
            span.set_attribute("association_ideas", association_count)

    async def _transformative_imagination(self, task: CreativeTask, snapshot: CreativitySnapshot):
        """Apply transformative processes to existing ideas."""

        with tracer.start_as_current_span("transformative_imagination") as span:
            if not snapshot.ideas:
                return

            transformation_methods = [
                "analogy", "metaphor", "inversion", "amplification", "combination"
            ]

            transformation_count = 0
            for idea in snapshot.ideas[-5:]:  # Transform recent ideas
                for method in transformation_methods:
                    if transformation_count >= 10:
                        break

                    transformed = await self._apply_transformation(
                        idea["content"], method, task, snapshot
                    )

                    if transformed:
                        confidence = self._calculate_transformation_confidence(
                            idea["content"], transformed, method
                        )

                        snapshot.add_transformation(
                            original=str(idea["content"]),
                            transformed=str(transformed),
                            process=method,
                            confidence=confidence
                        )

                        # Create new idea from transformation
                        novelty = self._calculate_novelty(transformed, snapshot.ideas)
                        coherence = self._calculate_coherence(transformed, task)

                        snapshot.add_idea(
                            idea_type=f"transformed_{method}",
                            content=transformed,
                            novelty=novelty,
                            coherence=coherence
                        )

                        transformation_count += 1
                        creativity_ideas_generated.labels(
                            component=self._component_id,
                            idea_type=f"transformed_{method}"
                        ).inc()

            span.set_attribute("transformations_applied", len(snapshot.transformations))
            span.set_attribute("transformation_ideas", transformation_count)

    async def _creative_synthesis(self, task: CreativeTask, snapshot: CreativitySnapshot):
        """Synthesize ideas into coherent creative solutions."""

        with tracer.start_as_current_span("creative_synthesis") as span:
            if len(snapshot.ideas) < 2:
                return

            # Group ideas by similarity for synthesis
            idea_groups = await self._group_similar_ideas(snapshot.ideas)

            synthesis_count = 0
            for group in idea_groups:
                if len(group) >= 2 and synthesis_count < 5:
                    synthesized = await self._synthesize_idea_group(group, task)

                    if synthesized:
                        # Calculate synthesis quality
                        novelty = max(idea.get("novelty", 0.0) for idea in group) * 1.1
                        coherence = sum(idea.get("coherence", 0.0) for idea in group) / len(group)

                        snapshot.add_idea(
                            idea_type="synthesized",
                            content=synthesized,
                            novelty=min(novelty, 1.0),
                            coherence=min(coherence, 1.0)
                        )

                        synthesis_count += 1
                        creativity_ideas_generated.labels(
                            component=self._component_id,
                            idea_type="synthesized"
                        ).inc()

            # Update synthesis quality metric
            if synthesis_count > 0:
                avg_synthesis_quality = sum(
                    idea.get("validation_score", 0.0)
                    for idea in snapshot.ideas
                    if idea.get("type", "").startswith("synthesized")
                ) / synthesis_count
                snapshot.synthesis_quality = avg_synthesis_quality

            span.set_attribute("idea_groups", len(idea_groups))
            span.set_attribute("syntheses_created", synthesis_count)
            span.set_attribute("synthesis_quality", snapshot.synthesis_quality)

    async def _synthesize_and_validate(self, snapshot: CreativitySnapshot, task: CreativeTask):
        """Perform final synthesis and quality validation."""

        # Quality validation checks
        if self.config["quality_validation_enabled"]:
            await self._perform_quality_validation(snapshot, task)

        # Calculate final metrics
        self._calculate_final_metrics(snapshot)

    async def _request_guardian_approvals(self, snapshot: CreativitySnapshot):
        """Request Guardian approval for generated ideas."""

        if not self.guardian_validator:
            return

        for idea in snapshot.ideas:
            try:
                approval_result = await self.guardian_validator({
                    "type": "creative_idea",
                    "content": idea["content"],
                    "novelty": idea.get("novelty", 0.0),
                    "coherence": idea.get("coherence", 0.0)
                })

                approved = approval_result.get("approved", False)
                reason = approval_result.get("reason", "No reason provided")

                idea["guardian_approved"] = approved
                snapshot.add_guardian_approval(idea["id"], approved, reason)

                creativity_guardian_approvals.labels(
                    component=self._component_id,
                    approved=str(approved).lower()
                ).inc()

            except Exception as e:
                logger.warning(f"Guardian approval failed for idea {idea['id']}: {e}")
                idea["guardian_approved"] = False

    async def _finalize_snapshot(self, snapshot: CreativitySnapshot, processing_time: float):
        """Finalize snapshot with performance metrics and cleanup."""

        snapshot.generation_time_ms = processing_time

        # Calculate process efficiency
        if processing_time > 0:
            ideas_per_ms = len(snapshot.ideas) / processing_time
            target_rate = 0.1  # Target: 0.1 ideas per ms
            snapshot.process_efficiency = min(ideas_per_ms / target_rate, 1.0)

        # Memory pressure assessment
        memory_items = (len(snapshot.ideas) + len(snapshot.associations) +
                       len(snapshot.transformations))
        max_memory_items = 100
        snapshot.memory_pressure_score = min(memory_items / max_memory_items, 1.0)

        # Update internal state
        self._recent_ideas.extend(snapshot.ideas[-10:])  # Keep recent ideas
        if len(self._recent_ideas) > 50:
            self._recent_ideas = self._recent_ideas[-25:]  # Trim to 25

        self._cycle_count += 1

    def _update_metrics(self, snapshot: CreativitySnapshot, processing_time: float, process_type: str):
        """Update Prometheus metrics for observability."""

        creativity_cycles_total.labels(
            component=self._component_id,
            process_type=process_type
        ).inc()

        creativity_latency_seconds.labels(
            component=self._component_id,
            process_type=process_type
        ).observe(processing_time / 1000.0)

        creativity_novelty_score.labels(component=self._component_id).set(
            snapshot.novelty_score
        )

        creativity_coherence_score.labels(component=self._component_id).set(
            snapshot.coherence_score
        )

        # Update internal tracking
        self._processing_times.append(processing_time)
        self._quality_scores.append((snapshot.novelty_score + snapshot.coherence_score) / 2.0)

        # Keep recent metrics
        if len(self._processing_times) > 100:
            self._processing_times.pop(0)
        if len(self._quality_scores) > 100:
            self._quality_scores.pop(0)

    # Helper methods for creative processes

    async def _populate_concept_network(self, task: CreativeTask, context: Optional[Dict[str, Any]]):
        """Populate concept network for associative reasoning."""
        # This would integrate with knowledge bases or semantic networks
        # For now, create a simple conceptual mapping
        base_concepts = task.seed_concepts + list(task.context.keys())

        for concept in base_concepts:
            if concept not in self._concept_network:
                # Generate related concepts (simplified implementation)
                related = await self._generate_related_concepts(concept, task.inspiration_domains)
                self._concept_network[concept] = related

    async def _generate_related_concepts(self, concept: str, domains: List[str]) -> List[str]:
        """Generate related concepts for associative reasoning."""
        # Simplified implementation - in production would use semantic networks
        related = []

        # Domain-based associations
        for domain in domains:
            related.extend([f"{concept}_{domain}", f"{domain}_{concept}"])

        # Conceptual variations
        related.extend([
            f"enhanced_{concept}",
            f"minimal_{concept}",
            f"alternative_{concept}",
            f"future_{concept}"
        ])

        return related[:10]  # Limit to 10 for performance

    async def _generate_perspective_ideas(
        self,
        prompt: str,
        perspective: str,
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate ideas from a specific perspective."""
        # Simplified creative idea generation
        ideas = []

        base_idea = {
            "description": f"{perspective} approach to: {prompt}",
            "perspective": perspective,
            "context_elements": list(context.keys())[:3]
        }

        # Generate variations
        for i in range(3):
            variation = base_idea.copy()
            variation["variation"] = i + 1
            variation["description"] += f" (variant {i + 1})"
            ideas.append(variation)

        return ideas

    def _calculate_novelty(self, idea_content: Dict[str, Any], existing_ideas: List[Dict[str, Any]]) -> float:
        """Calculate novelty score for an idea."""
        if not existing_ideas:
            return 0.8  # High novelty for first ideas

        # Simplified novelty calculation based on content similarity
        content_str = str(idea_content)

        similarity_scores = []
        for existing in existing_ideas:
            existing_str = str(existing.get("content", ""))

            # Simple text-based similarity (in production would use semantic similarity)
            common_words = len(set(content_str.split()) & set(existing_str.split()))
            total_words = len(set(content_str.split()) | set(existing_str.split()))

            similarity = common_words / max(total_words, 1)
            similarity_scores.append(similarity)

        # Novelty is inverse of maximum similarity
        max_similarity = max(similarity_scores) if similarity_scores else 0
        novelty = 1.0 - max_similarity

        return max(0.1, min(novelty, 1.0))

    def _calculate_coherence(self, idea_content: Dict[str, Any], task: CreativeTask) -> float:
        """Calculate coherence score for an idea."""
        coherence = 0.5  # Base coherence

        content_str = str(idea_content).lower()
        prompt_words = set(task.prompt.lower().split())
        content_words = set(content_str.split())

        # Coherence based on prompt alignment
        common_words = len(prompt_words & content_words)
        prompt_coverage = common_words / max(len(prompt_words), 1)

        coherence += prompt_coverage * 0.3

        # Constraint adherence bonus
        constraint_violations = 0
        for constraint in task.constraints:
            if constraint.lower() in content_str:
                constraint_violations += 1

        if task.constraints:
            constraint_adherence = 1.0 - (constraint_violations / len(task.constraints))
            coherence += constraint_adherence * 0.2

        return max(0.1, min(coherence, 1.0))

    def _find_related_concepts(self, concept: str) -> List[str]:
        """Find related concepts in the concept network."""
        return self._concept_network.get(concept, [])

    def _calculate_association_strength(self, concept1: str, concept2: str) -> float:
        """Calculate strength of association between concepts."""
        # Simplified association strength calculation
        c1_words = set(concept1.lower().split())
        c2_words = set(concept2.lower().split())

        common = len(c1_words & c2_words)
        total = len(c1_words | c2_words)

        return common / max(total, 1) + random.uniform(0.1, 0.3)  # Add some randomness

    async def _generate_association_idea(
        self,
        source: str,
        target: str,
        prompt: str,
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Generate idea from concept association."""
        return {
            "description": f"Combining {source} and {target} for: {prompt}",
            "source_concept": source,
            "target_concept": target,
            "association_type": "semantic",
            "context_elements": list(context.keys())[:2]
        }

    async def _refine_idea(
        self,
        idea: Dict[str, Any],
        task: CreativeTask,
        snapshot: CreativitySnapshot
    ) -> Optional[Dict[str, Any]]:
        """Refine an existing idea."""
        original_content = idea["content"]

        refined = original_content.copy() if isinstance(original_content, dict) else {"original": original_content}

        # Add refinement elements
        refined["refinement"] = "enhanced_detail"
        refined["quality_improvements"] = ["clarity", "feasibility", "innovation"]
        refined["constraints_addressed"] = task.constraints[:2]

        return refined

    async def _apply_transformation(
        self,
        content: Dict[str, Any],
        method: str,
        task: CreativeTask,
        snapshot: CreativitySnapshot
    ) -> Optional[Dict[str, Any]]:
        """Apply transformation method to content."""
        transformed = content.copy() if isinstance(content, dict) else {"original": content}

        transformed["transformation_method"] = method
        transformed["transformation_applied"] = True

        if method == "analogy":
            transformed["analogy_domain"] = random.choice(task.inspiration_domains or ["nature", "technology"])
        elif method == "inversion":
            transformed["inversion_aspect"] = "opposite_approach"
        elif method == "amplification":
            transformed["amplification_factor"] = random.uniform(1.5, 3.0)

        return transformed

    def _calculate_transformation_confidence(
        self,
        original: Dict[str, Any],
        transformed: Dict[str, Any],
        method: str
    ) -> float:
        """Calculate confidence in transformation quality."""
        # Simplified confidence calculation
        base_confidence = 0.6

        if method in ["analogy", "metaphor"]:
            base_confidence += 0.2
        elif method in ["inversion", "amplification"]:
            base_confidence += 0.1

        return min(base_confidence + random.uniform(-0.1, 0.1), 1.0)

    async def _group_similar_ideas(self, ideas: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Group similar ideas for synthesis."""
        # Simplified grouping by idea type
        groups = {}

        for idea in ideas:
            idea_type = idea.get("type", "unknown")
            base_type = idea_type.split("_")[0]  # Get base type (e.g., "divergent" from "divergent_functional")

            if base_type not in groups:
                groups[base_type] = []
            groups[base_type].append(idea)

        # Return groups with 2+ ideas
        return [group for group in groups.values() if len(group) >= 2]

    async def _synthesize_idea_group(
        self,
        group: List[Dict[str, Any]],
        task: CreativeTask
    ) -> Optional[Dict[str, Any]]:
        """Synthesize a group of ideas into a unified concept."""
        if len(group) < 2:
            return None

        synthesis = {
            "description": f"Synthesis of {len(group)} ideas for: {task.prompt}",
            "source_ideas": [idea.get("id", f"idea_{i}") for i, idea in enumerate(group)],
            "synthesis_elements": [],
            "unified_approach": True
        }

        # Extract key elements from each idea
        for idea in group:
            content = idea.get("content", {})
            if isinstance(content, dict):
                synthesis["synthesis_elements"].extend(list(content.keys())[:2])

        return synthesis

    async def _perform_quality_validation(self, snapshot: CreativitySnapshot, task: CreativeTask):
        """Perform comprehensive quality validation."""

        # Novelty validation
        avg_novelty = snapshot.novelty_score
        if avg_novelty < self.min_novelty_threshold:
            snapshot.add_validation_check(
                "novelty_threshold",
                False,
                f"Average novelty {avg_novelty:.3f} below threshold {self.min_novelty_threshold}"
            )
            snapshot.flag_anomaly("low_novelty", f"Ideas lack sufficient originality: {avg_novelty:.3f}")
        else:
            snapshot.add_validation_check("novelty_threshold", True, "Novelty requirements met")

        # Coherence validation
        avg_coherence = snapshot.coherence_score
        if avg_coherence < self.min_coherence_threshold:
            snapshot.add_validation_check(
                "coherence_threshold",
                False,
                f"Average coherence {avg_coherence:.3f} below threshold {self.min_coherence_threshold}"
            )
        else:
            snapshot.add_validation_check("coherence_threshold", True, "Coherence requirements met")

        # Fluency validation
        if snapshot.fluency_count < task.min_ideas:
            snapshot.add_validation_check(
                "fluency_minimum",
                False,
                f"Generated {snapshot.fluency_count} ideas, required {task.min_ideas}"
            )
        else:
            snapshot.add_validation_check("fluency_minimum", True, "Fluency requirements met")

    def _calculate_final_metrics(self, snapshot: CreativitySnapshot):
        """Calculate final aggregate metrics."""

        if not snapshot.ideas:
            return

        # Elaboration depth - complexity of generated ideas
        total_complexity = sum(
            len(str(idea.get("content", ""))) / 100.0  # Normalize by length
            for idea in snapshot.ideas
        )
        snapshot.elaboration_depth = min(total_complexity / len(snapshot.ideas), 1.0)

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics."""

        if not self._processing_times:
            return {
                "cycles_completed": self._cycle_count,
                "average_latency_ms": 0.0,
                "p95_latency_ms": 0.0,
                "average_quality_score": 0.0,
                "guardian_approval_rate": 0.0
            }

        sorted_times = sorted(self._processing_times)
        p95_idx = int(len(sorted_times) * 0.95)

        guardian_approval_rate = 0.0
        if self._guardian_decisions:
            guardian_approval_rate = sum(self._guardian_decisions) / len(self._guardian_decisions)

        return {
            "cycles_completed": self._cycle_count,
            "average_latency_ms": sum(self._processing_times) / len(self._processing_times),
            "p95_latency_ms": sorted_times[p95_idx] if p95_idx < len(sorted_times) else sorted_times[-1],
            "average_quality_score": sum(self._quality_scores) / len(self._quality_scores) if self._quality_scores else 0.0,
            "guardian_approval_rate": guardian_approval_rate,
            "current_flow_state": self._flow_state,
            "creative_energy": self._creative_energy,
            "concept_network_size": len(self._concept_network)
        }

    async def reset_state(self):
        """Reset creativity engine state for testing."""
        self._flow_state = "blocked"
        self._creative_energy = 0.0
        self._concept_network.clear()
        self._recent_ideas.clear()
        self._processing_times.clear()
        self._quality_scores.clear()
        self._guardian_decisions.clear()
        self._cycle_count = 0


# Export for public API
__all__ = ["CreativityEngine"]
