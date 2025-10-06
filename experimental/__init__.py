"""
Compatibility package for experimental/ → candidate/ migration.

Legacy code may import from 'experimental.*' - this shim re-exports
everything from 'candidate' for backward compatibility.

This compatibility layer will be removed in v0.04.
"""

# Re-export everything from candidate
from candidate import *  # noqa: F401, F403

__all__ = ["*"]  # Export all symbols from candidate
