"""
GDPR Compliance Module
=====================
Data protection validation for EU General Data Protection Regulation.

Note: This is a minimal implementation for testing infrastructure.
Full GDPR compliance will be implemented in the comprehensive compliance update.
"""

import streamlit as st

from .data_protection_validator import (
    DataCategory,
    DataProcessingActivity,
    GDPRAssessment,
    GDPRValidator,
    LawfulBasis,
    ProcessingPurpose,
)

__all__ = [
    "DataCategory",
    "DataProcessingActivity",
    "GDPRAssessment",
    "GDPRValidator",
    "LawfulBasis",
    "ProcessingPurpose",
]
