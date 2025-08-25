"""
LUKHAS Voice - Basic VoiceHub Example
=====================================

This script demonstrates the basic usage of the VoiceHub
to process a voice-related request.
"""

import sys
import os
import asyncio

# Add the root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..')))

# Mock logger for the example
class Logger:
    def info(self, *args, **kwargs):
        print(f"INFO: {args} {kwargs}")

    def warning(self, *args, **kwargs):
        print(f"WARNING: {args} {kwargs}")

    def error(self, *args, **kwargs):
        print(f"ERROR: {args} {kwargs}")

    def debug(self, *args, **kwargs):
        print(f"DEBUG: {args} {kwargs}")

logger = Logger()

try:
    from candidate.bridge.voice.voice_hub import get_voice_hub
except ImportError as e:
    print(f"Error: Could not import get_voice_hub: {e}")
    print("Please ensure you are running this script from the root of the repository,")
    print("or that the 'candidate' directory is in your Python path.")
    sys.exit(1)


async def main():
    """
    Demonstrates basic VoiceHub functionality.
    """
    print("--- LUKHAS Voice: Basic VoiceHub Example ---")

    # 1. Get the VoiceHub instance
    print("\n1. Getting the VoiceHub instance...")
    voice_hub = get_voice_hub()
    print("   - VoiceHub instance obtained.")

    # 2. Initialize the VoiceHub
    print("\n2. Initializing the VoiceHub...")
    await voice_hub.initialize()
    print("   - VoiceHub initialized.")
    print(f"   - Registered services: {voice_hub.list_services()}")

    # 3. Process a sample voice request
    print("\n3. Processing a sample voice request...")
    sample_request = {
        "text": "Hello, LUKHAS. How are you today?",
        "context": {"user_id": "user_456", "session_id": "session_abc"},
        "audio": b"..."  # Placeholder for audio data
    }
    result = await voice_hub.process_voice_request(sample_request)
    print("   - Voice request processed.")

    # 4. Print the result
    print("\n4. Displaying the processing result...")
    print(f"   - Full result: {result}")

    # 5. Shutdown the hub
    print("\n5. Shutting down the VoiceHub...")
    await voice_hub.shutdown()
    print("   - VoiceHub shut down.")

    print("\n--- Example Complete ---")


if __name__ == "__main__":
    asyncio.run(main())
