"""
ΛTRACE - Symbolic Activity Logger
=================================

Advanced symbolic logging system for tracking user activities
and system interactions within the LUKHAS ecosystem.

Features:
- Symbolic activity representation
- Privacy-preserving logging
- Pattern recognition integration
- Compliance tracking
"""
import logging

import streamlit as st

from .activity_logger import LambdaTraceLogger as ActivityLogger

__all__ = ["ActivityLogger"]