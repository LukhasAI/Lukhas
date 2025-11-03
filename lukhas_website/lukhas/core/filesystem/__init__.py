"""
LUKHAS AI Filesystem Core Module
==============================

Centralized filesystem utilities for LUKHAS AI project.
Provides path management, directory utilities, and project structure helpers.
"""

from .path_manager import (
    LukhasPathManager,
    ensure_lukhas_structure,
    get_lukhas_root,
    migrate_deprecated_path,
    paths,
)

__all__ = [
    "LukhasPathManager",
    "ensure_lukhas_structure",
    "get_lukhas_root",
    "migrate_deprecated_path",
    "paths",
]
