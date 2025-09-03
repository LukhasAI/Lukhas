from typing import Any

import pytest

from candidate.bridge.llm_wrappers.base import LLMWrapper


class _DummyWrapper(LLMWrapper):
    async def generate_response(self, prompt: str, model: str, **kwargs: Any) -> tuple[str, str]:
        return "ok", model

    def is_available(self) -> bool:
        return True


@pytest.mark.asyncio
async def test_generate_response_returns_text_and_model() -> None:
    """Ensure wrapper subclasses return a response and model # ΛTAG: llm_response"""
    wrapper = _DummyWrapper()
    text, model = await wrapper.generate_response("hi", "gpt")
    assert text == "ok"
    assert model == "gpt"
