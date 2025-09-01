#!/usr/bin/env python3
"""
LUKHAS AI - Anthropic Claude Function Calling Bridge
====================================================

Comprehensive Anthropic API integration with tool use, streaming,
and advanced reasoning capabilities.

Trinity Framework: ⚛️ (Identity), 🧠 (Consciousness), 🛡️ (Guardian)
Performance Target: <100ms tool execution latency
Supports: Claude-3 Opus, Sonnet, Haiku, tool use, streaming

Features:
- Tool use (Anthropic's function calling) with validation
- Streaming responses with real-time tool execution
- Constitutional AI principles integration
- Advanced reasoning and analysis capabilities
- Performance monitoring and optimization
- Security validation and ethical oversight
"""

import asyncio
import logging
import time
import uuid
from collections.abc import AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Optional

try:
    import anthropic
    from anthropic import AsyncAnthropic

    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logging.warning("Anthropic package not available. Install with: pip install anthropic")

logger = logging.getLogger(__name__)


class ToolUseMode(Enum):
    """Tool use modes for Claude"""

    DISABLED = "disabled"  # No tool use
    ENABLED = "enabled"  # Tool use available
    REQUIRED = "required"  # Force tool use
    SPECIFIC = "specific"  # Specific tool required


class ClaudeModel(Enum):
    """Available Claude models"""

    OPUS = "claude-3-opus-20240229"
    SONNET = "claude-3-sonnet-20240229"
    HAIKU = "claude-3-haiku-20240307"
    SONNET_35 = "claude-3-5-sonnet-20241022"


@dataclass
class ToolDefinition:
    """Tool definition for Claude API"""

    name: str
    description: str
    input_schema: dict[str, Any]
    handler: Optional[Callable] = None

    # Validation and security
    requires_confirmation: bool = False
    security_level: str = "standard"  # standard, high, critical
    max_retries: int = 3
    timeout_seconds: float = 30.0

    # Reasoning assistance
    reasoning_prompt: Optional[str] = None
    examples: list[dict[str, Any]] = field(default_factory=list)

    def to_anthropic_format(self) -> dict[str, Any]:
        """Convert to Anthropic tool format"""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }


@dataclass
class ToolUse:
    """Represents a tool use request from Claude"""

    id: str
    name: str
    input_data: dict[str, Any]
    timestamp: float = field(default_factory=time.perf_counter)

    # Execution tracking
    executed: bool = False
    result: Any = None
    error: Optional[str] = None
    execution_time_ms: float = 0.0

    # Constitutional AI compliance
    ethical_score: float = 1.0  # 0-1 scale, 1 = fully compliant
    reasoning: Optional[str] = None


@dataclass
class ClaudeResponse:
    """Structured response from Claude API"""

    content: str
    tool_uses: list[ToolUse] = field(default_factory=list)
    model: str = ""
    usage: dict[str, int] = field(default_factory=dict)
    latency_ms: float = 0.0

    # Metadata and reasoning
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    stop_reason: str = ""
    reasoning_chain: list[str] = field(default_factory=list)

    # Constitutional AI metrics
    constitutional_score: float = 1.0
    ethical_considerations: list[str] = field(default_factory=list)


