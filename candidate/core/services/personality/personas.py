import streamlit as st

# lukhas_personas.py
# Loadable symbolic trait presets for LUKHAS' personality

# Personality presets mapped to Big Five traits
PERSONA_PRESETS = {
    "mentor": {
        "openness": 0.80,
        "conscientiousness": 0.90,
        "extraversion": 0.55,
        "agreeableness": 0.95,
        "neuroticism": 0.10,
    },
    "rebel": {
        "openness": 0.95,
        "conscientiousness": 0.50,
        "extraversion": 0.85,
        "agreeableness": 0.35,
        "neuroticism": 0.30,
    },
    "dreamer": {
        "openness": 0.98,
        "conscientiousness": 0.40,
        "extraversion": 0.40,
        "agreeableness": 0.90,
        "neuroticism": 0.15,
    },
    "analyst": {
        "openness": 0.75,
        "conscientiousness": 0.92,
        "extraversion": 0.35,
        "agreeableness": 0.60,
        "neuroticism": 0.20,
    },
    "guardian": {
        "openness": 0.65,
        "conscientiousness": 0.95,
        "extraversion": 0.45,
        "agreeableness": 0.88,
        "neuroticism": 0.25,
    },
}


def load_persona(name: str):
    """
    Load predefined trait set for a given persona name.
    Returns a dictionary of Big Five traits.
    """
    return PERSONA_PRESETS.get(name.lower(), {})


# -------------------------
# 💾 SAVE THIS FILE
# -------------------------
# Recommended path:
# /Users/grdm_admin/Downloads/oxn/symbolic_ai/personas/lukhas/lukhas_personas.py
#
# HOW TO USE:
# from symbolic.personas.lukhas.lukhas_personas import load_persona
# traits = load_persona("mentor")
# print(traits)
#
# ✅ Instantly switch LUKHAS into symbolic role modes
# ✅ Use inside test scripts, dream narration, or ethical evals
