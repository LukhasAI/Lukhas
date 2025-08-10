"""
LUKHAS Emotion Vocabulary
=========================

Symbolic vocabulary for emotional states and transitions.

Created: 2025-07-27
Author: Jules
Status: DRAFT
"""

EMOTION_VOCABULARY = {
    "joy": {
        "emoji": "😊",
        "symbol": "JOY◊",
        "meaning": "A positive emotional state characterized by feelings of happiness,
        pleasure, and contentment.",
        "resonance": "positive",
        "guardian_weight": 0.1,
        "contexts": ["happiness", "pleasure", "contentment"],
    },
    "sadness": {
        "emoji": "😢",
        "symbol": "SAD◊",
        "meaning": "A negative emotional state characterized by feelings of sorrow,
        loss, and unhappiness.",
        "resonance": "negative",
        "guardian_weight": 0.4,
        "contexts": ["sorrow", "loss", "unhappiness"],
    },
    "anger": {
        "emoji": "😠",
        "symbol": "ANGER◊",
        "meaning": "A strong feeling of annoyance, displeasure, or hostility.",
        "resonance": "negative",
        "guardian_weight": 0.7,
        "contexts": ["annoyance", "displeasure", "hostility"],
    },
    "fear": {
        "emoji": "😨",
        "symbol": "FEAR◊",
        "meaning": "An unpleasant emotion caused by the belief that someone or something is dangerous, likely to cause pain, or a threat.",
        "resonance": "negative",
        "guardian_weight": 0.6,
        "contexts": ["danger", "pain", "threat"],
    },
}


def get_emotion_symbol(emotion: str) -> str:
    """Get emoji symbol for an emotion."""
    return EMOTION_VOCABULARY.get(emotion, {}).get("emoji", "❓")


def get_guardian_weight(emotion: str) -> float:
    """Get guardian weight for an emotion."""
    return EMOTION_VOCABULARY.get(emotion, {}).get("guardian_weight", 0.5)


if __name__ == "__main__":
    print(f"Joy: {get_emotion_symbol('joy')}")
    print(f"Sadness: {get_emotion_symbol('sadness')}")
    print(f"Anger: {get_emotion_symbol('anger')}")
    print(f"Fear: {get_emotion_symbol('fear')}")
    print(f"Guardian weight of anger: {get_guardian_weight('anger')}")
