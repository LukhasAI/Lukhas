"""
Authentication Service Bridge
Bridge to lukhas_website.lukhas.identity.auth_service (single source of truth)

Token verification and authentication services.
Constellation Framework: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian
"""
from lukhas_website.lukhas.identity.auth_service import verify_token

__all__ = ["verify_token"]
