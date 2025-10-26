"""Import-smoke for matriz.nodes.validator_node."""

def test_validator_node_imports():
    mod = __import__("matriz.nodes.validator_node", fromlist=["*"])
    assert mod is not None
