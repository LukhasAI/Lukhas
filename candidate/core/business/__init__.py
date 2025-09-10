"""
NIAS Economic Platform - Business Logic Module.

This module implements the core business logic for the Non-Intrusive
Advertising System (NIAS) with ethical profit sharing and Guardian System integration.
"""
import streamlit as st

# Core business components
from .api_budget_manager import APIBudgetManager
from .consciousness_cache import ConsciousnessCacheManager
from .guardian_integrated_platform import (
    GuardianIntegratedPlatform,
    GuardianSystemAdapter,
)
from .revenue_tracker import RevenueTracker

__all__ = [
    "APIBudgetManager",
    "ConsciousnessCacheManager",
    "GuardianIntegratedPlatform",
    "GuardianSystemAdapter",
    "RevenueTracker",
]
