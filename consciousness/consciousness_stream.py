"""
Consciousness Stream Bridge - Canonical Public API
Bridge to candidate/labs/core consciousness_stream (single source of truth)

Consciousness stream processing and management.
Constellation Framework: ⚛️🧠
"""
# Re-export consciousness_stream from appropriate source
try:
    from candidate.core.consciousness_stream import *  # noqa: F401, F403
except (ModuleNotFoundError, ImportError):  # pragma: no cover - optional fallback
    try:
        from labs.core.consciousness_stream import *  # noqa: F401, F403
    except (ModuleNotFoundError, ImportError):  # pragma: no cover
        try:
            from core.consciousness_stream import *  # noqa: F401, F403
        except (ModuleNotFoundError, ImportError) as e:
            raise ImportError(
                f"consciousness_stream not found in candidate, labs, or core: {e}"
            ) from e

__all__ = ["StreamProcessor", "ConsciousnessStream"]
