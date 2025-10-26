"""
LUKHAS AI Real-Time Audio Streaming System
Real-time audio streaming with low latency and Trinity Framework integration.
⚛️ Identity-aware stream management
🧠 Consciousness-driven stream adaptation
🛡️ Guardian-validated streaming operations
"""

import asyncio
import contextlib
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional

import numpy as np
from voice.audio_processing import AudioFormat

from core.common.glyph import GLYPHSymbol, create_glyph
from core.common.logger import get_logger
from governance.guardian import GuardianValidator

logger = get_logger(__name__)


class StreamingMode(Enum):
    """Audio streaming modes"""

    REAL_TIME = "real_time"  # Lowest latency
    LOW_LATENCY = "low_latency"  # Balanced latency/quality
    HIGH_QUALITY = "high_quality"  # Quality prioritized
    BUFFERED = "buffered"  # Higher latency, stable


class StreamState(Enum):
    """Stream states"""

    IDLE = "idle"
    STARTING = "starting"
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class StreamConfig:
    """Audio stream configuration"""

    # Basic parameters
    sample_rate: int = 44100
    channels: int = 1
    format: AudioFormat = AudioFormat.PCM_16

    # Streaming parameters
    mode: StreamingMode = StreamingMode.LOW_LATENCY
    buffer_size: int = 1024
    max_buffer_count: int = 10
    target_latency_ms: float = 50.0

    # Quality parameters
    adaptive_quality: bool = True
    min_buffer_count: int = 2
    max_latency_ms: float = 200.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "format": self.format.value,
            "mode": self.mode.value,
            "buffer_size": self.buffer_size,
            "max_buffer_count": self.max_buffer_count,
            "target_latency_ms": self.target_latency_ms,
            "adaptive_quality": self.adaptive_quality,
            "min_buffer_count": self.min_buffer_count,
            "max_latency_ms": self.max_latency_ms,
        }


@dataclass
class AudioChunk:
    """Audio data chunk for streaming"""

    data: np.ndarray
    timestamp: float
    sequence_number: int
    sample_rate: int = 44100
    channels: int = 1
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def duration_ms(self) -> float:
        """Get chunk duration in milliseconds"""
        return (len(self.data) / (self.sample_rate * self.channels)) * 1000


@dataclass
class StreamStats:
    """Stream statistics"""

    chunks_processed: int = 0
    bytes_streamed: int = 0
    average_latency_ms: float = 0.0
    buffer_underruns: int = 0
    buffer_overruns: int = 0
    processing_errors: int = 0
    start_time: float = field(default_factory=time.time)

    @property
    def uptime_seconds(self) -> float:
        return time.time() - self.start_time

    @property
    def throughput_kbps(self) -> float:
        if self.uptime_seconds > 0:
            return (self.bytes_streamed * 8) / (self.uptime_seconds * 1000)
        return 0.0


class AudioStreamProcessor(ABC):
    """Abstract base for audio stream processors"""

    @abstractmethod
    async def process_chunk(self, chunk: AudioChunk) -> AudioChunk:
        """Process audio chunk"""
        pass


class PassthroughProcessor(AudioStreamProcessor):
    """Passthrough processor (no processing)"""

    async def process_chunk(self, chunk: AudioChunk) -> AudioChunk:
        return chunk


class VolumeProcessor(AudioStreamProcessor):
    """Volume adjustment processor"""

    def __init__(self, volume: float = 1.0):
        self.volume = volume

    async def process_chunk(self, chunk: AudioChunk) -> AudioChunk:
        processed_data = chunk.data * self.volume
        return AudioChunk(
            data=processed_data,
            timestamp=chunk.timestamp,
            sequence_number=chunk.sequence_number,
            sample_rate=chunk.sample_rate,
            channels=chunk.channels,
            metadata={**chunk.metadata, "volume_applied": self.volume},
        )


