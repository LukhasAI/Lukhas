"""
LUKHAS Memory Fold System
========================

Central memory fold architecture implementing the research paper's
memory fold concept with optimized hybrid implementations.
"""
import streamlit as st

import logging

logger = logging.getLogger(__name__)

# Core memory fold components
try:
    from .distributed_memory_fold import DistributedMemoryFold
    from .hybrid_memory_fold import HybridMemoryFold, create_hybrid_memory_fold
    from .memory_fold import HybridMemoryItem
    from .memory_fold_system import MemoryFoldSystem, MemoryItem
    from .optimized_hybrid_memory_fold import OptimizedHybridMemoryFold

    logger.info("Memory fold system components loaded successfully")
except ImportError as e:
    logger.warning(f"Failed to import memory fold components: {e}")
    HybridMemoryItem = None
    MemoryFoldSystem = None
    MemoryItem = None
    HybridMemoryFold = None
    create_hybrid_memory_fold = None
    OptimizedHybridMemoryFold = None
    DistributedMemoryFold = None

__all__ = [
    "DistributedMemoryFold",
    "HybridMemoryFold",
    "HybridMemoryItem",
    "MemoryFoldSystem",
    "MemoryItem",
    "OptimizedHybridMemoryFold",
    "create_hybrid_memory_fold",
]
