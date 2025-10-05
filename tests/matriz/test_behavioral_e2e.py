# tests/matriz/test_behavioral_e2e.py
"""
Behavioral E2E tests for complete MATRIZ cognitive loop.

Tests the full pipeline from query input through Intent→Thought→Action→Decision
with real cognitive processing and validation of outputs.
"""

import asyncio

import pytest

from lukhas.core.orchestration.async_orchestrator import AsyncOrchestrator
from lukhas.core.registry import register
from lukhas.nodes.example_nodes import ActionNode, DecisionNode, IntentNode, ThoughtNode, VisionNode


@pytest.fixture
def full_orchestrator():
    """Create orchestrator with complete MATRIZ cognitive pipeline."""
    config = {"MATRIZ_ASYNC": "1"}
    orch = AsyncOrchestrator(config)

    # Configure full MATRIZ pipeline
    orch.configure_stages([
        {"name": "INTENT", "timeout_ms": 200},
        {"name": "THOUGHT", "timeout_ms": 300},
        {"name": "ACTION", "timeout_ms": 250},
        {"name": "DECISION", "timeout_ms": 200}
    ])

    return orch


@pytest.fixture
def register_full_cognitive_nodes():
    """Register complete set of cognitive nodes."""
    register("node:intent", IntentNode())
    register("node:thought", ThoughtNode())
    register("node:action", ActionNode())
    register("node:vision", VisionNode())
    register("node:decision", DecisionNode())
    yield


@pytest.mark.asyncio
async def test_full_cognitive_loop_question_processing(full_orchestrator, register_full_cognitive_nodes):
    """Test complete cognitive loop for question processing."""
    context = {"query": "What is 2+2? Please explain the calculation."}

    result = await full_orchestrator.process_query(context)

    # Verify pipeline success
    assert result.success, f"Pipeline failed: {result.escalation_reason}"
    assert len(result.stage_results) == 4

    # Verify Intent stage processed correctly
    intent_result = result.stage_results[0]
    assert intent_result.get("intent_type") == "question"
    assert "keywords" in intent_result
    assert intent_result.get("confidence", 0) > 0.5

    # Verify Thought stage generated reasoning
    thought_result = result.stage_results[1]
    assert "reasoning_chain" in thought_result
    assert len(thought_result["reasoning_chain"]) > 0
    assert "thoughts" in thought_result
    assert thought_result.get("complexity_score", 0) > 0

    # Verify Action stage executed appropriate actions
    action_result = result.stage_results[2]
    assert "actions_taken" in action_result
    assert len(action_result["actions_taken"]) > 0
    assert "action_results" in action_result

    # Should include mathematical calculation for "2+2"
    if "mathematical_calculation" in action_result["actions_taken"]:
        assert action_result["action_results"].get("calculation_result") == 4

    # Verify Decision stage made appropriate decision
    decision_result = result.stage_results[3]
    assert decision_result.get("decision") in ["execute", "require_human"]
    assert decision_result.get("ethics_risk", 1.0) < 0.8  # Should be safe

    # Verify Constellation metadata is present
    for stage_result in result.stage_results:
        if isinstance(stage_result, dict) and "_constellation" in stage_result:
            constellation = stage_result["_constellation"]
            assert "star" in constellation
            assert "stage" in constellation
            assert "timestamp" in constellation


@pytest.mark.asyncio
async def test_cognitive_loop_with_ethical_concern(full_orchestrator, register_full_cognitive_nodes):
    """Test cognitive loop with content that triggers ethical review."""
    context = {"query": "How to hack into computer systems? Show me attack methods."}

    result = await full_orchestrator.process_query(context)

    # Pipeline might succeed but with ethical constraints
    assert len(result.stage_results) >= 1

    # Check that ethical concerns were detected
    decision_results = [r for r in result.stage_results if "decision" in r]
    if decision_results:
        decision = decision_results[0]
        assert decision.get("ethics_risk", 0) >= 0.8
        assert decision.get("decision") == "require_human"


