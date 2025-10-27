import asyncio
import json
import time
from pathlib import Path
from typing import Any, Dict, List

import pytest

from labs.bridge.explainability_interface_layer import (
    CompletenessMetrics,
    ExplanationLevel,
    ExplanationMode,
    ExplainabilityInterface,
)
from labs.bridge.llm_wrappers.openai_modulated_service import (
    VectorStoreAdapter,
    VectorStoreConfig,
    VectorStoreProvider,
)


class DummyMEGClient:
    def __init__(self) -> None:
        self.calls: List[str] = []

    async def get_context(self, decision_id: str) -> Dict[str, Any]:
        self.calls.append(decision_id)
        await asyncio.sleep(0)
        return {"episodes": [decision_id]}


@pytest.mark.asyncio
async def test_explainability_cache_ttl_expires() -> None:
    dummy_interface = ExplainabilityInterface(cache_ttl_seconds=1)
    cache = dummy_interface.cache
    explanation = await dummy_interface.explain({"id": "x", "result": "approve"})

    cache_key = dummy_interface._generate_cache_key(
        {"id": "x", "result": "approve"}, ExplanationMode.TEXT, ExplanationLevel.DETAILED
    )
    cache.put(cache_key, explanation)

    cache_entry = cache._cache[cache_key]
    cache_entry.stored_at -= 5
    assert cache.get(cache_key) is None
    stats = cache.stats()
    assert stats["expired"] >= 1


@pytest.mark.asyncio
async def test_generate_formal_proof_validates_reasoning() -> None:
    interface = ExplainabilityInterface()
    decision = {
        "id": "decision-1",
        "premises": ["A", "A -> B"],
        "reasoning_steps": [
            {"statement": "B", "rule": "Modus Ponens", "depends_on": [1, 2]},
        ],
        "conclusion": "B",
        "expected_outcome": "B",
    }

    proof = await interface.generate_formal_proof(decision)
    assert proof.valid
    assert proof.steps[-1]["type"] == "conclusion"
    assert proof.steps[-1]["statement"] == "B"


@pytest.mark.asyncio
async def test_multimodal_explanation_contains_channels() -> None:
    interface = ExplainabilityInterface()
    decision = {
        "id": "multi-1",
        "result": "approve",
        "factors": ["policy"],
        "reasoning_steps": [{"operation": "infer", "output": {"value": 1}, "symbolic": "policy"}],
        "confidence": 0.9,
        "drift_score": 0.1,
    }

    explanation = await interface.explain(decision, mode=ExplanationMode.MULTIMODAL)
    assert isinstance(explanation.content, dict)
    assert set(explanation.content.keys()) == {"text", "visual", "audio", "summary"}
    assert explanation.completeness is not None
    assert isinstance(explanation.completeness, CompletenessMetrics)


@pytest.mark.asyncio
async def test_template_loading_and_refresh(tmp_path: Path) -> None:
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()

    yaml_template = {
        "templates": [
            {
                "template_id": "text_simple",
                "name": "Simple",
                "mode": "text",
                "level": "simple",
                "template": "Decision: {result}",
                "variables": ["result"],
            }
        ]
    }
    (templates_dir / "simple.yaml").write_text(json.dumps(yaml_template))

    interface = ExplainabilityInterface(template_dir=templates_dir)
    assert "text_simple" in interface.templates

    # Modify template and refresh
    yaml_template["templates"][0]["template"] = "Updated: {result}"
    (templates_dir / "simple.yaml").write_text(json.dumps(yaml_template))
    interface.refresh_templates()
    assert interface.templates["text_simple"].template == "Updated: {result}"


@pytest.mark.asyncio
async def test_meg_context_caching() -> None:
    meg_client = DummyMEGClient()
    interface = ExplainabilityInterface(meg_client=meg_client, cache_ttl_seconds=10)
    decision = {"id": "meg-1", "result": "approve"}

    context_first = await interface._get_meg_context(decision)
    context_second = await interface._get_meg_context(decision)

    assert context_first == context_second
    assert meg_client.calls.count("meg-1") == 1


@pytest.mark.asyncio
async def test_srd_signature_contains_prefix() -> None:
    interface = ExplainabilityInterface()
    decision = {"id": "sig-1", "result": "approve"}
    explanation = await interface.explain(decision, sign_explanation=True)
    assert explanation.signature is not None
    assert explanation.signature.startswith("SRD-SHA256:")


@pytest.mark.asyncio
async def test_vector_store_adapter_fallback(tmp_path: Path) -> None:
    config = VectorStoreConfig(
        provider=VectorStoreProvider.FAISS,
        endpoint="local",
        index_name="test-index",
        dimension=2,
    )
    adapter = VectorStoreAdapter(config)

    await adapter.initialize()
    vectors = [[0.0, 1.0], [1.0, 0.0]]
    ids = ["v1", "v2"]
    metadata = [{"text": "alpha"}, {"text": "beta"}]

    assert await adapter.upsert_embeddings(vectors, ids, metadata)
    results = await adapter.search([0.0, 1.0], top_k=1)
    assert results
    assert results[0]["metadata"]["text"] in {"alpha", "beta"}

    assert await adapter.health_check()
