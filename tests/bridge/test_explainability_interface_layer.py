"""Tests for the explainability interface layer."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

import pytest
from labs.bridge.explainability_interface_layer import (
    CompletenessMetrics,
    ExplainabilityInterface,
    ExplanationLevel,
    ExplanationMode,
    FormalProof,
)


class _SymbolicEngineStub:
    """Stub symbolic engine returning deterministic traces."""

    async def trace_reasoning(self, decision: Dict[str, object]) -> List[Dict[str, object]]:
        return [
            {
                "step_id": 1,
                "operation": "infer",
                "input": {"fact": "a"},
                "output": {"fact": "b"},
                "confidence": 0.9,
                "symbolic_form": "a -> b",
            }
        ]


class _MegClientStub:
    """Stub MEG client returning a minimal context payload."""

    async def get_context(self, decision_id: Optional[str]) -> Dict[str, object]:  # pragma: no cover - simple stub
        return {"decision_id": decision_id, "memory": ["contextual insight"]}


@pytest.fixture()
def decision_payload() -> Dict[str, object]:
    return {
        "id": "decision-1",
        "result": "approve",
        "confidence": 0.82,
        "factors": ["risk", "value"],
        "premises": ["risk acceptable", "value positive"],
        "reasoning_steps": [
            {
                "statement": "If risk acceptable and value positive then approve",
                "rule": "Implication",
                "depends_on": [1, 2],
                "operation": "combine",
                "input": {"left": "risk acceptable", "right": "value positive"},
                "output": {"decision": "approve"},
                "confidence": 0.85,
                "symbolic": "risk ∧ value → approve",
            }
        ],
        "conclusion": "approve",
    }


@pytest.mark.asyncio
async def test_text_explanation_has_completeness(decision_payload: Dict[str, object]) -> None:
    interface = ExplainabilityInterface()
    explanation = await interface.explain(decision_payload, ExplanationMode.TEXT, ExplanationLevel.DETAILED)

    assert explanation.mode is ExplanationMode.TEXT
    assert isinstance(explanation.completeness, CompletenessMetrics)
    assert 0 <= explanation.completeness.coverage_score <= 1
    assert explanation.metadata["decision_id"] == "decision-1"


@pytest.mark.asyncio
async def test_cache_records_hits(decision_payload: Dict[str, object]) -> None:
    interface = ExplainabilityInterface()
    await interface.explain(decision_payload)  # miss
    await interface.explain(decision_payload)  # hit

    stats = interface.cache.stats()
    assert stats["hits"] == 1
    assert stats["misses"] == 1


@pytest.mark.asyncio
async def test_formal_proof_contains_conclusion(decision_payload: Dict[str, object]) -> None:
    interface = ExplainabilityInterface()
    proof = await interface.generate_formal_proof(decision_payload)

    assert isinstance(proof, FormalProof)
    assert proof.conclusion == "approve"
    assert proof.steps[-1]["type"] == "conclusion"
    assert proof.valid is True


@pytest.mark.asyncio
async def test_multimodal_response_includes_audio(decision_payload: Dict[str, object]) -> None:
    interface = ExplainabilityInterface()
    content = await interface.explain(
        decision_payload,
        mode=ExplanationMode.MULTIMODAL,
        level=ExplanationLevel.SIMPLE,
    )

    assert set(content.content.keys()) == {"text", "visual", "audio"}
    assert content.content["audio"]["format"] == "mp3"


@pytest.mark.asyncio
async def test_symbolic_trace_uses_stubs(decision_payload: Dict[str, object]) -> None:
    interface = ExplainabilityInterface(
        symbolic_engine=_SymbolicEngineStub(),
        meg_client=_MegClientStub(),
    )

    explanation = await interface.explain(
        decision_payload,
        mode=ExplanationMode.SYMBOLIC,
        level=ExplanationLevel.DETAILED,
        include_trace=True,
    )

    assert explanation.reasoning_trace is not None
    assert any(step.get("operation") == "meg_recall" for step in explanation.reasoning_trace)


@pytest.mark.asyncio
async def test_signature_generation(decision_payload: Dict[str, object]) -> None:
    interface = ExplainabilityInterface()
    explanation = await interface.explain(
        decision_payload,
        include_proof=True,
        include_trace=True,
        sign_explanation=True,
    )

    assert explanation.signature and explanation.signature.startswith("SRD-SHA256:")


@pytest.mark.asyncio
async def test_template_loading_from_json(tmp_path: Path, decision_payload: Dict[str, object]) -> None:
    template_dir = tmp_path / "templates"
    template_dir.mkdir()

    template_payload = {
        "templates": [
            {
                "template_id": "text_detailed",
                "name": "Detailed",
                "mode": "text",
                "level": "detailed",
                "template": "Decision: {result} (confidence: {confidence})",
                "variables": ["result", "confidence"],
            }
        ]
    }
    (template_dir / "templates.json").write_text(json.dumps(template_payload), encoding="utf-8")

    interface = ExplainabilityInterface(template_dir=template_dir)
    explanation = await interface.explain(decision_payload, ExplanationMode.TEXT, ExplanationLevel.DETAILED)

    assert "Decision: approve" in explanation.content
