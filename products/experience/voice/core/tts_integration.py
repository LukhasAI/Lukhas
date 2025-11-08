"""
LUKHAS AI TTS Service Integration
Unified Text-to-Speech service integration with multiple providers and Trinity Framework support.
⚛️ Identity-aware TTS selection
🧠 Consciousness-driven voice synthesis
🛡️ Guardian-protected TTS operations
"""

import json
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from bridge.voice.systems.voice_synthesis import (
    CoquiProvider,
    EdgeTTSProvider,
    ElevenLabsProvider,
    VoiceSynthesisProvider,
)
from voice.audio_processing import LUKHASAudioProcessor, ProcessingQuality
from voice.voice_modulator import VoiceModulationMode, VoiceModulator

from core.common.glyph import GLYPHSymbol, create_glyph
from core.common.logger import get_logger
from governance.guardian import GuardianValidator

logger = get_logger(__name__)


class TTSProviderType(Enum):
    """TTS provider types"""

    ELEVENLABS = "elevenlabs"
    EDGE_TTS = "edge_tts"
    COQUI = "coqui"
    OPENAI = "openai"
    GOOGLE = "google"
    AZURE = "azure"
    AWS_POLLY = "aws_polly"


class TTSQuality(Enum):
    """TTS quality levels"""

    DRAFT = "draft"
    STANDARD = "standard"
    HIGH = "high"
    PREMIUM = "premium"


@dataclass
class TTSRequest:
    """TTS request structure"""

    text: str
    voice_id: Optional[str] = None
    emotion: Optional[str] = None
    speed: float = 1.0
    pitch: float = 1.0
    volume: float = 1.0
    quality: TTSQuality = TTSQuality.STANDARD
    provider_preference: Optional[TTSProviderType] = None

    # Context parameters
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    context: dict[str, Any] = field(default_factory=dict)

    # Processing options
    apply_audio_processing: bool = True
    audio_processing_quality: ProcessingQuality = ProcessingQuality.STANDARD
    modulation_mode: Optional[VoiceModulationMode] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "text": self.text,
            "voice_id": self.voice_id,
            "emotion": self.emotion,
            "speed": self.speed,
            "pitch": self.pitch,
            "volume": self.volume,
            "quality": self.quality.value,
            "provider_preference": (self.provider_preference.value if self.provider_preference else None),
            "user_id": self.user_id,
            "session_id": self.session_id,
            "context": self.context,
            "apply_audio_processing": self.apply_audio_processing,
            "audio_processing_quality": self.audio_processing_quality.value,
            "modulation_mode": (self.modulation_mode.value if self.modulation_mode else None),
        }


@dataclass
class TTSResponse:
    """TTS response structure"""

    success: bool
    audio_data: Optional[bytes] = None
    format: str = "wav"
    sample_rate: int = 44100
    duration_seconds: float = 0.0

    # Provider information
    provider_used: Optional[str] = None
    voice_id_used: Optional[str] = None

    # Processing information
    processing_time_ms: float = 0.0
    audio_processing_applied: bool = False
    modulation_applied: bool = False

    # Quality metrics
    quality_metrics: dict[str, float] = field(default_factory=dict)

    # Error information
    error_message: Optional[str] = None
    error_code: Optional[str] = None

    # Metadata
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "success": self.success,
            "audio_data_size": len(self.audio_data) if self.audio_data else 0,
            "format": self.format,
            "sample_rate": self.sample_rate,
            "duration_seconds": self.duration_seconds,
            "provider_used": self.provider_used,
            "voice_id_used": self.voice_id_used,
            "processing_time_ms": self.processing_time_ms,
            "audio_processing_applied": self.audio_processing_applied,
            "modulation_applied": self.modulation_applied,
            "quality_metrics": self.quality_metrics,
            "error_message": self.error_message,
            "error_code": self.error_code,
            "metadata": self.metadata,
        }


class TTSProviderAdapter(ABC):
    """Abstract adapter for TTS providers"""

    @abstractmethod
    async def synthesize(self, request: TTSRequest) -> TTSResponse:
        """Synthesize speech from text"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available"""
        pass

    @abstractmethod
    def get_supported_voices(self) -> list[dict[str, Any]]:
        """Get list of supported voices"""
        pass

    @abstractmethod
    def get_provider_type(self) -> TTSProviderType:
        """Get provider type"""
        pass


