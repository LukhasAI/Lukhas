#!/usr/bin/env python3
from __future__ import annotations


"""

#TAG:core
#TAG:glyph
#TAG:neuroplastic
#TAG:colony

LUKHAS (Logical Unified Knowledge Hyper-Adaptable System) - Symbolic Foundry

Copyright (c) 2025 LUKHAS Cognitive AI Development Team
All rights reserved.

This file is part of the LUKHAS Cognitive system, an enterprise artificial general
intelligence platform combining symbolic reasoning, emotional intelligence,
quantum integration, and bio-inspired architecture.

Mission: To illuminate complex reality through rigorous logic, adaptive
intelligence, and human-centred ethics—turning data into understanding,
understanding into foresight, and foresight into shared benefit for people
and planet.

Symbolic Foundry: Glyph fusion and mutation engine providing dynamic evolution
of symbolic representations through entropy-driven mutation, semantic fusion,
creative synthesis, and safety validation with complete lineage tracking for
the GLYPH subsystem.

For more information, visit: https://ai
"""
from datetime import timezone

# ΛTRACE: Symbolic Foundry initialization
# ΛORIGIN_AGENT: Claude Code
# ΛTASK_ID: Task 14

__version__ = "2.0.0"
__author__ = "LUKHAS Development Team"
__email__ = "dev@ai"
__status__ = "Production"

import logging
import random
import uuid
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

import numpy as np

# Internal imports
from .glyph import EmotionVector, Glyph, GlyphPriority, GlyphType

# Configure logger
logger = logging.getLogger(__name__)


@dataclass
class FusionCandidate:
    """Candidate result from glyph fusion operations."""

    fusion_id: str
    source_glyphs: list[str]  # Source glyph IDs
    fused_glyph: Glyph
    fusion_method: str
    compatibility_score: float
    stability_prediction: float
    risk_assessment: dict[str, float]
    creation_timestamp: datetime

    def to_dict(self) -> dict[str, Any]:
        """Convert fusion candidate to dictionary."""
        return {
            "fusion_id": self.fusion_id,
            "source_glyphs": self.source_glyphs,
            "fused_glyph": self.fused_glyph.to_dict(),
            "fusion_method": self.fusion_method,
            "compatibility_score": self.compatibility_score,
            "stability_prediction": self.stability_prediction,
            "risk_assessment": self.risk_assessment,
            "creation_timestamp": self.creation_timestamp.isoformat(),
        }


@dataclass
class MutationResult:
    """Result from glyph mutation operations."""

    mutation_id: str
    source_glyph_id: str
    mutated_glyph: Glyph
    mutation_type: str
    mutation_strength: float
    viability_score: float
    novelty_assessment: float
    safety_classification: str
    mutation_timestamp: datetime

    def to_dict(self) -> dict[str, Any]:
        """Convert mutation result to dictionary."""
        return {
            "mutation_id": self.mutation_id,
            "source_glyph_id": self.source_glyph_id,
            "mutated_glyph": self.mutated_glyph.to_dict(),
            "mutation_type": self.mutation_type,
            "mutation_strength": self.mutation_strength,
            "viability_score": self.viability_score,
            "novelty_assessment": self.novelty_assessment,
            "safety_classification": self.safety_classification,
            "mutation_timestamp": self.mutation_timestamp.isoformat(),
        }


