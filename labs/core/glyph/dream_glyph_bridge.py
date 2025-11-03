from __future__ import annotations

from collections import defaultdict
from datetime import timezone

#!/usr/bin/env python3

"""

#TAG:core
#TAG:glyph
#TAG:neuroplastic
#TAG:colony

LUKHAS (Logical Unified Knowledge Hyper-Adaptable System) - Dream-Glyph Bridge

Copyright (c) 2025 LUKHAS Cognitive AI Development Team
All rights reserved.

This file is part of the LUKHAS Cognitive system, an enterprise artificial general
intelligence platform combining symbolic reasoning, emotional intelligence,
quantum integration, and bio-inspired architecture.

Mission: To illuminate complex reality through rigorous logic, adaptive
intelligence, and human-centred ethics—turning data into understanding,
understanding into foresight, and foresight into shared benefit for people
and planet.

Dream-Glyph Bridge: Integration system between Dream Systems and GLYPH
subsystem, enabling glyph-to-dream seed conversion, dream-to-glyph generation,
archetypal mapping, and symbolic memory integration for enhanced dream
processing and glyph evolution.

For more information, visit: https://ai
"""

# ΛTRACE: Dream-Glyph Bridge initialization
# ΛORIGIN_AGENT: Claude Code
# ΛTASK_ID: Task 14

__version__ = "1.0.0"
__author__ = "LUKHAS Development Team"
__email__ = "dev@ai"
__status__ = "Production"

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional

# Internal imports
from symbolic.glyphs.glyph import EmotionVector, Glyph, GlyphFactory, GlyphPriority, GlyphType

# Configure logger
logger = logging.getLogger(__name__)


class DreamPhase(Enum):
    """Dream processing phases for glyph integration."""

    INITIATION = "initiation"  # Dream startup with glyph seeds
    PATTERN = "pattern"  # Pattern recognition from glyphs
    DEEP_SYMBOLIC = "deep_symbolic"  # Deep symbolic processing
    CREATIVE = "creative"  # Creative synthesis phase
    INTEGRATION = "integration"  # Integration back to memory


class ArchetypalGlyphMapping(Enum):
    """Mapping between Jungian archetypes and glyph types."""

    SELF = GlyphType.ETHICAL  # Self archetype -> Ethical glyphs
    SHADOW = GlyphType.COLLAPSE  # Shadow archetype -> Collapse glyphs
    ANIMA_ANIMUS = GlyphType.EMOTION  # Anima/Animus -> Emotion glyphs
    HERO = GlyphType.ACTION  # Hero archetype -> Action glyphs
    SAGE = GlyphType.MEMORY  # Sage archetype -> Memory glyphs
    MOTHER = GlyphType.CAUSAL  # Mother archetype -> Causal glyphs
    TRICKSTER = GlyphType.DREAM  # Trickster -> Dream glyphs


@dataclass
class DreamSeed:
    """Glyph-derived seed for dream generation."""

    seed_id: str
    source_glyph_id: str
    dream_phase: DreamPhase
    symbolic_content: dict[str, Any]
    emotional_context: EmotionVector
    archetypal_resonance: list[str]
    narrative_fragments: list[str]
    symbolic_intensity: float
    creation_timestamp: datetime

    def to_dict(self) -> dict[str, Any]:
        """Convert dream seed to dictionary."""
        return {
            "seed_id": self.seed_id,
            "source_glyph_id": self.source_glyph_id,
            "dream_phase": self.dream_phase.value,
            "symbolic_content": self.symbolic_content,
            "emotional_context": self.emotional_context.to_dict(),
            "archetypal_resonance": self.archetypal_resonance,
            "narrative_fragments": self.narrative_fragments,
            "symbolic_intensity": self.symbolic_intensity,
            "creation_timestamp": self.creation_timestamp.isoformat(),
        }


@dataclass
class DreamGlyph:
    """Glyph extracted from dream processing."""

    dream_id: str
    extracted_glyph: Glyph
    dream_phase: DreamPhase
    archetypal_source: str
    consolidation_score: float
    narrative_context: str
    extraction_method: str

    def to_dict(self) -> dict[str, Any]:
        """Convert dream glyph to dictionary."""
        return {
            "dream_id": self.dream_id,
            "extracted_glyph": self.extracted_glyph.to_dict(),
            "dream_phase": self.dream_phase.value,
            "archetypal_source": self.archetypal_source,
            "consolidation_score": self.consolidation_score,
            "narrative_context": self.narrative_context,
            "extraction_method": self.extraction_method,
        }


