"""
🧠 LUKHAS AI - UNIFIED OPENAI CLIENT
Unified OpenAI integration combining all client features

Copyright (c) 2025 LUKHAS AI. All rights reserved.
"""

import asyncio
import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional, Union, AsyncIterator
import uuid

from openai import AsyncOpenAI, OpenAI

# Use fallback imports for core.common
try:
    from core.common import get_logger, retry, with_timeout
    logger = get_logger(__name__, "BRIDGE")
except ImportError:
    # Fallback to standard logging if core.common not available
    import logging
    logger = logging.getLogger(__name__)
    
    def retry(*args, **kwargs):
        """Fallback retry decorator"""
        def decorator(func):
            return func
        return decorator
    
    def with_timeout(*args, **kwargs):
        """Fallback timeout decorator"""
        def decorator(func):
            return func
        return decorator


@dataclass
class ConversationMessage:
    """Represents a single message in a conversation"""
    
    role: str
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def to_openai_format(self) -> dict[str, Any]:
        """Convert to OpenAI API format"""
        return {
            "role": self.role,
            "content": self.content,
        }


@dataclass
class ConversationState:
    """Manages conversation state and history"""
    
    conversation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    messages: list[ConversationMessage] = field(default_factory=list)
    system_prompt: Optional[str] = None
    max_history: int = 50
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def add_message(self, role: str, content: str, **metadata) -> ConversationMessage:
        """Add a message to the conversation"""
        message = ConversationMessage(
            role=role,
            content=content,
            metadata=metadata
        )
        self.messages.append(message)
        
        # Trim history if needed
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history:]
        
        return message
    
    def to_openai_messages(self) -> list[dict[str, Any]]:
        """Convert to OpenAI messages format"""
        messages = []
        
        # Add system prompt if present
        if self.system_prompt:
            messages.append({
                "role": "system",
                "content": self.system_prompt
            })
        
        # Add conversation messages
        messages.extend([msg.to_openai_format() for msg in self.messages])
        
        return messages


