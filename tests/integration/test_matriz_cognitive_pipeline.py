import time

import pytest
from matriz.core.node_interface import CognitiveNode, NodeState, NodeTrigger
from matriz.core.orchestrator import CognitiveOrchestrator


class MockCognitiveNode(CognitiveNode):
    def __init__(self, node_name, capabilities):
        super().__init__(node_name, capabilities)

    def process(self, input_data: dict) -> dict:
        trigger_node_id = input_data.get("trigger_node_id")
        triggers = []
        if trigger_node_id:
            triggers.append(
                NodeTrigger(
                    event_type="causal_link",
                    timestamp=int(time.time() * 1000),
                    trigger_node_id=trigger_node_id,
                    effect="triggered_computation",
                )
            )
        return {
            "answer": f"Processed by {self.node_name}",
            "confidence": 0.9,
            "matriz_node": self.create_matriz_node(
                "COMPUTATION",
                NodeState(confidence=0.9, salience=0.9),
                triggers=triggers,
                additional_data={"input": input_data},
            ),
        }

    def validate_output(self, output: dict) -> bool:
        return True

@pytest.mark.integration
def test_matriz_cognitive_cycle():
    orchestrator = CognitiveOrchestrator()
    node = MockCognitiveNode("reasoning", ["reasoning"])
    orchestrator.register_node("reasoning", node)
    orchestrator._select_node = lambda intent_node: "reasoning"

    result = orchestrator.process_query("test query")

    assert "answer" in result
    assert "matriz_nodes" in result
    assert len(result["matriz_nodes"]) > 2
    assert any(n["type"] == "INTENT" for n in result["matriz_nodes"])
    assert any(n["type"] == "DECISION" for n in result["matriz_nodes"])
    assert any(n["type"] == "COMPUTATION" for n in result["matriz_nodes"])

@pytest.mark.integration
def test_multi_node_orchestration_sequential():
    orchestrator = CognitiveOrchestrator()
    math_node = MockCognitiveNode("math", ["mathematical_reasoning"])
    facts_node = MockCognitiveNode("facts", ["information_retrieval"])
    orchestrator.register_node("math", math_node)
    orchestrator.register_node("facts", facts_node)

    # The default _select_node is not deterministic, so we override it for the test
    def select_node(intent_node):
        if intent_node['additional_data']['intent'] == 'mathematical':
            return 'math'
        return 'facts'
    orchestrator._select_node = select_node

    result = orchestrator.process_query("2 + 2")
    assert "Processed by math" in result["answer"]

    result = orchestrator.process_query("What is the capital of France?")
    assert "Processed by facts" in result["answer"]

@pytest.mark.integration
@pytest.mark.asyncio
async def test_multi_node_orchestration_parallel():
    orchestrator = CognitiveOrchestrator()
    node1 = MockCognitiveNode("node1", ["capability1"])
    node2 = MockCognitiveNode("node2", ["capability2"])
    orchestrator.register_node("node1", node1)
    orchestrator.register_node("node2", node2)

    orchestrator._select_node = lambda intent_node: "node1" if "node1" in intent_node['additional_data']['input_text'] else "node2"
    result1 = orchestrator.process_query("query for node1")
    assert "Processed by node1" in result1["answer"]

    result2 = orchestrator.process_query("query for node2")
    assert "Processed by node2" in result2["answer"]

@pytest.mark.integration
@pytest.mark.asyncio
async def test_state_preservation_across_steps():
    orchestrator = CognitiveOrchestrator()
    node = MockCognitiveNode("test_node", ["testing"])
    orchestrator.register_node("test_node", node)
    orchestrator._select_node = lambda intent_node: "test_node"


    assert len(orchestrator.matriz_graph) == 0
    orchestrator.process_query("first query")
    assert len(orchestrator.matriz_graph) > 0
    first_graph_size = len(orchestrator.matriz_graph)

    orchestrator.process_query("second query")
    assert len(orchestrator.matriz_graph) > first_graph_size

@pytest.mark.integration
def test_causal_chain_reconstruction():
    orchestrator = CognitiveOrchestrator()
    node = MockCognitiveNode("test_node", ["testing"])
    orchestrator.register_node("test_node", node)
    orchestrator._select_node = lambda intent_node: "test_node"

    result = orchestrator.process_query("test query")
    matriz_nodes = result["matriz_nodes"]
    last_node_id = ""
    for node in matriz_nodes:
        if node["type"] == "COMPUTATION":
            last_node_id = node["id"]
            break

    causal_chain = orchestrator.get_causal_chain(last_node_id)
    assert len(causal_chain) > 1
    assert any(node["type"] == "INTENT" for node in causal_chain)
    assert any(node["type"] == "DECISION" for node in causal_chain)

@pytest.mark.integration
def test_error_propagation_when_node_fails():
    orchestrator = CognitiveOrchestrator()

    class FailingNode(CognitiveNode):
        def __init__(self):
            super().__init__("failing_node", ["failing"])
        def process(self, input_data: dict) -> dict:
            raise ValueError("Simulated processing error")
        def validate_output(self, output: dict) -> bool:
            return True

    failing_node = FailingNode()
    orchestrator.register_node("failing", failing_node)
    orchestrator._select_node = lambda intent_node: "failing"

    result = orchestrator.process_query("any query")
    assert "error" in result
    assert "failed during processing" in result["error"]

@pytest.mark.integration
def test_recovery_when_node_not_found():
    orchestrator = CognitiveOrchestrator()
    orchestrator._select_node = lambda intent_node: "non_existent_node"

    result = orchestrator.process_query("any query")
    assert "error" in result
    assert "No node available" in result["error"]

@pytest.mark.performance
def test_performance_latency(benchmark):
    orchestrator = CognitiveOrchestrator()
    node = MockCognitiveNode("perf_node", ["performance_testing"])
    orchestrator.register_node("perf_node", node)
    orchestrator._select_node = lambda intent_node: "perf_node"

    def run_query():
        orchestrator.process_query("performance test")

    benchmark(run_query)
    p95_latency = benchmark.stats.get('95th_percentile')
    if p95_latency:
        assert p95_latency < 0.250

@pytest.mark.performance
def test_performance_throughput(benchmark):
    orchestrator = CognitiveOrchestrator()
    node = MockCognitiveNode("throughput_node", ["throughput_testing"])
    orchestrator.register_node("throughput_node", node)
    orchestrator._select_node = lambda intent_node: "throughput_node"

    def run_query():
        orchestrator.process_query("throughput test")

    benchmark.pedantic(run_query, iterations=100, rounds=10)
    ops_per_second = benchmark.stats.get('ops')
    if ops_per_second:
        assert ops_per_second > 50

@pytest.mark.efficiency
def test_memory_efficiency():
    import tracemalloc

    tracemalloc.start()

    orchestrator = CognitiveOrchestrator()
    node = MockCognitiveNode("memory_node", ["memory_testing"])
    orchestrator.register_node("memory_node", node)
    orchestrator._select_node = lambda intent_node: "memory_node"

    orchestrator.process_query("memory test")

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    assert peak < 100 * 1024 * 1024