class DreamGlyphBridge:
    """
    Bridge between Dream Systems and GLYPH subsystem.

    Provides bidirectional integration:
    - Converts glyphs into dream seeds for symbolic processing
    - Extracts glyphs from dream content for memory consolidation
    - Manages archetypal mapping and emotional context preservation
    """

    def __init__(self):
        """Initialize the Dream-Glyph Bridge."""
        self.dream_seeds: dict[str, DreamSeed] = {}
        self.dream_glyphs: dict[str, DreamGlyph] = {}
        self.archetypal_mappings = self._initialize_archetypal_mappings()
        self.narrative_templates = self._initialize_narrative_templates()

        logger.info("Dream-Glyph Bridge initialized")

    def glyph_to_dream_seed(
        self,
        glyph: Glyph,
        dream_phase: DreamPhase = DreamPhase.INITIATION,
        intensity_multiplier: float = 1.0,
    ) -> DreamSeed:
        """
        Convert a glyph into a dream seed for dream processing.

        Args:
            glyph: Source glyph to convert
            dream_phase: Target dream phase for processing
            intensity_multiplier: Multiplier for symbolic intensity

        Returns:
            DreamSeed instance ready for dream processing
        """
        # Generate symbolic content based on glyph
        symbolic_content = self._extract_symbolic_content(glyph, dream_phase)

        # Map to archetypal resonance
        archetypal_resonance = self._map_to_archetypes(glyph)

        # Generate narrative fragments
        narrative_fragments = self._generate_narrative_fragments(glyph, dream_phase)

        # Calculate symbolic intensity
        base_intensity = self._calculate_symbolic_intensity(glyph)
        symbolic_intensity = min(1.0, base_intensity * intensity_multiplier)

        # Create dream seed
        seed_id = f"dream_seed_{glyph.id[:8]}_{datetime.now(timezone.utc).strftime('%H%M%S')}"

        dream_seed = DreamSeed(
            seed_id=seed_id,
            source_glyph_id=glyph.id,
            dream_phase=dream_phase,
            symbolic_content=symbolic_content,
            emotional_context=glyph.emotion_vector,
            archetypal_resonance=archetypal_resonance,
            narrative_fragments=narrative_fragments,
            symbolic_intensity=symbolic_intensity,
            creation_timestamp=datetime.now(timezone.utc),
        )

        self.dream_seeds[seed_id] = dream_seed
        logger.debug(f"Created dream seed {seed_id} from glyph {glyph.id}")

        return dream_seed

    def dream_to_glyph(
        self,
        dream_id: str,
        dream_content: dict[str, Any],
        dream_phase: DreamPhase,
        consolidation_method: str = "archetypal_extraction",
    ) -> Optional[DreamGlyph]:
        """
        Extract a glyph from dream content for memory consolidation.

        Args:
            dream_id: Unique dream identifier
            dream_content: Dream content dictionary
            dream_phase: Phase where extraction occurred
            consolidation_method: Method used for glyph extraction

        Returns:
            DreamGlyph instance if extraction successful
        """
        try:
            # Extract archetypal source
            archetypal_source = self._identify_archetypal_source(dream_content)

            # Create consolidated glyph
            extracted_glyph = self._create_dream_glyph(dream_content, archetypal_source, dream_phase)

            # Calculate consolidation score
            consolidation_score = self._calculate_consolidation_score(dream_content, extracted_glyph)

            # Extract narrative context
            narrative_context = self._extract_narrative_context(dream_content)

            # Create dream glyph
            dream_glyph = DreamGlyph(
                dream_id=dream_id,
                extracted_glyph=extracted_glyph,
                dream_phase=dream_phase,
                archetypal_source=archetypal_source,
                consolidation_score=consolidation_score,
                narrative_context=narrative_context,
                extraction_method=consolidation_method,
            )

            self.dream_glyphs[dream_id] = dream_glyph
            logger.debug(f"Extracted glyph {extracted_glyph.id} from dream {dream_id}")

            return dream_glyph

        except Exception as e:
            logger.error(f"Failed to extract glyph from dream {dream_id}: {e}")
            return None

    def create_memory_consolidation_glyph(self, memory_traces: list[dict[str, Any]], dream_narrative: str) -> Glyph:
        """
        Create a glyph for memory consolidation from dream processing.

        Args:
            memory_traces: List of memory trace data
            dream_narrative: Narrative generated during dream processing

        Returns:
            Consolidated memory glyph
        """
        # Analyze memory traces for patterns
        dominant_emotions = self._analyze_emotional_patterns(memory_traces)
        symbolic_themes = self._extract_symbolic_themes(memory_traces, dream_narrative)

        # Create consolidated emotion vector
        consolidated_emotion = self._consolidate_emotions(dominant_emotions)

        # Create memory consolidation glyph
        memory_glyph = GlyphFactory.create_memory_glyph(
            memory_key=f"consolidated_{len(memory_traces)}_traces",
            emotion_vector=consolidated_emotion,
        )

        # Add dream-specific semantic tags
        memory_glyph.add_semantic_tag("dream_consolidated")
        memory_glyph.add_semantic_tag("memory_integration")
        for theme in symbolic_themes:
            memory_glyph.add_semantic_tag(f"theme_{theme}")

        # Set priority based on consolidation importance
        if len(memory_traces) > 5:
            memory_glyph.priority = GlyphPriority.HIGH

        # Add dream narrative to content
        memory_glyph.content["dream_narrative"] = dream_narrative
        memory_glyph.content["consolidated_traces"] = len(memory_traces)
        memory_glyph.content["consolidation_timestamp"] = datetime.now(timezone.utc).isoformat()

        memory_glyph.update_symbolic_hash()

        logger.info(f"Created memory consolidation glyph {memory_glyph.id} from {len(memory_traces)} traces")
        return memory_glyph

    def get_archetypal_dream_seeds(self, archetype: str) -> list[DreamSeed]:
        """
        Get dream seeds matching a specific archetypal pattern.

        Args:
            archetype: Archetype name to match

        Returns:
            List of matching dream seeds
        """
        matching_seeds = []

        for seed in self.dream_seeds.values():
            if archetype.lower() in [arch.lower() for arch in seed.archetypal_resonance]:
                matching_seeds.append(seed)

        return matching_seeds

    def get_dream_glyph_lineage(self, dream_id: str) -> Optional[dict[str, Any]]:
        """
        Get the complete lineage of a dream glyph.

        Args:
            dream_id: Dream identifier

        Returns:
            Lineage information dictionary
        """
        if dream_id not in self.dream_glyphs:
            return None

        dream_glyph = self.dream_glyphs[dream_id]
        glyph = dream_glyph.extracted_glyph

        lineage = {
            "dream_id": dream_id,
            "glyph_id": glyph.id,
            "archetypal_source": dream_glyph.archetypal_source,
            "dream_phase": dream_glyph.dream_phase.value,
            "consolidation_score": dream_glyph.consolidation_score,
            "emotional_vector": glyph.emotion_vector.to_dict(),
            "semantic_tags": list(glyph.semantic_tags),
            "causal_links": {
                "parent_glyph_id": glyph.causal_link.parent_glyph_id,
                "causal_origin_id": glyph.causal_link.causal_origin_id,
                "event_chain_hash": glyph.causal_link.event_chain_hash,
            },
            "memory_associations": list(glyph.memory_keys),
            "narrative_context": dream_glyph.narrative_context,
        }

        return lineage

    def _initialize_archetypal_mappings(self) -> dict[str, Any]:
        """Initialize archetypal mapping configurations."""
        return {
            "self": {
                "glyph_type": GlyphType.ETHICAL,
                "symbols": ["⚖️", "🎯", "💎", "🔱"],
                "themes": ["wholeness", "integration", "purpose", "identity"],
                "emotional_emphasis": ["trust", "joy", "anticipation"],
            },
            "shadow": {
                "glyph_type": GlyphType.COLLAPSE,
                "symbols": ["🌑", "🔮", "⚡", "🌊"],
                "themes": ["hidden", "repressed", "chaos", "transformation"],
                "emotional_emphasis": ["fear", "anger", "disgust"],
            },
            "anima": {
                "glyph_type": GlyphType.EMOTION,
                "symbols": ["🌙", "💫", "🌸", "💭"],
                "themes": [
                    "feeling",
                    "intuition",
                    "creativity",
                    "receptivity",
                ],
                "emotional_emphasis": ["joy", "trust", "surprise"],
            },
            "animus": {
                "glyph_type": GlyphType.ACTION,
                "symbols": ["⚔️", "🔥", "⚡", "🎯"],
                "themes": ["logic", "action", "focus", "achievement"],
                "emotional_emphasis": ["anticipation", "trust", "anger"],
            },
            "hero": {
                "glyph_type": GlyphType.ACTION,
                "symbols": ["🦅", "⚡", "🔱", "🏆"],
                "themes": ["courage", "journey", "transformation", "victory"],
                "emotional_emphasis": ["anticipation", "joy", "trust"],
            },
            "sage": {
                "glyph_type": GlyphType.MEMORY,
                "symbols": ["📚", "🔍", "💡", "🕯️"],
                "themes": ["wisdom", "knowledge", "understanding", "guidance"],
                "emotional_emphasis": ["trust", "anticipation", "joy"],
            },
            "mother": {
                "glyph_type": GlyphType.CAUSAL,
                "symbols": ["🌱", "🤱", "🏠", "💚"],
                "themes": ["nurturing", "protection", "growth", "connection"],
                "emotional_emphasis": ["trust", "joy", "anticipation"],
            },
            "trickster": {
                "glyph_type": GlyphType.DREAM,
                "symbols": ["🎭", "🌈", "🔄", "🎲"],
                "themes": ["change", "humor", "disruption", "creativity"],
                "emotional_emphasis": ["surprise", "joy", "anticipation"],
            },
        }

    def _initialize_narrative_templates(self) -> dict[str, list[str]]:
        """Initialize narrative templates for different dream phases."""
        return {
            "initiation": [
                "A {symbol} appears in the threshold between sleep and waking...",
                "You find yourself in a space where {theme} begins to unfold...",
                "The dream opens with a sense of {emotion}, drawing you deeper...",
            ],
            "pattern": [
                "Patterns emerge: {theme} weaves through the narrative like threads of {emotion}...",
                "Recognition dawns as {symbol} reveals its connection to {theme}...",
                "The dream logic crystallizes around the interplay of {emotion} and {theme}...",
            ],
            "deep_symbolic": [
                "In the depths of the dream, {symbol} transforms into pure {theme}...",
                "The archetypal {archetype} speaks through symbols of {emotion}...",
                "Layers of meaning unfold as {theme} resonates with ancient {archetype} wisdom...",
            ],
            "creative": [
                "New possibilities arise as {theme} dances with {emotion}...",
                "The creative spark of {archetype} illuminates unexpected connections...",
                "Novel combinations emerge: {symbol} becomes a bridge to {theme}...",
            ],
            "integration": [
                "The dream consolidates its wisdom: {theme} integrated with {emotion}...",
                "As the dream fades, {symbol} remains as a bridge to waking consciousness...",
                "The archetypal {archetype} leaves its mark through embodied {theme}...",
            ],
        }

    def _extract_symbolic_content(self, glyph: Glyph, dream_phase: DreamPhase) -> dict[str, Any]:
        """Extract symbolic content from glyph for dream processing."""
        content = {
            "symbol": glyph.symbol,
            "glyph_type": glyph.glyph_type.value,
            "semantic_tags": list(glyph.semantic_tags),
            "stability_index": glyph.stability_index,
            "collapse_risk": glyph.collapse_risk_level,
            "drift_anchor": glyph.drift_anchor_score,
            "phase_context": dream_phase.value,
        }

        # Add glyph-specific content
        content.update(glyph.content)

        return content

    def _map_to_archetypes(self, glyph: Glyph) -> list[str]:
        """Map glyph characteristics to archetypal patterns."""
        archetypes = []

        # Primary archetype based on glyph type
        for archetype, mapping in self.archetypal_mappings.items():
            if mapping["glyph_type"] == glyph.glyph_type:
                archetypes.append(archetype)

        # Secondary archetypes based on semantic tags
        for tag in glyph.semantic_tags:
            for archetype, mapping in self.archetypal_mappings.items():
                if any(theme in tag.lower() for theme in mapping["themes"]):
                    if archetype not in archetypes:
                        archetypes.append(archetype)

        # Emotional archetypes
        emotion = glyph.emotion_vector
        for archetype, mapping in self.archetypal_mappings.items():
            emphasis = mapping["emotional_emphasis"]
            if any(getattr(emotion, em, 0) > 0.5 for em in emphasis) and archetype not in archetypes:
                archetypes.append(archetype)

        return archetypes[:3]  # Limit to top 3 archetypes

    def _generate_narrative_fragments(self, glyph: Glyph, dream_phase: DreamPhase) -> list[str]:
        """Generate narrative fragments for dream processing."""
        templates = self.narrative_templates.get(dream_phase.value, [])
        if not templates:
            return [f"A {glyph.symbol} appears in the dream..."]

        fragments = []
        archetypes = self._map_to_archetypes(glyph)

        for template in templates[:3]:  # Limit to 3 templates
            # Find archetypal mapping for context
            archetype_mapping = None
            if archetypes:
                archetype_mapping = self.archetypal_mappings.get(archetypes[0])

            # Fill template with glyph context
            context = {
                "symbol": glyph.symbol,
                "theme": (archetype_mapping["themes"][0] if archetype_mapping else "mystery"),
                "emotion": self._get_dominant_emotion(glyph.emotion_vector),
                "archetype": archetypes[0] if archetypes else "unknown",
            }

            try:
                fragment = template.format(**context)
                fragments.append(fragment)
            except KeyError:
                # Fallback if template has missing keys
                fragments.append(f"The {glyph.symbol} manifests in the dream space...")

        return fragments

    def _calculate_symbolic_intensity(self, glyph: Glyph) -> float:
        """Calculate symbolic intensity for dream processing."""
        intensity_factors = []

        # Emotional intensity
        intensity_factors.append(glyph.emotion_vector.intensity * 0.4)

        # Priority importance
        priority_weights = {
            GlyphPriority.CRITICAL: 1.0,
            GlyphPriority.HIGH: 0.8,
            GlyphPriority.MEDIUM: 0.5,
            GlyphPriority.LOW: 0.3,
            GlyphPriority.EPHEMERAL: 0.1,
        }
        intensity_factors.append(priority_weights.get(glyph.priority, 0.5) * 0.3)

        # Stability as inverse intensity (unstable = more intense)
        instability = 1.0 - glyph.stability_index
        intensity_factors.append(instability * 0.2)

        # Semantic richness
        semantic_richness = min(1.0, len(glyph.semantic_tags) / 10.0)
        intensity_factors.append(semantic_richness * 0.1)

        return sum(intensity_factors)

    def _identify_archetypal_source(self, dream_content: dict[str, Any]) -> str:
        """Identify archetypal source from dream content."""
        # Look for archetypal keywords in dream content
        content_text = json.dumps(dream_content).lower()

        archetype_scores = {}
        for archetype, mapping in self.archetypal_mappings.items():
            score = 0
            for theme in mapping["themes"]:
                if theme in content_text:
                    score += 1
            archetype_scores[archetype] = score

        # Return archetype with highest score
        if archetype_scores:
            return max(archetype_scores, key=archetype_scores.get)
        else:
            return "unknown"

    def _create_dream_glyph(
        self,
        dream_content: dict[str, Any],
        archetypal_source: str,
        dream_phase: DreamPhase,
    ) -> Glyph:
        """Create a glyph from dream content."""
        # Get archetypal mapping
        archetype_mapping = self.archetypal_mappings.get(archetypal_source)

        if archetype_mapping:
            glyph_type = archetype_mapping["glyph_type"]
            symbol = archetype_mapping["symbols"][0]  # Use first symbol
        else:
            glyph_type = GlyphType.DREAM
            symbol = "💭"

        # Create dream-derived glyph
        dream_glyph = Glyph(glyph_type=glyph_type, symbol=symbol, priority=GlyphPriority.MEDIUM)

        # Set emotion vector based on dream content
        dream_glyph.emotion_vector = self._extract_dream_emotions(dream_content, archetype_mapping)

        # Add semantic tags
        dream_glyph.add_semantic_tag("dream_derived")
        dream_glyph.add_semantic_tag(f"phase_{dream_phase.value}")
        dream_glyph.add_semantic_tag(f"archetype_{archetypal_source}")

        # Add dream content
        dream_glyph.content["dream_source"] = dream_content
        dream_glyph.content["archetypal_source"] = archetypal_source

        dream_glyph.update_symbolic_hash()
        return dream_glyph

    def _calculate_consolidation_score(self, dream_content: dict[str, Any], glyph: Glyph) -> float:
        """Calculate consolidation score for dream glyph."""
        score_factors = []

        # Content richness
        content_complexity = len(str(dream_content)) / 1000.0  # Normalize by length
        score_factors.append(min(1.0, content_complexity) * 0.3)

        # Emotional coherence
        emotional_coherence = glyph.emotion_vector.stability
        score_factors.append(emotional_coherence * 0.4)

        # Semantic richness
        semantic_score = min(1.0, len(glyph.semantic_tags) / 5.0)
        score_factors.append(semantic_score * 0.2)

        # Symbolic stability
        score_factors.append(glyph.stability_index * 0.1)

        return sum(score_factors)

    def _extract_narrative_context(self, dream_content: dict[str, Any]) -> str:
        """Extract narrative context from dream content."""
        # Look for narrative elements
        narrative_keys = [
            "text",
            "narrative",
            "story",
            "content",
            "description",
        ]

        for key in narrative_keys:
            if key in dream_content:
                return str(dream_content[key])[:500]  # Limit to 500 chars

        # Fallback to general content summary
        return f"Dream content with {len(dream_content)} elements processed"

    def _analyze_emotional_patterns(self, memory_traces: list[dict[str, Any]]) -> dict[str, float]:
        """Analyze emotional patterns across memory traces."""
        emotion_sums = defaultdict(float)
        emotion_counts = defaultdict(int)

        for trace in memory_traces:
            emotions = trace.get("emotions", {})
            for emotion, value in emotions.items():
                emotion_sums[emotion] += value
                emotion_counts[emotion] += 1

        # Calculate averages
        dominant_emotions = {}
        for emotion in emotion_sums:
            if emotion_counts[emotion] > 0:
                dominant_emotions[emotion] = emotion_sums[emotion] / emotion_counts[emotion]

        return dominant_emotions

    def _extract_symbolic_themes(self, memory_traces: list[dict[str, Any]], dream_narrative: str) -> list[str]:
        """Extract symbolic themes from memory traces and dream narrative."""
        themes = set()

        # Extract from memory traces
        for trace in memory_traces:
            tags = trace.get("tags", [])
            themes.update(tags)

        # Extract from dream narrative
        narrative_lower = dream_narrative.lower()
        for mapping in self.archetypal_mappings.values():
            for theme in mapping["themes"]:
                if theme in narrative_lower:
                    themes.add(theme)

        return list(themes)[:5]  # Limit to 5 themes

    def _consolidate_emotions(self, emotion_patterns: dict[str, float]) -> EmotionVector:
        """Consolidate emotion patterns into a single EmotionVector."""
        emotion_vector = EmotionVector()

        # Map patterns to emotion vector attributes
        emotion_mapping = {
            "joy": "joy",
            "happiness": "joy",
            "pleasure": "joy",
            "sadness": "sadness",
            "sorrow": "sadness",
            "grief": "sadness",
            "anger": "anger",
            "rage": "anger",
            "fury": "anger",
            "fear": "fear",
            "anxiety": "fear",
            "worry": "fear",
            "surprise": "surprise",
            "amazement": "surprise",
            "wonder": "surprise",
            "disgust": "disgust",
            "revulsion": "disgust",
            "aversion": "disgust",
            "trust": "trust",
            "confidence": "trust",
            "faith": "trust",
            "anticipation": "anticipation",
            "expectation": "anticipation",
            "hope": "anticipation",
        }

        for pattern, value in emotion_patterns.items():
            emotion_attr = emotion_mapping.get(pattern.lower())
            if emotion_attr and hasattr(emotion_vector, emotion_attr):
                current_value = getattr(emotion_vector, emotion_attr)
                setattr(
                    emotion_vector,
                    emotion_attr,
                    min(1.0, current_value + value),
                )

        # Set meta-emotional properties
        emotion_vector.intensity = min(1.0, sum(emotion_patterns.values()) / len(emotion_patterns))
        emotion_vector.stability = 1.0 - (
            max(emotion_patterns.values()) - min(emotion_patterns.values()) if emotion_patterns else 0
        )

        return emotion_vector

    def _extract_dream_emotions(
        self,
        dream_content: dict[str, Any],
        archetype_mapping: Optional[dict[str, Any]],
    ) -> EmotionVector:
        """Extract emotion vector from dream content."""
        emotion_vector = EmotionVector()

        # Use archetypal emotional emphasis if available
        if archetype_mapping:
            emphasis = archetype_mapping["emotional_emphasis"]
            for emotion in emphasis:
                if hasattr(emotion_vector, emotion):
                    setattr(emotion_vector, emotion, 0.6)  # Moderate emphasis

        # Extract from dream content if available
        if "emotions" in dream_content:
            emotions = dream_content["emotions"]
            for emotion, value in emotions.items():
                if hasattr(emotion_vector, emotion):
                    current = getattr(emotion_vector, emotion)
                    setattr(emotion_vector, emotion, min(1.0, current + value))

        # Set reasonable defaults for meta-emotions
        emotion_vector.intensity = 0.5
        emotion_vector.stability = 0.7
        emotion_vector.valence = 0.3  # Slightly positive
        emotion_vector.arousal = 0.4  # Moderate arousal

        return emotion_vector

    def _get_dominant_emotion(self, emotion_vector: EmotionVector) -> str:
        """Get the dominant emotion from an emotion vector."""
        emotions = {
            "joy": emotion_vector.joy,
            "sadness": emotion_vector.sadness,
            "anger": emotion_vector.anger,
            "fear": emotion_vector.fear,
            "surprise": emotion_vector.surprise,
            "disgust": emotion_vector.disgust,
            "trust": emotion_vector.trust,
            "anticipation": emotion_vector.anticipation,
        }

        return max(emotions, key=emotions.get) if emotions else "neutral"

    def get_statistics(self) -> dict[str, Any]:
        """Get bridge operation statistics."""
        total_seeds = len(self.dream_seeds)
        total_glyphs = len(self.dream_glyphs)

        # Count by dream phase
        phase_counts = defaultdict(int)
        for seed in self.dream_seeds.values():
            phase_counts[seed.dream_phase.value] += 1

        # Count by archetypal source
        archetype_counts = defaultdict(int)
        for glyph in self.dream_glyphs.values():
            archetype_counts[glyph.archetypal_source] += 1

        return {
            "total_dream_seeds": total_seeds,
            "total_dream_glyphs": total_glyphs,
            "dream_phase_distribution": dict(phase_counts),
            "archetypal_distribution": dict(archetype_counts),
            "average_consolidation_score": sum(g.consolidation_score for g in self.dream_glyphs.values())
            / max(1, total_glyphs),
            "average_symbolic_intensity": sum(s.symbolic_intensity for s in self.dream_seeds.values())
            / max(1, total_seeds),
        }


