"""
context_builder.py — NIAS helper module

Builds symbolic context for NIAS delivery. Supports standalone mode by
gracefully handling DAST or ABAS imports.

Author: You
"""

from . import mesh_visualizer, trace_logger


def build_user_context(user_id):
    emotional_vector = mesh_visualizer.get_emotional_state(user_id)
    task_tags = []

    try:
        from dast import get_current_tags

        task_tags = get_current_tags(user_id)
    except ImportError:
        trace_logger.log_meta("DAST module not found — fallback active.")

    try:
        from abas import is_allowed_now

        if not is_allowed_now(user_id):
            trace_logger.log_block(None, reason="ABAS: attention block")
            return None
    except ImportError:
        trace_logger.log_meta("ABAS module not found — arbitration bypassed.")

    return {
        "emotional_vector": emotional_vector,
        "task_tags": task_tags,
        "user_tier": 3,
    }
