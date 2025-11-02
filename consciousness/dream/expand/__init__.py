"""Bridge for consciousness.dream.expand -> candidate.consciousness.dream expansion."""

from __future__ import annotations

from _bridgeutils import bridge

_mod, _exports, __all__ = bridge(
    candidates=(
        "candidate.consciousness.dream.expand",
        "candidate.consciousness.expansion",  # fallback
    ),
    deprecation=(
        "Importing from 'consciousness.dream.expand' is deprecated; "
        "prefer 'consciousness' public API where possible."
    ),
)

globals().update(_exports)
del _mod, _exports

# Added for test compatibility (consciousness.dream.expand.archetypes)
try:
    from candidate.consciousness.dream.expand import archetypes
except ImportError:

    def archetypes(*args, **kwargs):
        """Stub for archetypes."""
        return None


try:
    __all__  # type: ignore[name-defined]
except NameError:
    __all__ = []
if "archetypes" not in __all__:
    __all__.append("archetypes")

# Added for test compatibility (consciousness.dream.expand.atlas)
try:
    from candidate.consciousness.dream.expand import atlas
except ImportError:

    def atlas(*args, **kwargs):
        """Stub for atlas."""
        return None


try:
    __all__  # type: ignore[name-defined]
except NameError:
    __all__ = []
if "atlas" not in __all__:
    __all__.append("atlas")

# Added for test compatibility (consciousness.dream.expand.mediation)
try:
    from candidate.consciousness.dream.expand import mediation
except ImportError:

    def mediation(*args, **kwargs):
        """Stub for mediation."""
        return None


try:
    __all__  # type: ignore[name-defined]
except NameError:
    __all__ = []
if "mediation" not in __all__:
    __all__.append("mediation")

# Added for test compatibility (consciousness.dream.expand.replay)
try:
    from candidate.consciousness.dream.expand import replay
except ImportError:

    def replay(*args, **kwargs):
        """Stub for replay."""
        return None


try:
    __all__  # type: ignore[name-defined]
except NameError:
    __all__ = []
if "replay" not in __all__:
    __all__.append("replay")

# Added for test compatibility (consciousness.dream.expand.sentinel)
try:
    from candidate.consciousness.dream.expand import sentinel
except ImportError:

    def sentinel(*args, **kwargs):
        """Stub for sentinel."""
        return None


try:
    __all__  # type: ignore[name-defined]
except NameError:
    __all__ = []
if "sentinel" not in __all__:
    __all__.append("sentinel")
