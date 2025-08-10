"""

#TAG:memory
#TAG:temporal
#TAG:neuroplastic
#TAG:colony


══════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - MEG OPENAI GUARD
║ OpenAI API protection using MEG.guard decorator
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: meg_openai_guard.py
║ Path: lukhas/ethics/meg_openai_guard.py
║ Version: 1.0.0 | Created: 2025-07-28
║ Authors: LUKHAS AI Core Team | Jules-03 Integration
╠══════════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠══════════════════════════════════════════════════════════════════════════════════
║ Drop-in replacements for OpenAI API calls with MEG.guard protection.
║ Prevents infinite loops, enforces timeouts, and provides ethical oversight.
║
║ Usage:
║   Instead of: openai.ChatCompletion.create(...)
║   Use: meg_chat_completion(...)
║
║ ΛTAG: meg_openai_guard, api_protection, jules03
╚══════════════════════════════════════════════════════════════════════════════════
"""

from typing import Any, Dict, Optional

from core.common import get_logger

from .meg_guard import meg

logger = get_logger(__name__)

# Import OpenAI if available
try:
    import openai

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI not available. MEG guards will return mock responses.")


# Standard timeouts as per Jules-03 implementation
TIMEOUT_CRITICAL = 30  # For critical operations
TIMEOUT_STANDARD = 60  # For standard operations
TIMEOUT_EXTENDED = 120  # For complex operations
TIMEOUT_LONG = 180  # For very long operations


@meg.guard(timeout=TIMEOUT_STANDARD)
def meg_chat_completion(**kwargs) -> Dict[str, Any]:
    """
    MEG-guarded replacement for openai.ChatCompletion.create()

    Standard 60-second timeout. Use for most operations.
    """
    if not OPENAI_AVAILABLE:
        return {
            "choices": [
                {
                    "message": {"content": "Mock response: OpenAI not available"},
                    "finish_reason": "stop",
                }
            ]
        }

    logger.info("MEG.guard: Executing OpenAI chat completion")
    return openai.ChatCompletion.create(**kwargs)


@meg.guard(timeout=TIMEOUT_CRITICAL)
def meg_chat_completion_critical(**kwargs) -> Dict[str, Any]:
    """
    MEG-guarded replacement with 30-second timeout for critical operations.

    Use for operations that must complete quickly.
    """
    if not OPENAI_AVAILABLE:
        return {
            "choices": [
                {
                    "message": {"content": "Mock response: Critical operation"},
                    "finish_reason": "stop",
                }
            ]
        }

    logger.info("MEG.guard: Executing critical OpenAI chat completion")
    return openai.ChatCompletion.create(**kwargs)


@meg.guard(timeout=TIMEOUT_EXTENDED)
def meg_chat_completion_extended(**kwargs) -> Dict[str, Any]:
    """
    MEG-guarded replacement with 120-second timeout for complex operations.

    Use for operations like summarization or complex reasoning.
    """
    if not OPENAI_AVAILABLE:
        return {
            "choices": [
                {
                    "message": {"content": "Mock response: Extended operation"},
                    "finish_reason": "stop",
                }
            ]
        }

    logger.info("MEG.guard: Executing extended OpenAI chat completion")
    return openai.ChatCompletion.create(**kwargs)


@meg.guard(timeout=TIMEOUT_LONG)
def meg_chat_completion_long(**kwargs) -> Dict[str, Any]:
    """
    MEG-guarded replacement with 180-second timeout for very long operations.

    Use for operations like report generation or multi-step reasoning.
    """
    if not OPENAI_AVAILABLE:
        return {
            "choices": [
                {
                    "message": {"content": "Mock response: Long operation"},
                    "finish_reason": "stop",
                }
            ]
        }

    logger.info("MEG.guard: Executing long OpenAI chat completion")
    return openai.ChatCompletion.create(**kwargs)


@meg.guard(timeout=TIMEOUT_STANDARD)
async def meg_chat_completion_async(**kwargs) -> Dict[str, Any]:
    """
    MEG-guarded replacement for openai.ChatCompletion.acreate()

    Async version with standard 60-second timeout.
    """
    if not OPENAI_AVAILABLE:
        return {
            "choices": [
                {
                    "message": {"content": "Mock async response: OpenAI not available"},
                    "finish_reason": "stop",
                }
            ]
        }

    logger.info("MEG.guard: Executing async OpenAI chat completion")
    return await openai.ChatCompletion.acreate(**kwargs)


