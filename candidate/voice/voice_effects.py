"""
LUKHAS AI Voice Effects Processing System
Advanced voice effect processing with real-time capabilities and Trinity Framework integration.
⚛️ Identity-aware effect selection
🧠 Consciousness-driven effect parameters
🛡️ Guardian-validated effect processing
"""

import asyncio
import logging
import numpy as np
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
import json
import time
import math

from candidate.core.common.glyph import GLYPH
from candidate.governance.guardian import GuardianValidator
from candidate.core.common.logger import get_logger
from candidate.voice.audio_processing import AudioBuffer, AudioFormat


logger = get_logger(__name__)


class VoiceEffectType(Enum):
    """Types of voice effects"""
    REVERB = "reverb"
    ECHO = "echo"
    DELAY = "delay"
    CHORUS = "chorus"
    FLANGER = "flanger"
    PHASER = "phaser"
    DISTORTION = "distortion"
    BITCRUSHER = "bitcrusher"
    VOCODER = "vocoder"
    PITCH_SHIFT = "pitch_shift"
    TIME_STRETCH = "time_stretch"
    TREMOLO = "tremolo"
    VIBRATO = "vibrato"
    COMPRESSOR = "compressor"
    GATE = "gate"
    FILTER = "filter"
    EQ = "eq"
    HARMONIZER = "harmonizer"
    RING_MODULATOR = "ring_modulator"
    FORMANT_SHIFT = "formant_shift"


class EffectIntensity(Enum):
    """Effect intensity levels"""
    SUBTLE = "subtle"
    MODERATE = "moderate"
    STRONG = "strong"
    EXTREME = "extreme"


@dataclass
class EffectParameters:
    """Generic effect parameters"""
    intensity: EffectIntensity = EffectIntensity.MODERATE
    mix: float = 0.5  # Dry/wet mix (0.0 = dry, 1.0 = wet)
    enabled: bool = True
    
    # Common parameters
    frequency: Optional[float] = None
    depth: Optional[float] = None
    rate: Optional[float] = None
    feedback: Optional[float] = None
    delay_time: Optional[float] = None
    
    # Custom parameters
    custom_params: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "intensity": self.intensity.value,
            "mix": self.mix,
            "enabled": self.enabled,
            "frequency": self.frequency,
            "depth": self.depth,
            "rate": self.rate,
            "feedback": self.feedback,
            "delay_time": self.delay_time,
            "custom_params": self.custom_params
        }


class VoiceEffect(ABC):
    """Abstract base class for voice effects"""
    
    def __init__(self, effect_type: VoiceEffectType):
        self.effect_type = effect_type
        self.logger = get_logger(f"{__name__}.{effect_type.value.title()}Effect")
        
    @abstractmethod
    async def apply(self, buffer: AudioBuffer, parameters: EffectParameters) -> AudioBuffer:
        """Apply effect to audio buffer"""
        pass
    
    @abstractmethod
    def get_latency_ms(self) -> float:
        """Get effect processing latency"""
        pass
    
    def get_effect_type(self) -> VoiceEffectType:
        """Get effect type"""
        return self.effect_type


