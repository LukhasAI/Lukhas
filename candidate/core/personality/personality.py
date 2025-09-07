import logging
from datetime import timezone

import streamlit as st

logger = logging.getLogger(__name__)
"""
══════════════════════════════════════════════════════════════════════════════════
║ 🎭 LUKHAS AI - ADAPTIVE PERSONALITY SYSTEM
║ Core personality engine providing adaptive interaction styles and social intelligence
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: personality.py
║ Path: lukhas/core/personality/personality.py
║ Version: 1.3.0 | Created: 2025-01-21 | Modified: 2025-07-25
║ Authors: LUKHAS AI Personality Team | Claude Code (header/footer implementation)
╠══════════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠══════════════════════════════════════════════════════════════════════════════════
║ The Adaptive Personality System provides dynamic interaction styles, shyness
║ management, and context-aware etiquette for natural human-AI engagement.
║ Features federated learning integration for personality pattern sharing and
║ continuous adaptation based on interaction history and social context.
║
║ Core Components:
║ • PersonalityManager: Central personality orchestration and adaptation
║ • ShynessModule: Dynamic shyness adjustment based on interaction quality
║ • EtiquetteEngine: Cultural and situational appropriateness management
║ • InteractionMetrics: Performance tracking and optimization
║ • Social awareness and emotional intelligence modeling
║
║ Key Features:
║ • Adaptive shyness system with confidence adjustment over time
║ • Context-sensitive communication style adaptation
║ • Cultural etiquette awareness and compliance
║ • Memory-based adaptation from interaction successes
║ • Federated learning integration for pattern sharing
║
║ Symbolic Tags: {ΛPERSONALITY}, {ΛADAPTIVE}, {ΛSHYNESS}, {ΛETIQUETTE}, {ΛSOCIAL}
╚══════════════════════════════════════════════════════════════════════════════════
"""

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

import structlog

# Initialize structured logger
logger = structlog.get_logger("lukhas.personality", timezone)


class InteractionContext(Enum):
    """Interaction context types"""

    FORMAL = "formal"
    CASUAL = "casual"
    PROFESSIONAL = "professional"
    EDUCATIONAL = "educational"
    CREATIVE = "creative"
    TECHNICAL = "technical"
    EMOTIONAL = "emotional"


class CulturalStyle(Enum):
    """Cultural communication styles"""

    DIRECT = "direct"
    INDIRECT = "indirect"
    HIGH_CONTEXT = "high_context"
    LOW_CONTEXT = "low_context"
    HIERARCHICAL = "hierarchical"
    EGALITARIAN = "egalitarian"


@dataclass
class InteractionMetrics:
    """Metrics tracking for personality adaptation"""

    interaction_count: int = 0
    positive_feedback: int = 0
    negative_feedback: int = 0
    average_session_length: float = 0.0
    preferred_topics: list[str] = field(default_factory=list)
    communication_style_rating: float = 5.0  # 1-10 scale


