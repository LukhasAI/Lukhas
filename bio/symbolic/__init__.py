"""
Compatibility shim for bio_symbolic
DEPRECATED: This module will be removed on 2025-11-01
Please update imports to: lukhas.accepted.bio.symbolic

TODO[T4-AUDIT]:triage - Deep bio hierarchy with unclear integration path. Need architecture analysis.
"""

import warnings

from lukhas.bio.symbolic import *

# warnings.warn(
#     "Import 'bio_symbolic' is deprecated and will be removed on 2025-11-01. "
#     "Please update to 'lukhas.accepted.bio.symbolic'",
#     DeprecationWarning,
#     stacklevel=2,
# )

# Re-export everything for backward compatibility
__all__ = dir()
