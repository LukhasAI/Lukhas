"""
SEEDRA - Secure Emotional & Encrypted Data for Realtime Access

Core consent and data management system for LUKHAS ethical AI operations.
"""
import time

import streamlit as st

from .seedra_core import ConsentLevel, DataSensitivity, SEEDRACore, get_seedra

__all__ = ["ConsentLevel", "DataSensitivity", "SEEDRACore", "get_seedra"]

__version__ = "1.0.0"
