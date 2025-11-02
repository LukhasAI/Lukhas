"""Re-export for bio symbolic processor under accepted.bio.symbolic"""

import logging

logger = logging.getLogger(__name__)

try:
    # Prefer top-level bio
    from bio.symbolic import get_symbolic_processor

    logger.info("accepted.bio.symbolic -> bio.symbolic")
except Exception:
    try:
        from bio.symbolic import get_symbolic_processor

        logger.info("accepted.bio.symbolic -> candidate.bio.symbolic")
    except Exception as e:
        logger.warning(f"Could not wire symbolic processor: {e}")

        def get_symbolic_processor(*a, **k):
            return None


__all__ = ["get_symbolic_processor"]
