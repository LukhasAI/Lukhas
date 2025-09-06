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

from .agi_modulation_bridge import (
    AGIModulationBridge,
    AGIModulationMode,
    AGIModulationParams,
    agi_modulation_bridge,
    apply_signal_modulation,
    emit_agi_signal,
    get_agi_modulation_status,
    register_agi_for_modulation,
    start_homeostatic_regulation,
)
from .agi_service_bridge import (
    AGIServiceAdapter,
    AGIServiceBridge,
    ServiceMetrics,
    ServiceRegistration,
    agi_service_bridge,
    get_agi_service,
    health_check_agi_services,
    initialize_agi_services,
    register_agi_service,
)
from .agi_service_initializer import (
    AGIServiceConfiguration,
    AGIServiceInitializer,
    agi_initializer,
    initialize_agi_system,
)
from .consent_privacy_constitutional_bridge import (
    ConsentPrivacyConstitutionalBridge,
    ConsentRecord,
    ConsentStatus,
    ConstitutionalContext,
    PrivacyContext,
    PrivacyLevel,
    check_operation_governance,
    consent_privacy_constitutional_bridge,
    get_governance_status,
    register_agi_for_governance,
    validate_consent_for_operation,
)
from .qi_bio_agi_bridge import (
    IntegrationMetrics,
    IntegrationResult,
    ProcessingContext,
    ProcessingMode,
    QIBioAGIBridge,
    get_qi_bio_agi_status,
    hybrid_process,
    initialize_qi_bio_agi_systems,
    qi_bio_agi_bridge,
    register_agi_for_integration,
)
from .vocabulary_integration_service import (
    VocabularyEvent,
    VocabularyIntegrationService,
    VocabularyMetrics,
    create_module_message,
    get_vocabulary_health,
    log_agi_operation,
    vocabulary_service,
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
