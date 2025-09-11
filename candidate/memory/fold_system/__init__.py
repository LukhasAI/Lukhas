"""
LUKHAS Memory Fold System
========================

Central memory fold architecture implementing the research paper's
memory fold concept with optimized hybrid implementations.
"""
import logging

logger = logging.getLogger(__name__)

# Core memory fold components - import in dependency order to avoid circular imports
try:
    # Import memory_fold_system first as it's the base
    from .distributed_memory_fold import DistributedMemoryFold
    from .hybrid_memory_fold import HybridMemoryFold, create_hybrid_memory_fold

    # Then import dependent modules
    from .memory_fold import HybridMemoryItem
    from .memory_fold_system import MemoryFoldSystem, MemoryItem
    from .optimized_hybrid_memory_fold import OptimizedHybridMemoryFold

    logger.info("✅ Memory fold system components loaded successfully")
except ImportError as e:
    logger.debug(f"Memory fold system import issue (using compatibility layer): {e}")
    # Create compatibility classes for systems that depend on these
    class MemoryFoldSystem:
        def __init__(self, config=None):
            self.config = config or {}
    class MemoryItem:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
    class HybridMemoryItem:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    # Set other classes to None when not available
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
