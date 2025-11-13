"""
LUKHAS AI API System
===================

Production-ready API interface and endpoint management.
Provides access to the FastAPI backend and API infrastructure.

This module serves as the stable interface to:
- FastAPI application and endpoints
- API authentication and security
- RESTful service interfaces
- API documentation and schemas

Author: LUKHAS AI API Systems
Version: 2.0.0
"""

import logging

# Configure a logger for this module
logger = logging.getLogger(__name__)

# Explicitly import API modules to make them available under the 'api' namespace
# This follows a robust import strategy, avoiding sys.path modifications.
try:
    from . import auth_helpers
except ImportError as e:
    logger.warning(f"Could not import 'auth_helpers': {e}")
    auth_helpers = None

try:
    from . import dreams
except ImportError as e:
    logger.warning(f"Could not import 'dreams': {e}")
    dreams = None

try:
    from . import drift
except ImportError as e:
    logger.warning(f"Could not import 'drift': {e}")
    drift = None

try:
    from . import glyphs
except ImportError as e:
    logger.warning(f"Could not import 'glyphs': {e}")
    glyphs = None

try:
    from . import identity
except ImportError as e:
    logger.warning(f"Could not import 'identity': {e}")
    identity = None

try:
    from . import oidc
except ImportError as e:
    logger.warning(f"Could not import 'oidc': {e}")
    oidc = None

try:
    from . import routing_admin
except ImportError as e:
    logger.warning(f"Could not import 'routing_admin': {e}")
    routing_admin = None

try:
    from . import system_endpoints
except ImportError as e:
    logger.warning(f"Could not import 'system_endpoints': {e}")
    system_endpoints = None


# Define the public API of this module
__all__ = [
    "auth_helpers",
    "dreams",
    "drift",
    "glyphs",
    "identity",
    "oidc",
    "routing_admin",
    "system_endpoints",
]

__version__ = "2.0.0"

# Note: This module provides a stable, explicit interface to the API ecosystem.
# The actual API implementations are co-located in this directory.
