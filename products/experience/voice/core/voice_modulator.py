"""
LUKHAS AI Voice Modulator System
Implements comprehensive voice modulation capabilities with Trinity Framework integration.
⚛️ Identity-conscious voice adaptation
🧠 Context-aware processing
🛡️ Guardian-validated operations
"""

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, Union

import numpy as np

from candidate.core.common.glyph import GLYPHToken, GLYPHSymbol, create_glyph
from candidate.core.common.logger import get_logger
from candidate.governance.guardian import GuardianValidator

logger = get_logger(__name__)


class VoiceModulationMode(Enum):
    """Voice modulation modes for different use cases"""

    NATURAL = "natural"
    EMOTIONAL = "emotional"
    ROBOTIC = "robotic"
    WHISPER = "whisper"
    DRAMATIC = "dramatic"
    PROFESSIONAL = "professional"
    CREATIVE = "creative"
    THERAPEUTIC = "therapeutic"


class AudioFormat(Enum):
    """Supported audio formats"""

    WAV = "wav"
    MP3 = "mp3"
    FLAC = "flac"
    OGG = "ogg"


@dataclass
class VoiceParameters:
    """Voice modulation parameters"""

    pitch_shift: float = 1.0  # Pitch multiplier (0.5-2.0)
    speed_factor: float = 1.0  # Speed multiplier (0.5-2.0)
    volume_gain: float = 1.0  # Volume multiplier (0.0-2.0)

    # Advanced parameters
    formant_shift: float = 1.0  # Formant frequency shift
    breathiness: float = 0.0  # Breathiness level (0.0-1.0)
    roughness: float = 0.0  # Voice roughness (0.0-1.0)
    vibrato_rate: float = 0.0  # Vibrato frequency (Hz)
    vibrato_depth: float = 0.0  # Vibrato depth (0.0-1.0)

    # Emotional parameters
    emotion_intensity: float = 0.5  # Emotional intensity (0.0-1.0)
    valence: float = 0.0  # Emotional valence (-1.0 to 1.0)
    arousal: float = 0.0  # Emotional arousal (-1.0 to 1.0)

    # Context parameters
    context_adaptation: float = 1.0  # Context adaptation strength
    personality_blend: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "pitch_shift": self.pitch_shift,
            "speed_factor": self.speed_factor,
            "volume_gain": self.volume_gain,
            "formant_shift": self.formant_shift,
            "breathiness": self.breathiness,
            "roughness": self.roughness,
            "vibrato_rate": self.vibrato_rate,
            "vibrato_depth": self.vibrato_depth,
            "emotion_intensity": self.emotion_intensity,
            "valence": self.valence,
            "arousal": self.arousal,
            "context_adaptation": self.context_adaptation,
            "personality_blend": self.personality_blend,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "VoiceParameters":
        """Create from dictionary"""
        return cls(
            pitch_shift=data.get("pitch_shift", 1.0),
            speed_factor=data.get("speed_factor", 1.0),
            volume_gain=data.get("volume_gain", 1.0),
            formant_shift=data.get("formant_shift", 1.0),
            breathiness=data.get("breathiness", 0.0),
            roughness=data.get("roughness", 0.0),
            vibrato_rate=data.get("vibrato_rate", 0.0),
            vibrato_depth=data.get("vibrato_depth", 0.0),
            emotion_intensity=data.get("emotion_intensity", 0.5),
            valence=data.get("valence", 0.0),
            arousal=data.get("arousal", 0.0),
            context_adaptation=data.get("context_adaptation", 1.0),
            personality_blend=data.get("personality_blend", {}),
        )


class VoiceModulationEngine(ABC):
    """Abstract base class for voice modulation engines"""

    @abstractmethod
    async def modulate_audio(
        self, audio_data: bytes, parameters: VoiceParameters, sample_rate: int = 44100
    ) -> tuple[bytes, dict[str, Any]]:
        """Modulate audio data with given parameters"""
        pass

    @abstractmethod
    def get_supported_formats(self) -> list[AudioFormat]:
        """Get list of supported audio formats"""
        pass


