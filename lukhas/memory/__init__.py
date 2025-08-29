"""
LUKHAS AI Memory Module
Fold-based memory with cascade prevention and emotional valence tracking
Trinity Framework: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian
"""

from typing import Any, Optional

# Version info
__version__ = "1.0.0"
__author__ = "LUKHAS AI Team"

# Core exports
try:
    from .fold_system import FoldManager, MemoryFold
    from .matriz_adapter import MemoryMatrizAdapter
    from .memory_wrapper import MemoryWrapper, get_memory_manager

    MEMORY_AVAILABLE = True
except ImportError:
    MemoryWrapper = None
    MemoryFold = None
    FoldManager = None
    MemoryMatrizAdapter = None
    MEMORY_AVAILABLE = False


# Module-level convenience functions
def create_fold(
    content: Any, causal_chain: Optional[list[str]] = None, **kwargs
) -> Optional[Any]:
    """Create a memory fold (dry-run by default)"""
    if not MEMORY_AVAILABLE:
        return None

    manager = get_memory_manager()
    if manager:
        return manager.create_fold(content, causal_chain, **kwargs)
    return None


def consolidate_memory(**kwargs) -> dict[str, Any]:
    """Consolidate memory folds (dry-run by default)"""
    if not MEMORY_AVAILABLE:
        return {"ok": False, "error": "memory_not_available"}

    manager = get_memory_manager()
    if manager:
        return manager.consolidate_memory(**kwargs)
    return {"ok": False, "error": "manager_not_available"}


def access_memory(query: dict[str, Any], **kwargs) -> dict[str, Any]:
    """Access memory with query (dry-run by default)"""
    if not MEMORY_AVAILABLE:
        return {"ok": False, "error": "memory_not_available"}

    manager = get_memory_manager()
    if manager:
        return manager.access_memory(query, **kwargs)
    return {"ok": False, "error": "manager_not_available"}


def dump_state(output_path: str) -> dict[str, Any]:
    """Dump current memory state to JSON file"""
    import hashlib
    import json
    import time

    if not MEMORY_AVAILABLE:
        # Create minimal dump for testing
        state = {
            "version": __version__,
            "folds": 0,
            # Non-security checksum: use SHA256 to satisfy security linters
            "checksum": hashlib.sha256(b"empty_memory_state").hexdigest(),
            "timestamp": time.time(),
            "status": "memory_not_available",
        }
    else:
        manager = get_memory_manager()
        if manager and hasattr(manager, "fold_manager") and manager.fold_manager:
            try:
                # Get fold count from manager
                fold_count = len(getattr(manager.fold_manager, "folds", {}))
            except Exception:
                fold_count = 0
        else:
            fold_count = 0

        # Create state dump
        state_content = f"version:{__version__},folds:{fold_count},time:{time.time()}"
        state = {
            "version": __version__,
            "folds": fold_count,
            # Non-security checksum: use SHA256 to satisfy security linters
            "checksum": hashlib.sha256(state_content.encode()).hexdigest(),
            "timestamp": time.time(),
            "status": "available" if MEMORY_AVAILABLE else "unavailable",
        }

    # Write to file
    try:
        with open(output_path, "w") as f:
            json.dump(state, f, indent=2)
        return {"ok": True, "path": output_path, "state": state}
    except Exception as e:
        return {"ok": False, "error": str(e)}


__all__ = [
    "MemoryWrapper",
    "MemoryFold",
    "FoldManager",
    "MemoryMatrizAdapter",
    "create_fold",
    "consolidate_memory",
    "access_memory",
    "get_memory_manager",
    "dump_state",
    "MEMORY_AVAILABLE",
]
