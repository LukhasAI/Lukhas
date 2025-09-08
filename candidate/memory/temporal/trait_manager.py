"""

#TAG:memory
#TAG:temporal
#TAG:neuroplastic
#TAG:colony


Enhanced Core TypeScript - Integrated from Advanced Systems
Original: trait_manager_2.py
Advanced: trait_manager_2.py
Integration Date: 2025-05-31T07:55:28.113331
"""

# trait_manager.py
# Dynamic Big Five Personality Trait Engine for LUKHAS

import json
import os
from datetime import datetime, timezone

TRAIT_FILE = "logs/lukhas_traits.json"


def default_traits():
    return {
        "openness": 0.87,
        "conscientiousness": 0.76,
        "extraversion": 0.60,
        "agreeableness": 0.91,
        "neuroticism": 0.18,
    }


def load_traits():
    if not os.path.exists(TRAIT_FILE):
        return default_traits()
    with open(TRAIT_FILE) as f:
        return json.load(f)


def save_traits(traits):
    with open(TRAIT_FILE, "w") as f:
        json.dump(traits, f, indent=2)


def reset_traits():
    save_traits(default_traits())
    print("🔄 LUKHAS traits reset to default.")


def decay_traits(traits, baseline=None, rate=0.01):
    if baseline is None:
        baseline = default_traits()
    for trait in traits:
        traits[trait] += (baseline[trait] - traits[trait]) * rate
    return traits


def adjust_traits_from_context(traits, context):
    context = context.lower()
    if "betray" in context or "guilt" in context:
        traits["agreeableness"] += 0.02
        traits["conscientiousness"] += 0.01
    if "dream" in context or "imagine" in context:
        traits["openness"] += 0.03
    if "tired" in context:
        traits["extraversion"] -= 0.02
        traits["neuroticism"] += 0.01
    if "love" in context or "thank you" in context:
        traits["agreeableness"] += 0.02
    traits = {k: min(1.0, max(0.0, round(v, 4))) for k, v in traits.items()}
    return traits


def log_trait_shift(input_text, new_traits):
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        "input": input_text,
        "traits": new_traits,
    }
    log_file = "logs/lukhas_trait_history.json"
    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")


def process_traits(input_text):
    traits = load_traits()
    traits = decay_traits(traits)
    updated = adjust_traits_from_context(traits, input_text)
    save_traits(updated)
    log_trait_shift(input_text, updated)
    return updated


def emoji_trait_bar(traits):
    bar = "\n🧬 LUKHAS PERSONALITY TRAIT BAR\n"
    for trait, val in traits.items():
        emoji = "⭐" * int(val * 10)
        bar += f"{trait[:4].capitalize()}: {emoji}\n"
    return bar
