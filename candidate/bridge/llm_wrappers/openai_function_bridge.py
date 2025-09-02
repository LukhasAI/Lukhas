#!/usr/bin/env python3
"""
LUKHAS AI - OpenAI Function Calling Bridge
==========================================

Comprehensive OpenAI API integration with function calling, streaming,
and multi-model orchestration support.

Trinity Framework: ⚛️ (Identity), 🧠 (Consciousness), 🛡️ (Guardian)
Performance Target: <100ms function call latency
Supports: GPT-4, GPT-3.5-turbo, function calling, streaming

Features:
- Function calling with tool validation
- Streaming responses with Server-Sent Events
- Rate limiting and retry mechanisms
- Cost optimization and token management
- Performance monitoring and metrics
- Security validation and input sanitization
"""

import asyncio
import json
import logging
import time
import uuid
from collections.abc import AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Optional

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class FunctionCallMode(Enum):
    """Function calling modes"""

    NONE = "none"  # No function calling
    AUTO = "auto"  # Automatic function selection
    REQUIRED = "required"  # Force function calling
    SPECIFIC = "specific"  # Specific function required


@dataclass
class FunctionDefinition:
    """Function definition for OpenAI API"""

    name: str
    description: str
    parameters: dict[str, Any]
    handler: Optional[Callable] = None

    # Validation settings
    requires_confirmation: bool = False
    security_level: str = "standard"  # standard, high, critical
    max_retries: int = 3
    timeout_seconds: float = 30.0

    def to_openai_format(self) -> dict[str, Any]:
        """Convert to OpenAI function format"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


@dataclass
class FunctionCall:
    """Represents a function call request"""

    id: str
    name: str
    arguments: dict[str, Any]
    timestamp: float = field(default_factory=time.perf_counter)

    # Execution tracking
    executed: bool = False
    result: Any = None
    error: Optional[str] = None
    execution_time_ms: float = 0.0


@dataclass
class OpenAIResponse:
    """Structured response from OpenAI API"""

    content: str
    function_calls: list[FunctionCall] = field(default_factory=list)
    model: str = ""
    usage: dict[str, int] = field(default_factory=dict)
    latency_ms: float = 0.0

    # Metadata
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    finish_reason: str = ""


class OpenAIFunctionBridge:
    """
    Enhanced OpenAI bridge with comprehensive function calling support.

    Provides:
    - Function calling with validation and security
    - Streaming responses for real-time interactions
    - Performance monitoring and optimization
    - Rate limiting and cost management
    - Multi-model support (GPT-4, GPT-3.5-turbo)
    """

    def __init__(
        self, api_key: Optional[str] = None, default_model: str = "gpt-4-1106-preview"
    ):
        """Initialize OpenAI function bridge"""

        self.api_key = api_key or self._get_api_key()
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.default_model = default_model

        # Function registry
        self.functions: dict[str, FunctionDefinition] = {}

        # Performance tracking
        from typing import Any

        # explicitly type metrics to avoid mypy inferring 'object' for values
        self.metrics: dict[str, Any] = {
            "total_requests": 0,
            "function_calls": 0,
            "average_latency_ms": 0.0,
            "token_usage": {"input": 0, "output": 0, "total": 0},
            "errors": 0,
            "streaming_sessions": 0,
        }

        # Rate limiting
        self.request_times: list[float] = []
        self.max_requests_per_minute = 60

        logger.info("🚀 OpenAI Function Bridge initialized")
        logger.info(f"   Default model: {default_model}")
        logger.info(f"   API key: {self.api_key[:20] if self.api_key else 'None'}...")

    def _get_api_key(self) -> Optional[str]:
        """Get OpenAI API key from environment"""
        import os

        return os.getenv("OPENAI_API_KEY")

    def register_function(self, func_def: FunctionDefinition):
        """Register a function for calling"""
        self.functions[func_def.name] = func_def
        logger.info(f"📋 Registered function: {func_def.name}")
        logger.debug(f"   Description: {func_def.description}")
        logger.debug(f"   Security level: {func_def.security_level}")

    def register_functions_from_dict(self, functions: dict[str, dict[str, Any]]):
        """Register multiple functions from dictionary"""
        for name, definition in functions.items():
            func_def = FunctionDefinition(
                name=name,
                description=definition["description"],
                parameters=definition["parameters"],
                handler=definition.get("handler"),
                requires_confirmation=definition.get("requires_confirmation", False),
                security_level=definition.get("security_level", "standard"),
            )
            self.register_function(func_def)

        logger.info(f"📋 Registered {len(functions)} functions from dictionary")

    def get_available_functions(self) -> list[dict[str, Any]]:
        """Get all available functions in OpenAI format"""
        return [func.to_openai_format() for func in self.functions.values()]

    async def complete_with_functions(
        self,
        messages: list[dict[str, str]],
        model: Optional[str] = None,
        function_mode: FunctionCallMode = FunctionCallMode.AUTO,
        specific_function: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        execute_functions: bool = True,
    ) -> OpenAIResponse:
        """
        Complete chat with function calling support.

        Args:
            messages: Conversation messages
            model: Model to use (defaults to default_model)
            function_mode: How to handle function calling
            specific_function: Specific function to call if mode is SPECIFIC
            max_tokens: Maximum response tokens
            temperature: Response randomness
            execute_functions: Whether to automatically execute functions

        Returns:
            OpenAI response with function calls
        """
        request_start = time.perf_counter()
        model = model or self.default_model

        # Rate limiting check
        await self._check_rate_limit()

        try:
            # Prepare function calling parameters
            api_params = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }

            # Add function calling if functions available and mode allows
            if self.functions and function_mode != FunctionCallMode.NONE:
                api_params["tools"] = self.get_available_functions()

                if function_mode == FunctionCallMode.REQUIRED:
                    api_params["tool_choice"] = "required"
                elif function_mode == FunctionCallMode.SPECIFIC and specific_function:
                    api_params["tool_choice"] = {
                        "type": "function",
                        "function": {"name": specific_function},
                    }
                # AUTO mode uses default behavior

            # Make API request
            response = await self.client.chat.completions.create(**api_params)

            # Process response
            request_end = time.perf_counter()
            latency_ms = (request_end - request_start) * 1000

            # Extract content and function calls
            message = response.choices[0].message
            content = message.content or ""
            function_calls = []

            # Process tool calls (function calls)
            if hasattr(message, "tool_calls") and message.tool_calls:
                for tool_call in message.tool_calls:
                    if tool_call.type == "function":
                        try:
                            arguments = json.loads(tool_call.function.arguments)
                        except json.JSONDecodeError:
                            arguments = {}

                        func_call = FunctionCall(
                            id=tool_call.id,
                            name=tool_call.function.name,
                            arguments=arguments,
                        )
                        function_calls.append(func_call)

            # Execute functions if requested
            if execute_functions and function_calls:
                for func_call in function_calls:
                    await self._execute_function_call(func_call)

            # Create response object
            openai_response = OpenAIResponse(
                content=content,
                function_calls=function_calls,
                model=model,
                usage=response.usage.model_dump() if response.usage else {},
                latency_ms=latency_ms,
                finish_reason=response.choices[0].finish_reason or "",
            )

            # Update metrics
            self._update_metrics(openai_response)

            logger.info(f"✅ Completed request in {latency_ms:.2f}ms")
            logger.info(f"   Function calls: {len(function_calls)}")
            logger.info(
                f"   Tokens used: {openai_response.usage.get('total_tokens', 0)}"
            )

            return openai_response

        except Exception as e:
            self.metrics["errors"] += 1
            logger.error(f"❌ OpenAI API error: {e!s}")

            # Return error response
            return OpenAIResponse(
                content=f"Error: {e!s}",
                latency_ms=(time.perf_counter() - request_start) * 1000,
            )

    async def stream_with_functions(
        self,
        messages: list[dict[str, str]],
        model: Optional[str] = None,
        function_mode: FunctionCallMode = FunctionCallMode.AUTO,
        **kwargs,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """
        Stream chat completion with function calling support.

        Args:
            messages: Conversation messages
            model: Model to use
            function_mode: Function calling mode
            **kwargs: Additional parameters

        Yields:
            Streaming response chunks
        """
        model = model or self.default_model
        self.metrics["streaming_sessions"] += 1

        try:
            # Prepare streaming parameters
            api_params = {
                "model": model,
                "messages": messages,
                "stream": True,
                **kwargs,
            }

            # Add function calling if available
            if self.functions and function_mode != FunctionCallMode.NONE:
                api_params["tools"] = self.get_available_functions()

                if function_mode == FunctionCallMode.REQUIRED:
                    api_params["tool_choice"] = "required"

            # Start streaming
            stream = await self.client.chat.completions.create(**api_params)

            async for chunk in stream:
                if chunk.choices:
                    choice = chunk.choices[0]

                    # Yield content delta
                    if choice.delta.content:
                        yield {
                            "type": "content",
                            "content": choice.delta.content,
                            "finish_reason": choice.finish_reason,
                        }

                    # Yield function call data
                    if hasattr(choice.delta, "tool_calls") and choice.delta.tool_calls:
                        for tool_call in choice.delta.tool_calls:
                            yield {
                                "type": "function_call",
                                "function_name": (
                                    tool_call.function.name
                                    if tool_call.function
                                    else None
                                ),
                                "arguments": (
                                    tool_call.function.arguments
                                    if tool_call.function
                                    else None
                                ),
                            }

        except Exception as e:
            logger.error(f"❌ Streaming error: {e!s}")
            yield {"type": "error", "error": str(e)}

    async def _execute_function_call(self, func_call: FunctionCall):
        """Execute a function call with validation and error handling"""
        execution_start = time.perf_counter()

        try:
            # Validate function exists
            if func_call.name not in self.functions:
                func_call.error = f"Function '{func_call.name}' not registered"
                return

            func_def = self.functions[func_call.name]

            # Security validation
            if func_def.security_level == "critical":
                # Additional security checks for critical functions
                if not await self._validate_critical_function_call(func_call, func_def):
                    func_call.error = "Critical function validation failed"
                    return

            # Execute function if handler available
            if func_def.handler:
                if asyncio.iscoroutinefunction(func_def.handler):
                    result = await func_def.handler(**func_call.arguments)
                else:
                    result = func_def.handler(**func_call.arguments)

                func_call.result = result
                func_call.executed = True

                logger.info(f"🎯 Executed function: {func_call.name}")
                logger.debug(f"   Arguments: {func_call.arguments}")
                logger.debug(f"   Result: {result}")
            else:
                func_call.error = "No handler registered for function"

        except Exception as e:
            func_call.error = str(e)
            logger.error(f"❌ Function execution error: {e!s}")

        finally:
            func_call.execution_time_ms = (time.perf_counter() - execution_start) * 1000
            self.metrics["function_calls"] += 1

    async def _validate_critical_function_call(
        self, func_call: FunctionCall, func_def: FunctionDefinition
    ) -> bool:
        """Validate critical function calls with additional security"""
        try:
            # Check if confirmation is required
            if func_def.requires_confirmation:
                logger.warning(
                    f"🔒 Critical function '{func_call.name}' requires confirmation"
                )
                # In a real implementation, this would prompt for user confirmation
                return False

            # Validate argument types and values
            required_params = func_def.parameters.get("required", [])
            for param in required_params:
                if param not in func_call.arguments:
                    logger.error(f"❌ Missing required parameter: {param}")
                    return False

            return True

        except Exception as e:
            logger.error(f"❌ Critical function validation error: {e!s}")
            return False

    async def _check_rate_limit(self):
        """Check and enforce rate limiting"""
        current_time = time.time()

        # Clean old requests (older than 1 minute)
        self.request_times = [
            req_time for req_time in self.request_times if current_time - req_time < 60
        ]

        # Check if we're hitting rate limit
        if len(self.request_times) >= self.max_requests_per_minute:
            wait_time = 60 - (current_time - self.request_times[0])
            logger.warning(f"⏱️ Rate limit reached, waiting {wait_time:.1f}s")
            await asyncio.sleep(wait_time)

        # Record this request
        self.request_times.append(current_time)

    def _update_metrics(self, response: OpenAIResponse):
        """Update performance metrics"""
        self.metrics["total_requests"] += 1

        # Update average latency
        current_avg = self.metrics["average_latency_ms"]
        total_requests = self.metrics["total_requests"]
        new_avg = (
            (current_avg * (total_requests - 1)) + response.latency_ms
        ) / total_requests
        self.metrics["average_latency_ms"] = new_avg

        # Update token usage
        for key in ["input", "output", "total"]:
            if f"{key}_tokens" in response.usage:
                self.metrics["token_usage"][key] += response.usage[f"{key}_tokens"]

    def get_metrics(self) -> dict[str, Any]:
        """Get comprehensive performance metrics"""
        return {
            **self.metrics,
            "registered_functions": len(self.functions),
            "functions_available": list(self.functions.keys()),
            "average_cost_per_request": self._estimate_cost_per_request(),
            "performance_score": self._calculate_performance_score(),
        }

    def _estimate_cost_per_request(self) -> float:
        """Estimate average cost per request"""
        total_tokens = self.metrics["token_usage"]["total"]
        total_requests = self.metrics["total_requests"]

        if total_requests == 0:
            return 0.0

        avg_tokens_per_request = total_tokens / total_requests
        # Rough cost estimate for GPT-4 ($0.03/1K input + $0.06/1K output)
        estimated_cost = (avg_tokens_per_request / 1000) * 0.045  # Average rate

        return estimated_cost

    def _calculate_performance_score(self) -> float:
        """Calculate overall performance score (0-1)"""
        # Factors: latency, success rate, function execution rate
        latency_score = max(
            0, 1 - (self.metrics["average_latency_ms"] / 1000)
        )  # 1s = 0 score
        error_rate = self.metrics["errors"] / max(self.metrics["total_requests"], 1)
        success_score = 1 - error_rate

        # Weighted average
        return latency_score * 0.4 + success_score * 0.6


# Predefined function definitions for common LUKHAS operations
LUKHAS_FUNCTION_DEFINITIONS = {
    "get_memory_fold": {
        "description": "Retrieve a specific memory fold from lukhas_memory system",
        "parameters": {
            "type": "object",
            "properties": {
                "fold_id": {
                    "type": "string",
                    "description": "Unique identifier for the memory fold",
                },
                "include_context": {
                    "type": "boolean",
                    "description": "Whether to include contextual information",
                },
            },
            "required": ["fold_id"],
        },
        "security_level": "standard",
    },
    "consciousness_query": {
        "description": "Query LUKHAS consciousness system for insights or decisions",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The consciousness query to process",
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "description": "Query priority level",
                },
            },
            "required": ["query"],
        },
        "security_level": "high",
    },
    "emotional_assessment": {
        "description": "Assess emotional context and provide VAD (Valence, Arousal, Dominance) analysis",
        "parameters": {
            "type": "object",
            "properties": {
                "text_input": {
                    "type": "string",
                    "description": "Text to analyze for emotional content",
                },
                "context_weight": {
                    "type": "number",
                    "description": "Weight of contextual factors (0-1)",
                },
            },
            "required": ["text_input"],
        },
        "security_level": "standard",
    },
    "guardian_validate": {
        "description": "Validate content through LUKHAS Guardian ethical oversight system",
        "parameters": {
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "Content to validate"},
                "validation_level": {
                    "type": "string",
                    "enum": ["basic", "standard", "strict"],
                    "description": "Level of validation required",
                },
            },
            "required": ["content"],
        },
        "security_level": "critical",
        "requires_confirmation": True,
    },
}

# Export main components
__all__ = [
    "LUKHAS_FUNCTION_DEFINITIONS",
    "FunctionCall",
    "FunctionCallMode",
    "FunctionDefinition",
    "OpenAIFunctionBridge",
    "OpenAIResponse",
]