class LUKHASAudioStream:
    """LUKHAS real-time audio stream"""

    def __init__(self, stream_id: str, config: StreamConfig):
        self.stream_id = stream_id
        self.config = config
        self.logger = get_logger(f"{__name__}.LUKHASAudioStream.{stream_id}")
        self.guardian = GuardianValidator()

        # Stream state
        self.state = StreamState.IDLE
        self.stats = StreamStats()

        # Buffering
        self.input_queue = asyncio.Queue(maxsize=config.max_buffer_count)
        self.output_queue = asyncio.Queue(maxsize=config.max_buffer_count)

        # Processing
        self.processors: list[AudioStreamProcessor] = [PassthroughProcessor()]
        self.processing_task: Optional[asyncio.Task] = None

        # Sequence tracking
        self.next_sequence = 0
        self.last_processed_sequence = -1

        # Adaptive quality
        self.current_latency = 0.0
        self.quality_adjustment_factor = 1.0

        # Callbacks
        self.on_chunk_callback: Optional[Callable[[AudioChunk], None]] = None
        self.on_error_callback: Optional[Callable[[Exception], None]] = None
        self.on_state_change_callback: Optional[Callable[[StreamState], None]] = None

    async def start(self) -> bool:
        """Start the audio stream"""
        try:
            if self.state != StreamState.IDLE:
                self.logger.warning(f"Stream {self.stream_id} already started")
                return False

            # Guardian validation
            validation_result = await self.guardian.validate_operation(
                {
                    "operation_type": "audio_stream_start",
                    "stream_id": self.stream_id,
                    "config": self.config.to_dict(),
                }
            )

            if not validation_result.get("approved", False):
                raise ValueError(f"Guardian rejected stream start: {validation_result.get('reason')}")

            self._set_state(StreamState.STARTING)

            # Start processing task
            self.processing_task = asyncio.create_task(self._processing_loop())

            self._set_state(StreamState.ACTIVE)
            self.stats.start_time = time.time()

            # Create GLYPH event
            glyph_token = create_glyph(
                GLYPHSymbol.CREATE,
                "voice_pipeline",
                "consciousness",
                {
                    "audio.stream.started",
                    {"stream_id": self.stream_id, "config": self.config.to_dict()},
                },
            )

            self.logger.info(f"Audio stream {self.stream_id} started")
            return True

        except Exception as e:
            self.logger.error(f"Failed to start stream {self.stream_id}: {e!s}")
            self._set_state(StreamState.ERROR)
            if self.on_error_callback:
                self.on_error_callback(e)
            return False

    async def stop(self) -> bool:
        """Stop the audio stream"""
        try:
            if self.state not in [StreamState.ACTIVE, StreamState.PAUSED]:
                return True

            self._set_state(StreamState.STOPPING)

            # Cancel processing task
            if self.processing_task:
                self.processing_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await self.processing_task

            # Clear queues
            while not self.input_queue.empty():
                try:
                    self.input_queue.get_nowait()
                except asyncio.QueueEmpty:
                    break

            while not self.output_queue.empty():
                try:
                    self.output_queue.get_nowait()
                except asyncio.QueueEmpty:
                    break

            self._set_state(StreamState.IDLE)

            # Create GLYPH event
            glyph_token = create_glyph(
                GLYPHSymbol.CREATE,
                "voice_pipeline",
                "consciousness",
                {
                    "audio.stream.stopped",
                    {"stream_id": self.stream_id, "stats": self.get_stats()},
                },
            )

            self.logger.info(f"Audio stream {self.stream_id} stopped")
            return True

        except Exception as e:
            self.logger.error(f"Failed to stop stream {self.stream_id}: {e!s}")
            self._set_state(StreamState.ERROR)
            return False

    async def push_audio(self, audio_data: np.ndarray, timestamp: Optional[float] = None) -> bool:
        """Push audio data to stream"""
        try:
            if self.state != StreamState.ACTIVE:
                return False

            if timestamp is None:
                timestamp = time.time()

            chunk = AudioChunk(
                data=audio_data,
                timestamp=timestamp,
                sequence_number=self.next_sequence,
                sample_rate=self.config.sample_rate,
                channels=self.config.channels,
            )
            self.next_sequence += 1

            # Try to add to queue (non-blocking)
            try:
                self.input_queue.put_nowait(chunk)
                return True
            except asyncio.QueueFull:
                self.stats.buffer_overruns += 1
                self.logger.warning(f"Stream {self.stream_id} buffer overrun")

                # If adaptive quality, reduce buffer size
                if self.config.adaptive_quality:
                    await self._adapt_quality(overrun=True)

                return False

        except Exception as e:
            self.logger.error(f"Failed to push audio to stream {self.stream_id}: {e!s}")
            self.stats.processing_errors += 1
            return False

    async def get_audio(self, timeout: float = 0.1) -> Optional[AudioChunk]:
        """Get processed audio chunk from stream"""
        try:
            if self.state != StreamState.ACTIVE:
                return None

            chunk = await asyncio.wait_for(self.output_queue.get(), timeout=timeout)

            # Update stats
            current_time = time.time()
            latency = (current_time - chunk.timestamp) * 1000  # Convert to ms

            if self.stats.chunks_processed > 0:
                self.stats.average_latency_ms = (
                    self.stats.average_latency_ms * self.stats.chunks_processed + latency
                ) / (self.stats.chunks_processed + 1)
            else:
                self.stats.average_latency_ms = latency

            self.current_latency = latency

            # Adaptive quality adjustment
            if self.config.adaptive_quality:
                await self._adapt_quality()

            return chunk

        except asyncio.TimeoutError:
            self.stats.buffer_underruns += 1
            if self.config.adaptive_quality:
                await self._adapt_quality(underrun=True)
            return None
        except Exception as e:
            self.logger.error(f"Failed to get audio from stream {self.stream_id}: {e!s}")
            self.stats.processing_errors += 1
            return None

    async def _processing_loop(self):
        """Main processing loop for the stream"""
        while self.state == StreamState.ACTIVE:
            try:
                # Get chunk from input queue
                chunk = await asyncio.wait_for(self.input_queue.get(), timeout=0.1)

                # Process through all processors
                processed_chunk = chunk
                for processor in self.processors:
                    processed_chunk = await processor.process_chunk(processed_chunk)

                # Apply quality adjustment
                if self.config.adaptive_quality and self.quality_adjustment_factor != 1.0:
                    processed_chunk.data *= self.quality_adjustment_factor

                # Add to output queue
                try:
                    self.output_queue.put_nowait(processed_chunk)
                except asyncio.QueueFull:
                    # Drop oldest chunk if queue is full
                    try:
                        self.output_queue.get_nowait()
                        self.output_queue.put_nowait(processed_chunk)
                    except asyncio.QueueEmpty:
                        pass

                # Update stats
                self.stats.chunks_processed += 1
                self.stats.bytes_streamed += len(chunk.data) * 4  # 4 bytes per float32
                self.last_processed_sequence = chunk.sequence_number

                # Callback
                if self.on_chunk_callback:
                    self.on_chunk_callback(processed_chunk)

            except asyncio.TimeoutError:
                # No input data, continue
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Processing error in stream {self.stream_id}: {e!s}")
                self.stats.processing_errors += 1
                if self.on_error_callback:
                    self.on_error_callback(e)

    async def _adapt_quality(self, underrun: bool = False, overrun: bool = False):
        """Adapt stream quality based on performance"""
        if not self.config.adaptive_quality:
            return

        if overrun:
            # Too much data, reduce quality slightly
            self.quality_adjustment_factor = max(0.5, self.quality_adjustment_factor * 0.95)
            self.logger.debug(f"Stream {self.stream_id} quality reduced to {self.quality_adjustment_factor:.2f}")
        elif underrun:
            # Not enough data, increase quality slightly
            self.quality_adjustment_factor = min(1.0, self.quality_adjustment_factor * 1.05)
            self.logger.debug(f"Stream {self.stream_id} quality increased to {self.quality_adjustment_factor:.2f}")
        elif self.current_latency > self.config.max_latency_ms:
            # Latency too high, reduce quality
            self.quality_adjustment_factor = max(0.5, self.quality_adjustment_factor * 0.98)
        elif self.current_latency < self.config.target_latency_ms * 0.5:
            # Latency very low, can increase quality
            self.quality_adjustment_factor = min(1.0, self.quality_adjustment_factor * 1.02)

    def _set_state(self, new_state: StreamState):
        """Set stream state and notify callback"""
        if self.state != new_state:
            old_state = self.state
            self.state = new_state
            self.logger.debug(f"Stream {self.stream_id} state: {old_state.value} -> {new_state.value}")
            if self.on_state_change_callback:
                self.on_state_change_callback(new_state)

    def add_processor(self, processor: AudioStreamProcessor):
        """Add audio processor to the stream"""
        self.processors.append(processor)

    def remove_processor(self, processor: AudioStreamProcessor):
        """Remove audio processor from the stream"""
        if processor in self.processors:
            self.processors.remove(processor)

    def get_stats(self) -> dict[str, Any]:
        """Get stream statistics"""
        return {
            "stream_id": self.stream_id,
            "state": self.state.value,
            "chunks_processed": self.stats.chunks_processed,
            "bytes_streamed": self.stats.bytes_streamed,
            "average_latency_ms": self.stats.average_latency_ms,
            "current_latency_ms": self.current_latency,
            "buffer_underruns": self.stats.buffer_underruns,
            "buffer_overruns": self.stats.buffer_overruns,
            "processing_errors": self.stats.processing_errors,
            "uptime_seconds": self.stats.uptime_seconds,
            "throughput_kbps": self.stats.throughput_kbps,
            "quality_factor": self.quality_adjustment_factor,
            "input_queue_size": self.input_queue.qsize(),
            "output_queue_size": self.output_queue.qsize(),
        }


