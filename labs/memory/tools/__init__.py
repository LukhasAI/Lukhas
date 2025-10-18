import logging

logger = logging.getLogger(__name__)
"""
Tools Module
Auto-generated module initialization file
"""

from fromfromfromcandidate.core.common import (
    GuardianRejectionError,
    LukhasError,
    MemoryDriftError,
)

from core.common import get_logger

logger = get_logger(__name__)

try:
    from .memory_drift_auditor import MemoryDriftAuditor

    logger.debug("Imported MemoryDriftAuditor from .memory_drift_auditor")
except ImportError as e:
    logger.warning(f"Could not import MemoryDriftAuditor: {e}")
    MemoryDriftAuditor = None

try:
    from .lambda_archive_inspector import LambdaArchiveInspector

    logger.debug("Imported LambdaArchiveInspector from .lambda_archive_inspector")
except ImportError as e:
    logger.warning(f"Could not import LambdaArchiveInspector: {e}")
    LambdaArchiveInspector = None

try:
    from .lambda_vault_scan import LambdaVaultScan

    logger.debug("Imported LambdaVaultScan from .lambda_vault_scan")
except ImportError as e:
    logger.warning(f"Could not import LambdaVaultScan: {e}")
    LambdaVaultScan = None

__all__ = [
    "LambdaArchiveInspector",
    "LambdaVaultScan",
    "MemoryDriftAuditor",
]

# Filter out None values from __all__ if imports failed
__all__ = [name for name in __all__ if globals().get(name) is not None]

logger.info(f"tools module initialized. Available components: {__all__}")
