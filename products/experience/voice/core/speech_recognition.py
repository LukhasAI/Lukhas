"""
LUKHAS AI Speech Recognition System
Advanced speech recognition with multiple providers and Trinity Framework integration.
⚛️ Identity-aware recognition models
🧠 Consciousness-driven transcription enhancement
🛡️ Guardian-validated speech processing
"""

import os
import tempfile
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

import numpy as np

from candidate.core.common.glyph import GLYPHToken, GLYPHSymbol, create_glyph
from candidate.core.common.logger import get_logger
from candidate.governance.guardian import GuardianValidator
from candidate.voice.audio_processing import AudioFormat, LUKHASAudioProcessor

logger = get_logger(__name__)


class SpeechRecognitionProvider(Enum):
    """Speech recognition providers"""

    WHISPER_OPENAI = "whisper_openai"
    WHISPER_LOCAL = "whisper_local"
    GOOGLE_SPEECH = "google_speech"
    AZURE_SPEECH = "azure_speech"
    AWS_TRANSCRIBE = "aws_transcribe"
    ASSEMBLYAI = "assemblyai"


class RecognitionQuality(Enum):
    """Recognition quality levels"""

    FAST = "fast"  # Speed optimized
    BALANCED = "balanced"  # Balance of speed and accuracy
    ACCURATE = "accurate"  # Accuracy optimized
    PREMIUM = "premium"  # Highest accuracy, slowest


class LanguageCode(Enum):
    """Supported language codes"""

    EN_US = "en-US"
    EN_GB = "en-GB"
    ES_ES = "es-ES"
    FR_FR = "fr-FR"
    DE_DE = "de-DE"
    IT_IT = "it-IT"
    PT_BR = "pt-BR"
    RU_RU = "ru-RU"
    JA_JP = "ja-JP"
    KO_KR = "ko-KR"
    ZH_CN = "zh-CN"
    AR_SA = "ar-SA"


@dataclass
class SpeechRecognitionRequest:
    """Speech recognition request"""

    audio_data: bytes
    audio_format: AudioFormat = AudioFormat.PCM_16
    sample_rate: int = 16000
    channels: int = 1

    # Recognition parameters
    language: LanguageCode = LanguageCode.EN_US
    quality: RecognitionQuality = RecognitionQuality.BALANCED
    provider_preference: Optional[SpeechRecognitionProvider] = None

    # Advanced options
    enable_word_timestamps: bool = False
    enable_confidence_scores: bool = True
    enable_speaker_diarization: bool = False
    enable_punctuation: bool = True
    enable_automatic_punctuation: bool = True

    # Context for better recognition
    context_phrases: list[str] = field(default_factory=list)
    vocabulary_hints: list[str] = field(default_factory=list)

    # Processing options
    noise_reduction: bool = True
    voice_activity_detection: bool = True

    # User context
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    context: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "audio_data_size": len(self.audio_data),
            "audio_format": self.audio_format.value,
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "language": self.language.value,
            "quality": self.quality.value,
            "provider_preference": (self.provider_preference.value if self.provider_preference else None),
            "enable_word_timestamps": self.enable_word_timestamps,
            "enable_confidence_scores": self.enable_confidence_scores,
            "enable_speaker_diarization": self.enable_speaker_diarization,
            "enable_punctuation": self.enable_punctuation,
            "enable_automatic_punctuation": self.enable_automatic_punctuation,
            "context_phrases": self.context_phrases,
            "vocabulary_hints": self.vocabulary_hints,
            "noise_reduction": self.noise_reduction,
            "voice_activity_detection": self.voice_activity_detection,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "context": self.context,
        }


@dataclass
class WordTimestamp:
    """Word-level timestamp information"""

    word: str
    start_time: float
    end_time: float
    confidence: float = 1.0


