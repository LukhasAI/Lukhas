"""Shim for backwards compatibility.

Keep this file while we migrate internals to `branding.constellation.triad`.
It re-exports the public Triad surface so old imports continue to work.
"""

# Import explicit names instead of star import to satisfy linting and make the
# public surface unambiguous.
from constellation.triad import Consciousness, Guardian, Identity

__all__ = ["Consciousness", "Guardian", "Identity"]
