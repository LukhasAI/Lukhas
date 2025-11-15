"""
Consciousness Awareness Engine Bridge - Canonical Public API
Bridge to candidate/labs consciousness awareness engine (single source of truth)

Constellation Framework: ⚛️🧠🛡️
"""
# Re-export AwarenessEngine from appropriate source
try:
    from candidate.consciousness.awareness.awareness_engine import *  # noqa: F401, F403
    from candidate.consciousness.awareness.awareness_engine import AwarenessEngine
except (ModuleNotFoundError, ImportError):  # pragma: no cover - optional fallback
    try:
        from labs.consciousness.awareness.awareness_engine import *  # noqa: F401, F403
        from labs.consciousness.awareness.awareness_engine import AwarenessEngine  # type: ignore[import-not-found]
    except (ModuleNotFoundError, ImportError) as e:
        raise ImportError(
            f"AwarenessEngine not found in candidate or labs consciousness.awareness: {e}"
        ) from e

__all__ = ["AwarenessEngine"]
