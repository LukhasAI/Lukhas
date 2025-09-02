"""
LUKHAS AI Audio Filters System
Advanced audio filtering with real-time capabilities and Trinity Framework integration.
⚛️ Identity-aware filter selection
🧠 Consciousness-driven filtering parameters
🛡️ Guardian-validated filter operations
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional

import numpy as np
from scipy import signal

from candidate.core.common.glyph import GLYPH
from candidate.core.common.logger import get_logger
from candidate.governance.guardian import GuardianValidator
from candidate.voice.audio_processing import AudioBuffer

logger = get_logger(__name__)


class FilterType(Enum):
    """Audio filter types"""

    LOW_PASS = "low_pass"
    HIGH_PASS = "high_pass"
    BAND_PASS = "band_pass"
    BAND_STOP = "band_stop"
    NOTCH = "notch"
    PEAKING_EQ = "peaking_eq"
    SHELVING_LOW = "shelving_low"
    SHELVING_HIGH = "shelving_high"
    ADAPTIVE_NOISE = "adaptive_noise"
    SPECTRAL_GATE = "spectral_gate"


@dataclass
class FilterParameters:
    """Audio filter parameters"""

    frequency: float = 1000.0  # Center/cutoff frequency in Hz
    gain: float = 0.0  # Gain in dB
    q_factor: float = 1.0  # Quality factor
    order: int = 4  # Filter order
    enabled: bool = True

    # Advanced parameters
    bandwidth: Optional[float] = None
    slope: float = 6.0  # dB/octave
    threshold: float = -20.0  # For gates/compressors


class AudioFilter(ABC):
    """Abstract base class for audio filters"""

    @abstractmethod
    async def apply(self, buffer: AudioBuffer, params: FilterParameters) -> AudioBuffer:
        """Apply filter to audio buffer"""
        pass


class LowPassFilter(AudioFilter):
    """Low-pass filter implementation"""

    async def apply(self, buffer: AudioBuffer, params: FilterParameters) -> AudioBuffer:
        """Apply low-pass filter"""
        if not params.enabled:
            return buffer

        nyquist = buffer.sample_rate / 2
        normalized_freq = min(params.frequency / nyquist, 0.99)

        sos = signal.butter(params.order, normalized_freq, btype="low", output="sos")
        filtered_data = signal.sosfilt(sos, buffer.data)

        return AudioBuffer(
            data=filtered_data,
            sample_rate=buffer.sample_rate,
            channels=buffer.channels,
            format=buffer.format,
            metadata={**buffer.metadata, "low_pass_applied": True},
        )


class HighPassFilter(AudioFilter):
    """High-pass filter implementation"""

    async def apply(self, buffer: AudioBuffer, params: FilterParameters) -> AudioBuffer:
        """Apply high-pass filter"""
        if not params.enabled:
            return buffer

        nyquist = buffer.sample_rate / 2
        normalized_freq = max(params.frequency / nyquist, 0.01)

        sos = signal.butter(params.order, normalized_freq, btype="high", output="sos")
        filtered_data = signal.sosfilt(sos, buffer.data)

        return AudioBuffer(
            data=filtered_data,
            sample_rate=buffer.sample_rate,
            channels=buffer.channels,
            format=buffer.format,
            metadata={**buffer.metadata, "high_pass_applied": True},
        )


class BandPassFilter(AudioFilter):
    """Band-pass filter implementation"""

    async def apply(self, buffer: AudioBuffer, params: FilterParameters) -> AudioBuffer:
        """Apply band-pass filter"""
        if not params.enabled:
            return buffer

        nyquist = buffer.sample_rate / 2

        # Calculate bandwidth
        if params.bandwidth:
            low_freq = params.frequency - params.bandwidth / 2
            high_freq = params.frequency + params.bandwidth / 2
        else:
            # Use Q factor
            bandwidth = params.frequency / params.q_factor
            low_freq = params.frequency - bandwidth / 2
            high_freq = params.frequency + bandwidth / 2

        low_norm = max(low_freq / nyquist, 0.01)
        high_norm = min(high_freq / nyquist, 0.99)

        sos = signal.butter(
            params.order, [low_norm, high_norm], btype="band", output="sos"
        )
        filtered_data = signal.sosfilt(sos, buffer.data)

        return AudioBuffer(
            data=filtered_data,
            sample_rate=buffer.sample_rate,
            channels=buffer.channels,
            format=buffer.format,
            metadata={**buffer.metadata, "band_pass_applied": True},
        )


class NotchFilter(AudioFilter):
    """Notch filter implementation"""

    async def apply(self, buffer: AudioBuffer, params: FilterParameters) -> AudioBuffer:
        """Apply notch filter"""
        if not params.enabled:
            return buffer

        nyquist = buffer.sample_rate / 2

        # Calculate notch bandwidth from q_factor
        bandwidth = params.frequency / params.q_factor
        low_freq = params.frequency - bandwidth / 2
        high_freq = params.frequency + bandwidth / 2

        low_norm = max(low_freq / nyquist, 0.01)
        high_norm = min(high_freq / nyquist, 0.99)

        sos = signal.butter(
            params.order, [low_norm, high_norm], btype="bandstop", output="sos"
        )
        filtered_data = signal.sosfilt(sos, buffer.data)

        return AudioBuffer(
            data=filtered_data,
            sample_rate=buffer.sample_rate,
            channels=buffer.channels,
            format=buffer.format,
            metadata={**buffer.metadata, "notch_applied": True},
        )


class AdaptiveNoiseFilter(AudioFilter):
    """Adaptive noise reduction filter"""

    async def apply(self, buffer: AudioBuffer, params: FilterParameters) -> AudioBuffer:
        """Apply adaptive noise reduction"""
        if not params.enabled:
            return buffer

        data = buffer.data.copy()

        # Simple spectral subtraction method
        frame_size = 1024
        hop_size = 512

        # Estimate noise from first few frames
        noise_frames = min(5, len(data) // frame_size)
        noise_spectrum = np.zeros(frame_size // 2 + 1)

        for i in range(noise_frames):
            frame = data[i * frame_size : (i + 1) * frame_size]
            if len(frame) == frame_size:
                fft = np.fft.rfft(frame)
                noise_spectrum += np.abs(fft) / noise_frames

        # Process frames with spectral subtraction
        filtered_data = np.zeros_like(data)
        window = np.hanning(frame_size)

        for i in range(0, len(data) - frame_size, hop_size):
            frame = data[i : i + frame_size] * window
            fft = np.fft.rfft(frame)
            magnitude = np.abs(fft)
            phase = np.angle(fft)

            # Spectral subtraction
            alpha = 2.0  # Over-subtraction factor
            enhanced_magnitude = magnitude - alpha * noise_spectrum
            enhanced_magnitude = np.maximum(enhanced_magnitude, 0.1 * magnitude)

            # Reconstruct signal
            enhanced_fft = enhanced_magnitude * np.exp(1j * phase)
            enhanced_frame = np.fft.irfft(enhanced_fft, n=frame_size)

            # Overlap-add
            filtered_data[i : i + frame_size] += enhanced_frame * window

        return AudioBuffer(
            data=filtered_data,
            sample_rate=buffer.sample_rate,
            channels=buffer.channels,
            format=buffer.format,
            metadata={**buffer.metadata, "adaptive_noise_applied": True},
        )


class LUKHASAudioFilterBank:
    """LUKHAS audio filter bank with multiple filter types"""

    def __init__(self):
        self.logger = get_logger(f"{__name__}.LUKHASAudioFilterBank")
        self.guardian = GuardianValidator()

        self.filters = {
            FilterType.LOW_PASS: LowPassFilter(),
            FilterType.HIGH_PASS: HighPassFilter(),
            FilterType.BAND_PASS: BandPassFilter(),
            FilterType.NOTCH: NotchFilter(),
            FilterType.ADAPTIVE_NOISE: AdaptiveNoiseFilter(),
        }

    async def apply_filter(
        self, buffer: AudioBuffer, filter_type: FilterType, params: FilterParameters
    ) -> AudioBuffer:
        """Apply single filter"""
        try:
            validation_result = await self.guardian.validate_operation(
                {
                    "operation_type": "audio_filter",
                    "filter_type": filter_type.value,
                    "audio_length": len(buffer.data),
                }
            )

            if not validation_result.get("approved", False):
                self.logger.warning(f"Guardian rejected filter {filter_type.value}")
                return buffer

            if filter_type in self.filters:
                result = await self.filters[filter_type].apply(buffer, params)

                await GLYPH.emit(
                    "audio.filter.applied",
                    {
                        "filter_type": filter_type.value,
                        "frequency": params.frequency,
                        "enabled": params.enabled,
                    },
                )

                return result
            else:
                self.logger.error(f"Filter {filter_type.value} not available")
                return buffer

        except Exception as e:
            self.logger.error(f"Filter {filter_type.value} failed: {e!s}")
            return buffer

    async def apply_filter_chain(
        self,
        buffer: AudioBuffer,
        filter_chain: list[tuple[FilterType, FilterParameters]],
    ) -> AudioBuffer:
        """Apply chain of filters"""
        current_buffer = buffer

        for filter_type, params in filter_chain:
            current_buffer = await self.apply_filter(
                current_buffer, filter_type, params
            )

        return current_buffer


# Export main classes
__all__ = [
    "AdaptiveNoiseFilter",
    "AudioFilter",
    "BandPassFilter",
    "FilterParameters",
    "FilterType",
    "HighPassFilter",
    "LUKHASAudioFilterBank",
    "LowPassFilter",
    "NotchFilter",
]
