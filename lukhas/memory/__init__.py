"""
LUKHAS AI Memory Module
Unified memory system with fold-based storage
Trinity Framework: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian
"""

__version__ = "3.0.0"
__trinity__ = "⚛️🧠🛡️"

# Core memory systems
from . import causal, colonies, consolidation, episodic, fold
from .causal import get_causal_memory
from .colonies import get_memory_colony
from .consolidation import get_consolidator
from .episodic import get_episodic_memory

# Convenience imports
from .fold import get_fold_manager

__all__ = [
    "fold",
    "causal",
    "episodic",
    "consolidation",
    "colonies",
    "get_fold_manager",
    "get_causal_memory",
    "get_episodic_memory",
    "get_consolidator",
    "get_memory_colony",
]


class UnifiedMemory:
    """Unified interface to all memory systems"""

    def __init__(self):
        self.fold_manager = get_fold_manager()
        self.causal = get_causal_memory()
        self.episodic = get_episodic_memory()
        self.consolidator = get_consolidator()
        self.colony = get_memory_colony()

    def store(self, content, memory_type="episodic", **kwargs):
        """Store memory in appropriate system"""
        if memory_type == "fold":
            return self.fold_manager.create_fold(content, **kwargs)
        elif memory_type == "episodic":
            return self.episodic.store_episode(content, **kwargs)
        elif memory_type == "causal":
            return self.causal.add_causal_link(content, **kwargs)
        else:
            # Default to colony storage
            import uuid

            memory_id = str(uuid.uuid4())
            self.colony.store_memory(memory_id, content)
            return memory_id

    def retrieve(self, query, memory_type="episodic"):
        """Retrieve memory from appropriate system"""
        if memory_type == "fold":
            return self.fold_manager.retrieve_fold(query)
        elif memory_type == "episodic":
            return self.episodic.retrieve_by_similarity(query)
        elif memory_type == "causal":
            return self.causal.get_effects(query)
        else:
            return self.colony.retrieve_memory(query)

    def get_status(self):
        """Get overall memory system status"""
        return {
            "folds": len(self.fold_manager.folds),
            "episodes": len(self.episodic.episodes),
            "causal_links": len(self.causal.causal_graph),
            "colony": self.colony.get_colony_status(),
            "trinity": "synchronized",
        }


# Singleton instance
_unified_memory = None


def get_unified_memory() -> UnifiedMemory:
    """Get or create unified memory instance"""
    global _unified_memory
    if _unified_memory is None:
        _unified_memory = UnifiedMemory()
    return _unified_memory


# Trinity integration
def trinity_sync():
    """Synchronize with Trinity Framework"""
    return {
        "identity": "⚛️",
        "consciousness": "🧠",
        "guardian": "🛡️",
        "memory_status": "synchronized",
    }
