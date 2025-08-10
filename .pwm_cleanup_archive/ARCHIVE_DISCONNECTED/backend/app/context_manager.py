"""
╭──────────────────────────────────────────────────────────────╮
│ MODULE      : context_manager.py                             │
│ DESCRIPTION : Build symbolic context for LucasID sessions    │
│ TYPE        : Symbolic Session Context Builder               │
│ AUTHOR      : Lukhas Systems                                  │
│ UPDATED     : 2025-04-29                                     │
╰──────────────────────────────────────────────────────────────╯
"""

from datetime import datetime

# ── In-memory symbolic context store (to be DB-backed) ─────────

session_contexts = {}


def build_context(
    user_id: int, username_slug: str, entity_type: str, tier: int
) -> dict:
    """
    Construct a symbolic context footprint for the session.
    """
    context = {
        "user_id": user_id,
        "username_slug": username_slug,
        "entity_type": entity_type,
        "tier": tier,
        "session_start": str(datetime.utcnow()),
        "symbolic_trace": f"{tier}-{entity_type}-{username_slug.upper()}",
    }
    session_contexts[user_id] = context
    print(f"🧠 Symbolic context built for {username_slug}: {context['symbolic_trace']}")
    return context


def get_context(user_id: int) -> dict:
    """
    Retrieve an existing symbolic session context.
    """
    return session_contexts.get(user_id)
