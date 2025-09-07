"""
NIΛS - Non-Intrusive Lambda Symbolic System
Core module initialization

This module contains the core NIΛS functionality including:
- Event bus architecture with dream coordination
- NIAS hub for service orchestration
- Dream recording and symbolic message processing
- Integration with Lambda Products ecosystem
"""
import streamlit as st

from .consent_filter import ConsentFilter, get_consent_filter
from .dream_recorder import DreamRecorder, get_dream_recorder
from .nias_engine import NIASEngine, get_nias_engine
from .nias_hub import NIASHub, get_nias_hub
from .tier_manager import TierManager, get_tier_manager
from .widget_engine import WidgetEngine, get_widget_engine

__version__ = "1.0.0"
__all__ = [
    "ConsentFilter",
    "DreamRecorder",
    "NIASEngine",
    "NIASHub",
    "TierManager",
    "WidgetEngine",
    "get_consent_filter",
    "get_dream_recorder",
    "get_nias_engine",
    "get_nias_hub",
    "get_tier_manager",
    "get_widget_engine",
]
