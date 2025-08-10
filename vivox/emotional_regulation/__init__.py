"""
VIVOX.ERN - Emotional Regulation Network
Complete emotional regulation system with full integration capabilities

This module provides:
- Core emotional processing and regulation
- Event bus integration for system-wide communication
- Neuroplastic learning and tag system integration
- Endocrine system integration for biological authenticity
- Comprehensive audit trails and user transparency
"""

from typing import Optional

from .endocrine_integration import (
    VIVOXEndocrineIntegration,
)

# Integration components
from .event_integration import (
    VIVOXERNIntegratedSystem,
    VIVOXEventBusIntegration,
)
from .neuroplastic_integration import (
    VIVOXNeuroplasticLearner,
    VIVOXTagSystemIntegration,
)
from .transparency_audit import (
    TransparencyLevel,
    UserTransparencyReport,
    VIVOXAuditSystem,
)

# Core components
from .vivox_ern_core import (
    EmotionalMemory,
    EmotionalRegulator,
    RegulationResponse,
    RegulationStrategy,
    VADVector,
    VIVOXEmotionalRegulationNetwork,
)


# Main factory function
def create_complete_vivox_ern_system(
    event_bus=None,
    hormone_system=None,
    storage_path: Optional[str] = None,
    enable_neuroplastic_learning: bool = True,
    enable_audit_trails: bool = True,
) -> VIVOXERNIntegratedSystem:
    """
    Create a complete VIVOX.ERN system with all integrations

    Args:
        event_bus: Optional event bus for system integration
        hormone_system: Optional endocrine system for hormone integration
        storage_path: Optional path for audit storage
        enable_neuroplastic_learning: Enable neuroplastic learning features
        enable_audit_trails: Enable comprehensive audit trails

    Returns:
        Fully integrated VIVOX.ERN system
    """

    # Create core VIVOX.ERN
    vivox_ern = VIVOXEmotionalRegulationNetwork()

    # Create event integration
    VIVOXEventBusIntegration(event_bus)

    # Create neuroplastic learning if enabled
    if enable_neuroplastic_learning:
        neuroplastic_learner = VIVOXNeuroplasticLearner()
        tag_integration = VIVOXTagSystemIntegration(neuroplastic_learner)

        # Connect neuroplastic interfaces
        vivox_ern.set_integration_interface(
            "neuroplastic_connector", neuroplastic_learner
        )
        vivox_ern.set_integration_interface("tag_integration", tag_integration)

    # Create endocrine integration if hormone system provided
    if hormone_system:
        endocrine_integration = VIVOXEndocrineIntegration(hormone_system)
        vivox_ern.set_integration_interface("endocrine_system", endocrine_integration)

    # Create audit system if enabled
    if enable_audit_trails:
        audit_system = VIVOXAuditSystem(storage_path)
        vivox_ern.set_integration_interface("audit_system", audit_system)

    # Create integrated system
    integrated_system = VIVOXERNIntegratedSystem(vivox_ern, event_bus)

    return integrated_system


# Convenience exports
__all__ = [
    # Core classes
    "VIVOXEmotionalRegulationNetwork",
    "EmotionalRegulator",
    "VADVector",
    "RegulationStrategy",
    "RegulationResponse",
    "EmotionalMemory",
    # Integration classes
    "VIVOXEventBusIntegration",
    "VIVOXERNIntegratedSystem",
    "VIVOXNeuroplasticLearner",
    "VIVOXTagSystemIntegration",
    "VIVOXEndocrineIntegration",
    "VIVOXAuditSystem",
    "UserTransparencyReport",
    "TransparencyLevel",
    # Factory function
    "create_complete_vivox_ern_system",
]
