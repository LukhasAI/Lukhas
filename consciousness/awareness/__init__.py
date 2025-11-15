"""
Consciousness Awareness Bridge - Canonical Public API
Bridge to candidate.consciousness.awareness (single source of truth)

Awareness components for consciousness tracking and monitoring.
Constellation Framework: ⚛️🧠🛡️
"""
# Re-export the package itself for submodule access
try:
    from candidate.consciousness import awareness
except ModuleNotFoundError:  # pragma: no cover - optional fallback
    from labs.consciousness import awareness  # type: ignore[import-not-found]

# Re-export AwarenessEngine for test compatibility
try:
    from candidate.consciousness.awareness.awareness_engine import AwarenessEngine
except (ModuleNotFoundError, ImportError):  # pragma: no cover - optional fallback
    try:
        from labs.consciousness.awareness.awareness_engine import AwarenessEngine  # type: ignore[import-not-found]
    except (ModuleNotFoundError, ImportError):
        # Fallback: AwarenessEngine not available
        AwarenessEngine = None  # type: ignore[assignment,misc]

__all__ = ["awareness", "AwarenessEngine"]
