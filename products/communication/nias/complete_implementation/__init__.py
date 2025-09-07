"""
NIAS (Non-Intrusive Ad System) Plugin for Lucas AGI System

A comprehensive modular plugin ecosystem for cross-sector deployment,
integrating DAST, ABAS, and Lucas Systems for safe, consensual interactions.
"""
import streamlit as st

from .src.core.config import NIASConfig
from .src.core.nias_plugin import NIASPlugin

__version__ = "1.0.0"
__author__ = "Lucas AGI Systems"

__all__ = ["NIASConfig", "NIASPlugin"]
