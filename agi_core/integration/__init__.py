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
    # AGI Modulation
    "AGIModulationBridge",
    "AGIModulationMode",
    "AGIModulationParams",
    "AGIServiceAdapter",
    # Service Bridge
    "AGIServiceBridge",
    "AGIServiceConfiguration",
    # Service Initializer
    "AGIServiceInitializer",
    # Consent/Privacy/Constitutional
    "ConsentPrivacyConstitutionalBridge",
    "ConsentRecord",
    "ConsentStatus",
    "ConstitutionalContext",
    "IntegrationMetrics",
    "IntegrationResult",
    "PrivacyContext",
    "PrivacyLevel",
    "ProcessingContext",
    "ProcessingMode",
    # QI-Bio-AGI Integration
    "QIBioAGIBridge",
    "ServiceMetrics",
    "ServiceRegistration",
    "VocabularyEvent",
    # Vocabulary Integration
    "VocabularyIntegrationService",
    "VocabularyMetrics",
    "agi_initializer",
    "agi_modulation_bridge",
    "agi_service_bridge",
    "apply_signal_modulation",
    "check_operation_governance",
    "consent_privacy_constitutional_bridge",
    "create_module_message",
    "emit_agi_signal",
    "get_agi_modulation_status",
    "get_agi_service",
    "get_governance_status",
    "get_qi_bio_agi_status",
    "get_vocabulary_health",
    "health_check_agi_services",
    "hybrid_process",
    "initialize_agi_services",
    "initialize_agi_system",
    "initialize_qi_bio_agi_systems",
    "log_agi_operation",
    "qi_bio_agi_bridge",
    "register_agi_for_governance",
    "register_agi_for_integration",
    "register_agi_for_modulation",
    "register_agi_service",
    "start_homeostatic_regulation",
    "validate_consent_for_operation",
    "vocabulary_service",
]
