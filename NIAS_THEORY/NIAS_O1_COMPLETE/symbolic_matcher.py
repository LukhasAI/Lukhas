"""
symbolic_matcher.py — part of NIAS (Non-Intrusive Ad System) for LUCΛS AGI

Filters symbolic messages based on emotional state, dream status,
and symbolic tag relevance. Blocks are logged symbolically.

Author: You
"""

from . import trace_logger


def matches(msg, user_context):
    msg_tags = msg.get("tags", [])
    msg_emotion = msg.get("emotion", "neutral")
    msg_intensity = msg.get("intensity", 0.5)

    task_tags = user_context.get("task_tags", [])
    evector = user_context.get("emotional_vector", {})
    dream_residue = evector.get("dream_residue", False)
    tolerance = evector.get("tolerance", 0.8)
    stress = evector.get("stress", 0)

    if dream_residue:
        trace_logger.log_block(msg, reason="Dream residue active")
        return False

    if not any(tag in task_tags for tag in msg_tags):
        trace_logger.log_block(msg, reason="Symbolic mismatch (tags)")
        return False

    if msg_emotion == "soft" and stress > 0.7:
        trace_logger.log_block(msg, reason="Emotional mismatch (soft vs stress)")
        return False

    if msg_intensity > tolerance:
        trace_logger.log_block(msg, reason="Message intensity exceeds tolerance")
        return False

    return True