class ReverbEffect(VoiceEffect):
    """Reverb effect implementation"""
    
    def __init__(self):
        super().__init__(VoiceEffectType.REVERB)
        
    async def apply(self, buffer: AudioBuffer, parameters: EffectParameters) -> AudioBuffer:
        """Apply reverb effect"""
        if not parameters.enabled:
            return buffer
            
        data = buffer.data.copy()
        sample_rate = buffer.sample_rate
        
        # Reverb parameters based on intensity
        intensity_params = {
            EffectIntensity.SUBTLE: {"room_size": 0.3, "damping": 0.7, "delays": [0.02, 0.04, 0.06]},
            EffectIntensity.MODERATE: {"room_size": 0.5, "damping": 0.5, "delays": [0.03, 0.05, 0.08, 0.11]},
            EffectIntensity.STRONG: {"room_size": 0.7, "damping": 0.3, "delays": [0.02, 0.04, 0.07, 0.10, 0.14]},
            EffectIntensity.EXTREME: {"room_size": 0.9, "damping": 0.1, "delays": [0.01, 0.03, 0.06, 0.09, 0.13, 0.18]}
        }
        
        params = intensity_params[parameters.intensity]
        room_size = params["room_size"]
        damping = params["damping"]
        delays = params["delays"]
        
        # Create reverb signal
        reverb_signal = np.zeros_like(data)
        
        for i, delay_time in enumerate(delays):
            delay_samples = int(delay_time * sample_rate)
            if delay_samples < len(data):
                # Create delayed version with decay
                decay = room_size * (0.7 ** i)  # Each delay decays more
                delayed = np.pad(data[:-delay_samples], (delay_samples, 0), mode='constant')
                
                # Apply damping (low-pass filter)
                if damping > 0:
                    from scipy import signal
                    cutoff = 8000 * (1.0 - damping)
                    sos = signal.butter(2, cutoff, btype='lowpass', fs=sample_rate, output='sos')
                    delayed = signal.sosfilt(sos, delayed)
                
                reverb_signal += delayed * decay
        
        # Mix dry and wet signals
        output = data * (1.0 - parameters.mix) + reverb_signal * parameters.mix
        
        return AudioBuffer(
            data=output,
            sample_rate=buffer.sample_rate,
            channels=buffer.channels,
            format=buffer.format,
            metadata={**buffer.metadata, "reverb_applied": True}
        )
    
    def get_latency_ms(self) -> float:
        return 180.0  # Maximum delay time


class EchoEffect(VoiceEffect):
    """Echo/Delay effect implementation"""
    
    def __init__(self):
        super().__init__(VoiceEffectType.ECHO)
        
    async def apply(self, buffer: AudioBuffer, parameters: EffectParameters) -> AudioBuffer:
        """Apply echo effect"""
        if not parameters.enabled:
            return buffer
            
        data = buffer.data.copy()
        sample_rate = buffer.sample_rate
        
        # Echo parameters
        delay_time = parameters.delay_time or 0.3  # Default 300ms
        feedback = parameters.feedback or 0.3
        
        # Adjust based on intensity
        intensity_multipliers = {
            EffectIntensity.SUBTLE: {"delay": 0.5, "feedback": 0.5},
            EffectIntensity.MODERATE: {"delay": 1.0, "feedback": 1.0},
            EffectIntensity.STRONG: {"delay": 1.5, "feedback": 1.3},
            EffectIntensity.EXTREME: {"delay": 2.0, "feedback": 1.6}
        }
        
        multiplier = intensity_multipliers[parameters.intensity]
        delay_time *= multiplier["delay"]
        feedback *= multiplier["feedback"]
        feedback = min(feedback, 0.8)  # Prevent runaway feedback
        
        delay_samples = int(delay_time * sample_rate)
        
        if delay_samples >= len(data):
            return buffer  # Delay too long
        
        # Create echo buffer
        output = np.zeros(len(data) + delay_samples)
        output[:len(data)] = data
        
        # Apply multiple echoes with feedback
        current_delay = delay_samples
        current_gain = feedback
        
        while current_delay < len(output) and current_gain > 0.01:
            # Add delayed signal
            end_idx = min(len(data), len(output) - current_delay)
            output[current_delay:current_delay + end_idx] += data[:end_idx] * current_gain
            
            # Next echo
            current_delay += delay_samples
            current_gain *= feedback
        
        # Trim to original length and apply mix
        echo_signal = output[:len(data)] - data  # Extract only the echo part
        mixed_output = data * (1.0 - parameters.mix) + (data + echo_signal) * parameters.mix
        
        return AudioBuffer(
            data=mixed_output,
            sample_rate=buffer.sample_rate,
            channels=buffer.channels,
            format=buffer.format,
            metadata={**buffer.metadata, "echo_applied": True}
        )
    
    def get_latency_ms(self) -> float:
        return 600.0  # Maximum delay time


