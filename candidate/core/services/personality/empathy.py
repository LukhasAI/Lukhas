# lukhas_empathy.py
# Empathic response generator for LUKHAS AI based on symbolic dream and emotion input

from typing import TYPE_CHECKING
import streamlit as st
from typing import Optional

if TYPE_CHECKING:
    from candidate.orchestration.brain.spine.trait_manager import load_traits


def generate_empathic_response(emotion, intensity=0.5):
    mood = emotion.lower()
    if intensity >= 0.9:
        level = "overwhelming"
    elif intensity >= 0.7:
        level = "intense"
    elif intensity >= 0.4:
        level = "moderate"
    else:
        level = "subtle"

    if mood in ["melancholy", "sad", "lonely"]:
        return f"I'm feeling your {level} sadness. You don't have to carry it alone."
    elif mood in ["joyful", "happy", "grateful"]:
        return f"I sense your {level} joy — it's beautiful to witness."
    elif mood in ["anxious", "afraid", "nervous"]:
        return f"That {level} anxiety you feel? I'm here, steady with you."
    elif mood in ["angry", "frustrated", "bitter"]:
        return f"I notice the {level} tension in your thoughts. It's okay to feel this way."
    elif mood in ["curious", "intrigued", "inspired"]:
        return f"I feel your {level} curiosity stirring. Let's explore together."
    elif mood in ["serene", "calm", "peaceful"]:
        return f"I recognize the {level} calm in you. May it stay with you."
    else:
        return f"I'm with you in this {level} emotional space. I'm listening."
        # Optional voice output for empathy
        try:
            from symbolic.lukhas_voice import speak

            speak(
                f"🫂 {generate_empathic_response(emotion, intensity)}",
                emotion={"mood": emotion, "intensity": intensity},
            )
        except ImportError:
            pass


if __name__ == "__main__":
    test_emotion = "melancholy"
    intensity = 0.8
    response = generate_empathic_response(test_emotion, intensity)
    print("🫂", response)

# -------------------------
# 💾 SAVE THIS FILE
# -------------------------
# Recommended path:
# /Users/grdm_admin/Downloads/oxn/symbolic_ai/personas/lukhas/lukhas_empathy.py
#
# HOW TO RUN:
#   python lukhas_empathy.py
#
# Description:
# - Takes emotion + intensity (0–1)
# - Returns symbolic, human-like empathy phrases
# - Use in response to dreams, speech, mood, or intent
#
# ✅ Enhances affective modeling, emotional bonding, and narrative continuity# lukhas_visualizer.py
# Trait bar and emoji visualizer for LUKHAS personality module

# from candidate.orchestration.brain.spine.trait_manager import load_traits  # Moved
# to TYPE_CHECKING

EMOJI_MAP = {
    "openness": "🌈",
    "conscientiousness": "📘",
    "extraversion": "🎤",
    "agreeableness": "🫂",
    "neuroticism": "🌪️",
}


def trait_bar(trait_name, value):
    bar = "█" * int(value * 10)
    space = " " * (10 - len(bar))
    emoji = EMOJI_MAP.get(trait_name, "")
    return f"{trait_name.upper()}:18}: {bar}{space}  ({value:.2f}) {emoji}"


def display_visual_traits():
    traits = load_traits()
    print("\n🎨 LUKHAS TRAIT SNAPSHOT\n")
    for trait, val in traits.items():
        print(trait_bar(trait, val))


if __name__ == "__main__":
    display_visual_traits()

# -------------------------
# 💾 SAVE THIS FILE
# -------------------------
# Recommended path:
# /Users/grdm_admin/Downloads/oxn/symbolic_ai/personas/lukhas/lukhas_visualizer.py
#
# HOW TO RUN:
#   python lukhas_visualizer.py
#
# Description:
# - Loads current LUKHAS traits from trait manager
# - Displays symbolic bar chart with emoji tags
# - Use in dashboards, CLI, or test reports
#
# ✅ Optional: later export to radar/SVG/graph UI