# Create a convenience function for easy integration


def create_glyph_dream_seed(glyph: Glyph, dream_phase: str = "initiation") -> DreamSeed:
    """
    Convenience function to create a dream seed from a glyph.

    Args:
        glyph: Source glyph
        dream_phase: Dream phase name

    Returns:
        DreamSeed instance
    """
    bridge = DreamGlyphBridge()
    phase = DreamPhase(dream_phase.lower())
    return bridge.glyph_to_dream_seed(glyph, phase)


"""
═══════════════════════════════════════════════════════════════════════════════
║ 🌙 LUKHAS AI - DREAM-GLYPH BRIDGE
║ Version: 1.0.0 | Created: 2025-07-25 | Modified: 2025-07-25
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠═══════════════════════════════════════════════════════════════════════════════
║ CAPABILITIES
╠═══════════════════════════════════════════════════════════════════════════════
║ • Glyph-to-Dream Conversion: Transform glyphs into rich dream seeds
║ • Dream-to-Glyph Extraction: Generate glyphs from dream processing
║ • Archetypal Mapping: 8 Jungian archetypes integrated with glyph types
║ • Memory Consolidation: Long-term storage through glyph-based compression
║ • Emotional Context Preservation: Seamless emotion vector transfer
║ • Narrative Generation: Template-based dream narrative creation
║ • Phase-Aware Processing: Support for 5 dream processing phases
║ • Statistical Analytics: Comprehensive operation metrics and reporting
╠═══════════════════════════════════════════════════════════════════════════════
║ INTEGRATION POINTS
╠═══════════════════════════════════════════════════════════════════════════════
║ • GLYPH Subsystem: Full integration with glyph schema and factory patterns
║ • Dream Systems: Native support for dream processing phases and content
║ • Memory System: Memory consolidation and trace analysis integration
║ • Emotion Engine: Emotion vector preservation and processing
║ • Archetypal Framework: Jungian archetype mapping and resonance analysis
║ • Narrative Engine: Template-based story generation and context extraction
╚═══════════════════════════════════════════════════════════════════════════════
"""