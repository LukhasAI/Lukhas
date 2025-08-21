"""
NIAS (Non-Intrusive Ad System) Plugin for Lucas AGI System

A comprehensive modular plugin ecosystem for cross-sector deployment,
integrating DAST, ABAS, and Lucas Systems for safe, consensual interactions.
"""

from .src.core.nias_plugin import NIASPlugin
from .src.core.config import NIASConfig

__version__ = "1.0.0"
__author__ = "Lucas AGI Systems"

__all__ = ["NIASPlugin", "NIASConfig"]
