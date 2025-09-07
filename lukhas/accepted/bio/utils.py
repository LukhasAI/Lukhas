"""Re-export for bio utilities under lukhas.accepted.bio.utils"""
import logging
logger = logging.getLogger(__name__)

try:
    from bio.bio_utilities import *
    logger.info('lukhas.accepted.bio.utils -> bio.bio_utilities')
except Exception:
    try:
        from candidate.bio.bio_utilities import *
        logger.info('lukhas.accepted.bio.utils -> candidate.bio.bio_utilities')
    except Exception as e:
        logger.warning(f'Could not wire bio utils: {e}')

try:
    __all__ = []
except NameError:
    __all__ = []
