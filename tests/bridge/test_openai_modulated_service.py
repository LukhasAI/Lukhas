import pytest

from lukhas.bridge.llm_wrappers.openai_modulated_service import OpenAIModulatedService
from lukhas.orchestration.signals.homeostasis import ModulationParams
from lukhas.orchestration.signals.signal_bus import Signal, SignalType, get_signal_bus


class FakeOpenAIClient:
    async def chat_completion(
        self, messages, task=None, temperature=None, max_tokens=None, **kwargs
    ):
        # Return a minimal shape similar to OpenAI's model_dump
        return {
            "choices": [{"message": {"content": f"ok:{messages[-1]['content'][:10]}"}}],
            "lukhas_test": True,
            "params": {
                "temperature": temperature,
                "max_tokens": max_tokens,
                "task": task,
            },
        }


@pytest.mark.asyncio
async def test_generate_with_signals_and_params(monkeypatch):
    bus = get_signal_bus()
    bus.clear_history()

    # Seed a signal
    bus.publish(Signal(name=SignalType.NOVELTY, level=0.8, source="test"))

    service = OpenAIModulatedService(client=FakeOpenAIClient())

    params = ModulationParams(temperature=0.5, max_output_tokens=256)
    out = await service.generate(
        "hello world", signals=bus.get_active_signals(), params=params
    )

    assert "content" in out
    assert out["modulation"]["params"]["temperature"] == 0.5
    assert out["modulation"]["params"]["max_tokens"] == 256


@pytest.mark.asyncio
async def test_generate_derives_params_when_missing():
    bus = get_signal_bus()
    bus.clear_history()

    service = OpenAIModulatedService(client=FakeOpenAIClient())
    out = await service.generate("urgent please respond now")

    assert "content" in out
    # Should include modulation metadata
    assert "signal_levels" in out["modulation"]
