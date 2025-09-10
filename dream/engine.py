"""
Dream Engine Module
Core dream processing and generation engine for LUKHAS AI
Trinity Framework: ⚛️🧠🛡️
"""

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class DreamType(Enum):
    """Types of dreams that can be generated"""

    LUCID = "lucid"
    SYMBOLIC = "symbolic"
    NARRATIVE = "narrative"
    MEMORY_REPLAY = "memory_replay"
    CREATIVE = "creative"
    PREDICTIVE = "predictive"
    HEALING = "healing"
    CONSCIOUSNESS_EXPLORATION = "consciousness_exploration"


class DreamState(Enum):
    """Current state of dream processing"""

    INITIALIZING = "initializing"
    ACTIVE = "active"
    TRANSITIONING = "transitioning"
    COMPLETING = "completing"
    ENDED = "ended"
    ERROR = "error"


@dataclass
class DreamElement:
    """Individual element within a dream"""

    element_id: str
    element_type: str  # character, object, scene, emotion, symbol
    properties: dict[str, Any]
    interactions: list[str] = field(default_factory=list)
    symbolic_meaning: Optional[str] = None
    emotional_weight: float = 0.0


@dataclass
class DreamSequence:
    """Complete dream sequence"""

    sequence_id: str
    dream_type: DreamType
    elements: list[DreamElement]
    narrative_arc: list[str]
    emotional_journey: list[tuple[str, float]]  # (emotion, intensity)
    consciousness_integration: dict[str, Any]
    created_at: datetime
    duration_estimate: float  # in minutes
    lucidity_level: float = 0.0  # 0.0 = non-lucid, 1.0 = fully lucid


@dataclass
class DreamContext:
    """Context for dream generation"""

    dreamer_state: dict[str, Any]
    recent_memories: list[dict[str, Any]]
    emotional_state: dict[str, float]
    consciousness_level: float
    external_influences: list[str]
    dream_goals: list[str]
    constraints: dict[str, Any]