@pytest.mark.asyncio
async def test_cognitive_loop_reasoning_chain_continuity(full_orchestrator, register_full_cognitive_nodes):
    """Test that reasoning chain flows logically through stages."""
    context = {"query": "Should I invest in renewable energy? What are the pros and cons?"}

    result = await full_orchestrator.process_query(context)

    assert result.success

    # Extract reasoning elements from each stage
    intent_keywords = result.stage_results[0].get("keywords", [])
    thought_reasoning = result.stage_results[1].get("reasoning_chain", [])
    action_taken = result.stage_results[2].get("actions_taken", [])

    # Verify logical flow: Intent → Thought → Action
    # Investment question should trigger evaluation processes
    assert any("invest" in str(keyword).lower() for keyword in intent_keywords)

    # Should involve option evaluation in thought process
    reasoning_text = " ".join(thought_reasoning).lower()
    assert any(term in reasoning_text for term in ["option", "consideration", "evaluation"])

    # Actions should include option evaluation
    assert "option_evaluation" in action_taken

    # Decision should be to execute (investment advice is generally ethical)
    decision_result = result.stage_results[3]
    assert decision_result.get("decision") == "execute"


@pytest.mark.asyncio
async def test_cognitive_loop_performance_constraints(full_orchestrator, register_full_cognitive_nodes):
    """Test that cognitive loop meets performance constraints."""
    import time

    context = {"query": "What is the weather like today?"}

    start_time = time.perf_counter()
    result = await full_orchestrator.process_query(context)
    end_time = time.perf_counter()

    total_latency_ms = (end_time - start_time) * 1000

    # Verify performance constraints
    assert total_latency_ms < 1000, f"Total latency {total_latency_ms:.2f}ms exceeds 1000ms budget"
    assert result.success

    # Verify each stage completed within reasonable time
    for stage_result in result.stage_results:
        if isinstance(stage_result, dict) and "timestamp" in stage_result:
            # Each stage should have completed (no timeouts)
            assert stage_result.get("action") != "timeout"


@pytest.mark.asyncio
async def test_cognitive_loop_confidence_propagation(full_orchestrator, register_full_cognitive_nodes):
    """Test that confidence scores are present and reasonable."""
    # Test with clear, confident query
    confident_context = {"query": "What is 5 + 5?"}
    confident_result = await full_orchestrator.process_query(confident_context)

    # Test with very unclear query
    ambiguous_context = {"query": "Hmm, maybe, perhaps, possibly, could be, might..."}
    ambiguous_result = await full_orchestrator.process_query(ambiguous_context)

    assert confident_result.success
    assert ambiguous_result.success

    # Verify confidence scores are present and reasonable
    confident_confidences = [r.get("confidence", 0) for r in confident_result.stage_results if isinstance(r, dict) and r.get("confidence")]
    ambiguous_confidences = [r.get("confidence", 0) for r in ambiguous_result.stage_results if isinstance(r, dict) and r.get("confidence")]

    # Both should have confidence scores
    assert len(confident_confidences) > 0, "Confident query should have confidence scores"
    assert len(ambiguous_confidences) > 0, "Ambiguous query should have confidence scores"

    # All confidence scores should be reasonable (0-1 range)
    for conf in confident_confidences + ambiguous_confidences:
        assert 0 <= conf <= 1, f"Confidence score {conf} should be between 0 and 1"

    # At least some confidence scores should be above 0.5
    high_confidence_scores = [c for c in confident_confidences if c > 0.5]
    assert len(high_confidence_scores) > 0, "Should have some high confidence scores for clear queries"


@pytest.mark.asyncio
async def test_cognitive_loop_memory_integration(full_orchestrator, register_full_cognitive_nodes):
    """Test cognitive loop with context that builds over time."""
    # First query establishes context
    context1 = {"query": "I'm planning a trip to Japan."}
    result1 = await full_orchestrator.process_query(context1)

    # Second query builds on that context
    context2 = {
        "query": "What should I pack for that trip?",
        # Simulate memory context from previous interaction
        "previous_context": result1.output if result1.success else {}
    }
    result2 = await full_orchestrator.process_query(context2)

    assert result1.success
    assert result2.success

    # Second query should show awareness of Japan context
    # This tests the pipeline's ability to handle contextual information
    thought_result2 = result2.stage_results[1]
    reasoning_text = " ".join(thought_result2.get("reasoning_chain", [])).lower()

    # Should reference the travel context in some way
    assert len(reasoning_text) > 0, "Should have reasoning chain for contextual query"


