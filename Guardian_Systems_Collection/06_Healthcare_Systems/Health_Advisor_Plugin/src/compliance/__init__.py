"""
Core compliance module for Health Advisor Plugin.
Handles compliance requirements across different healthcare regulations.
"""

from typing import Dict, Any, List, Optional
from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ComplianceFramework(Enum):
    """Supported compliance frameworks"""
    HIPAA = "HIPAA"
    GDPR = "GDPR"
    HITECH = "HITECH"
    NHS = "NHS_DSP"  # NHS Data Security and Protection
    RGPD = "RGPD"    # Spanish/EU implementation
    BDSG = "BDSG"    # German Federal Data Protection Act

class DataCategory(Enum):
    """Categories of protected health information"""
    PHI = "PHI"
    PII = "PII"
    PAYMENT = "PAYMENT"
    GENETIC = "GENETIC"
    BIOMETRIC = "BIOMETRIC"

class ComplianceManager:
    """
    Main compliance management class that coordinates various compliance
    requirements and ensures data handling follows all applicable regulations.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize compliance manager with configuration
        
        Args:
            config: Configuration dictionary containing compliance settings
        """
        self.config = config
        self.active_frameworks = [
            ComplianceFramework(framework)
            for framework in config.get('frameworks', ['HIPAA', 'GDPR'])
        ]
        self._init_compliance_modules()
        logger.info(f"Compliance Manager initialized with frameworks: {self.active_frameworks}")
    
    def _init_compliance_modules(self):
        """Initialize specific compliance modules based on active frameworks"""
        from .hipaa import HIPAACompliance
        from .gdpr import GDPRCompliance
        from .audit import AuditManager
        
        self.hipaa = HIPAACompliance(self.config.get('hipaa', {}))
        self.gdpr = GDPRCompliance(self.config.get('gdpr', {}))
        self.audit = AuditManager(self.config.get('audit', {}))
    
    async def validate_data_handling(
        self,
        data: Any,
        category: DataCategory,
        operation: str,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Validate if data handling complies with all active frameworks
        
        Args:
            data: The data being handled
            category: Category of the data (PHI, PII, etc.)
            operation: Type of operation (read, write, transfer, etc.)
            context: Additional context about the operation
        
        Returns:
            bool: Whether the operation is compliant
        """
        for framework in self.active_frameworks:
            if not await self._check_framework_compliance(
                framework, data, category, operation, context
            ):
                return False
        return True
    
    async def _check_framework_compliance(
        self,
        framework: ComplianceFramework,
        data: Any,
        category: DataCategory,
        operation: str,
        context: Optional[Dict[str, Any]]
    ) -> bool:
        """Check compliance for a specific framework"""
        if framework == ComplianceFramework.HIPAA:
            return await self.hipaa.validate_operation(data, category, operation, context)
        elif framework == ComplianceFramework.GDPR:
            return await self.gdpr.validate_operation(data, category, operation, context)
        # Add other framework checks as needed
        return True
    
    async def log_compliance_event(
        self,
        event_type: str,
        details: Dict[str, Any],
        severity: str = "INFO"
    ) -> None:
        """Log a compliance-related event"""
        await self.audit.log_event(
            timestamp=datetime.utcnow(),
            event_type=event_type,
            details=details,
            severity=severity
        )
    
    async def get_retention_policy(
        self,
        data_category: DataCategory
    ) -> Dict[str, Any]:
        """Get retention policy for a data category"""
        policies = []
        for framework in self.active_frameworks:
            if framework == ComplianceFramework.HIPAA:
                policies.append(await self.hipaa.get_retention_policy(data_category))
            elif framework == ComplianceFramework.GDPR:
                policies.append(await self.gdpr.get_retention_policy(data_category))
        
        # Return the most stringent policy
        return max(policies, key=lambda x: x.get('retention_period', 0))
    
    async def validate_data_transfer(
        self,
        source_region: str,
        target_region: str,
        data_categories: List[DataCategory],
        transfer_method: str
    ) -> Dict[str, Any]:
        """Validate if data transfer between regions is compliant"""
        results = {
            'allowed': True,
            'requirements': [],
            'restrictions': []
        }
        
        for framework in self.active_frameworks:
            if framework == ComplianceFramework.GDPR:
                gdpr_result = await self.gdpr.validate_transfer(
                    source_region, target_region, data_categories, transfer_method
                )
                results['requirements'].extend(gdpr_result.get('requirements', []))
                results['restrictions'].extend(gdpr_result.get('restrictions', []))
                if not gdpr_result.get('allowed', True):
                    results['allowed'] = False
        
        return results