class SymbolicFoundry:
    """
    Glyph fusion and mutation engine for symbolic evolution.

    Provides capabilities for:
    - Fusing multiple glyphs into new symbolic entities
    - Mutating existing glyphs based on various criteria
    - Evaluating compatibility and stability of symbolic operations
    - Managing safety and ethical constraints during evolution
    """

    def __init__(self):
        """Initialize the Symbolic Foundry."""
        self.fusion_history: list[FusionCandidate] = []
        self.mutation_history: list[MutationResult] = []
        self.active_glyphs: dict[str, Glyph] = {}
        self.fusion_patterns: dict[str, dict[str, Any]] = self._initialize_fusion_patterns()
        self.mutation_strategies: dict[str, dict[str, Any]] = self._initialize_mutation_strategies()

        logger.info("Symbolic Foundry initialized")

    def register_glyph(self, glyph: Glyph) -> bool:
        """
        Register a glyph for fusion and mutation operations.

        Args:
            glyph: Glyph instance to register

        Returns:
            True if registration successful
        """
        if glyph.id in self.active_glyphs:
            logger.warning(f"Glyph {glyph.id} already registered")
            return False

        self.active_glyphs[glyph.id] = glyph
        logger.debug(f"Registered glyph {glyph.id}: {glyph.symbol}")
        return True

    def fuse_glyphs(
        self,
        glyph_ids: list[str],
        fusion_method: str = "semantic_blend",
        fusion_strength: float = 0.5,
    ) -> Optional[FusionCandidate]:
        """
            Fuse multiple glyphs into a new symbolic entity.

            Args:
                glyph_ids: List of glyph IDs to fuse
                fusion_method: Method for fusion ("semantic_blend", "emotional_merge",
        "symbolic_synthesis")
                fusion_strength: Strength of fusion operation (0.0-1.0)

            Returns:
                FusionCandidate if successful, None otherwise
        """
        if len(glyph_ids) < 2:
            logger.error("At least 2 glyphs required for fusion")
            return None

        # Validate all glyphs exist
        source_glyphs = []
        for glyph_id in glyph_ids:
            if glyph_id not in self.active_glyphs:
                logger.error(f"Glyph {glyph_id} not found in active glyphs")
                return None
            source_glyphs.append(self.active_glyphs[glyph_id])

        # Check compatibility
        compatibility_score = self._assess_fusion_compatibility(source_glyphs)
        if compatibility_score < 0.3:
            logger.warning(f"Low compatibility score for fusion: {compatibility_score:.3f}")

        # Perform fusion based on method
        try:
            if fusion_method == "semantic_blend":
                fused_glyph = self._semantic_blend_fusion(source_glyphs, fusion_strength)
            elif fusion_method == "emotional_merge":
                fused_glyph = self._emotional_merge_fusion(source_glyphs, fusion_strength)
            elif fusion_method == "symbolic_synthesis":
                fused_glyph = self._symbolic_synthesis_fusion(source_glyphs, fusion_strength)
            else:
                logger.error(f"Unknown fusion method: {fusion_method}")
                return None
        except Exception as e:
            logger.error(f"Fusion failed: {e}")
            return None

        # Create fusion candidate
        fusion_id = f"fusion_{uuid.uuid4().hex[:8]}"
        stability_prediction = self._predict_fusion_stability(fused_glyph, source_glyphs)
        risk_assessment = self._assess_fusion_risks(fused_glyph, source_glyphs)

        candidate = FusionCandidate(
            fusion_id=fusion_id,
            source_glyphs=glyph_ids,
            fused_glyph=fused_glyph,
            fusion_method=fusion_method,
            compatibility_score=compatibility_score,
            stability_prediction=stability_prediction,
            risk_assessment=risk_assessment,
            creation_timestamp=datetime.now(timezone.utc),
        )

        self.fusion_history.append(candidate)
        logger.info(f"Fusion completed: {fusion_id}, compatibility: {compatibility_score:.3f}")

        return candidate

    def mutate_glyph(
        self,
        glyph_id: str,
        mutation_type: str = "evolutionary",
        mutation_strength: float = 0.3,
        target_properties: Optional[dict[str, Any]] = None,
    ) -> Optional[MutationResult]:
        """
            Mutate an existing glyph based on specified criteria.

            Args:
                glyph_id: ID of glyph to mutate
                mutation_type: Type of mutation ("evolutionary", "drift_correction",
        "enhancement", "creative")
                mutation_strength: Strength of mutation (0.0-1.0)
                target_properties: Desired properties for mutation guidance

            Returns:
                MutationResult if successful, None otherwise
        """
        if glyph_id not in self.active_glyphs:
            logger.error(f"Glyph {glyph_id} not found for mutation")
            return None

        source_glyph = self.active_glyphs[glyph_id]

        try:
            # Perform mutation based on type
            if mutation_type == "evolutionary":
                mutated_glyph = self._evolutionary_mutation(source_glyph, mutation_strength)
            elif mutation_type == "drift_correction":
                mutated_glyph = self._drift_correction_mutation(source_glyph, mutation_strength)
            elif mutation_type == "enhancement":
                mutated_glyph = self._enhancement_mutation(source_glyph, mutation_strength, target_properties)
            elif mutation_type == "creative":
                mutated_glyph = self._creative_mutation(source_glyph, mutation_strength)
            else:
                logger.error(f"Unknown mutation type: {mutation_type}")
                return None
        except Exception as e:
            logger.error(f"Mutation failed: {e}")
            return None

        # Assess mutation result
        viability_score = self._assess_mutation_viability(mutated_glyph, source_glyph)
        novelty_assessment = self._assess_mutation_novelty(mutated_glyph, source_glyph)
        safety_classification = self._classify_mutation_safety(mutated_glyph)

        # Create mutation result
        mutation_id = f"mutation_{uuid.uuid4().hex[:8]}"

        result = MutationResult(
            mutation_id=mutation_id,
            source_glyph_id=glyph_id,
            mutated_glyph=mutated_glyph,
            mutation_type=mutation_type,
            mutation_strength=mutation_strength,
            viability_score=viability_score,
            novelty_assessment=novelty_assessment,
            safety_classification=safety_classification,
            mutation_timestamp=datetime.now(timezone.utc),
        )

        self.mutation_history.append(result)
        logger.info(f"Mutation completed: {mutation_id}, viability: {viability_score:.3f}")

        return result

    def _initialize_fusion_patterns(self) -> dict[str, dict[str, Any]]:
        """Initialize fusion pattern configurations."""
        return {
            "semantic_blend": {
                "weight_distribution": [
                    0.4,
                    0.4,
                    0.2,
                ],  # Primary, secondary, tertiary
                "symbol_strategy": "hybrid",
                "emotion_blend_method": "weighted_average",
                "stability_bias": 0.7,
            },
            "emotional_merge": {
                "emotion_dominance": 0.8,
                "semantic_preservation": 0.3,
                "symbol_strategy": "emotion_driven",
                "stability_bias": 0.5,
            },
            "symbolic_synthesis": {
                "creativity_factor": 0.9,
                "novelty_boost": 0.6,
                "symbol_strategy": "creative_generation",
                "stability_bias": 0.4,
            },
        }

    def _initialize_mutation_strategies(self) -> dict[str, dict[str, Any]]:
        """Initialize mutation strategy configurations."""
        return {
            "evolutionary": {
                "change_rate": 0.3,
                "preserve_core": True,
                "allow_type_change": False,
                "stability_importance": 0.8,
            },
            "drift_correction": {
                "anchor_strength": 0.9,
                "correction_focus": "stability",
                "preserve_identity": True,
                "safety_priority": 0.9,
            },
            "enhancement": {
                "improvement_focus": "targeted",
                "allow_radical_change": False,
                "preserve_semantics": True,
                "optimization_bias": 0.7,
            },
            "creative": {
                "novelty_emphasis": 0.8,
                "allow_type_change": True,
                "creative_freedom": 0.9,
                "safety_checks": True,
            },
        }

    def _assess_fusion_compatibility(self, glyphs: list[Glyph]) -> float:
        """Assess compatibility of glyphs for fusion."""
        if len(glyphs) < 2:
            return 0.0

        compatibility_factors = []

        # Type compatibility
        type_similarity = self._calculate_type_compatibility(glyphs)
        compatibility_factors.append(type_similarity * 0.3)

        # Emotional compatibility
        emotion_harmony = self._calculate_emotion_harmony(glyphs)
        compatibility_factors.append(emotion_harmony * 0.4)

        # Temporal compatibility
        temporal_alignment = self._calculate_temporal_alignment(glyphs)
        compatibility_factors.append(temporal_alignment * 0.2)

        # Semantic compatibility
        semantic_coherence = self._calculate_semantic_coherence(glyphs)
        compatibility_factors.append(semantic_coherence * 0.1)

        return sum(compatibility_factors)

    def _calculate_type_compatibility(self, glyphs: list[Glyph]) -> float:
        """Calculate type compatibility between glyphs."""
        types = [g.glyph_type for g in glyphs]
        unique_types = set(types)

        # Compatible type pairs
        compatible_pairs = {
            (GlyphType.MEMORY, GlyphType.EMOTION),
            (GlyphType.DREAM, GlyphType.MEMORY),
            (GlyphType.CAUSAL, GlyphType.TEMPORAL),
            (GlyphType.ACTION, GlyphType.EMOTION),
            (GlyphType.DRIFT, GlyphType.COLLAPSE),
        }

        if len(unique_types) == 1:
            return 1.0  # Same type = perfect compatibility
        elif len(unique_types) == 2:
            type_pair = tuple(sorted(unique_types))
            return 0.8 if type_pair in compatible_pairs else 0.4
        else:
            return 0.2  # Multiple types = low compatibility

    def _calculate_emotion_harmony(self, glyphs: list[Glyph]) -> float:
        """Calculate emotional harmony between glyphs."""
        if not glyphs:
            return 0.0

        # Calculate average emotional distance
        total_distance = 0.0
        comparisons = 0

        for i, glyph1 in enumerate(glyphs):
            for glyph2 in glyphs[i + 1 :]:
                distance = glyph1.emotion_vector.distance_to(glyph2.emotion_vector)
                total_distance += distance
                comparisons += 1

        if comparisons == 0:
            return 1.0

        average_distance = total_distance / comparisons
        # Convert distance to harmony (inverse relationship)
        harmony = max(0.0, 1.0 - average_distance / 2.0)
        return harmony

    def _calculate_temporal_alignment(self, glyphs: list[Glyph]) -> float:
        """Calculate temporal alignment between glyphs."""
        if not glyphs:
            return 0.0

        # Check age similarity
        ages = [g.temporal_stamp.age_seconds() for g in glyphs]
        if not ages:
            return 1.0

        age_variance = np.var(ages) if len(ages) > 1 else 0.0
        max_variance = (24 * 3600) ** 2  # 1 day variance threshold

        alignment = max(0.0, 1.0 - age_variance / max_variance)
        return alignment

    def _calculate_semantic_coherence(self, glyphs: list[Glyph]) -> float:
        """Calculate semantic coherence between glyphs."""
        if not glyphs:
            return 0.0

        # Check for common semantic tags
        all_tags = [set(g.semantic_tags) for g in glyphs]
        if not all_tags:
            return 0.5

        # Calculate Jaccard similarity across all tag sets
        union_tags = set().union(*all_tags)
        intersection_tags = set.intersection(*all_tags) if all_tags else set()

        if not union_tags:
            return 1.0

        coherence = len(intersection_tags) / len(union_tags)
        return coherence

    def _semantic_blend_fusion(self, glyphs: list[Glyph], strength: float) -> Glyph:
        """Perform semantic blend fusion of glyphs."""
        # Create new glyph with blended properties
        fused_glyph = Glyph()
        fused_glyph.glyph_type = glyphs[0].glyph_type  # Use primary glyph type

        # Blend symbols
        symbols = [g.symbol for g in glyphs]
        fused_glyph.symbol = self._blend_symbols(symbols, "semantic")

        # Blend emotions
        fused_glyph.emotion_vector = self._blend_emotions(glyphs, strength)

        # Combine semantic tags
        all_tags = set()
        for glyph in glyphs:
            all_tags.update(glyph.semantic_tags)
        fused_glyph.semantic_tags = all_tags

        # Set fusion-specific tags
        fused_glyph.add_semantic_tag("fused_glyph")
        fused_glyph.add_semantic_tag(f"fusion_{len(glyphs)}_way")

        # Blend content
        fused_glyph.content = self._blend_content(glyphs, "semantic")

        # Update derived properties
        fused_glyph.update_symbolic_hash()

        return fused_glyph

    def _emotional_merge_fusion(self, glyphs: list[Glyph], strength: float) -> Glyph:
        """Perform emotional merge fusion of glyphs."""
        # Find glyph with strongest emotional intensity
        max(glyphs, key=lambda g: g.emotion_vector.intensity)

        fused_glyph = Glyph()
        fused_glyph.glyph_type = GlyphType.EMOTION
        fused_glyph.symbol = self._blend_symbols([g.symbol for g in glyphs], "emotional")

        # Emotion-focused blending
        fused_glyph.emotion_vector = self._blend_emotions(glyphs, strength, focus="intensity")

        # Combine memory keys and drift anchors
        for glyph in glyphs:
            fused_glyph.memory_keys.update(glyph.memory_keys)
            fused_glyph.drift_anchor_score = max(fused_glyph.drift_anchor_score, glyph.drift_anchor_score)

        # Emotional fusion tags
        fused_glyph.add_semantic_tag("emotional_fusion")
        fused_glyph.add_semantic_tag("intensity_merge")

        fused_glyph.update_symbolic_hash()
        return fused_glyph

    def _symbolic_synthesis_fusion(self, glyphs: list[Glyph], strength: float) -> Glyph:
        """Perform symbolic synthesis fusion of glyphs."""
        fused_glyph = Glyph()
        fused_glyph.glyph_type = GlyphType.ACTION  # Synthesis creates action potential

        # Creative symbol generation
        fused_glyph.symbol = self._generate_synthesis_symbol(glyphs, strength)

        # Synthesize emotions with creative boost
        fused_glyph.emotion_vector = self._synthesize_emotions(glyphs, strength)

        # Creative content synthesis
        fused_glyph.content = self._synthesize_content(glyphs)

        # Synthesis-specific properties
        fused_glyph.add_semantic_tag("symbolic_synthesis")
        fused_glyph.add_semantic_tag("creative_fusion")
        fused_glyph.priority = GlyphPriority.HIGH  # Synthesis results are important

        fused_glyph.update_symbolic_hash()
        return fused_glyph

    def _blend_symbols(self, symbols: list[str], method: str) -> str:
        """Blend multiple symbols into a new symbol."""
        if not symbols:
            return "?"

        if method == "semantic":
            # Take characters from each symbol
            result = ""
            for i, symbol in enumerate(symbols):
                if i < len(symbol):
                    result += symbol[i]
            return result[:4] or symbols[0]  # Limit to 4 chars

        elif method == "emotional":
            # Use symbol with highest emotional resonance
            return max(symbols, key=lambda s: len(s))

        else:
            return symbols[0]

    def _blend_emotions(self, glyphs: list[Glyph], strength: float, focus: str = "average") -> EmotionVector:
        """Blend emotion vectors from multiple glyphs."""
        if not glyphs:
            return EmotionVector()

        if focus == "intensity":
            # Weight by emotional intensity
            weights = [g.emotion_vector.intensity for g in glyphs]
            total_weight = sum(weights) if sum(weights) > 0 else 1.0
            weights = [w / total_weight for w in weights]
        else:
            # Equal weighting
            weights = [1.0 / len(glyphs)] * len(glyphs)

        # Blend primary emotions
        blended = EmotionVector()
        for i, glyph in enumerate(glyphs):
            weight = weights[i] * strength
            ev = glyph.emotion_vector

            blended.joy += ev.joy * weight
            blended.sadness += ev.sadness * weight
            blended.anger += ev.anger * weight
            blended.fear += ev.fear * weight
            blended.surprise += ev.surprise * weight
            blended.disgust += ev.disgust * weight
            blended.trust += ev.trust * weight
            blended.anticipation += ev.anticipation * weight

            blended.intensity += ev.intensity * weight
            blended.valence += ev.valence * weight
            blended.arousal += ev.arousal * weight
            blended.stability += ev.stability * weight

        return blended

    def _blend_content(self, glyphs: list[Glyph], method: str) -> dict[str, Any]:
        """Blend content from multiple glyphs."""
        blended_content = {}

        for glyph in glyphs:
            for key, value in glyph.content.items():
                if key not in blended_content:
                    blended_content[key] = []
                blended_content[key].append(value)

        # Consolidate content
        result = {}
        for key, values in blended_content.items():
            if len(values) == 1:
                result[key] = values[0]
            else:
                result[key] = values

        return result

    def _generate_synthesis_symbol(self, glyphs: list[Glyph], strength: float) -> str:
        """Generate creative synthesis symbol."""
        # Extract unique characters from all symbols
        all_chars = set()
        for glyph in glyphs:
            all_chars.update(glyph.symbol)

        # Create creative combination
        unique_chars = list(all_chars)
        if len(unique_chars) >= 2:
            # Combine first characters creatively
            return "".join(unique_chars[:3]) + "⚡"  # Add synthesis marker
        else:
            return glyphs[0].symbol + "✨"  # Add creative marker

    def _synthesize_emotions(self, glyphs: list[Glyph], strength: float) -> EmotionVector:
        """Synthesize emotions with creative enhancement."""
        base_emotion = self._blend_emotions(glyphs, strength)

        # Add creative boost
        base_emotion.surprise = min(1.0, base_emotion.surprise + 0.2)
        base_emotion.anticipation = min(1.0, base_emotion.anticipation + 0.1)
        base_emotion.intensity = min(1.0, base_emotion.intensity + 0.15)

        return base_emotion

    def _synthesize_content(self, glyphs: list[Glyph]) -> dict[str, Any]:
        """Synthesize content with creative combinations."""
        content = self._blend_content(glyphs, "synthesis")
        content["synthesis_metadata"] = {
            "source_count": len(glyphs),
            "synthesis_timestamp": datetime.now(timezone.utc).isoformat(),
            "creative_fusion": True,
        }
        return content

    def _evolutionary_mutation(self, glyph: Glyph, strength: float) -> Glyph:
        """Perform evolutionary mutation on a glyph."""
        mutated = Glyph()

        # Copy base properties
        mutated.glyph_type = glyph.glyph_type
        mutated.priority = glyph.priority
        mutated.symbol = self._mutate_symbol(glyph.symbol, strength, "evolutionary")

        # Evolve emotion vector
        mutated.emotion_vector = self._evolve_emotion_vector(glyph.emotion_vector, strength)

        # Copy and evolve semantic tags
        mutated.semantic_tags = glyph.semantic_tags.copy()
        mutated.add_semantic_tag("evolved")
        mutated.add_semantic_tag(f"evolution_gen_{random.randint(1, 10)}")

        # Inherit memory associations
        mutated.memory_keys = glyph.memory_keys.copy()
        mutated.drift_anchor_score = glyph.drift_anchor_score

        # Set up causal link
        mutated.causal_link.parent_glyph_id = glyph.id
        mutated.causal_link.causal_origin_id = glyph.causal_link.causal_origin_id or glyph.id

        mutated.update_symbolic_hash()
        return mutated

    def _drift_correction_mutation(self, glyph: Glyph, strength: float) -> Glyph:
        """Perform drift correction mutation."""
        mutated = Glyph()

        # Preserve core identity
        mutated.glyph_type = glyph.glyph_type
        mutated.priority = max(glyph.priority, GlyphPriority.HIGH)  # Boost priority
        mutated.symbol = glyph.symbol  # Keep original symbol

        # Stabilize emotion vector
        mutated.emotion_vector = self._stabilize_emotion_vector(glyph.emotion_vector, strength)

        # Add stabilization tags
        mutated.semantic_tags = glyph.semantic_tags.copy()
        mutated.add_semantic_tag("drift_corrected")
        mutated.add_semantic_tag("stabilized")

        # Strengthen drift anchor
        mutated.drift_anchor_score = min(1.0, glyph.drift_anchor_score + strength * 0.3)
        mutated.stability_index = min(1.0, glyph.stability_index + strength * 0.2)

        # Maintain causal links
        mutated.causal_link = glyph.causal_link

        mutated.update_symbolic_hash()
        return mutated

    def _enhancement_mutation(self, glyph: Glyph, strength: float, targets: Optional[dict[str, Any]]) -> Glyph:
        """Perform enhancement mutation based on target properties."""
        mutated = Glyph()

        # Copy base structure
        mutated.glyph_type = glyph.glyph_type
        mutated.symbol = glyph.symbol

        # Enhance based on targets
        if targets:
            if "emotion_boost" in targets:
                mutated.emotion_vector = self._boost_emotion_vector(
                    glyph.emotion_vector, targets["emotion_boost"], strength
                )
            else:
                mutated.emotion_vector = glyph.emotion_vector

            if targets.get("priority_boost"):
                mutated.priority = GlyphPriority.HIGH
            else:
                mutated.priority = glyph.priority
        else:
            # Default enhancement
            mutated.emotion_vector = self._enhance_emotion_vector(glyph.emotion_vector, strength)
            mutated.priority = glyph.priority

        # Enhancement tags
        mutated.semantic_tags = glyph.semantic_tags.copy()
        mutated.add_semantic_tag("enhanced")
        mutated.add_semantic_tag("optimized")

        mutated.update_symbolic_hash()
        return mutated

    def _creative_mutation(self, glyph: Glyph, strength: float) -> Glyph:
        """Perform creative mutation with high novelty."""
        mutated = Glyph()

        # Allow type change for creativity
        if strength > 0.7:
            creative_types = [
                GlyphType.ACTION,
                GlyphType.DREAM,
                GlyphType.EMOTION,
            ]
            mutated.glyph_type = random.choice(creative_types)
        else:
            mutated.glyph_type = glyph.glyph_type

        # Creative symbol mutation
        mutated.symbol = self._mutate_symbol(glyph.symbol, strength, "creative")

        # Creative emotion evolution
        mutated.emotion_vector = self._creative_emotion_evolution(glyph.emotion_vector, strength)

        # Creative semantic expansion
        mutated.semantic_tags = glyph.semantic_tags.copy()
        mutated.add_semantic_tag("creative_mutation")
        mutated.add_semantic_tag("novel_variant")

        # Creative content
        mutated.content = glyph.content.copy()
        mutated.content["creative_seed"] = random.randint(1000, 9999)

        mutated.update_symbolic_hash()
        return mutated

    def _mutate_symbol(self, symbol: str, strength: float, mutation_type: str) -> str:
        """Mutate a glyph symbol based on type and strength."""
        if mutation_type == "evolutionary":
            # Gradual changes
            if strength > 0.5 and len(symbol) > 1:
                # Change one character
                chars = list(symbol)
                idx = random.randint(0, len(chars) - 1)
                chars[idx] = chr(ord(chars[idx]) + random.choice([-1, 1]))
                return "".join(chars)
            return symbol

        elif mutation_type == "creative":
            # More dramatic changes
            if strength > 0.6:
                # Add creative elements
                creative_additions = ["✨", "⚡", "🔮", "💫", "🌟"]
                return symbol + random.choice(creative_additions)
            return symbol

        return symbol

    def _evolve_emotion_vector(self, emotion: EmotionVector, strength: float) -> EmotionVector:
        """Evolve emotion vector gradually."""
        evolved = EmotionVector()

        # Copy base emotions with small random variations
        variation = strength * 0.1
        evolved.joy = max(0.0, min(1.0, emotion.joy + random.uniform(-variation, variation)))
        evolved.sadness = max(
            0.0,
            min(1.0, emotion.sadness + random.uniform(-variation, variation)),
        )
        evolved.anger = max(
            0.0,
            min(1.0, emotion.anger + random.uniform(-variation, variation)),
        )
        evolved.fear = max(0.0, min(1.0, emotion.fear + random.uniform(-variation, variation)))
        evolved.surprise = max(
            0.0,
            min(1.0, emotion.surprise + random.uniform(-variation, variation)),
        )
        evolved.disgust = max(
            0.0,
            min(1.0, emotion.disgust + random.uniform(-variation, variation)),
        )
        evolved.trust = max(
            0.0,
            min(1.0, emotion.trust + random.uniform(-variation, variation)),
        )
        evolved.anticipation = max(
            0.0,
            min(
                1.0,
                emotion.anticipation + random.uniform(-variation, variation),
            ),
        )

        # Evolve meta-emotional states
        evolved.intensity = emotion.intensity
        evolved.valence = emotion.valence
        evolved.arousal = emotion.arousal
        evolved.stability = min(1.0, emotion.stability + strength * 0.05)  # Slight stability boost

        return evolved

    def _stabilize_emotion_vector(self, emotion: EmotionVector, strength: float) -> EmotionVector:
        """Stabilize emotion vector to reduce drift."""
        stabilized = EmotionVector()

        # Move toward neutral/stable state
        stabilization_factor = strength * 0.5

        stabilized.joy = emotion.joy * (1 - stabilization_factor) + 0.3 * stabilization_factor
        stabilized.sadness = emotion.sadness * (1 - stabilization_factor)
        stabilized.anger = emotion.anger * (1 - stabilization_factor)
        stabilized.fear = emotion.fear * (1 - stabilization_factor)
        stabilized.surprise = emotion.surprise * (1 - stabilization_factor)
        stabilized.disgust = emotion.disgust * (1 - stabilization_factor)
        stabilized.trust = emotion.trust * (1 - stabilization_factor) + 0.4 * stabilization_factor
        stabilized.anticipation = emotion.anticipation * (1 - stabilization_factor)

        # Boost stability metrics
        stabilized.stability = min(1.0, emotion.stability + strength * 0.3)
        stabilized.intensity = emotion.intensity * (1 - stabilization_factor * 0.5)
        stabilized.valence = emotion.valence * 0.8  # Move toward neutral
        stabilized.arousal = emotion.arousal * (1 - stabilization_factor * 0.3)

        return stabilized

    def _enhance_emotion_vector(self, emotion: EmotionVector, strength: float) -> EmotionVector:
        """Enhance positive aspects of emotion vector."""
        enhanced = EmotionVector()

        # Boost positive emotions
        enhanced.joy = min(1.0, emotion.joy + strength * 0.2)
        enhanced.trust = min(1.0, emotion.trust + strength * 0.15)
        enhanced.anticipation = min(1.0, emotion.anticipation + strength * 0.1)

        # Preserve other emotions
        enhanced.sadness = emotion.sadness
        enhanced.anger = emotion.anger
        enhanced.fear = emotion.fear
        enhanced.surprise = emotion.surprise
        enhanced.disgust = emotion.disgust

        # Enhance meta-emotional states
        enhanced.intensity = min(1.0, emotion.intensity + strength * 0.1)
        enhanced.valence = min(1.0, emotion.valence + strength * 0.2)
        enhanced.arousal = emotion.arousal
        enhanced.stability = min(1.0, emotion.stability + strength * 0.1)

        return enhanced

    def _boost_emotion_vector(self, emotion: EmotionVector, boost_target: str, strength: float) -> EmotionVector:
        """Boost specific emotion in the vector."""
        boosted = EmotionVector()

        # Copy base emotions
        boosted.joy = emotion.joy
        boosted.sadness = emotion.sadness
        boosted.anger = emotion.anger
        boosted.fear = emotion.fear
        boosted.surprise = emotion.surprise
        boosted.disgust = emotion.disgust
        boosted.trust = emotion.trust
        boosted.anticipation = emotion.anticipation

        # Apply targeted boost
        boost_amount = strength * 0.3
        if hasattr(boosted, boost_target):
            current_value = getattr(boosted, boost_target)
            setattr(boosted, boost_target, min(1.0, current_value + boost_amount))

        # Copy meta-emotional states
        boosted.intensity = emotion.intensity
        boosted.valence = emotion.valence
        boosted.arousal = emotion.arousal
        boosted.stability = emotion.stability

        return boosted

    def _creative_emotion_evolution(self, emotion: EmotionVector, strength: float) -> EmotionVector:
        """Perform creative evolution of emotion vector."""
        creative = EmotionVector()

        # Randomly boost different emotions for creativity
        emotions = ["joy", "surprise", "anticipation", "trust"]
        target_emotion = random.choice(emotions)

        creative.joy = emotion.joy
        creative.sadness = emotion.sadness
        creative.anger = emotion.anger
        creative.fear = emotion.fear
        creative.surprise = emotion.surprise
        creative.disgust = emotion.disgust
        creative.trust = emotion.trust
        creative.anticipation = emotion.anticipation

        # Apply creative boost
        if hasattr(creative, target_emotion):
            current = getattr(creative, target_emotion)
            setattr(creative, target_emotion, min(1.0, current + strength * 0.4))

        # Enhance creativity-related meta-states
        creative.intensity = min(1.0, emotion.intensity + strength * 0.2)
        creative.valence = emotion.valence
        creative.arousal = min(1.0, emotion.arousal + strength * 0.15)
        creative.stability = emotion.stability

        return creative

    def _predict_fusion_stability(self, fused_glyph: Glyph, source_glyphs: list[Glyph]) -> float:
        """Predict stability of fused glyph."""
        # Base stability from source glyphs
        source_stability = sum(g.stability_index for g in source_glyphs) / len(source_glyphs)

        # Complexity penalty (more sources = lower stability)
        complexity_penalty = (len(source_glyphs) - 2) * 0.1

        # Type consistency bonus
        types = [g.glyph_type for g in source_glyphs]
        type_consistency = 1.0 if len(set(types)) == 1 else 0.7

        predicted_stability = source_stability * type_consistency - complexity_penalty
        return max(0.0, min(1.0, predicted_stability))

    def _assess_fusion_risks(self, fused_glyph: Glyph, source_glyphs: list[Glyph]) -> dict[str, float]:
        """Assess risks associated with fusion."""
        risks = {
            "identity_loss": 0.0,
            "instability": 0.0,
            "semantic_drift": 0.0,
            "emotional_overflow": 0.0,
        }

        # Identity loss risk (more sources = higher risk)
        risks["identity_loss"] = min(0.8, (len(source_glyphs) - 2) * 0.2)

        # Instability risk (based on source instability)
        avg_instability = sum(1.0 - g.stability_index for g in source_glyphs) / len(source_glyphs)
        risks["instability"] = avg_instability

        # Semantic drift risk (different types)
        types = [g.glyph_type for g in source_glyphs]
        if len(set(types)) > 1:
            risks["semantic_drift"] = 0.4

        # Emotional overflow risk (high intensity)
        if fused_glyph.emotion_vector.intensity > 0.8:
            risks["emotional_overflow"] = 0.6

        return risks

    def _assess_mutation_viability(self, mutated_glyph: Glyph, source_glyph: Glyph) -> float:
        """Assess viability of mutation result."""
        viability_factors = []

        # Stability preservation
        stability_preservation = 1.0 - abs(mutated_glyph.stability_index - source_glyph.stability_index)
        viability_factors.append(stability_preservation * 0.4)

        # Emotional coherence
        emotion_distance = mutated_glyph.emotion_vector.distance_to(source_glyph.emotion_vector)
        emotion_coherence = max(0.0, 1.0 - emotion_distance / 2.0)
        viability_factors.append(emotion_coherence * 0.3)

        # Type consistency
        type_consistency = 1.0 if mutated_glyph.glyph_type == source_glyph.glyph_type else 0.6
        viability_factors.append(type_consistency * 0.2)

        # Priority appropriateness
        priority_factor = 0.8 if mutated_glyph.priority.value >= source_glyph.priority.value else 0.5
        viability_factors.append(priority_factor * 0.1)

        return sum(viability_factors)

    def _assess_mutation_novelty(self, mutated_glyph: Glyph, source_glyph: Glyph) -> float:
        """Assess novelty of mutation result."""
        novelty_factors = []

        # Symbol difference
        symbol_novelty = 0.0 if mutated_glyph.symbol == source_glyph.symbol else 0.5
        novelty_factors.append(symbol_novelty)

        # Emotional change
        emotion_distance = mutated_glyph.emotion_vector.distance_to(source_glyph.emotion_vector)
        emotion_novelty = min(1.0, emotion_distance)
        novelty_factors.append(emotion_novelty)

        # Semantic tag differences
        source_tags = source_glyph.semantic_tags
        mutated_tags = mutated_glyph.semantic_tags
        new_tags = mutated_tags - source_tags
        tag_novelty = min(1.0, len(new_tags) / max(1, len(source_tags)))
        novelty_factors.append(tag_novelty)

        return sum(novelty_factors) / len(novelty_factors)

    def _classify_mutation_safety(self, mutated_glyph: Glyph) -> str:
        """Classify safety level of mutated glyph."""
        # Check for stability
        if mutated_glyph.stability_index < 0.3:
            return "RESTRICTED"

        # Check emotional extremes
        emotion = mutated_glyph.emotion_vector
        if emotion.anger > 0.9 or emotion.fear > 0.9 or emotion.disgust > 0.9:
            return "REVIEW"

        # Check for collapse risk
        if mutated_glyph.collapse_risk_level > 0.7:
            return "CAUTION"

        return "SAFE"

    def get_fusion_statistics(self) -> dict[str, Any]:
        """Get statistics about fusion operations."""
        if not self.fusion_history:
            return {"fusion_count": 0}

        compatibilities = [f.compatibility_score for f in self.fusion_history]
        stabilities = [f.stability_prediction for f in self.fusion_history]

        return {
            "fusion_count": len(self.fusion_history),
            "average_compatibility": sum(compatibilities) / len(compatibilities),
            "average_stability": sum(stabilities) / len(stabilities),
            "fusion_methods": Counter(f.fusion_method for f in self.fusion_history),
            "successful_fusions": len([f for f in self.fusion_history if f.compatibility_score > 0.6]),
        }

    def get_mutation_statistics(self) -> dict[str, Any]:
        """Get statistics about mutation operations."""
        if not self.mutation_history:
            return {"mutation_count": 0}

        viabilities = [m.viability_score for m in self.mutation_history]
        novelties = [m.novelty_assessment for m in self.mutation_history]

        return {
            "mutation_count": len(self.mutation_history),
            "average_viability": sum(viabilities) / len(viabilities),
            "average_novelty": sum(novelties) / len(novelties),
            "mutation_types": Counter(m.mutation_type for m in self.mutation_history),
            "safe_mutations": len([m for m in self.mutation_history if m.safety_classification == "SAFE"]),
        }


