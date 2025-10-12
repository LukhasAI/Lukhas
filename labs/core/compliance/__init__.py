"""
LUKHAS AI Global Regulatory Compliance Framework
===============================================
Comprehensive compliance system covering all major AI regulations worldwide:

🇪🇺 EU AI Act (2024): Risk-based compliance with 4-tier classification
🇺🇸 NIST AI RMF: Risk management with generative AI profile
🇺🇸 CCPA ADMT: Automated decision-making transparency
🇬🇧 UK Algorithmic Transparency: Public sector AI oversight
🌐 Multi-jurisdictional orchestration and democratic oversight

Components:
- EU AI Act risk classification and compliance engine
- Enhanced privacy compliance (GDPR/CCPA/PIPEDA)
- NIST AI Risk Management Framework integration
- Global compliance orchestration and monitoring
- Democratic oversight and transparency reporting
- Regulatory change management and adaptation

Integration:
- Constellation Framework (⚛️🧠🛡️) compliance alignment
- Constitutional AI regulatory principle enforcement
- Guardian System 2.0 compliance violation detection
- Secure logging for regulatory audit trails
"""
import logging
from typing import Any, Dict, List, Optional

import streamlit as st

# Version information
__version__ = "1.0.0"
__compliance_frameworks__ = [
    "EU_AI_Act_2024",
    "GDPR_2018",
    "CCPA_2020",
    "CCPA_ADMT_2025",
    "NIST_AI_RMF_2023",
    "NIST_AI_RMF_Generative_2024",
    "UK_Algorithmic_Transparency_2024",
    "ISO_27001_2022",
    "SOC2_Type2",
]

# Import core compliance components
try:
    from .compliance_dashboard import ComplianceDashboard
    from .democratic_oversight import DemocraticOversightEngine
    from .eu_ai_act_classifier import AIRiskTier, EUAIActClassifier
    from .global_compliance_manager import GlobalComplianceManager
    from .nist_ai_rmf import AIRiskCategory, NISTAIRiskFramework
    from .privacy_compliance_engine import PrivacyComplianceEngine, PrivacyFramework
    from .regulatory_change_monitor import RegulatoryChangeMonitor

    # Compliance framework status
    COMPLIANCE_COMPONENTS_AVAILABLE = True

except ImportError:
    # Graceful fallback if components not yet implemented
    COMPLIANCE_COMPONENTS_AVAILABLE = False

    # Create placeholder classes for development
    class EUAIActClassifier:
        def __init__(self):
            pass

    class PrivacyComplianceEngine:
        def __init__(self):
            pass

    class NISTAIRiskFramework:
        def __init__(self):
            pass


def get_supported_frameworks() -> list[str]:
    """Get list of supported compliance frameworks"""
    return __compliance_frameworks__.copy()


def get_compliance_status() -> dict[str, Any]:
    """Get current compliance framework status"""
    return {
        "version": __version__,
        "components_available": COMPLIANCE_COMPONENTS_AVAILABLE,
        "supported_frameworks": len(__compliance_frameworks__),
        "frameworks": __compliance_frameworks__,
        "integration_ready": COMPLIANCE_COMPONENTS_AVAILABLE,
    }


# Global compliance framework instance
_global_compliance_manager: Optional["GlobalComplianceManager"] = None


def get_global_compliance_manager():
    """Get or create global compliance manager instance"""
    global _global_compliance_manager

    if not _global_compliance_manager and COMPLIANCE_COMPONENTS_AVAILABLE:
        _global_compliance_manager = GlobalComplianceManager()

    return _global_compliance_manager


# Convenience function for compliance checking
async def check_compliance(ai_system_data: dict[str, Any], jurisdiction: str = "auto") -> dict[str, Any]:
    """
    Convenience function for comprehensive compliance checking

    Args:
        ai_system_data: AI system metadata and configuration
        jurisdiction: Target jurisdiction ("EU", "US", "UK", "CA", "auto")

    Returns:
        Comprehensive compliance assessment results
    """

    if not COMPLIANCE_COMPONENTS_AVAILABLE:
        return {
            "compliance_status": "framework_loading",
            "message": "Compliance framework components are being initialized",
            "supported_frameworks": __compliance_frameworks__,
        }

    compliance_manager = get_global_compliance_manager()
    if compliance_manager:
        return await compliance_manager.comprehensive_compliance_check(ai_system_data, jurisdiction)

    return {"compliance_status": "unavailable", "message": "Global compliance manager not available"}
