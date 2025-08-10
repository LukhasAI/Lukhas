"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: test_voice.py
Advanced: test_voice.py
Integration Date: 2025-05-31T07:55:28.336193
"""

"""
Voice Interface Test Suite
-------------------------
Tests voice processing dependencies and functionality.
"""

import logging
import sys
import wave
from pathlib import Path

import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("voice_test")


def test_basic_audio():
    """Test basic audio processing dependencies"""
    try:
        import scipy.io.wavfile as wav
        import sounddevice as sd

        logger.info("sounddevice version: %s", sd.__version__)

        # Get audio device info
        devices = sd.query_devices()
        logger.info("Available audio devices:")
        for i, dev in enumerate(devices):
            logger.info(
                f"  {i}: {dev['name']} (in: {dev['max_input_channels']}, out: {dev['max_output_channels']})"
            )

        return True
    except ImportError as e:
        logger.error("Basic audio import failed: %s", e)
        return False


def test_elevenlabs():
    """Test ElevenLabs integration"""
    try:
        from elevenlabs import generate, play, set_api_key

        # Don't actually make API calls, just verify the library is available
        logger.info("ElevenLabs package is available")
        return True
    except ImportError as e:
        logger.error("ElevenLabs import failed: %s", e)
        return False


def test_edge_tts():
    """Test Microsoft Edge TTS"""
    try:
        import edge_tts

        logger.info("edge-tts package is available")
        return True
    except ImportError as e:
        logger.error("edge-tts import failed: %s", e)
        return False


def test_voice_processing():
    """Test voice processing capabilities"""
    try:
        import librosa
        import torch
        import torchaudio

        logger.info("pytorch audio version: %s", torchaudio.__version__)
        logger.info("librosa version: %s", librosa.__version__)

        # Create a test audio file
        test_file = Path("test_audio.wav")
        sample_rate = 44100
        duration = 1  # seconds

        # Generate a test tone
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio_data = np.sin(2 * np.pi * 440 * t)  # 440 Hz tone

        # Save test audio
        try:
            with wave.open(str(test_file), "w") as f:
                f.setnchannels(1)
                f.setsampwidth(2)
                f.setframerate(sample_rate)
                f.writeframes((audio_data * 32767).astype(np.int16).tobytes())

            # Test loading with different libraries
            librosa_audio, _ = librosa.load(test_file, sr=sample_rate)
            torchaudio_audio, _ = torchaudio.load(test_file)

            logger.info("Successfully processed audio with librosa and torchaudio")
        except Exception as e:
            logger.error(f"Audio processing failed: {e}")
            return False
        finally:
            test_file.unlink(missing_ok=True)

        return True
    except ImportError as e:
        logger.error("Voice processing import failed: %s", e)
        return False


def test_whisper():
    """Test Whisper speech recognition"""
    try:
        import whisper

        # Just verify the model can be loaded (don't actually download it)
        logger.info("Whisper package is available")
        available_models = whisper.available_models()
        logger.info("Available Whisper models: %s", available_models)

        return True
    except ImportError as e:
        logger.error("Whisper import failed: %s", e)
        return False


def test_vosk():
    """Test Vosk speech recognition"""
    try:
        from vosk import KaldiRecognizer, Model

        logger.info("Vosk package is available")
        return True
    except ImportError as e:
        logger.error("Vosk import failed: %s", e)
        return False


def main():
    """Run all voice interface tests"""
    logger.info("Starting voice interface tests...")

    tests = [
        ("Basic Audio", test_basic_audio),
        ("ElevenLabs", test_elevenlabs),
        ("Edge TTS", test_edge_tts),
        ("Voice Processing", test_voice_processing),
        ("Whisper", test_whisper),
        ("Vosk", test_vosk),
    ]

    results = {}
    for name, test_fn in tests:
        logger.info("Testing %s...", name)
        results[name] = test_fn()

    # Print summary
    logger.info("\nTest Summary:")
    for name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info("%s: %s", name, status)

    # Return success only if all tests passed
    return all(results.values())


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
