import logging
logger = logging.getLogger(__name__)
"""
Governance Module
Auto-generated module initialization file
"""

from candidate.core.common import get_logger

logger = get_logger(__name__)

try:
    from .ethical_drift_governor import EthicalDriftGovernor

    logger.debug("Imported EthicalDriftGovernor from .ethical_drift_governor")
except ImportError as e:
    logger.warning(f"Could not import EthicalDriftGovernor: {e}")
    EthicalDriftGovernor = None

__all__ = [
    "EthicalDriftGovernor",
]

# Filter out None values from __all__ if imports failed
__all__ = [name for name in __all__ if globals().get(name) is not None]

logger.info(f"governance module initialized. Available components: {__all__}")