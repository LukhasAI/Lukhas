#!/usr/bin/env python3

"""
LUKHAS AI Bridge Module
======================

External API connections and interfaces for multi-model orchestration.
Provides secure, feature-flagged access to external services and AI models.

This module enables LUKHAS AI to connect with:
- Multiple AI/LLM providers (OpenAI, Anthropic, Google Gemini, Perplexity)
- Cloud services (Gmail, Google Drive, Dropbox)
- Real-time communication APIs
- Custom protocol bridges

All connections are secured with OAuth2, circuit breakers, and comprehensive telemetry.
"""
import logging
import os
import time
from typing import Any, Optional

import streamlit as st

# Pre-declare bridge-related types for static type-checkers
BridgeWrapper: Optional[Any] = None
MultiModelOrchestrator: Optional[Any] = None
APIBridge: Optional[Any] = None

# Try to import BridgeWrapper at module level
try:
    from .bridge_wrapper import BridgeWrapper
except ImportError:
    BridgeWrapper = None

# Configure module logger
logger = logging.getLogger(__name__)

# Feature flags for Bridge module
BRIDGE_ACTIVE = os.getenv("BRIDGE_ACTIVE", "false").lower() == "true"
BRIDGE_DRY_RUN = os.getenv("BRIDGE_DRY_RUN", "true").lower() == "true"

# Module metadata
MODULE_VERSION = "2.0.0"
MODULE_NAME = "bridge"

# Global instance for singleton pattern
_bridge_wrapper_instance: Optional[Any] = None


def get_bridge_wrapper() -> Optional[Any]:
    """Get the Bridge wrapper instance (singleton)"""
    global _bridge_wrapper_instance
    if _bridge_wrapper_instance is None:
        if BridgeWrapper is not None:
            _bridge_wrapper_instance = BridgeWrapper()
        else:
            logger.warning("BridgeWrapper not available")
            return None
    return _bridge_wrapper_instance


def get_bridge_status() -> dict[str, Any]:
    """Get Bridge module status and capabilities"""
    return {
        "module": MODULE_NAME,
        "version": MODULE_VERSION,
        "active": BRIDGE_ACTIVE,
        "dry_run": BRIDGE_DRY_RUN,
        "capabilities": {
            "llm_providers": ["openai", "anthropic", "gemini", "perplexity"],
            "service_adapters": ["gmail", "drive", "dropbox"],
            "api_support": ["rest", "websocket", "grpc"],
            "security": ["oauth2", "circuit_breakers", "rate_limiting"],
        },
    }


# Import core bridge classes
try:
    from .bridge_wrapper import BridgeWrapper, MultiModelOrchestrator

    # Alias for backward compatibility
    APIBridge = BridgeWrapper
except ImportError as e:
    logger.warning(f"Failed to import bridge classes: {e}")
    BridgeWrapper = None
    MultiModelOrchestrator = None
    APIBridge = None

# Export main interface
__all__ = [
    "BRIDGE_ACTIVE",
    "BRIDGE_DRY_RUN",
    "MODULE_VERSION",
    "APIBridge",  # Alias
    "BridgeWrapper",
    "MultiModelOrchestrator",
    "get_bridge_status",
    "get_bridge_wrapper",
]