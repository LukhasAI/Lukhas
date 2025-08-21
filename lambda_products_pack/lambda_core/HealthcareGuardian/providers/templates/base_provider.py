"""
Base Healthcare Provider Interface

This module defines the base interface that all healthcare provider
implementations must extend. It provides common functionality and
enforces consistent interface across different healthcare systems.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ProviderConfig:
    """Base configuration for healthcare providers"""
    provider_id: str
    provider_name: str
    provider_type: str  # public, private, integrated
    region: str
    environment: str  # production, sandbox
    api_version: str
    compliance_mode: str  # strict, standard

@dataclass
class SecurityConfig:
    """Security configuration"""
    encryption_algorithm: str
    key_rotation_days: int
    session_timeout_minutes: int
    mfa_required: bool
    audit_retention_days: int

class BaseHealthcareProvider(ABC):
    """Base class for all healthcare provider implementations"""
    
    def __init__(self, 
                 provider_config: ProviderConfig,
                 security_config: SecurityConfig):
        """Initialize the healthcare provider interface"""
        self.config = provider_config
        self.security = security_config
        self.initialize_logging()
    
    def initialize_logging(self):
        """Set up provider-specific logging"""
        log_format = (
            f"%(asctime)s - {self.config.provider_id} - "
            "%(name)s - %(levelname)s - %(message)s"
        )
        logging.basicConfig(format=log_format, level=logging.INFO)
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize provider-specific connections and resources"""
        pass
    
    @abstractmethod
    async def validate_credentials(self) -> bool:
        """Validate provider credentials"""
        pass
    
    @abstractmethod
    async def get_patient_record(self,
                               patient_id: str,
                               record_types: Optional[List[str]] = None
                               ) -> Dict[str, Any]:
        """Retrieve patient records"""
        pass
    
    @abstractmethod
    async def update_patient_record(self,
                                  patient_id: str,
                                  data: Dict[str, Any],
                                  update_type: str) -> bool:
        """Update patient records"""
        pass
    
    @abstractmethod
    async def verify_coverage(self,
                            patient_id: str,
                            service_code: str) -> Dict[str, Any]:
        """Verify insurance coverage"""
        pass
    
    @abstractmethod
    async def submit_claim(self,
                         claim_data: Dict[str, Any]) -> str:
        """Submit insurance claim"""
        pass
    
    @abstractmethod
    async def get_claim_status(self,
                             claim_id: str) -> Dict[str, Any]:
        """Get status of submitted claim"""
        pass
    
    @abstractmethod
    async def schedule_appointment(self,
                                patient_id: str,
                                provider_id: str,
                                appointment_data: Dict[str, Any]) -> str:
        """Schedule a medical appointment"""
        pass
    
    @abstractmethod
    async def get_provider_schedule(self,
                                  provider_id: str,
                                  start_date: datetime,
                                  end_date: datetime) -> List[Dict[str, Any]]:
        """Get provider's schedule"""
        pass
    
    @abstractmethod
    async def handle_error(self, error: Exception) -> None:
        """Handle provider-specific errors"""
        pass
    
    def log_audit_event(self,
                       event_type: str,
                       user_id: str,
                       resource_id: str,
                       action: str,
                       details: Optional[Dict[str, Any]] = None) -> None:
        """Log audit event"""
        event_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "provider_id": self.config.provider_id,
            "event_type": event_type,
            "user_id": user_id,
            "resource_id": resource_id,
            "action": action,
            "environment": self.config.environment,
            "details": details or {}
        }
        logger.info(f"Audit event: {event_data}")
    
    def validate_data(self,
                     data: Dict[str, Any],
                     required_fields: List[str]) -> bool:
        """Validate data against required fields"""
        missing_fields = [
            field for field in required_fields 
            if field not in data or data[field] is None
        ]
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")
        return True