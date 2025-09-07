"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: nias_core.py
Advanced: nias_core.py
Integration Date: 2025-05-31T07:55:30.518606
"""

"""
╭──────────────────────────────────────────────────────────────────────────────╮
│                          LUCΛS :: NIAS CORE MODULE                           │
│                      Version: v1.0 | Subsystem: NIAS                         │
│    Core symbolic delivery logic, consent-aware, and ethically filtered.      │
│                       Author: Gonzo R.D.M & GPT-4o, 2025                     │
╰──────────────────────────────────────────────────────────────────────────────╯

DESCRIPTION:
    The NIAS Core module is responsible for orchestrating symbolic message
    delivery in the LUCΛS system. It connects matching logic, ABAS checks,
    and tier-aware consent filtration. This is where final decisions are made
    on whether a symbolic signal may reach the user.

"""

from lukhas.core.interfaces.as_agent.sys.abas.abas import is_allowed_now
from lukhas.core.interfaces.as_agent.sys.nias.consent_filter import is_allowed
from lukhas.core.interfaces.as_agent.sys.nias.symbolic_matcher import (
    match_message_to_context,
)
from lukhas.core.interfaces.as_agent.sys.nias.trace_logger import log_delivery_event


def push_symbolic_message(message, user_context):
    """
    Accepts a symbolic message and user context.
    Routes message through matching, consent, and attention filters.
    Returns delivery decision and symbolic outcome.
    """
    user_id = user_context.get("user_id", "unknown_user")

    # Step 1: Consent filter
    if not is_allowed(user_context, message):
        log_delivery_event(
            user_id,
            message["message_id"],
            "blocked",
            user_context,
            "consent_filter",
        )
        return {"status": "blocked", "reason": "consent_filter"}

    # Step 2: ABAS threshold check
    if not is_allowed_now(user_context):
        log_delivery_event(
            user_id,
            message["message_id"],
            "blocked",
            user_context,
            "abas_threshold",
        )
        return {"status": "blocked", "reason": "abas_threshold"}

    # Step 3: Symbolic matcher
    match = match_message_to_context(message, user_context)
    decision = match["decision"]

    # Step 4: Trace + return outcome
    log_delivery_event(
        user_id,
        message["message_id"],
        decision,
        user_context,
        "symbolic_match",
    )
    return {"status": decision, "reason": "symbolic_match"}


"""
──────────────────────────────────────────────────────────────────────────────────────
EXECUTION:
    This module is called by the main NIAS delivery loop.
    It coordinates symbolic match evaluation and tier-filtered delivery.

USED BY:
    - delivery_loop.py
    - context_builder.py

REQUIRES:
    - symbolic_matcher
    - consent_filter
    - abas

NOTES:
    - Tier-sensitive logic
    - Works in tandem with emotion vector and dream fallback
──────────────────────────────────────────────────────────────────────────────────────
"""
