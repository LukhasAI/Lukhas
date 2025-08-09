"""
══════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - UNIFIED OPENAI CLIENT
║ Unified OpenAI integration combining all client features
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: unified_openai_client.py
║ Path: lukhas/bridge/llm_wrappers/unified_openai_client.py
║ Version: 2.0.0 | Created: 2025-07-27
║ Authors: LUKHAS AI Integration Team
╠══════════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠══════════════════════════════════════════════════════════════════════════════════
║ This unified client combines features from all three previous OpenAI clients:
║ • Async support and conversation management (from gpt_client.py)
║ • Comprehensive documentation and error handling (from openai_wrapper.py)
║ • Task-specific configurations (from openai_client.py)
║ • Environment variable based configuration (no macOS keychain dependency)
║
║ Key Features:
║ • Async/await support for all operations
║ • Conversation state management
║ • Task-specific model selection
║ • Streaming response support
║ • Function calling capabilities
║ • Token optimization
║ • Comprehensive error handling with retries
║ • Environment-based configuration
╚══════════════════════════════════════════════════════════════════════════════════
"""

import os
import logging
from core.common import get_logger
import json
import uuid
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, List, AsyncIterator, Union
from dataclasses import dataclass, asdict
import aiohttp
from openai import AsyncOpenAI, OpenAI

logger = logging.getLogger("ΛTRACE.bridge.unified_openai")


@dataclass
class ConversationMessage:
    """Represents a single message in a conversation"""
    role: str  # "system", "user", "assistant", "function"
    content: str
    timestamp: str
    message_id: str
    metadata: Optional[Dict[str, Any]] = None
    function_call: Optional[Dict[str, Any]] = None


@dataclass
class ConversationState:
    """Represents the state of a conversation"""
    conversation_id: str
    session_id: str
    user_id: str
    messages: List[ConversationMessage]
    context: Dict[str, Any]
    created_at: str
    updated_at: str
    total_tokens: int = 0
    max_context_length: int = 8000  # Conservative limit for GPT-4