"""
═══════════════════════════════════════════════════════════════════════════════
║ 🏭 LUKHAS AI - SYMBOLIC FOUNDRY
║ Version: 2.0.0 | Created: 2025-07-25 | Modified: 2025-07-25
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠═══════════════════════════════════════════════════════════════════════════════
║ CAPABILITIES
╠═══════════════════════════════════════════════════════════════════════════════
║ • Glyph Fusion: Multi-glyph semantic blending and synthesis
║ • Mutation Engine: Evolutionary, corrective, enhancement, and creative mutations
║ • Compatibility Assessment: Multi-factor fusion compatibility analysis
║ • Stability Prediction: Future stability forecasting for fused entities
║ • Risk Assessment: Comprehensive safety and viability evaluation
║ • Lineage Tracking: Complete provenance and causal relationship management
║ • Safety Classification: SAFE/CAUTION/REVIEW/RESTRICTED classification system
║ • Statistics Generation: Comprehensive analytics for fusion and mutation operations
╠═══════════════════════════════════════════════════════════════════════════════
║ INTEGRATION POINTS
╠═══════════════════════════════════════════════════════════════════════════════
║ • Core Glyph System: Full integration with Glyph schema and factory patterns
║ • Memory System: Memory key inheritance and drift anchor management
║ • Emotion Engine: Sophisticated emotion vector blending and evolution
║ • Causal Tracking: Parent-child relationship management and lineage preservation
║ • Safety Framework: Multi-level safety assessment and risk management
║ • Temporal System: Age-based compatibility and temporal alignment assessment
╚═══════════════════════════════════════════════════════════════════════════════
"""