class LegacyTTSProviderAdapter(TTSProviderAdapter):
    """Adapter for legacy VoiceSynthesisProvider classes"""

    def __init__(self, provider: VoiceSynthesisProvider, provider_type: TTSProviderType):
        self.provider = provider
        self.provider_type = provider_type
        self.logger = get_logger(f"{__name__}.{provider_type.value.title()}Adapter")

    async def synthesize(self, request: TTSRequest) -> TTSResponse:
        """Synthesize using legacy provider"""
        start_time = time.time()

        try:
            # Convert request to legacy format
            params = {
                "speed": request.speed,
                "pitch": request.pitch,
                "volume": request.volume,
            }

            # Call legacy provider
            result = self.provider.synthesize(
                text=request.text,
                voice_id=request.voice_id,
                emotion=request.emotion,
                params=params,
            )

            processing_time = (time.time() - start_time) * 1000

            if result.get("success", False):
                audio_data = result.get("audio_data")
                format_type = result.get("format", "mp3")

                # Estimate duration (rough calculation)
                if audio_data:
                    # Rough estimation: assume 16kbps for MP3, 44.1kHz for WAV
                    if format_type.lower() == "mp3":
                        duration = len(audio_data) * 8 / (16000)  # 16 kbps
                    else:
                        duration = len(audio_data) / (44100 * 2)  # 16-bit mono
                else:
                    duration = 0.0

                return TTSResponse(
                    success=True,
                    audio_data=audio_data,
                    format=format_type,
                    duration_seconds=duration,
                    provider_used=self.provider_type.value,
                    voice_id_used=result.get("voice_id"),
                    processing_time_ms=processing_time,
                    metadata=result,
                )
            else:
                return TTSResponse(
                    success=False,
                    error_message=result.get("error", "Unknown error"),
                    provider_used=self.provider_type.value,
                    processing_time_ms=processing_time,
                )

        except Exception as e:
            self.logger.error(f"Legacy provider synthesis failed: {e!s}")
            return TTSResponse(
                success=False,
                error_message=str(e),
                provider_used=self.provider_type.value,
                processing_time_ms=(time.time() - start_time) * 1000,
            )

    def is_available(self) -> bool:
        """Check if legacy provider is available"""
        return self.provider.is_available()

    def get_supported_voices(self) -> list[dict[str, Any]]:
        """Get supported voices from legacy provider"""
        try:
            if hasattr(self.provider, "get_available_voices"):
                return self.provider.get_available_voices()
            else:
                return []
        except Exception as e:
            self.logger.error(f"Failed to get voices: {e!s}")
            return []

    def get_provider_type(self) -> TTSProviderType:
        """Get provider type"""
        return self.provider_type


