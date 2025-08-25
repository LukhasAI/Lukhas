"""
Common Compliance Manager for Healthcare Providers

This module provides shared compliance functionality across different
regulatory frameworks (GDPR, HIPAA, LOPD, etc.).
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class ComplianceLevel(Enum):
    """Compliance enforcement levels"""
    STRICT = "strict"
    STANDARD = "standard"
    LENIENT = "lenient"

class DataClassification(Enum):
    """Data classification levels"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"  # PHI/PII

class ComplianceFramework(Enum):
    """Supported compliance frameworks"""
    GDPR = "gdpr"
    HIPAA = "hipaa"
    LOPD = "lopd"
    PIPEDA = "pipeda"
    CCPA = "ccpa"

class BaseComplianceManager(ABC):
    """Base class for compliance management"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.compliance_level = ComplianceLevel(config.get('compliance_level', 'standard'))
        self.frameworks = [ComplianceFramework(f) for f in config.get('frameworks', ['gdpr'])]
        self.audit_enabled = config.get('audit_enabled', True)
        
    @abstractmethod
    async def validate_data_processing(self,
                                     data: Dict[str, Any],
                                     purpose: str,
                                     legal_basis: str) -> bool:
        """Validate if data processing is compliant"""
        pass
    
    @abstractmethod
    async def check_consent(self,
                          subject_id: str,
                          purpose: str,
                          data_types: List[str]) -> bool:
        """Check if consent exists for data processing"""
        pass
    
    @abstractmethod
    async def log_data_access(self,
                            user_id: str,
                            subject_id: str,
                            data_accessed: List[str],
                            purpose: str) -> None:
        """Log data access for audit purposes"""
        pass

class UnifiedComplianceManager(BaseComplianceManager):
    """Unified compliance manager supporting multiple frameworks"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.data_retention_days = config.get('data_retention_days', 2555)  # 7 years default
        self.consent_cache = {}
        
    async def validate_data_processing(self,
                                     data: Dict[str, Any],
                                     purpose: str,
                                     legal_basis: str) -> bool:
        """Validate data processing across all configured frameworks"""
        
        # Check each framework's requirements
        for framework in self.frameworks:
            if framework == ComplianceFramework.GDPR:
                if not await self._validate_gdpr_processing(data, purpose, legal_basis):
                    return False
            elif framework == ComplianceFramework.HIPAA:
                if not await self._validate_hipaa_processing(data, purpose, legal_basis):
                    return False
            elif framework == ComplianceFramework.LOPD:
                if not await self._validate_lopd_processing(data, purpose, legal_basis):
                    return False
        
        return True
    
    async def _validate_gdpr_processing(self,
                                      data: Dict[str, Any],
                                      purpose: str,
                                      legal_basis: str) -> bool:
        """Validate GDPR compliance"""
        
        # Check if legal basis is valid
        valid_legal_bases = [
            'consent', 'contract', 'legal_obligation',
            'vital_interests', 'public_task', 'legitimate_interests'
        ]
        
        if legal_basis not in valid_legal_bases:
            logger.warning(f"Invalid GDPR legal basis: {legal_basis}")
            return False
        
        # Check data minimization principle
        if not self._check_data_minimization(data, purpose):
            logger.warning("GDPR data minimization check failed")
            return False
        
        return True
    
    async def _validate_hipaa_processing(self,
                                       data: Dict[str, Any],
                                       purpose: str,
                                       legal_basis: str) -> bool:
        """Validate HIPAA compliance"""
        
        # Check if purpose is permitted under HIPAA
        permitted_purposes = [
            'treatment', 'payment', 'healthcare_operations',
            'public_health', 'research', 'oversight'
        ]
        
        if purpose not in permitted_purposes:
            logger.warning(f"Purpose not permitted under HIPAA: {purpose}")
            return False
        
        return True
    
    async def _validate_lopd_processing(self,
                                      data: Dict[str, Any],
                                      purpose: str,
                                      legal_basis: str) -> bool:
        """Validate Spanish LOPD compliance"""
        
        # LOPD follows similar principles to GDPR
        return await self._validate_gdpr_processing(data, purpose, legal_basis)
    
    def _check_data_minimization(self, data: Dict[str, Any], purpose: str) -> bool:
        """Check if data collection follows minimization principle"""
        
        # Define purpose-specific data requirements
        purpose_data_map = {
            'treatment': ['medical_history', 'current_symptoms', 'medications'],
            'payment': ['insurance_info', 'billing_address', 'service_codes'],
            'appointment': ['contact_info', 'availability', 'medical_specialty']
        }
        
        allowed_fields = purpose_data_map.get(purpose, [])
        
        # Check if collected data exceeds what's necessary
        for field in data.keys():
            if field not in allowed_fields and field not in ['patient_id', 'timestamp']:
                logger.warning(f"Excessive data collection: {field} not needed for {purpose}")
                return False
        
        return True
    
    async def check_consent(self,
                          subject_id: str,
                          purpose: str,
                          data_types: List[str]) -> bool:
        """Check consent across all frameworks"""
        
        # Check cache first
        cache_key = f"{subject_id}:{purpose}:{':'.join(data_types)}"
        if cache_key in self.consent_cache:
            consent_data = self.consent_cache[cache_key]
            if consent_data['expires'] > datetime.utcnow():
                return consent_data['valid']
        
        # Validate consent for each framework
        consent_valid = True
        
        if ComplianceFramework.GDPR in self.frameworks:
            consent_valid &= await self._check_gdpr_consent(subject_id, purpose, data_types)
        
        if ComplianceFramework.HIPAA in self.frameworks:
            consent_valid &= await self._check_hipaa_authorization(subject_id, purpose, data_types)
        
        # Cache result
        self.consent_cache[cache_key] = {
            'valid': consent_valid,
            'expires': datetime.utcnow() + timedelta(hours=1)
        }
        
        return consent_valid
    
    async def _check_gdpr_consent(self,
                                subject_id: str,
                                purpose: str,
                                data_types: List[str]) -> bool:
        """Check GDPR consent requirements"""
        
        # GDPR requires explicit consent for sensitive data
        sensitive_data_types = ['health', 'genetic', 'biometric']
        
        for data_type in data_types:
            if data_type in sensitive_data_types:
                # Must have explicit consent
                if not await self._has_explicit_consent(subject_id, data_type, purpose):
                    return False
        
        return True
    
    async def _check_hipaa_authorization(self,
                                       subject_id: str,
                                       purpose: str,
                                       data_types: List[str]) -> bool:
        """Check HIPAA authorization requirements"""
        
        # HIPAA allows disclosure for TPO without authorization
        if purpose in ['treatment', 'payment', 'healthcare_operations']:
            return True
        
        # Other purposes require authorization
        return await self._has_hipaa_authorization(subject_id, purpose)
    
    async def _has_explicit_consent(self,
                                  subject_id: str,
                                  data_type: str,
                                  purpose: str) -> bool:
        """Check if explicit consent exists"""
        # Implementation would check consent database
        return True  # Placeholder
    
    async def _has_hipaa_authorization(self,
                                     subject_id: str,
                                     purpose: str) -> bool:
        """Check if HIPAA authorization exists"""
        # Implementation would check authorization database
        return True  # Placeholder
    
    async def log_data_access(self,
                            user_id: str,
                            subject_id: str,
                            data_accessed: List[str],
                            purpose: str) -> None:
        """Log data access for audit purposes"""
        
        access_log = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'subject_id': subject_id,
            'data_accessed': data_accessed,
            'purpose': purpose,
            'frameworks': [f.value for f in self.frameworks],
            'compliance_level': self.compliance_level.value
        }
        
        logger.info(f"Data access logged: {access_log}")
        
        # Implementation would store in audit database
        pass