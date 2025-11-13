"""
DEPRECATED: Legacy Bridge Module
=================================

This module is a legacy bridge and will be removed in a future release.

**Deprecation Notice**: This import path is deprecated as of 2025-11-12.

Use the canonical import path instead:
    from lukhas_website.lukhas.governance.guardian import GuardianShadowFilter

Or use the new bridge pattern:
    from governance.guardian import GuardianShadowFilter

Migration Path:
    OLD: from governance.guardian_shadow_filter import GuardianShadowFilter
    NEW: from lukhas_website.lukhas.governance.guardian import GuardianShadowFilter

This module will be removed in Phase 4 (2025-Q1).
"""
from __future__ import annotations

import warnings

warnings.warn(
    "governance.guardian_shadow_filter is deprecated. "
    "Use lukhas_website.lukhas.governance.guardian or governance.guardian instead.",
    DeprecationWarning,
    stacklevel=2,
)

from labs.governance.guardian_shadow_filter import GuardianShadowFilter, filter_shadows

__all__ = ["GuardianShadowFilter", "filter_shadows"]
