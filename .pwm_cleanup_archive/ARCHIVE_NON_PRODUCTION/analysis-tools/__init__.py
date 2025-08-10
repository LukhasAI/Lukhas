"""
Analysis-Tools Module
Auto-generated module initialization file
"""

import logging

logger = logging.getLogger(__name__)

try:
    from .analyze_core_isolation import AnalyzeCoreIsolation

    logger.debug("Imported AnalyzeCoreIsolation from .analyze_core_isolation")
except ImportError as e:
    logger.warning(f"Could not import AnalyzeCoreIsolation: {e}")
    AnalyzeCoreIsolation = None

__all__ = [
    "AnalyzeCoreIsolation",
]

# Filter out None values from __all__ if imports failed
__all__ = [name for name in __all__ if globals().get(name) is not None]

logger.info(f"analysis-tools module initialized. Available components: {__all__}")
