"""
SEEDRA - Secure Emotional & Encrypted Data for Realtime Access

Core consent and data management system for LUKHAS ethical AI operations.
"""

from .seedra_core import ConsentLevel, DataSensitivity, SEEDRACore, get_seedra

__all__ = ["SEEDRACore", "ConsentLevel", "DataSensitivity", "get_seedra"]

__version__ = "1.0.0"
