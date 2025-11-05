"""Compatibility package for legacy `bio.*` imports."""
from __future__ import annotations

from bio.core import BioCore

__all__ = ["energy", "BioCore"]

# Bridge export for bio.adapters
try:
    from labs.bio import adapters
except ImportError:
    def adapters(*args, **kwargs):
        """Stub for adapters."""
        return None

try:
    __all__  # type: ignore[name-defined]
except NameError:
    __all__ = []
if "adapters" not in __all__:
    __all__.append("adapters")

# Bridge export for bio.compound_governor
try:
    from labs.bio import compound_governor
except ImportError:
    def compound_governor(*args, **kwargs):
        """Stub for compound_governor."""
        return None

try:
    __all__  # type: ignore[name-defined]
except NameError:
    __all__ = []
if "compound_governor" not in __all__:
    __all__.append("compound_governor")

# Bridge export for bio.matriz_adapter
try:
    from labs.bio import matriz_adapter
except ImportError:
    def matriz_adapter(*args, **kwargs):
        """Stub for matriz_adapter."""
        return None

try:
    __all__  # type: ignore[name-defined]
except NameError:
    __all__ = []
if "matriz_adapter" not in __all__:
    __all__.append("matriz_adapter")

# Bridge export for bio.qi
try:
    from labs.bio import qi
except ImportError:
    def qi(*args, **kwargs):
        """Stub for qi."""
        return None

try:
    __all__  # type: ignore[name-defined]
except NameError:
    __all__ = []
if "qi" not in __all__:
    __all__.append("qi")

# Bridge export for bio.spirulina_atp_system
try:
    from labs.bio import spirulina_atp_system
except ImportError:
    def spirulina_atp_system(*args, **kwargs):
        """Stub for spirulina_atp_system."""
        return None

try:
    __all__  # type: ignore[name-defined]
except NameError:
    __all__ = []
if "spirulina_atp_system" not in __all__:
    __all__.append("spirulina_atp_system")

# Bridge export for bio.symbolic_proteome
try:
    from labs.bio import symbolic_proteome
except ImportError:
    def symbolic_proteome(*args, **kwargs):
        """Stub for symbolic_proteome."""
        return None

try:
    __all__  # type: ignore[name-defined]
except NameError:
    __all__ = []
if "symbolic_proteome" not in __all__:
    __all__.append("symbolic_proteome")

# Bridge export for bio.voice
try:
    from labs.bio import voice
except ImportError:
    def voice(*args, **kwargs):
        """Stub for voice."""
        return None

try:
    __all__  # type: ignore[name-defined]
except NameError:
    __all__ = []
if "voice" not in __all__:
    __all__.append("voice")