class DreamEngine:
    """
    Core dream processing engine for LUKHAS AI.

    Generates, processes, and manages dream sequences with consciousness integration.
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """Initialize dream engine"""
        self.config = config or {}
        self.active_dreams: dict[str, DreamSequence] = {}
        self.dream_templates: dict[DreamType, dict[str, Any]] = {}
        self.element_generators: dict[str, Any] = {}
        self.state = DreamState.INITIALIZING

        # Configuration
        self.max_active_dreams = self.config.get("max_active_dreams", 3)
        self.default_duration = self.config.get("default_duration", 20.0)  # minutes
        self.lucidity_threshold = self.config.get("lucidity_threshold", 0.7)

        # Initialize components
        self._initialize_templates()
        self._initialize_generators()

        self.state = DreamState.ACTIVE
        logger.info("Dream Engine initialized successfully")

    def _initialize_templates(self):
        """Initialize dream type templates"""
        self.dream_templates = {
            DreamType.LUCID: {
                "focus": "conscious_control",
                "narrative_style": "interactive",
                "symbol_density": 0.3,
                "emotional_intensity": 0.7,
                "memory_integration": 0.8,
            },
            DreamType.SYMBOLIC: {
                "focus": "symbolic_meaning",
                "narrative_style": "abstract",
                "symbol_density": 0.9,
                "emotional_intensity": 0.6,
                "memory_integration": 0.5,
            },
            DreamType.NARRATIVE: {
                "focus": "story_coherence",
                "narrative_style": "linear",
                "symbol_density": 0.4,
                "emotional_intensity": 0.8,
                "memory_integration": 0.7,
            },
            DreamType.MEMORY_REPLAY: {
                "focus": "memory_processing",
                "narrative_style": "episodic",
                "symbol_density": 0.2,
                "emotional_intensity": 0.9,
                "memory_integration": 1.0,
            },
            DreamType.CREATIVE: {
                "focus": "novel_combinations",
                "narrative_style": "surreal",
                "symbol_density": 0.7,
                "emotional_intensity": 0.5,
                "memory_integration": 0.3,
            },
            DreamType.PREDICTIVE: {
                "focus": "future_scenarios",
                "narrative_style": "speculative",
                "symbol_density": 0.5,
                "emotional_intensity": 0.6,
                "memory_integration": 0.6,
            },
            DreamType.HEALING: {
                "focus": "emotional_processing",
                "narrative_style": "therapeutic",
                "symbol_density": 0.6,
                "emotional_intensity": 0.7,
                "memory_integration": 0.8,
            },
            DreamType.CONSCIOUSNESS_EXPLORATION: {
                "focus": "self_discovery",
                "narrative_style": "introspective",
                "symbol_density": 0.8,
                "emotional_intensity": 0.6,
                "memory_integration": 0.9,
            },
        }

    def _initialize_generators(self):
        """Initialize element generators"""
        self.element_generators = {
            "character": self._generate_character,
            "object": self._generate_object,
            "scene": self._generate_scene,
            "emotion": self._generate_emotion,
            "symbol": self._generate_symbol,
            "action": self._generate_action,
            "dialogue": self._generate_dialogue,
        }

    async def generate_dream(
        self, dream_type: DreamType, context: DreamContext, duration: Optional[float] = None
    ) -> DreamSequence:
        """
        Generate a complete dream sequence.

        Args:
            dream_type: Type of dream to generate
            context: Context for dream generation
            duration: Duration in minutes (optional)

        Returns:
            Generated dream sequence
        """
        if len(self.active_dreams) >= self.max_active_dreams:
            raise RuntimeError("Maximum active dreams reached")

        sequence_id = f"dream_{uuid.uuid4().hex[:8]}"
        duration = duration or self.default_duration

        logger.info(f"Generating {dream_type.value} dream: {sequence_id}")

        # Get template for dream type
        template = self.dream_templates[dream_type]

        # Generate dream elements
        elements = await self._generate_elements(dream_type, context, template)

        # Create narrative arc
        narrative_arc = await self._generate_narrative_arc(elements, template)

        # Generate emotional journey
        emotional_journey = await self._generate_emotional_journey(elements, context.emotional_state, template)

        # Calculate consciousness integration
        consciousness_integration = await self._calculate_consciousness_integration(elements, context, template)

        # Determine lucidity level
        lucidity_level = await self._calculate_lucidity_level(context, template)

        # Create dream sequence
        dream_sequence = DreamSequence(
            sequence_id=sequence_id,
            dream_type=dream_type,
            elements=elements,
            narrative_arc=narrative_arc,
            emotional_journey=emotional_journey,
            consciousness_integration=consciousness_integration,
            created_at=datetime.now(timezone.utc),
            duration_estimate=duration,
            lucidity_level=lucidity_level,
        )

        # Store active dream
        self.active_dreams[sequence_id] = dream_sequence

        logger.info(f"Dream generated: {sequence_id} ({len(elements)} elements, {lucidity_level:.2f} lucidity)")

        return dream_sequence

    async def _generate_elements(
        self, dream_type: DreamType, context: DreamContext, template: dict[str, Any]
    ) -> list[DreamElement]:
        """Generate dream elements based on type and context"""
        elements = []
        element_count = int(template.get("symbol_density", 0.5) * 20) + 5  # 5-25 elements

        # Generate base elements
        for _i in range(element_count):
            element_type = self._select_element_type(template, context)
            generator = self.element_generators.get(element_type, self._generate_generic)

            element = await generator(dream_type, context, template)
            elements.append(element)

        # Add memory-based elements if relevant
        if template.get("memory_integration", 0.0) > 0.5:
            memory_elements = await self._generate_memory_elements(context, template)
            elements.extend(memory_elements)

        return elements

    def _select_element_type(self, template: dict[str, Any], context: DreamContext) -> str:
        """Select appropriate element type based on template and context"""
        # Simple weighted selection based on dream focus
        focus = template.get("focus", "balanced")

        if focus == "symbolic_meaning":
            return "symbol" if len(context.recent_memories) % 3 == 0 else "object"
        elif focus == "memory_processing":
            return "character" if len(context.recent_memories) % 2 == 0 else "scene"
        elif focus == "emotional_processing":
            return "emotion"
        elif focus == "story_coherence":
            return "action" if len(context.recent_memories) % 4 == 0 else "dialogue"
        else:
            # Balanced selection
            types = ["character", "object", "scene", "emotion", "symbol", "action"]
            return types[len(context.recent_memories) % len(types)]

    async def _generate_character(
        self, dream_type: DreamType, context: DreamContext, template: dict[str, Any]
    ) -> DreamElement:
        """Generate dream character"""
        return DreamElement(
            element_id=f"char_{uuid.uuid4().hex[:6]}",
            element_type="character",
            properties={
                "name": f"Character_{len(context.recent_memories) % 100}",
                "role": "guide" if dream_type == DreamType.LUCID else "participant",
                "familiar": len(context.recent_memories) % 3 == 0,
                "emotional_resonance": context.emotional_state.get("joy", 0.5),
            },
            symbolic_meaning="aspect_of_self" if dream_type == DreamType.SYMBOLIC else None,
            emotional_weight=0.7,
        )

    async def _generate_object(
        self, dream_type: DreamType, context: DreamContext, template: dict[str, Any]
    ) -> DreamElement:
        """Generate dream object"""
        return DreamElement(
            element_id=f"obj_{uuid.uuid4().hex[:6]}",
            element_type="object",
            properties={
                "material": "ethereal" if template.get("symbol_density", 0) > 0.7 else "solid",
                "significance": "high" if dream_type == DreamType.SYMBOLIC else "medium",
                "interactable": dream_type == DreamType.LUCID,
                "memory_linked": len(context.recent_memories) > 0,
            },
            symbolic_meaning="transformation" if dream_type == DreamType.SYMBOLIC else None,
            emotional_weight=0.4,
        )

    async def _generate_scene(
        self, dream_type: DreamType, context: DreamContext, template: dict[str, Any]
    ) -> DreamElement:
        """Generate dream scene"""
        return DreamElement(
            element_id=f"scene_{uuid.uuid4().hex[:6]}",
            element_type="scene",
            properties={
                "setting": "familiar" if len(context.recent_memories) % 2 == 0 else "novel",
                "atmosphere": "mysterious" if dream_type == DreamType.SYMBOLIC else "comfortable",
                "stability": "fluid" if template.get("narrative_style") == "surreal" else "stable",
                "consciousness_accessible": dream_type == DreamType.CONSCIOUSNESS_EXPLORATION,
            },
            symbolic_meaning="life_stage" if dream_type == DreamType.SYMBOLIC else None,
            emotional_weight=0.6,
        )

    async def _generate_emotion(
        self, dream_type: DreamType, context: DreamContext, template: dict[str, Any]
    ) -> DreamElement:
        """Generate emotional element"""
        # Select emotion based on context
        dominant_emotion = (
            max(context.emotional_state.items(), key=lambda x: x[1])[0] if context.emotional_state else "calm"
        )

        return DreamElement(
            element_id=f"emotion_{uuid.uuid4().hex[:6]}",
            element_type="emotion",
            properties={
                "primary_emotion": dominant_emotion,
                "intensity": context.emotional_state.get(dominant_emotion, 0.5),
                "processing_needed": dream_type == DreamType.HEALING,
                "consciousness_integration": dream_type == DreamType.CONSCIOUSNESS_EXPLORATION,
            },
            symbolic_meaning="emotional_growth" if dream_type == DreamType.HEALING else None,
            emotional_weight=0.9,
        )

    async def _generate_symbol(
        self, dream_type: DreamType, context: DreamContext, template: dict[str, Any]
    ) -> DreamElement:
        """Generate symbolic element"""
        symbols = ["water", "bridge", "door", "mirror", "tree", "spiral", "light", "shadow"]
        symbol = symbols[len(context.recent_memories) % len(symbols)]

        return DreamElement(
            element_id=f"symbol_{uuid.uuid4().hex[:6]}",
            element_type="symbol",
            properties={
                "symbol_type": symbol,
                "archetypal": dream_type == DreamType.SYMBOLIC,
                "personal_meaning": len(context.recent_memories) % 3 == 0,
                "transformation_potential": dream_type in [DreamType.HEALING, DreamType.CONSCIOUSNESS_EXPLORATION],
            },
            symbolic_meaning=f"represents_{symbol}_archetype",
            emotional_weight=0.8,
        )

    async def _generate_action(
        self, dream_type: DreamType, context: DreamContext, template: dict[str, Any]
    ) -> DreamElement:
        """Generate action element"""
        return DreamElement(
            element_id=f"action_{uuid.uuid4().hex[:6]}",
            element_type="action",
            properties={
                "action_type": "exploration" if dream_type == DreamType.LUCID else "reaction",
                "agency": dream_type == DreamType.LUCID,
                "consequence_aware": context.consciousness_level > 0.7,
                "memory_triggered": len(context.recent_memories) > 2,
            },
            symbolic_meaning="choice_point" if dream_type == DreamType.CONSCIOUSNESS_EXPLORATION else None,
            emotional_weight=0.5,
        )

    async def _generate_dialogue(
        self, dream_type: DreamType, context: DreamContext, template: dict[str, Any]
    ) -> DreamElement:
        """Generate dialogue element"""
        return DreamElement(
            element_id=f"dialogue_{uuid.uuid4().hex[:6]}",
            element_type="dialogue",
            properties={
                "speaker": "self" if dream_type == DreamType.CONSCIOUSNESS_EXPLORATION else "other",
                "content_type": "wisdom" if dream_type == DreamType.SYMBOLIC else "conversation",
                "understanding_level": context.consciousness_level,
                "emotional_context": max(context.emotional_state.items(), key=lambda x: x[1])[0]
                if context.emotional_state
                else "neutral",
            },
            symbolic_meaning="inner_voice" if dream_type == DreamType.CONSCIOUSNESS_EXPLORATION else None,
            emotional_weight=0.6,
        )

    async def _generate_generic(
        self, dream_type: DreamType, context: DreamContext, template: dict[str, Any]
    ) -> DreamElement:
        """Generate generic element when specific generator not available"""
        return DreamElement(
            element_id=f"generic_{uuid.uuid4().hex[:6]}",
            element_type="generic",
            properties={"placeholder": True, "template_based": True},
            emotional_weight=0.3,
        )

    async def _generate_memory_elements(self, context: DreamContext, template: dict[str, Any]) -> list[DreamElement]:
        """Generate elements based on recent memories"""
        memory_elements = []

        for i, memory in enumerate(context.recent_memories[:3]):  # Limit to 3 memories
            element = DreamElement(
                element_id=f"memory_{i}_{uuid.uuid4().hex[:6]}",
                element_type="memory_fragment",
                properties={
                    "memory_source": memory.get("id", f"mem_{i}"),
                    "memory_type": memory.get("type", "episodic"),
                    "integration_level": template.get("memory_integration", 0.5),
                    "distortion_level": 1.0 - template.get("memory_integration", 0.5),
                },
                symbolic_meaning="past_integration",
                emotional_weight=memory.get("emotional_intensity", 0.5),
            )
            memory_elements.append(element)

        return memory_elements

    async def _generate_narrative_arc(self, elements: list[DreamElement], template: dict[str, Any]) -> list[str]:
        """Generate narrative arc connecting dream elements"""
        narrative_style = template.get("narrative_style", "linear")

        if narrative_style == "linear":
            return [f"sequence_{i}" for i in range(len(elements))]
        elif narrative_style == "abstract":
            return [f"abstraction_{i%3}" for i in range(len(elements))]
        elif narrative_style == "surreal":
            return [f"surreal_transition_{i%5}" for i in range(len(elements))]
        elif narrative_style == "interactive":
            return [f"choice_point_{i}" if i % 3 == 0 else f"sequence_{i}" for i in range(len(elements))]
        else:
            return [f"arc_{i}" for i in range(len(elements))]

    async def _generate_emotional_journey(
        self, elements: list[DreamElement], base_emotional_state: dict[str, float], template: dict[str, Any]
    ) -> list[tuple[str, float]]:
        """Generate emotional journey through dream"""
        journey = []

        # Start with base emotional state
        if base_emotional_state:
            primary_emotion = max(base_emotional_state.items(), key=lambda x: x[1])
            journey.append(primary_emotion)
        else:
            journey.append(("calm", 0.5))

        # Add emotional transitions based on elements
        for i, element in enumerate(elements):
            if element.element_type == "emotion":
                emotion = element.properties.get("primary_emotion", "neutral")
                intensity = element.properties.get("intensity", 0.5)
                journey.append((emotion, intensity))
            elif element.emotional_weight > 0.7:
                # High emotional weight elements create emotional shifts
                if i % 2 == 0:
                    journey.append(("curiosity", 0.6))
                else:
                    journey.append(("wonder", 0.7))

        return journey

    async def _calculate_consciousness_integration(
        self, elements: list[DreamElement], context: DreamContext, template: dict[str, Any]
    ) -> dict[str, Any]:
        """Calculate consciousness integration metrics"""
        integration = {
            "awareness_level": context.consciousness_level,
            "memory_integration": template.get("memory_integration", 0.5),
            "symbolic_density": template.get("symbol_density", 0.5),
            "emotional_processing": template.get("emotional_intensity", 0.5),
            "self_reflection_opportunities": sum(1 for e in elements if e.element_type in ["symbol", "emotion"]),
            "total_elements": len(elements),
        }

        # Calculate overall integration score
        integration["integration_score"] = (
            integration["awareness_level"] * 0.3
            + integration["memory_integration"] * 0.3
            + integration["symbolic_density"] * 0.2
            + integration["emotional_processing"] * 0.2
        )

        return integration

    async def _calculate_lucidity_level(self, context: DreamContext, template: dict[str, Any]) -> float:
        """Calculate lucidity level for dream"""
        base_lucidity = context.consciousness_level

        # Adjust based on dream type template
        if template.get("focus") == "conscious_control":
            base_lucidity += 0.3
        elif template.get("focus") == "self_discovery" or template.get("narrative_style") == "interactive":
            base_lucidity += 0.2

        # Clamp to valid range
        return max(0.0, min(1.0, base_lucidity))

    async def process_dream(self, sequence_id: str) -> dict[str, Any]:
        """Process an active dream sequence"""
        if sequence_id not in self.active_dreams:
            raise ValueError(f"Dream sequence {sequence_id} not found")

        dream = self.active_dreams[sequence_id]

        # Simulate dream processing
        processing_result = {
            "sequence_id": sequence_id,
            "processing_time": datetime.now(timezone.utc),
            "insights": self._extract_insights(dream),
            "memory_consolidation": self._consolidate_memories(dream),
            "emotional_resolution": self._process_emotions(dream),
            "consciousness_updates": self._update_consciousness(dream),
        }

        logger.info(f"Processed dream: {sequence_id}")
        return processing_result

    def _extract_insights(self, dream: DreamSequence) -> list[str]:
        """Extract insights from dream sequence"""
        insights = []

        # Analyze symbolic elements
        symbols = [e for e in dream.elements if e.element_type == "symbol"]
        if symbols:
            insights.append(f"Symbolic theme: {symbols[0].properties.get('symbol_type', 'transformation')}")

        # Analyze emotional journey
        if dream.emotional_journey:
            primary_emotions = [e[0] for e in dream.emotional_journey]
            if len(set(primary_emotions)) > 3:
                insights.append("Complex emotional processing detected")
            else:
                insights.append(f"Focused on {primary_emotions[0]} emotions")

        # Consciousness integration insights
        integration_score = dream.consciousness_integration.get("integration_score", 0.5)
        if integration_score > 0.8:
            insights.append("High consciousness integration achieved")
        elif integration_score < 0.3:
            insights.append("Low consciousness integration - processing needed")

        return insights

    def _consolidate_memories(self, dream: DreamSequence) -> dict[str, Any]:
        """Consolidate memories from dream"""
        return {
            "memories_processed": len([e for e in dream.elements if e.element_type == "memory_fragment"]),
            "integration_quality": dream.consciousness_integration.get("memory_integration", 0.5),
            "new_associations": len(dream.elements) // 3,  # Rough estimate
        }

    def _process_emotions(self, dream: DreamSequence) -> dict[str, Any]:
        """Process emotions from dream"""
        emotional_elements = [e for e in dream.elements if e.element_type == "emotion"]
        return {
            "emotions_processed": len(emotional_elements),
            "emotional_intensity": sum(e.emotional_weight for e in emotional_elements) / len(emotional_elements)
            if emotional_elements
            else 0.0,
            "resolution_achieved": dream.dream_type == DreamType.HEALING,
        }

    def _update_consciousness(self, dream: DreamSequence) -> dict[str, Any]:
        """Update consciousness based on dream"""
        return {
            "lucidity_development": dream.lucidity_level,
            "self_awareness_growth": dream.consciousness_integration.get("self_reflection_opportunities", 0) / 10,
            "integration_advancement": dream.consciousness_integration.get("integration_score", 0.5),
        }

    async def end_dream(self, sequence_id: str) -> dict[str, Any]:
        """End an active dream sequence"""
        if sequence_id not in self.active_dreams:
            raise ValueError(f"Dream sequence {sequence_id} not found")

        dream = self.active_dreams[sequence_id]

        # Final processing
        final_result = await self.process_dream(sequence_id)

        # Archive the dream
        archived_dream = {"sequence": dream, "final_processing": final_result, "ended_at": datetime.now(timezone.utc)}

        # Remove from active dreams
        del self.active_dreams[sequence_id]

        logger.info(f"Dream ended: {sequence_id}")
        return archived_dream

    def get_active_dreams(self) -> list[str]:
        """Get list of active dream sequence IDs"""
        return list(self.active_dreams.keys())

    def get_dream_info(self, sequence_id: str) -> Optional[dict[str, Any]]:
        """Get information about a dream sequence"""
        if sequence_id not in self.active_dreams:
            return None

        dream = self.active_dreams[sequence_id]
        return {
            "sequence_id": sequence_id,
            "dream_type": dream.dream_type.value,
            "element_count": len(dream.elements),
            "lucidity_level": dream.lucidity_level,
            "duration_estimate": dream.duration_estimate,
            "created_at": dream.created_at.isoformat(),
            "consciousness_integration": dream.consciousness_integration,
        }


# Global dream engine instance
_dream_engine = None


def get_dream_engine(config: Optional[dict[str, Any]] = None) -> DreamEngine:
    """Get or create global dream engine instance"""
    global _dream_engine
    if _dream_engine is None:
        _dream_engine = DreamEngine(config)
    return _dream_engine


# Convenience functions
async def generate_dream(
    dream_type: DreamType,
    dreamer_state: dict[str, Any],
    emotional_state: Optional[dict[str, float]] = None,
    duration: Optional[float] = None,
) -> DreamSequence:
    """Generate a dream with simplified parameters"""
    context = DreamContext(
        dreamer_state=dreamer_state,
        recent_memories=[],
        emotional_state=emotional_state or {},
        consciousness_level=dreamer_state.get("consciousness_level", 0.7),
        external_influences=[],
        dream_goals=[],
        constraints={},
    )

    engine = get_dream_engine()
    return await engine.generate_dream(dream_type, context, duration)


async def process_dream_sequence(sequence_id: str) -> dict[str, Any]:
    """Process a dream sequence"""
    engine = get_dream_engine()
    return await engine.process_dream(sequence_id)


# Export public interface
__all__ = [
    "DreamType",
    "DreamState",
    "DreamElement",
    "DreamSequence",
    "DreamContext",
    "DreamEngine",
    "get_dream_engine",
    "generate_dream",
    "process_dream_sequence",
]
