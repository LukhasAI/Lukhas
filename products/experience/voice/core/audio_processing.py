"""
LUKHAS AI Audio Signal Processing System
Advanced audio signal processing with real-time capabilities and Trinity Framework integration.
⚛️ Identity-aware audio processing
🧠 Consciousness-driven signal enhancement
🛡️ Guardian-validated audio operations
"""

import asyncio
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional

import numpy as np

from candidate.core.common.glyph import GLYPHSymbol, create_glyph
from candidate.core.common.logger import get_logger
from candidate.governance.guardian import GuardianValidator

logger = get_logger(__name__)


class AudioFormat(Enum):
    """Supported audio formats"""

    PCM_16 = "pcm_16"
    PCM_24 = "pcm_24"
    PCM_32 = "pcm_32"
    FLOAT_32 = "float_32"
    FLOAT_64 = "float_64"


class ProcessingQuality(Enum):
    """Audio processing quality levels"""

    DRAFT = "draft"  # Fastest, lowest quality
    STANDARD = "standard"  # Balanced speed/quality
    HIGH = "high"  # High quality, slower
    STUDIO = "studio"  # Highest quality, slowest


class FilterType(Enum):
    """Audio filter types"""

    LOW_PASS = "low_pass"
    HIGH_PASS = "high_pass"
    BAND_PASS = "band_pass"
    BAND_STOP = "band_stop"
    NOTCH = "notch"
    SHELVING_LOW = "shelving_low"
    SHELVING_HIGH = "shelving_high"
    PEAKING_EQ = "peaking_eq"


@dataclass
class AudioBuffer:
    """Audio buffer with metadata"""

    data: np.ndarray
    sample_rate: int
    channels: int
    format: AudioFormat
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> float:
        """Get duration in seconds"""
        return len(self.data) / (self.sample_rate * self.channels)

    @property
    def samples_per_channel(self) -> int:
        """Get number of samples per channel"""
        return len(self.data) // self.channels

    def to_mono(self) -> "AudioBuffer":
        """Convert to mono"""
        if self.channels == 1:
            return self

        mono_data = np.mean(self.data.reshape(-1, self.channels), axis=1)
        return AudioBuffer(
            data=mono_data,
            sample_rate=self.sample_rate,
            channels=1,
            format=self.format,
            timestamp=self.timestamp,
            metadata=self.metadata.copy(),
        )

    def to_stereo(self) -> "AudioBuffer":
        """Convert to stereo"""
        if self.channels == 2:
            return self
        elif self.channels == 1:
            # Duplicate mono to stereo
            stereo_data = np.repeat(self.data, 2)
            return AudioBuffer(
                data=stereo_data,
                sample_rate=self.sample_rate,
                channels=2,
                format=self.format,
                timestamp=self.timestamp,
                metadata=self.metadata.copy(),
            )
        else:
            # Multi-channel to stereo (mix down)
            reshaped = self.data.reshape(-1, self.channels)
            stereo_data = np.column_stack(
                [
                    np.mean(reshaped, axis=1),  # Left channel (mix all)
                    np.mean(reshaped, axis=1),  # Right channel (same mix)
                ]
            ).flatten()
            return AudioBuffer(
                data=stereo_data,
                sample_rate=self.sample_rate,
                channels=2,
                format=self.format,
                timestamp=self.timestamp,
                metadata=self.metadata.copy(),
            )


@dataclass
class AudioProcessingConfig:
    """Configuration for audio processing"""

    sample_rate: int = 44100
    channels: int = 1
    format: AudioFormat = AudioFormat.PCM_16
    quality: ProcessingQuality = ProcessingQuality.STANDARD

    # Processing parameters
    frame_size: int = 1024
    hop_length: int = 512
    window_function: str = "hann"

    # Real-time parameters
    buffer_size: int = 4096
    max_latency_ms: float = 50.0

    # Quality parameters
    noise_gate_threshold: float = -60.0  # dB
    compressor_ratio: float = 4.0
    limiter_threshold: float = -1.0  # dB