class OpenAITTSAdapter(TTSProviderAdapter):
    """Adapter for OpenAI TTS API"""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.api_key = config.get("api_key")
        self.logger = get_logger(f"{__name__}.OpenAITTSAdapter")

        # Voice mappings
        self.voice_mappings = {
            "alloy": "alloy",
            "echo": "echo",
            "fable": "fable",
            "onyx": "onyx",
            "nova": "nova",
            "shimmer": "shimmer",
        }

    async def synthesize(self, request: TTSRequest) -> TTSResponse:
        """Synthesize using OpenAI TTS"""
        start_time = time.time()

        try:
            import openai

            client = openai.AsyncOpenAI(api_key=self.api_key)

            # Select voice
            voice = request.voice_id or "nova"
            if voice not in self.voice_mappings:
                voice = "nova"

            # Select model based on quality
            model = "tts-1-hd" if request.quality in [TTSQuality.HIGH, TTSQuality.PREMIUM] else "tts-1"

            # Make TTS request
            response = await client.audio.speech.create(
                model=model,
                voice=voice,
                input=request.text,
                response_format="wav",
                speed=request.speed,
            )

            audio_data = response.content
            processing_time = (time.time() - start_time) * 1000

            # Estimate duration
            duration = len(audio_data) / (44100 * 2)  # Rough estimate for WAV

            return TTSResponse(
                success=True,
                audio_data=audio_data,
                format="wav",
                duration_seconds=duration,
                provider_used="openai",
                voice_id_used=voice,
                processing_time_ms=processing_time,
                metadata={"model": model},
            )

        except Exception as e:
            self.logger.error(f"OpenAI TTS failed: {e!s}")
            return TTSResponse(
                success=False,
                error_message=str(e),
                provider_used="openai",
                processing_time_ms=(time.time() - start_time) * 1000,
            )

    def is_available(self) -> bool:
        """Check if OpenAI TTS is available"""
        return self.api_key is not None and len(self.api_key) > 0

    def get_supported_voices(self) -> list[dict[str, Any]]:
        """Get OpenAI supported voices"""
        return [
            {"voice_id": "alloy", "name": "Alloy", "gender": "neutral"},
            {"voice_id": "echo", "name": "Echo", "gender": "male"},
            {"voice_id": "fable", "name": "Fable", "gender": "neutral"},
            {"voice_id": "onyx", "name": "Onyx", "gender": "male"},
            {"voice_id": "nova", "name": "Nova", "gender": "female"},
            {"voice_id": "shimmer", "name": "Shimmer", "gender": "female"},
        ]

    def get_provider_type(self) -> TTSProviderType:
        """Get provider type"""
        return TTSProviderType.OPENAI


class TTSProviderManager:
    """Manager for multiple TTS providers"""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.logger = get_logger(f"{__name__}.TTSProviderManager")

        # Initialize providers
        self.providers: dict[TTSProviderType, TTSProviderAdapter] = {}
        self._initialize_providers()

        # Provider selection strategy
        self.provider_priority = [
            TTSProviderType.ELEVENLABS,
            TTSProviderType.OPENAI,
            TTSProviderType.EDGE_TTS,
            TTSProviderType.COQUI,
        ]

    def _initialize_providers(self):
        """Initialize all configured providers"""
        # ElevenLabs
        elevenlabs_config = self.config.get("elevenlabs", {})
        if elevenlabs_config.get("enabled", False):
            provider = ElevenLabsProvider(elevenlabs_config)
            self.providers[TTSProviderType.ELEVENLABS] = LegacyTTSProviderAdapter(provider, TTSProviderType.ELEVENLABS)

        # Edge TTS
        edge_config = self.config.get("edge_tts", {})
        if edge_config.get("enabled", True):  # Enabled by default
            provider = EdgeTTSProvider(edge_config)
            self.providers[TTSProviderType.EDGE_TTS] = LegacyTTSProviderAdapter(provider, TTSProviderType.EDGE_TTS)

        # Coqui TTS
        coqui_config = self.config.get("coqui", {})
        if coqui_config.get("enabled", False):
            provider = CoquiProvider(coqui_config)
            self.providers[TTSProviderType.COQUI] = LegacyTTSProviderAdapter(provider, TTSProviderType.COQUI)

        # OpenAI TTS
        openai_config = self.config.get("openai", {})
        if openai_config.get("enabled", False):
            self.providers[TTSProviderType.OPENAI] = OpenAITTSAdapter(openai_config)

        self.logger.info(f"Initialized {len(self.providers)} TTS providers")

    def get_available_providers(self) -> list[TTSProviderType]:
        """Get list of available providers"""
        available = []
        for provider_type, provider in self.providers.items():
            if provider.is_available():
                available.append(provider_type)
        return available

    def select_provider(self, request: TTSRequest) -> Optional[TTSProviderAdapter]:
        """Select best provider for request"""
        # If specific provider requested and available
        if request.provider_preference and request.provider_preference in self.providers:
            provider = self.providers[request.provider_preference]
            if provider.is_available():
                return provider

        # Select based on priority and availability
        for provider_type in self.provider_priority:
            if provider_type in self.providers:
                provider = self.providers[provider_type]
                if provider.is_available():
                    return provider

        return None

    def get_all_voices(self) -> dict[str, list[dict[str, Any]]]:
        """Get all voices from all providers"""
        all_voices = {}
        for provider_type, provider in self.providers.items():
            if provider.is_available():
                try:
                    voices = provider.get_supported_voices()
                    all_voices[provider_type.value] = voices
                except Exception as e:
                    self.logger.error(f"Failed to get voices from {provider_type.value}: {e}")
        return all_voices


