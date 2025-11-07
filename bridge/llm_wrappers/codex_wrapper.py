#!/usr/bin/env python3
"""
OpenAI Codex API Wrapper for LUKHAS AI Agent Integration
========================================================

OpenAI Codex is a code-understanding AI that can generate, fix, and explain code.
This wrapper integrates Codex capabilities into LUKHAS orchestration workflows.

API Documentation: https://platform.openai.com/docs/api-reference

Features:
- Code generation and completion
- Code explanation and documentation
- Bug fixing and refactoring suggestions
- Multi-language support

Usage:
    from bridge.llm_wrappers.codex_wrapper import CodexClient

    async with CodexClient() as codex:
        # Generate code
        response = await codex.complete(
            prompt="Write a Python function to calculate fibonacci numbers",
            max_tokens=500
        )

        # Fix code
        fixed = await codex.fix_code(
            code="def fib(n): return fib(n-1) + fib(n-2)",
            error="RecursionError: maximum recursion depth exceeded"
        )
"""
from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime
from typing import Optional

import aiohttp
from pydantic import BaseModel, Field

# Import keychain manager for secure API key storage
try:
    from core.security.keychain_manager import KeychainManager
    KEYCHAIN_AVAILABLE = True
except ImportError:
    KEYCHAIN_AVAILABLE = False
    KeychainManager = None

logger = logging.getLogger(__name__)


