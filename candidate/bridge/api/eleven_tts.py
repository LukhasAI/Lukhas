"""

#TAG:bridge
#TAG:api
#TAG:neuroplastic
#TAG:colony

Enhanced Core TypeScript - Integrated from Advanced Systems
Original: eleven_tts.py
Advanced: eleven_tts.py
Integration Date: 2025-05-31T07:55:28.337770
"""

import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path

#!/usr/bin/env python3
"""
ElevenLabs Text-to-Speech CLI interface for Lukhas
Uses the existing elevenlabs_client.py for speech synthesis
"""


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("eleven_tts")

# Make sure we can import the ElevenLabsClient
CURRENT_DIR = Path(__file__).parent
sys.path.append(str(CURRENT_DIR))
sys.path.append(str(CURRENT_DIR / "integrations" / "elevenlabs"))

# Import the client
try:
    from integrations.elevenlabs.elevenlabs_client import ElevenLabsClient

    logger.info("Successfully imported ElevenLabsClient")
except ImportError as e:
    logger.error(f"Failed to import ElevenLabsClient: {e}")
    sys.exit(1)


async def generate_speech(text, voice_id=None, output_path=None, play=True):
    """Generate speech using ElevenLabs API through existing client"""
    try:
        # Initialize client
        voice_id = voice_id or os.environ.get("LUKHAS_VOICE_ID", "s0XGIcqmceN2l7kjsqoZ")
        client = ElevenLabsClient(voice_id=voice_id)
        logger.info(f"Initialized ElevenLabsClient with voice ID: {voice_id}")

        # Create output directory if needed
        if output_path:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        # Generate speech
        if play:
            logger.info("Generating and playing audio")
            result = await client.generate_and_play(text, voice_id=voice_id)
        else:
            logger.info("Generating audio without playback")
            result = await client.text_to_speech(text, voice_id=voice_id)

        # Copy to output path if specified
        if output_path and result.get("audio_path"):
            import shutil

            try:
                shutil.copy2(result["audio_path"], output_path)
                logger.info(f"Audio saved to: {output_path}")
            except Exception as e:
                logger.error(f"Failed to save audio to {output_path}: {e}")

        # Check for errors
        if "error" in result:
            logger.error(f"Error in speech generation: {result['error']}")
            return False

        logger.info("Speech generation completed successfully")
        return True

    except Exception as e:
        logger.error(f"Error in generate_speech: {e}")
        return False
    finally:
        # Clean up
        if "client" in locals():
            await client.close()


def main():
    """Main function to parse arguments and run speech generation"""
    parser = argparse.ArgumentParser(description="Generate speech using ElevenLabs")
    parser.add_argument("--text", help="Text to convert to speech")
    parser.add_argument("--text-file", help="File containing text to convert")
    parser.add_argument("--output", help="Output audio file path")
    parser.add_argument("--voice", help="Voice ID to use")
    parser.add_argument("--play", action="store_true", help="Play audio after generation")

    args = parser.parse_args()

    # Get text content
    if args.text:
        text = args.text
    elif args.text_file:
        try:
            with open(args.text_file) as f:
                text = f.read()
            logger.info(f"Read text from file: {args.text_file}")
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            return 1
    else:
        logger.error("Must provide either --text or --text-file")
        return 1

    # Run async function
    success = asyncio.run(generate_speech(text, voice_id=args.voice, output_path=args.output, play=args.play))

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
