"""
DEPRECATED: Legacy Bridge Module
=================================

This module is a legacy bridge and will be removed in a future release.

**Deprecation Notice**: This import path is deprecated as of 2025-11-12.

Use the canonical import path instead:
    from lukhas_website.lukhas.governance.guardian import GuardianSystem

Or use the new bridge pattern:
    from governance.guardian import GuardianSystem

Migration Path:
    OLD: from governance.guardian_system import GuardianSystem
    NEW: from lukhas_website.lukhas.governance.guardian import GuardianSystem

This module will be removed in Phase 4 (2025-Q1).
"""
from __future__ import annotations

import warnings

warnings.warn(
    "governance.guardian_system is deprecated. "
    "Use lukhas_website.lukhas.governance.guardian or governance.guardian instead.",
    DeprecationWarning,
    stacklevel=2,
)

from labs.governance.guardian_system import GuardianSystem

__all__ = ["GuardianSystem"]
