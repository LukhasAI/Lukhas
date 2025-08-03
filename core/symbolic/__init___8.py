# -*- coding: utf-8 -*-
"""

#TAG:core
#TAG:symbolic
#TAG:neuroplastic
#TAG:colony


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
log.info("core.memory module initialized - memory fold system with symbolic integration")

# Import core memory fold components
try:
    from .fold_engine import AGIMemory, MemoryFold, MemoryType, MemoryPriority
    from .fold_lineage_tracker import FoldLineageTracker
    from .memory_fold import MemoryFoldSystem as MemoryFoldManager
    from .dream_memory_fold import DreamMemoryFold
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
    from core.symbolic.symbolic_boot import GLYPH_MAP, get_glyph_meaning
    SYMBOLIC_INTEGRATION_ENABLED = True
except ImportError:
    log.warning("Symbolic integration not available - memory folds will operate without GLYPH encoding")
    SYMBOLIC_INTEGRATION_ENABLED = False
    GLYPH_MAP = {}
    get_glyph_meaning = lambda x: "Unknown"

# CLAUDE_EDIT_v0.1: Export list for memory module
__all__ = [
    # Core fold components
    'AGIMemory',
    'MemoryFold',
    'MemoryType',
    'MemoryPriority',
    'FoldLineageTracker',
    'MemoryFoldManager',
    'DreamMemoryFold',
    # Symbolic integration flags
    'SYMBOLIC_INTEGRATION_ENABLED',
]

# Memory fold configuration with symbolic hooks
MEMORY_FOLD_CONFIG = {
    'compression_enabled': True,
    'symbolic_encoding': SYMBOLIC_INTEGRATION_ENABLED,
    'drift_detection': True,
    'lineage_tracking': True,
    'max_fold_depth': 7,  # Symbolic significance
    'glyph_compression_ratio': 0.618,  # Golden ratio for optimal compression
}

log.info(f"Memory fold configuration: {MEMORY_FOLD_CONFIG}")

# Import isolated memory components
try:
    from .systems.memory_trace import MemoryTrace
    from .systems.memory_voice_helix import VoiceHelix
    from .systems.chatgpt_memory_integrator import ChatGPTMemoryIntegrator
    
    # Register with memory fold system
    if 'memory_manager' in globals():
        memory_manager.register_component('trace', MemoryTrace)
        memory_manager.register_component('voice_helix', VoiceHelix)
        memory_manager.register_component('chatgpt', ChatGPTMemoryIntegrator)
except ImportError as e:
    log.warning(f"Some memory components not available: {e}")
