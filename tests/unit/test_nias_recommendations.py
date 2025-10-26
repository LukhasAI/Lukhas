import pytest
from products.communication.nias_candidate.core.nias_engine import ContextAwareRecommendation


@pytest.mark.asyncio
async def test_build_recommendations_from_context() -> None:
    recommender = ContextAwareRecommendation()
    payloads = recommender._build_recommendations(
        {"recommendations": [{"symbol": "focus"}]},
        {"user_id": "user-123"},
    )

    assert payloads
    assert payloads[0]["user_id"] == "user-123"
    assert payloads[0]["source"] == "dast"


@pytest.mark.asyncio
async def test_build_recommendations_fallback() -> None:
    recommender = ContextAwareRecommendation()
    payloads = recommender._build_recommendations({}, {"user_id": "user-456", "signals": {"mood": 0.2}})

    assert payloads
    assert payloads[0]["source"] == "fallback"