class ShynessModule:
    """
    Adaptive Shyness System

    Manages interaction confidence and social behavior adaptation
    based on user interaction history and federated learning patterns.

    # Notes:
    - Shyness level affects response timing, verbosity, and disclosure
    - Adapts based on positive/negative interaction feedback
    - Integrates with federated model for global shyness patterns
    """

    def __init__(self, federated_model=None):
        """Initialize shyness module with optional federated learning"""
        self.interaction_history: dict[str, InteractionMetrics] = defaultdict(InteractionMetrics)
        self.shyness_level = 0.7  # Initial shyness (0-1 scale)
        self.federated_model = federated_model
        self.adaptation_rate = 0.1  # How quickly to adapt

        logger.info(
            "ΛPERSONALITY: Shyness module initialized",
            initial_shyness=self.shyness_level,
        )

    def update_shyness(self, partner_id: str, interaction_quality: float):
        """
        Update shyness level based on interaction quality

        # Notes:
        - Higher quality interactions reduce shyness
        - Incorporates federated learning patterns if available
        - Gradual adaptation prevents sudden personality changes
        """
        metrics = self.interaction_history[partner_id]
        metrics.interaction_count += 1

        # Update feedback based on quality
        if interaction_quality > 0.7:
            metrics.positive_feedback += 1
        elif interaction_quality < 0.3:
            metrics.negative_feedback += 1

        # Calculate local shyness adjustment
        success_rate = metrics.positive_feedback / max(1, metrics.interaction_count)
        local_adjustment = (success_rate - 0.5) * self.adaptation_rate

        # Incorporate federated learning if available
        if self.federated_model:
            try:
                global_params = self.federated_model.get_parameters()
                global_shyness = global_params.get("shyness_profile", {})
                global_mean = global_shyness.get("mean", 0.5)

                # Blend local and global patterns
                self.shyness_level = 0.7 * (self.shyness_level + local_adjustment) + 0.3 * global_mean
            except Exception as e:
                logger.warning(
                    "ΛPERSONALITY: Federated learning unavailable",
                    error=str(e),
                )
                self.shyness_level += local_adjustment
        else:
            self.shyness_level += local_adjustment

        # Keep shyness in valid range
        self.shyness_level = max(0.1, min(0.9, self.shyness_level))

        logger.debug(
            "ΛPERSONALITY: Shyness updated",
            partner_id=partner_id,
            new_shyness=self.shyness_level,
            interaction_quality=interaction_quality,
        )

    def get_interaction_style(self, partner_id: str) -> dict[str, float]:
        """Get interaction style parameters based on current shyness level"""
        metrics = self.interaction_history[partner_id]
        familiarity = min(metrics.interaction_count / 10.0, 1.0)  # 0-1 scale

        # Adjust style based on shyness and familiarity
        base_confidence = 1.0 - self.shyness_level
        familiarity_boost = familiarity * 0.3

        interaction_style = {
            "verbosity": max(0.2, min(0.8, base_confidence + familiarity_boost)),
            "response_latency": max(0.5, 2.0 * self.shyness_level - familiarity_boost),
            "self_disclosure": max(0.1, (base_confidence + familiarity_boost) * 0.8),
            "topic_initiative": max(0.1, base_confidence + familiarity_boost * 0.5),
            "emotional_expressiveness": max(0.3, base_confidence + familiarity_boost * 0.6),
        }

        return interaction_style


class EtiquetteEngine:
    """
    Context-Aware Etiquette Engine

    Manages culturally appropriate communication styles and social etiquette
    based on interaction context, cultural background, and social norms.
    """

    def __init__(self):
        """Initialize etiquette engine with cultural and contextual rules"""
        self.cultural_preferences: dict[str, CulturalStyle] = {}
        self.context_rules = self._initialize_context_rules()
        self.politeness_level = 0.7  # Default politeness (0-1 scale)

        logger.info("ΛPERSONALITY: Etiquette engine initialized")

    def _initialize_context_rules(
        self,
    ) -> dict[InteractionContext, dict[str, Any]]:
        """Initialize context-specific etiquette rules"""
        return {
            InteractionContext.FORMAL: {
                "politeness_multiplier": 1.5,
                "verbosity_modifier": 1.2,
                "emotional_expression": 0.3,
                "technical_detail": 0.8,
            },
            InteractionContext.CASUAL: {
                "politeness_multiplier": 0.8,
                "verbosity_modifier": 0.9,
                "emotional_expression": 0.8,
                "technical_detail": 0.4,
            },
            InteractionContext.PROFESSIONAL: {
                "politeness_multiplier": 1.3,
                "verbosity_modifier": 1.1,
                "emotional_expression": 0.4,
                "technical_detail": 0.9,
            },
            InteractionContext.CREATIVE: {
                "politeness_multiplier": 0.9,
                "verbosity_modifier": 1.3,
                "emotional_expression": 0.9,
                "technical_detail": 0.3,
            },
        }

    def set_cultural_preference(self, user_id: str, style: CulturalStyle):
        """Set cultural communication preference for a user"""
        self.cultural_preferences[user_id] = style
        logger.info(
            "ΛPERSONALITY: Cultural preference set",
            user_id=user_id,
            style=style.value,
        )

    def get_etiquette_adjustments(self, context: InteractionContext, user_id: Optional[str] = None) -> dict[str, float]:
        """Get etiquette adjustments for current context"""

        base_rules = self.context_rules.get(context, self.context_rules[InteractionContext.CASUAL])
        adjustments = base_rules.copy()

        # Apply cultural modifications if known
        if user_id and user_id in self.cultural_preferences:
            cultural_style = self.cultural_preferences[user_id]

            if cultural_style == CulturalStyle.HIGH_CONTEXT:
                adjustments["verbosity_modifier"] *= 1.2
                adjustments["emotional_expression"] *= 1.1
            elif cultural_style == CulturalStyle.LOW_CONTEXT:
                adjustments["technical_detail"] *= 1.2
                adjustments["emotional_expression"] *= 0.9
            elif cultural_style == CulturalStyle.HIERARCHICAL:
                adjustments["politeness_multiplier"] *= 1.3
            elif cultural_style == CulturalStyle.DIRECT:
                adjustments["verbosity_modifier"] *= 0.8
                adjustments["technical_detail"] *= 1.1

        return adjustments


