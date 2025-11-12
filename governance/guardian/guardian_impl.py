"""
Bridge module for governance.guardian.guardian_impl
===================================================

Provides access to GuardianSystemImpl from lukhas_website.lukhas.governance.guardian.guardian_impl
with fallback to labs implementation if needed.

This bridge enables imports like:
    from governance.guardian.guardian_impl import GuardianSystemImpl

Guardian Implementation:
- GuardianSystemImpl: Real Guardian system implementation with drift detection,
  ethical evaluation, and safety validation. Loaded when GUARDIAN_ACTIVE=true.
"""

from __future__ import annotations

try:
    # Primary: lukhas_website production lane
    from lukhas_website.lukhas.governance.guardian.guardian_impl import GuardianSystemImpl
except ImportError:
    try:
        # Fallback: labs development lane
        from labs.governance.guardian.guardian_impl import GuardianSystemImpl
    except ImportError:
        # Final fallback: raise informative error
        raise ImportError(
            "GuardianSystemImpl not found. "
            "Expected location: lukhas_website.lukhas.governance.guardian.guardian_impl "
            "or labs.governance.guardian.guardian_impl"
        )

__all__ = ["GuardianSystemImpl"]
