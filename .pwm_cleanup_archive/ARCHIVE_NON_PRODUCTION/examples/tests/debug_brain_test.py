#!/usr/bin/env python3
"""
Debug test to identify the source of the NoneType error
"""
import asyncio
import traceback


async def debug_test():
    try:
        print("🔍 Starting debug test...")

        # Test 1: Direct AGI orchestrator
        print("\n--- Testing AGI Orchestrator ---")

        result = await lukhas_agi_orchestrator.process_agi_request(
            "test input", {"debug": True}
        )
        print(f"AGI Result type: {type(result)}")
        print(f"AGI Result: {result}")

        # Test 2: Cognitive enhancement
        print("\n--- Testing Cognitive Enhancement ---")
        from orchestration_src.brain.cognitive_agi_enhancement import (
            CognitiveAGIEnhancement,
        )

        enhancement = CognitiveAGIEnhancement()
        cog_result = await enhancement.enhance_cognitive_processing(
            "test input", {"debug": True}
        )
        print(f"Cognitive Result type: {type(cog_result)}")
        print(f"Cognitive Result: {cog_result}")

    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"Traceback: {traceback.format_exc()}")


if __name__ == "__main__":
    asyncio.run(debug_test())