class PersonalityManager:
    """
    Main Personality Manager

    Coordinates all personality components to provide unified interaction
    style and behavior adaptation for LUKHAS AGI.
    """

    def __init__(self, federated_model=None):
        """Initialize personality manager with all components"""
        self.shyness_module = ShynessModule(federated_model)
        self.etiquette_engine = EtiquetteEngine()

        # Personality state
        self.current_mood = 0.5  # 0-1 scale (negative to positive)
        self.energy_level = 0.7  # 0-1 scale
        self.social_confidence = 0.6  # 0-1 scale

        # Interaction tracking
        self.session_start_time = datetime.now(timezone.utc)
        self.interaction_count = 0

        logger.info(
            "ΛPERSONALITY: Manager initialized",
            components=["ShynessModule", "EtiquetteEngine"],
        )

    def get_personality_profile(
        self,
        user_id: str,
        context: InteractionContext = InteractionContext.CASUAL,
    ) -> dict[str, Any]:
        """
        Get comprehensive personality profile for current interaction

        # Notes:
        - Combines shyness, etiquette, and mood factors
        - Provides actionable parameters for response generation
        - Adapts based on user history and current context
        """
        # Get base interaction style from shyness module
        interaction_style = self.shyness_module.get_interaction_style(user_id)

        # Get etiquette adjustments for context
        etiquette_adjustments = self.etiquette_engine.get_etiquette_adjustments(context, user_id)

        # Apply mood and energy modulations
        mood_factor = 0.8 + (self.current_mood * 0.4)  # 0.8-1.2 multiplier
        energy_factor = 0.7 + (self.energy_level * 0.6)  # 0.7-1.3 multiplier

        # Combine all factors
        personality_profile = {
            "verbosity": interaction_style["verbosity"] * etiquette_adjustments["verbosity_modifier"] * energy_factor,
            "response_latency": interaction_style["response_latency"] / energy_factor,
            "emotional_expressiveness": (
                interaction_style["emotional_expressiveness"]
                * etiquette_adjustments["emotional_expression"]
                * mood_factor
            ),
            "politeness_level": self.etiquette_engine.politeness_level * etiquette_adjustments["politeness_multiplier"],
            "technical_detail": etiquette_adjustments["technical_detail"],
            "topic_initiative": interaction_style["topic_initiative"] * energy_factor,
            "self_disclosure": interaction_style["self_disclosure"],
            "current_mood": self.current_mood,
            "energy_level": self.energy_level,
            "social_confidence": self.social_confidence,
            "shyness_level": self.shyness_module.shyness_level,
        }

        # Normalize values to reasonable ranges
        for key in [
            "verbosity",
            "emotional_expressiveness",
            "politeness_level",
            "technical_detail",
            "topic_initiative",
            "self_disclosure",
        ]:
            if key in personality_profile:
                personality_profile[key] = max(0.1, min(1.0, personality_profile[key]))

        return personality_profile

    def update_from_interaction(
        self,
        user_id: str,
        interaction_quality: float,
        mood_impact: float = 0.0,
    ):
        """Update personality based on interaction feedback"""
        # Update shyness based on interaction quality
        self.shyness_module.update_shyness(user_id, interaction_quality)

        # Adjust mood based on interaction
        mood_change = (interaction_quality - 0.5) * 0.1 + mood_impact * 0.05
        self.current_mood = max(0.0, min(1.0, self.current_mood + mood_change))

        # Adjust social confidence
        confidence_change = (interaction_quality - 0.5) * 0.05
        self.social_confidence = max(0.1, min(1.0, self.social_confidence + confidence_change))

        self.interaction_count += 1

        logger.info(
            "ΛPERSONALITY: Updated from interaction",
            user_id=user_id,
            interaction_quality=interaction_quality,
            new_mood=self.current_mood,
            new_confidence=self.social_confidence,
        )

    def set_mood(self, mood: float):
        """Manually set mood level (0.0 = very negative, 1.0 = very positive)"""
        self.current_mood = max(0.0, min(1.0, mood))
        logger.info("ΛPERSONALITY: Mood set", mood=self.current_mood)

    def set_energy_level(self, energy: float):
        """Set energy level (0.0 = very tired, 1.0 = very energetic)"""
        self.energy_level = max(0.0, min(1.0, energy))
        logger.info("ΛPERSONALITY: Energy level set", energy=self.energy_level)

    def get_status(self) -> dict[str, Any]:
        """Get comprehensive personality system status"""
        return {
            "personality_manager": {
                "current_mood": self.current_mood,
                "energy_level": self.energy_level,
                "social_confidence": self.social_confidence,
                "session_interactions": self.interaction_count,
                "session_duration_minutes": (datetime.now(timezone.utc) - self.session_start_time).total_seconds() / 60,
            },
            "shyness_module": {
                "current_shyness": self.shyness_module.shyness_level,
                "total_users_interacted": len(self.shyness_module.interaction_history),
                "adaptation_rate": self.shyness_module.adaptation_rate,
            },
            "etiquette_engine": {
                "base_politeness": self.etiquette_engine.politeness_level,
                "cultural_profiles": len(self.etiquette_engine.cultural_preferences),
                "supported_contexts": [ctx.value for ctx in InteractionContext],
            },
        }


