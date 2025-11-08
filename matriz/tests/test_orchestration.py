"""
Unit and integration tests for the MATRIZ orchestration modules.
"""

import pytest
from unittest.mock import Mock, patch

# It's good practice to patch modules that might not be available
# in all test environments.
import time

try:
    from matriz.core.orchestrator import CognitiveOrchestrator
    from matriz.core.async_orchestrator import AsyncCognitiveOrchestrator, StageType
    from matriz.core.node_interface import CognitiveNode, NodeState, NodeTrigger
    from matriz.core.example_node import MathReasoningNode
except ImportError:
    pytest.skip("MATRIZ core components not available", allow_module_level=True)

# A concrete implementation of the abstract CognitiveNode for testing purposes.
class ConcreteNode(CognitiveNode):
    def __init__(self, node_name="test_node", capabilities=["test"]):
        super().__init__(node_name, capabilities)

    def process(self, input_data):
        # A simple process method for testing that correctly handles triggers.
        state = NodeState(confidence=0.9, salience=0.8)
        trigger_id = input_data.get("trigger_node_id")
        triggers = []
        if trigger_id:
            triggers.append(
                NodeTrigger(
                    event_type="causal_link",
                    timestamp=int(time.time() * 1000),
                    trigger_node_id=trigger_id
                )
            )
        return {
            "answer": "processed",
            "confidence": 0.9,
            "matriz_node": self.create_matriz_node("COMPUTATION", state, triggers=triggers),
        }

    def validate_output(self, output):
        return "answer" in output and "matriz_node" in output

# --- Tests for node_interface.py ---

def test_create_matriz_node_valid():
    """Tests that a valid MATRIZ node can be created."""
    node = ConcreteNode()
    state = NodeState(confidence=0.8, salience=0.7)
    matriz_node = node.create_matriz_node("DECISION", state, additional_data={"key": "value"})

    assert matriz_node["type"] == "DECISION"
    assert matriz_node["state"]["confidence"] == 0.8
    assert matriz_node["state"]["key"] == "value"
    assert "id" in matriz_node
    assert "version" in matriz_node

def test_create_matriz_node_invalid_type():
    """Tests that creating a node with an invalid type raises an error."""
    node = ConcreteNode()
    state = NodeState(confidence=0.8, salience=0.7)
    with pytest.raises(ValueError):
        node.create_matriz_node("INVALID_TYPE", state)

def test_validate_matriz_node():
    """Tests the validation of MATRIZ nodes."""
    node = ConcreteNode()
    state = NodeState(confidence=0.8, salience=0.7)
    valid_node = node.create_matriz_node("DECISION", state)

    assert node.validate_matriz_node(valid_node)

    invalid_node_no_state = valid_node.copy()
    del invalid_node_no_state["state"]
    assert not node.validate_matriz_node(invalid_node_no_state)

    invalid_node_bad_confidence = valid_node.copy()
    invalid_node_bad_confidence["state"] = {"confidence": 1.1, "salience": 0.5}
    assert not node.validate_matriz_node(invalid_node_bad_confidence)

# --- Tests for example_node.py ---

def test_math_reasoning_node_extract_expression():
    """Tests the expression extraction logic of the MathReasoningNode."""
    node = MathReasoningNode()
    assert node._extract_math_expression("calculate 5 * (2 + 3)") == "5 * (2 + 3)"
    assert node._extract_math_expression("what is 10 / 2") == "10 / 2"
    assert node._extract_math_expression("solve 2**8") == "2**8"
    assert node._extract_math_expression("just some text") == ""

def test_math_reasoning_node_safe_eval():
    """Tests the safe evaluation logic of the MathReasoningNode."""
    node = MathReasoningNode()
    assert node._safe_eval("2+2") == 4.0
    with pytest.raises(ValueError, match="invalid characters"):
        node._safe_eval("import os")
    with pytest.raises(ValueError, match="Unbalanced parentheses"):
        node._safe_eval("(2+2")

def test_math_reasoning_node_valid_expression():
    """Tests the MathReasoningNode with a valid mathematical expression."""
    node = MathReasoningNode()
    result = node.process({"query": "what is 2 + 2?"})

    assert result["answer"] == "The result is 4.0"
    assert result["confidence"] > 0.9
    assert "matriz_node" in result
    assert node.validate_output(result)

