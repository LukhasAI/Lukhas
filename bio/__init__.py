"""
Bio module compatibility layer
Provides backward compatibility for bio.bio_utilities imports
"""

import warnings

from lukhas.bio.utils import *

# Import bio_utilities for backward compatibility
try:
    from . import bio_utilities
except ImportError:
    import sys
    import types

    # Create a virtual bio_utilities module
    bio_utilities = types.ModuleType("bio_utilities")

    # Re-export everything from lukhas.bio.utils
    for name in dir():
        if not name.startswith("_"):
            setattr(bio_utilities, name, globals()[name])

    sys.modules["bio.bio_utilities"] = bio_utilities

warnings.warn(
    "Import 'bio.bio_utilities' is deprecated. Please update to 'lukhas.accepted.bio.utils'",
    DeprecationWarning,
    stacklevel=2,
)