class ChorusEffect(VoiceEffect):
    """Chorus effect implementation"""
    
    def __init__(self):
        super().__init__(VoiceEffectType.CHORUS)
        
    async def apply(self, buffer: AudioBuffer, parameters: EffectParameters) -> AudioBuffer:
        """Apply chorus effect"""
        if not parameters.enabled:
            return buffer
            
        data = buffer.data.copy()
        sample_rate = buffer.sample_rate
        
        # Chorus parameters
        rate = parameters.rate or 0.5  # LFO rate in Hz
        depth = parameters.depth or 0.002  # Delay modulation depth in seconds
        
        # Adjust based on intensity
        intensity_multipliers = {
            EffectIntensity.SUBTLE: {"voices": 2, "depth": 0.5, "rate": 0.5},
            EffectIntensity.MODERATE: {"voices": 3, "depth": 1.0, "rate": 1.0},
            EffectIntensity.STRONG: {"voices": 4, "depth": 1.5, "rate": 1.5},
            EffectIntensity.EXTREME: {"voices": 6, "depth": 2.0, "rate": 2.0}
        }
        
        params = intensity_multipliers[parameters.intensity]
        num_voices = params["voices"]
        depth *= params["depth"]
        rate *= params["rate"]
        
        # Create time vector
        t = np.arange(len(data)) / sample_rate
        
        # Generate chorus voices
        chorus_signal = np.zeros_like(data)
        
        for voice in range(num_voices):
            # Each voice has slightly different LFO parameters
            voice_rate = rate * (1.0 + voice * 0.1)
            voice_phase = voice * (2 * np.pi / num_voices)
            
            # Generate LFO
            lfo = np.sin(2 * np.pi * voice_rate * t + voice_phase)
            
            # Calculate delay modulation
            base_delay = 0.01 + voice * 0.005  # Base delay for each voice
            delay_modulation = base_delay + depth * lfo
            delay_samples = delay_modulation * sample_rate
            
            # Apply variable delay (simplified interpolation)
            voice_output = np.zeros_like(data)
            for i in range(len(data)):
                delay = int(delay_samples[i])
                if i >= delay:
                    voice_output[i] = data[i - delay]
            
            chorus_signal += voice_output / num_voices
        
        # Mix with original
        output = data * (1.0 - parameters.mix) + chorus_signal * parameters.mix
        
        return AudioBuffer(
            data=output,
            sample_rate=buffer.sample_rate,
            channels=buffer.channels,
            format=buffer.format,
            metadata={**buffer.metadata, "chorus_applied": True}
        )
    
    def get_latency_ms(self) -> float:
        return 50.0


class DistortionEffect(VoiceEffect):
    """Distortion effect implementation"""
    
    def __init__(self):
        super().__init__(VoiceEffectType.DISTORTION)
        
    async def apply(self, buffer: AudioBuffer, parameters: EffectParameters) -> AudioBuffer:
        """Apply distortion effect"""
        if not parameters.enabled:
            return buffer
            
        data = buffer.data.copy()
        
        # Distortion parameters based on intensity
        intensity_params = {
            EffectIntensity.SUBTLE: {"drive": 2.0, "threshold": 0.7},
            EffectIntensity.MODERATE: {"drive": 5.0, "threshold": 0.5},
            EffectIntensity.STRONG: {"drive": 10.0, "threshold": 0.3},
            EffectIntensity.EXTREME: {"drive": 20.0, "threshold": 0.1}
        }
        
        params = intensity_params[parameters.intensity]
        drive = params["drive"]
        threshold = params["threshold"]
        
        # Apply drive (gain)
        driven = data * drive
        
        # Apply soft clipping
        def soft_clip(x, thresh):
            return np.where(
                np.abs(x) <= thresh,
                x,
                np.sign(x) * (thresh + (1 - thresh) * np.tanh((np.abs(x) - thresh) / (1 - thresh)))
            )
        
        distorted = soft_clip(driven, threshold)
        
        # Normalize to prevent excessive volume
        distorted *= 0.7 / np.max(np.abs(distorted) + 1e-10)
        
        # Mix with original
        output = data * (1.0 - parameters.mix) + distorted * parameters.mix
        
        return AudioBuffer(
            data=output,
            sample_rate=buffer.sample_rate,
            channels=buffer.channels,
            format=buffer.format,
            metadata={**buffer.metadata, "distortion_applied": True}
        )
    
    def get_latency_ms(self) -> float:
        return 5.0