def test_math_reasoning_node_no_expression():
    """Tests the MathReasoningNode with a query that doesn't contain a mathematical expression."""
    node = MathReasoningNode()
    result = node.process({"query": "hello world"})

    assert "could not find a mathematical expression" in result["answer"]
    assert result["confidence"] < 0.2
    assert node.validate_output(result)

def test_math_reasoning_node_invalid_expression():
    """Tests the MathReasoningNode with an invalid expression (division by zero)."""
    node = MathReasoningNode()
    result = node.process({"query": "calculate 1/0"})

    assert "couldn't evaluate" in result["answer"]
    assert "Division by zero" in result["answer"]
    assert result["confidence"] < 0.3
    assert node.validate_output(result)

# --- Tests for orchestrator.py ---

def test_orchestrator_register_node():
    """Tests that a node can be registered with the orchestrator."""
    orchestrator = CognitiveOrchestrator()
    node = ConcreteNode()
    orchestrator.register_node("test_node", node)
    assert "test_node" in orchestrator.available_nodes

def test_orchestrator_process_query_success():
    """Tests a successful query processing workflow."""
    orchestrator = CognitiveOrchestrator()
    # Since the internal logic of the orchestrator is to use a 'math' node for this query,
    # we'll register our concrete node under that name.
    orchestrator.register_node("math", ConcreteNode())

    result = orchestrator.process_query("1+1")

    assert "answer" in result
    assert result["answer"] == "processed"

def test_orchestrator_process_query_no_node_available():
    """Tests processing a query when no suitable node is available."""
    orchestrator = CognitiveOrchestrator()
    # No node is registered, so this should fail.
    result = orchestrator.process_query("1+1")
    assert "error" in result
    assert "No node available" in result["error"]

def test_orchestrator_process_query_node_fails():
    """Tests error handling when a node fails during processing."""
    orchestrator = CognitiveOrchestrator()
    mock_node = Mock(spec=CognitiveNode)
    mock_node.process.side_effect = Exception("Node failed")
    orchestrator.register_node("math", mock_node)

    result = orchestrator.process_query("1+1")
    assert "error" in result
    assert "failed during processing" in result["error"]

def test_orchestrator_with_validator():
    """Tests the orchestrator's workflow when a validator node is present."""
    orchestrator = CognitiveOrchestrator()
    orchestrator.register_node("math", ConcreteNode())

    # The validator will just check for the presence of an answer.
    class SimpleValidator(CognitiveNode):
        def process(self, input_data): return {}
        def validate_output(self, output): return "answer" in output

    orchestrator.register_node("validator", SimpleValidator("validator", ["validation"]))

    result = orchestrator.process_query("1+1")
    assert "answer" in result
    # Check that a reflection node was created due to validation
    assert any(node['type'] == 'REFLECTION' for node in result['matriz_nodes'])

def test_orchestrator_get_causal_chain():
    """Tests the retrieval of a causal chain of nodes."""
    orchestrator = CognitiveOrchestrator()
    orchestrator.register_node("math", ConcreteNode())
    result = orchestrator.process_query("1+1")

    # Get the ID of the last node in the graph
    last_node_id = result['matriz_nodes'][-1]['id']
    chain = orchestrator.get_causal_chain(last_node_id)

    # The causal chain should include the intent, decision, and processing nodes.
    assert len(chain) >= 3
    node_types_in_chain = {node['type'] for node in chain}
    assert "INTENT" in node_types_in_chain
    assert "DECISION" in node_types_in_chain

# --- Tests for async_orchestrator.py ---

@pytest.mark.asyncio
async def test_async_orchestrator_register_node():
    """Tests that a node can be registered with the async orchestrator."""
    orchestrator = AsyncCognitiveOrchestrator()
    node = ConcreteNode()
    orchestrator.register_node("test_node", node)
    assert "test_node" in orchestrator.available_nodes