@meg.guard(timeout=TIMEOUT_LONG)
async def meg_chat_completion_async_long(**kwargs) -> Dict[str, Any]:
    """
    MEG-guarded async replacement with 180-second timeout.

    For long-running async operations.
    """
    if not OPENAI_AVAILABLE:
        return {
            "choices": [
                {
                    "message": {"content": "Mock async response: Long operation"},
                    "finish_reason": "stop",
                }
            ]
        }

    logger.info("MEG.guard: Executing long async OpenAI chat completion")
    return await openai.ChatCompletion.acreate(**kwargs)


# Helper functions for common patterns
def meg_generate_text(
    prompt: str,
    model: str = "gpt-4",
    temperature: float = 0.7,
    max_tokens: int = 1000,
    timeout: int = TIMEOUT_STANDARD,
    **kwargs,
) -> Optional[str]:
    """
    Simplified MEG-guarded text generation.

    Args:
        prompt: The prompt to send
        model: OpenAI model to use
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
        timeout: Custom timeout (defaults to standard)
        **kwargs: Additional OpenAI parameters

    Returns:
        Generated text or None on failure
    """

    @meg.guard(timeout=timeout, fallback_value=None)
    def _generate():
        if not OPENAI_AVAILABLE:
            return "Mock response for: " + prompt[:50] + "..."

        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )
        return response["choices"][0]["message"]["content"]

    return _generate()


def meg_complete_with_system(
    user_prompt: str,
    system_prompt: str = "You are a helpful assistant",
    model: str = "gpt-4",
    timeout: int = TIMEOUT_STANDARD,
    **kwargs,
) -> Optional[str]:
    """
    MEG-guarded completion with system message.

    Args:
        user_prompt: User's prompt
        system_prompt: System instruction
        model: OpenAI model to use
        timeout: Custom timeout
        **kwargs: Additional parameters

    Returns:
        Generated text or None on failure
    """

    @meg.guard(timeout=timeout, fallback_value=None)
    def _complete():
        if not OPENAI_AVAILABLE:
            return f"Mock response with system: {system_prompt[:30]}..."

        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            **kwargs,
        )
        return response["choices"][0]["message"]["content"]

    return _complete()


# Migration helpers for easy adoption
class MEGChatCompletion:
    """Drop-in replacement for openai.ChatCompletion with MEG protection"""

    @staticmethod
    def create(**kwargs):
        """MEG-protected create method"""
        return meg_chat_completion(**kwargs)

    @staticmethod
    async def acreate(**kwargs):
        """MEG-protected async create method"""
        return await meg_chat_completion_async(**kwargs)


def patch_openai_with_meg():
    """
    Monkey-patch OpenAI to use MEG guards globally.

    WARNING: This affects ALL OpenAI calls in the application.
    Use with caution and only if you want system-wide protection.
    """
    if not OPENAI_AVAILABLE:
        logger.warning("Cannot patch OpenAI - module not available")
        return

    # Store originals
    if not hasattr(openai.ChatCompletion, "_original_create"):
        openai.ChatCompletion._original_create = openai.ChatCompletion.create
        openai.ChatCompletion._original_acreate = openai.ChatCompletion.acreate

    # Replace with MEG versions
    openai.ChatCompletion.create = meg_chat_completion
    openai.ChatCompletion.acreate = meg_chat_completion_async

    logger.info("OpenAI has been patched with MEG guards")


def unpatch_openai():
    """Remove MEG patches from OpenAI"""
    if not OPENAI_AVAILABLE:
        return

    if hasattr(openai.ChatCompletion, "_original_create"):
        openai.ChatCompletion.create = openai.ChatCompletion._original_create
        openai.ChatCompletion.acreate = openai.ChatCompletion._original_acreate
        delattr(openai.ChatCompletion, "_original_create")
        delattr(openai.ChatCompletion, "_original_acreate")

    logger.info("OpenAI MEG patches removed")


# Usage examples as per Jules-03 patterns
"""
Example migrations from Jules-03:

1. In agent_self.py:
   OLD: response = openai.ChatCompletion.create(...)
   NEW: response = meg_chat_completion_critical(...)  # 30s timeout

2. In notion_sync.py:
   OLD: response = openai.ChatCompletion.create(...)
   NEW: response = meg_chat_completion_extended(...)  # 120s timeout

3. In ethical_auditor.py:
   OLD: response = await openai.ChatCompletion.acreate(...)
   NEW: response = await meg_chat_completion_async_long(...)  # 180s timeout

4. In lukhas_dna_link.py:
   OLD: response = openai.ChatCompletion.create(...)
   NEW: response = meg_chat_completion(...)  # 60s standard timeout

5. For report generation:
   OLD: response = openai.ChatCompletion.create(...)
   NEW: response = meg_chat_completion_long(...)  # 180s timeout
"""
