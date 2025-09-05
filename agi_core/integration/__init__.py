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
]