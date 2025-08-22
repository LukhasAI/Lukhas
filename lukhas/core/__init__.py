"""
LUKHAS AI Core Module
Foundational systems for symbolic processing, GLYPH engine, and Trinity Framework
Trinity Framework: Identity, Consciousness, Guardian
"""

from .core_wrapper import (
    CoreWrapper,
    GlyphResult,
    SymbolicResult, 
    CoreStatus,
    get_core,
    encode_concept,
    create_trinity_glyph,
    get_core_status
)

# Version and module info
__version__ = "2.0.0"
__module_name__ = "core"
__description__ = "LUKHAS AI foundational systems - GLYPH engine, symbolic processing, Trinity Framework"

# Trinity Framework symbols
TRINITY_SYMBOLS = {
    "identity": "⚛️",
    "consciousness": "🧠", 
    "guardian": "🛡️",
    "framework": "⚛️🧠🛡️"
}

# Export public interface
__all__ = [
    "CoreWrapper",
    "GlyphResult",
    "SymbolicResult", 
    "CoreStatus",
    "get_core",
    "encode_concept", 
    "create_trinity_glyph",
    "get_core_status",
    "TRINITY_SYMBOLS"
]