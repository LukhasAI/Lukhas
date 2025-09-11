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
        test_authentication_flows,
        test_security_compliance,
        test_session_management,
    )

    logger.info("Successfully imported auth validation tools")
    __all__ = [
        "test_api_key_validation",
        "test_authentication_flows",
        "test_session_management",
        "test_security_compliance",
    ]
except ImportError as e:
    logger.warning(f"Could not import validation tools: {e}")
    __all__ = []

logger.info(f"validation tools initialized. Available components: {__all__}")