class PitchShiftEffect(VoiceEffect):
    """Pitch shift effect implementation"""
    
    def __init__(self):
        super().__init__(VoiceEffectType.PITCH_SHIFT)
        
    async def apply(self, buffer: AudioBuffer, parameters: EffectParameters) -> AudioBuffer:
        """Apply pitch shift effect"""
        if not parameters.enabled:
            return buffer
            
        data = buffer.data.copy()
        sample_rate = buffer.sample_rate
        
        # Pitch shift amount in semitones
        semitones = parameters.custom_params.get("semitones", 0)
        
        # Adjust based on intensity if no custom value
        if semitones == 0:
            intensity_semitones = {
                EffectIntensity.SUBTLE: 2,
                EffectIntensity.MODERATE: 5,
                EffectIntensity.STRONG: 12,
                EffectIntensity.EXTREME: 24
            }
            semitones = intensity_semitones[parameters.intensity]
        
        # Convert semitones to ratio
        pitch_ratio = 2.0 ** (semitones / 12.0)
        
        # Simple pitch shift using resampling (changes speed too)
        # More advanced implementations would use PSOLA or phase vocoder
        from scipy import signal
        
        # Resample for pitch shift
        new_length = int(len(data) / pitch_ratio)
        pitched = signal.resample(data, new_length)
        
        # Pad or truncate to original length
        if len(pitched) > len(data):
            pitched = pitched[:len(data)]
        else:
            pitched = np.pad(pitched, (0, len(data) - len(pitched)), mode='constant')
        
        # Mix with original
        output = data * (1.0 - parameters.mix) + pitched * parameters.mix
        
        return AudioBuffer(
            data=output,
            sample_rate=buffer.sample_rate,
            channels=buffer.channels,
            format=buffer.format,
            metadata={**buffer.metadata, "pitch_shift_applied": True, "semitones": semitones}
        )
    
    def get_latency_ms(self) -> float:
        return 100.0


class VibratoEffect(VoiceEffect):
    """Vibrato effect implementation"""
    
    def __init__(self):
        super().__init__(VoiceEffectType.VIBRATO)
        
    async def apply(self, buffer: AudioBuffer, parameters: EffectParameters) -> AudioBuffer:
        """Apply vibrato effect"""
        if not parameters.enabled:
            return buffer
            
        data = buffer.data.copy()
        sample_rate = buffer.sample_rate
        
        # Vibrato parameters
        rate = parameters.rate or 4.0  # Hz
        depth = parameters.depth or 0.02  # Pitch modulation depth (as ratio)
        
        # Adjust based on intensity
        intensity_multipliers = {
            EffectIntensity.SUBTLE: {"rate": 0.5, "depth": 0.5},
            EffectIntensity.MODERATE: {"rate": 1.0, "depth": 1.0},
            EffectIntensity.STRONG: {"rate": 1.5, "depth": 1.5},
            EffectIntensity.EXTREME: {"rate": 2.0, "depth": 2.0}
        }
        
        multiplier = intensity_multipliers[parameters.intensity]
        rate *= multiplier["rate"]
        depth *= multiplier["depth"]
        
        # Create time vector
        t = np.arange(len(data)) / sample_rate
        
        # Generate vibrato LFO
        lfo = np.sin(2 * np.pi * rate * t)
        
        # Apply pitch modulation using variable delay
        max_delay_samples = int(depth * sample_rate / 10)  # Convert to delay samples
        delay_samples = max_delay_samples * lfo
        
        output = np.zeros_like(data)
        for i in range(len(data)):
            delay = int(delay_samples[i])
            if i >= abs(delay):
                if delay >= 0:
                    output[i] = data[i - delay]
                else:
                    output[i] = data[i + abs(delay)] if i + abs(delay) < len(data) else data[i]
            else:
                output[i] = data[i]
        
        # Mix with original
        mixed_output = data * (1.0 - parameters.mix) + output * parameters.mix
        
        return AudioBuffer(
            data=mixed_output,
            sample_rate=buffer.sample_rate,
            channels=buffer.channels,
            format=buffer.format,
            metadata={**buffer.metadata, "vibrato_applied": True}
        )
    
    def get_latency_ms(self) -> float:
        return 20.0


