"""
EU AI Act Module
===============

Components for EU AI Act compliance validation and assessment.
"""

from .compliance_validator import (
    AISystemProfile,
    ComplianceAssessment,
    EUAIActValidator,
)

__all__ = ["AISystemProfile", "ComplianceAssessment", "EUAIActValidator"]
