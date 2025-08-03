"""

#TAG:governance
#TAG:guardian
#TAG:neuroplastic
#TAG:colony


GDPR Module
==========

Components for GDPR compliance validation and data protection assessment.
"""

from .data_protection_validator import GDPRValidator, DataProcessingActivity, GDPRAssessment

__all__ = ['GDPRValidator', 'DataProcessingActivity', 'GDPRAssessment']
