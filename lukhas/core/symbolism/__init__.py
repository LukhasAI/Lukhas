"""
LUKHAS AI Symbolic System
Tag-based symbolic processing and methylation
Trinity Framework: ⚛️🧠🛡️

This module provides symbolic tagging and processing capabilities for LUKHAS AI,
including tag scopes, permissions, and methylation models for tag lifecycle management.
"""
import streamlit as st

from .methylation_model import MethylationModel, get_methylation_model
from .tags import SymbolicTag, TagManager, TagPermission, TagScope, get_tag_manager

__all__ = [
    "MethylationModel",
    "SymbolicTag",
    "TagManager",
    "TagPermission",
    "TagScope",
    "get_methylation_model",
    "get_tag_manager",
]