"""
Infrastructure Module
Auto-generated module initialization file
"""

import logging

import streamlit as st

logger = logging.getLogger(__name__)

try:
    from .base_node import BaseNode

    logger.debug("Imported BaseNode from .base_node")
except ImportError as e:
    logger.warning(f"Could not import BaseNode: {e}")
    BaseNode = None

try:
    from .node_collection import NodeCollection

    logger.debug("Imported NodeCollection from .node_collection")
except ImportError as e:
    logger.warning(f"Could not import NodeCollection: {e}")
    NodeCollection = None

try:
    from .node_registry import NodeRegistry

    logger.debug("Imported NodeRegistry from .node_registry")
except ImportError as e:
    logger.warning(f"Could not import NodeRegistry: {e}")
    NodeRegistry = None

try:
    from .node_manager import NodeManager

    logger.debug("Imported NodeManager from .node_manager")
except ImportError as e:
    logger.warning(f"Could not import NodeManager: {e}")
    NodeManager = None

__all__ = [
    "BaseNode",
    "NodeCollection",
    "NodeManager",
    "NodeRegistry",
]

# Filter out None values from __all__ if imports failed
__all__ = [name for name in __all__ if globals().get(name) is not None]

logger.info(f"infrastructure module initialized. Available components: {__all__}")
