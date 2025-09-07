"""
LUKHAS AI Audio Codec System
Audio encoding and decoding with multiple format support and Trinity Framework integration.
⚛️ Identity-aware codec selection
🧠 Consciousness-driven quality optimization
🛡️ Guardian-validated encoding operations
"""

import io
import wave
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

import numpy as np

from candidate.core.common.glyph import GLYPHSymbol, create_glyph
from candidate.core.common.logger import get_logger
from candidate.governance.guardian import GuardianValidator

logger = get_logger(__name__)


class AudioCodec(Enum):
    """Supported audio codecs"""

    PCM_WAV = "pcm_wav"
    MP3 = "mp3"
    FLAC = "flac"
    OGG_VORBIS = "ogg_vorbis"
    AAC = "aac"
    OPUS = "opus"


class CodecQuality(Enum):
    """Codec quality levels"""

    LOW = "low"  # Highly compressed
    MEDIUM = "medium"  # Balanced
    HIGH = "high"  # High quality
    LOSSLESS = "lossless"  # No compression


@dataclass
class CodecParameters:
    """Codec encoding parameters"""

    quality: CodecQuality = CodecQuality.MEDIUM
    bitrate: Optional[int] = None  # kbps
    sample_rate: int = 44100
    channels: int = 1
    bit_depth: int = 16

    # Codec-specific parameters
    compression_level: int = 5  # 0-9 for FLAC, etc.
    variable_bitrate: bool = True
    metadata: dict[str, str] = None


class AudioEncoder(ABC):
    """Abstract base class for audio encoders"""

    @abstractmethod
    async def encode(self, audio_data: np.ndarray, params: CodecParameters) -> bytes:
        """Encode audio data"""
        pass

    @abstractmethod
    def get_codec_type(self) -> AudioCodec:
        """Get codec type"""
        pass


class AudioDecoder(ABC):
    """Abstract base class for audio decoders"""

    @abstractmethod
    async def decode(self, encoded_data: bytes) -> tuple[np.ndarray, dict[str, Any]]:
        """Decode audio data"""
        pass


