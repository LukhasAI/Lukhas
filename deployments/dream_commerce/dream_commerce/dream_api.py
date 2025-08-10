"""
Dream Commerce API
Commercial API for dream generation and analysis
Abstracts LUKHAS personality features behind feature flags
"""

import asyncio
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class DreamRequest:
    """Commercial dream generation request"""

    prompt: str
    style: str = "standard"  # standard, creative, lucid
    length: str = "medium"  # short, medium, long
    use_personality: bool = False
    include_symbolism: bool = True
    include_narration: bool = False


@dataclass
class DreamResponse:
    """Commercial dream generation response"""

    dream_id: str
    content: str
    symbols: List[str]
    themes: List[str]
    emotional_tone: str
    metadata: Dict[str, Any]


class DreamCommerceAPI:
    """
    Commercial API for dream generation
    Provides clean interface without exposing LUKHAS personality
    """

    def __init__(self):
        self._engine = None
        self._narrator = None
        self._personality_loaded = False

    async def initialize(self):
        """Initialize the dream commerce API"""
        # Import core dream engine
        from dream.engine.dream_engine import DreamEngine

        self._engine = DreamEngine()

    async def generate_dream(self, request: DreamRequest) -> DreamResponse:
        """
        Generate a dream based on commercial request

        Args:
            request: DreamRequest with generation parameters

        Returns:
            DreamResponse with generated dream content
        """
        # Basic dream generation without personality
        dream_data = {
            "prompt": request.prompt,
            "style": request.style,
            "length": request.length,
        }

        if request.use_personality:
            # Only load personality if explicitly requested
            await self._load_personality()
            dream_data["personality"] = True

        # Generate dream
        result = await self._generate_core_dream(dream_data)

        # Extract commercial-safe components
        response = DreamResponse(
            dream_id=self._generate_dream_id(),
            content=result.get("content", ""),
            symbols=result.get("symbols", []),
            themes=result.get("themes", []),
            emotional_tone=result.get("emotional_tone", "neutral"),
            metadata={
                "style": request.style,
                "length": request.length,
                "timestamp": self._get_timestamp(),
            },
        )

        if request.include_narration and request.use_personality:
            response.metadata["narration"] = await self._add_narration(result)

        return response

    async def analyze_dream(self, dream_content: str) -> Dict[str, Any]:
        """
        Analyze dream content for symbols and themes

        Args:
            dream_content: Text content of dream

        Returns:
            Analysis results
        """
        # Use core analysis without personality
        from dream.core.dream_utils import analyze_dream_symbols

        analysis = analyze_dream_symbols(dream_content)

        return {
            "symbols": analysis.get("symbols", []),
            "themes": analysis.get("themes", []),
            "emotional_tone": analysis.get("emotional_tone", "neutral"),
            "coherence_score": analysis.get("coherence_score", 0.0),
        }

    async def _load_personality(self):
        """Lazy load personality components when needed"""
        if self._personality_loaded:
            return

        try:
            # Only load if explicitly requested
            from personality.narrative_engine_dream_narrator_queue import (
                DreamNarratorQueue,
            )

            self._narrator = DreamNarratorQueue()
            self._personality_loaded = True
        except ImportError:
            # Personality features not available in this deployment
            pass

    async def _generate_core_dream(self, dream_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate dream using core engine"""
        # Simplified example - real implementation would use the engine
        return {
            "content": f"A dream about {dream_data['prompt']}...",
            "symbols": ["water", "flight", "mirror"],
            "themes": ["transformation", "discovery"],
            "emotional_tone": "contemplative",
        }

    async def _add_narration(self, dream_result: Dict[str, Any]) -> str:
        """Add narrative voice if personality is loaded"""
        if not self._narrator:
            return ""

        # Use narrator to add LUKHAS personality touch
        return "Narrative enhancement would go here"

    def _generate_dream_id(self) -> str:
        """Generate unique dream ID"""
        import uuid

        return f"dream_{uuid.uuid4().hex[:8]}"

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime

        return datetime.utcnow().isoformat()


# Example usage
async def example_commercial_usage():
    """Example of using the commercial API"""
    api = DreamCommerceAPI()
    await api.initialize()

    # Standard commercial request (no personality)
    standard_request = DreamRequest(
        prompt="flying over mountains", style="standard", use_personality=False
    )

    standard_response = await api.generate_dream(standard_request)
    print(f"Standard Dream: {standard_response.content}")

    # Premium request with personality
    premium_request = DreamRequest(
        prompt="exploring ancient ruins",
        style="creative",
        use_personality=True,
        include_narration=True,
    )

    premium_response = await api.generate_dream(premium_request)
    print(f"Premium Dream: {premium_response.content}")

    # Analysis only
    analysis = await api.analyze_dream("I was swimming in a cosmic ocean...")
    print(f"Analysis: {analysis}")


if __name__ == "__main__":
    asyncio.run(example_commercial_usage())
