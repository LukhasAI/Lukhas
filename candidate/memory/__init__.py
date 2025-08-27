"""
LUKHAS AI Consolidated Memory Module

This module consolidates all memory-related components:
- Core memory management
- Fold-based memory system
- Memory safety features
- Planning and optimization
- Memory interfaces and bridges
- Colony systems
"""


# Version info
__version__ = "2.0.0"
__author__ = "LUKHAS AI Team"

# Import core components
try:
    from .core import MemoryCore
    from .folds.base import MemoryFold
except ImportError:
    MemoryCore = None
    MemoryFold = None

# Import safety features
try:
    from .safety import MemorySafetyManager
except ImportError:
    MemorySafetyManager = None

# Import planning
try:
    from .planning import MemoryPlanner
except ImportError:
    MemoryPlanner = None

# Import services
try:
    from .services.manager import MemoryManager
    from .services.orchestrator import MemoryOrchestrator
except ImportError:
    pass

__all__ = [
    "MemoryCore",
    "MemoryFold",
    "MemorySafetyManager",
    "MemoryPlanner",
    "MemoryManager",
    "MemoryOrchestrator",
]
