"""
Consciousness Platform API Example
"""

import asyncio

from consciousness_platform import (
    ConsciousnessLevel,
    ConsciousnessPlatformAPI,
    ReflectionRequest,
)


async def main():
    # Initialize API
    api = ConsciousnessPlatformAPI(consciousness_level=ConsciousnessLevel.ENHANCED)

    # Get consciousness state
    state = await api.get_state()
    print(f"Consciousness Level: {state.level.value}")
    print(f"Awareness Scores: {state.awareness_scores}")

    # Perform reflection
    reflection = ReflectionRequest(topic="The meaning of existence", depth=3)

    result = await api.reflect(reflection)
    print(f"Insights: {result['insights']}")


if __name__ == "__main__":
    asyncio.run(main())