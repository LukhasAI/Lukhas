"""

#TAG:governance
#TAG:guardian
#TAG:neuroplastic
#TAG:colony


LUKHAS AI Regulatory Compliance Framework
========================================

Comprehensive AI compliance framework supporting multiple regulatory jurisdictions
including EU AI Act, GDPR, NIST AI RMF, and global compliance standards.

Components:
- EU AI Act compliance validation
- GDPR data protection compliance
- NIST AI Risk Management Framework
- Global regulatory compliance orchestration
- Self-healing compliance monitoring
"""

from .eu_ai_act.compliance_validator import EUAIActValidator
from .gdpr.data_protection_validator import GDPRValidator
from .nist.ai_risk_management import NISTAIRiskManager
from .global_compliance.multi_jurisdiction_engine import GlobalComplianceEngine

__all__ = [
    'EUAIActValidator',
    'GDPRValidator', 
    'NISTAIRiskManager',
    'GlobalComplianceEngine'
]

__version__ = "1.0.0"
__author__ = "LUKHAS AI Compliance Team"
