"""
LUKHAS AI Bio-Consciousness Integration Module
Connects bio-symbolic processing with consciousness systems.
"""

import logging
from enum import Enum
from typing import Any, Dict

# Assuming SymbolicGlyph is available from the bio module.
# A real implementation might need to handle circular dependencies carefully.
from lukhas.bio.core.bio_symbolic import SymbolicGlyph

logger = logging.getLogger(__name__)


class BioAwareConsciousnessState(Enum):
    """Represents consciousness states that are aware of bio-signals."""
    CALM_FOCUS = "CALM_FOCUS"
    ENERGETIC_ENGAGEMENT = "ENERGETIC_ENGAGEMENT"
    RESTORATIVE_INTEGRATION = "RESTORATIVE_INTEGRATION"
    CREATIVE_EXPLORATION = "CREATIVE_EXPLORATION"
    STRESSED_ADAPTATION = "STRESSED_ADAPTATION"


# Mapping from bio-symbolic glyphs to consciousness layers/states
# This is a simplified data structure for the integration design.
BIO_CONSCIOUSNESS_MAP: Dict[SymbolicGlyph, BioAwareConsciousnessState] = {
    # Rhythm
    SymbolicGlyph.CIRCADIAN: BioAwareConsciousnessState.RESTORATIVE_INTEGRATION,
    SymbolicGlyph.ULTRADIAN: BioAwareConsciousnessState.CALM_FOCUS,
    SymbolicGlyph.VITAL: BioAwareConsciousnessState.ENERGETIC_ENGAGEMENT,
    SymbolicGlyph.NEURAL: BioAwareConsciousnessState.CREATIVE_EXPLORATION,

    # Energy
    SymbolicGlyph.POWER_ABUNDANT: BioAwareConsciousnessState.ENERGETIC_ENGAGEMENT,
    SymbolicGlyph.POWER_BALANCED: BioAwareConsciousnessState.CALM_FOCUS,
    SymbolicGlyph.POWER_CONSERVE: BioAwareConsciousnessState.RESTORATIVE_INTEGRATION,
    SymbolicGlyph.POWER_CRITICAL: BioAwareConsciousnessState.STRESSED_ADAPTATION,

    # Stress
    SymbolicGlyph.STRESS_TRANSFORM: BioAwareConsciousnessState.CREATIVE_EXPLORATION,
    SymbolicGlyph.STRESS_ADAPT: BioAwareConsciousnessState.STRESSED_ADAPTATION,
    SymbolicGlyph.STRESS_BUFFER: BioAwareConsciousnessState.CALM_FOCUS,
    SymbolicGlyph.STRESS_FLOW: BioAwareConsciousnessState.ENERGETIC_ENGAGEMENT,

    # Dream
    SymbolicGlyph.DREAM_EXPLORE: BioAwareConsciousnessState.CREATIVE_EXPLORATION,
    SymbolicGlyph.DREAM_INTEGRATE: BioAwareConsciousnessState.RESTORATIVE_INTEGRATION,
    SymbolicGlyph.DREAM_PROCESS: BioAwareConsciousnessState.CALM_FOCUS,

    # Homeostasis
    SymbolicGlyph.HOMEO_PERFECT: BioAwareConsciousnessState.CALM_FOCUS,
    SymbolicGlyph.HOMEO_BALANCED: BioAwareConsciousnessState.CALM_FOCUS,
    SymbolicGlyph.HOMEO_ADJUSTING: BioAwareConsciousnessState.STRESSED_ADAPTATION,
    SymbolicGlyph.HOMEO_STRESSED: BioAwareConsciousnessState.STRESSED_ADAPTATION,
}


def bio_feedback_loop(bio_symbolic_result: Dict[str, Any]):
    """
    A basic bio-feedback mechanism.

    This function takes the result from the bio-symbolic orchestrator
    and can trigger actions in the consciousness system.
    """
    dominant_glyph_str = bio_symbolic_result.get("dominant_glyph")
    if dominant_glyph_str:
        try:
            dominant_glyph = SymbolicGlyph(dominant_glyph_str)
            target_state = BIO_CONSCIOUSNESS_MAP.get(dominant_glyph)
            if target_state:
                logger.info(
                    f"Bio-feedback: Dominant glyph {dominant_glyph.name} suggests "
                    f"transition to consciousness state: {target_state.name}"
                )
            else:
                logger.warning(f"Bio-feedback: No consciousness state mapping for glyph {dominant_glyph.name}")
        except ValueError:
            logger.error(f"Bio-feedback: Unknown glyph value '{dominant_glyph_str}'")

__all__ = ["BioAwareConsciousnessState", "BIO_CONSCIOUSNESS_MAP", "bio_feedback_loop"]
