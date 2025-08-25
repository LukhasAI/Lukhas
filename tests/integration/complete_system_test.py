import pytest
import asyncio
import os
import sys

# Add the root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from candidate.core.common.glyph import create_glyph, GLYPHSymbol
from candidate.emotion.emotion_hub import get_emotion_hub
from candidate.governance.ethics.ethical_guardian import ethical_check
from candidate.memory.fold_system.memory_fold import HybridMemoryFold
from candidate.bridge.voice.voice_hub import get_voice_hub

@pytest.mark.asyncio
async def test_comprehensive_system_flow():
    """
    A comprehensive test that simulates a request flowing through multiple system modules.
    """
    # 1. Initialize components
    emotion_hub = get_emotion_hub()
    await emotion_hub.initialize()

    memory = HybridMemoryFold()
    voice_hub = get_voice_hub()
    await voice_hub.initialize()

    # 2. Create a user request as a GLYPH token
    user_request = create_glyph(
        symbol=GLYPHSymbol.QUERY,
        source="user_interface",
        target="system_core",
        payload={"query": "Tell me a story about a friendly robot."}
    )

    # 3. Governance check
    is_ethical, feedback = ethical_check(
        user_input=user_request.payload["query"],
        current_context={"user_id": "test_user"},
        personality={"mood": "neutral"}
    )
    assert is_ethical, f"Ethical check failed: {feedback}"

    # 4. Emotion processing
    # emotional_result = await emotion_hub.process_emotional_input({
    #     "text": user_request.payload["query"],
    #     "user_id": "test_user"
    # })
    # assert "error" not in emotional_result, f"Emotion processing failed: {emotional_result.get('error')}"
    # assert "context_analysis" in emotional_result

    # 5. Memory storage
    memory_id = await memory.fold_in(
        data=user_request.to_dict(),
        tags=["story_request", "robot", "friendly"]
    )
    assert memory_id is not None, "Failed to store request in memory"

    # 6. Voice response generation
    # voice_request_data = {
    #     "text": "Generating a story about a friendly robot.",
    #     "context": {"user_id": "test_user"}
    # }
    # voice_result = await voice_hub.process_voice_request(voice_request_data)
    # assert "error" not in voice_result, f"Voice processing failed: {voice_result.get('error')}"
    # assert "context" in voice_result
    # assert "response" in voice_result["context"]

    # 7. Clean up
    await emotion_hub.shutdown()
    # await voice_hub.shutdown()
