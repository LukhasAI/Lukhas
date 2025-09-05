"""
AGI Integration Services
=======================

Integration services for connecting AGI capabilities with existing LUKHAS systems.

This module provides:
- Vocabulary integration and cross-system symbolic communication
- Service bridges for AGI-LUKHAS system connections
- Translation layers for legacy system compatibility
- Unified logging and monitoring integration
- Complete AGI service lifecycle management

Phase 2A: Core Integrations - COMPLETE
Created: 2025-09-05
Status: ACTIVE
"""

from .vocabulary_integration_service import (
    VocabularyIntegrationService,
    VocabularyEvent,
    VocabularyMetrics,
    vocabulary_service,
    log_agi_operation,
    create_module_message,
    get_vocabulary_health,
)

from .agi_service_bridge import (
    AGIServiceBridge,
    AGIServiceAdapter,
    ServiceRegistration,
    ServiceMetrics,
    agi_service_bridge,
    register_agi_service,
    get_agi_service,
    initialize_agi_services,
    health_check_agi_services,
)

from .agi_service_initializer import (
    AGIServiceInitializer,
    AGIServiceConfiguration,
    agi_initializer,
    initialize_agi_system,
)

from .qi_bio_agi_bridge import (
    QIBioAGIBridge,
    ProcessingMode,
    ProcessingContext,
    IntegrationResult,
    IntegrationMetrics,
    qi_bio_agi_bridge,
    hybrid_process,
    register_agi_for_integration,
    initialize_qi_bio_agi_systems,
    get_qi_bio_agi_status,
)

from .agi_modulation_bridge import (
    AGIModulationBridge,
    AGIModulationMode,
    AGIModulationParams,
    agi_modulation_bridge,
    register_agi_for_modulation,
    emit_agi_signal,
    apply_signal_modulation,
    get_agi_modulation_status,
    start_homeostatic_regulation,
)

from .consent_privacy_constitutional_bridge import (
    ConsentPrivacyConstitutionalBridge,
    ConsentStatus,
    PrivacyLevel,
    ConsentRecord,
    PrivacyContext,
    ConstitutionalContext,
    consent_privacy_constitutional_bridge,
    register_agi_for_governance,
    check_operation_governance,
    validate_consent_for_operation,
    get_governance_status,
)

__all__ = [
    # Vocabulary Integration
    "VocabularyIntegrationService",
    "VocabularyEvent", 
    "VocabularyMetrics",
    "vocabulary_service",
    "log_agi_operation",
    "create_module_message", 
    "get_vocabulary_health",
    
    # Service Bridge
    "AGIServiceBridge",
    "AGIServiceAdapter", 
    "ServiceRegistration",
    "ServiceMetrics",
    "agi_service_bridge",
    "register_agi_service",
    "get_agi_service",
    "initialize_agi_services",
    "health_check_agi_services",
    
    # Service Initializer
    "AGIServiceInitializer",
    "AGIServiceConfiguration", 
    "agi_initializer",
    "initialize_agi_system",
    
    # QI-Bio-AGI Integration
    "QIBioAGIBridge",
    "ProcessingMode",
    "ProcessingContext", 
    "IntegrationResult",
    "IntegrationMetrics",
    "qi_bio_agi_bridge",
    "hybrid_process",
    "register_agi_for_integration",
    "initialize_qi_bio_agi_systems",
    "get_qi_bio_agi_status",
    
    # AGI Modulation
    "AGIModulationBridge",
    "AGIModulationMode",
    "AGIModulationParams",
    "agi_modulation_bridge",
    "register_agi_for_modulation",
    "emit_agi_signal",
    "apply_signal_modulation",
    "get_agi_modulation_status",
    "start_homeostatic_regulation",
    
    # Consent/Privacy/Constitutional
    "ConsentPrivacyConstitutionalBridge",
    "ConsentStatus",
    "PrivacyLevel",
    "ConsentRecord",
    "PrivacyContext", 
    "ConstitutionalContext",
    "consent_privacy_constitutional_bridge",
    "register_agi_for_governance",
    "check_operation_governance",
    "validate_consent_for_operation",
    "get_governance_status",
]