@dataclass
class SpeechSegment:
    """Speech segment with metadata"""

    text: str
    start_time: float
    end_time: float
    confidence: float
    speaker_id: Optional[str] = None
    language: Optional[str] = None
    words: list[WordTimestamp] = field(default_factory=list)


@dataclass
class SpeechRecognitionResult:
    """Speech recognition result"""

    success: bool
    text: str = ""
    confidence: float = 0.0

    # Detailed results
    segments: list[SpeechSegment] = field(default_factory=list)
    alternatives: list[str] = field(default_factory=list)

    # Provider information
    provider_used: Optional[str] = None
    language_detected: Optional[str] = None

    # Processing information
    processing_time_ms: float = 0.0
    audio_duration_seconds: float = 0.0

    # Error information
    error_message: Optional[str] = None
    error_code: Optional[str] = None

    # Quality metrics
    quality_metrics: dict[str, float] = field(default_factory=dict)

    # Metadata
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "success": self.success,
            "text": self.text,
            "confidence": self.confidence,
            "segments": [
                {
                    "text": seg.text,
                    "start_time": seg.start_time,
                    "end_time": seg.end_time,
                    "confidence": seg.confidence,
                    "speaker_id": seg.speaker_id,
                    "language": seg.language,
                    "words": [
                        {
                            "word": w.word,
                            "start_time": w.start_time,
                            "end_time": w.end_time,
                            "confidence": w.confidence,
                        }
                        for w in seg.words
                    ],
                }
                for seg in self.segments
            ],
            "alternatives": self.alternatives,
            "provider_used": self.provider_used,
            "language_detected": self.language_detected,
            "processing_time_ms": self.processing_time_ms,
            "audio_duration_seconds": self.audio_duration_seconds,
            "error_message": self.error_message,
            "error_code": self.error_code,
            "quality_metrics": self.quality_metrics,
            "metadata": self.metadata,
        }


class SpeechRecognitionProviderAdapter(ABC):
    """Abstract adapter for speech recognition providers"""

    @abstractmethod
    async def recognize(self, request: SpeechRecognitionRequest) -> SpeechRecognitionResult:
        """Recognize speech from audio"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available"""
        pass

    @abstractmethod
    def get_supported_languages(self) -> list[LanguageCode]:
        """Get list of supported languages"""
        pass

    @abstractmethod
    def get_provider_type(self) -> SpeechRecognitionProvider:
        """Get provider type"""
        pass


