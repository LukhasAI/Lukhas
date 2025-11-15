"""
Consciousness Interfaces Bridge - Canonical Public API
Bridge to candidate/labs consciousness interfaces (single source of truth)

Protocol and interface definitions for consciousness modules.
Constellation Framework: ⚛️🧠
"""
# Re-export consciousness interfaces from appropriate source
try:
    from candidate.consciousness.interfaces import *  # noqa: F401, F403
except (ModuleNotFoundError, ImportError):  # pragma: no cover - optional fallback
    try:
        from labs.consciousness.interfaces import *  # noqa: F401, F403
    except (ModuleNotFoundError, ImportError):  # pragma: no cover
        # Minimal fallback - provide basic interface protocol
        pass

__all__ = []
