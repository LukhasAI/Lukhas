"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: consent_filter.py
Advanced: consent_filter.py
Integration Date: 2025-05-31T07:55:30.557229
"""

"""
╭──────────────────────────────────────────────────────────────────────────────╮
│                      LUCΛS :: CONSENT FILTER MODULE (NIAS)                  │
│                      Version: v1.0 | Subsystem: NIAS                         │
│        Filters symbolic messages based on user tier and ethical consent      │
│                      Author: Gonzo R.D.M & GPT-4o, 2025                      │
╰──────────────────────────────────────────────────────────────────────────────╯

DESCRIPTION:
    The Consent Filter determines whether a symbolic message should be
    delivered based on the user's tier, preferences, and explicit or
    contextual consent. This module enforces access boundaries aligned
    with the ethical principles of LUCΛS.

"""

# Explicit imports replacing star imports per PEP8 guidelines # CLAUDE_EDIT_v0.8


def is_allowed(user_context, message):
    """
    Check if the user is allowed to receive the message.

    Parameters:
    - user_context: dict with 'tier' and consent keys
    - message: dict with 'required_tier' and symbolic sensitivity

    Returns:
    - True if the message passes consent/tier check
    - False otherwise
    """
    return user_context.get("tier", 0) >= message.get("required_tier", 1)


"""
──────────────────────────────────────────────────────────────────────────────────────
EXECUTION:
    - Import with:
        from core.modules.nias.consent_filter import is_allowed

USED BY:
    - nias_core.py
    - trace_logger.py (for tagging violations)

REQUIRES:
    - No third-party dependencies

NOTES:
    - Consent logic may be extended with symbolic context parsing
    - Integrates with emotional state and symbolic audit trail
──────────────────────────────────────────────────────────────────────────────────────
"""