class AudioSignalProcessor(ABC):
    """Abstract base class for audio signal processors"""

    @abstractmethod
    async def process(self, buffer: AudioBuffer) -> AudioBuffer:
        """Process audio buffer"""
        pass

    @abstractmethod
    def get_latency_ms(self) -> float:
        """Get processing latency in milliseconds"""
        pass


class NoiseGateProcessor(AudioSignalProcessor):
    """Noise gate processor to remove low-level noise"""

    def __init__(self, threshold_db: float = -60.0, ratio: float = 10.0):
        self.threshold_db = threshold_db
        self.ratio = ratio
        self.threshold_linear = 10 ** (threshold_db / 20.0)

    async def process(self, buffer: AudioBuffer) -> AudioBuffer:
        """Apply noise gate"""
        data = buffer.data.copy()

        # Calculate envelope (RMS with sliding window)
        frame_size = 1024
        envelope = np.zeros_like(data)

        for i in range(0, len(data) - frame_size, frame_size // 2):
            frame = data[i : i + frame_size]
            rms = np.sqrt(np.mean(frame**2))
            envelope[i : i + frame_size] = np.maximum(envelope[i : i + frame_size], rms)

        # Apply gate
        gate_signal = np.where(envelope > self.threshold_linear, 1.0, 0.0)

        # Smooth gate signal to avoid clicks
        gate_smoothed = self._smooth_gate(gate_signal, buffer.sample_rate)

        processed_data = data * gate_smoothed

        return AudioBuffer(
            data=processed_data,
            sample_rate=buffer.sample_rate,
            channels=buffer.channels,
            format=buffer.format,
            metadata={**buffer.metadata, "noise_gate_applied": True},
        )

    def get_latency_ms(self) -> float:
        return 5.0  # Minimal latency

    def _smooth_gate(self, gate_signal: np.ndarray, sample_rate: int) -> np.ndarray:
        """Smooth gate signal to avoid clicks"""
        # Apply low-pass filter to smooth transitions
        from scipy import signal

        # Design low-pass filter (10Hz cutoff)
        sos = signal.butter(4, 10, btype="lowpass", fs=sample_rate, output="sos")
        smoothed = signal.sosfilt(sos, gate_signal)

        # Ensure values are between 0 and 1
        return np.clip(smoothed, 0.0, 1.0)


class CompressorProcessor(AudioSignalProcessor):
    """Dynamic range compressor"""

    def __init__(
        self,
        threshold_db: float = -20.0,
        ratio: float = 4.0,
        attack_ms: float = 10.0,
        release_ms: float = 100.0,
    ):
        self.threshold_db = threshold_db
        self.ratio = ratio
        self.attack_ms = attack_ms
        self.release_ms = release_ms
        self.threshold_linear = 10 ** (threshold_db / 20.0)

    async def process(self, buffer: AudioBuffer) -> AudioBuffer:
        """Apply compression"""
        data = buffer.data.copy()
        sample_rate = buffer.sample_rate

        # Calculate attack/release coefficients
        attack_coeff = np.exp(-1.0 / (sample_rate * self.attack_ms / 1000.0))
        release_coeff = np.exp(-1.0 / (sample_rate * self.release_ms / 1000.0))

        # Process compression
        compressed_data = np.zeros_like(data)
        envelope = 0.0

        for i, sample in enumerate(data):
            # Envelope follower
            abs_sample = abs(sample)
            if abs_sample > envelope:
                envelope = abs_sample + (envelope - abs_sample) * attack_coeff
            else:
                envelope = abs_sample + (envelope - abs_sample) * release_coeff

            # Calculate gain reduction
            if envelope > self.threshold_linear:
                gain_reduction = 1.0 - (1.0 - self.threshold_linear / envelope) * (1.0 - 1.0 / self.ratio)
            else:
                gain_reduction = 1.0

            compressed_data[i] = sample * gain_reduction

        return AudioBuffer(
            data=compressed_data,
            sample_rate=buffer.sample_rate,
            channels=buffer.channels,
            format=buffer.format,
            metadata={**buffer.metadata, "compression_applied": True},
        )

    def get_latency_ms(self) -> float:
        return 15.0


class LimiterProcessor(AudioSignalProcessor):
    """Audio limiter to prevent clipping"""

    def __init__(self, threshold_db: float = -1.0, lookahead_ms: float = 5.0):
        self.threshold_db = threshold_db
        self.lookahead_ms = lookahead_ms
        self.threshold_linear = 10 ** (threshold_db / 20.0)

    async def process(self, buffer: AudioBuffer) -> AudioBuffer:
        """Apply limiting"""
        data = buffer.data.copy()
        sample_rate = buffer.sample_rate

        # Lookahead samples
        lookahead_samples = int(sample_rate * self.lookahead_ms / 1000.0)

        if lookahead_samples > 0:
            # Add lookahead delay
            padded_data = np.pad(data, (lookahead_samples, 0), mode="constant")
            limited_data = np.zeros_like(padded_data)

            for i in range(len(padded_data)):
                # Look ahead for peaks
                lookahead_end = min(i + lookahead_samples, len(padded_data))
                peak = np.max(np.abs(padded_data[i:lookahead_end]))

                # Calculate limiting gain
                gain = self.threshold_linear / peak if peak > self.threshold_linear else 1.0

                limited_data[i] = padded_data[i] * gain

            # Remove lookahead delay
            output_data = limited_data[lookahead_samples:]
        else:
            # Simple limiting without lookahead
            output_data = np.clip(data, -self.threshold_linear, self.threshold_linear)

        return AudioBuffer(
            data=output_data,
            sample_rate=buffer.sample_rate,
            channels=buffer.channels,
            format=buffer.format,
            metadata={**buffer.metadata, "limiting_applied": True},
        )

    def get_latency_ms(self) -> float:
        return self.lookahead_ms


class EqualizerProcessor(AudioSignalProcessor):
    """Parametric equalizer"""

    def __init__(self, bands: Optional[list[dict[str, float]]] = None):
        # Default EQ bands if none provided
        self.bands = bands or [
            {"freq": 100, "gain": 0, "q": 1.0, "type": "high_pass"},
            {"freq": 1000, "gain": 0, "q": 1.0, "type": "peaking"},
            {"freq": 8000, "gain": 0, "q": 1.0, "type": "shelving_high"},
        ]

    async def process(self, buffer: AudioBuffer) -> AudioBuffer:
        """Apply equalization"""
        data = buffer.data.copy()
        sample_rate = buffer.sample_rate

        # Apply each EQ band
        for band in self.bands:
            data = await self._apply_eq_band(data, sample_rate, band)

        return AudioBuffer(
            data=data,
            sample_rate=buffer.sample_rate,
            channels=buffer.channels,
            format=buffer.format,
            metadata={
                **buffer.metadata,
                "eq_applied": True,
                "eq_bands": len(self.bands),
            },
        )

    async def _apply_eq_band(self, data: np.ndarray, sample_rate: int, band: dict[str, float]) -> np.ndarray:
        """Apply single EQ band"""
        from scipy import signal

        freq = band["freq"]
        gain = band["gain"]
        q = band.get("q", 1.0)
        band_type = band.get("type", "peaking")

        # Convert gain from dB to linear
        gain_linear = 10 ** (gain / 20.0)

        # Design filter based on type
        if band_type == "low_pass":
            sos = signal.butter(4, freq, btype="lowpass", fs=sample_rate, output="sos")
        elif band_type == "high_pass":
            sos = signal.butter(4, freq, btype="highpass", fs=sample_rate, output="sos")
        elif band_type == "band_pass":
            bandwidth = freq / q
            low_freq = freq - bandwidth / 2
            high_freq = freq + bandwidth / 2
            sos = signal.butter(4, [low_freq, high_freq], btype="bandpass", fs=sample_rate, output="sos")
        elif band_type == "peaking":
            # Peaking EQ (boost/cut at specific frequency)
            w0 = 2 * np.pi * freq / sample_rate
            A = gain_linear
            alpha = np.sin(w0) / (2 * q)

            # Peaking EQ coefficients
            b0 = 1 + alpha * A
            b1 = -2 * np.cos(w0)
            b2 = 1 - alpha * A
            a0 = 1 + alpha / A
            a1 = -2 * np.cos(w0)
            a2 = 1 - alpha / A

            # Normalize
            b = [b0 / a0, b1 / a0, b2 / a0]
            a = [1, a1 / a0, a2 / a0]

            return signal.lfilter(b, a, data)
        else:
            # Default to no processing
            return data

        # Apply filter
        return signal.sosfilt(sos, data)

    def get_latency_ms(self) -> float:
        return 10.0 * len(self.bands)  # Approximate latency per band


class ReverbProcessor(AudioSignalProcessor):
    """Simple reverb processor"""

    def __init__(
        self,
        room_size: float = 0.5,
        damping: float = 0.5,
        wet_level: float = 0.3,
        dry_level: float = 0.7,
    ):
        self.room_size = room_size
        self.damping = damping
        self.wet_level = wet_level
        self.dry_level = dry_level

    async def process(self, buffer: AudioBuffer) -> AudioBuffer:
        """Apply reverb"""
        data = buffer.data.copy()
        sample_rate = buffer.sample_rate

        # Simple reverb using multiple delayed/filtered copies
        reverb_delays = [
            int(0.03 * sample_rate),  # 30ms
            int(0.05 * sample_rate),  # 50ms
            int(0.08 * sample_rate),  # 80ms
            int(0.11 * sample_rate),  # 110ms
        ]

        # Create reverb signal
        reverb_signal = np.zeros_like(data)

        for delay in reverb_delays:
            if delay < len(data):
                # Delayed and attenuated version
                delayed = np.pad(data[:-delay], (delay, 0), mode="constant") * (0.3 * self.room_size)

                # Apply damping (low-pass filter)
                from scipy import signal

                sos = signal.butter(2, 8000, btype="lowpass", fs=sample_rate, output="sos")
                delayed_filtered = signal.sosfilt(sos, delayed) * (1.0 - self.damping)

                reverb_signal += delayed_filtered

        # Mix dry and wet signals
        output = data * self.dry_level + reverb_signal * self.wet_level

        return AudioBuffer(
            data=output,
            sample_rate=buffer.sample_rate,
            channels=buffer.channels,
            format=buffer.format,
            metadata={**buffer.metadata, "reverb_applied": True},
        )

    def get_latency_ms(self) -> float:
        return 110.0  # Based on longest delay


class AudioProcessingChain:
    """Chain of audio processors"""

    def __init__(self, processors: Optional[list[AudioSignalProcessor]] = None):
        self.processors = processors or []
        self.logger = get_logger(f"{__name__}.AudioProcessingChain")

    def add_processor(self, processor: AudioSignalProcessor):
        """Add processor to chain"""
        self.processors.append(processor)

    def remove_processor(self, processor: AudioSignalProcessor):
        """Remove processor from chain"""
        if processor in self.processors:
            self.processors.remove(processor)

    async def process(self, buffer: AudioBuffer) -> AudioBuffer:
        """Process audio through entire chain"""
        current_buffer = buffer

        for processor in self.processors:
            try:
                current_buffer = await processor.process(current_buffer)
            except Exception as e:
                self.logger.error(f"Processor {type(processor).__name__} failed: {e!s}")
                # Continue with unprocessed buffer
                pass

        return current_buffer

    def get_total_latency_ms(self) -> float:
        """Get total chain latency"""
        return sum(p.get_latency_ms() for p in self.processors)


class LUKHASAudioProcessor:
    """Main LUKHAS audio processor with Trinity Framework integration"""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}
        self.logger = get_logger(f"{__name__}.LUKHASAudioProcessor")
        self.guardian = GuardianValidator()

        # Processing configuration
        self.processing_config = AudioProcessingConfig(**self.config.get("processing", {}))

        # Initialize processing chains for different quality levels
        self.processing_chains = {
            ProcessingQuality.DRAFT: self._create_draft_chain(),
            ProcessingQuality.STANDARD: self._create_standard_chain(),
            ProcessingQuality.HIGH: self._create_high_quality_chain(),
            ProcessingQuality.STUDIO: self._create_studio_chain(),
        }

        # Real-time processing
        self.real_time_active = False
        self.real_time_queue = asyncio.Queue()

        self.logger.info("LUKHAS Audio Processor initialized")

    def _create_draft_chain(self) -> AudioProcessingChain:
        """Create minimal processing chain for speed"""
        return AudioProcessingChain(
            [
                NoiseGateProcessor(threshold_db=-50.0),
                LimiterProcessor(threshold_db=-3.0),
            ]
        )

    def _create_standard_chain(self) -> AudioProcessingChain:
        """Create standard processing chain"""
        return AudioProcessingChain(
            [
                NoiseGateProcessor(threshold_db=-60.0),
                CompressorProcessor(threshold_db=-20.0, ratio=3.0),
                EqualizerProcessor(
                    [
                        {"freq": 80, "gain": -2, "q": 1.0, "type": "high_pass"},
                        {"freq": 3000, "gain": 1, "q": 2.0, "type": "peaking"},
                    ]
                ),
                LimiterProcessor(threshold_db=-1.0),
            ]
        )

    def _create_high_quality_chain(self) -> AudioProcessingChain:
        """Create high-quality processing chain"""
        return AudioProcessingChain(
            [
                NoiseGateProcessor(threshold_db=-65.0),
                CompressorProcessor(threshold_db=-18.0, ratio=4.0, attack_ms=5.0),
                EqualizerProcessor(
                    [
                        {"freq": 60, "gain": -3, "q": 1.5, "type": "high_pass"},
                        {"freq": 200, "gain": -1, "q": 2.0, "type": "peaking"},
                        {"freq": 2000, "gain": 2, "q": 1.5, "type": "peaking"},
                        {"freq": 8000, "gain": 1, "q": 1.0, "type": "shelving_high"},
                    ]
                ),
                ReverbProcessor(room_size=0.3, wet_level=0.1),
                LimiterProcessor(threshold_db=-0.5, lookahead_ms=10.0),
            ]
        )

    def _create_studio_chain(self) -> AudioProcessingChain:
        """Create studio-quality processing chain"""
        return AudioProcessingChain(
            [
                NoiseGateProcessor(threshold_db=-70.0),
                CompressorProcessor(threshold_db=-16.0, ratio=6.0, attack_ms=3.0, release_ms=50.0),
                EqualizerProcessor(
                    [
                        {"freq": 40, "gain": -6, "q": 2.0, "type": "high_pass"},
                        {"freq": 120, "gain": -2, "q": 1.5, "type": "peaking"},
                        {"freq": 500, "gain": 1, "q": 2.0, "type": "peaking"},
                        {"freq": 2000, "gain": 3, "q": 1.5, "type": "peaking"},
                        {"freq": 5000, "gain": 2, "q": 2.0, "type": "peaking"},
                        {"freq": 12000, "gain": 2, "q": 1.0, "type": "shelving_high"},
                    ]
                ),
                ReverbProcessor(room_size=0.4, damping=0.3, wet_level=0.15),
                LimiterProcessor(threshold_db=-0.1, lookahead_ms=15.0),
            ]
        )

    async def process_audio(
        self,
        audio_data: bytes,
        sample_rate: int = 44100,
        channels: int = 1,
        format: AudioFormat = AudioFormat.PCM_16,
        quality: ProcessingQuality = ProcessingQuality.STANDARD,
        context: Optional[dict[str, Any]] = None,
    ) -> tuple[bytes, dict[str, Any]]:
        """
        Process audio data through LUKHAS audio processing pipeline

        Args:
            audio_data: Input audio as bytes
            sample_rate: Audio sample rate
            channels: Number of audio channels
            format: Audio format
            quality: Processing quality level
            context: Additional context for processing

        Returns:
            Tuple of (processed_audio_bytes, processing_metadata)
        """
        start_time = time.time()

        try:
            # Guardian validation
            validation_result = await self.guardian.validate_operation(
                {
                    "operation_type": "audio_processing",
                    "audio_length": len(audio_data),
                    "sample_rate": sample_rate,
                    "channels": channels,
                    "quality": quality.value,
                    "context": context or {},
                }
            )

            if not validation_result.get("approved", False):
                raise ValueError(f"Guardian rejected audio processing: {validation_result.get('reason')}")

            # Convert bytes to audio buffer
            audio_buffer = self._bytes_to_buffer(audio_data, sample_rate, channels, format)

            # Select processing chain based on quality
            processing_chain = self.processing_chains[quality]

            # Process audio
            processed_buffer = await processing_chain.process(audio_buffer)

            # Convert back to bytes
            processed_bytes = self._buffer_to_bytes(processed_buffer)

            # Calculate processing metrics
            processing_time = (time.time() - start_time) * 1000

            metadata = {
                "success": True,
                "processing_time_ms": processing_time,
                "quality_level": quality.value,
                "processors_used": len(processing_chain.processors),
                "total_latency_ms": processing_chain.get_total_latency_ms(),
                "input_samples": len(audio_buffer.data),
                "output_samples": len(processed_buffer.data),
                "guardian_approved": True,
                "processing_metadata": processed_buffer.metadata,
            }

            # Emit GLYPH event
            # Create GLYPH event
            glyph_token = create_glyph(GLYPHSymbol.CREATE, "voice_pipeline", "consciousness", {
                "audio.processing.completed",
                {
                    "quality": quality.value,
                    "processing_time_ms": processing_time,
                    "sample_rate": sample_rate,
                    "channels": channels,
                },
            })

            return processed_bytes, metadata

        except Exception as e:
            self.logger.error(f"Audio processing failed: {e!s}")

            # Create GLYPH event
            glyph_token = create_glyph(GLYPHSymbol.CREATE, "voice_pipeline", "consciousness", {"type": "audio.processing.error", "error": str(e), "quality": quality.value})

            return audio_data, {
                "success": False,
                "error": str(e),
                "processing_time_ms": (time.time() - start_time) * 1000,
            }

    def _bytes_to_buffer(self, audio_data: bytes, sample_rate: int, channels: int, format: AudioFormat) -> AudioBuffer:
        """Convert audio bytes to AudioBuffer"""
        if format == AudioFormat.PCM_16:
            audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
        elif format == AudioFormat.PCM_24:
            # 24-bit PCM (padded to 32-bit)
            audio_array = np.frombuffer(audio_data, dtype=np.int32).astype(np.float32) / (2**23)
        elif format == AudioFormat.PCM_32:
            audio_array = np.frombuffer(audio_data, dtype=np.int32).astype(np.float32) / (2**31)
        elif format == AudioFormat.FLOAT_32:
            audio_array = np.frombuffer(audio_data, dtype=np.float32)
        else:  # FLOAT_64
            audio_array = np.frombuffer(audio_data, dtype=np.float64).astype(np.float32)

        return AudioBuffer(data=audio_array, sample_rate=sample_rate, channels=channels, format=format)

    def _buffer_to_bytes(self, buffer: AudioBuffer) -> bytes:
        """Convert AudioBuffer to bytes"""
        if buffer.format == AudioFormat.PCM_16:
            audio_int16 = (buffer.data * 32767).astype(np.int16)
            return audio_int16.tobytes()
        elif buffer.format == AudioFormat.PCM_24:
            audio_int32 = (buffer.data * (2**23)).astype(np.int32)
            return audio_int32.tobytes()
        elif buffer.format == AudioFormat.PCM_32:
            audio_int32 = (buffer.data * (2**31)).astype(np.int32)
            return audio_int32.tobytes()
        elif buffer.format == AudioFormat.FLOAT_32:
            return buffer.data.astype(np.float32).tobytes()
        else:  # FLOAT_64
            return buffer.data.astype(np.float64).tobytes()

    async def start_real_time_processing(self):
        """Start real-time audio processing"""
        if self.real_time_active:
            return

        self.real_time_active = True
        asyncio.create_task(self._real_time_worker())
        self.logger.info("Real-time audio processing started")

    async def stop_real_time_processing(self):
        """Stop real-time audio processing"""
        self.real_time_active = False
        self.logger.info("Real-time audio processing stopped")

    async def _real_time_worker(self):
        """Real-time processing worker"""
        while self.real_time_active:
            try:
                # Get audio from queue (with timeout)
                audio_task = await asyncio.wait_for(self.real_time_queue.get(), timeout=0.1)

                # Process audio with draft quality for speed
                result = await self.process_audio(
                    audio_task["data"],
                    audio_task.get("sample_rate", 44100),
                    audio_task.get("channels", 1),
                    audio_task.get("format", AudioFormat.PCM_16),
                    ProcessingQuality.DRAFT,
                    audio_task.get("context"),
                )

                # Call callback if provided
                if "callback" in audio_task:
                    await audio_task["callback"](result)

            except asyncio.TimeoutError:
                # No audio to process, continue
                continue
            except Exception as e:
                self.logger.error(f"Real-time processing error: {e!s}")
                await asyncio.sleep(0.01)

    async def queue_real_time_audio(self, audio_data: bytes, callback: Optional[Callable] = None, **kwargs):
        """Queue audio for real-time processing"""
        await self.real_time_queue.put({"data": audio_data, "callback": callback, **kwargs})

    def get_supported_formats(self) -> list[AudioFormat]:
        """Get list of supported audio formats"""
        return list(AudioFormat)

    def get_processing_qualities(self) -> list[ProcessingQuality]:
        """Get list of processing quality levels"""
        return list(ProcessingQuality)

    async def analyze_audio_quality(self, audio_buffer: AudioBuffer) -> dict[str, float]:
        """Analyze audio quality metrics"""
        data = audio_buffer.data

        # RMS level
        rms = np.sqrt(np.mean(data**2))
        rms_db = 20 * np.log10(rms + 1e-10)

        # Peak level
        peak = np.max(np.abs(data))
        peak_db = 20 * np.log10(peak + 1e-10)

        # Crest factor (peak-to-RMS ratio)
        crest_factor = peak / (rms + 1e-10)
        crest_factor_db = 20 * np.log10(crest_factor)

        # THD+N estimation (simplified)
        # FFT-based harmonic analysis would be more accurate
        thd_estimate = np.std(data) / (np.mean(np.abs(data)) + 1e-10)

        # Dynamic range estimation
        sorted_data = np.sort(np.abs(data))
        p99 = sorted_data[int(0.99 * len(sorted_data))]
        p1 = sorted_data[int(0.01 * len(sorted_data))]
        dynamic_range_db = 20 * np.log10((p99 + 1e-10) / (p1 + 1e-10))

        return {
            "rms_db": float(rms_db),
            "peak_db": float(peak_db),
            "crest_factor_db": float(crest_factor_db),
            "thd_estimate": float(thd_estimate),
            "dynamic_range_db": float(dynamic_range_db),
            "sample_rate": float(audio_buffer.sample_rate),
            "duration_seconds": float(audio_buffer.duration),
        }


# Export main classes
__all__ = [
    "AudioBuffer",
    "AudioFormat",
    "AudioProcessingChain",
    "AudioProcessingConfig",
    "AudioSignalProcessor",
    "CompressorProcessor",
    "EqualizerProcessor",
    "FilterType",
    "LUKHASAudioProcessor",
    "LimiterProcessor",
    "NoiseGateProcessor",
    "ProcessingQuality",
    "ReverbProcessor",
]
