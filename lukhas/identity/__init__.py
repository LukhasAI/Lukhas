"""
LUKHAS AI - Identity Module
Identity management and authentication systems

Integrated Components:
- auth: Unified consciousness-aware authentication system
- wallet: WALLET identity management integration  
- qrg: QRG advanced authentication integration
- webauthn: WebAuthn support
- lambda_id: Lambda ID system
"""

# Core identity components
from . import lambda_id, webauthn

# Integrated authentication ecosystem (production-ready)
try:
    from . import auth_integration
    from .wallet import WalletAuthBridge
    from .qrg import QRGAuthBridge
    
    # Authentication integration available
    AUTHENTICATION_AVAILABLE = True
    
except ImportError:
    # Graceful fallback if integration components not available
    AUTHENTICATION_AVAILABLE = False

# Export components
__all__ = [
    'lambda_id',
    'webauthn', 
    'AUTHENTICATION_AVAILABLE'
]

# Add authentication components if available
if AUTHENTICATION_AVAILABLE:
    __all__.extend([
        'auth_integration',
        'WalletAuthBridge', 
        'QRGAuthBridge'
    ])
