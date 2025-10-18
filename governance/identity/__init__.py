"""
LUKHAS Governance Identity Module - Bridge Package
=================================================

This module provides identity management capabilities for the LUKHAS AI system.
The actual implementation is in governance.identity, this is a bridge
module for backwards compatibility with candidate modules.
"""

import logging

logger = logging.getLogger(__name__)

try:
    # Import from the actual implementation
    from governance.identity import *
    from governance.identity import (
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
    # If governance.identity is not available, log and provide a minimal stub
    logger.warning(f"Could not import governance.identity: {e}")

    # Provide minimal stub interface for development
    class IdentityStub:
        """Stub class for identity functionality when actual module unavailable"""

        pass
