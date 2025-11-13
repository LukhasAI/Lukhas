"""Tag registry with hormone-emotion crosswalk."""
from typing import Dict, List

# Hormone to emotion mapping for explainability
HORMONE_EMOTION_CROSSWALK: Dict[str, List[str]] = {
    "cortisol": ["stressed", "anxious", "alert"],
    "beta_endorphin": ["relaxed", "pleased", "relieved"],
    "dopamine": ["motivated", "excited", "rewarded"],
    "serotonin": ["stable", "content", "balanced"],
    "oxytocin": ["connected", "trusting", "bonded"],
    "adrenaline": ["energized", "alert", "activated"],
}

# Reverse mapping: emotion to hormones
EMOTION_HORMONE_CROSSWALK: Dict[str, List[str]] = {}
for hormone, emotions in HORMONE_EMOTION_CROSSWALK.items():
    for emotion in emotions:
        if emotion not in EMOTION_HORMONE_CROSSWALK:
            EMOTION_HORMONE_CROSSWALK[emotion] = []
        EMOTION_HORMONE_CROSSWALK[emotion].append(hormone)


def hormone_to_emotions(hormone: str) -> List[str]:
    """Get emotions associated with a hormone."""
    return HORMONE_EMOTION_CROSSWALK.get(hormone.lower(), [])


def emotion_to_hormones(emotion: str) -> List[str]:
    """Get hormones associated with an emotion."""
    return EMOTION_HORMONE_CROSSWALK.get(emotion.lower(), [])


if __name__ == "__main__":
    print("=== Hormone↔Emotion Crosswalk Demo ===\n")

    print("Hormone → Emotions:")
    for hormone in ["cortisol", "dopamine", "serotonin"]:
        emotions = hormone_to_emotions(hormone)
        print(f"  {hormone}: {', '.join(emotions)}")

    print("\nEmotion → Hormones:")
    for emotion in ["stressed", "motivated", "relaxed"]:
        hormones = emotion_to_hormones(emotion)
        print(f"  {emotion}: {', '.join(hormones)}")
