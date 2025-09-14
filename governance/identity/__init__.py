"""
LUKHAS Governance Identity Module - Bridge Package
=================================================

This module provides identity management capabilities for the LUKHAS AI system.
The actual implementation is in lukhas.governance.identity, this is a bridge
module for backwards compatibility with candidate modules.
"""

import logging

logger = logging.getLogger(__name__)

try:
    # Import from the actual implementation
    from lukhas.governance.identity import *
    from lukhas.governance.identity import (
        auth,
        auth_backend,
        auth_integration,
        auth_service,
        connector,
        extreme_performance_connector,
        interface,
        lambda_id,
        passkey,
        qrg,
        wallet,
        webauthn,
    )
except ImportError as e:
    # If lukhas.governance.identity is not available, log and provide a minimal stub
    logger.warning(f"Could not import lukhas.governance.identity: {e}")

    # Provide minimal stub interface for development
    class IdentityStub:
        """Stub class for identity functionality when actual module unavailable"""

        pass
