"""
LUKHAS Tag System
Central registry and management for all system tags
"""

from .registry import (
    TagCategory,
    TagDefinition,
    TagRegistry,
    explain_tag,
    get_decision_tags,
    get_hormone_tags,
    get_tag_registry,
)

__all__ = [
    "TagCategory",
    "TagDefinition",
    "TagRegistry",
    "get_tag_registry",
    "explain_tag",
    "get_decision_tags",
    "get_hormone_tags",
]

# Initialize the global registry on import
_registry = get_tag_registry()
