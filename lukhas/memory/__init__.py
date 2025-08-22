"""
LUKHAS AI Memory Module
Fold-based memory with cascade prevention and emotional valence tracking
Trinity Framework: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian
"""

from typing import Optional, Any, Dict, List

# Version info
__version__ = "1.0.0"
__author__ = "LUKHAS AI Team"

# Core exports
try:
    from .memory_wrapper import MemoryWrapper, get_memory_manager
    from .fold_system import MemoryFold, FoldManager
    from .matriz_adapter import MemoryMatrizAdapter

    MEMORY_AVAILABLE = True
except ImportError:
    MemoryWrapper = None
    MemoryFold = None
    FoldManager = None
    MemoryMatrizAdapter = None
    MEMORY_AVAILABLE = False


# Module-level convenience functions
def create_fold(content: Any, causal_chain: Optional[List[str]] = None, **kwargs) -> Optional[Any]:
    """Create a memory fold (dry-run by default)"""
    if not MEMORY_AVAILABLE:
        return None

    manager = get_memory_manager()
    if manager:
        return manager.create_fold(content, causal_chain, **kwargs)
    return None


def consolidate_memory(**kwargs) -> Dict[str, Any]:
    """Consolidate memory folds (dry-run by default)"""
    if not MEMORY_AVAILABLE:
        return {"ok": False, "error": "memory_not_available"}

    manager = get_memory_manager()
    if manager:
        return manager.consolidate_memory(**kwargs)
    return {"ok": False, "error": "manager_not_available"}


def access_memory(query: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Access memory with query (dry-run by default)"""
    if not MEMORY_AVAILABLE:
        return {"ok": False, "error": "memory_not_available"}

    manager = get_memory_manager()
    if manager:
        return manager.access_memory(query, **kwargs)
    return {"ok": False, "error": "manager_not_available"}


__all__ = [
    "MemoryWrapper",
    "MemoryFold",
    "FoldManager",
    "MemoryMatrizAdapter",
    "create_fold",
    "consolidate_memory",
    "access_memory",
    "get_memory_manager",
    "MEMORY_AVAILABLE",
]