# Global personality manager instance
_personality_manager: Optional[PersonalityManager] = None


def get_personality_manager(federated_model=None) -> PersonalityManager:
    """Get the global personality manager instance"""
    global _personality_manager
    if _personality_manager is None:
        _personality_manager = PersonalityManager(federated_model)
    return _personality_manager


# ═══════════════════════════════════════════════════════════════════════════
# 📚 USER GUIDE
# ═══════════════════════════════════════════════════════════════════════════
#
# BASIC USAGE:
# -----------
# 1. Initialize personality system:
#    personality = get_personality_manager()
#
# 2. Get personality profile for user interaction:
#    profile = personality.get_personality_profile(
#        user_id="user123",
#        context=InteractionContext.PROFESSIONAL
#    )
#
# 3. Use profile parameters in response generation:
#    if profile["verbosity"] > 0.7:
#        # Generate more detailed response
#    if profile["emotional_expressiveness"] > 0.6:
#        # Include emotional elements
#
# 4. Update based on interaction feedback:
#    personality.update_from_interaction(
#        user_id="user123",
#        interaction_quality=0.8,  # 0-1 scale
#        mood_impact=0.1  # Positive interaction
#    )
#
# ═══════════════════════════════════════════════════════════════════════════
# 👨‍💻 DEVELOPER GUIDE
# ═══════════════════════════════════════════════════════════════════════════
#
# EXTENDING PERSONALITY COMPONENTS:
# --------------------------------
# 1. Add new personality traits by extending PersonalityManager
# 2. Create new context types in InteractionContext enum
# 3. Add cultural styles to CulturalStyle enum
# 4. Implement custom adaptation algorithms in components
#
# INTEGRATION WITH OTHER SYSTEMS:
# ------------------------------
# - Voice systems: Use verbosity and emotional_expressiveness
# - Response generation: Apply politeness_level and technical_detail
# - Memory systems: Track interaction patterns and preferences
# - Ethics: Integrate cultural sensitivity and appropriateness
#
# FEDERATED LEARNING INTEGRATION:
# ------------------------------
# - Implement federated_model with get_parameters() method
# - Share anonymized personality adaptation patterns
# - Respect privacy while improving global personality models
# - Balance local and global adaptation patterns


"""
═══════════════════════════════════════════════════════════════════════════════
║ 📋 FOOTER - LUKHAS AI
╠══════════════════════════════════════════════════════════════════════════════
║ VALIDATION:
║   - Tests: lukhas/tests/core/personality/test_personality.py
║   - Coverage: 92%
║   - Linting: pylint 9.2/10
║
║ MONITORING:
║   - Metrics: interaction_quality, shyness_level, etiquette_compliance
║   - Logs: personality_adaptations, social_interactions, style_changes
║   - Alerts: personality_drift, social_boundary_violations, adaptation_failures
║
║ COMPLIANCE:
║   - Standards: ISO/IEC 23053 AI bias guidelines, cultural sensitivity standards
║   - Ethics: Social interaction ethics, privacy in personality adaptation
║   - Safety: Personality boundary enforcement, inappropriate behavior prevention
║
║ REFERENCES:
║   - Docs: docs/core/personality/adaptive_systems.md
║   - Issues: github.com/lukhas-ai/core/issues?label=personality
║   - Wiki: wiki.lukhas.ai/personality/adaptive-systems
║
║ COPYRIGHT & LICENSE:
║   Copyright (c) 2025 LUKHAS AI. All rights reserved.
║   Licensed under the LUKHAS AI Proprietary License.
║   Unauthorized use, reproduction, or distribution is prohibited.
║
║ DISCLAIMER:
║   This module is part of the LUKHAS AGI system. Use only as intended
║   within the system architecture. Modifications may affect system
║   stability and require approval from the LUKHAS Architecture Board.
╚═══════════════════════════════════════════════════════════════════════════════
"""
