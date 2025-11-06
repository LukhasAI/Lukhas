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

__all__ = ["awareness"]