class CodexConfig(BaseModel):
    """Configuration for OpenAI Codex API client."""

    api_key: str = Field(..., description="OpenAI API key")
    base_url: str = Field(
        default="https://api.openai.com/v1",
        description="OpenAI API base URL"
    )
    model: str = Field(
        default="gpt-4",
        description="Model to use (gpt-4, gpt-3.5-turbo, etc.)"
    )
    timeout: int = Field(default=300, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    temperature: float = Field(
        default=0.3,
        description="Sampling temperature (0.0-1.0, lower = more deterministic)"
    )
    max_tokens: int = Field(
        default=2000,
        description="Maximum tokens in response"
    )


class CodexResponse(BaseModel):
    """Response from Codex API."""

    content: str = Field(..., description="Generated content")
    model: str = Field(..., description="Model used")
    tokens_used: int = Field(..., description="Total tokens consumed")
    finish_reason: str = Field(..., description="Why generation stopped")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CodexClient:
    """
    Async client for OpenAI Codex API integration.

    Provides code generation, bug fixing, refactoring, and documentation
    generation for AI-driven coding workflows.
    """

    def __init__(
        self,
        api_key: str | None = None,
        config: CodexConfig | None = None
    ):
        """
        Initialize Codex API client.

        Args:
            api_key: OpenAI API key (or use OPENAI_API_KEY env var or macOS Keychain)
            config: Optional CodexConfig object for advanced configuration

        Raises:
            ValueError: If no API key can be found

        Note:
            API key lookup order:
            1. Explicit api_key parameter
            2. macOS Keychain (if available)
            3. OPENAI_API_KEY environment variable
            4. Raise ValueError if none found
        """
        if config:
            self.config = config
        else:
            # Try to get API key from multiple sources
            if not api_key:
                # 1. Try macOS Keychain first (most secure)
                if KEYCHAIN_AVAILABLE and KeychainManager:
                    try:
                        api_key = KeychainManager.get_key("OPENAI_API_KEY", fallback_to_env=False)
                        if api_key:
                            logger.debug("Using OpenAI API key from macOS Keychain")
                    except Exception:
                        pass

                # 2. Fallback to environment variable
                if not api_key:
                    api_key = os.getenv("OPENAI_API_KEY")
                    if api_key:
                        logger.debug("Using OpenAI API key from environment variable")

            if not api_key:
                raise ValueError(
                    "OpenAI API key required. Options:\n"
                    "1. Store in macOS Keychain: python scripts/setup_api_keys.py\n"
                    "2. Set environment variable: export OPENAI_API_KEY=your-key\n"
                    "3. Pass api_key parameter to CodexClient()"
                )

            self.config = CodexConfig(api_key=api_key)

        self._session: aiohttp.ClientSession | None = None
        self.logger = logging.getLogger(f"{__name__}.CodexClient")

    async def __aenter__(self) -> CodexClient:
        """Async context manager entry."""
        self._session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            },
            timeout=aiohttp.ClientTimeout(total=self.config.timeout)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._session:
            await self._session.close()

    def _get_session(self) -> aiohttp.ClientSession:
        """Get the aiohttp session, raising error if not initialized."""
        if not self._session:
            raise RuntimeError(
                "CodexClient not initialized. Use 'async with CodexClient() as client:'"
            )
        return self._session

    async def _make_request(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None
    ) -> CodexResponse:
        """
        Make a request to OpenAI Chat Completions API.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt for context
            temperature: Override default temperature
            max_tokens: Override default max_tokens

        Returns:
            CodexResponse with generated content
        """
        session = self._get_session()

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": temperature or self.config.temperature,
            "max_tokens": max_tokens or self.config.max_tokens,
        }

        url = f"{self.config.base_url}/chat/completions"

        for attempt in range(self.config.max_retries):
            try:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        choice = data["choices"][0]

                        return CodexResponse(
                            content=choice["message"]["content"],
                            model=data["model"],
                            tokens_used=data["usage"]["total_tokens"],
                            finish_reason=choice["finish_reason"]
                        )
                    else:
                        error_text = await response.text()
                        self.logger.error(
                            f"OpenAI API error (attempt {attempt + 1}): "
                            f"Status {response.status} - {error_text}"
                        )

                        if response.status in (429, 500, 502, 503, 504) and attempt < self.config.max_retries - 1:
                            # Retry on rate limit or server errors
                            await asyncio.sleep(2 ** attempt)
                            continue

                        raise RuntimeError(
                            f"OpenAI API request failed: {response.status} - {error_text}"
                        )

            except asyncio.TimeoutError:
                self.logger.error(f"Request timeout (attempt {attempt + 1})")
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise

        raise RuntimeError(f"Failed after {self.config.max_retries} retries")

    async def complete(
        self,
        prompt: str,
        temperature: float | None = None,
        max_tokens: int | None = None
    ) -> CodexResponse:
        """
        Generate code completion from prompt.

        Args:
            prompt: Coding task description
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens in response

        Returns:
            CodexResponse with generated code
        """
        system_prompt = (
            "You are an expert software engineer. "
            "Generate clean, efficient, well-documented code. "
            "Follow best practices and include error handling."
        )

        self.logger.info(f"Generating code completion for: {prompt[:100]}...")
        return await self._make_request(prompt, system_prompt, temperature, max_tokens)

    async def fix_code(
        self,
        code: str,
        error: str,
        context: str | None = None
    ) -> CodexResponse:
        """
        Fix code that has errors.

        Args:
            code: Code with errors
            error: Error message or description
            context: Optional additional context

        Returns:
            CodexResponse with fixed code
        """
        system_prompt = (
            "You are an expert debugger. "
            "Fix the provided code to resolve the error. "
            "Explain what was wrong and how you fixed it."
        )

        prompt_parts = [
            f"Code with error:\n```\n{code}\n```",
            f"\nError: {error}"
        ]

        if context:
            prompt_parts.append(f"\nContext: {context}")

        prompt_parts.append("\nProvide the fixed code and explanation.")

        prompt = "\n".join(prompt_parts)

        self.logger.info(f"Fixing code error: {error[:100]}...")
        return await self._make_request(prompt, system_prompt)

    async def refactor(
        self,
        code: str,
        instructions: str
    ) -> CodexResponse:
        """
        Refactor code according to instructions.

        Args:
            code: Code to refactor
            instructions: Refactoring instructions

        Returns:
            CodexResponse with refactored code
        """
        system_prompt = (
            "You are an expert at code refactoring. "
            "Improve code quality while maintaining functionality. "
            "Explain your changes."
        )

        prompt = (
            f"Refactor this code:\n```\n{code}\n```\n\n"
            f"Instructions: {instructions}\n\n"
            f"Provide the refactored code and explanation."
        )

        self.logger.info(f"Refactoring code: {instructions[:100]}...")
        return await self._make_request(prompt, system_prompt)

    async def explain(
        self,
        code: str,
        detail_level: str = "medium"
    ) -> CodexResponse:
        """
        Explain what code does.

        Args:
            code: Code to explain
            detail_level: Level of detail (brief/medium/detailed)

        Returns:
            CodexResponse with code explanation
        """
        detail_instructions = {
            "brief": "Provide a brief 1-2 sentence summary.",
            "medium": "Explain the code's purpose, key logic, and important details.",
            "detailed": "Provide a comprehensive explanation including purpose, logic flow, edge cases, and potential improvements."
        }

        system_prompt = (
            f"You are an expert code reviewer. "
            f"{detail_instructions.get(detail_level, detail_instructions['medium'])}"
        )

        prompt = f"Explain this code:\n```\n{code}\n```"

        self.logger.info(f"Explaining code ({detail_level} detail)...")
        return await self._make_request(prompt, system_prompt)

    async def document(
        self,
        code: str,
        style: str = "google"
    ) -> CodexResponse:
        """
        Generate documentation for code.

        Args:
            code: Code to document
            style: Docstring style (google/numpy/sphinx)

        Returns:
            CodexResponse with documented code
        """
        system_prompt = (
            f"You are an expert at writing code documentation. "
            f"Add comprehensive docstrings in {style} style. "
            f"Include descriptions, parameters, returns, and examples."
        )

        prompt = (
            f"Add documentation to this code:\n```\n{code}\n```\n\n"
            f"Return the code with added docstrings in {style} style."
        )

        self.logger.info(f"Generating {style}-style documentation...")
        return await self._make_request(prompt, system_prompt)


if __name__ == "__main__":
    # Demo usage
    async def demo():
        """Demonstrate Codex wrapper capabilities."""
        print("🤖 Testing LUKHAS Codex Wrapper\n")

        async with CodexClient() as codex:
            # Test code generation
            print("1. Generating code...")
            result = await codex.complete(
                "Write a Python function to check if a number is prime"
            )
            print(f"Generated ({result.tokens_used} tokens):\n{result.content}\n")

            # Test code explanation
            print("2. Explaining code...")
            result = await codex.explain(
                "def fib(n): return n if n <= 1 else fib(n-1) + fib(n-2)",
                detail_level="brief"
            )
            print(f"Explanation:\n{result.content}\n")

        print("✅ Demo complete!")

    # Run demo
    asyncio.run(demo())
