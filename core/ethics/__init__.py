"""
Core Ethics Bridge - Canonical Public API
Bridge to candidate.core.ethics (single source of truth)

Foundational ethical models, safety constraints, and evaluation mechanisms.
Constellation Framework: ⚛️🧠🛡️
"""
# Re-export the entire ethics module for access to all components
from labs.core import ethics

__all__ = ["ethics"]
