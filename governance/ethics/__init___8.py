"""

#TAG:governance
#TAG:ethics
#TAG:neuroplastic
#TAG:colony


ΛGOVERNOR - Global Ethical Arbitration Engine for LUKHAS AGI

This module provides the centralized oversight system for ethical escalations
and interventions across the LUKHAS AGI consciousness mesh.
"""

from .lambda_governor import (
    # Core classes
    LambdaGovernor,
    EscalationSignal,
    ArbitrationResponse,
    InterventionExecution,

    # Enums
    ActionDecision,
    EscalationSource,
    EscalationPriority,

    # Convenience functions
    create_lambda_governor,
    create_escalation_signal
)

__all__ = [
    'LambdaGovernor',
    'EscalationSignal',
    'ArbitrationResponse',
    'InterventionExecution',
    'ActionDecision',
    'EscalationSource',
    'EscalationPriority',
    'create_lambda_governor',
    'create_escalation_signal'
]

# Version info
__version__ = '1.0.0'
__author__ = 'CLAUDE-CODE'

# CLAUDE CHANGELOG
# - Created __init__.py for ethics.governor module # CLAUDE_EDIT_v0.1
# - Exported all public classes and functions # CLAUDE_EDIT_v0.1
# - Added module documentation and version info # CLAUDE_EDIT_v0.1