class UnifiedOpenAIClient:
    """
    Unified OpenAI client with async support, conversation management,
    and comprehensive error handling.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        organization: Optional[str] = None,
        base_url: Optional[str] = None,
        default_model: str = "gpt-4o-mini",
        max_retries: int = 3,
        timeout: float = 60.0,
    ):
        """
        Initialize the unified OpenAI client.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            organization: OpenAI organization ID
            base_url: Custom base URL for API
            default_model: Default model to use
            max_retries: Maximum retry attempts
            timeout: Request timeout in seconds
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.organization = organization or os.getenv("OPENAI_ORG_ID")
        self.base_url = base_url
        self.default_model = default_model
        self.max_retries = max_retries
        self.timeout = timeout
        
        if not self.api_key:
            raise ValueError("OpenAI API key must be provided or set in OPENAI_API_KEY environment variable")
        
        # Initialize clients
        client_args = {
            "api_key": self.api_key,
            "max_retries": max_retries,
            "timeout": timeout,
        }
        
        if self.organization:
            client_args["organization"] = self.organization
        if self.base_url:
            client_args["base_url"] = self.base_url
        
        self.client = OpenAI(**client_args)
        self.async_client = AsyncOpenAI(**client_args)
        
        # Conversation management
        self.conversations: dict[str, ConversationState] = {}
        
        logger.info(f"Initialized UnifiedOpenAIClient with model {default_model}")
    
    def create_conversation(
        self,
        conversation_id: Optional[str] = None,
        system_prompt: Optional[str] = None,
        max_history: int = 50,
    ) -> str:
        """
        Create a new conversation.
        
        Args:
            conversation_id: Optional custom conversation ID
            system_prompt: System prompt for the conversation
            max_history: Maximum messages to keep in history
            
        Returns:
            Conversation ID
        """
        if conversation_id is None:
            conversation_id = str(uuid.uuid4())
        
        self.conversations[conversation_id] = ConversationState(
            conversation_id=conversation_id,
            system_prompt=system_prompt,
            max_history=max_history,
        )
        
        return conversation_id
    
    def get_conversation(self, conversation_id: str) -> Optional[ConversationState]:
        """Get conversation by ID"""
        return self.conversations.get(conversation_id)
    
    @retry(max_attempts=3, delay=1.0, exceptions=(Exception,))
    async def chat_completion(
        self,
        messages: Union[str, list[dict[str, Any]]],
        model: Optional[str] = None,
        conversation_id: Optional[str] = None,
        stream: bool = False,
        **kwargs,
    ) -> Union[dict[str, Any], AsyncIterator[dict[str, Any]]]:
        """
        Create a chat completion.
        
        Args:
            messages: Either a string prompt or list of OpenAI messages
            model: Model to use (defaults to default_model)
            conversation_id: Optional conversation ID for state management
            stream: Whether to stream responses
            **kwargs: Additional OpenAI API parameters
            
        Returns:
            Response dict or async iterator for streaming
        """
        model = model or self.default_model
        
        # Handle different message formats
        if isinstance(messages, str):
            if conversation_id:
                # Add to conversation
                conversation = self.conversations.get(conversation_id)
                if conversation:
                    conversation.add_message("user", messages)
                    openai_messages = conversation.to_openai_messages()
                else:
                    openai_messages = [{"role": "user", "content": messages}]
            else:
                openai_messages = [{"role": "user", "content": messages}]
        else:
            openai_messages = messages
        
        # Prepare API call
        api_params = {
            "model": model,
            "messages": openai_messages,
            "stream": stream,
            **kwargs,
        }
        
        try:
            if stream:
                return self._stream_chat_completion(api_params, conversation_id)
            else:
                response = await self.async_client.chat.completions.create(**api_params)
                
                # Add response to conversation if tracking
                if conversation_id and response.choices:
                    conversation = self.conversations.get(conversation_id)
                    if conversation:
                        assistant_content = response.choices[0].message.content
                        if assistant_content:
                            conversation.add_message("assistant", assistant_content)
                
                return {
                    "id": response.id,
                    "object": response.object,
                    "created": response.created,
                    "model": response.model,
                    "choices": [
                        {
                            "index": choice.index,
                            "message": {
                                "role": choice.message.role,
                                "content": choice.message.content,
                            },
                            "finish_reason": choice.finish_reason,
                        }
                        for choice in response.choices
                    ],
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                        "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                        "total_tokens": response.usage.total_tokens if response.usage else 0,
                    } if response.usage else None,
                }
                
        except Exception as e:
            logger.error(f"Chat completion failed: {str(e)}")
            raise
    
    async def _stream_chat_completion(
        self,
        api_params: dict[str, Any],
        conversation_id: Optional[str] = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """Handle streaming chat completion"""
        assistant_content_parts = []
        
        try:
            async for chunk in await self.async_client.chat.completions.create(**api_params):
                chunk_dict = {
                    "id": chunk.id,
                    "object": chunk.object,
                    "created": chunk.created,
                    "model": chunk.model,
                    "choices": [],
                }
                
                if chunk.choices:
                    choice = chunk.choices[0]
                    chunk_dict["choices"] = [{
                        "index": choice.index,
                        "delta": {
                            "role": getattr(choice.delta, "role", None),
                            "content": getattr(choice.delta, "content", None),
                        },
                        "finish_reason": choice.finish_reason,
                    }]
                    
                    # Collect content for conversation tracking
                    if choice.delta.content:
                        assistant_content_parts.append(choice.delta.content)
                
                yield chunk_dict
            
            # Add complete response to conversation if tracking
            if conversation_id and assistant_content_parts:
                conversation = self.conversations.get(conversation_id)
                if conversation:
                    full_content = "".join(assistant_content_parts)
                    conversation.add_message("assistant", full_content)
                    
        except Exception as e:
            logger.error(f"Streaming chat completion failed: {str(e)}")
            raise
    
    async def embeddings(
        self,
        input_text: Union[str, list[str]],
        model: str = "text-embedding-ada-002",
        **kwargs,
    ) -> dict[str, Any]:
        """
        Create embeddings for input text.
        
        Args:
            input_text: Text or list of texts to embed
            model: Embedding model to use
            **kwargs: Additional API parameters
            
        Returns:
            Embeddings response
        """
        try:
            response = await self.async_client.embeddings.create(
                model=model,
                input=input_text,
                **kwargs,
            )
            
            return {
                "object": response.object,
                "data": [
                    {
                        "object": item.object,
                        "index": item.index,
                        "embedding": item.embedding,
                    }
                    for item in response.data
                ],
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "total_tokens": response.usage.total_tokens,
                } if response.usage else None,
            }
            
        except Exception as e:
            logger.error(f"Embeddings failed: {str(e)}")
            raise
    
    def clear_conversation(self, conversation_id: str) -> bool:
        """Clear a conversation"""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            return True
        return False
    
    def get_conversation_history(self, conversation_id: str) -> Optional[list[dict[str, Any]]]:
        """Get conversation history in OpenAI format"""
        conversation = self.conversations.get(conversation_id)
        if conversation:
            return conversation.to_openai_messages()
        return None


# Aliases for backward compatibility
GPTClient = UnifiedOpenAIClient
LukhasOpenAIClient = UnifiedOpenAIClient  
OpenAIWrapper = UnifiedOpenAIClient