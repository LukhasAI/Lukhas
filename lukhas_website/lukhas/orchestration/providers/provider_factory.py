#!/usr/bin/env python3
"""
LUKHAS Provider Factory
Production Schema v1.0.0

Factory for creating AI provider clients with feature flag gating and environment configuration.
"""

import logging
import os
from typing import Any, Optional

from .anthropic_client import AnthropicClient
from .base_client import AIProvider, BaseAIClient
from .google_client import GoogleClient
from .mock_client import MockAIClient
from .openai_client import OpenAIClient

logger = logging.getLogger(__name__)

# Global feature flag
ENABLE_PROVIDER_CALLS = os.getenv("LUKHAS_ENABLE_PROVIDER_CALLS", "0") == "1"


def create_provider_client(
    provider: AIProvider,
    config: Optional[dict[str, Any]] = None
) -> BaseAIClient:
    """
    Create an AI provider client with appropriate feature flag gating

    Args:
        provider: The AI provider to create a client for
        config: Optional configuration dictionary for the client

    Returns:
        BaseAIClient: Configured client instance (may be mock if feature flag disabled)
    """
    config = config or {}

    logger.info(f"Creating client for {provider.value} (provider_calls_enabled={ENABLE_PROVIDER_CALLS})")

    if provider == AIProvider.MOCK:
        return MockAIClient(**config)

    elif provider == AIProvider.OPENAI:
        # Check if we have API key and feature flag is enabled
        api_key = config.get("api_key") or os.getenv("OPENAI_API_KEY")
        if ENABLE_PROVIDER_CALLS and api_key:
            logger.info("Creating real OpenAI client")
            return OpenAIClient(**config)
        else:
            logger.info("Creating mock OpenAI client (feature flag disabled or no API key)")
            return MockAIClient(**config)

    elif provider == AIProvider.ANTHROPIC:
        # Check if we have API key and feature flag is enabled
        api_key = config.get("api_key") or os.getenv("ANTHROPIC_API_KEY")
        if ENABLE_PROVIDER_CALLS and api_key:
            logger.info("Creating real Anthropic client")
            return AnthropicClient(**config)
        else:
            logger.info("Creating mock Anthropic client (feature flag disabled or no API key)")
            return MockAIClient(**config)

    elif provider == AIProvider.GOOGLE:
        # Check if we have API key and feature flag is enabled
        api_key = config.get("api_key") or os.getenv("GOOGLE_API_KEY")
        if ENABLE_PROVIDER_CALLS and api_key:
            logger.info("Creating real Google AI client")
            return GoogleClient(**config)
        else:
            logger.info("Creating mock Google AI client (feature flag disabled or no API key)")
            return MockAIClient(**config)

    else:
        logger.warning(f"Unknown provider {provider}, falling back to mock client")
        return MockAIClient(**config)


def get_provider_status() -> dict[str, dict[str, Any]]:
    """
    Get status of all provider configurations

    Returns:
        Dictionary with provider status information
    """
    status = {
        "feature_flag_enabled": ENABLE_PROVIDER_CALLS,
        "providers": {}
    }

    for provider in AIProvider:
        if provider == AIProvider.MOCK:
            status["providers"][provider.value] = {
                "available": True,
                "mode": "mock",
                "api_key_configured": False
            }
            continue

        # Check for API keys
        api_key_env_vars = {
            AIProvider.OPENAI: "OPENAI_API_KEY",
            AIProvider.ANTHROPIC: "ANTHROPIC_API_KEY",
            AIProvider.GOOGLE: "GOOGLE_API_KEY"
        }

        env_var = api_key_env_vars.get(provider)
        api_key_present = bool(os.getenv(env_var)) if env_var else False

        # Determine mode
        if ENABLE_PROVIDER_CALLS and api_key_present:
            mode = "production"
        elif api_key_present:
            mode = "mock_with_key"
        else:
            mode = "mock_no_key"

        status["providers"][provider.value] = {
            "available": True,
            "mode": mode,
            "api_key_configured": api_key_present,
            "env_var": env_var
        }

    return status


def validate_provider_configuration() -> dict[str, Any]:
    """
    Validate provider configuration and return detailed status

    Returns:
        Dictionary with validation results
    """
    validation = {
        "valid": True,
        "issues": [],
        "recommendations": [],
        "provider_status": get_provider_status()
    }

    # Check if feature flag is enabled but no API keys are configured
    if ENABLE_PROVIDER_CALLS:
        configured_providers = [
            provider for provider, info in validation["provider_status"]["providers"].items()
            if info.get("api_key_configured", False)
        ]

        if not configured_providers:
            validation["valid"] = False
            validation["issues"].append(
                "LUKHAS_ENABLE_PROVIDER_CALLS=1 but no API keys configured"
            )
            validation["recommendations"].append(
                "Configure at least one provider API key: OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY"
            )
        else:
            validation["recommendations"].append(
                f"Production mode active with {len(configured_providers)} provider(s): {', '.join(configured_providers)}"
            )
    else:
        validation["recommendations"].append(
            "Mock mode active - set LUKHAS_ENABLE_PROVIDER_CALLS=1 to enable real API calls"
        )

    # Check for partial configurations
    for provider_name, info in validation["provider_status"]["providers"].items():
        if info["mode"] == "mock_with_key":
            validation["recommendations"].append(
                f"{provider_name}: API key configured but feature flag disabled"
            )

    return validation


# Convenience function for creating all standard providers
def create_all_providers(config: Optional[dict[str, dict[str, Any]]] = None) -> dict[AIProvider, BaseAIClient]:
    """
    Create all available providers with given configuration

    Args:
        config: Optional nested configuration dict with provider-specific configs

    Returns:
        Dictionary mapping providers to their configured clients
    """
    config = config or {}
    providers = {}

    for provider in AIProvider:
        provider_config = config.get(provider.value, {})
        providers[provider] = create_provider_client(provider, provider_config)

    return providers
