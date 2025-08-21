"""
EHR Interface Template for Health Advisor Provider Plugin

This module defines the required interfaces for EHR system integration.
Providers must implement these interfaces to ensure compatibility.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime


class EHRInterface(ABC):
    """Abstract base class for EHR system integration"""
    
    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the EHR connection with configuration"""
        pass
    
    @abstractmethod
    async def get_patient_record(self, 
                               patient_id: str,
                               record_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """Retrieve patient records from the EHR system"""
        pass
    
    @abstractmethod
    async def update_patient_record(self,
                                  patient_id: str,
                                  data: Dict[str, Any],
                                  update_type: str) -> bool:
        """Update patient records in the EHR system"""
        pass
    
    @abstractmethod
    async def create_encounter(self,
                             patient_id: str,
                             encounter_data: Dict[str, Any]) -> str:
        """Create a new patient encounter record"""
        pass
    
    @abstractmethod
    async def get_provider_schedule(self,
                                  provider_id: str,
                                  start_date: datetime,
                                  end_date: datetime) -> List[Dict[str, Any]]:
        """Get provider's schedule for a date range"""
        pass

    @abstractmethod
    async def validate_credentials(self) -> bool:
        """Validate provider credentials and connection status"""
        pass
    
    @abstractmethod
    async def handle_error(self, error: Exception) -> None:
        """Handle and log EHR-specific errors"""
        pass


class ProviderNotificationInterface(ABC):
    """Interface for provider notifications"""
    
    @abstractmethod
    async def send_notification(self,
                              provider_id: str,
                              notification_type: str,
                              content: Dict[str, Any],
                              priority: str = "normal") -> bool:
        """Send notification to healthcare provider"""
        pass
    
    @abstractmethod
    async def get_notification_preferences(self,
                                        provider_id: str) -> Dict[str, Any]:
        """Get provider's notification preferences"""
        pass