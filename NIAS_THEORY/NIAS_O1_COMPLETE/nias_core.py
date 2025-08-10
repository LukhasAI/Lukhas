"""
nias_core.py — Core logic for NIAS (Non-Intrusive Ad System)

Routes symbolic messages through consent, emotional filtering, symbolic matching,
and timing logic. Logs all delivery or block outcomes.

Author: You
"""

from . import (
    consent_filter,
    context_builder,
    delivery_loop,
    emotional_sorter,
    symbolic_matcher,
    trace_logger,
)


def push(msg, user_id="default"):
    user_context = context_builder.build_user_context(user_id)
    if user_context is None:
        trace_logger.log_block(msg, reason="User context invalid or blocked")
        return {"status": "deferred", "reason": "Context unavailable"}

    if not consent_filter.allowed(msg, user_context):
        trace_logger.log_block(msg, reason="Consent denied or tier lock")
        return {"status": "blocked", "reason": "Consent or Tier Block"}

    if not emotional_sorter.stable_for(msg, user_context):
        trace_logger.log_block(msg, reason="Emotional state unstable")
        return {"status": "deferred", "reason": "Emotional overflow"}

    if not symbolic_matcher.matches(msg, user_context):
        trace_logger.log_block(msg, reason="Symbolic mismatch")
        return {"status": "blocked", "reason": "Symbolic mismatch"}

    delivery_loop.schedule(msg)
    trace_logger.log_success(msg)
    return {"status": "delivered", "method": "visual"}
