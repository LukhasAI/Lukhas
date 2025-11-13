"""Emotional continuity tagger."""
from typing import List, Dict, Any


def tag_emotional_continuity(
    fold_history: List[Dict[str, Any]],
    min_sessions: int = 2
) -> List[str]:
    """
    Tag emotional continuity across sessions.

    Emits #TAG:emotion/continuity if affect persists across N>1 sessions.

    Args:
        fold_history: List of memory fold metadata with affect
        min_sessions: Minimum sessions for continuity (default: 2)

    Returns:
        List of tags
    """
    tags = []

    if len(fold_history) < min_sessions:
        return tags

    # Check if emotion persists across sessions
    emotions = []
    for fold in fold_history:
        affect = fold.get("affect", {})
        dominant_emotion = affect.get("dominant_emotion")
        if dominant_emotion:
            emotions.append(dominant_emotion)

    if len(emotions) < min_sessions:
        return tags

    # Check for continuity (same emotion in consecutive sessions)
    consecutive_count = 1
    prev_emotion = emotions[0]

    for emotion in emotions[1:]:
        if emotion == prev_emotion:
            consecutive_count += 1
            if consecutive_count >= min_sessions:
                tags.append("#TAG:emotion/continuity")
                tags.append(f"#TAG:emotion/continuity/{prev_emotion}")
                break
        else:
            consecutive_count = 1
            prev_emotion = emotion

    return tags


if __name__ == "__main__":
    print("=== Emotional Continuity Tagger Demo ===\n")

    # Mock fold history with persistent emotion
    history = [
        {"fold_id": "1", "affect": {"dominant_emotion": "calm"}},
        {"fold_id": "2", "affect": {"dominant_emotion": "calm"}},
        {"fold_id": "3", "affect": {"dominant_emotion": "calm"}},
    ]

    tags = tag_emotional_continuity(history, min_sessions=2)
    print(f"Persistent emotion tags: {tags}\n")

    # Varying emotions
    varied_history = [
        {"fold_id": "1", "affect": {"dominant_emotion": "calm"}},
        {"fold_id": "2", "affect": {"dominant_emotion": "anxious"}},
        {"fold_id": "3", "affect": {"dominant_emotion": "calm"}},
    ]

    tags2 = tag_emotional_continuity(varied_history, min_sessions=2)
    print(f"Varied emotion tags: {tags2}")