class WhisperOpenAIAdapter(SpeechRecognitionProviderAdapter):
    """OpenAI Whisper API adapter"""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.api_key = config.get("api_key")
        self.logger = get_logger(f"{__name__}.WhisperOpenAIAdapter")

    async def recognize(self, request: SpeechRecognitionRequest) -> SpeechRecognitionResult:
        """Recognize speech using OpenAI Whisper API"""
        start_time = time.time()

        try:
            import openai

            client = openai.AsyncOpenAI(api_key=self.api_key)

            # Create temporary audio file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(request.audio_data)
                temp_file_path = temp_file.name

            try:
                # Select model based on quality
                model = "whisper-1"  # OpenAI only has one model

                # Prepare parameters
                params = {
                    "file": open(temp_file_path, "rb"),
                    "model": model,
                    "language": request.language.value.split("-")[0],  # Convert en-US to en
                }

                # Add optional parameters
                if request.enable_word_timestamps:
                    params["timestamp_granularities"] = ["word"]

                if request.context_phrases or request.vocabulary_hints:
                    # Combine context phrases and vocabulary hints
                    prompt = " ".join(request.context_phrases + request.vocabulary_hints)
                    params["prompt"] = prompt[:224]  # Whisper prompt limit

                # Call API
                if request.enable_word_timestamps:
                    response = await client.audio.transcriptions.create(response_format="verbose_json", **params)
                else:
                    response = await client.audio.transcriptions.create(response_format="json", **params)

                # Process response
                text = response.text
                processing_time = (time.time() - start_time) * 1000

                # Calculate audio duration
                audio_duration = len(request.audio_data) / (request.sample_rate * 2)  # 16-bit PCM

                # Create segments from response
                segments = []
                if hasattr(response, "segments"):
                    for seg in response.segments:
                        words = []
                        if hasattr(seg, "words"):
                            words = [
                                WordTimestamp(
                                    word=w.word,
                                    start_time=w.start,
                                    end_time=w.end,
                                    confidence=1.0,  # OpenAI doesn't provide word confidence
                                )
                                for w in seg.words
                            ]

                        segments.append(
                            SpeechSegment(
                                text=seg.text,
                                start_time=seg.start,
                                end_time=seg.end,
                                confidence=1.0,  # OpenAI doesn't provide segment confidence
                                words=words,
                            )
                        )

                return SpeechRecognitionResult(
                    success=True,
                    text=text,
                    confidence=1.0,  # OpenAI doesn't provide overall confidence
                    segments=segments,
                    provider_used="whisper_openai",
                    language_detected=request.language.value,
                    processing_time_ms=processing_time,
                    audio_duration_seconds=audio_duration,
                    metadata={"model": model},
                )

            finally:
                # Clean up temporary file
                os.unlink(temp_file_path)

        except Exception as e:
            self.logger.error(f"OpenAI Whisper recognition failed: {e!s}")
            return SpeechRecognitionResult(
                success=False,
                error_message=str(e),
                provider_used="whisper_openai",
                processing_time_ms=(time.time() - start_time) * 1000,
            )

    def is_available(self) -> bool:
        """Check if OpenAI Whisper is available"""
        return self.api_key is not None and len(self.api_key) > 0

    def get_supported_languages(self) -> list[LanguageCode]:
        """Get supported languages"""
        return [
            LanguageCode.EN_US,
            LanguageCode.EN_GB,
            LanguageCode.ES_ES,
            LanguageCode.FR_FR,
            LanguageCode.DE_DE,
            LanguageCode.IT_IT,
            LanguageCode.PT_BR,
            LanguageCode.RU_RU,
            LanguageCode.JA_JP,
            LanguageCode.KO_KR,
            LanguageCode.ZH_CN,
            LanguageCode.AR_SA,
        ]

    def get_provider_type(self) -> SpeechRecognitionProvider:
        """Get provider type"""
        return SpeechRecognitionProvider.WHISPER_OPENAI


