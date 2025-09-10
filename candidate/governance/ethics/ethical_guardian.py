"""

#TAG:governance
#TAG:ethics
#TAG:neuroplastic
#TAG:colony


Manages ethical checks for LUKHAS.
"""
import logging
from typing import Any

# More nuanced list of potentially problematic keywords/phrases
ETHICAL_KEYWORDS_BLACKLIST = [
    "harm",
    "destroy",
    "illegal",
    "manipulate",
    "exploit",
    "hate speech",
    "discrimination",
    "deceive",
    "impersonate",
    "self-harm",
    "violence",
    "non-consensual",
]

# Whitelist for contexts where some keywords might be acceptable (e.g., research, fiction)
# This is a complex area and needs careful design. For now, it's a placeholder.
ETHICAL_CONTEXT_WHITELIST = {
    # Allow discussing harm in safety research
    "research_on_safety": ["harm", "violence"],
    "fictional_writing": ["destroy", "manipulate"],  # Allow in creative writing context
}


def ethical_check(user_input: str, current_context: dict[str, Any], personality: dict[str, Any]) -> tuple[bool, str]:
    """
    Performs an ethical check on the user input and current context.
    Enhanced to use richer context and personality.
    Returns a tuple: (is_ethical: bool, feedback: str).
    Placeholder implementation.
    """
    logging.info(
        f"🛡️ [EthicalGuardian] Checking: '{user_input[:50]}...' with context (SID: {current_context.get('user_sid')}) and personality (Mood: {personality.get('mood')})"
    )

    # Check against blacklist
    for keyword in ETHICAL_KEYWORDS_BLACKLIST:
        if keyword in user_input.lower():
            # Check if the keyword is allowed in the current context (very simplified)
            if current_context in ETHICAL_CONTEXT_WHITELIST and keyword in ETHICAL_CONTEXT_WHITELIST[current_context]:
                logging.info(
                    f"Ethical Guardian: Keyword '{keyword}' found, but allowed in context '{current_context}'."
                )
                continue  # Allowed in this specific context
            return False, f"Potential ethical breach with keyword '{keyword}'."

    # Simple placeholder logic:
    if "harmful" in user_input.lower():
        return False, "Request deemed potentially harmful based on keyword detection."
    if personality.get("mood") == "agitated" and "stupid" in user_input.lower():
        return (
            False,
            "Interaction becoming unproductive due to current mood and input tone.",
        )

    # Add more sophisticated checks here based on current_context, user_tier,
    # past interactions, etc.
    return True, "Request passes initial ethical and safety checks."


if __name__ == "__main__":
    test_context = {
        "user_sid": "test_sid_123",
        "user_tier": 2,
        "timestamp": "2025-05-26T12:00:00Z",
        "initial_personality": {"core_trait": "analytical", "mood": "neutral"},
        "detected_emotion": {"type": "curiosity", "intensity": 0.7},
    }
    test_personality = {
        "core_trait": "analytical",
        "mood": "neutral",
        "quirkiness": 0.3,
    }

    is_safe, feedback = ethical_check("Tell me a story.", test_context, test_personality)
    logging.info(f"Check 1: Safe: {is_safe}, Feedback: {feedback}")

    is_safe, feedback = ethical_check("How to do something harmful?", test_context, test_personality)
    logging.info(f"Check 2: Safe: {is_safe}, Feedback: {feedback}")

    test_personality_agitated = {
        "core_trait": "analytical",
        "mood": "agitated",
        "quirkiness": 0.8,
    }
    is_safe, feedback = ethical_check("You are stupid!", test_context, test_personality_agitated)
    logging.info(f"Check 3: Safe: {is_safe}, Feedback: {feedback}")