"""

#TAG:core
#TAG:glyph
#TAG:neuroplastic
#TAG:colony

══════════════════════════════════════════════════════════════════════════════════
║ 🗺️ LUKHAS AI - CONTEXTUAL MAPPING COLONY
║ Context-aware biological to symbolic mapping with deep understanding
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: contextual_mapping_colony.py
║ Path: bio/symbolic/contextual_mapping_colony.py
║ Version: 1.0.0 | Created: 2025-07-28
║ Authors: LUKHAS Bio-Symbolic Team | Claude Code
╚══════════════════════════════════════════════════════════════════════════════════
"""
from consciousness.qi import qi
import streamlit as st
from datetime import timezone

import logging
from collections import defaultdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

import numpy as np

from lukhas.core.colonies.base_colony import BaseColony
from lukhas.core.symbolism.tags import TagPermission, TagScope

logger = logging.getLogger("ΛTRACE.bio.mapping", timezone)


class ContextLayer(Enum):
    """Context layers for hierarchical understanding."""

    ENVIRONMENTAL = "environmental"
    PERSONAL = "personal"
    SOCIAL = "social"
    QUANTUM = "quantum"
    SYMBOLIC = "symbolic"


class ContextualMappingColony(BaseColony):
    """
    Maps biological states to GLYPHs with deep context understanding.
    Implements fuzzy boundaries, multi-GLYPH representation, and temporal evolution.
    """

    def __init__(self, colony_id: str = "contextual_mapping_colony"):
        super().__init__(
            colony_id,
            capabilities=[
                "context_mapping",
                "fuzzy_boundaries",
                "temporal_evolution",
            ],
        )

        # Context layer processors
        self.context_processors = {
            ContextLayer.ENVIRONMENTAL: self._process_environmental_context,
            ContextLayer.PERSONAL: self._process_personal_context,
            ContextLayer.SOCIAL: self._process_social_context,
            ContextLayer.QUANTUM: self._process_quantum_context,
            ContextLayer.SYMBOLIC: self._process_symbolic_context,
        }

        # Fuzzy membership functions for GLYPH boundaries
        self.fuzzy_boundaries = self._initialize_fuzzy_boundaries()

        # Multi-GLYPH activation tracking
        self.active_glyphs: dict[str, float] = {}
        self.glyph_evolution_history = defaultdict(list)

        # Temporal evolution parameters
        self.temporal_config = {
            "evolution_rate": 0.1,  # How fast GLYPHs can change
            "momentum": 0.7,  # How much past influences present
            "max_active_glyphs": 5,  # Maximum simultaneous active GLYPHs
        }

        # Colony consensus cache
        self.consensus_cache = {}
        self.consensus_ttl = timedelta(seconds=60)

        # Quantum superposition states
        self.qi_states = {}

        # Context feature extractors
        self.feature_extractors = self._initialize_feature_extractors()

        logger.info(f"🗺️ ContextualMappingColony '{colony_id}' initialized")

    async def execute_task(self, task_id: str, task_data: dict[str, Any]) -> dict[str, Any]:
        """
        Map biological data to GLYPHs with deep context understanding.

        Args:
            task_id: Unique task identifier
            task_data: Contains bio_data, context, and thresholds

        Returns:
            Contextual GLYPH mappings with probabilities
        """
        with self.tracer.trace_operation("contextual_bio_mapping") as span:
            self.tracer.add_tag(span, "task_id", task_id)

            # Extract inputs
            bio_data = task_data.get("bio_data", {})
            context = task_data.get("context", {})
            thresholds = task_data.get("thresholds", {})

            # Process all context layers
            context_features = await self._process_context_layers(context, bio_data)

            # Calculate fuzzy GLYPH activations
            glyph_activations = self._calculate_fuzzy_activations(bio_data, context_features, thresholds)

            # Apply temporal evolution
            evolved_glyphs = self._apply_temporal_evolution(glyph_activations)

            # Get colony consensus on mappings
            consensus_glyphs = await self._get_colony_consensus(evolved_glyphs, context_features)

            # Handle quantum superposition
            qi_glyphs = self._process_quantum_superposition(consensus_glyphs, context_features)

            # Select final GLYPHs (top N by activation)
            final_glyphs = self._select_final_glyphs(qi_glyphs)

            # Calculate mapping confidence
            confidence = self._calculate_mapping_confidence(final_glyphs, context_features)

            # Prepare result
            result = {
                "task_id": task_id,
                "primary_glyph": final_glyphs[0] if final_glyphs else None,
                "active_glyphs": final_glyphs,
                "glyph_probabilities": qi_glyphs,
                "context_features": self._summarize_context(context_features),
                "confidence": confidence,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "colony_id": self.colony_id,
            }

            # Update history
            self._update_glyph_history(final_glyphs)

            # Tag mapping quality
            self._tag_mapping_quality(confidence)

            return result

    def _initialize_fuzzy_boundaries(self) -> dict[str, dict[str, Any]]:
        """Initialize fuzzy membership functions for GLYPH boundaries."""
        return {
            # Energy GLYPHs with Gaussian membership
            "ΛPOWER_ABUNDANT": {
                "center": 0.9,
                "width": 0.15,
                "type": "gaussian",
            },
            "ΛPOWER_BALANCED": {
                "center": 0.7,
                "width": 0.2,
                "type": "gaussian",
            },
            "ΛPOWER_CONSERVE": {
                "center": 0.5,
                "width": 0.2,
                "type": "gaussian",
            },
            "ΛPOWER_CRITICAL": {
                "center": 0.2,
                "width": 0.15,
                "type": "gaussian",
            },
            # Stress GLYPHs with sigmoid membership
            "ΛSTRESS_TRANSFORM": {
                "threshold": 0.8,
                "slope": 10,
                "type": "sigmoid",
            },
            "ΛSTRESS_ADAPT": {"center": 0.6, "width": 0.3, "type": "gaussian"},
            "ΛSTRESS_BUFFER": {
                "center": 0.4,
                "width": 0.2,
                "type": "gaussian",
            },
            "ΛSTRESS_FLOW": {
                "threshold": 0.3,
                "slope": -10,
                "type": "sigmoid",
            },
            # Add more GLYPHs as needed...
        }

    def _initialize_feature_extractors(self) -> dict[str, callable]:
        """Initialize context feature extraction functions."""
        return {
            "temporal": self._extract_temporal_features,
            "environmental": self._extract_environmental_features,
            "activity": self._extract_activity_features,
            "historical": self._extract_historical_features,
            "symbolic": self._extract_symbolic_features,
        }

    async def _process_context_layers(
        self, context: dict[str, Any], bio_data: dict[str, Any]
    ) -> dict[ContextLayer, dict[str, Any]]:
        """Process all context layers to extract features."""
        layer_features = {}

        for layer, processor in self.context_processors.items():
            layer_features[layer] = await processor(context, bio_data)

        return layer_features

    async def _process_environmental_context(self, context: dict[str, Any], bio_data: dict[str, Any]) -> dict[str, Any]:
        """Process environmental context layer."""
        features = {}

        # Time-based features
        now = datetime.now(timezone.utc)
        features["hour_of_day"] = now.hour
        features["day_of_week"] = now.weekday()
        features["is_weekend"] = now.weekday() >= 5

        # Environmental data (if available)
        if "environment" in context:
            env = context["environment"]
            features["temperature"] = env.get("temperature", 20)
            features["humidity"] = env.get("humidity", 50)
            features["light_level"] = env.get("light_level", 0.5)
            features["noise_level"] = env.get("noise_level", 0.3)

        # Season approximation
        month = now.month
        if month in [12, 1, 2]:
            features["season"] = "winter"
        elif month in [3, 4, 5]:
            features["season"] = "spring"
        elif month in [6, 7, 8]:
            features["season"] = "summer"
        else:
            features["season"] = "autumn"

        return features

    async def _process_personal_context(self, context: dict[str, Any], bio_data: dict[str, Any]) -> dict[str, Any]:
        """Process personal context layer."""
        features = {}

        # User profile features
        if "user_profile" in context:
            profile = context["user_profile"]
            features["age_group"] = profile.get("age_group", "adult")
            features["fitness_level"] = profile.get("fitness_level", "moderate")
            features["stress_tolerance"] = profile.get("stress_tolerance", 0.5)
            features["chronotype"] = profile.get("chronotype", "neutral")

        # Personal state
        if "personal_state" in context:
            state = context["personal_state"]
            features["mood"] = state.get("mood", "neutral")
            features["energy_perception"] = state.get("energy_perception", 0.5)
            features["focus_level"] = state.get("focus_level", 0.5)

        # Recent activities
        if "recent_activities" in context:
            activities = context["recent_activities"]
            features["physical_activity"] = activities.get("physical", 0)
            features["mental_activity"] = activities.get("mental", 0.5)
            features["social_activity"] = activities.get("social", 0.3)

        return features

    async def _process_social_context(self, context: dict[str, Any], bio_data: dict[str, Any]) -> dict[str, Any]:
        """Process social context layer."""
        features = {}

        # Social interaction features
        if "social" in context:
            social = context["social"]
            features["interaction_level"] = social.get("interaction_level", 0)
            features["social_stress"] = social.get("stress_level", 0)
            features["social_support"] = social.get("support_level", 0.5)
            features["crowd_density"] = social.get("crowd_density", 0)

        # Communication patterns
        if "communication" in context:
            comm = context["communication"]
            features["verbal_activity"] = comm.get("verbal", 0)
            features["digital_activity"] = comm.get("digital", 0.5)

        return features

    async def _process_quantum_context(self, context: dict[str, Any], bio_data: dict[str, Any]) -> dict[str, Any]:
        """Process quantum context layer."""
        features = {}

        # Quantum states
        if "quantum" in context:
            context["quantum"]
            features["coherence_level"] = qi.get("coherence", 0.5)
            features["entanglement_strength"] = qi.get("entanglement", 0)
            features["superposition_count"] = qi.get("superposition_count", 0)
            features["collapse_probability"] = qi.get("collapse_prob", 0.5)

        # Quantum field effects
        features["field_strength"] = context.get("qi_field_strength", 0.3)
        features["phase_alignment"] = context.get("phase_alignment", 0.5)

        return features

    async def _process_symbolic_context(self, context: dict[str, Any], bio_data: dict[str, Any]) -> dict[str, Any]:
        """Process symbolic context layer."""
        features = {}

        # Active GLYPHs and tags
        features["active_glyphs"] = list(self.active_glyphs.keys())
        features["glyph_count"] = len(self.active_glyphs)

        # Tag analysis
        if hasattr(self, "symbolic_carryover"):
            features["active_tags"] = list(self.symbolic_carryover.keys())
            features["tag_strength"] = (
                np.mean([tag[3] for tag in self.symbolic_carryover.values()]) if self.symbolic_carryover else 0
            )

        # Symbolic momentum
        features["symbolic_momentum"] = self.temporal_config["momentum"]

        # Colony state
        features["colony_health"] = 1.0  # Placeholder
        features["colony_consensus"] = 0.8  # Placeholder

        return features

    def _calculate_fuzzy_activations(
        self,
        bio_data: dict[str, Any],
        context_features: dict[ContextLayer, dict[str, Any]],
        thresholds: dict[str, Any],
    ) -> dict[str, float]:
        """Calculate fuzzy GLYPH activations based on bio data and context."""
        activations = {}

        # Energy-based GLYPHs
        if "energy_level" in bio_data or "atp_level" in bio_data:
            energy = bio_data.get("energy_level", bio_data.get("atp_level", 0.5))

            for glyph in [
                "ΛPOWER_ABUNDANT",
                "ΛPOWER_BALANCED",
                "ΛPOWER_CONSERVE",
                "ΛPOWER_CRITICAL",
            ]:
                if glyph in self.fuzzy_boundaries:
                    activation = self._fuzzy_membership(energy, self.fuzzy_boundaries[glyph])

                    # Modify based on context
                    activation = self._apply_context_modulation(activation, glyph, context_features)

                    if activation > 0.1:  # Threshold for consideration
                        activations[glyph] = activation

        # Stress-based GLYPHs
        if "cortisol" in bio_data or "stress" in bio_data:
            stress = bio_data.get("stress", bio_data.get("cortisol", 0.5) / 30)  # Normalize cortisol

            for glyph in [
                "ΛSTRESS_TRANSFORM",
                "ΛSTRESS_ADAPT",
                "ΛSTRESS_BUFFER",
                "ΛSTRESS_FLOW",
            ]:
                if glyph in self.fuzzy_boundaries:
                    activation = self._fuzzy_membership(stress, self.fuzzy_boundaries[glyph])

                    # Context modulation
                    activation = self._apply_context_modulation(activation, glyph, context_features)

                    if activation > 0.1:
                        activations[glyph] = activation

        # Homeostatic GLYPHs
        if "temperature" in bio_data and "ph" in bio_data:
            # Calculate homeostatic score
            temp_norm = (bio_data["temperature"] - 35) / 4  # Normalize to [0,1]
            ph_norm = (bio_data["ph"] - 7.0) / 0.8
            homeo_score = 1 - (abs(temp_norm - 0.5) + abs(ph_norm - 0.5)) / 2

            # Map to homeostatic GLYPHs
            if homeo_score > 0.8:
                activations["ΛHOMEO_PERFECT"] = homeo_score
            elif homeo_score > 0.6:
                activations["ΛHOMEO_BALANCED"] = homeo_score
            elif homeo_score > 0.4:
                activations["ΛHOMEO_ADJUSTING"] = 1 - homeo_score
            else:
                activations["ΛHOMEO_STRESSED"] = 1 - homeo_score

        # Rhythm GLYPHs based on heart rate
        if "heart_rate" in bio_data:
            hr = bio_data["heart_rate"]

            # Map HR to rhythm GLYPHs
            if 50 <= hr <= 65:
                activations["ΛRHYTHM_DEEP"] = 0.8
            elif 65 <= hr <= 85:
                activations["ΛRHYTHM_BALANCED"] = 0.9
            elif hr > 100:
                activations["ΛRHYTHM_ACTIVE"] = min(hr / 150, 1.0)

        return activations

    def _fuzzy_membership(self, value: float, params: dict[str, Any]) -> float:
        """Calculate fuzzy membership value."""
        if params["type"] == "gaussian":
            # Gaussian membership function
            center = params["center"]
            width = params["width"]
            return np.exp(-0.5 * ((value - center) / width) ** 2)

        elif params["type"] == "sigmoid":
            # Sigmoid membership function
            threshold = params["threshold"]
            slope = params["slope"]
            return 1 / (1 + np.exp(-slope * (value - threshold)))

        else:
            return 0.0

    def _apply_context_modulation(
        self,
        activation: float,
        glyph: str,
        context_features: dict[ContextLayer, dict[str, Any]],
    ) -> float:
        """Modulate GLYPH activation based on context."""
        modulated = activation

        # Environmental modulation
        env = context_features.get(ContextLayer.ENVIRONMENTAL, {})
        if "POWER" in glyph:
            # Energy GLYPHs affected by time of day
            hour = env.get("hour_of_day", 12)
            if 6 <= hour <= 10:  # Morning boost
                modulated *= 1.2
            elif 14 <= hour <= 16:  # Afternoon dip
                modulated *= 0.8
            elif hour >= 22 or hour <= 4:  # Night suppression
                modulated *= 0.6

        # Personal modulation
        personal = context_features.get(ContextLayer.PERSONAL, {})
        if "STRESS" in glyph:
            # Stress GLYPHs affected by stress tolerance
            tolerance = personal.get("stress_tolerance", 0.5)
            modulated *= 0.5 + tolerance

        # Quantum modulation
        context_features.get(ContextLayer.QUANTUM, {})
        coherence = qi.get("coherence_level", 0.5)
        if coherence > 0.8:
            # High coherence amplifies all activations
            modulated *= 1.3

        # Symbolic modulation
        symbolic = context_features.get(ContextLayer.SYMBOLIC, {})
        if glyph in symbolic.get("active_glyphs", []):
            # Already active GLYPHs have momentum
            modulated *= 1 + self.temporal_config["momentum"]

        return np.clip(modulated, 0, 1)

    def _apply_temporal_evolution(self, activations: dict[str, float]) -> dict[str, float]:
        """Apply temporal evolution to GLYPH activations."""
        evolved = {}

        for glyph, new_activation in activations.items():
            if glyph in self.active_glyphs:
                # Blend with previous activation (momentum)
                old_activation = self.active_glyphs[glyph]
                evolved_activation = (
                    self.temporal_config["momentum"] * old_activation
                    + (1 - self.temporal_config["momentum"]) * new_activation
                )
            else:
                # New GLYPH - apply evolution rate
                evolved_activation = new_activation * self.temporal_config["evolution_rate"]

            evolved[glyph] = evolved_activation

        # Decay inactive GLYPHs
        for glyph, old_activation in self.active_glyphs.items():
            if glyph not in evolved:
                decayed = old_activation * (1 - self.temporal_config["evolution_rate"])
                if decayed > 0.05:  # Keep if above threshold
                    evolved[glyph] = decayed

        return evolved

    async def _get_colony_consensus(
        self,
        glyphs: dict[str, float],
        context_features: dict[ContextLayer, dict[str, Any]],
    ) -> dict[str, float]:
        """Get colony consensus on GLYPH mappings."""
        # Check cache
        cache_key = f"{sorted(glyphs.items())}_{datetime.now(timezone.utc)}.minute}"
        if cache_key in self.consensus_cache:
            cached_time, cached_value = self.consensus_cache[cache_key]
            if datetime.now(timezone.utc) - cached_time < self.consensus_ttl:
                return cached_value

        # Simulate colony voting (in production, query other colonies)
        consensus = {}

        for glyph, activation in glyphs.items():
            # Simulate votes from different colony perspectives
            votes = []

            # Memory colony perspective
            memory_vote = activation * 0.9 if "MEMORY" in glyph else activation
            votes.append(memory_vote)

            # Reasoning colony perspective
            reasoning_vote = activation * 1.1 if "ADAPT" in glyph else activation
            votes.append(reasoning_vote)

            # Creative colony perspective
            creative_vote = activation * 1.2 if "TRANSFORM" in glyph else activation
            votes.append(creative_vote)

            # Consensus activation
            consensus[glyph] = np.mean(votes)

        # Cache result
        self.consensus_cache[cache_key] = (datetime.now(timezone.utc), consensus)

        return consensus

    def _process_quantum_superposition(
        self,
        glyphs: dict[str, float],
        context_features: dict[ContextLayer, dict[str, Any]],
    ) -> dict[str, float]:
        """Process quantum superposition of GLYPHs."""
        context_features.get(ContextLayer.QUANTUM, {})
        superposition_count = qi.get("superposition_count", 0)

        if superposition_count > 0:
            # Allow multiple GLYPHs to exist in superposition
            # Normalize probabilities
            total = sum(glyphs.values())
            if total > 0:
                return {glyph: prob / total for glyph, prob in glyphs.items()}

        return glyphs

    def _select_final_glyphs(self, glyphs: dict[str, float]) -> list[tuple[str, float]]:
        """Select final active GLYPHs."""
        # Sort by activation strength
        sorted_glyphs = sorted(glyphs.items(), key=lambda x: x[1], reverse=True)

        # Take top N
        max_glyphs = self.temporal_config["max_active_glyphs"]
        final = sorted_glyphs[:max_glyphs]

        # Update active GLYPHs
        self.active_glyphs = dict(final)

        return final

    def _calculate_mapping_confidence(
        self,
        glyphs: list[tuple[str, float]],
        context_features: dict[ContextLayer, dict[str, Any]],
    ) -> float:
        """Calculate confidence in the mapping."""
        if not glyphs:
            return 0.0

        confidence_factors = []

        # Factor 1: Activation strength of primary GLYPH
        primary_strength = glyphs[0][1] if glyphs else 0
        confidence_factors.append(primary_strength)

        # Factor 2: Clarity (difference between top 2 GLYPHs)
        if len(glyphs) >= 2:
            clarity = glyphs[0][1] - glyphs[1][1]
            confidence_factors.append(min(clarity * 2, 1.0))
        else:
            confidence_factors.append(1.0)

        # Factor 3: Context completeness
        context_completeness = (
            sum(len(features) for features in context_features.values()) / 50
        )  # Assume 50 total possible features
        confidence_factors.append(min(context_completeness, 1.0))

        # Factor 4: Quantum coherence
        context_features.get(ContextLayer.QUANTUM, {})
        coherence = qi.get("coherence_level", 0.5)
        confidence_factors.append(coherence)

        return np.mean(confidence_factors)

    def _summarize_context(self, context_features: dict[ContextLayer, dict[str, Any]]) -> dict[str, Any]:
        """Create summary of context features."""
        summary = {}

        for layer, features in context_features.items():
            # Extract key features for each layer
            if layer == ContextLayer.ENVIRONMENTAL:
                summary["environment"] = {
                    "time": features.get("hour_of_day"),
                    "season": features.get("season"),
                }
            elif layer == ContextLayer.PERSONAL:
                summary["personal"] = {
                    "mood": features.get("mood"),
                    "energy": features.get("energy_perception"),
                }
            elif layer == ContextLayer.QUANTUM:
                summary["quantum"] = {"coherence": features.get("coherence_level")}

        return summary

    def _update_glyph_history(self, glyphs: list[tuple[str, float]]):
        """Update GLYPH evolution history."""
        timestamp = datetime.now(timezone.utc)

        for glyph, activation in glyphs:
            self.glyph_evolution_history[glyph].append({"timestamp": timestamp, "activation": activation})

            # Keep only recent history (last 100 entries)
            if len(self.glyph_evolution_history[glyph]) > 100:
                self.glyph_evolution_history[glyph].pop(0)

    def _tag_mapping_quality(self, confidence: float):
        """Tag mapping quality based on confidence."""
        if confidence >= 0.8:
            tag = "ΛMAPPING_EXCELLENT"
            scope = TagScope.GLOBAL
        elif confidence >= 0.6:
            tag = "ΛMAPPING_GOOD"
            scope = TagScope.LOCAL
        else:
            tag = "ΛMAPPING_UNCERTAIN"
            scope = TagScope.LOCAL

        self.symbolic_carryover[tag] = (
            tag,
            scope,
            TagPermission.PUBLIC,
            confidence,
            300.0,  # 5 minute persistence
        )

    def _extract_temporal_features(self, context: dict[str, Any]) -> dict[str, float]:
        """Extract temporal context features."""
        now = datetime.now(timezone.utc)
        features = {
            "hour_sin": np.sin(2 * np.pi * now.hour / 24),
            "hour_cos": np.cos(2 * np.pi * now.hour / 24),
            "day_sin": np.sin(2 * np.pi * now.weekday() / 7),
            "day_cos": np.cos(2 * np.pi * now.weekday() / 7),
            "month_sin": np.sin(2 * np.pi * now.month / 12),
            "month_cos": np.cos(2 * np.pi * now.month / 12),
        }
        return features

    def _extract_environmental_features(self, context: dict[str, Any]) -> dict[str, float]:
        """Extract environmental features."""
        env = context.get("environment", {})
        return {
            "temperature_norm": (env.get("temperature", 20) - 10) / 30,
            "humidity_norm": env.get("humidity", 50) / 100,
            "light_norm": env.get("light_level", 0.5),
            "noise_norm": env.get("noise_level", 0.3),
        }

    def _extract_activity_features(self, context: dict[str, Any]) -> dict[str, float]:
        """Extract activity-related features."""
        activities = context.get("recent_activities", {})
        return {
            "physical_activity": activities.get("physical", 0),
            "mental_activity": activities.get("mental", 0.5),
            "social_activity": activities.get("social", 0.3),
            "rest_activity": activities.get("rest", 0.2),
        }

    def _extract_historical_features(self, context: dict[str, Any]) -> dict[str, float]:
        """Extract historical pattern features."""
        history = context.get("history", {})
        return {
            "avg_stress_24h": history.get("avg_stress_24h", 0.5),
            "avg_energy_24h": history.get("avg_energy_24h", 0.5),
            "sleep_quality_7d": history.get("sleep_quality_7d", 0.7),
            "coherence_trend": history.get("coherence_trend", 0),
        }

    def _extract_symbolic_features(self, context: dict[str, Any]) -> dict[str, float]:
        """Extract symbolic state features."""
        return {
            "active_glyph_count": len(self.active_glyphs),
            "glyph_stability": 1 - len(self.glyph_evolution_history) / 100,
            "tag_density": len(self.symbolic_carryover) / 10,
        }


# Colony instance factory


def create_mapping_colony(
    colony_id: Optional[str] = None,
) -> ContextualMappingColony:
    """Create a new contextual mapping colony instance."""
    return ContextualMappingColony(colony_id or "mapping_colony_default")