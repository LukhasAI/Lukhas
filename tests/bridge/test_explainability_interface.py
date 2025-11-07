"""Tests for ExplainabilityInterface high priority tasks."""

import asyncio

import pytest
from labs.bridge.explainability_interface_layer import (
    ExplainabilityInterface,
    ExplanationLevel,
)


class _StubSymbolicEngine:
    async def trace_reasoning(self, decision):
        return [
            {
                "step_id": 1,
                "operation": "infer",
                "symbolic_form": "A → B",
            }
        ]


class _StubMEGClient:
    async def get_context(self, decision_id):
        return {"episode_id": decision_id}


@pytest.mark.unit
def test_reasoning_trace_includes_meg_context():
    interface = ExplainabilityInterface(
        symbolic_engine=_StubSymbolicEngine(),
        meg_client=_StubMEGClient(),
    )

    decision = {"id": "decision-1"}
    trace = asyncio.run(interface.generate_reasoning_trace(decision))

    assert trace[0]["operation"] == "infer"
    assert any(step["operation"] == "meg_recall" for step in trace)


@pytest.mark.unit
def test_multimodal_generation_serializes_text_output():
    interface = ExplainabilityInterface()

    async def fake_text(decision, level):
        return {"summary": "Decision processed"}

    interface._generate_text_explanation = fake_text  # type: ignore[attr-defined]

    decision = {"id": "decision-2", "reasoning_steps": []}
    result = asyncio.run(interface._generate_multimodal_explanation(decision, ExplanationLevel.DETAILED))

    assert isinstance(result["text"], str)
    assert "generated_at" in result["visual"]
    assert "generated_at" in result["audio"]
