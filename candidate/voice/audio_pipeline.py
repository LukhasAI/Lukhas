"""
LUKHAS AI Audio Processing Pipeline
Comprehensive audio processing pipeline with Trinity Framework integration.
⚛️ Identity-aware pipeline configuration
🧠 Consciousness-driven processing decisions
🛡️ Guardian-validated pipeline operations
"""

import asyncio
import time
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

import numpy as np

from candidate.core.common.glyph import GLYPH
from candidate.core.common.logger import get_logger
from candidate.governance.guardian import GuardianValidator
from candidate.voice.audio_processing import (
    AudioBuffer,
    AudioFormat,
    LUKHASAudioProcessor,
    ProcessingQuality,
)
from candidate.voice.tts_integration import LUKHASTTSService, TTSRequest
from candidate.voice.voice_effects import (
    EffectIntensity,
    VoiceEffectsProcessor,
    VoiceEffectType,
)
from candidate.voice.voice_modulator import VoiceModulationMode, VoiceModulator

logger = get_logger(__name__)


class PipelineStage(Enum):
    """Audio pipeline processing stages"""
    INPUT_VALIDATION = "input_validation"
    PRE_PROCESSING = "pre_processing"
    TTS_SYNTHESIS = "tts_synthesis"
    VOICE_MODULATION = "voice_modulation"
    EFFECTS_PROCESSING = "effects_processing"
    AUDIO_PROCESSING = "audio_processing"
    POST_PROCESSING = "post_processing"
    OUTPUT_FORMATTING = "output_formatting"
    QUALITY_ANALYSIS = "quality_analysis"


