"""Core Ports - Protocol definitions for dependency injection.

This package contains Protocol (typing.Protocol) definitions that establish
clear contracts for external dependencies. Using Protocols enables:

- **Type-safe dependency injection**: Accept any implementation matching the Protocol
- **Testing with mocks**: Easy to create test doubles without inheritance
- **Loose coupling**: Depend on interfaces, not concrete implementations
- **Lane isolation**: Core can depend on Protocol, not on labs implementations

Available Protocols:
- OpenAIProvider: Interface for OpenAI API clients

Part of T4 quality initiative for maintainable, testable architecture.
"""

from core.ports.openai_provider import (
    ChatMessage,
    ChatCompletionResponse,
    OpenAIProvider,
)

__all__ = [
    "OpenAIProvider",
    "ChatMessage",
    "ChatCompletionResponse",
]
