"""
LUKHAS AI - External Service Adapters
====================================

Comprehensive adapters for external services including Gmail, Dropbox,
and OAuth authentication flows with enterprise-grade security.

Copyright (c) 2025 LUKHAS AI. All rights reserved.
"""

from .oauth_manager import OAuthManager

# Optional imports (may have missing dependencies)
try:
    from .dropbox_adapter import DropboxAdapter
    DROPBOX_AVAILABLE = True
except ImportError:
    DropboxAdapter = None
    DROPBOX_AVAILABLE = False

try:
    from .gmail_adapter import GmailAdapter
    GMAIL_AVAILABLE = True
except ImportError:
    GmailAdapter = None
    GMAIL_AVAILABLE = False

# TODO: ExternalServiceRouter not yet implemented
# from .external_service_router import ExternalServiceRouter

__all__ = ["OAuthManager"]
if DROPBOX_AVAILABLE:
    __all__.append("DropboxAdapter")
if GMAIL_AVAILABLE:
    __all__.append("GmailAdapter")
