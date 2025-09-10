"""Re-export for bio hub under lukhas.accepted.bio.hub"""
import logging

logger = logging.getLogger(__name__)

try:
    from bio.hub import *
    logger.info("lukhas.accepted.bio.hub -> bio.hub")
except Exception:
    try:
        from candidate.bio.bio_integration_hub import *
        logger.info("lukhas.accepted.bio.hub -> candidate.bio.bio_integration_hub")
    except Exception as e:
        logger.warning(f"Could not wire bio hub: {e}")

try:
    __all__ = []
except NameError:
    __all__ = []