class WhisperLocalAdapter(SpeechRecognitionProviderAdapter):
    """Local Whisper model adapter"""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.model_name = config.get("model_name", "base")
        self.device = config.get("device", "cpu")
        self.model = None
        self.logger = get_logger(f"{__name__}.WhisperLocalAdapter")

    def _load_model(self):
        """Load Whisper model"""
        if self.model is None:
            try:
                import whisper

                self.model = whisper.load_model(self.model_name, device=self.device)
                self.logger.info(f"Loaded Whisper model: {self.model_name}")
            except ImportError:
                self.logger.error("Whisper package not installed")
                raise
            except Exception as e:
                self.logger.error(f"Failed to load Whisper model: {e!s}")
                raise

    async def recognize(self, request: SpeechRecognitionRequest) -> SpeechRecognitionResult:
        """Recognize speech using local Whisper model"""
        start_time = time.time()

        try:
            self._load_model()

            # Create temporary audio file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(request.audio_data)
                temp_file_path = temp_file.name

            try:
                # Prepare options
                options = {
                    "language": request.language.value.split("-")[0],
                    "task": "transcribe",
                }

                if request.enable_word_timestamps:
                    options["word_timestamps"] = True

                # Run inference
                result = self.model.transcribe(temp_file_path, **options)

                # Process result
                text = result["text"]
                processing_time = (time.time() - start_time) * 1000

                # Calculate audio duration
                audio_duration = len(request.audio_data) / (request.sample_rate * 2)

                # Create segments
                segments = []
                if "segments" in result:
                    for seg in result["segments"]:
                        words = []
                        if "words" in seg:
                            words = [
                                WordTimestamp(
                                    word=w["word"],
                                    start_time=w["start"],
                                    end_time=w["end"],
                                    confidence=w.get("probability", 1.0),
                                )
                                for w in seg["words"]
                            ]

                        segments.append(
                            SpeechSegment(
                                text=seg["text"],
                                start_time=seg["start"],
                                end_time=seg["end"],
                                confidence=seg.get("avg_logprob", 0.0) + 1.0,  # Convert logprob to 0-1 range
                                words=words,
                            )
                        )

                # Overall confidence from segments
                overall_confidence = np.mean([seg.confidence for seg in segments]) if segments else 0.8

                return SpeechRecognitionResult(
                    success=True,
                    text=text,
                    confidence=overall_confidence,
                    segments=segments,
                    provider_used="whisper_local",
                    language_detected=result.get("language", request.language.value),
                    processing_time_ms=processing_time,
                    audio_duration_seconds=audio_duration,
                    metadata={"model": self.model_name, "device": self.device},
                )

            finally:
                # Clean up temporary file
                os.unlink(temp_file_path)

        except Exception as e:
            self.logger.error(f"Local Whisper recognition failed: {e!s}")
            return SpeechRecognitionResult(
                success=False,
                error_message=str(e),
                provider_used="whisper_local",
                processing_time_ms=(time.time() - start_time) * 1000,
            )

    def is_available(self) -> bool:
        """Check if local Whisper is available"""
        try:
            import whisper

            return True
        except ImportError:
            return False

    def get_supported_languages(self) -> list[LanguageCode]:
        """Get supported languages"""
        return [
            LanguageCode.EN_US,
            LanguageCode.EN_GB,
            LanguageCode.ES_ES,
            LanguageCode.FR_FR,
            LanguageCode.DE_DE,
            LanguageCode.IT_IT,
            LanguageCode.PT_BR,
            LanguageCode.RU_RU,
            LanguageCode.JA_JP,
            LanguageCode.KO_KR,
            LanguageCode.ZH_CN,
            LanguageCode.AR_SA,
        ]

    def get_provider_type(self) -> SpeechRecognitionProvider:
        """Get provider type"""
        return SpeechRecognitionProvider.WHISPER_LOCAL


