"""
LUKHAS Identity Service Registry
===============================
Coordinates all identity services and registers them with the global registry.
Provides T4 architecture compliant service discovery and initialization.
"""

import logging
from typing import Any, Dict, Optional
from core.registry import register, resolve
from .facades.authentication_facade import AuthenticationFacade
from .services.authenticator_service import ApiKeyAuthenticator, PasswordAuthenticator
from .services.session_service import SessionService
from .services.token_service import TokenService
        try:
            try:
            try:
    try:
import asyncio
    try:

        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(_auto_initialize())
    except RuntimeError:
        # No event loop running, skip auto-initialization
        pass
