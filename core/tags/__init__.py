"""
DEPRECATED: The `core.tags` module has been migrated to the MATRIZ architecture.
Please use `lukhas.tags` instead.
"""
import warnings

warnings.warn(
    "`core.tags` is deprecated and will be removed in a future version. "
    "Please use `lukhas.tags` instead.",
    DeprecationWarning,
    stacklevel=2,
)

from lukhas.tags import *
