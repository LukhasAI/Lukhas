"""
LUKHAS Governance Identity Module - Bridge Package
=================================================

This module provides identity management capabilities for the LUKHAS AI system.
The actual implementation is in lukhas.governance.identity, this is a bridge
module for backwards compatibility with candidate modules.
"""

try:
    # Import from the actual implementation
    from lukhas.governance.identity import *
    from lukhas.governance.identity import (
        auth_backend,
        connector,
        extreme_performance_connector,
        interface,
    )
    
    # Import auth_integration from the correct location
    try:
        from lukhas.identity import auth_integration
    except ImportError:
        auth_integration = None
    
    # Import other auth components (if they exist)
    try:
        from lukhas.identity import auth_service
    except ImportError:
        auth_service = None
    
    # Auth module alias
    auth = auth_backend
    
    # Legacy identity components (provide stubs if not available)
    try:
        from lukhas.identity import lambda_id
    except ImportError:
        lambda_id = None
    
    try:
        from lukhas.identity import passkey
    except ImportError:
        passkey = None
    
    try:
        from lukhas.identity import qrg
    except ImportError:
        qrg = None
    
    try:
        from lukhas.identity import wallet
    except ImportError:
        wallet = None
    
    try:
        from lukhas.identity import webauthn
    except ImportError:
        webauthn = None

except ImportError as e:
    # If lukhas.governance.identity is not available, provide error message
    import warnings

    warnings.warn(f"Could not import lukhas.governance.identity: {e}", ImportWarning, stacklevel=2)

    # Provide minimal stub interface for development
    class IdentityStub:
        """Stub class for identity functionality when actual module unavailable"""

        pass
