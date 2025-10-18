"""Shim for backwards compatibility.

Keep this file while we migrate internals to `branding.constellation.triad`.
It re-exports the public Triad surface so old imports continue to work.
"""

from constellation.triad import *  # noqa: F401,F403

__all__ = ["Identity", "Consciousness", "Guardian"]