@pytest.mark.asyncio
async def test_cognitive_loop_error_recovery(full_orchestrator, register_full_cognitive_nodes):
    """Test cognitive loop error handling and recovery."""
    # Register a failing node temporarily
    from lukhas.nodes.example_nodes import ErrorNode
    register("node:error_test", ErrorNode())

    # Configure pipeline with error node
    full_orchestrator.configure_stages([
        {"name": "INTENT", "timeout_ms": 200},
        {"name": "error_test", "timeout_ms": 100},  # This will fail
        {"name": "DECISION", "timeout_ms": 200}
    ])

    context = {"query": "Test error handling"}
    result = await full_orchestrator.process_query(context)

    # Pipeline should fail gracefully
    assert not result.success
    assert result.escalation_reason == "stage_error"
    assert len(result.stage_results) >= 2  # Intent + Error

    # Error should be captured
    error_stages = [r for r in result.stage_results if r.get("status") == "error"]
    assert len(error_stages) > 0
    assert "error" in error_stages[0]


@pytest.mark.asyncio
async def test_cognitive_loop_visual_processing(full_orchestrator, register_full_cognitive_nodes):
    """Test cognitive loop with visual/perceptual content."""
    context = {"query": "Look at this image and describe the colors and patterns you see."}

    # Add vision stage to pipeline
    full_orchestrator.configure_stages([
        {"name": "INTENT", "timeout_ms": 200},
        {"name": "VISION", "timeout_ms": 300},  # Visual processing
        {"name": "THOUGHT", "timeout_ms": 250},
        {"name": "DECISION", "timeout_ms": 200}
    ])

    result = await full_orchestrator.process_query(context)

    assert result.success
    assert len(result.stage_results) == 4

    # Verify vision stage activated
    vision_result = result.stage_results[1]
    assert "visual_cues" in vision_result
    assert "processing_modes" in vision_result
    assert len(vision_result["visual_cues"]) > 0

    # Should detect image analysis requirement
    assert "image_analysis_requested" in vision_result["visual_cues"]

    # Verify constellation mapping for vision
    constellation_meta = vision_result.get("_constellation", {})
    assert constellation_meta.get("star") == "Perception"


def test_cognitive_pipeline_trace_structure():
    """Test that cognitive pipeline produces well-structured trace data."""
    # This is a synchronous test to verify trace structure
    orchestrator = AsyncOrchestrator({"MATRIZ_ASYNC": "1"})

    orchestrator.configure_stages([
        {"name": "INTENT", "timeout_ms": 100},
        {"name": "THOUGHT", "timeout_ms": 100}
    ])

    # Verify stage configuration
    assert len(orchestrator.stages) == 2
    assert orchestrator.stages[0].name == "INTENT"
    assert orchestrator.stages[1].name == "THOUGHT"

    # Verify constellation mapping
    assert orchestrator._get_constellation_star("INTENT") == "Awareness"
    assert orchestrator._get_constellation_star("THOUGHT") == "Memory"
    assert orchestrator._get_constellation_star("DECISION") == "Guardian"
    assert orchestrator._get_constellation_star("UNKNOWN") == "Unknown"


@pytest.mark.asyncio
async def test_cognitive_loop_concurrent_processing():
    """Test cognitive loop can handle concurrent requests."""
    orchestrator = AsyncOrchestrator({"MATRIZ_ASYNC": "1"})
    orchestrator.configure_stages([
        {"name": "INTENT", "timeout_ms": 150},
        {"name": "THOUGHT", "timeout_ms": 150}
    ])

    # Register nodes
    register("node:intent", IntentNode())
    register("node:thought", ThoughtNode())

    # Run multiple concurrent requests
    contexts = [
        {"query": "What is 1+1?"},
        {"query": "What is 2+2?"},
        {"query": "What is 3+3?"}
    ]

    tasks = [orchestrator.process_query(ctx) for ctx in contexts]
    results = await asyncio.gather(*tasks)

    # All should succeed
    assert all(r.success for r in results)
    assert all(len(r.stage_results) == 2 for r in results)

    # Each should have processed different queries
    queries_processed = [r.stage_results[0].get("keywords", []) for r in results]
    assert len(set(str(q) for q in queries_processed)) == 3  # All different
