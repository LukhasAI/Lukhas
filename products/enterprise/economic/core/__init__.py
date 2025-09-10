"""
Economic Intelligence and Market Manipulation Module

This module provides advanced economic analysis, market intelligence,
and strategic positioning capabilities for the LUKHAS AI system.

Part of the Trinity Framework (⚛️🧠🛡️)
"""

from typing import TYPE_CHECKING

import streamlit as st

if TYPE_CHECKING:
    from .market_intelligence.economic_reality_manipulator import (
        EconomicRealityManipulator,
    )

__all__ = ["EconomicRealityManipulator"]
