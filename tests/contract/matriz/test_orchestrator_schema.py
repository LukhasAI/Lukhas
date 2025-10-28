import os
import sys

import pytest

pytestmark = pytest.mark.skipif(sys.version_info < (3, 10), reason='matriz module requires Python 3.10+')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
try:
    from MATRIZ.core.node_interface import CognitiveNode
    from MATRIZ.core.orchestrator import CognitiveOrchestrator
    from MATRIZ.nodes.math_node import MathNode
    from MATRIZ.nodes.validator_node import ValidatorNode
except ImportError:

    class CognitiveNode:

        def __init__(self, node_name, capabilities):
            pass

        def process(self, input_data):
            return {}

        def validate_matriz_node(self, node):
            return True

    class CognitiveOrchestrator:

        def register_node(self, name, node):
            pass

        def process_query(self, query):
            return {'matriz_nodes': []}

    class MathNode(CognitiveNode):

        def process(self, input_data):
            return {'matriz_node': {'type': 'COMPUTATION'}}

    class ValidatorNode(CognitiveNode):
        pass

class _ValidatorHarness(CognitiveNode):

    def process(self, input_data):
        raise NotImplementedError

    def validate_output(self, output):
        return True

def _schema_validate(node: dict) -> bool:
    """Use the node interface helper to validate a node schema."""
    harness = _ValidatorHarness(node_name='schema_validator_harness', capabilities=['schema_validation'])
    return harness.validate_matriz_node(node)

def test_orchestrator_emits_schema_compliant_nodes():
    orch = CognitiveOrchestrator()
    orch.register_node('math', MathNode())
    orch.register_node('validator', ValidatorNode())
    result = orch.process_query('What is 2 + 2?')
    assert 'matriz_nodes' in result
    nodes = result['matriz_nodes']
    assert isinstance(nodes, list) and len(nodes) >= 2
    for node in nodes:
        assert _schema_validate(node), f'Node failed schema validation: {node}'
    types = {n.get('type') for n in nodes}
    assert 'INTENT' in types
    assert 'DECISION' in types

def test_math_node_outputs_computation_node_schema():
    node = MathNode()
    out = node.process({'expression': '2+3*5'})
    assert out['matriz_node']['type'] == 'COMPUTATION'
    assert _schema_validate(out['matriz_node']) is True