class VoiceEffectsProcessor:
    """Main voice effects processor with effect chain management"""
    
    def __init__(self):
        self.logger = get_logger(f"{__name__}.VoiceEffectsProcessor")
        self.guardian = GuardianValidator()
        
        # Initialize available effects
        self.effects = {
            VoiceEffectType.REVERB: ReverbEffect(),
            VoiceEffectType.ECHO: EchoEffect(),
            VoiceEffectType.CHORUS: ChorusEffect(),
            VoiceEffectType.DISTORTION: DistortionEffect(),
            VoiceEffectType.PITCH_SHIFT: PitchShiftEffect(),
            VoiceEffectType.VIBRATO: VibratoEffect()
        }
        
        # Effect presets
        self.presets = {
            "natural": [],
            "radio": [
                (VoiceEffectType.COMPRESSOR, EffectParameters(intensity=EffectIntensity.MODERATE, mix=0.8)),
                (VoiceEffectType.EQ, EffectParameters(intensity=EffectIntensity.MODERATE, mix=0.6))
            ],
            "robot": [
                (VoiceEffectType.DISTORTION, EffectParameters(intensity=EffectIntensity.STRONG, mix=0.7)),
                (VoiceEffectType.PITCH_SHIFT, EffectParameters(intensity=EffectIntensity.MODERATE, mix=0.8,
                 custom_params={"semitones": -5}))
            ],
            "ethereal": [
                (VoiceEffectType.REVERB, EffectParameters(intensity=EffectIntensity.STRONG, mix=0.6)),
                (VoiceEffectType.CHORUS, EffectParameters(intensity=EffectIntensity.MODERATE, mix=0.4)),
                (VoiceEffectType.PITCH_SHIFT, EffectParameters(intensity=EffectIntensity.SUBTLE, mix=0.3,
                 custom_params={"semitones": 7}))
            ],
            "vintage": [
                (VoiceEffectType.DISTORTION, EffectParameters(intensity=EffectIntensity.SUBTLE, mix=0.3)),
                (VoiceEffectType.ECHO, EffectParameters(intensity=EffectIntensity.MODERATE, mix=0.4))
            ],
            "dramatic": [
                (VoiceEffectType.REVERB, EffectParameters(intensity=EffectIntensity.MODERATE, mix=0.5)),
                (VoiceEffectType.VIBRATO, EffectParameters(intensity=EffectIntensity.SUBTLE, mix=0.3))
            ]
        }
        
        self.logger.info("Voice Effects Processor initialized")
    
    async def apply_effect(
        self, 
        buffer: AudioBuffer, 
        effect_type: VoiceEffectType, 
        parameters: EffectParameters
    ) -> AudioBuffer:
        """Apply single effect to audio buffer"""
        try:
            # Guardian validation
            validation_result = await self.guardian.validate_operation({
                "operation_type": "voice_effect",
                "effect_type": effect_type.value,
                "parameters": parameters.to_dict(),
                "audio_length": len(buffer.data)
            })
            
            if not validation_result.get("approved", False):
                self.logger.warning(f"Guardian rejected effect {effect_type.value}: {validation_result.get('reason')}")
                return buffer
            
            if effect_type not in self.effects:
                self.logger.error(f"Effect {effect_type.value} not available")
                return buffer
            
            effect = self.effects[effect_type]
            result = await effect.apply(buffer, parameters)
            
            # Emit GLYPH event
            await GLYPH.emit("voice.effect.applied", {
                "effect_type": effect_type.value,
                "intensity": parameters.intensity.value,
                "mix": parameters.mix,
                "latency_ms": effect.get_latency_ms()
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Effect {effect_type.value} failed: {str(e)}")
            return buffer
    
    async def apply_effect_chain(
        self, 
        buffer: AudioBuffer, 
        effect_chain: List[Tuple[VoiceEffectType, EffectParameters]]
    ) -> AudioBuffer:
        """Apply chain of effects to audio buffer"""
        current_buffer = buffer
        
        for effect_type, parameters in effect_chain:
            current_buffer = await self.apply_effect(current_buffer, effect_type, parameters)
        
        return current_buffer
    
    async def apply_preset(
        self, 
        buffer: AudioBuffer, 
        preset_name: str,
        intensity_override: Optional[EffectIntensity] = None
    ) -> AudioBuffer:
        """Apply preset effect chain"""
        if preset_name not in self.presets:
            self.logger.error(f"Preset '{preset_name}' not found")
            return buffer
        
        effect_chain = self.presets[preset_name].copy()
        
        # Override intensity if requested
        if intensity_override:
            effect_chain = [
                (effect_type, EffectParameters(
                    intensity=intensity_override,
                    mix=params.mix,
                    enabled=params.enabled,
                    frequency=params.frequency,
                    depth=params.depth,
                    rate=params.rate,
                    feedback=params.feedback,
                    delay_time=params.delay_time,
                    custom_params=params.custom_params
                ))
                for effect_type, params in effect_chain
            ]
        
        result = await self.apply_effect_chain(buffer, effect_chain)
        
        # Emit GLYPH event
        await GLYPH.emit("voice.preset.applied", {
            "preset_name": preset_name,
            "effects_count": len(effect_chain),
            "intensity_override": intensity_override.value if intensity_override else None
        })
        
        return result
    
    def get_available_effects(self) -> List[VoiceEffectType]:
        """Get list of available effects"""
        return list(self.effects.keys())
    
    def get_available_presets(self) -> List[str]:
        """Get list of available presets"""
        return list(self.presets.keys())
    
    def get_effect_latency(self, effect_type: VoiceEffectType) -> float:
        """Get effect latency in milliseconds"""
        if effect_type in self.effects:
            return self.effects[effect_type].get_latency_ms()
        return 0.0
    
    def get_chain_latency(self, effect_chain: List[VoiceEffectType]) -> float:
        """Get total latency for effect chain"""
        return sum(self.get_effect_latency(effect_type) for effect_type in effect_chain)
    
    def add_custom_preset(
        self, 
        name: str, 
        effect_chain: List[Tuple[VoiceEffectType, EffectParameters]]
    ):
        """Add custom preset"""
        self.presets[name] = effect_chain
        self.logger.info(f"Added custom preset: {name}")
    
    def remove_preset(self, name: str):
        """Remove preset"""
        if name in self.presets:
            del self.presets[name]
            self.logger.info(f"Removed preset: {name}")


# Convenience functions
async def apply_voice_effect(
    audio_data: bytes,
    sample_rate: int,
    effect_type: VoiceEffectType,
    intensity: EffectIntensity = EffectIntensity.MODERATE,
    mix: float = 0.5
) -> bytes:
    """
    Apply single voice effect to audio data
    
    Args:
        audio_data: Input audio as bytes
        sample_rate: Audio sample rate
        effect_type: Type of effect to apply
        intensity: Effect intensity
        mix: Dry/wet mix
        
    Returns:
        Processed audio as bytes
    """
    processor = VoiceEffectsProcessor()
    
    # Convert bytes to AudioBuffer
    audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
    buffer = AudioBuffer(
        data=audio_array,
        sample_rate=sample_rate,
        channels=1,
        format=AudioFormat.PCM_16
    )
    
    # Apply effect
    parameters = EffectParameters(intensity=intensity, mix=mix)
    result_buffer = await processor.apply_effect(buffer, effect_type, parameters)
    
    # Convert back to bytes
    result_int16 = (result_buffer.data * 32767).astype(np.int16)
    return result_int16.tobytes()


async def apply_voice_preset(
    audio_data: bytes,
    sample_rate: int,
    preset_name: str,
    intensity_override: Optional[EffectIntensity] = None
) -> bytes:
    """
    Apply voice effect preset to audio data
    
    Args:
        audio_data: Input audio as bytes
        sample_rate: Audio sample rate
        preset_name: Name of preset to apply
        intensity_override: Override intensity for all effects
        
    Returns:
        Processed audio as bytes
    """
    processor = VoiceEffectsProcessor()
    
    # Convert bytes to AudioBuffer
    audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
    buffer = AudioBuffer(
        data=audio_array,
        sample_rate=sample_rate,
        channels=1,
        format=AudioFormat.PCM_16
    )
    
    # Apply preset
    result_buffer = await processor.apply_preset(buffer, preset_name, intensity_override)
    
    # Convert back to bytes
    result_int16 = (result_buffer.data * 32767).astype(np.int16)
    return result_int16.tobytes()


# Export main classes
__all__ = [
    "VoiceEffectsProcessor",
    "VoiceEffect",
    "VoiceEffectType",
    "EffectIntensity",
    "EffectParameters",
    "ReverbEffect",
    "EchoEffect",
    "ChorusEffect",
    "DistortionEffect",
    "PitchShiftEffect",
    "VibratoEffect",
    "apply_voice_effect",
    "apply_voice_preset"
]