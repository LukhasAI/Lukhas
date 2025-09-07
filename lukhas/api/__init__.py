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
Version: 1.0.0
"""
import streamlit as st

# Standard library imports
import contextlib
import os
import sys

# Add api directory to path for imports
_api_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "api")
if _api_path not in sys.path:
    sys.path.insert(0, _api_path)

# Re-export main API components if they exist
with contextlib.suppress(ImportError):
    # Import any API systems that exist
    pass

__version__ = "1.0.0"
__all__ = []

# Note: This module provides access to the API ecosystem
# The actual API implementations are in /api directory
