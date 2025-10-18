"""
LUKHAS bridge.llm_wrappers package
----------------------------------
Unified API wrappers for multiple language model providers with a consistent
contract and optional provider-specific optimizations.

Copyright (c) 2025 LUKHAS AI. All rights reserved.
"""
# Module imports
import logging
from typing import Any, Optional

import streamlit as st

# Pre-declare wrapper client types for static type-checkers
UnifiedOpenAIClient: Optional[Any] = None
GPTClient: Optional[Any] = None
LukhasOpenAIClient: Optional[Any] = None
OpenAIWrapper: Optional[Any] = None

# Configure module logger
logger = logging.getLogger("ΛTRACE.bridge.llm_wrappers")

# Module constants
MODULE_VERSION = "1.0.0"
MODULE_NAME = "llm_wrappers"

# Import the unified OpenAI client (re-exported in __all__)
try:
    from .unified_openai_client import (
        GPTClient,
        LukhasOpenAIClient,
        OpenAIWrapper,
        UnifiedOpenAIClient,
    )

    logger.info("Successfully imported UnifiedOpenAIClient")
except ImportError as e:
    logger.warning(f"Failed to import UnifiedOpenAIClient: {e}")
    UnifiedOpenAIClient = None
    GPTClient = None
    LukhasOpenAIClient = None
    OpenAIWrapper = None

# Import other wrappers if they exist
optional_imports = []
for wrapper_name, class_name in [
    ("anthropic_wrapper", "AnthropicWrapper"),
    ("gemini_wrapper", "GeminiWrapper"),
    ("perplexity_wrapper", "PerplexityWrapper"),
    ("azure_openai_wrapper", "AzureOpenaiWrapper"),
]:
    try:
        module = __import__(
            f"bridge.llm_wrappers.{wrapper_name}",
            fromlist=[class_name],
        )
        wrapper_class = getattr(module, class_name)
        globals()[class_name] = wrapper_class
        optional_imports.append(class_name)
    except ImportError:
        logger.debug("Optional wrapper %s not available", wrapper_name)
        globals()[class_name] = None

try:
    from .openai_modulated_service import OpenAIModulatedService

    logger.info("OpenAIModulatedService available")
except Exception as e:
    logger.debug(f"OpenAIModulatedService not available: {e}")
    OpenAIModulatedService = None  # type: ignore

__all__ = [
    "GPTClient",
    "LukhasOpenAIClient",
    "OpenAIModulatedService",
    "OpenAIWrapper",
    "UnifiedOpenAIClient",
]

# Mark re-exported symbols as used for static analyzers
try:
    _EXPORTED = (
        UnifiedOpenAIClient,
        GPTClient,
        LukhasOpenAIClient,
        OpenAIWrapper,
        OpenAIModulatedService,
    )
    logger.debug(
        "Exports ready: %s",
        [getattr(x, "__name__", str(x)) for x in _EXPORTED if x is not None],
    )
except Exception:
    pass

"""
Notes
-----
- Exports are re-exported for convenience; imports may appear unused to
    static analyzers (noqa markers are intentional).
"""