class GoogleSpeechAdapter(SpeechRecognitionProviderAdapter):
    """Google Cloud Speech-to-Text adapter"""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.credentials_path = config.get("credentials_path")
        self.project_id = config.get("project_id")
        self.logger = get_logger(f"{__name__}.GoogleSpeechAdapter")

    async def recognize(self, request: SpeechRecognitionRequest) -> SpeechRecognitionResult:
        """Recognize speech using Google Cloud Speech-to-Text"""
        start_time = time.time()

        try:
            from google.cloud import speech

            # Initialize client
            if self.credentials_path:
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.credentials_path

            client = speech.SpeechClient()

            # Configure recognition
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=request.sample_rate,
                language_code=request.language.value,
                enable_automatic_punctuation=request.enable_automatic_punctuation,
                enable_word_time_offsets=request.enable_word_timestamps,
                enable_word_confidence=request.enable_confidence_scores,
                max_alternatives=3 if request.enable_confidence_scores else 1,
            )

            # Add speech contexts for better recognition
            if request.context_phrases or request.vocabulary_hints:
                speech_contexts = [speech.SpeechContext(phrases=request.context_phrases + request.vocabulary_hints)]
                config.speech_contexts = speech_contexts

            # Create audio object
            audio = speech.RecognitionAudio(content=request.audio_data)

            # Recognize speech
            response = client.recognize(config=config, audio=audio)

            processing_time = (time.time() - start_time) * 1000

            if not response.results:
                return SpeechRecognitionResult(
                    success=False,
                    error_message="No speech detected",
                    provider_used="google_speech",
                    processing_time_ms=processing_time,
                )

            # Process results
            best_result = response.results[0]
            best_alternative = best_result.alternatives[0]

            text = best_alternative.transcript
            confidence = best_alternative.confidence

            # Get alternatives
            alternatives = [alt.transcript for alt in best_result.alternatives[1:]]

            # Create word timestamps if available
            words = []
            if hasattr(best_alternative, "words"):
                words = [
                    WordTimestamp(
                        word=w.word,
                        start_time=w.start_time.total_seconds(),
                        end_time=w.end_time.total_seconds(),
                        confidence=w.confidence if hasattr(w, "confidence") else 1.0,
                    )
                    for w in best_alternative.words
                ]

            # Create segment
            audio_duration = len(request.audio_data) / (request.sample_rate * 2)
            segments = [
                SpeechSegment(
                    text=text,
                    start_time=0.0,
                    end_time=audio_duration,
                    confidence=confidence,
                    words=words,
                )
            ]

            return SpeechRecognitionResult(
                success=True,
                text=text,
                confidence=confidence,
                segments=segments,
                alternatives=alternatives,
                provider_used="google_speech",
                processing_time_ms=processing_time,
                audio_duration_seconds=audio_duration,
            )

        except Exception as e:
            self.logger.error(f"Google Speech recognition failed: {e!s}")
            return SpeechRecognitionResult(
                success=False,
                error_message=str(e),
                provider_used="google_speech",
                processing_time_ms=(time.time() - start_time) * 1000,
            )

    def is_available(self) -> bool:
        """Check if Google Speech is available"""
        try:
            from google.cloud import speech

            return self.credentials_path is not None or "GOOGLE_APPLICATION_CREDENTIALS" in os.environ
        except ImportError:
            return False

    def get_supported_languages(self) -> list[LanguageCode]:
        """Get supported languages"""
        return [
            LanguageCode.EN_US,
            LanguageCode.EN_GB,
            LanguageCode.ES_ES,
            LanguageCode.FR_FR,
            LanguageCode.DE_DE,
            LanguageCode.IT_IT,
            LanguageCode.PT_BR,
            LanguageCode.RU_RU,
            LanguageCode.JA_JP,
            LanguageCode.KO_KR,
            LanguageCode.ZH_CN,
            LanguageCode.AR_SA,
        ]

    def get_provider_type(self) -> SpeechRecognitionProvider:
        """Get provider type"""
        return SpeechRecognitionProvider.GOOGLE_SPEECH


class SpeechRecognitionProviderManager:
    """Manager for speech recognition providers"""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.logger = get_logger(f"{__name__}.SpeechRecognitionProviderManager")

        # Initialize providers
        self.providers: dict[SpeechRecognitionProvider, SpeechRecognitionProviderAdapter] = {}
        self._initialize_providers()

        # Provider priority
        self.provider_priority = [
            SpeechRecognitionProvider.WHISPER_OPENAI,
            SpeechRecognitionProvider.GOOGLE_SPEECH,
            SpeechRecognitionProvider.WHISPER_LOCAL,
        ]

    def _initialize_providers(self):
        """Initialize configured providers"""
        # OpenAI Whisper
        openai_config = self.config.get("whisper_openai", {})
        if openai_config.get("enabled", False):
            self.providers[SpeechRecognitionProvider.WHISPER_OPENAI] = WhisperOpenAIAdapter(openai_config)

        # Local Whisper
        local_config = self.config.get("whisper_local", {})
        if local_config.get("enabled", True):  # Enabled by default if available
            provider = WhisperLocalAdapter(local_config)
            if provider.is_available():
                self.providers[SpeechRecognitionProvider.WHISPER_LOCAL] = provider

        # Google Speech
        google_config = self.config.get("google_speech", {})
        if google_config.get("enabled", False):
            provider = GoogleSpeechAdapter(google_config)
            if provider.is_available():
                self.providers[SpeechRecognitionProvider.GOOGLE_SPEECH] = provider

        self.logger.info(f"Initialized {len(self.providers)} speech recognition providers")

    def get_available_providers(self) -> list[SpeechRecognitionProvider]:
        """Get available providers"""
        available = []
        for provider_type, provider in self.providers.items():
            if provider.is_available():
                available.append(provider_type)
        return available

    def select_provider(self, request: SpeechRecognitionRequest) -> Optional[SpeechRecognitionProviderAdapter]:
        """Select best provider for request"""
        # If specific provider requested
        if request.provider_preference and request.provider_preference in self.providers:
            provider = self.providers[request.provider_preference]
            if provider.is_available():
                return provider

        # Select based on priority and availability
        for provider_type in self.provider_priority:
            if provider_type in self.providers:
                provider = self.providers[provider_type]
                if provider.is_available():
                    # Check language support
                    supported_languages = provider.get_supported_languages()
                    if request.language in supported_languages:
                        return provider

        return None


