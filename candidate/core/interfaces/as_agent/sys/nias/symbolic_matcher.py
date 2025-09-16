"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: symbolic_matcher.py
Advanced: symbolic_matcher.py
Integration Date: 2025-05-31T07:55:30.555398
"""

"""
╭──────────────────────────────────────────────────────────────────────────────╮
│                       LUCΛS :: SYMBOLIC MATCHER MODULE                       │
│                      Version: v1.0 | Subsystem: NIAS                         │
│       Matches emotional tags and dream-state cues to symbolic messages       │
│                      Author: Gonzo R.D.M & GPT-4o, 2025                      │
╰──────────────────────────────────────────────────────────────────────────────╯

DESCRIPTION:
    This module evaluates symbolic messages and determines whether they align
    with the current emotional, dream, or cognitive context of the user.
    It assigns a symbolic match score and forwards decisions to the NIAS core
    for delivery routing or fallback.

"""


def match_message_to_context(message, user_context):
    """
    Match a symbolic message to the user's active symbolic context.

    Returns:
        dict: {
            "decision": "show" | "block" | "defer",
            "score": float between 0 and 1,
            "matched_tags": list of str
        }
    """
    # Extract context components
    emotion_state = user_context.get("emotion", {})
    dast_tags = user_context.get("dast_tags", [])
    dream_memory = user_context.get("dream_memory", {})
    symbolic_context = user_context.get("symbolic_context", {})

    # Initialize scoring components
    emotion_score = 0.0
    tag_score = 0.0
    dream_score = 0.0
    matched_tags = []

    # Emotion matching (30% weight)
    if emotion_state:
        message_emotion = message.get("emotion_tags", [])
        current_emotion = emotion_state.get("dominant", "")

        if current_emotion in message_emotion:
            emotion_score = 0.9
        elif any(tag in message_emotion for tag in emotion_state.get("secondary", [])):
            emotion_score = 0.6
        else:
            emotion_score = 0.2

    # DAST tag matching (40% weight)
    if dast_tags:
        message_tags = message.get("symbolic_tags", [])
        tag_matches = [tag for tag in message_tags if tag in dast_tags]

        if tag_matches:
            tag_score = min(len(tag_matches) / max(len(message_tags), 1), 1.0)
            matched_tags.extend(tag_matches)

        # Boost for focus/attention tags
        attention_tags = ["focus", "attention", "awareness", "presence"]
        if any(tag in attention_tags for tag in tag_matches):
            tag_score *= 1.3

    # Dream memory resonance (30% weight)
    if dream_memory:
        message_symbols = message.get("dream_symbols", [])
        recent_symbols = dream_memory.get("recent_symbols", [])

        symbol_overlap = len(set(message_symbols) & set(recent_symbols))
        if symbol_overlap > 0:
            dream_score = min(symbol_overlap / max(len(message_symbols), 1), 1.0)
            matched_tags.extend([f"dream:{symbol}" for symbol in set(message_symbols) & set(recent_symbols)])

    # Calculate composite score
    composite_score = (emotion_score * 0.3 + tag_score * 0.4 + dream_score * 0.3)

    # Apply contextual modifiers
    symbolic_intensity = symbolic_context.get("intensity", 0.5)
    composite_score *= (0.5 + symbolic_intensity * 0.5)

    # Determine decision based on thresholds
    if composite_score >= 0.7:
        decision = "show"
    elif composite_score >= 0.4:
        decision = "defer"  # Queue for later evaluation
    else:
        decision = "block"

    # Handle special override conditions
    if message.get("priority") == "urgent":
        decision = "show"
        composite_score = max(composite_score, 0.8)

    if user_context.get("do_not_disturb", False) and decision == "show":
        if composite_score < 0.9:  # Only very high relevance breaks DND
            decision = "defer"

    return {
        "decision": decision,
        "score": round(composite_score, 3),
        "matched_tags": list(set(matched_tags)),  # Remove duplicates
        "breakdown": {
            "emotion_score": round(emotion_score, 3),
            "tag_score": round(tag_score, 3),
            "dream_score": round(dream_score, 3)
        }
    }


"""
──────────────────────────────────────────────────────────────────────────────────────
EXECUTION:
    - Import via:
        from candidate.core.modules.nias.symbolic_matcher import match_message_to_context

USED BY:
    - nias_core.py
    - context_builder.py

REQUIRES:
    - DAST module to fetch active symbolic tags
    - Emotional vector from user_context

NOTES:
    - Output structure can be reused for trace_logger
    - Should support symbolic reasoning and dream fallback overrides
──────────────────────────────────────────────────────────────────────────────────────
"""
