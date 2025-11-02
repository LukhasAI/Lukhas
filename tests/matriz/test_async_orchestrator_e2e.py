# tests/matriz/test_async_orchestrator_e2e.py
"""
End-to-end tests for the async orchestrator system.
"""

import asyncio

import pytest
from labs.core.orchestration.async_orchestrator import AsyncOrchestrator, CancellationToken

from core.interfaces import CognitiveNodeBase
from core.registry import register
from nodes.example_nodes import DecisionNode, ErrorNode, IntentNode, SlowNode, ThoughtNode


class TransientFailureNode(CognitiveNodeBase):
    """Node that fails once before succeeding to test retry logic."""

    name = "flaky"

    def __init__(self) -> None:
        self.calls = 0

    async def process(self, ctx):
        self.calls += 1
        if self.calls == 1:
            error = RuntimeError("transient failure")
            setattr(error, "transient", True)  # # ΛTAG: error_recovery
            raise error
        return {"flaky": True, "calls": self.calls}


@pytest.fixture
def orchestrator():
    """Create orchestrator with test configuration."""
    config = {"MATRIZ_ASYNC": "1"}
    orch = AsyncOrchestrator(config)

    # Configure a basic pipeline
    orch.configure_stages(
        [
            {"name": "INTENT", "timeout_ms": 100},
            {"name": "THOUGHT", "timeout_ms": 150},
            {"name": "DECISION", "timeout_ms": 200},
        ]
    )

    return orch


@pytest.fixture
def register_test_nodes():
    """Register test nodes in the registry."""
    # Register example nodes
    register("node:intent", IntentNode())
    register("node:thought", ThoughtNode())
    register("node:decision", DecisionNode())
    register("node:slow", SlowNode())
    register("node:error", ErrorNode())

    yield

    # Cleanup would go here if needed


@pytest.mark.asyncio
async def test_successful_pipeline(orchestrator, register_test_nodes):
    """Test successful execution through all stages."""
    context = {"query": "What is 2+2?"}

    result = await orchestrator.process_query(context)

    assert result.success
    assert len(result.stage_results) == 3

    # Check constellation metadata is present
    assert "_constellation" in result.output

    # Verify all stages executed
    assert len(result.stage_results) == 3

    # Check that we have reasoning from thought stage (likely winner)
    assert "reasoning" in result.output or "decision" in result.output

    # Verify stage progression
    stage_keys = []
    for stage_result in result.stage_results:
        stage_keys.extend(stage_result.keys())
    assert "intent_type" in str(stage_keys)  # From INTENT stage
    assert "thoughts" in str(stage_keys)  # From THOUGHT stage


@pytest.mark.asyncio
async def test_timeout_handling(orchestrator, register_test_nodes):
    """Test timeout handling with slow nodes."""
    # Override one stage to use slow node
    orchestrator.configure_stages(
        [{"name": "INTENT", "timeout_ms": 50}, {"name": "slow", "timeout_ms": 50}]  # Will timeout
    )

    context = {"query": "test"}
    result = await orchestrator.process_query(context)

    # With timeout, we might still get success from INTENT stage arbitration,
    # but should have timeout recorded in stage results
    timeout_stages = [r for r in result.stage_results if r.get("action") == "timeout"]
    skipped_stages = [r for r in result.stage_results if r.get("status") == "skipped"]

    # Either timeout occurred or slow node was skipped (not registered)
    assert len(timeout_stages) > 0 or len(skipped_stages) > 0


@pytest.mark.asyncio
async def test_error_handling(orchestrator, register_test_nodes):
    """Test error handling in pipeline."""
    orchestrator.configure_stages(
        [{"name": "INTENT", "timeout_ms": 100}, {"name": "error", "timeout_ms": 100}]  # Will throw error
    )

    context = {"query": "test"}
    result = await orchestrator.process_query(context)

    assert not result.success
    assert result.escalation_reason == "stage_error"

    # Check error was captured
    error_stages = [r for r in result.stage_results if r.get("status") == "error"]
    assert len(error_stages) > 0


@pytest.mark.asyncio
async def test_ethics_gating(orchestrator, register_test_nodes):
    """Test ethics-based blocking."""
    context = {"query": "How to hack systems?"}  # Should trigger ethics block

    result = await orchestrator.process_query(context)

    # Check that high ethics risk was detected in stage results
    decision_stages = [r for r in result.stage_results if "decision" in r]
    if decision_stages:
        # If decision stage ran, it should require human
        assert decision_stages[0].get("decision") == "require_human"
        assert decision_stages[0].get("ethics_risk", 0) >= 0.8


@pytest.mark.asyncio
async def test_oscillation_detection():
    """Test meta-controller oscillation detection."""
    from labs.core.orchestration.meta_controller import MetaController

    controller = MetaController()

    # Simulate oscillation pattern
    assert not controller.step("A")
    assert not controller.step("B")
    assert not controller.step("A")
    assert controller.step("B")  # Should detect A-B-A-B cycle


