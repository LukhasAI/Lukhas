"""
LUKHAS AI Symbolic System
Tag-based symbolic processing and methylation
Trinity Framework: ⚛️🧠🛡️

This module provides symbolic tagging and processing capabilities for LUKHAS AI,
including tag scopes, permissions, and methylation models for tag lifecycle management.
"""

from .methylation_model import MethylationModel
from .methylation_model import get_methylation_model
from .tags import SymbolicTag
from .tags import TagManager
from .tags import TagPermission
from .tags import TagScope
from .tags import get_tag_manager

__all__ = [
    "TagScope",
    "TagPermission",
    "SymbolicTag",
    "TagManager",
    "get_tag_manager",
    "MethylationModel",
    "get_methylation_model",
]
