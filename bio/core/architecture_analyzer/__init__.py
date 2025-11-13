"""
Bio Architecture Analyzer Bridge - Canonical Public API
Bridge to candidate/labs bio architecture analyzer (single source of truth)

Bio-inspired architecture analysis and pattern recognition.
Constellation Framework: 🌱
"""
# Re-export from appropriate source
try:
    from candidate.bio.core.architecture_analyzer import *  # noqa: F401, F403
except (ModuleNotFoundError, ImportError):  # pragma: no cover - optional fallback
    try:
        from labs.bio.core.architecture_analyzer import *  # noqa: F401, F403
    except (ModuleNotFoundError, ImportError):  # pragma: no cover
        # Minimal stub
        class Architecture:
            """Placeholder for bio architecture analysis."""
            pass

__all__ = ["Architecture"]
