"""

#TAG:qim
#TAG:entanglement
#TAG:neuroplastic
#TAG:colony


Bio Affect Model
================

Provides simple emotional repair utilities for dream synthesis.
"""
import streamlit as st

from consciousness.qi import qi

# ΛTAG: emotional_repair_model
SADNESS_THRESHOLD = 0.6


def inject_narrative_repair(narrative: str, emotions: dict[str, float], *, threshold: float = SADNESS_THRESHOLD) -> str:
    """Inject narrative repair elements if sadness exceeds threshold."""
    sadness = emotions.get("sadness", 0.0)
    if sadness > threshold:
        # Basic narrative repair wording
        repair_phrase = " A healing warmth resolves lingering sorrow."
        return narrative + repair_phrase
    return narrative
