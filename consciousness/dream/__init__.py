"""
Consciousness Dream Bridge - Canonical Public API
Bridge to labs.consciousness.dream (single source of truth)

Dream processing, state transitions, and creative exploration.
Constellation Framework: ⚛️🧠🛡️
"""
# Note: labs/consciousness/dream has minimal __init__.py
# Re-export the package itself for submodule access
from labs.consciousness import dream

__all__ = ["dream"]
