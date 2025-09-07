"""
LUKHAS Tag System
Central registry and management for all system tags
"""
import streamlit as st

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
    "explain_tag",
    "get_decision_tags",
    "get_hormone_tags",
    "get_tag_registry",
]

# Initialize the global registry on import
_registry = get_tag_registry()
