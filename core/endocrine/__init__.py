"""
DEPRECATED: The `core.endocrine` module has been migrated to the MATRIZ architecture.
Please use `lukhas.endocrine` instead.
"""
import warnings

warnings.warn(
    "`core.endocrine` is deprecated and will be removed in a future version. "
    "Please use `lukhas.endocrine` instead.",
    DeprecationWarning,
    stacklevel=2,
)

from lukhas.endocrine import *
