"""
Collective Ad Mind Bridge
Bridge to candidate/labs collective ad mind systems

Collective advertising and marketing intelligence.
"""
try:
    from candidate.core.collective.collective_ad_mind import *  # noqa: F401, F403
except (ModuleNotFoundError, ImportError):
    try:
        from labs.core.collective.collective_ad_mind import *  # noqa: F401, F403
    except (ModuleNotFoundError, ImportError):
        # Minimal stub
        class CollectiveAdMind:
            """Placeholder for collective ad mind."""
            pass

__all__ = ["CollectiveAdMind"]
