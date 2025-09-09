"""
LUKHAS AI Filesystem Core Module
==============================

Centralized filesystem utilities for LUKHAS AI project.
Provides path management, directory utilities, and project structure helpers.
"""

from .path_manager import (
    LukhasPathManager,
    paths,
    get_lukhas_root,
    ensure_lukhas_structure,
    migrate_deprecated_path,
)

__all__ = [
    "LukhasPathManager",
    "paths", 
    "get_lukhas_root",
    "ensure_lukhas_structure",
    "migrate_deprecated_path",
]