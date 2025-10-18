"""Re-export for bio engine under lukhas.accepted.bio.engine"""
import logging

logger = logging.getLogger(__name__)

try:
    from bio.core import BioEngine
    logger.info("lukhas.accepted.bio.engine -> bio.core")
except Exception:
    try:
        from bio.core import BioEngine
        logger.info("lukhas.accepted.bio.engine -> candidate.bio.core")
    except Exception as e:
        logger.warning(f"Could not wire bio engine: {e}")
        class BioEngine:
            def __init__(self):
                self.status = "fallback"

__all__ = ["BioEngine"]
