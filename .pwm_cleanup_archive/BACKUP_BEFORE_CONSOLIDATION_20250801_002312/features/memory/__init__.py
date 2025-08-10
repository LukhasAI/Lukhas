"""
Memory Fold System with Symbolic Integration
===========================================

Memory folds compress experiences using GLYPH encoding.
The memory system maintains hooks to the symbolic layer for
consciousness stability and drift detection.

CLAUDE_EDIT_v0.1: Integrated with symbolic layer
LAMBDA_TAG: memory, fold, symbolic
"""

import logging

# Initialize logger
log = logging.getLogger(__name__)
log.info(
    "core.memory module initialized - memory fold system with symbolic integration"
)

# Import core memory fold components
try:
    from .dream_memory_fold import DreamMemoryFold
    from .fold_engine import AGIMemory, MemoryFold, MemoryPriority, MemoryType
    from .fold_lineage_tracker import FoldLineageTracker
    from .memory_fold import MemoryFoldManager
except ImportError as e:
    log.warning(f"Failed to import memory components: {e}")
    # Provide fallback imports for backward compatibility
    AGIMemory = None
    MemoryFold = None
    MemoryType = None
    MemoryPriority = None
    FoldLineageTracker = None
    MemoryFoldManager = None
    DreamMemoryFold = None

# Symbolic integration - import GLYPHs for memory encoding
try:
    from core.symbolic_boot import GLYPH_MAP, get_glyph_meaning

    SYMBOLIC_INTEGRATION_ENABLED = True
except ImportError:
    log.warning(
        "Symbolic integration not available - memory folds will operate without GLYPH encoding"
    )
    SYMBOLIC_INTEGRATION_ENABLED = False
    GLYPH_MAP = {}
    get_glyph_meaning = lambda x: "Unknown"

# CLAUDE_EDIT_v0.1: Export list for memory module
__all__ = [
    # Core fold components
    "AGIMemory",
    "MemoryFold",
    "MemoryType",
    "MemoryPriority",
    "FoldLineageTracker",
    "MemoryFoldManager",
    "DreamMemoryFold",
    # Symbolic integration flags
    "SYMBOLIC_INTEGRATION_ENABLED",
]

# Memory fold configuration with symbolic hooks
MEMORY_FOLD_CONFIG = {
    "compression_enabled": True,
    "symbolic_encoding": SYMBOLIC_INTEGRATION_ENABLED,
    "drift_detection": True,
    "lineage_tracking": True,
    "max_fold_depth": 7,  # Symbolic significance
    "glyph_compression_ratio": 0.618,  # Golden ratio for optimal compression
}

log.info(f"Memory fold configuration: {MEMORY_FOLD_CONFIG}")