class LUKHASVoiceModulationEngine(VoiceModulationEngine):
    """LUKHAS AI voice modulation engine with advanced capabilities"""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}
        self.guardian = GuardianValidator()
        self.logger = get_logger(f"{__name__}.LUKHASVoiceModulationEngine")

        # Cache for processed parameters
        self.parameter_cache = {}

        # Emotion mapping for voice parameters
        self.emotion_mappings = {
            "happiness": VoiceParameters(
                pitch_shift=1.1,
                speed_factor=1.05,
                volume_gain=1.1,
                valence=0.8,
                arousal=0.6,
                emotion_intensity=0.7,
            ),
            "sadness": VoiceParameters(
                pitch_shift=0.9,
                speed_factor=0.85,
                volume_gain=0.8,
                breathiness=0.3,
                valence=-0.6,
                arousal=-0.3,
                emotion_intensity=0.6,
            ),
            "anger": VoiceParameters(
                pitch_shift=1.05,
                speed_factor=1.15,
                volume_gain=1.2,
                roughness=0.4,
                valence=-0.5,
                arousal=0.8,
                emotion_intensity=0.8,
            ),
            "fear": VoiceParameters(
                pitch_shift=1.15,
                speed_factor=1.1,
                volume_gain=0.9,
                vibrato_rate=4.0,
                vibrato_depth=0.05,
                valence=-0.4,
                arousal=0.7,
            ),
            "surprise": VoiceParameters(
                pitch_shift=1.2,
                speed_factor=0.95,
                volume_gain=1.05,
                valence=0.3,
                arousal=0.8,
                emotion_intensity=0.6,
            ),
            "disgust": VoiceParameters(
                pitch_shift=0.95,
                speed_factor=0.9,
                volume_gain=0.85,
                roughness=0.2,
                valence=-0.7,
                arousal=0.2,
                emotion_intensity=0.5,
            ),
            "neutral": VoiceParameters(
                pitch_shift=1.0,
                speed_factor=1.0,
                volume_gain=1.0,
                valence=0.0,
                arousal=0.0,
                emotion_intensity=0.3,
            ),
        }

    async def modulate_audio(
        self, audio_data: bytes, parameters: VoiceParameters, sample_rate: int = 44100
    ) -> tuple[bytes, dict[str, Any]]:
        """
        Modulate audio data with advanced voice parameters.
        Implements Trinity Framework compliance with Guardian validation.
        """
        try:
            # Guardian validation - ensure ethical voice processing
            validation_result = await self.guardian.validate_operation(
                {
                    "operation_type": "voice_modulation",
                    "parameters": parameters.to_dict(),
                    "audio_length": len(audio_data),
                    "sample_rate": sample_rate,
                }
            )

            if not validation_result.get("approved", False):
                raise ValueError(f"Guardian rejected voice modulation: {validation_result.get('reason')}")

            # Convert audio data to numpy array
            audio_array = self._bytes_to_audio_array(audio_data, sample_rate)

            # Apply modulation effects in order
            modulated_audio = audio_array.copy()
            processing_metadata = {}

            # 1. Pitch shifting
            if parameters.pitch_shift != 1.0:
                modulated_audio, pitch_meta = await self._apply_pitch_shift(
                    modulated_audio, parameters.pitch_shift, sample_rate
                )
                processing_metadata["pitch_shift"] = pitch_meta

            # 2. Speed/time stretching
            if parameters.speed_factor != 1.0:
                modulated_audio, speed_meta = await self._apply_speed_change(
                    modulated_audio, parameters.speed_factor, sample_rate
                )
                processing_metadata["speed_change"] = speed_meta

            # 3. Volume adjustment
            if parameters.volume_gain != 1.0:
                modulated_audio = self._apply_volume_adjustment(modulated_audio, parameters.volume_gain)
                processing_metadata["volume_adjustment"] = {"gain": parameters.volume_gain}

            # 4. Formant shifting
            if parameters.formant_shift != 1.0:
                modulated_audio, formant_meta = await self._apply_formant_shift(
                    modulated_audio, parameters.formant_shift, sample_rate
                )
                processing_metadata["formant_shift"] = formant_meta

            # 5. Breathiness effect
            if parameters.breathiness > 0.0:
                modulated_audio = await self._apply_breathiness(modulated_audio, parameters.breathiness, sample_rate)
                processing_metadata["breathiness"] = {"level": parameters.breathiness}

            # 6. Roughness effect
            if parameters.roughness > 0.0:
                modulated_audio = await self._apply_roughness(modulated_audio, parameters.roughness, sample_rate)
                processing_metadata["roughness"] = {"level": parameters.roughness}

            # 7. Vibrato effect
            if parameters.vibrato_rate > 0.0 and parameters.vibrato_depth > 0.0:
                modulated_audio = await self._apply_vibrato(
                    modulated_audio,
                    parameters.vibrato_rate,
                    parameters.vibrato_depth,
                    sample_rate,
                )
                processing_metadata["vibrato"] = {
                    "rate": parameters.vibrato_rate,
                    "depth": parameters.vibrato_depth,
                }

            # Convert back to bytes
            output_audio_data = self._audio_array_to_bytes(modulated_audio, sample_rate)

            # Generate GLYPH for voice modulation event
            glyph_data = {
                "type": "VOICE_MODULATION",
                "parameters": parameters.to_dict(),
                "processing_metadata": processing_metadata,
                "quality_metrics": await self._calculate_quality_metrics(audio_array, modulated_audio, sample_rate),
                "guardian_approved": True,
            }

            # Create GLYPH event
        glyph_token = create_glyph(GLYPHSymbol.CREATE, "voice_pipeline", "consciousness", {"voice.modulation.completed", glyph_data)

            return output_audio_data, {
                "success": True,
                "parameters_applied": parameters.to_dict(),
                "processing_metadata": processing_metadata,
                "quality_metrics": glyph_data["quality_metrics"],
            }

        except Exception as e:
            self.logger.error(f"Voice modulation failed: {e!s}")
            # Create GLYPH event
        glyph_token = create_glyph(GLYPHSymbol.CREATE, "voice_pipeline", "consciousness", {
                "voice.modulation.error",
                {"error": str(e), "parameters": parameters.to_dict()},
            )

            return audio_data, {
                "success": False,
                "error": str(e),
                "original_returned": True,
            }

    def get_supported_formats(self) -> list[AudioFormat]:
        """Get supported audio formats"""
        return [AudioFormat.WAV, AudioFormat.MP3, AudioFormat.FLAC]

    async def get_emotion_parameters(self, emotion: str) -> VoiceParameters:
        """Get voice parameters for specific emotion"""
        if emotion in self.emotion_mappings:
            return self.emotion_mappings[emotion]

        # Default to neutral for unknown emotions
        self.logger.warning(f"Unknown emotion '{emotion}', using neutral parameters")
        return self.emotion_mappings["neutral"]

    def _bytes_to_audio_array(self, audio_data: bytes, sample_rate: int) -> np.ndarray:
        """Convert audio bytes to numpy array"""
        # Simple implementation - assumes 16-bit PCM audio
        audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)
        return audio_array / 32768.0  # Normalize to [-1.0, 1.0]

    def _audio_array_to_bytes(self, audio_array: np.ndarray, sample_rate: int) -> bytes:
        """Convert numpy array to audio bytes"""
        # Convert back to 16-bit PCM
        audio_int16 = (audio_array * 32767).astype(np.int16)
        return audio_int16.tobytes()

    async def _apply_pitch_shift(
        self, audio: np.ndarray, shift_factor: float, sample_rate: int
    ) -> tuple[np.ndarray, dict[str, Any]]:
        """Apply pitch shifting using PSOLA-like algorithm"""
        # Simplified pitch shifting implementation
        # In production, use more sophisticated algorithms like PSOLA or phase vocoder

        if abs(shift_factor - 1.0) < 0.01:
            return audio, {"applied": False}

        # Simple resampling-based pitch shift (changes speed too)
        from scipy import signal

        # Calculate new length
        new_length = int(len(audio) / shift_factor)

        # Resample
        pitched_audio = signal.resample(audio, new_length)

        # Pad or truncate to original length
        if len(pitched_audio) > len(audio):
            pitched_audio = pitched_audio[: len(audio)]
        else:
            padding = len(audio) - len(pitched_audio)
            pitched_audio = np.pad(pitched_audio, (0, padding), mode="constant")

        return pitched_audio, {
            "applied": True,
            "shift_factor": shift_factor,
            "algorithm": "resample_based",
        }

    async def _apply_speed_change(
        self, audio: np.ndarray, speed_factor: float, sample_rate: int
    ) -> tuple[np.ndarray, dict[str, Any]]:
        """Apply speed change without pitch shift (time stretching)"""
        if abs(speed_factor - 1.0) < 0.01:
            return audio, {"applied": False}

        # Simple time stretching using overlap-add

        # Calculate new length
        new_length = int(len(audio) / speed_factor)

        # Simple implementation - in production use WSOLA or phase vocoder
        from scipy import signal

        stretched_audio = signal.resample(audio, new_length)

        # Pad or truncate to desired length
        target_length = len(audio)
        if len(stretched_audio) > target_length:
            stretched_audio = stretched_audio[:target_length]
        else:
            padding = target_length - len(stretched_audio)
            stretched_audio = np.pad(stretched_audio, (0, padding), mode="constant")

        return stretched_audio, {
            "applied": True,
            "speed_factor": speed_factor,
            "algorithm": "overlap_add",
        }

    def _apply_volume_adjustment(self, audio: np.ndarray, gain: float) -> np.ndarray:
        """Apply volume gain adjustment"""
        # Apply gain with soft clipping to prevent distortion
        adjusted = audio * gain

        # Soft clipping
        adjusted = np.tanh(adjusted)

        return adjusted

    async def _apply_formant_shift(
        self, audio: np.ndarray, shift_factor: float, sample_rate: int
    ) -> tuple[np.ndarray, dict[str, Any]]:
        """Apply formant frequency shifting"""
        if abs(shift_factor - 1.0) < 0.01:
            return audio, {"applied": False}

        # Simplified formant shifting using spectral envelope manipulation
        # In production, use more sophisticated formant analysis and synthesis

        # Use FFT-based processing
        fft_size = 2048
        hop_length = fft_size // 4

        # Apply spectral envelope shifting
        # This is a simplified version - production would use LPC or cepstral analysis
        window = np.hanning(fft_size)

        # Process in overlapping frames
        output = np.zeros_like(audio)

        for i in range(0, len(audio) - fft_size, hop_length):
            frame = audio[i : i + fft_size] * window

            # FFT
            spectrum = np.fft.rfft(frame)

            # Shift formants by resampling spectrum
            frequencies = np.linspace(0, sample_rate // 2, len(spectrum))
            new_frequencies = frequencies / shift_factor

            # Interpolate spectrum at new frequencies
            shifted_spectrum = np.interp(frequencies, new_frequencies, np.abs(spectrum))

            # Maintain original phase
            phase = np.angle(spectrum)
            new_spectrum = shifted_spectrum * np.exp(1j * phase)

            # IFFT
            shifted_frame = np.fft.irfft(new_spectrum, n=fft_size).real

            # Overlap-add
            output[i : i + fft_size] += shifted_frame * window

        return output, {
            "applied": True,
            "shift_factor": shift_factor,
            "algorithm": "spectral_envelope",
        }

    async def _apply_breathiness(self, audio: np.ndarray, breathiness: float, sample_rate: int) -> np.ndarray:
        """Add breathiness effect to voice"""
        # Add filtered noise to simulate breathiness
        noise = np.random.normal(0, 0.1, len(audio))

        # High-pass filter the noise to simulate breath
        from scipy import signal

        sos = signal.butter(6, 1000, btype="highpass", fs=sample_rate, output="sos")
        filtered_noise = signal.sosfilt(sos, noise)

        # Mix with original audio
        breathy_audio = audio + filtered_noise * breathiness * 0.1

        return breathy_audio

    async def _apply_roughness(self, audio: np.ndarray, roughness: float, sample_rate: int) -> np.ndarray:
        """Add roughness effect to voice"""
        # Add low-frequency modulation to simulate roughness
        t = np.arange(len(audio)) / sample_rate

        # Create roughness modulation (low frequency)
        rough_freq = 8.0  # Hz
        modulation = 1.0 + roughness * 0.3 * np.sin(2 * np.pi * rough_freq * t)

        # Apply modulation
        rough_audio = audio * modulation

        return rough_audio

    async def _apply_vibrato(self, audio: np.ndarray, rate: float, depth: float, sample_rate: int) -> np.ndarray:
        """Add vibrato effect to voice"""
        t = np.arange(len(audio)) / sample_rate

        # Create vibrato modulation
        vibrato_modulation = 1.0 + depth * np.sin(2 * np.pi * rate * t)

        # Apply modulation
        vibrato_audio = audio * vibrato_modulation

        return vibrato_audio

    async def _calculate_quality_metrics(
        self, original: np.ndarray, processed: np.ndarray, sample_rate: int
    ) -> dict[str, float]:
        """Calculate audio quality metrics"""
        # Signal-to-Noise Ratio
        signal_power = np.mean(original**2)
        noise_power = np.mean((processed - original) ** 2)
        snr = 10 * np.log10(signal_power / (noise_power + 1e-10))

        # RMS levels
        original_rms = np.sqrt(np.mean(original**2))
        processed_rms = np.sqrt(np.mean(processed**2))

        # Dynamic range
        dynamic_range = 20 * np.log10(np.max(np.abs(processed)) / (np.std(processed) + 1e-10))

        return {
            "snr_db": float(snr),
            "original_rms": float(original_rms),
            "processed_rms": float(processed_rms),
            "dynamic_range_db": float(dynamic_range),
            "processing_gain_db": 20 * np.log10((processed_rms + 1e-10) / (original_rms + 1e-10)),
        }


class VoiceModulator:
    """
    Main Voice Modulator class implementing FILES_LIBRARY VoiceModulator interface
    Provides high-level interface for voice modulation operations
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}
        self.logger = get_logger(f"{__name__}.VoiceModulator")

        # Initialize modulation engine
        self.engine = LUKHASVoiceModulationEngine(self.config.get("engine", {}))

        # Mode mappings
        self.mode_mappings = {
            VoiceModulationMode.NATURAL: self._get_natural_parameters,
            VoiceModulationMode.EMOTIONAL: self._get_emotional_parameters,
            VoiceModulationMode.ROBOTIC: self._get_robotic_parameters,
            VoiceModulationMode.WHISPER: self._get_whisper_parameters,
            VoiceModulationMode.DRAMATIC: self._get_dramatic_parameters,
            VoiceModulationMode.PROFESSIONAL: self._get_professional_parameters,
            VoiceModulationMode.CREATIVE: self._get_creative_parameters,
            VoiceModulationMode.THERAPEUTIC: self._get_therapeutic_parameters,
        }

        # Cache for determined parameters
        self.parameter_cache = {}

        self.logger.info("LUKHAS Voice Modulator initialized successfully")

    async def modulate(
        self,
        audio_data: bytes,
        mode: Union[VoiceModulationMode, str],
        context: Optional[dict[str, Any]] = None,
        custom_parameters: Optional[VoiceParameters] = None,
    ) -> tuple[bytes, dict[str, Any]]:
        """
        Modulate audio with specified mode and context

        Args:
            audio_data: Input audio as bytes
            mode: Modulation mode
            context: Context information for adaptation
            custom_parameters: Override parameters

        Returns:
            Tuple of (modulated_audio_bytes, metadata)
        """
        try:
            # Convert mode if string
            if isinstance(mode, str):
                mode = VoiceModulationMode(mode)

            # Determine parameters
            if custom_parameters:
                parameters = custom_parameters
            else:
                parameters = await self.determine_parameters(mode, context or {})

            # Apply modulation
            modulated_audio, metadata = await self.engine.modulate_audio(audio_data, parameters)

            # Add mode information to metadata
            metadata["modulation_mode"] = mode.value
            metadata["context_used"] = context or {}

            return modulated_audio, metadata

        except Exception as e:
            self.logger.error(f"Voice modulation failed: {e!s}")
            return audio_data, {
                "success": False,
                "error": str(e),
                "mode": mode.value if hasattr(mode, "value") else str(mode),
            }

    def determine_parameters(self, mode: VoiceModulationMode, context: dict[str, Any]) -> VoiceParameters:
        """
        Determine voice parameters based on mode and context
        Implements context-aware parameter selection
        """
        # Get base parameters for mode
        base_parameters = self.mode_mappings[mode](context)

        # Apply context adaptations
        adapted_parameters = self._adapt_to_context(base_parameters, context)

        # Cache parameters for consistency
        cache_key = f"{mode.value}_{hash(json.dumps(context, sort_keys=True)}"
        self.parameter_cache[cache_key] = adapted_parameters

        return adapted_parameters

    def _get_natural_parameters(self, context: dict[str, Any]) -> VoiceParameters:
        """Get parameters for natural voice mode"""
        return VoiceParameters(
            pitch_shift=1.0,
            speed_factor=1.0,
            volume_gain=1.0,
            emotion_intensity=0.2,
            context_adaptation=1.0,
        )

    def _get_emotional_parameters(self, context: dict[str, Any]) -> VoiceParameters:
        """Get parameters for emotional voice mode"""
        emotion = context.get("emotion", "neutral")

        # Use emotion mappings from engine
        if hasattr(self.engine, "emotion_mappings") and emotion in self.engine.emotion_mappings:
            base_params = self.engine.emotion_mappings[emotion]
        else:
            base_params = VoiceParameters()

        # Enhance emotional intensity
        base_params.emotion_intensity = 0.8
        base_params.context_adaptation = 1.5

        return base_params

    def _get_robotic_parameters(self, context: dict[str, Any]) -> VoiceParameters:
        """Get parameters for robotic voice mode"""
        return VoiceParameters(
            pitch_shift=0.85,
            speed_factor=0.95,
            volume_gain=1.1,
            formant_shift=0.9,
            roughness=0.3,
            emotion_intensity=0.1,
            valence=-0.2,
            arousal=-0.1,
        )

    def _get_whisper_parameters(self, context: dict[str, Any]) -> VoiceParameters:
        """Get parameters for whisper voice mode"""
        return VoiceParameters(
            pitch_shift=0.9,
            speed_factor=0.8,
            volume_gain=0.6,
            breathiness=0.7,
            emotion_intensity=0.3,
            valence=-0.1,
            arousal=-0.3,
        )

    def _get_dramatic_parameters(self, context: dict[str, Any]) -> VoiceParameters:
        """Get parameters for dramatic voice mode"""
        return VoiceParameters(
            pitch_shift=1.1,
            speed_factor=0.9,
            volume_gain=1.2,
            vibrato_rate=3.0,
            vibrato_depth=0.08,
            emotion_intensity=0.9,
            valence=0.3,
            arousal=0.6,
        )

    def _get_professional_parameters(self, context: dict[str, Any]) -> VoiceParameters:
        """Get parameters for professional voice mode"""
        return VoiceParameters(
            pitch_shift=0.98,
            speed_factor=0.95,
            volume_gain=1.0,
            formant_shift=1.05,
            emotion_intensity=0.4,
            valence=0.1,
            arousal=0.0,
        )

    def _get_creative_parameters(self, context: dict[str, Any]) -> VoiceParameters:
        """Get parameters for creative voice mode"""
        return VoiceParameters(
            pitch_shift=1.05,
            speed_factor=1.1,
            volume_gain=1.05,
            vibrato_rate=2.5,
            vibrato_depth=0.05,
            emotion_intensity=0.7,
            valence=0.5,
            arousal=0.4,
        )

    def _get_therapeutic_parameters(self, context: dict[str, Any]) -> VoiceParameters:
        """Get parameters for therapeutic voice mode"""
        return VoiceParameters(
            pitch_shift=0.95,
            speed_factor=0.85,
            volume_gain=0.9,
            breathiness=0.2,
            emotion_intensity=0.6,
            valence=0.4,
            arousal=-0.2,
        )

    def _adapt_to_context(self, base_parameters: VoiceParameters, context: dict[str, Any]) -> VoiceParameters:
        """Adapt parameters based on context"""
        adapted = VoiceParameters(
            pitch_shift=base_parameters.pitch_shift,
            speed_factor=base_parameters.speed_factor,
            volume_gain=base_parameters.volume_gain,
            formant_shift=base_parameters.formant_shift,
            breathiness=base_parameters.breathiness,
            roughness=base_parameters.roughness,
            vibrato_rate=base_parameters.vibrato_rate,
            vibrato_depth=base_parameters.vibrato_depth,
            emotion_intensity=base_parameters.emotion_intensity,
            valence=base_parameters.valence,
            arousal=base_parameters.arousal,
            context_adaptation=base_parameters.context_adaptation,
            personality_blend=base_parameters.personality_blend.copy(),
        )

        # Adapt based on user preferences
        user_prefs = context.get("user_preferences", {})
        if "voice_speed" in user_prefs:
            adapted.speed_factor *= user_prefs["voice_speed"]
        if "voice_pitch" in user_prefs:
            adapted.pitch_shift *= user_prefs["voice_pitch"]

        # Adapt based on content type
        content_type = context.get("content_type", "general")
        if content_type == "reading":
            adapted.speed_factor *= 0.9  # Slower for reading
        elif content_type == "announcement":
            adapted.volume_gain *= 1.1  # Louder for announcements
        elif content_type == "conversation":
            adapted.emotion_intensity *= 1.2  # More expressive for conversation

        # Adapt based on time of day
        hour = context.get("hour_of_day")
        if hour is not None:
            if 6 <= hour <= 9:  # Morning
                adapted.arousal += 0.1
                adapted.volume_gain *= 1.05
            elif hour >= 22 or hour <= 6:  # Night
                adapted.volume_gain *= 0.85
                adapted.speed_factor *= 0.9

        return adapted


# Compatibility class for FILES_LIBRARY interface
class LucasVoiceSystem:
    """
    Compatibility wrapper providing FILES_LIBRARY LucasVoiceSystem interface
    """

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.voice_modulator = VoiceModulator(config.get("voice_settings", {}))
        self.logger = get_logger(f"{__name__}.LucasVoiceSystem")

        # GDPR and data retention settings
        self.gdpr_enabled = config.get("gdpr_enabled", True)
        self.data_retention_days = config.get("data_retention_days", 30)

        self.logger.info("LucasVoiceSystem initialized with LUKHAS voice modulator")

    async def process_input(self, text: str, context: dict[str, Any]) -> dict[str, Any]:
        """Process text input through voice system"""
        try:
            # Extract voice profile and parameters
            voice_profile = context.get("voice_profile", {})
            mode = voice_profile.get("mode", "natural")

            # For now, return processing metadata
            # In full implementation, this would integrate with TTS
            return {
                "success": True,
                "text": text,
                "voice_mode": mode,
                "parameters": self.voice_modulator.determine_parameters(VoiceModulationMode(mode), context).to_dict(),
                "context": context,
                "gdpr_compliant": self.gdpr_enabled,
            }

        except Exception as e:
            self.logger.error(f"Voice processing failed: {e!s}")
            return {"success": False, "error": str(e), "text": text}


# Export main classes
__all__ = [
    "AudioFormat",
    "LUKHASVoiceModulationEngine",
    "LucasVoiceSystem",
    "VoiceModulationMode",
    "VoiceModulator",
    "VoiceParameters",
]