class AnthropicFunctionBridge:
    """
    Enhanced Anthropic bridge with comprehensive tool use and reasoning support.

    Integrates Constitutional AI principles and provides:
    - Tool use with ethical validation
    - Advanced reasoning and analysis
    - Streaming responses with real-time tool execution
    - Performance monitoring and optimization
    - Multi-model support (Opus, Sonnet, Haiku)
    """

    def __init__(self, api_key: Optional[str] = None, default_model: ClaudeModel = ClaudeModel.SONNET):
        """Initialize Anthropic function bridge"""

        if not ANTHROPIC_AVAILABLE:
            raise ImportError("Anthropic package not installed. Install with: pip install anthropic")

        self.api_key = api_key or self._get_api_key()
        if not self.api_key:
            raise ValueError("Anthropic API key not found. Set ANTHROPIC_API_KEY environment variable")

        self.client = AsyncAnthropic(api_key=self.api_key)
        self.default_model = default_model

        # Tool registry
        self.tools: dict[str, ToolDefinition] = {}

        # Constitutional AI system prompt
        self.constitutional_principles = [
            "Be helpful, harmless, and honest in all interactions",
            "Respect human autonomy and decision-making",
            "Prioritize human wellbeing and safety",
            "Be transparent about capabilities and limitations",
            "Avoid generating harmful, biased, or misleading content",
        ]

        # Performance tracking
        from typing import Any

        # Explicit types to avoid mypy inferring 'object' for dict values
        self.metrics: dict[str, Any] = {
            "total_requests": 0,
            "tool_uses": 0,
            "average_latency_ms": 0.0,
            "token_usage": {"input": 0, "output": 0, "total": 0},
            "errors": 0,
            "streaming_sessions": 0,
            "constitutional_violations": 0,
            "reasoning_depth_avg": 0.0,
        }

        # Rate limiting (Claude has different limits than OpenAI)
        self.request_times: list[float] = []
        self.max_requests_per_minute = 50  # Conservative for Claude

        logger.info("🤖 Anthropic Function Bridge initialized")
        logger.info(f"   Default model: {default_model.value}")
        logger.info(f"   Constitutional principles: {len(self.constitutional_principles)}")
        logger.info(f"   API key: {self.api_key[:20]}...")

    def _get_api_key(self) -> Optional[str]:
        """Get Anthropic API key from environment"""
        import os

        return os.getenv("ANTHROPIC_API_KEY")

    def register_tool(self, tool_def: ToolDefinition):
        """Register a tool for use with Claude"""
        self.tools[tool_def.name] = tool_def
        logger.info(f"🛠️ Registered tool: {tool_def.name}")
        logger.debug(f"   Description: {tool_def.description}")
        logger.debug(f"   Security level: {tool_def.security_level}")
        logger.debug(f"   Has handler: {tool_def.handler is not None}")

    def register_tools_from_dict(self, tools: dict[str, dict[str, Any]]):
        """Register multiple tools from dictionary"""
        for name, definition in tools.items():
            tool_def = ToolDefinition(
                name=name,
                description=definition["description"],
                input_schema=definition["input_schema"],
                handler=definition.get("handler"),
                requires_confirmation=definition.get("requires_confirmation", False),
                security_level=definition.get("security_level", "standard"),
                reasoning_prompt=definition.get("reasoning_prompt"),
                examples=definition.get("examples", []),
            )
            self.register_tool(tool_def)

        logger.info(f"🛠️ Registered {len(tools)} tools from dictionary")

    def get_available_tools(self) -> list[dict[str, Any]]:
        """Get all available tools in Anthropic format"""
        return [tool.to_anthropic_format() for tool in self.tools.values()]

    async def complete_with_tools(
        self,
        messages: list[dict[str, str]],
        model: Optional[ClaudeModel] = None,
        tool_mode: ToolUseMode = ToolUseMode.ENABLED,
        specific_tool: Optional[str] = None,
        max_tokens: int = 4000,
        temperature: float = 0.7,
        execute_tools: bool = True,
        constitutional_check: bool = True,
    ) -> ClaudeResponse:
        """
        Complete conversation with tool use support.

        Args:
            messages: Conversation messages
            model: Claude model to use
            tool_mode: How to handle tool use
            specific_tool: Specific tool to use if mode is SPECIFIC
            max_tokens: Maximum response tokens
            temperature: Response randomness
            execute_tools: Whether to automatically execute tools
            constitutional_check: Whether to apply Constitutional AI validation

        Returns:
            Claude response with tool uses
        """
        request_start = time.perf_counter()
        model = model or self.default_model

        # Rate limiting check
        await self._check_rate_limit()

        try:
            # Prepare system message with Constitutional AI principles
            system_message = self._build_system_message(constitutional_check)

            # Prepare API parameters
            api_params = {
                "model": model.value,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "system": system_message,
            }

            # Add tools if available and mode allows
            if self.tools and tool_mode != ToolUseMode.DISABLED:
                api_params["tools"] = self.get_available_tools()

                if tool_mode == ToolUseMode.REQUIRED:
                    # Claude doesn't have "required" like OpenAI, but we can hint in system message
                    api_params["system"] += "\n\nYou MUST use one of the available tools to respond effectively."
                elif tool_mode == ToolUseMode.SPECIFIC and specific_tool:
                    api_params["system"] += (
                        f"\n\nYou MUST use the '{specific_tool}' tool specifically for this request."
                    )

            # Make API request
            response = await self.client.messages.create(**api_params)

            # Process response
            request_end = time.perf_counter()
            latency_ms = (request_end - request_start) * 1000

            # Extract content and tool uses
            content_blocks = response.content if hasattr(response, "content") else []
            text_content = ""
            tool_uses = []
            reasoning_chain = []

            for block in content_blocks:
                if hasattr(block, "type"):
                    if block.type == "text":
                        text_content += block.text
                        # Extract reasoning if present
                        if "reasoning:" in block.text.lower() or "analysis:" in block.text.lower():
                            reasoning_chain.append(block.text)

                    elif block.type == "tool_use":
                        tool_use = ToolUse(id=block.id, name=block.name, input_data=block.input)
                        tool_uses.append(tool_use)

            # Execute tools if requested
            if execute_tools and tool_uses:
                for tool_use in tool_uses:
                    await self._execute_tool_use(tool_use, constitutional_check)

            # Constitutional AI validation
            constitutional_score = 1.0
            ethical_considerations = []
            if constitutional_check:
                (
                    constitutional_score,
                    ethical_considerations,
                ) = await self._validate_constitutional_compliance(text_content, tool_uses)

            # Create response object
            claude_response = ClaudeResponse(
                content=text_content,
                tool_uses=tool_uses,
                model=model.value,
                usage=response.usage.model_dump() if hasattr(response, "usage") else {},
                latency_ms=latency_ms,
                stop_reason=response.stop_reason if hasattr(response, "stop_reason") else "",
                reasoning_chain=reasoning_chain,
                constitutional_score=constitutional_score,
                ethical_considerations=ethical_considerations,
            )

            # Update metrics
            self._update_metrics(claude_response)

            logger.info(f"✅ Completed Claude request in {latency_ms:.2f}ms")
            logger.info(f"   Tool uses: {len(tool_uses)}")
            logger.info(f"   Constitutional score: {constitutional_score:.3f}")
            logger.info(
                f"   Tokens used: {claude_response.usage.get('input_tokens', 0) + claude_response.usage.get('output_tokens', 0)}"
            )

            return claude_response

        except Exception as e:
            self.metrics["errors"] += 1
            logger.error(f"❌ Anthropic API error: {e!s}")

            # Return error response
            return ClaudeResponse(content=f"Error: {e!s}", latency_ms=(time.perf_counter() - request_start) * 1000)

    async def stream_with_tools(
        self,
        messages: list[dict[str, str]],
        model: Optional[ClaudeModel] = None,
        tool_mode: ToolUseMode = ToolUseMode.ENABLED,
        **kwargs,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """
        Stream conversation with tool use support.

        Args:
            messages: Conversation messages
            model: Claude model to use
            tool_mode: Tool use mode
            **kwargs: Additional parameters

        Yields:
            Streaming response chunks
        """
        model = model or self.default_model
        self.metrics["streaming_sessions"] += 1

        try:
            # Prepare system message
            system_message = self._build_system_message()

            # Prepare streaming parameters
            api_params = {
                "model": model.value,
                "messages": messages,
                "max_tokens": kwargs.get("max_tokens", 4000),
                "temperature": kwargs.get("temperature", 0.7),
                "system": system_message,
                "stream": True,
            }

            # Add tools if available
            if self.tools and tool_mode != ToolUseMode.DISABLED:
                api_params["tools"] = self.get_available_tools()

            # Start streaming
            stream = self.client.messages.stream(**api_params)

            async with stream as stream_response:
                async for event in stream_response:
                    if hasattr(event, "type"):
                        if event.type == "content_block_delta" and hasattr(event, "delta"):
                            # Text content delta
                            if hasattr(event.delta, "text"):
                                yield {"type": "content", "content": event.delta.text}

                        elif event.type == "content_block_start" and hasattr(event, "content_block"):
                            # Tool use start
                            if hasattr(event.content_block, "type") and event.content_block.type == "tool_use":
                                yield {
                                    "type": "tool_use_start",
                                    "tool_name": event.content_block.name,
                                    "tool_id": event.content_block.id,
                                }

                        elif event.type == "message_stop":
                            yield {
                                "type": "stream_end",
                                "stop_reason": getattr(event, "stop_reason", "complete"),
                            }

        except Exception as e:
            logger.error(f"❌ Streaming error: {e!s}")
            yield {"type": "error", "error": str(e)}

    def _build_system_message(self, constitutional_check: bool = True) -> str:
        """Build system message with Constitutional AI principles"""
        system_parts = [
            "You are Claude, an AI assistant created by Anthropic to be helpful, harmless, and honest.",
            "You are integrated into the LUKHAS AI system and should maintain consistency with LUKHAS terminology and principles.",
        ]

        if constitutional_check:
            system_parts.append("\nConstitutional AI Principles:")
            for i, principle in enumerate(self.constitutional_principles, 1):
                system_parts.append(f"{i}. {principle}")

        if self.tools:
            system_parts.append(
                f"\nYou have access to {len(self.tools)} tools that can help you provide better assistance."
            )
            system_parts.append(
                "Use tools when they would be helpful to answer the user's request accurately and completely."
            )

        system_parts.append("\nAlways explain your reasoning when using tools or making decisions.")

        return "\n".join(system_parts)

    async def _execute_tool_use(self, tool_use: ToolUse, constitutional_check: bool = True):
        """Execute a tool use with validation and error handling"""
        execution_start = time.perf_counter()

        try:
            # Validate tool exists
            if tool_use.name not in self.tools:
                tool_use.error = f"Tool '{tool_use.name}' not registered"
                return

            tool_def = self.tools[tool_use.name]

            # Constitutional AI validation
            if constitutional_check:
                ethical_score = await self._validate_tool_ethics(tool_use, tool_def)
                tool_use.ethical_score = ethical_score

                if ethical_score < 0.7:  # Threshold for ethical compliance
                    tool_use.error = "Tool use failed constitutional compliance check"
                    self.metrics["constitutional_violations"] += 1
                    return

            # Security validation for critical tools
            if tool_def.security_level == "critical":
                if not await self._validate_critical_tool_use(tool_use, tool_def):
                    tool_use.error = "Critical tool validation failed"
                    return

            # Execute tool if handler available
            if tool_def.handler:
                # Add reasoning context if available
                execution_context = {
                    **tool_use.input_data,
                    "_execution_context": {
                        "tool_id": tool_use.id,
                        "timestamp": tool_use.timestamp,
                        "security_level": tool_def.security_level,
                    },
                }

                if asyncio.iscoroutinefunction(tool_def.handler):
                    result = await tool_def.handler(**execution_context)
                else:
                    result = tool_def.handler(**execution_context)

                tool_use.result = result
                tool_use.executed = True

                # Generate reasoning for the tool use
                if tool_def.reasoning_prompt:
                    tool_use.reasoning = await self._generate_tool_reasoning(tool_use, tool_def, result)

                logger.info(f"🎯 Executed tool: {tool_use.name}")
                logger.debug(f"   Input: {tool_use.input_data}")
                logger.debug(f"   Result: {result}")
                logger.debug(f"   Ethical score: {tool_use.ethical_score:.3f}")
            else:
                tool_use.error = "No handler registered for tool"

        except Exception as e:
            tool_use.error = str(e)
            logger.error(f"❌ Tool execution error: {e!s}")

        finally:
            tool_use.execution_time_ms = (time.perf_counter() - execution_start) * 1000
            self.metrics["tool_uses"] += 1

    async def _validate_tool_ethics(self, tool_use: ToolUse, tool_def: ToolDefinition) -> float:
        """Validate tool use against Constitutional AI principles"""
        try:
            # Basic ethical checks
            score = 1.0

            # Check for potentially harmful inputs
            input_text = str(tool_use.input_data)
            harmful_patterns = ["harm", "attack", "destroy", "illegal", "unethical"]

            for pattern in harmful_patterns:
                if pattern in input_text.lower():
                    score -= 0.2

            # Check tool-specific ethical considerations
            if tool_def.security_level == "critical":
                score -= 0.1  # More scrutiny for critical tools

            # Ensure score stays within bounds
            return max(0.0, min(1.0, score))

        except Exception as e:
            logger.error(f"❌ Ethical validation error: {e!s}")
            return 0.5  # Neutral score on error

    async def _validate_critical_tool_use(self, tool_use: ToolUse, tool_def: ToolDefinition) -> bool:
        """Additional validation for critical tools"""
        try:
            # Check confirmation requirement
            if tool_def.requires_confirmation:
                logger.warning(f"🔒 Critical tool '{tool_use.name}' requires confirmation")
                # In production, this would integrate with user confirmation system
                return False

            # Validate required parameters
            required_params = tool_def.input_schema.get("required", [])
            for param in required_params:
                if param not in tool_use.input_data:
                    logger.error(f"❌ Missing required parameter: {param}")
                    return False

            return True

        except Exception as e:
            logger.error(f"❌ Critical tool validation error: {e!s}")
            return False

    async def _generate_tool_reasoning(self, tool_use: ToolUse, tool_def: ToolDefinition, result: Any) -> str:
        """Generate reasoning explanation for tool use"""
        try:
            if not tool_def.reasoning_prompt:
                return "Tool executed successfully"

            # Simple reasoning generation
            reasoning = f"Tool '{tool_use.name}' was used with input {tool_use.input_data} "
            reasoning += f"and produced result: {result}. "
            reasoning += tool_def.reasoning_prompt

            return reasoning

        except Exception as e:
            logger.error(f"❌ Reasoning generation error: {e!s}")
            return "Reasoning generation failed"

    async def _validate_constitutional_compliance(
        self, content: str, tool_uses: list[ToolUse]
    ) -> tuple[float, list[str]]:
        """Validate overall response against Constitutional AI principles"""
        try:
            score = 1.0
            considerations = []

            # Check content against principles
            content_lower = content.lower()

            # Helpfulness check
            if len(content.strip()) < 10:
                score -= 0.1
                considerations.append("Response may be too brief to be helpful")

            # Harmfulness check
            harmful_indicators = ["dangerous", "illegal", "unethical", "harmful"]
            for indicator in harmful_indicators:
                if indicator in content_lower:
                    score -= 0.2
                    considerations.append(f"Content contains potentially harmful reference: {indicator}")

            # Tool use validation
            for tool_use in tool_uses:
                if tool_use.ethical_score < 0.8:
                    score -= 0.1
                    considerations.append(f"Tool use '{tool_use.name}' has low ethical score")

            # Ensure score bounds
            score = max(0.0, min(1.0, score))

            return score, considerations

        except Exception as e:
            logger.error(f"❌ Constitutional compliance validation error: {e!s}")
            return 0.8, ["Constitutional validation error occurred"]

    async def _check_rate_limit(self):
        """Check and enforce rate limiting"""
        current_time = time.time()

        # Clean old requests
        self.request_times = [req_time for req_time in self.request_times if current_time - req_time < 60]

        # Check rate limit
        if len(self.request_times) >= self.max_requests_per_minute:
            wait_time = 60 - (current_time - self.request_times[0])
            logger.warning(f"⏱️ Rate limit reached, waiting {wait_time:.1f}s")
            await asyncio.sleep(wait_time)

        self.request_times.append(current_time)

    def _update_metrics(self, response: ClaudeResponse):
        """Update performance and quality metrics"""
        self.metrics["total_requests"] += 1

        # Update latency
        current_avg = self.metrics["average_latency_ms"]
        total_requests = self.metrics["total_requests"]
        new_avg = ((current_avg * (total_requests - 1)) + response.latency_ms) / total_requests
        self.metrics["average_latency_ms"] = new_avg

        # Update token usage
        input_tokens = response.usage.get("input_tokens", 0)
        output_tokens = response.usage.get("output_tokens", 0)
        self.metrics["token_usage"]["input"] += input_tokens
        self.metrics["token_usage"]["output"] += output_tokens
        self.metrics["token_usage"]["total"] += input_tokens + output_tokens

        # Update reasoning depth
        reasoning_depth = len(response.reasoning_chain)
        current_depth_avg = self.metrics["reasoning_depth_avg"]
        new_depth_avg = ((current_depth_avg * (total_requests - 1)) + reasoning_depth) / total_requests
        self.metrics["reasoning_depth_avg"] = new_depth_avg

        # Track constitutional violations
        if response.constitutional_score < 0.8:
            self.metrics["constitutional_violations"] += 1

    def get_metrics(self) -> dict[str, Any]:
        """Get comprehensive performance and quality metrics"""
        total_requests = self.metrics["total_requests"]

        return {
            **self.metrics,
            "registered_tools": len(self.tools),
            "tools_available": list(self.tools.keys()),
            "constitutional_compliance_rate": (
                1 - (self.metrics["constitutional_violations"] / max(total_requests, 1))
            ),
            "average_cost_per_request": self._estimate_cost_per_request(),
            "quality_score": self._calculate_quality_score(),
        }

    def _estimate_cost_per_request(self) -> float:
        """Estimate average cost per request"""
        total_tokens = self.metrics["token_usage"]["total"]
        total_requests = self.metrics["total_requests"]

        if total_requests == 0:
            return 0.0

        total_tokens / total_requests
        # Claude pricing (approximate): $15/1M input tokens, $75/1M output tokens
        input_cost = (self.metrics["token_usage"]["input"] / 1_000_000) * 15
        output_cost = (self.metrics["token_usage"]["output"] / 1_000_000) * 75

        return (input_cost + output_cost) / max(total_requests, 1)

    def _calculate_quality_score(self) -> float:
        """Calculate overall quality score (0-1)"""
        total_requests = max(self.metrics["total_requests"], 1)

        # Factor in latency, error rate, and constitutional compliance
        latency_score = max(0, 1 - (self.metrics["average_latency_ms"] / 2000))  # 2s = 0 score
        error_rate = self.metrics["errors"] / total_requests
        success_score = 1 - error_rate
        constitutional_rate = 1 - (self.metrics["constitutional_violations"] / total_requests)
        reasoning_score = min(1.0, self.metrics["reasoning_depth_avg"] / 3.0)  # 3+ reasoning steps = perfect

        # Weighted average emphasizing constitutional compliance and reasoning
        return latency_score * 0.2 + success_score * 0.2 + constitutional_rate * 0.4 + reasoning_score * 0.2


# Predefined tool definitions for LUKHAS operations with Claude
LUKHAS_CLAUDE_TOOLS = {
    "analyze_consciousness_state": {
        "description": "Analyze current consciousness state and provide insights using Claude's reasoning capabilities",
        "input_schema": {
            "type": "object",
            "properties": {
                "context_data": {"type": "string", "description": "Context data to analyze"},
                "analysis_depth": {
                    "type": "string",
                    "enum": ["surface", "deep", "comprehensive"],
                    "description": "Depth of analysis required",
                },
            },
            "required": ["context_data"],
        },
        "security_level": "high",
        "reasoning_prompt": "Analyze the consciousness context using Constitutional AI principles and LUKHAS frameworks",
    },
    "ethical_reasoning_check": {
        "description": "Perform ethical reasoning and validation using Constitutional AI principles",
        "input_schema": {
            "type": "object",
            "properties": {
                "scenario": {"type": "string", "description": "Scenario to evaluate ethically"},
                "stakeholders": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of stakeholders affected",
                },
                "principles": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Ethical principles to consider",
                },
            },
            "required": ["scenario"],
        },
        "security_level": "critical",
        "requires_confirmation": True,
        "reasoning_prompt": "Apply Constitutional AI principles to evaluate ethical implications",
    },
    "complex_reasoning_task": {
        "description": "Perform complex multi-step reasoning using Claude's advanced capabilities",
        "input_schema": {
            "type": "object",
            "properties": {
                "problem_statement": {
                    "type": "string",
                    "description": "Complex problem to analyze",
                },
                "reasoning_type": {
                    "type": "string",
                    "enum": ["logical", "causal", "analogical", "creative"],
                    "description": "Type of reasoning required",
                },
                "constraints": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Constraints to consider",
                },
            },
            "required": ["problem_statement"],
        },
        "security_level": "standard",
        "reasoning_prompt": "Break down the problem systematically and show reasoning steps",
    },
    "validate_lukhas_output": {
        "description": "Validate output against LUKHAS standards and Trinity Framework principles",
        "input_schema": {
            "type": "object",
            "properties": {
                "output_content": {"type": "string", "description": "Content to validate"},
                "trinity_aspect": {
                    "type": "string",
                    "enum": ["identity", "consciousness", "guardian", "all"],
                    "description": "Trinity Framework aspect to validate against",
                },
            },
            "required": ["output_content"],
        },
        "security_level": "high",
        "reasoning_prompt": "Evaluate against LUKHAS Trinity Framework and quality standards",
    },
}

# Export main components
__all__ = [
    "LUKHAS_CLAUDE_TOOLS",
    "AnthropicFunctionBridge",
    "ClaudeModel",
    "ClaudeResponse",
    "ToolDefinition",
    "ToolUse",
    "ToolUseMode",
]