class LUKHASTTSService:
    """Main LUKHAS TTS service with Trinity Framework integration"""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}
        self.logger = get_logger(f"{__name__}.LUKHASTTSService")
        self.guardian = GuardianValidator()

        # Initialize components
        self.provider_manager = TTSProviderManager(self.config.get("providers", {}))
        self.voice_modulator = VoiceModulator(self.config.get("modulator", {}))
        self.audio_processor = LUKHASAudioProcessor(self.config.get("audio_processor", {}))

        # Service statistics
        self.stats = {
            "requests_total": 0,
            "requests_successful": 0,
            "requests_failed": 0,
            "average_processing_time": 0.0,
            "providers_used": {},
            "start_time": time.time(),
        }

        # Cache for recent results (simple in-memory cache)
        self.response_cache = {}
        self.cache_max_size = self.config.get("cache_max_size", 100)

        self.logger.info("LUKHAS TTS Service initialized")

    async def synthesize_speech(self, request: TTSRequest) -> TTSResponse:
        """
        Main TTS synthesis method with full LUKHAS integration

        Args:
            request: TTS request with text and parameters

        Returns:
            TTS response with audio data and metadata
        """
        start_time = time.time()
        self.stats["requests_total"] += 1

        try:
            # Guardian validation
            validation_result = await self.guardian.validate_operation(
                {
                    "operation_type": "tts_synthesis",
                    "text_length": len(request.text),
                    "request": request.to_dict(),
                }
            )

            if not validation_result.get("approved", False):
                return TTSResponse(
                    success=False,
                    error_message=f"Guardian rejected TTS request: {validation_result.get('reason')}",
                    error_code="GUARDIAN_REJECTED",
                )

            # Check cache first
            cache_key = self._generate_cache_key(request)
            if cache_key in self.response_cache:
                cached_response = self.response_cache[cache_key]
                cached_response.metadata["from_cache"] = True
                return cached_response

            # Select provider
            provider = self.provider_manager.select_provider(request)
            if not provider:
                return TTSResponse(
                    success=False,
                    error_message="No available TTS providers",
                    error_code="NO_PROVIDERS",
                )

            # Synthesize speech
            tts_response = await provider.synthesize(request)

            if not tts_response.success:
                self.stats["requests_failed"] += 1
                return tts_response

            # Apply voice modulation if requested
            if request.modulation_mode and tts_response.audio_data:
                try:
                    modulated_audio, mod_metadata = await self.voice_modulator.modulate(
                        tts_response.audio_data,
                        request.modulation_mode,
                        request.context,
                    )

                    if mod_metadata.get("success", False):
                        tts_response.audio_data = modulated_audio
                        tts_response.modulation_applied = True
                        tts_response.metadata["modulation"] = mod_metadata

                except Exception as e:
                    self.logger.warning(f"Voice modulation failed: {e!s}")
                    # Continue without modulation

            # Apply audio processing if requested
            if request.apply_audio_processing and tts_response.audio_data:
                try:
                    processed_audio, proc_metadata = await self.audio_processor.process_audio(
                        tts_response.audio_data,
                        tts_response.sample_rate,
                        1,  # Assume mono for now
                        quality=request.audio_processing_quality,
                        context=request.context,
                    )

                    if proc_metadata.get("success", False):
                        tts_response.audio_data = processed_audio
                        tts_response.audio_processing_applied = True
                        tts_response.metadata["audio_processing"] = proc_metadata

                except Exception as e:
                    self.logger.warning(f"Audio processing failed: {e!s}")
                    # Continue without processing

            # Update processing time
            total_time = (time.time() - start_time) * 1000
            tts_response.processing_time_ms = total_time

            # Update statistics
            self.stats["requests_successful"] += 1
            provider_type = provider.get_provider_type().value
            self.stats["providers_used"][provider_type] = self.stats["providers_used"].get(provider_type, 0) + 1

            # Update average processing time
            self.stats["average_processing_time"] = (
                self.stats["average_processing_time"] * (self.stats["requests_successful"] - 1) + total_time
            ) / self.stats["requests_successful"]

            # Cache response
            if len(self.response_cache) < self.cache_max_size:
                self.response_cache[cache_key] = tts_response

            # Emit GLYPH event
            create_glyph(
                GLYPHSymbol.CREATE,
                "voice_pipeline",
                "consciousness",
                {
                    "event": "tts.synthesis.completed",
                    "data": {
                        "provider": provider_type,
                        "processing_time_ms": total_time,
                        "text_length": len(request.text),
                        "audio_duration": tts_response.duration_seconds,
                        "modulation_applied": tts_response.modulation_applied,
                        "audio_processing_applied": tts_response.audio_processing_applied,
                    },
                },
            )

            return tts_response

        except Exception as e:
            self.logger.error(f"TTS synthesis failed: {e!s}")
            self.stats["requests_failed"] += 1

            # Create GLYPH event
            create_glyph(
                GLYPHSymbol.CREATE,
                "voice_pipeline",
                "consciousness",
                {
                    "event": "tts.synthesis.error",
                    "data": {"error": str(e), "text_length": len(request.text)},
                },
            )

            return TTSResponse(
                success=False,
                error_message=str(e),
                error_code="SYNTHESIS_ERROR",
                processing_time_ms=(time.time() - start_time) * 1000,
            )

    def _generate_cache_key(self, request: TTSRequest) -> str:
        """Generate cache key for request"""
        # Use hash of key request parameters
        key_params = {
            "text": request.text,
            "voice_id": request.voice_id,
            "emotion": request.emotion,
            "speed": request.speed,
            "pitch": request.pitch,
            "volume": request.volume,
            "quality": request.quality.value,
            "provider": (request.provider_preference.value if request.provider_preference else None),
        }
        return str(hash(json.dumps(key_params, sort_keys=True)))

    async def get_available_voices(self) -> dict[str, list[dict[str, Any]]]:
        """Get all available voices from all providers"""
        return self.provider_manager.get_all_voices()

    async def get_service_health(self) -> dict[str, Any]:
        """Get service health status"""
        available_providers = self.provider_manager.get_available_providers()

        return {
            "status": "healthy" if available_providers else "degraded",
            "available_providers": [p.value for p in available_providers],
            "total_providers": len(self.provider_manager.providers),
            "stats": self.stats.copy(),
            "uptime_seconds": time.time() - self.stats["start_time"],
        }

    def clear_cache(self):
        """Clear response cache"""
        self.response_cache.clear()
        self.logger.info("TTS response cache cleared")

    async def preload_voices(self, provider_types: Optional[list[TTSProviderType]] = None):
        """Preload voice information from providers"""
        if provider_types is None:
            provider_types = list(self.provider_manager.providers.keys())

        for provider_type in provider_types:
            if provider_type in self.provider_manager.providers:
                try:
                    provider = self.provider_manager.providers[provider_type]
                    if provider.is_available():
                        voices = provider.get_supported_voices()
                        self.logger.info(f"Preloaded {len(voices)} voices from {provider_type.value}")
                except Exception as e:
                    self.logger.error(f"Failed to preload voices from {provider_type.value}: {e}")


# Convenience functions for common use cases
async def text_to_speech(
    text: str,
    voice_id: Optional[str] = None,
    emotion: Optional[str] = None,
    quality: TTSQuality = TTSQuality.STANDARD,
    provider: Optional[TTSProviderType] = None,
) -> TTSResponse:
    """
    Simple text-to-speech conversion

    Args:
        text: Text to convert
        voice_id: Voice to use
        emotion: Emotion to apply
        quality: Quality level
        provider: Preferred provider

    Returns:
        TTS response
    """
    # Create default service (would normally be singleton)
    service = LUKHASTTSService()

    request = TTSRequest(
        text=text,
        voice_id=voice_id,
        emotion=emotion,
        quality=quality,
        provider_preference=provider,
    )

    return await service.synthesize_speech(request)


# Export main classes
__all__ = [
    "LUKHASTTSService",
    "TTSProviderAdapter",
    "TTSProviderManager",
    "TTSProviderType",
    "TTSQuality",
    "TTSRequest",
    "TTSResponse",
    "text_to_speech",
]
