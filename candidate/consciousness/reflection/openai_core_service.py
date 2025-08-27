"""

#TAG:consciousness
#TAG:reflection
#TAG:neuroplastic
#TAG:colony


══════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - OPENAI CORE SERVICE
║ Centralized OpenAI integration service for all LUKHAS modules
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: openai_core_service.py
║ Path: bridge/openai_core_service.py
║ Version: 1.0.0 | Created: 2025-07-28
║ Authors: LUKHAS AI Integration Team | Claude Code
╠══════════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠══════════════════════════════════════════════════════════════════════════════════
║ This module provides centralized OpenAI integration for the entire LUKHAS system:
║ • Unified API access for all modules
║ • Automatic model selection based on task
║ • Fallback mechanisms for resilience
║ • Usage tracking and optimization
║ • Cost management and budgeting
║ • Mock responses for development/testing
║
║ All LUKHAS modules should use this service instead of direct OpenAI calls.
╚══════════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import hashlib
import json
import logging
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional, Union

# Try to import from candidate.core.common if available
try:
    from candidate.core.common import get_logger

    logger = get_logger("ΛTRACE.bridge.openai_core")
except ImportError:
    logger = logging.getLogger("ΛTRACE.bridge.openai_core")

# Mock imports for when OpenAI is not available
try:
    from openai import AsyncOpenAI, OpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

    # Mock classes for development
    class AsyncOpenAI:
        pass

    class OpenAI:
        pass


class OpenAICapability(Enum):
    """Available OpenAI capabilities."""

    TEXT_GENERATION = "text_generation"
    IMAGE_GENERATION = "image_generation"
    AUDIO_GENERATION = "audio_generation"
    AUDIO_TRANSCRIPTION = "audio_transcription"
    EMBEDDINGS = "embeddings"
    VISION = "vision"
    FUNCTION_CALLING = "function_calling"
    MODERATION = "moderation"


class ModelType(Enum):
    """Model types for different tasks."""

    REASONING = "reasoning"
    CREATIVE = "creative"
    FAST = "fast"
    VISION = "vision"
    EMBEDDING = "embedding"
    TTS = "tts"
    WHISPER = "whisper"
    DALLE = "dalle"
    MODERATION = "moderation"


@dataclass
class OpenAIRequest:
    """Standardized OpenAI request format."""

    module: str
    capability: OpenAICapability
    data: dict[str, Any]
    model_preference: Optional[ModelType] = None
    priority: int = 5  # 1-10, higher is more important
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None


@dataclass
class OpenAIResponse:
    """Standardized OpenAI response format."""

    request_id: str
    module: str
    capability: OpenAICapability
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    usage: Optional[dict[str, Any]] = None
    latency_ms: Optional[int] = None
    fallback_used: bool = False


class OpenAICoreService:
    """
    Centralized OpenAI service for all LUKHAS modules.
    Provides unified access, fallbacks, and usage tracking.
    """

    # Model configurations
    MODELS = {
        ModelType.REASONING: "gpt-4-turbo-preview",
        ModelType.CREATIVE: "gpt-4",
        ModelType.FAST: "gpt-3.5-turbo",
        ModelType.VISION: "gpt-4-vision-preview",
        ModelType.EMBEDDING: "text-embedding-3-large",
        ModelType.TTS: "tts-1-hd",
        ModelType.WHISPER: "whisper-1",
        ModelType.DALLE: "dall-e-3",
        ModelType.MODERATION: "text-moderation-latest",
    }

    # Capability to models mapping
    CAPABILITY_MODELS = {
        OpenAICapability.TEXT_GENERATION: [
            ModelType.REASONING,
            ModelType.CREATIVE,
            ModelType.FAST,
        ],
        OpenAICapability.IMAGE_GENERATION: [ModelType.DALLE],
        OpenAICapability.AUDIO_GENERATION: [ModelType.TTS],
        OpenAICapability.AUDIO_TRANSCRIPTION: [ModelType.WHISPER],
        OpenAICapability.EMBEDDINGS: [ModelType.EMBEDDING],
        OpenAICapability.VISION: [ModelType.VISION],
        OpenAICapability.FUNCTION_CALLING: [ModelType.REASONING, ModelType.FAST],
        OpenAICapability.MODERATION: [ModelType.MODERATION],
    }

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the OpenAI core service.

        Args:
            api_key: Optional API key. If not provided, uses environment variable.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.mock_mode = not OPENAI_AVAILABLE or not self.api_key

        if self.mock_mode:
            logger.warning("OpenAI Core Service running in MOCK MODE")
            self.mock_provider = OpenAIMockProvider()
        else:
            self.async_client = AsyncOpenAI(api_key=self.api_key)
            self.sync_client = OpenAI(api_key=self.api_key)

        # Usage tracking
        self.usage_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "fallback_requests": 0,
            "tokens_used": 0,
            "cost_estimate": 0.0,
            "by_module": {},
            "by_capability": {},
        }

        # Cache for responses
        self.cache = {}
        self.cache_ttl = timedelta(minutes=15)

        # Rate limiting
        self.rate_limiter = RateLimiter()

        logger.info(f"OpenAI Core Service initialized (mock_mode={self.mock_mode})")

    async def process_request(self, request: OpenAIRequest) -> OpenAIResponse:
        """
        Process an OpenAI request from any module.

        Args:
            request: Standardized OpenAI request

        Returns:
            Standardized OpenAI response
        """
        start_time = datetime.utcnow()
        request_id = self._generate_request_id(request)

        logger.info(f"Processing request {request_id} from {request.module}")

        # Update stats
        self.usage_stats["total_requests"] += 1
        self._update_module_stats(request.module, "requests")

        try:
            # Check cache
            cache_key = self._get_cache_key(request)
            if cache_key in self.cache:
                cached_response = self.cache[cache_key]
                if self._is_cache_valid(cached_response):
                    logger.info(f"Cache hit for request {request_id}")
                    cached_response.request_id = request_id
                    return cached_response

            # Rate limiting
            await self.rate_limiter.check_rate_limit(request)

            # Process based on capability
            if self.mock_mode:
                response = await self._process_mock_request(request)
            else:
                response = await self._process_real_request(request)

            # Update response metadata
            response.request_id = request_id
            response.module = request.module
            response.capability = request.capability
            response.latency_ms = int(
                (datetime.utcnow() - start_time).total_seconds() * 1000
            )

            # Cache successful responses
            if response.success and cache_key:
                self.cache[cache_key] = response

            # Update stats
            if response.success:
                self.usage_stats["successful_requests"] += 1
                self._update_module_stats(request.module, "successful")
            else:
                self.usage_stats["failed_requests"] += 1
                self._update_module_stats(request.module, "failed")

            if response.fallback_used:
                self.usage_stats["fallback_requests"] += 1

            return response

        except Exception as e:
            logger.error(f"Error processing request {request_id}: {e}")
            return OpenAIResponse(
                request_id=request_id,
                module=request.module,
                capability=request.capability,
                success=False,
                error=str(e),
                latency_ms=int((datetime.utcnow() - start_time).total_seconds() * 1000),
            )

    async def _process_real_request(self, request: OpenAIRequest) -> OpenAIResponse:
        """Process request using real OpenAI API."""
        capability_handlers = {
            OpenAICapability.TEXT_GENERATION: self._handle_text_generation,
            OpenAICapability.IMAGE_GENERATION: self._handle_image_generation,
            OpenAICapability.AUDIO_GENERATION: self._handle_audio_generation,
            OpenAICapability.AUDIO_TRANSCRIPTION: self._handle_audio_transcription,
            OpenAICapability.EMBEDDINGS: self._handle_embeddings,
            OpenAICapability.VISION: self._handle_vision,
            OpenAICapability.FUNCTION_CALLING: self._handle_function_calling,
            OpenAICapability.MODERATION: self._handle_moderation,
        }

        handler = capability_handlers.get(request.capability)
        if not handler:
            return OpenAIResponse(
                request_id="",
                module=request.module,
                capability=request.capability,
                success=False,
                error=f"Unsupported capability: {request.capability}",
            )

        return await handler(request)

    async def _handle_text_generation(self, request: OpenAIRequest) -> OpenAIResponse:
        """Handle text generation requests."""
        try:
            # Select model
            model = self._select_model(request)

            # Prepare messages
            messages = request.data.get("messages", [])
            if isinstance(request.data.get("prompt"), str):
                messages = [{"role": "user", "content": request.data["prompt"]}]

            # Make API call
            response = await self.async_client.chat.completions.create(
                model=self.MODELS[model],
                messages=messages,
                temperature=request.data.get("temperature", 0.7),
                max_tokens=request.data.get("max_tokens", 2000),
                stream=request.data.get("stream", False),
            )

            # Handle streaming
            if request.data.get("stream", False):
                return OpenAIResponse(
                    request_id="",
                    module=request.module,
                    capability=request.capability,
                    success=True,
                    data=response,  # Return stream directly
                )

            # Extract response
            result = response.model_dump()
            content = result["choices"][0]["message"]["content"]

            return OpenAIResponse(
                request_id="",
                module=request.module,
                capability=request.capability,
                success=True,
                data={
                    "content": content,
                    "finish_reason": result["choices"][0]["finish_reason"],
                    "model": result["model"],
                },
                usage=result.get("usage"),
            )

        except Exception as e:
            logger.error(f"Text generation error: {e}")
            # Try fallback
            return await self._process_mock_request(request)

    async def _handle_image_generation(self, request: OpenAIRequest) -> OpenAIResponse:
        """Handle image generation requests."""
        try:
            response = await self.async_client.images.generate(
                model=self.MODELS[ModelType.DALLE],
                prompt=request.data["prompt"],
                size=request.data.get("size", "1024x1024"),
                quality=request.data.get("quality", "standard"),
                n=request.data.get("n", 1),
                response_format=request.data.get("response_format", "url"),
            )

            images = []
            for image in response.data:
                images.append(
                    {
                        "url": image.url if hasattr(image, "url") else None,
                        "b64_json": (
                            image.b64_json if hasattr(image, "b64_json") else None
                        ),
                        "revised_prompt": (
                            image.revised_prompt
                            if hasattr(image, "revised_prompt")
                            else None
                        ),
                    }
                )

            return OpenAIResponse(
                request_id="",
                module=request.module,
                capability=request.capability,
                success=True,
                data={"images": images},
            )

        except Exception as e:
            logger.error(f"Image generation error: {e}")
            return await self._process_mock_request(request)

    async def _handle_audio_generation(self, request: OpenAIRequest) -> OpenAIResponse:
        """Handle audio generation (TTS) requests."""
        try:
            response = await self.async_client.audio.speech.create(
                model=self.MODELS[ModelType.TTS],
                voice=request.data.get("voice", "nova"),
                input=request.data["text"],
                speed=request.data.get("speed", 1.0),
            )

            # Save or return audio data
            if "output_path" in request.data:
                response.stream_to_file(request.data["output_path"])
                data = {"path": request.data["output_path"]}
            else:
                # Return bytes for in-memory handling
                audio_bytes = response.content
                data = {"audio_bytes": audio_bytes}

            return OpenAIResponse(
                request_id="",
                module=request.module,
                capability=request.capability,
                success=True,
                data=data,
            )

        except Exception as e:
            logger.error(f"Audio generation error: {e}")
            return await self._process_mock_request(request)

    async def _handle_audio_transcription(
        self, request: OpenAIRequest
    ) -> OpenAIResponse:
        """Handle audio transcription (Whisper) requests."""
        try:
            # Open audio file
            audio_file = request.data["audio_file"]
            with open(audio_file, "rb") as f:
                response = await self.async_client.audio.transcriptions.create(
                    model=self.MODELS[ModelType.WHISPER],
                    file=f,
                    language=request.data.get("language"),
                )

            return OpenAIResponse(
                request_id="",
                module=request.module,
                capability=request.capability,
                success=True,
                data={"text": response.text, "language": request.data.get("language")},
            )

        except Exception as e:
            logger.error(f"Audio transcription error: {e}")
            return await self._process_mock_request(request)

    async def _handle_embeddings(self, request: OpenAIRequest) -> OpenAIResponse:
        """Handle embedding generation requests."""
        try:
            response = await self.async_client.embeddings.create(
                model=self.MODELS[ModelType.EMBEDDING], input=request.data["input"]
            )

            embeddings = [e.embedding for e in response.data]

            return OpenAIResponse(
                request_id="",
                module=request.module,
                capability=request.capability,
                success=True,
                data={"embeddings": embeddings, "model": response.model},
                usage=(
                    response.usage.model_dump() if hasattr(response, "usage") else None
                ),
            )

        except Exception as e:
            logger.error(f"Embedding generation error: {e}")
            return await self._process_mock_request(request)

    async def _handle_vision(self, request: OpenAIRequest) -> OpenAIResponse:
        """Handle vision (image understanding) requests."""
        try:
            messages = request.data.get("messages", [])

            # Ensure image is properly formatted
            if "image_url" in request.data:
                messages.append(
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": request.data.get(
                                    "prompt", "What is in this image?"
                                ),
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": request.data["image_url"]},
                            },
                        ],
                    }
                )

            response = await self.async_client.chat.completions.create(
                model=self.MODELS[ModelType.VISION],
                messages=messages,
                max_tokens=request.data.get("max_tokens", 1000),
            )

            result = response.model_dump()
            content = result["choices"][0]["message"]["content"]

            return OpenAIResponse(
                request_id="",
                module=request.module,
                capability=request.capability,
                success=True,
                data={"analysis": content},
                usage=result.get("usage"),
            )

        except Exception as e:
            logger.error(f"Vision processing error: {e}")
            return await self._process_mock_request(request)

    async def _handle_function_calling(self, request: OpenAIRequest) -> OpenAIResponse:
        """Handle function calling requests."""
        try:
            model = self._select_model(request)

            response = await self.async_client.chat.completions.create(
                model=self.MODELS[model],
                messages=request.data["messages"],
                functions=request.data.get("functions", []),
                function_call=request.data.get("function_call", "auto"),
                temperature=request.data.get("temperature", 0.7),
            )

            result = response.model_dump()
            message = result["choices"][0]["message"]

            return OpenAIResponse(
                request_id="",
                module=request.module,
                capability=request.capability,
                success=True,
                data={
                    "content": message.get("content"),
                    "function_call": message.get("function_call"),
                },
                usage=result.get("usage"),
            )

        except Exception as e:
            logger.error(f"Function calling error: {e}")
            return await self._process_mock_request(request)

    async def _handle_moderation(self, request: OpenAIRequest) -> OpenAIResponse:
        """Handle content moderation requests."""
        try:
            response = await self.async_client.moderations.create(
                input=request.data["input"]
            )

            result = response.model_dump()

            return OpenAIResponse(
                request_id="",
                module=request.module,
                capability=request.capability,
                success=True,
                data={
                    "flagged": result["results"][0]["flagged"],
                    "categories": result["results"][0]["categories"],
                    "scores": result["results"][0]["category_scores"],
                },
            )

        except Exception as e:
            logger.error(f"Moderation error: {e}")
            return await self._process_mock_request(request)

    async def _process_mock_request(self, request: OpenAIRequest) -> OpenAIResponse:
        """Process request using mock provider."""
        return await self.mock_provider.process(request)

    def _select_model(self, request: OpenAIRequest) -> ModelType:
        """Select appropriate model based on request."""
        if request.model_preference:
            return request.model_preference

        # Default selections based on capability
        defaults = {
            OpenAICapability.TEXT_GENERATION: ModelType.FAST,
            OpenAICapability.FUNCTION_CALLING: ModelType.REASONING,
        }

        return defaults.get(request.capability, ModelType.FAST)

    def _generate_request_id(self, request: OpenAIRequest) -> str:
        """Generate unique request ID."""
        timestamp = datetime.utcnow().isoformat()
        data_hash = hashlib.sha256(  # Changed from MD5 for security
            json.dumps(asdict(request), sort_keys=True).encode()
        ).hexdigest()[:8]
        return f"{request.module}_{timestamp}_{data_hash}"

    def _get_cache_key(self, request: OpenAIRequest) -> Optional[str]:
        """Generate cache key for request."""
        # Only cache certain capabilities
        if request.capability not in [
            OpenAICapability.TEXT_GENERATION,
            OpenAICapability.EMBEDDINGS,
        ]:
            return None

        # Create stable key from request data
        key_data = {
            "capability": request.capability.value,
            "data": request.data,
            "model_preference": (
                request.model_preference.value if request.model_preference else None
            ),
        }

        return hashlib.sha256(json.dumps(key_data, sort_keys=True).encode()).hexdigest()

    def _is_cache_valid(self, response: OpenAIResponse) -> bool:
        """Check if cached response is still valid."""
        # For now, always consider cache valid within TTL
        # In future, could check based on response metadata
        return True

    def _update_module_stats(self, module: str, stat_type: str):
        """Update usage statistics for module."""
        if module not in self.usage_stats["by_module"]:
            self.usage_stats["by_module"][module] = {
                "requests": 0,
                "successful": 0,
                "failed": 0,
                "tokens": 0,
                "cost": 0.0,
            }

        if stat_type == "requests":
            self.usage_stats["by_module"][module]["requests"] += 1
        elif stat_type == "successful":
            self.usage_stats["by_module"][module]["successful"] += 1
        elif stat_type == "failed":
            self.usage_stats["by_module"][module]["failed"] += 1

    def get_usage_report(self) -> dict[str, Any]:
        """Get comprehensive usage report."""
        return {
            "summary": self.usage_stats,
            "by_module": self.usage_stats["by_module"],
            "cache_stats": {"size": len(self.cache), "hit_rate": "Not implemented"},
            "timestamp": datetime.utcnow().isoformat(),
        }


class OpenAIMockProvider:
    """
    Provides mock responses for OpenAI capabilities.
    Used for development, testing, and fallback scenarios.
    """

    def __init__(self):
        self.mock_responses = self._load_mock_responses()

    async def process(self, request: OpenAIRequest) -> OpenAIResponse:
        """Process request with mock response."""
        logger.info(f"Mock processing {request.capability} for {request.module}")

        handlers = {
            OpenAICapability.TEXT_GENERATION: self._mock_text_generation,
            OpenAICapability.IMAGE_GENERATION: self._mock_image_generation,
            OpenAICapability.AUDIO_GENERATION: self._mock_audio_generation,
            OpenAICapability.AUDIO_TRANSCRIPTION: self._mock_audio_transcription,
            OpenAICapability.EMBEDDINGS: self._mock_embeddings,
            OpenAICapability.VISION: self._mock_vision,
            OpenAICapability.FUNCTION_CALLING: self._mock_function_calling,
            OpenAICapability.MODERATION: self._mock_moderation,
        }

        handler = handlers.get(request.capability)
        if handler:
            return await handler(request)

        return OpenAIResponse(
            request_id="mock",
            module=request.module,
            capability=request.capability,
            success=False,
            error="Mock handler not implemented",
            fallback_used=True,
        )

    async def _mock_text_generation(self, request: OpenAIRequest) -> OpenAIResponse:
        """Mock text generation response."""
        # Module-specific mock responses
        module_responses = {
            "dream": "In this dream, you find yourself in a surreal landscape where thoughts become visible...",
            "memory": "The memory folds reveal patterns of interconnected experiences...",
            "consciousness": "Awareness fluctuates between different states of perception...",
            "reasoning": "Analysis suggests multiple pathways to the solution...",
            "emotion": "The emotional resonance indicates a complex interplay of feelings...",
        }

        content = module_responses.get(
            request.module, "This is a mock response for development purposes."
        )

        return OpenAIResponse(
            request_id="mock",
            module=request.module,
            capability=request.capability,
            success=True,
            data={"content": content},
            fallback_used=True,
        )

    async def _mock_image_generation(self, request: OpenAIRequest) -> OpenAIResponse:
        """Mock image generation response."""
        return OpenAIResponse(
            request_id="mock",
            module=request.module,
            capability=request.capability,
            success=True,
            data={
                "images": [
                    {
                        "url": "mock://image/placeholder.png",
                        "revised_prompt": request.data.get("prompt", "Mock image"),
                    }
                ]
            },
            fallback_used=True,
        )

    async def _mock_audio_generation(self, request: OpenAIRequest) -> OpenAIResponse:
        """Mock audio generation response."""
        return OpenAIResponse(
            request_id="mock",
            module=request.module,
            capability=request.capability,
            success=True,
            data={"path": "mock://audio/placeholder.mp3"},
            fallback_used=True,
        )

    async def _mock_audio_transcription(self, request: OpenAIRequest) -> OpenAIResponse:
        """Mock audio transcription response."""
        return OpenAIResponse(
            request_id="mock",
            module=request.module,
            capability=request.capability,
            success=True,
            data={"text": "This is a mock transcription of the audio file."},
            fallback_used=True,
        )

    async def _mock_embeddings(self, request: OpenAIRequest) -> OpenAIResponse:
        """Mock embedding generation response."""
        # Generate random embeddings
        import random

        embedding_dim = 1536  # OpenAI embedding dimension
        mock_embedding = [random.random() for _ in range(embedding_dim)]

        return OpenAIResponse(
            request_id="mock",
            module=request.module,
            capability=request.capability,
            success=True,
            data={"embeddings": [mock_embedding]},
            fallback_used=True,
        )

    async def _mock_vision(self, request: OpenAIRequest) -> OpenAIResponse:
        """Mock vision analysis response."""
        return OpenAIResponse(
            request_id="mock",
            module=request.module,
            capability=request.capability,
            success=True,
            data={
                "analysis": "The image appears to contain abstract patterns and colors."
            },
            fallback_used=True,
        )

    async def _mock_function_calling(self, request: OpenAIRequest) -> OpenAIResponse:
        """Mock function calling response."""
        return OpenAIResponse(
            request_id="mock",
            module=request.module,
            capability=request.capability,
            success=True,
            data={
                "content": "I will call the appropriate function.",
                "function_call": {
                    "name": "mock_function",
                    "arguments": '{"param": "value"}',
                },
            },
            fallback_used=True,
        )

    async def _mock_moderation(self, request: OpenAIRequest) -> OpenAIResponse:
        """Mock moderation response."""
        return OpenAIResponse(
            request_id="mock",
            module=request.module,
            capability=request.capability,
            success=True,
            data={"flagged": False, "categories": {}, "scores": {}},
            fallback_used=True,
        )

    def _load_mock_responses(self) -> dict[str, Any]:
        """Load predefined mock responses."""
        # Could load from JSON file for more complex mocks
        return {}


class RateLimiter:
    """Simple rate limiter for API calls."""

    def __init__(self):
        self.limits = {"per_minute": 60, "per_hour": 1000, "per_day": 10000}
        self.requests = []

    async def check_rate_limit(self, request: OpenAIRequest):
        """Check if request is within rate limits."""
        now = datetime.utcnow()

        # Clean old requests
        cutoff = now - timedelta(days=1)
        self.requests = [r for r in self.requests if r > cutoff]

        # Check limits
        minute_ago = now - timedelta(minutes=1)
        hour_ago = now - timedelta(hours=1)

        minute_count = sum(1 for r in self.requests if r > minute_ago)
        hour_count = sum(1 for r in self.requests if r > hour_ago)
        day_count = len(self.requests)

        if minute_count >= self.limits["per_minute"]:
            await asyncio.sleep(60 - (now - minute_ago).seconds)
        elif hour_count >= self.limits["per_hour"]:
            raise Exception("Hourly rate limit exceeded")
        elif day_count >= self.limits["per_day"]:
            raise Exception("Daily rate limit exceeded")

        # Record request
        self.requests.append(now)


# Convenience functions for modules
async def generate_text(
    module: str, prompt: str, model_type: ModelType = ModelType.FAST, **kwargs
) -> str:
    """Convenience function for text generation."""
    service = OpenAICoreService()
    request = OpenAIRequest(
        module=module,
        capability=OpenAICapability.TEXT_GENERATION,
        data={"prompt": prompt, **kwargs},
        model_preference=model_type,
    )
    response = await service.process_request(request)
    if response.success:
        return response.data["content"]
    else:
        raise Exception(f"Text generation failed: {response.error}")


async def generate_image(
    module: str, prompt: str, size: str = "1024x1024", **kwargs
) -> dict[str, Any]:
    """Convenience function for image generation."""
    service = OpenAICoreService()
    request = OpenAIRequest(
        module=module,
        capability=OpenAICapability.IMAGE_GENERATION,
        data={"prompt": prompt, "size": size, **kwargs},
    )
    response = await service.process_request(request)
    if response.success:
        return response.data["images"][0]
    else:
        raise Exception(f"Image generation failed: {response.error}")


async def generate_audio(
    module: str,
    text: str,
    voice: str = "nova",
    output_path: Optional[str] = None,
    **kwargs,
) -> Union[str, bytes]:
    """Convenience function for audio generation."""
    service = OpenAICoreService()
    data = {"text": text, "voice": voice, **kwargs}
    if output_path:
        data["output_path"] = output_path

    request = OpenAIRequest(
        module=module, capability=OpenAICapability.AUDIO_GENERATION, data=data
    )
    response = await service.process_request(request)
    if response.success:
        return response.data.get("path") or response.data.get("audio_bytes")
    else:
        raise Exception(f"Audio generation failed: {response.error}")


# Example usage
async def demo():
    """Demonstrate OpenAI Core Service usage."""
    service = OpenAICoreService()

    # Text generation example
    text_request = OpenAIRequest(
        module="demo",
        capability=OpenAICapability.TEXT_GENERATION,
        data={"prompt": "Describe a dream about flying"},
        model_preference=ModelType.CREATIVE,
    )

    response = await service.process_request(text_request)
    print(f"Text Generation Response: {response.success}")
    if response.success:
        print(f"Content: {response.data['content'][:100]}...")

    # Get usage report
    report = service.get_usage_report()
    print(f"\nUsage Report: {json.dumps(report, indent=2)}")


if __name__ == "__main__":
    asyncio.run(demo())
