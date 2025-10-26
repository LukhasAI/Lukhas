from enum import Enum


class BioAwareConsciousnessState(Enum):
    STRESSED_ADAPTATION = "stressed_adaptation"
    CREATIVE_EXPLORATION = "creative_exploration"
    RESTORATIVE_INTEGRATION = "restorative_integration"


BIO_CONSCIOUSNESS_MAP = {
    "power_critical": BioAwareConsciousnessState.STRESSED_ADAPTATION,
    "dream_explore": BioAwareConsciousnessState.CREATIVE_EXPLORATION,
    "circadian": BioAwareConsciousnessState.RESTORATIVE_INTEGRATION,
}
