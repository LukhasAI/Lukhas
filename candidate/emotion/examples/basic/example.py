"""
LUKHAS Emotion - Basic EmotionHub Example
=========================================

This script demonstrates the basic usage of the EmotionHub
to process emotional input and view the resulting state.
"""

import sys
import os
import asyncio

# Add the root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

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
    from candidate.emotion.emotion_hub import get_emotion_hub
except ImportError as e:
    print(f"Error: Could not import get_emotion_hub: {e}")
    print("Please ensure you are running this script from the root of the repository,")
    print("or that the 'candidate' directory is in your Python path.")
    sys.exit(1)


async def main():
    """
    Demonstrates basic EmotionHub functionality.
    """
    print("--- LUKHAS Emotion: Basic EmotionHub Example ---")

    # 1. Get the EmotionHub instance
    print("\n1. Getting the EmotionHub instance...")
    emotion_hub = get_emotion_hub()
    print("   - EmotionHub instance obtained.")

    # 2. Initialize the EmotionHub
    print("\n2. Initializing the EmotionHub...")
    await emotion_hub.initialize()
    print("   - EmotionHub initialized.")
    print(f"   - Registered services: {emotion_hub.list_services()}")

    # 3. Get the initial emotional state
    print("\n3. Getting the initial emotional state...")
    initial_state = emotion_hub.get_emotional_state()
    print(f"   - Initial state: {initial_state}")

    # 4. Process some sample emotional input
    print("\n4. Processing sample emotional input...")
    sample_input = {
        "text": "I am so happy to be a part of this project!",
        "user_id": "user_123",
        "context": "project_kickoff"
    }
    emotional_result = await emotion_hub.process_emotional_input(sample_input)
    print("   - Emotional input processed.")

    # 5. Get the updated emotional state
    print("\n5. Getting the updated emotional state...")
    updated_state = emotion_hub.get_emotional_state()
    print(f"   - Updated state: {updated_state}")

    # 6. Print the analysis results
    print("\n6. Displaying the analysis results...")
    print(f"   - Full analysis: {emotional_result}")

    # 7. Shutdown the hub
    print("\n7. Shutting down the EmotionHub...")
    await emotion_hub.shutdown()
    print("   - EmotionHub shut down.")

    print("\n--- Example Complete ---")


if __name__ == "__main__":
    # The emotion hub uses asyncio, so we run the main function in an event loop.
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExample interrupted by user.")