class LUKHASSpeechRecognitionService:
    """Main LUKHAS speech recognition service"""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}
        self.logger = get_logger(f"{__name__}.LUKHASSpeechRecognitionService")
        self.guardian = GuardianValidator()

        # Initialize components
        self.provider_manager = SpeechRecognitionProviderManager(self.config.get("providers", {}))
        self.audio_processor = LUKHASAudioProcessor(self.config.get("audio_processor", {}))

        # Service statistics
        self.stats = {
            "recognitions_total": 0,
            "recognitions_successful": 0,
            "recognitions_failed": 0,
            "average_processing_time": 0.0,
            "providers_used": {},
            "languages_processed": {},
        }

        self.logger.info("LUKHAS Speech Recognition Service initialized")

    async def recognize_speech(self, request: SpeechRecognitionRequest) -> SpeechRecognitionResult:
        """
        Recognize speech from audio data

        Args:
            request: Speech recognition request

        Returns:
            Speech recognition result
        """
        start_time = time.time()
        self.stats["recognitions_total"] += 1

        try:
            # Guardian validation
            validation_result = await self.guardian.validate_operation(
                {
                    "operation_type": "speech_recognition",
                    "audio_length": len(request.audio_data),
                    "request": request.to_dict(),
                }
            )

            if not validation_result.get("approved", False):
                return SpeechRecognitionResult(
                    success=False,
                    error_message=f"Guardian rejected recognition: {validation_result.get('reason')}",
                    error_code="GUARDIAN_REJECTED",
                )

            # Pre-process audio if requested
            processed_audio_data = request.audio_data
            if request.noise_reduction or request.voice_activity_detection:
                try:
                    processed_audio_data, proc_metadata = await self.audio_processor.process_audio(
                        request.audio_data,
                        request.sample_rate,
                        request.channels,
                        request.audio_format,
                    )

                    if proc_metadata.get("success", False):
                        request.audio_data = processed_audio_data
                        self.logger.debug("Applied audio pre-processing for recognition")

                except Exception as e:
                    self.logger.warning(f"Audio pre-processing failed: {e!s}")
                    # Continue with original audio

            # Select provider
            provider = self.provider_manager.select_provider(request)
            if not provider:
                return SpeechRecognitionResult(
                    success=False,
                    error_message="No available speech recognition providers",
                    error_code="NO_PROVIDERS",
                )

            # Recognize speech
            result = await provider.recognize(request)

            if result.success:
                self.stats["recognitions_successful"] += 1

                # Update provider usage stats
                provider_type = provider.get_provider_type().value
                self.stats["providers_used"][provider_type] = self.stats["providers_used"].get(provider_type, 0) + 1

                # Update language stats
                language = request.language.value
                self.stats["languages_processed"][language] = self.stats["languages_processed"].get(language, 0) + 1

                # Update average processing time
                total_time = (time.time() - start_time) * 1000
                result.processing_time_ms = total_time

                self.stats["average_processing_time"] = (
                    self.stats["average_processing_time"] * (self.stats["recognitions_successful"] - 1) + total_time
                ) / self.stats["recognitions_successful"]

                # Emit GLYPH event
                # Create GLYPH event
        glyph_token = create_glyph(GLYPHSymbol.CREATE, "voice_pipeline", "consciousness", {
                    "speech.recognition.completed",
                    {
                        "provider": provider_type,
                        "language": language,
                        "processing_time_ms": total_time,
                        "text_length": len(result.text),
                        "confidence": result.confidence,
                    },
                )
            else:
                self.stats["recognitions_failed"] += 1

                # Create GLYPH event
        glyph_token = create_glyph(GLYPHSymbol.CREATE, "voice_pipeline", "consciousness", {
                    "speech.recognition.error",
                    {
                        "provider": provider.get_provider_type().value,
                        "error": result.error_message,
                    },
                )

            return result

        except Exception as e:
            self.logger.error(f"Speech recognition failed: {e!s}")
            self.stats["recognitions_failed"] += 1

            return SpeechRecognitionResult(
                success=False,
                error_message=str(e),
                error_code="RECOGNITION_ERROR",
                processing_time_ms=(time.time() - start_time) * 1000,
            )

    async def recognize_from_file(
        self,
        file_path: str,
        language: LanguageCode = LanguageCode.EN_US,
        quality: RecognitionQuality = RecognitionQuality.BALANCED,
    ) -> SpeechRecognitionResult:
        """
        Recognize speech from audio file

        Args:
            file_path: Path to audio file
            language: Language code
            quality: Recognition quality

        Returns:
            Speech recognition result
        """
        try:
            # Read audio file
            with open(file_path, "rb") as f:
                audio_data = f.read()

            # Create request
            request = SpeechRecognitionRequest(audio_data=audio_data, language=language, quality=quality)

            return await self.recognize_speech(request)

        except Exception as e:
            self.logger.error(f"File recognition failed: {e!s}")
            return SpeechRecognitionResult(success=False, error_message=str(e), error_code="FILE_ERROR")

    async def get_service_health(self) -> dict[str, Any]:
        """Get service health status"""
        available_providers = self.provider_manager.get_available_providers()

        return {
            "status": "healthy" if available_providers else "degraded",
            "available_providers": [p.value for p in available_providers],
            "total_providers": len(self.provider_manager.providers),
            "stats": self.stats.copy(),
        }

    def get_supported_languages(self) -> dict[str, list[LanguageCode]]:
        """Get supported languages by provider"""
        languages_by_provider = {}
        for provider_type, provider in self.provider_manager.providers.items():
            if provider.is_available():
                languages_by_provider[provider_type.value] = provider.get_supported_languages()
        return languages_by_provider


# Convenience function
async def transcribe_audio(
    audio_data: bytes,
    language: LanguageCode = LanguageCode.EN_US,
    quality: RecognitionQuality = RecognitionQuality.BALANCED,
) -> str:
    """
    Simple audio transcription

    Args:
        audio_data: Audio data as bytes
        language: Language code
        quality: Recognition quality

    Returns:
        Transcribed text
    """
    service = LUKHASSpeechRecognitionService()

    request = SpeechRecognitionRequest(audio_data=audio_data, language=language, quality=quality)

    result = await service.recognize_speech(request)

    if result.success:
        return result.text
    else:
        raise RuntimeError(f"Transcription failed: {result.error_message}")


# Export main classes
__all__ = [
    "LUKHASSpeechRecognitionService",
    "LanguageCode",
    "RecognitionQuality",
    "SpeechRecognitionProvider",
    "SpeechRecognitionRequest",
    "SpeechRecognitionResult",
    "SpeechSegment",
    "WordTimestamp",
    "transcribe_audio",
]