class ProcessingMode(Enum):
    """Pipeline processing modes"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    STREAMING = "streaming"
    BATCH = "batch"
    REAL_TIME = "real_time"


@dataclass
class PipelineConfig:
    """Configuration for audio processing pipeline"""
    # Processing mode
    mode: ProcessingMode = ProcessingMode.SEQUENTIAL

    # Quality settings
    target_quality: ProcessingQuality = ProcessingQuality.STANDARD

    # Enabled stages
    enabled_stages: list[PipelineStage] = field(default_factory=lambda: [
        PipelineStage.INPUT_VALIDATION,
        PipelineStage.TTS_SYNTHESIS,
        PipelineStage.AUDIO_PROCESSING,
        PipelineStage.OUTPUT_FORMATTING
    ])

    # Stage configurations
    tts_config: dict[str, Any] = field(default_factory=dict)
    modulation_config: dict[str, Any] = field(default_factory=dict)
    effects_config: dict[str, Any] = field(default_factory=dict)
    audio_processing_config: dict[str, Any] = field(default_factory=dict)

    # Performance settings
    max_parallel_workers: int = 4
    timeout_seconds: float = 30.0

    # Output settings
    output_format: AudioFormat = AudioFormat.PCM_16
    output_sample_rate: int = 44100
    output_channels: int = 1

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "mode": self.mode.value,
            "target_quality": self.target_quality.value,
            "enabled_stages": [stage.value for stage in self.enabled_stages],
            "tts_config": self.tts_config,
            "modulation_config": self.modulation_config,
            "effects_config": self.effects_config,
            "audio_processing_config": self.audio_processing_config,
            "max_parallel_workers": self.max_parallel_workers,
            "timeout_seconds": self.timeout_seconds,
            "output_format": self.output_format.value,
            "output_sample_rate": self.output_sample_rate,
            "output_channels": self.output_channels
        }


@dataclass
class PipelineInput:
    """Input data for audio pipeline"""
    # Text input
    text: str

    # Processing parameters
    voice_id: Optional[str] = None
    emotion: Optional[str] = None
    modulation_mode: Optional[VoiceModulationMode] = None
    effects_preset: Optional[str] = None
    custom_effects: list[tuple[VoiceEffectType, dict[str, Any]]] = field(default_factory=list)

    # Context information
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    context: dict[str, Any] = field(default_factory=dict)

    # Quality preferences
    quality_preference: ProcessingQuality = ProcessingQuality.STANDARD
    latency_target_ms: Optional[float] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "text": self.text,
            "voice_id": self.voice_id,
            "emotion": self.emotion,
            "modulation_mode": self.modulation_mode.value if self.modulation_mode else None,
            "effects_preset": self.effects_preset,
            "custom_effects": [(effect.value, params) for effect, params in self.custom_effects],
            "user_id": self.user_id,
            "session_id": self.session_id,
            "context": self.context,
            "quality_preference": self.quality_preference.value,
            "latency_target_ms": self.latency_target_ms
        }


@dataclass
class PipelineOutput:
    """Output from audio pipeline"""
    success: bool
    audio_data: Optional[bytes] = None
    format: AudioFormat = AudioFormat.PCM_16
    sample_rate: int = 44100
    channels: int = 1
    duration_seconds: float = 0.0

    # Processing information
    total_processing_time_ms: float = 0.0
    stages_completed: list[PipelineStage] = field(default_factory=list)
    stage_times: dict[str, float] = field(default_factory=dict)

    # Quality metrics
    quality_metrics: dict[str, float] = field(default_factory=dict)

    # Error information
    error_message: Optional[str] = None
    error_stage: Optional[PipelineStage] = None

    # Metadata from each stage
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "success": self.success,
            "audio_data_size": len(self.audio_data) if self.audio_data else 0,
            "format": self.format.value,
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "duration_seconds": self.duration_seconds,
            "total_processing_time_ms": self.total_processing_time_ms,
            "stages_completed": [stage.value for stage in self.stages_completed],
            "stage_times": self.stage_times,
            "quality_metrics": self.quality_metrics,
            "error_message": self.error_message,
            "error_stage": self.error_stage.value if self.error_stage else None,
            "metadata": self.metadata
        }


class PipelineStageProcessor(ABC):
    """Abstract base class for pipeline stage processors"""

    def __init__(self, stage: PipelineStage):
        self.stage = stage
        self.logger = get_logger(f"{__name__}.{stage.value.title()}Stage")

    @abstractmethod
    async def process(self, input_data: Any, context: dict[str, Any]) -> tuple[Any, dict[str, Any]]:
        """Process data for this stage"""
        pass

    def get_stage(self) -> PipelineStage:
        """Get stage type"""
        return self.stage


class InputValidationStage(PipelineStageProcessor):
    """Input validation stage"""

    def __init__(self):
        super().__init__(PipelineStage.INPUT_VALIDATION)
        self.guardian = GuardianValidator()

    async def process(self, input_data: PipelineInput, context: dict[str, Any]) -> tuple[PipelineInput, dict[str, Any]]:
        """Validate input data"""
        # Guardian validation
        validation_result = await self.guardian.validate_operation({
            "operation_type": "pipeline_input_validation",
            "text_length": len(input_data.text),
            "input_data": input_data.to_dict()
        })

        if not validation_result.get("approved", False):
            raise ValueError(f"Guardian rejected input: {validation_result.get('reason')}")

        # Basic validation
        if not input_data.text or len(input_data.text.strip()) == 0:
            raise ValueError("Text input is empty")

        if len(input_data.text) > 10000:  # Max text length
            raise ValueError("Text input too long (max 10000 characters)")

        # Validate quality preference
        if input_data.latency_target_ms and input_data.latency_target_ms < 50:
            self.logger.warning("Very low latency target may affect quality")

        metadata = {
            "validation_passed": True,
            "text_length": len(input_data.text),
            "word_count": len(input_data.text.split()),
            "guardian_approved": validation_result.get("approved", False)
        }

        return input_data, metadata


class TTSSynthesisStage(PipelineStageProcessor):
    """TTS synthesis stage"""

    def __init__(self, config: dict[str, Any]):
        super().__init__(PipelineStage.TTS_SYNTHESIS)
        self.tts_service = LUKHASTTSService(config)

    async def process(self, input_data: PipelineInput, context: dict[str, Any]) -> tuple[AudioBuffer, dict[str, Any]]:
        """Synthesize speech from text"""
        # Create TTS request
        tts_request = TTSRequest(
            text=input_data.text,
            voice_id=input_data.voice_id,
            emotion=input_data.emotion,
            quality=input_data.quality_preference,
            user_id=input_data.user_id,
            session_id=input_data.session_id,
            context=input_data.context,
            apply_audio_processing=False  # We'll handle this in later stages
        )

        # Synthesize speech
        tts_response = await self.tts_service.synthesize_speech(tts_request)

        if not tts_response.success:
            raise RuntimeError(f"TTS synthesis failed: {tts_response.error_message}")

        # Convert to AudioBuffer
        if tts_response.audio_data:
            audio_array = np.frombuffer(tts_response.audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            buffer = AudioBuffer(
                data=audio_array,
                sample_rate=tts_response.sample_rate,
                channels=1,  # Assume mono for now
                format=AudioFormat.PCM_16,
                metadata=tts_response.metadata
            )
        else:
            raise RuntimeError("TTS synthesis produced no audio data")

        metadata = {
            "provider_used": tts_response.provider_used,
            "voice_id_used": tts_response.voice_id_used,
            "duration_seconds": tts_response.duration_seconds,
            "tts_processing_time_ms": tts_response.processing_time_ms
        }

        return buffer, metadata


class VoiceModulationStage(PipelineStageProcessor):
    """Voice modulation stage"""

    def __init__(self, config: dict[str, Any]):
        super().__init__(PipelineStage.VOICE_MODULATION)
        self.voice_modulator = VoiceModulator(config)

    async def process(self, input_data: tuple[AudioBuffer, PipelineInput], context: dict[str, Any]) -> tuple[AudioBuffer, dict[str, Any]]:
        """Apply voice modulation"""
        audio_buffer, pipeline_input = input_data

        if not pipeline_input.modulation_mode:
            # No modulation requested
            return audio_buffer, {"modulation_applied": False}

        # Convert buffer to bytes for modulation
        audio_bytes = (audio_buffer.data * 32767).astype(np.int16).tobytes()

        # Apply modulation
        modulated_bytes, mod_metadata = await self.voice_modulator.modulate(
            audio_bytes,
            pipeline_input.modulation_mode,
            pipeline_input.context
        )

        if not mod_metadata.get("success", False):
            self.logger.warning(f"Voice modulation failed: {mod_metadata.get('error')}")
            return audio_buffer, {"modulation_applied": False, "error": mod_metadata.get("error")}

        # Convert back to AudioBuffer
        modulated_array = np.frombuffer(modulated_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        modulated_buffer = AudioBuffer(
            data=modulated_array,
            sample_rate=audio_buffer.sample_rate,
            channels=audio_buffer.channels,
            format=audio_buffer.format,
            metadata={**audio_buffer.metadata, **mod_metadata}
        )

        return modulated_buffer, {"modulation_applied": True, "modulation_metadata": mod_metadata}


class EffectsProcessingStage(PipelineStageProcessor):
    """Effects processing stage"""

    def __init__(self, config: dict[str, Any]):
        super().__init__(PipelineStage.EFFECTS_PROCESSING)
        self.effects_processor = VoiceEffectsProcessor()

    async def process(self, input_data: tuple[AudioBuffer, PipelineInput], context: dict[str, Any]) -> tuple[AudioBuffer, dict[str, Any]]:
        """Apply voice effects"""
        audio_buffer, pipeline_input = input_data

        effects_applied = []
        current_buffer = audio_buffer

        # Apply preset if specified
        if pipeline_input.effects_preset:
            try:
                current_buffer = await self.effects_processor.apply_preset(
                    current_buffer,
                    pipeline_input.effects_preset
                )
                effects_applied.append(f"preset:{pipeline_input.effects_preset}")
            except Exception as e:
                self.logger.warning(f"Effects preset failed: {str(e)}")

        # Apply custom effects
        for effect_type, effect_params in pipeline_input.custom_effects:
            try:
                from candidate.voice.voice_effects import EffectParameters

                # Convert dict to EffectParameters
                params = EffectParameters(
                    intensity=EffectIntensity(effect_params.get("intensity", "moderate")),
                    mix=effect_params.get("mix", 0.5),
                    enabled=effect_params.get("enabled", True),
                    custom_params=effect_params.get("custom_params", {})
                )

                current_buffer = await self.effects_processor.apply_effect(
                    current_buffer,
                    effect_type,
                    params
                )
                effects_applied.append(effect_type.value)
            except Exception as e:
                self.logger.warning(f"Effect {effect_type.value} failed: {str(e)}")

        metadata = {
            "effects_applied": effects_applied,
            "effects_count": len(effects_applied)
        }

        return current_buffer, metadata


class AudioProcessingStage(PipelineStageProcessor):
    """Audio signal processing stage"""

    def __init__(self, config: dict[str, Any]):
        super().__init__(PipelineStage.AUDIO_PROCESSING)
        self.audio_processor = LUKHASAudioProcessor(config)

    async def process(self, input_data: tuple[AudioBuffer, PipelineInput], context: dict[str, Any]) -> tuple[AudioBuffer, dict[str, Any]]:
        """Apply audio signal processing"""
        audio_buffer, pipeline_input = input_data

        # Convert buffer to bytes for processing
        audio_bytes = (audio_buffer.data * 32767).astype(np.int16).tobytes()

        # Apply audio processing
        processed_bytes, proc_metadata = await self.audio_processor.process_audio(
            audio_bytes,
            audio_buffer.sample_rate,
            audio_buffer.channels,
            audio_buffer.format,
            pipeline_input.quality_preference,
            pipeline_input.context
        )

        if not proc_metadata.get("success", False):
            self.logger.warning(f"Audio processing failed: {proc_metadata.get('error')}")
            return audio_buffer, {"processing_applied": False, "error": proc_metadata.get("error")}

        # Convert back to AudioBuffer
        processed_array = np.frombuffer(processed_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        processed_buffer = AudioBuffer(
            data=processed_array,
            sample_rate=audio_buffer.sample_rate,
            channels=audio_buffer.channels,
            format=audio_buffer.format,
            metadata={**audio_buffer.metadata, **proc_metadata}
        )

        return processed_buffer, {"processing_applied": True, "processing_metadata": proc_metadata}


class OutputFormattingStage(PipelineStageProcessor):
    """Output formatting stage"""

    def __init__(self, config: PipelineConfig):
        super().__init__(PipelineStage.OUTPUT_FORMATTING)
        self.config = config

    async def process(self, input_data: AudioBuffer, context: dict[str, Any]) -> tuple[bytes, dict[str, Any]]:
        """Format audio output"""
        audio_buffer = input_data

        # Convert to target format
        if self.config.output_format == AudioFormat.PCM_16:
            output_bytes = (audio_buffer.data * 32767).astype(np.int16).tobytes()
        elif self.config.output_format == AudioFormat.PCM_24:
            output_bytes = (audio_buffer.data * (2**23 - 1)).astype(np.int32).tobytes()
        elif self.config.output_format == AudioFormat.FLOAT_32:
            output_bytes = audio_buffer.data.astype(np.float32).tobytes()
        else:
            # Default to PCM 16
            output_bytes = (audio_buffer.data * 32767).astype(np.int16).tobytes()

        # Calculate duration
        duration = len(audio_buffer.data) / audio_buffer.sample_rate

        metadata = {
            "output_format": self.config.output_format.value,
            "output_sample_rate": self.config.output_sample_rate,
            "output_channels": self.config.output_channels,
            "duration_seconds": duration,
            "output_size_bytes": len(output_bytes)
        }

        return output_bytes, metadata


class LUKHASAudioPipeline:
    """Main LUKHAS audio processing pipeline"""

    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or PipelineConfig()
        self.logger = get_logger(f"{__name__}.LUKHASAudioPipeline")
        self.guardian = GuardianValidator()

        # Initialize stage processors
        self.stages = {
            PipelineStage.INPUT_VALIDATION: InputValidationStage(),
            PipelineStage.TTS_SYNTHESIS: TTSSynthesisStage(self.config.tts_config),
            PipelineStage.VOICE_MODULATION: VoiceModulationStage(self.config.modulation_config),
            PipelineStage.EFFECTS_PROCESSING: EffectsProcessingStage(self.config.effects_config),
            PipelineStage.AUDIO_PROCESSING: AudioProcessingStage(self.config.audio_processing_config),
            PipelineStage.OUTPUT_FORMATTING: OutputFormattingStage(self.config)
        }

        # Processing statistics
        self.stats = {
            "pipelines_processed": 0,
            "pipelines_successful": 0,
            "pipelines_failed": 0,
            "average_processing_time": 0.0,
            "stage_success_rates": {stage.value: 1.0 for stage in PipelineStage}
        }

        self.logger.info("LUKHAS Audio Pipeline initialized")

    async def process(self, input_data: PipelineInput) -> PipelineOutput:
        """
        Process audio through complete pipeline

        Args:
            input_data: Pipeline input data

        Returns:
            Pipeline output with processed audio
        """
        start_time = time.time()
        self.stats["pipelines_processed"] += 1

        output = PipelineOutput(success=False)
        current_data = input_data

        try:
            # Guardian validation for entire pipeline
            validation_result = await self.guardian.validate_operation({
                "operation_type": "audio_pipeline",
                "input_data": input_data.to_dict(),
                "pipeline_config": self.config.to_dict()
            })

            if not validation_result.get("approved", False):
                output.error_message = f"Guardian rejected pipeline: {validation_result.get('reason')}"
                return output

            # Process through enabled stages
            for stage in self.config.enabled_stages:
                if stage not in self.stages:
                    self.logger.warning(f"Stage {stage.value} not available, skipping")
                    continue

                stage_start = time.time()

                try:
                    processor = self.stages[stage]

                    # Handle different stage input/output types
                    if stage == PipelineStage.INPUT_VALIDATION or stage == PipelineStage.TTS_SYNTHESIS:
                        current_data, stage_metadata = await processor.process(current_data, {})
                    elif stage in [PipelineStage.VOICE_MODULATION, PipelineStage.EFFECTS_PROCESSING, PipelineStage.AUDIO_PROCESSING]:
                        current_data, stage_metadata = await processor.process((current_data, input_data), {})
                    elif stage == PipelineStage.OUTPUT_FORMATTING:
                        current_data, stage_metadata = await processor.process(current_data, {})
                    else:
                        current_data, stage_metadata = await processor.process(current_data, {})

                    # Record stage completion
                    stage_time = (time.time() - stage_start) * 1000
                    output.stages_completed.append(stage)
                    output.stage_times[stage.value] = stage_time
                    output.metadata[stage.value] = stage_metadata

                    self.logger.debug(f"Stage {stage.value} completed in {stage_time:.2f}ms")

                except Exception as e:
                    self.logger.error(f"Stage {stage.value} failed: {str(e)}")
                    output.error_stage = stage
                    output.error_message = str(e)

                    # Update stage failure rate
                    current_rate = self.stats["stage_success_rates"][stage.value]
                    self.stats["stage_success_rates"][stage.value] = current_rate * 0.95  # Decay rate

                    return output

            # Pipeline completed successfully
            output.success = True
            output.audio_data = current_data
            output.format = self.config.output_format
            output.sample_rate = self.config.output_sample_rate
            output.channels = self.config.output_channels

            # Calculate duration
            if isinstance(current_data, bytes):
                if self.config.output_format == AudioFormat.PCM_16:
                    samples = len(current_data) // 2  # 16-bit = 2 bytes per sample
                else:
                    samples = len(current_data) // 4  # 32-bit = 4 bytes per sample
                output.duration_seconds = samples / self.config.output_sample_rate

            # Update statistics
            self.stats["pipelines_successful"] += 1

            processing_time = (time.time() - start_time) * 1000
            output.total_processing_time_ms = processing_time

            # Update average processing time
            self.stats["average_processing_time"] = (
                (self.stats["average_processing_time"] * (self.stats["pipelines_successful"] - 1) + processing_time) /
                self.stats["pipelines_successful"]
            )

            # Emit GLYPH event
            await GLYPH.emit("audio.pipeline.completed", {
                "processing_time_ms": processing_time,
                "stages_completed": len(output.stages_completed),
                "text_length": len(input_data.text),
                "audio_duration": output.duration_seconds
            })

            return output

        except Exception as e:
            self.logger.error(f"Pipeline failed: {str(e)}")
            self.stats["pipelines_failed"] += 1

            output.error_message = str(e)
            output.total_processing_time_ms = (time.time() - start_time) * 1000

            await GLYPH.emit("audio.pipeline.error", {
                "error": str(e),
                "stages_completed": len(output.stages_completed)
            })

            return output

    async def process_streaming(self, input_data: PipelineInput) -> AsyncGenerator[dict[str, Any], None]:
        """
        Process audio with streaming output

        Args:
            input_data: Pipeline input data

        Yields:
            Processing updates and final result
        """
        yield {"type": "started", "timestamp": time.time()}

        for stage in self.config.enabled_stages:
            yield {"type": "stage_started", "stage": stage.value, "timestamp": time.time()}

            # Simulate stage processing with progress updates
            await asyncio.sleep(0.1)  # Placeholder for actual processing

            yield {"type": "stage_completed", "stage": stage.value, "timestamp": time.time()}

        # Process normally and yield final result
        result = await self.process(input_data)
        yield {"type": "completed", "result": result.to_dict(), "timestamp": time.time()}

    def get_pipeline_stats(self) -> dict[str, Any]:
        """Get pipeline processing statistics"""
        return self.stats.copy()

    def reset_stats(self):
        """Reset pipeline statistics"""
        self.stats = {
            "pipelines_processed": 0,
            "pipelines_successful": 0,
            "pipelines_failed": 0,
            "average_processing_time": 0.0,
            "stage_success_rates": {stage.value: 1.0 for stage in PipelineStage}
        }


# Convenience function for simple text-to-speech
async def text_to_speech_pipeline(
    text: str,
    voice_id: Optional[str] = None,
    quality: ProcessingQuality = ProcessingQuality.STANDARD,
    effects_preset: Optional[str] = None
) -> bytes:
    """
    Simple text-to-speech pipeline

    Args:
        text: Text to convert to speech
        voice_id: Voice to use
        quality: Processing quality
        effects_preset: Effects preset to apply

    Returns:
        Processed audio as bytes
    """
    pipeline = LUKHASAudioPipeline()

    input_data = PipelineInput(
        text=text,
        voice_id=voice_id,
        quality_preference=quality,
        effects_preset=effects_preset
    )

    result = await pipeline.process(input_data)

    if result.success:
        return result.audio_data
    else:
        raise RuntimeError(f"Pipeline failed: {result.error_message}")


# Export main classes
__all__ = [
    "LUKHASAudioPipeline",
    "PipelineConfig",
    "PipelineInput",
    "PipelineOutput",
    "PipelineStage",
    "ProcessingMode",
    "text_to_speech_pipeline"
]