class LUKHASAudioStreamManager:
    """Manager for multiple audio streams"""

    def __init__(self):
        self.logger = get_logger(f"{__name__}.LUKHASAudioStreamManager")
        self.streams: dict[str, LUKHASAudioStream] = {}
        self.global_stats = {
            "streams_created": 0,
            "streams_active": 0,
            "total_data_streamed": 0,
        }

    async def create_stream(self, stream_id: str, config: StreamConfig) -> LUKHASAudioStream:
        """Create new audio stream"""
        if stream_id in self.streams:
            raise ValueError(f"Stream {stream_id} already exists")

        stream = LUKHASAudioStream(stream_id, config)
        self.streams[stream_id] = stream
        self.global_stats["streams_created"] += 1

        # Set up callbacks for global tracking
        original_state_callback = stream.on_state_change_callback

        def state_change_callback(new_state: StreamState):
            if new_state == StreamState.ACTIVE:
                self.global_stats["streams_active"] += 1
            elif new_state in [StreamState.IDLE, StreamState.ERROR]:
                self.global_stats["streams_active"] = max(0, self.global_stats["streams_active"] - 1)

            if original_state_callback:
                original_state_callback(new_state)

        stream.on_state_change_callback = state_change_callback

        self.logger.info(f"Created audio stream: {stream_id}")
        return stream

    async def get_stream(self, stream_id: str) -> Optional[LUKHASAudioStream]:
        """Get existing stream"""
        return self.streams.get(stream_id)

    async def destroy_stream(self, stream_id: str) -> bool:
        """Destroy audio stream"""
        if stream_id not in self.streams:
            return False

        stream = self.streams[stream_id]
        await stream.stop()
        del self.streams[stream_id]

        self.logger.info(f"Destroyed audio stream: {stream_id}")
        return True

    async def stop_all_streams(self):
        """Stop all active streams"""
        for stream in self.streams.values():
            if stream.state == StreamState.ACTIVE:
                await stream.stop()

    def get_all_streams(self) -> dict[str, LUKHASAudioStream]:
        """Get all streams"""
        return self.streams.copy()

    def get_active_streams(self) -> dict[str, LUKHASAudioStream]:
        """Get only active streams"""
        return {stream_id: stream for stream_id, stream in self.streams.items() if stream.state == StreamState.ACTIVE}

    def get_global_stats(self) -> dict[str, Any]:
        """Get global streaming statistics"""
        total_throughput = sum(
            stream.stats.throughput_kbps for stream in self.streams.values() if stream.state == StreamState.ACTIVE
        )

        return {
            **self.global_stats,
            "streams_total": len(self.streams),
            "total_throughput_kbps": total_throughput,
        }


# Convenience functions
async def create_realtime_stream(stream_id: str, sample_rate: int = 44100, buffer_size: int = 512) -> LUKHASAudioStream:
    """Create real-time audio stream with minimal latency"""
    config = StreamConfig(
        mode=StreamingMode.REAL_TIME,
        sample_rate=sample_rate,
        buffer_size=buffer_size,
        max_buffer_count=5,
        target_latency_ms=20.0,
        adaptive_quality=True,
    )

    manager = LUKHASAudioStreamManager()
    return await manager.create_stream(stream_id, config)


# Export main classes
__all__ = [
    "AudioChunk",
    "AudioStreamProcessor",
    "LUKHASAudioStream",
    "LUKHASAudioStreamManager",
    "PassthroughProcessor",
    "StreamConfig",
    "StreamState",
    "StreamStats",
    "StreamingMode",
    "VolumeProcessor",
    "create_realtime_stream",
]
