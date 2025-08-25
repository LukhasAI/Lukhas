"""
Healthcare Provider Interface Templates

Standard interfaces that all healthcare provider implementations must follow.
"""

from .ehr_interface import EHRInterface, ProviderNotificationInterface
from .telemedicine_interface import TelemedicineInterface, TelemedicineSecurityHandler

__all__ = [
    "EHRInterface",
    "ProviderNotificationInterface", 
    "TelemedicineInterface",
    "TelemedicineSecurityHandler"
]