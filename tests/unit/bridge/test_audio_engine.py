import pytest
from products.experience.voice.bridge.audio_engine import create_audio_engine


@pytest.mark.asyncio
async def test_audio_engine_initialize_and_process():
    engine = create_audio_engine()
    assert engine.status == "inactive"
    success = await engine.initialize()
    assert success is True
    result = await engine.process({"sample": 1})
    assert result["status"] == "success"
    assert engine.status == "active"
