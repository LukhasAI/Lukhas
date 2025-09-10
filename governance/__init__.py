"""
LUKHAS Governance Module - Root Package
======================================

This module provides governance capabilities for the LUKHAS AI system.
The actual implementation is in lukhas.governance, this is a bridge module
for backwards compatibility with candidate modules.
"""

try:
    # Import from the actual implementation
    from lukhas.governance import *
    from lukhas.governance import (
        auth_cross_module_integration,
        auth_guardian_integration,
        auth_integration_system,
        consent_ledger,
        ethics,
        guardian,
        identity,
        security,
    )
except ImportError:
    # If lukhas.governance is not available, provide minimal interface
    pass