@pytest.mark.asyncio
async def test_async_orchestrator_process_query_success():
    """Tests a successful async query processing workflow."""
    orchestrator = AsyncCognitiveOrchestrator()
    orchestrator.register_node("math", ConcreteNode())

    result = await orchestrator.process_query("1+1")

    assert "answer" in result
    assert result["answer"] == "processed"
    assert "metrics" in result
    assert result["metrics"]["within_budget"]

@pytest.mark.asyncio
async def test_async_orchestrator_total_timeout():
    """Tests that the entire pipeline times out if it exceeds the total budget."""
    # Set a very short total timeout
    orchestrator = AsyncCognitiveOrchestrator(total_timeout=0.01)

    # Register a node that will definitely take longer than the timeout
    class SlowNode(CognitiveNode):
        def process(self, input_data):
            import time
            time.sleep(0.1)
            return {"answer": "done", "confidence": 1.0, "matriz_node": {}}
        def validate_output(self, output): return True

    orchestrator.register_node("math", SlowNode("slow", ["math"]))

    result = await orchestrator.process_query("1+1")

    assert "error" in result
    assert "Pipeline timeout exceeded" in result["error"]

@pytest.mark.asyncio
async def test_async_orchestrator_stage_timeout_and_recover():
    """Tests that a non-critical stage can time out without failing the pipeline."""
    # Set a very short timeout for a non-critical stage (validation)
    orchestrator = AsyncCognitiveOrchestrator(stage_timeouts={StageType.VALIDATION: 0.001})
    orchestrator.register_node("math", ConcreteNode())
    orchestrator.register_node("validator", ConcreteNode()) # A validator must be present for the stage to run

    # Mock the validation stage to be slow
    async def slow_validation(*args, **kwargs):
        import asyncio
        await asyncio.sleep(0.1)
        return True

    with patch.object(orchestrator, '_validate_async', side_effect=slow_validation):
        result = await orchestrator.process_query("1+1")

    assert "answer" in result
    assert result["answer"] == "processed"
    # Check that the validation stage did indeed time out
    validation_stage_result = next(s for s in result["stages"] if s["stage_type"] == StageType.VALIDATION)
    assert validation_stage_result["timeout"] is True

@pytest.mark.asyncio
async def test_async_orchestrator_get_performance_report():
    """Tests the performance reporting of the async orchestrator."""
    orchestrator = AsyncCognitiveOrchestrator()
    orchestrator.register_node("math", ConcreteNode())
    await orchestrator.process_query("1+1")

    report = orchestrator.get_performance_report()
    assert "node_health" in report
    assert "stage_timeouts" in report
    assert "orchestrator_metrics" in report

@pytest.mark.asyncio
async def test_async_orchestrator_get_health_report():
    """Tests the health reporting of the async orchestrator."""
    orchestrator = AsyncCognitiveOrchestrator()
    orchestrator.register_node("math", ConcreteNode())
    await orchestrator.process_query("1+1")

    report = orchestrator.get_health_report()
    assert report["status"] == "healthy"
    assert "math" in report["available_nodes"]

@pytest.mark.asyncio
async def test_async_orchestrator_adaptive_routing():
    """Tests that the orchestrator can select the best node based on health."""
    # Make the processing stage non-critical to allow failures to be recorded
    orchestrator = AsyncCognitiveOrchestrator(stage_critical={StageType.PROCESSING: False})

    class HealthyNode(CognitiveNode):
        def process(self, input_data): return {"answer": "healthy", "confidence": 1.0, "matriz_node": {}}
        def validate_output(self, output): return True

    class UnhealthyNode(CognitiveNode):
        def process(self, input_data): raise ValueError("I am unhealthy")
        def validate_output(self, output): return True

    orchestrator.register_node("math", UnhealthyNode("unhealthy_math", ["math"]))
    orchestrator.register_node("math_alternative", HealthyNode("healthy_math", ["math"]))

    # Run the orchestrator a few times to build up health history for the "math" node
    for _ in range(3):
        await orchestrator.process_query("1+1")

    # The "math" node should now be considered unhealthy
    assert orchestrator.node_health["math"]["failure_count"] >= 1

    # Check that the orchestrator selects the healthy alternative
    selected = await orchestrator._select_node_async({"intent": "mathematical"})
    assert selected == "math_alternative"
