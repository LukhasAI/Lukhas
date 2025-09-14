"""
LUKHAS AI - External Service Adapters
====================================

Comprehensive adapters for external services including Gmail, Dropbox,
and OAuth authentication flows with enterprise-grade security.

Copyright (c) 2025 LUKHAS AI. All rights reserved.
"""

# Core OAuth manager is always available
from .oauth_manager import OAuthManager

__all__ = ["OAuthManager"]

# Optional adapters with graceful degradation
try:
    from .gmail_adapter import GmailAdapter
    __all__.append("GmailAdapter")
except ImportError:
    pass

try:
    from .dropbox_adapter import DropboxAdapter
    __all__.append("DropboxAdapter")
except ImportError:
    pass