class UnifiedOpenAIClient:
    """
    Unified OpenAI client for LUKHAS AGI system.
    Combines best features from all previous implementations.
    """

    # Task-specific model configurations
    TASK_MODELS = {
        'reasoning': 'gpt-4',
        'creativity': 'gpt-4',
        'consciousness': 'gpt-4',
        'memory': 'gpt-3.5-turbo',
        'ethics': 'gpt-4',
        'coding': 'gpt-4',
        'voice_processing': 'gpt-3.5-turbo',
        'symbolic_reasoning': 'gpt-4',
        'general': 'gpt-3.5-turbo'
    }

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the unified OpenAI client.

        Args:
            api_key: Optional API key. If not provided, will use OPENAI_API_KEY env var.
        """
        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")

        # Store organization and project IDs for reference
        self.organization_id = os.getenv('OPENAI_ORGANIZATION_ID')
        self.project_id = os.getenv('OPENAI_PROJECT')

        # Initialize clients using auto-detection from environment
        # The OpenAI library will automatically use:
        # - OPENAI_API_KEY
        # - OPENAI_ORGANIZATION
        # - OPENAI_PROJECT (if available)

        # For sync client
        if api_key:
            # If API key was explicitly provided, use it
            self.client = OpenAI(api_key=api_key)
            self.async_client = AsyncOpenAI(api_key=api_key)
        else:
            # Otherwise use full auto-detection
            self.client = OpenAI()
            self.async_client = AsyncOpenAI()

        # Conversation management
        self.conversations: Dict[str, ConversationState] = {}

        # Default parameters
        self.default_temperature = 0.7
        self.default_max_tokens = 2000
        self.retry_attempts = 3
        self.retry_delay = 1.0

        logger.info(f"UnifiedOpenAIClient initialized with org: {self.organization_id}")

    # Conversation Management

    def create_conversation(self, user_id: str, session_id: str) -> str:
        """Create a new conversation"""
        conversation_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        self.conversations[conversation_id] = ConversationState(
            conversation_id=conversation_id,
            session_id=session_id,
            user_id=user_id,
            messages=[],
            context={},
            created_at=now,
            updated_at=now
        )

        logger.info(f"Created conversation {conversation_id} for user {user_id}")
        return conversation_id

    def add_message(self, conversation_id: str, role: str, content: str,
                   function_call: Optional[Dict] = None) -> ConversationMessage:
        """Add a message to a conversation"""
        if conversation_id not in self.conversations:
            raise ValueError(f"Conversation {conversation_id} not found")

        message = ConversationMessage(
            role=role,
            content=content,
            timestamp=datetime.utcnow().isoformat(),
            message_id=str(uuid.uuid4()),
            function_call=function_call
        )

        self.conversations[conversation_id].messages.append(message)
        self.conversations[conversation_id].updated_at = datetime.utcnow().isoformat()

        return message

    def get_conversation_messages(self, conversation_id: str,
                                 max_tokens: int = 4000) -> List[Dict[str, Any]]:
        """Get conversation messages formatted for OpenAI API"""
        if conversation_id not in self.conversations:
            raise ValueError(f"Conversation {conversation_id} not found")

        messages = []
        token_count = 0

        # Add messages in reverse order until we hit token limit
        for msg in reversed(self.conversations[conversation_id].messages):
            msg_dict = {
                "role": msg.role,
                "content": msg.content
            }
            if msg.function_call:
                msg_dict["function_call"] = msg.function_call

            # Rough token estimation (4 chars per token)
            msg_tokens = len(json.dumps(msg_dict)) // 4
            if token_count + msg_tokens > max_tokens:
                break

            messages.insert(0, msg_dict)
            token_count += msg_tokens

        return messages

    # Core API Methods

    async def chat_completion(
        self,
        messages: Union[List[Dict[str, Any]], str],
        model: Optional[str] = None,
        task: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        functions: Optional[List[Dict[str, Any]]] = None,
        function_call: Optional[Union[str, Dict[str, str]]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, Dict[str, str]]] = None,
        **kwargs
    ) -> Union[Dict[str, Any], AsyncIterator[Dict[str, Any]]]:
        """
        Create a chat completion with the OpenAI API.

        Args:
            messages: List of message dicts or a single prompt string
            model: Model to use (defaults to task-specific or general)
            task: Task type for model selection
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            functions: Function definitions for function calling
            function_call: Function calling behavior
            **kwargs: Additional parameters for the API

        Returns:
            Response dict or async iterator for streaming
        """
        # Handle string prompt
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]

        # Select model based on task
        if model is None:
            model = self.TASK_MODELS.get(task, self.TASK_MODELS['general'])

        # Set defaults
        temperature = temperature if temperature is not None else self.default_temperature
        max_tokens = max_tokens if max_tokens is not None else self.default_max_tokens

        # Prepare request parameters
        params = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }

        # Add function calling parameters if provided
        if functions:
            params["functions"] = functions
        if function_call is not None:
            params["function_call"] = function_call
            
        # Add tools (newer function calling API) if provided
        if tools:
            params["tools"] = tools
        if tool_choice is not None:
            params["tool_choice"] = tool_choice

        # Execute request with retries
        for attempt in range(self.retry_attempts):
            try:
                if stream:
                    return await self.async_client.chat.completions.create(
                        **params,
                        stream=True
                    )
                else:
                    response = await self.async_client.chat.completions.create(**params)
                    return response.model_dump()

            except Exception as e:
                logger.error(f"OpenAI API error (attempt {attempt + 1}): {e}")
                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                else:
                    raise

    def chat_completion_sync(
        self,
        messages: Union[List[Dict[str, Any]], str],
        model: Optional[str] = None,
        task: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Synchronous version of chat_completion"""
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]

        if model is None:
            model = self.TASK_MODELS.get(task, self.TASK_MODELS['general'])

        temperature = temperature if temperature is not None else self.default_temperature
        max_tokens = max_tokens if max_tokens is not None else self.default_max_tokens

        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )

        return response.model_dump()

    # Task-Specific Methods

    async def reasoning_task(self, prompt: str, context: Optional[Dict] = None) -> str:
        """Execute a reasoning task with appropriate model and parameters"""
        system_prompt = "You are an advanced reasoning system. Analyze the problem step by step."

        messages = [
            {"role": "system", "content": system_prompt}
        ]

        if context:
            messages.append({"role": "system", "content": f"Context: {json.dumps(context)}"})

        messages.append({"role": "user", "content": prompt})

        response = await self.chat_completion(
            messages=messages,
            task='reasoning',
            temperature=0.2  # Lower temperature for reasoning
        )

        return response['choices'][0]['message']['content']

    async def creative_task(self, prompt: str, style: Optional[str] = None) -> str:
        """Execute a creative task with appropriate parameters"""
        system_prompt = "You are a creative AI assistant capable of generating imaginative content."

        if style:
            system_prompt += f" Generate content in the style of: {style}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]

        response = await self.chat_completion(
            messages=messages,
            task='creativity',
            temperature=0.9  # Higher temperature for creativity
        )

        return response['choices'][0]['message']['content']

    async def ethics_check(self, action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check ethical implications of an action"""
        messages = [
            {
                "role": "system",
                "content": "You are an ethical reasoning system. Analyze the ethical implications of actions."
            },
            {
                "role": "user",
                "content": f"Analyze the ethical implications of: {action}\nContext: {json.dumps(context)}"
            }
        ]

        response = await self.chat_completion(
            messages=messages,
            task='ethics',
            temperature=0.3
        )

        content = response['choices'][0]['message']['content']

        # Parse response for ethical assessment
        return {
            "action": action,
            "assessment": content,
            "timestamp": datetime.utcnow().isoformat()
        }

    # Utility Methods

    async def count_tokens(self, text: str, model: str = "gpt-3.5-turbo") -> int:
        """Estimate token count for text"""
        # Rough estimation: 4 characters per token
        # In production, use tiktoken library for accurate counting
        return len(text) // 4

    def get_model_info(self, task: Optional[str] = None) -> Dict[str, Any]:
        """Get information about available models and current configuration"""
        return {
            "task_models": self.TASK_MODELS,
            "selected_model": self.TASK_MODELS.get(task, self.TASK_MODELS['general']) if task else None,
            "organization_id": self.organization_id,
            "project_id": self.project_id,
            "default_temperature": self.default_temperature,
            "default_max_tokens": self.default_max_tokens
        }

    async def close(self):
        """Clean up resources"""
        await self.async_client.close()
        logger.info("UnifiedOpenAIClient closed")


# Backward compatibility aliases
GPTClient = UnifiedOpenAIClient
LukhasOpenAIClient = UnifiedOpenAIClient
OpenAIWrapper = UnifiedOpenAIClient