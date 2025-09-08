"""
LUKHAS AI Validation Tools
=========================

Authentication and system validation utilities.
"""
import logging

logger = logging.getLogger(__name__)

try:
    from .validate_auth_implementation import (
        test_api_key_validation,
        test_password_hashing,
        test_bcrypt_integration
    )
    logger.info("Successfully imported auth validation tools")
    __all__ = ["test_api_key_validation", "test_password_hashing", "test_bcrypt_integration"]
except ImportError as e:
    logger.warning(f"Could not import validation tools: {e}")
    __all__ = []

logger.info(f"validation tools initialized. Available components: {__all__}")