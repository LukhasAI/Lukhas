"""
Compatibility package for experimental/ → labs/ migration.

Legacy code may import from 'experimental.*' - this shim re-exports
everything from 'labs' (formerly candidate) for backward compatibility.

Phase 2: candidate → labs rename complete
Phase 3: This compatibility layer deprecated, will be removed in v1.0
"""

# Re-export everything from labs (formerly candidate)
from labs import *

__all__ = ["*"]  # Export all symbols from labs
