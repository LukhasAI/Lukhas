import pytest
from dream.immersive_ingestion import dream_breath


@pytest.mark.asyncio
async def test_dream_breath_basic():
    memory = [{"note": "swimming in the sea", "emotion": "joy"}]
    result = await dream_breath(memory)
    assert result["dream"] == ["swimming in the sea"]
    assert result["reflection"]["length"] == 1
    assert 0.0 <= result["affect_delta"] <= 1.0