class WAVEncoder(AudioEncoder):
    """WAV encoder implementation"""

    async def encode(self, audio_data: np.ndarray, params: CodecParameters) -> bytes:
        """Encode to WAV format"""
        buffer = io.BytesIO()

        # Convert float audio to PCM
        if params.bit_depth == 16:
            pcm_data = (audio_data * 32767).astype(np.int16)
        elif params.bit_depth == 24:
            pcm_data = (audio_data * (2**23 - 1)).astype(np.int32)
        elif params.bit_depth == 32:
            pcm_data = (audio_data * (2**31 - 1)).astype(np.int32)
        else:
            pcm_data = (audio_data * 32767).astype(np.int16)

        # Write WAV file
        with wave.open(buffer, "wb") as wav_file:
            wav_file.setnchannels(params.channels)
            wav_file.setsampwidth(params.bit_depth // 8)
            wav_file.setframerate(params.sample_rate)
            wav_file.writeframes(pcm_data.tobytes())

        return buffer.getvalue()

    def get_codec_type(self) -> AudioCodec:
        return AudioCodec.PCM_WAV


class WAVDecoder(AudioDecoder):
    """WAV decoder implementation"""

    async def decode(self, encoded_data: bytes) -> tuple[np.ndarray, dict[str, Any]]:
        """Decode WAV data"""
        buffer = io.BytesIO(encoded_data)

        with wave.open(buffer, "rb") as wav_file:
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            sample_rate = wav_file.getframerate()
            frames = wav_file.getnframes()

            # Read audio data
            raw_data = wav_file.readframes(frames)

            # Convert to numpy array
            if sample_width == 1:
                audio_data = np.frombuffer(raw_data, dtype=np.uint8).astype(np.float32) / 128.0 - 1.0
            elif sample_width == 2:
                audio_data = np.frombuffer(raw_data, dtype=np.int16).astype(np.float32) / 32768.0
            elif sample_width == 3:
                # 24-bit is tricky, convert to 32-bit first
                padded = np.zeros(len(raw_data) // 3 * 4, dtype=np.uint8)
                for i in range(len(raw_data) // 3):
                    padded[i * 4 : i * 4 + 3] = raw_data[i * 3 : i * 3 + 3]
                audio_data = np.frombuffer(padded, dtype=np.int32).astype(np.float32) / (2**23)
            elif sample_width == 4:
                audio_data = np.frombuffer(raw_data, dtype=np.int32).astype(np.float32) / (2**31)
            else:
                raise ValueError(f"Unsupported sample width: {sample_width}")

        metadata = {
            "channels": channels,
            "sample_rate": sample_rate,
            "sample_width": sample_width,
            "frames": frames,
            "duration": frames / sample_rate,
        }

        return audio_data, metadata


class MP3Encoder(AudioEncoder):
    """MP3 encoder implementation (requires pydub and ffmpeg)"""

    async def encode(self, audio_data: np.ndarray, params: CodecParameters) -> bytes:
        """Encode to MP3 format"""
        try:
            import os
            import tempfile

            from pydub import AudioSegment

            # Convert to 16-bit PCM first
            pcm_data = (audio_data * 32767).astype(np.int16)

            # Create AudioSegment
            audio_segment = AudioSegment(
                pcm_data.tobytes(),
                frame_rate=params.sample_rate,
                sample_width=2,  # 16-bit
                channels=params.channels,
            )

            # Determine bitrate
            if params.bitrate:
                bitrate = f"{params.bitrate}k"
            else:
                quality_bitrates = {
                    CodecQuality.LOW: "64k",
                    CodecQuality.MEDIUM: "128k",
                    CodecQuality.HIGH: "320k",
                    CodecQuality.LOSSLESS: "320k",  # MP3 can't be lossless
                }
                bitrate = quality_bitrates[params.quality]

            # Export to MP3
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                audio_segment.export(temp_file.name, format="mp3", bitrate=bitrate)

                # Read encoded data
                with open(temp_file.name, "rb") as f:
                    encoded_data = f.read()

                # Clean up
                os.unlink(temp_file.name)

            return encoded_data

        except ImportError:
            raise RuntimeError("MP3 encoding requires pydub and ffmpeg")

    def get_codec_type(self) -> AudioCodec:
        return AudioCodec.MP3


class FLACEncoder(AudioEncoder):
    """FLAC encoder implementation (lossless)"""

    async def encode(self, audio_data: np.ndarray, params: CodecParameters) -> bytes:
        """Encode to FLAC format"""
        try:
            import os
            import tempfile

            from pydub import AudioSegment

            # Convert to appropriate bit depth
            if params.bit_depth == 24:
                pcm_data = (audio_data * (2**23 - 1)).astype(np.int32)
                sample_width = 3
            else:
                pcm_data = (audio_data * 32767).astype(np.int16)
                sample_width = 2

            # Create AudioSegment
            audio_segment = AudioSegment(
                pcm_data.tobytes(),
                frame_rate=params.sample_rate,
                sample_width=sample_width,
                channels=params.channels,
            )

            # Export to FLAC
            with tempfile.NamedTemporaryFile(suffix=".flac", delete=False) as temp_file:
                audio_segment.export(
                    temp_file.name,
                    format="flac",
                    parameters=["-compression_level", str(params.compression_level)],
                )

                # Read encoded data
                with open(temp_file.name, "rb") as f:
                    encoded_data = f.read()

                # Clean up
                os.unlink(temp_file.name)

            return encoded_data

        except ImportError:
            raise RuntimeError("FLAC encoding requires pydub and ffmpeg")

    def get_codec_type(self) -> AudioCodec:
        return AudioCodec.FLAC


class LUKHASAudioCodecManager:
    """LUKHAS audio codec manager"""

    def __init__(self):
        self.logger = get_logger(f"{__name__}.LUKHASAudioCodecManager")
        self.guardian = GuardianValidator()

        # Initialize encoders and decoders
        self.encoders = {
            AudioCodec.PCM_WAV: WAVEncoder(),
            AudioCodec.MP3: MP3Encoder(),
            AudioCodec.FLAC: FLACEncoder(),
        }

        self.decoders = {AudioCodec.PCM_WAV: WAVDecoder()}

        # Statistics
        self.stats = {
            "encodings_performed": 0,
            "decodings_performed": 0,
            "codecs_used": {},
            "total_data_processed": 0,
        }

    async def encode_audio(
        self,
        audio_data: np.ndarray,
        codec: AudioCodec,
        params: CodecParameters,
        context: Optional[dict[str, Any]] = None,
    ) -> bytes:
        """
        Encode audio data using specified codec

        Args:
            audio_data: Audio data as numpy array
            codec: Target codec
            params: Encoding parameters
            context: Additional context

        Returns:
            Encoded audio data as bytes
        """
        try:
            # Guardian validation
            validation_result = await self.guardian.validate_operation(
                {
                    "operation_type": "audio_encoding",
                    "codec": codec.value,
                    "audio_length": len(audio_data),
                    "context": context or {},
                }
            )

            if not validation_result.get("approved", False):
                raise ValueError(f"Guardian rejected encoding: {validation_result.get('reason')}")

            if codec not in self.encoders:
                raise ValueError(f"Encoder for {codec.value} not available")

            encoder = self.encoders[codec]
            encoded_data = await encoder.encode(audio_data, params)

            # Update statistics
            self.stats["encodings_performed"] += 1
            self.stats["codecs_used"][codec.value] = self.stats["codecs_used"].get(codec.value, 0) + 1
            self.stats["total_data_processed"] += len(audio_data)

            # Emit GLYPH event
            # Create GLYPH event
            glyph_token = create_glyph(GLYPHSymbol.CREATE, "voice_pipeline", "consciousness",
                "audio.encoding.completed",
                {
                    "codec": codec.value,
                    "quality": params.quality.value,
                    "input_size": len(audio_data),
                    "output_size": len(encoded_data),
                    "compression_ratio": (len(audio_data) / len(encoded_data) if len(encoded_data) > 0 else 0),
                })

            return encoded_data

        except Exception as e:
            self.logger.error(f"Audio encoding failed: {e!s}")
            # Create GLYPH event
            glyph_token = create_glyph(GLYPHSymbol.CREATE, "voice_pipeline", "consciousness",
                "audio.encoding.error", {"codec": codec.value, "error": str(e)})
            raise

    async def decode_audio(
        self,
        encoded_data: bytes,
        codec: AudioCodec,
        context: Optional[dict[str, Any]] = None,
    ) -> tuple[np.ndarray, dict[str, Any]]:
        """
        Decode audio data from specified codec

        Args:
            encoded_data: Encoded audio data
            codec: Source codec
            context: Additional context

        Returns:
            Tuple of (audio_data, metadata)
        """
        try:
            # Guardian validation
            validation_result = await self.guardian.validate_operation(
                {
                    "operation_type": "audio_decoding",
                    "codec": codec.value,
                    "data_length": len(encoded_data),
                    "context": context or {},
                }
            )

            if not validation_result.get("approved", False):
                raise ValueError(f"Guardian rejected decoding: {validation_result.get('reason')}")

            if codec not in self.decoders:
                raise ValueError(f"Decoder for {codec.value} not available")

            decoder = self.decoders[codec]
            audio_data, metadata = await decoder.decode(encoded_data)

            # Update statistics
            self.stats["decodings_performed"] += 1
            self.stats["total_data_processed"] += len(audio_data)

            # Emit GLYPH event
            # Create GLYPH event
            glyph_token = create_glyph(GLYPHSymbol.CREATE, "voice_pipeline", "consciousness",
                "audio.decoding.completed",
                {
                    "codec": codec.value,
                    "input_size": len(encoded_data),
                    "output_size": len(audio_data),
                    "metadata": metadata,
                })

            return audio_data

            return audio_data, metadata

        except Exception as e:
            self.logger.error(f"Audio decoding failed: {e!s}")
            # Create GLYPH event
            glyph_token = create_glyph(GLYPHSymbol.CREATE, "voice_pipeline", "consciousness",
                "audio.decoding.error", {"codec": codec.value, "error": str(e)})
            raise

    def get_supported_codecs(self) -> dict[str, list[AudioCodec]]:
        """Get supported codecs for encoding and decoding"""
        return {
            "encoders": list(self.encoders.keys()),
            "decoders": list(self.decoders.keys()),
        }

    def get_codec_info(self, codec: AudioCodec) -> dict[str, Any]:
        """Get information about a specific codec"""
        codec_info = {
            AudioCodec.PCM_WAV: {
                "name": "PCM WAV",
                "description": "Uncompressed PCM audio",
                "lossless": True,
                "typical_bitrate": "1411 kbps (44.1kHz 16-bit stereo)",
                "file_extension": ".wav",
            },
            AudioCodec.MP3: {
                "name": "MP3",
                "description": "MPEG Audio Layer III",
                "lossless": False,
                "typical_bitrate": "128-320 kbps",
                "file_extension": ".mp3",
            },
            AudioCodec.FLAC: {
                "name": "FLAC",
                "description": "Free Lossless Audio Codec",
                "lossless": True,
                "typical_bitrate": "700-1000 kbps",
                "file_extension": ".flac",
            },
        }

        return codec_info.get(codec, {"name": codec.value, "description": "Unknown codec"})

    def get_stats(self) -> dict[str, Any]:
        """Get codec usage statistics"""
        return self.stats.copy()


# Convenience functions
async def encode_to_wav(
    audio_data: np.ndarray,
    sample_rate: int = 44100,
    bit_depth: int = 16,
    channels: int = 1,
) -> bytes:
    """Simple WAV encoding"""
    codec_manager = LUKHASAudioCodecManager()
    params = CodecParameters(
        quality=CodecQuality.LOSSLESS,
        sample_rate=sample_rate,
        bit_depth=bit_depth,
        channels=channels,
    )
    return await codec_manager.encode_audio(audio_data, AudioCodec.PCM_WAV, params)


async def decode_from_wav(encoded_data: bytes) -> tuple[np.ndarray, dict[str, Any]]:
    """Simple WAV decoding"""
    codec_manager = LUKHASAudioCodecManager()
    return await codec_manager.decode_audio(encoded_data, AudioCodec.PCM_WAV)


# Export main classes
__all__ = [
    "AudioCodec",
    "AudioDecoder",
    "AudioEncoder",
    "CodecParameters",
    "CodecQuality",
    "FLACEncoder",
    "LUKHASAudioCodecManager",
    "MP3Encoder",
    "WAVDecoder",
    "WAVEncoder",
    "decode_from_wav",
    "encode_to_wav",
]