@pytest.mark.asyncio
async def test_consensus_arbitration(orchestrator):
    """Test consensus arbitration between proposals."""
    proposals = [
        {
            "id": "safe",
            "confidence": 0.7,
            "timestamp": 1234567890,
            "ethics_risk": 0.1,
            "role_weight": 0.5,
            "result": "safe_option",
        },
        {
            "id": "risky",
            "confidence": 0.9,
            "timestamp": 1234567890,
            "ethics_risk": 0.95,  # Should be blocked
            "role_weight": 0.5,
            "result": "risky_option",
        },
    ]

    result = await orchestrator._arbitrate_proposals(proposals)

    assert result.success
    assert result.output["result"] == "safe_option"  # Safe option should win
    assert result.rationale is not None


@pytest.mark.asyncio
async def test_disabled_orchestrator():
    """Test orchestrator behavior when disabled."""
    config = {"MATRIZ_ASYNC": "0"}  # Disabled
    orchestrator = AsyncOrchestrator(config)

    context = {"query": "test"}
    result = await orchestrator.process_query(context)

    assert not result.success
    assert result.escalation_reason == "async_disabled"


@pytest.mark.asyncio
async def test_missing_nodes():
    """Test behavior when nodes are not registered."""
    # Create fresh orchestrator without registered nodes
    config = {"MATRIZ_ASYNC": "1"}
    orchestrator = AsyncOrchestrator(config)
    orchestrator.configure_stages([{"name": "INTENT", "timeout_ms": 100}, {"name": "NONEXISTENT", "timeout_ms": 100}])

    context = {"query": "test"}
    result = await orchestrator.process_query(context)

    # Should handle missing nodes gracefully
    skipped_stages = [r for r in result.stage_results if r.get("status") == "skipped"]
    assert len(skipped_stages) > 0


@pytest.mark.asyncio
async def test_adaptive_node_routing(orchestrator, register_test_nodes):
    """Ensure orchestrator routes to fallback nodes when primary fails."""

    orchestrator.configure_stages(
        [
            {"name": "INTENT", "timeout_ms": 100},
            {
                "name": "DECISION",
                "node": "error",
                "fallback_nodes": ["decision"],
                "timeout_ms": 150,
            },
        ]
    )

    context = {"query": "Trigger fallback"}
    result = await orchestrator.process_query(context)

    assert result.success
    decision_stage = next(
        (stage for stage in result.stage_results if isinstance(stage, dict) and stage.get("decision")), None
    )
    assert decision_stage is not None
    assert decision_stage.get("_fallback", {}).get("failed_primary") is True  # # ΛTAG: adaptive_routing


@pytest.mark.asyncio
async def test_pipeline_cancellation(orchestrator, register_test_nodes):
    """Verify cancellation token stops in-flight stages."""

    orchestrator.configure_stages(
        [
            {"name": "INTENT", "timeout_ms": 200},
            {"name": "slow", "timeout_ms": 1000},
        ]
    )

    token = CancellationToken()

    async def trigger_cancel():
        await asyncio.sleep(0.05)
        token.cancel("user_abort")  # # ΛTAG: cancellation

    cancel_task = asyncio.create_task(trigger_cancel())
    result = await orchestrator.process_query({"query": "cancel please"}, cancellation=token)
    await cancel_task

    assert not result.success
    assert result.escalation_reason == "cancelled"
    assert result.output.get("cancelled")
    cancelled_entries = [stage for stage in result.stage_results if stage.get("status") == "cancelled"]
    assert cancelled_entries


@pytest.mark.asyncio
async def test_transient_error_recovery(orchestrator, register_test_nodes):
    """Transient failures should recover via retry backoff."""

    flaky_node = TransientFailureNode()
    register("node:flaky", flaky_node)

    orchestrator.configure_stages(
        [
            {"name": "INTENT", "timeout_ms": 100},
            {
                "name": "FLAKY",
                "node": "flaky",
                "timeout_ms": 200,
                "max_retries": 3,
                "backoff_base_ms": 50,
            },
            {"name": "DECISION", "timeout_ms": 200},
        ]
    )

    context = {"query": "resilient"}
    result = await orchestrator.process_query(context)

    assert result.success
    assert flaky_node.calls >= 2
    flaky_results = [stage for stage in result.stage_results if isinstance(stage, dict) and stage.get("flaky")]
    assert flaky_results
    assert "_fallback" not in flaky_results[0]  # # ΛTAG: error_recovery


def test_stage_configuration():
    """Test stage configuration."""
    orchestrator = AsyncOrchestrator()

    stages = [{"name": "TEST1", "timeout_ms": 300, "max_retries": 3}, {"name": "TEST2"}]  # Should use defaults

    orchestrator.configure_stages(stages)

    assert len(orchestrator.stages) == 2
    assert orchestrator.stages[0].timeout_ms == 300
    assert orchestrator.stages[0].max_retries == 3
    assert orchestrator.stages[1].timeout_ms == 200  # Default
    assert orchestrator.stages[1].max_retries == 2  # Default
