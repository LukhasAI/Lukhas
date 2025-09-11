"""
MATRIZ - LUKHAS AI Trace and Analysis System

This module provides trace analysis and API endpoints for the LUKHAS AI system.
Part of the MATRIZ-R1 Stream B implementation.
"""

__version__ = "1.0.0"
__author__ = "LUKHAS AI Development Team"

# Make traces_router available at package level
from .traces_router import router

__all__ = ["router"]
